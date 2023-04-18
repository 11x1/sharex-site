const kustuta_heateade = ( _ ) => {
    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'GET', '/api/kustuta_heateade' )
    kustutaja.send( )

    kustutaja.onreadystatechange = ( _ ) => {
        if ( kustutaja.readyState !== XMLHttpRequest.DONE )
            return;

        let json_tagastus = JSON.parse( kustutaja.response )

        if ( json_tagastus.status !== 200 )
            return;

        let heateade = document.getElementsByClassName( 'veateade hea' ).item( 0 )
        heateade.remove( )
    }
}

const kustuta_heateade_nupp = document.getElementById( 'kustuta_heateade' )
if ( kustuta_heateade_nupp !== null )
    kustuta_heateade_nupp.onclick = kustuta_heateade