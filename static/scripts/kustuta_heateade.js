const kustuta_heateade = ( heateade_nupp ) => {
    let heateade_div = heateade_nupp.parentNode

    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'GET', '/api/kustuta_heateade' )
    kustutaja.send( )

    kustutaja.onreadystatechange = ( _ ) => {
        if ( kustutaja.readyState !== XMLHttpRequest.DONE )
            return;

        let json_tagastus = JSON.parse( kustutaja.response )

        if ( json_tagastus.status !== 200 )
            return;

        heateade_div.remove( )
    }
}