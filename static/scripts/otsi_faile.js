const otsija_vorm = document.getElementById( 'otsija' )
const kaardid = document.getElementById( 'kaardid' )
const leht = document.getElementById( 'leht' )

const otsi_faile = ( lehe_nr ) => {
    let failinimi = document.getElementById( 'faili_osaline_nimi' ).value
    let sildid = '' // document.getElementById( 'sildid' ).value
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

        if ( localStorage.getItem( 'otsi_lehe_nr' ) === '0' ) {
            while ( kaardid.children.length > 1 ) {
                kaardid.removeChild(kaardid.lastChild)
            }
        }

        let faililugeja = 0
        for ( let tagastus_obj of json_tagastus ) {
            if ( faililugeja >= json_tagastus.length - 1 )
                break // 12 on limiit praegu, viimane 13 element sisaldab infot lehtede kohta

            let uus_kaart = loo_kaart( tagastus_obj.unikaalne_nimi, tagastus_obj.nimi, tagastus_obj.tuup )

            kaardid.append( uus_kaart )
            faililugeja += 1
        }

        let lehti = json_tagastus[ json_tagastus.length - 1 ].lehti

        console.log( lehti )

        if ( lehe_nr > lehti.enne + lehti.parast ) {
            localStorage.setItem( 'otsi_lehe_nr', '0' )
        } else {
            localStorage.setItem( 'otsi_lehe_nr', lehe_nr.toString( ) )
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
    otsi_faile( 1 )

    return false
}

otsija_vorm.onreset = _ => {
    otsija_vorm.reset( )
    localStorage.setItem( 'otsi_lehe_nr', '0' )

    setTimeout( otsi_faile, 10 ) // Vaike valeajastus kui kutsuksime kohe => failid ei oleks taastatud
}

localStorage.setItem( 'otsi_lehe_nr', '0' )

window.onscroll = sundmus => {
    let praegune_nr = parseInt( localStorage.getItem( 'otsi_lehe_nr' ) )
    console.log( 'page', praegune_nr )
    if ( praegune_nr === 0 )
        return

    if( Math.abs( document.body.scrollHeight - document.body.scrollTop - document.body.clientHeight ) < 1 ) {
        otsi_faile(
            praegune_nr + 1
        )
    }
}