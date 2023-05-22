const otsija_vorm = document.getElementById( 'otsija' )
const otsi_nupp = document.getElementById( 'otsi_saada' )

const kaardid = document.getElementById( 'kaardid' )
const leht = document.getElementById( 'leht' )

let otsitakse = false
let koik_failid_leitud = false
let ootab_tulemust = false

const otsi_faile = ( lehe_nr ) => {
    if ( ootab_tulemust ) return
    ootab_tulemust = true

    let failinimi = document.getElementById( 'faili_osaline_nimi' ).value
    let sildid = '' // document.getElementById( 'sildid' ).value
    let tuup = [ ]

    let otsitavad_tuubid = {
        pilt : document.getElementById( 'otsi_pilt' ).checked,
        video : document.getElementById( 'otsi_video' ).checked,
        gif : document.getElementById( 'otsi_gif' ).checked
    }

    if ( !( otsitavad_tuubid.pilt || otsitavad_tuubid.video || otsitavad_tuubid.gif ) || !otsitakse ) {
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

    failinimi = '%' + failinimi + '%'

    let otsija = new XMLHttpRequest( )
    otsija.open( 'POST', '/api/otsi' )

    lehe_nr = lehe_nr === undefined ? 1 : lehe_nr

    let andmed = new FormData( )
    andmed.append( 'failinimi', failinimi )
    andmed.append( 'sildid', sildid )
    andmed.append( 'tuup', tuup.join( '|' ) )
    andmed.append( 'lehe_nr', lehe_nr )

    otsija.send( andmed )

    otsija.onreadystatechange = ( _ ) => {
        if ( otsija.readyState !== XMLHttpRequest.DONE )
            return;

        if ( otsija.status !== 200 )
            return;

        let json_tagastus = JSON.parse( otsija.response )

        let faililugeja = 0
        for ( let tagastus_obj of json_tagastus ) {
            if ( faililugeja >= json_tagastus.length - 1 )
                break // 12 on limiit praegu, viimane 13 element sisaldab infot lehtede kohta

            let uus_kaart = loo_kaart( tagastus_obj.unikaalne_nimi, tagastus_obj.nimi, tagastus_obj.tuup, tagastus_obj.suurus )

            kaardid.append( uus_kaart )
            faililugeja += 1
        }

        let lehti = json_tagastus[ json_tagastus.length - 1 ].lehti

        if ( lehe_nr > lehti.enne + lehti.parast ) {
            localStorage.setItem( 'otsi_lehe_nr', '0' )
            koik_failid_leitud = true
        } else {
            localStorage.setItem( 'otsi_lehe_nr', lehe_nr.toString( ) )
        }

        otsija_vorm.onsubmit = sundmus => {
            sundmus.preventDefault( )
            otsi_faile( 1 )

            return false
        }

        ootab_tulemust = false
    }
}

otsija_vorm.onsubmit = sundmus => {
    koik_failid_leitud = false

    while ( kaardid.children.length > 1 ) {
        kaardid.removeChild( kaardid.lastChild )
    }

    otsitakse = true
    sundmus.preventDefault( )

    otsi_faile( 1 )

    return false
}

otsi_nupp.onclick = ( ) => {
    while ( kaardid.children.length > 1 ) {
        kaardid.removeChild( kaardid.lastChild )
    }
}

otsija_vorm.onreset = _ => {
    otsija_vorm.reset( )

    otsitakse = false
    koik_failid_leitud = false

    localStorage.setItem( 'otsi_lehe_nr', '1' )

    setTimeout( ( _ ) => otsi_faile( 1 ), 10 ) // Vaike valeajastus kui kutsuksime kohe => failid ei oleks taastatud
}

localStorage.setItem( 'otsi_lehe_nr', '1' )

window.onscroll = _ => {
    let peaks_leidma_uued = ( document.body.clientHeight - 20 ) <= ( document.scrollingElement.scrollTop + window.innerHeight )

    let praegune_lehe_nr = localStorage.getItem( 'otsi_lehe_nr' )

    if ( praegune_lehe_nr === '0' || !peaks_leidma_uued )
        return

    if ( isNaN( parseInt( praegune_lehe_nr ) || koik_failid_leitud ) )
        return // Kui ei saa numbrit

    otsi_faile( parseInt( praegune_lehe_nr ) + 1 )
}

let leia_koik_kui_valja_zoomitud = setInterval( ( ) => {
    window.onscroll.call(undefined, undefined )
    let praegune_lehe_nr = localStorage.getItem( 'otsi_lehe_nr' )

    if ( praegune_lehe_nr === '0' || window.innerHeight < document.body.clientHeight ) {
        clearInterval( leia_koik_kui_valja_zoomitud )
    }
}, 1000 )
