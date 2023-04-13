const otsija_vorm = document.getElementById( 'otsija' )
const kaardid = document.getElementById( 'kaardid' )

const otsi_faile = ( ) => {
    let failinimi = document.getElementById( 'faili_osaline_nimi' ).value
    let sildid = ''// document.getElementById( 'sildid' ).value
    let tuup = [ ]

    let otsitavad_tuubid = {
        pilt : document.getElementById( 'otsi_pilt' ).checked,
        video : document.getElementById( 'otsi_video' ).checked,
        gif : document.getElementById( 'otsi_gif' ).checked
    }

    if ( !( otsitavad_tuubid.pilt || otsitavad_tuubid.video || otsitavad_tuubid.gif ) ) {
        tuup.push( 'png', 'jpg', 'jpeg', 'mp4', 'mov', 'gif' )
    } else {
        if ( otsitavad_tuubid.pilt ) {
            tuup.push( 'png', 'jpg', 'jpeg' )
        }

        if ( otsitavad_tuubid.video ) {
            tuup.push( 'mp4', 'mov' )
        }

        if ( otsitavad_tuubid.gif ) {
            tuup.push( 'gif' )
        }
    }

    if ( failinimi === '' )
        failinimi = '%'

    let otsija = new XMLHttpRequest( )
    otsija.open( 'POST', '/api/otsi' )

    let andmed = new FormData( )
    andmed.append( 'failinimi', failinimi )
    andmed.append( 'sildid', sildid )
    andmed.append( 'tuup', tuup.join( '|' ) )

    otsija.send( andmed )

    otsija.onreadystatechange = ( _ ) => {
        if ( otsija.readyState !== XMLHttpRequest.DONE )
            return;

        if ( otsija.status !== 200 )
            return;

        let json_tagastus = JSON.parse( otsija.response )

        while ( kaardid.children.length > 1 ) {
            kaardid.removeChild( kaardid.lastChild )
        }

        for ( let tagastus_obj of json_tagastus ) {
            let uus_kaart_html = `
                <div class="kaart failikaart">
                    <a class="faili_link" href="/fail/${ tagastus_obj.unikaalne_nimi }">
                        <img class="esituspilt" src="/fail/${ tagastus_obj.unikaalne_nimi }" alt="${ tagastus_obj.nimi }">
                    </a>
                    <p class="nimi">${ tagastus_obj.nimi }.${ tagastus_obj.tuup }</p>
                    <div class="sildid-ja-nupud">
                        <div class="sildid">

                        </div>
                        <div class="nupud">
                            <button class="kustuta_fail" style="--aaris_kaart: var( --viga ); --taust_kaart: var( --viga ); --tekst_kaart: var( --taust-tavaline )">
                                <img src="./../static/assets/trash.svg" alt="Kustuta">
                            </button>

                            <button class="kopeeri_link" style="--aaris_kaart: black; --taust_kaart: var( --taust-peamine ); --tekst_kaart: var( --tekst );">
                                <img src="./../static/assets/link.svg" alt="Kopeeri link">
                            </button>
                        </div>
                    </div>
                </div>
            `

            kaardid.innerHTML += uus_kaart_html
        }

        otsija_vorm.onsubmit = sundmus => {
            sundmus.preventDefault( )
            otsi_faile( )

            return false
        }
    }
}

otsija_vorm.onsubmit = sundmus => {
    sundmus.preventDefault( )
    otsi_faile( )

    return false
}

otsija_vorm.onreset = _ => {
    console.log( 'wow' )
}