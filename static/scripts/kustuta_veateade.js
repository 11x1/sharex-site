const kustuta_veateade = ( _ ) => {
    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'GET', '/api/kustuta_veateade' )
    kustutaja.send( )

    kustutaja.onreadystatechange = ( _ ) => {
        if ( kustutaja.readyState !== XMLHttpRequest.DONE )
            return;

        let json_tagastus = JSON.parse( kustutaja.response )

        if ( json_tagastus.status !== 200 )
            return;

        let veateade = document.getElementsByClassName( 'heateade' ).item( 0 )
        veateade.remove( )
    }
}

const kustuta_veateade_nupp = document.getElementById( 'kustuta_veateade' )
if ( kustuta_veateade_nupp !== null )
    kustuta_veateade_nupp.onclick = kustuta_veateade