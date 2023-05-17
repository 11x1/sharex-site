const kustuta_veateade = ( kustuta_veateade_nupp ) => {
    let veateade_div = kustuta_veateade_nupp.parentNode

    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'GET', '/api/kustuta_veateade' )
    kustutaja.send( )

    kustutaja.onreadystatechange = ( _ ) => {
        if ( kustutaja.readyState !== XMLHttpRequest.DONE )
            return;

        let json_tagastus = JSON.parse( kustutaja.response )

        if ( json_tagastus.status !== 200 )
            return;

        veateade_div.remove( )
    }
}