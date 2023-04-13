const kustuta_veateade = ( _ ) => {
    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'GET', '/kustuta_veateade' )
    kustutaja.send( )

    kustutaja.onreadystatechange = ( _ ) => { // Kui kustutaja valmisolek muutub
        if ( kustutaja.readyState !== XMLHttpRequest.DONE )
            return;

        if ( kustutaja.status !== 200 )
            return;

        if ( kustutaja.responseText !== 'Veateade kustutatud.' )
            return;

        let veateade = document.getElementsByClassName( 'veateade' ).item( 0 )
        veateade.remove( )
    }
}

const kustuta_veateade_nupp = document.getElementById( 'kustuta_veateade' )
if ( kustuta_veateade_nupp !== null )
    kustuta_veateade_nupp.onclick = kustuta_veateade