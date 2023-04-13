const kustuta_fail = ( failikaart, faili_eriline_nimi ) => {
    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'POST', '/kustuta_fail/' )

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

        const tagastustekst = kustutaja.responseText
        if ( tagastustekst === 'Fail kustutatud.' )
            failikaart.remove( )
        else {
            // lisame veateate puhtalt htmli
            let leht = document.getElementById( 'leht' )

            let veateade = document.createElement( 'div' )
            veateade.className = 'veateade'

            let tekstielement = document.createElement( 'p' )
            tekstielement.innerText = tagastustekst

            let kustuta_veateade_nupp = document.createElement( 'button' )
            kustuta_veateade_nupp.id = 'kustuta_veateade'
            kustuta_veateade_nupp.innerText = 'X'

            kustuta_veateade_nupp.onclick = kustuta_veateade

            veateade.append( tekstielement )
            veateade.append( kustuta_veateade_nupp )

            leht.insertBefore( veateade, leht.firstChild )
        }
    }
}

let failikaardid = document.getElementsByClassName( 'failikaart' )

for ( let failikaart of failikaardid ) {
    let kustutamise_nupp = failikaart.getElementsByClassName( 'kustuta_fail' ).item( 0 )
    let link = failikaart.getElementsByClassName( 'faili_link' ).item( 0 ).href

    kustutamise_nupp.onclick = ( _ ) => {
        let faili_eriline_nimi = link.split( '/' )
        faili_eriline_nimi = faili_eriline_nimi[ faili_eriline_nimi.length - 1 ]

        kustuta_fail( failikaart, faili_eriline_nimi )
    }
}