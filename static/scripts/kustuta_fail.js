const kustuta_fail = ( failikaart, faili_eriline_nimi ) => {
    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'POST', '/api/kustuta_fail/' )

    const andmed = new FormData( )
    andmed.append( 'faili_eriline_nimi', faili_eriline_nimi )

    let api_voti = ''
    let kupsised =  document.cookie.split( '; ' )
    for ( let kupsis of kupsised ) {
        kupsis = kupsis.split( '=' )
        if ( kupsis[ 0 ] !== 'api_voti' )
            continue

        kupsis[ 0 ] = ''
        api_voti = kupsis.join( '' )

        api_voti += '='.repeat( kupsis.length - 2 )
        break
    }

    andmed.append( 'api_voti', api_voti )

    kustutaja.send( andmed )

    kustutaja.onreadystatechange = ( _ ) => { // Kui kustutaja valmisolek muutub
        if ( kustutaja.readyState !== XMLHttpRequest.DONE )
            return;

        if ( kustutaja.status !== 200 )
            return;

        const json_tagastus = JSON.parse( kustutaja.response )

        let leht = document.getElementById( 'leht' )

        if ( json_tagastus.status === 200 ) {
            failikaart.remove()

            let heateade = loo_heateade( json_tagastus.sonum )

            leht.insertBefore(heateade, leht.firstChild)
        } else {
            // lisame veateate puhtalt htmli
            let veateade = loo_veateade( json_tagastus.sonum )

            leht.insertBefore( veateade, leht.firstChild )
        }
    }
}

let failikaardid = document.getElementsByClassName( 'failikaart' )

const sea_kustutamine = ( failikaart ) => {
    let kustutamise_nupp = failikaart.getElementsByClassName( 'kustuta_fail' ).item( 0 )
    let link = failikaart.getElementsByClassName( 'faili_link' ).item( 0 ).href

    kustutamise_nupp.onclick = ( _ ) => {
        let faili_eriline_nimi = link.split( '/' )
        faili_eriline_nimi = faili_eriline_nimi[ faili_eriline_nimi.length - 1 ]

        kustuta_fail( failikaart, faili_eriline_nimi )
    }
}

for ( let failikaart of failikaardid ) {
    sea_kustutamine( failikaart )
}