const kustuta_kasutaja = _ => {
    let kustutaja = new XMLHttpRequest( )
    kustutaja.open( 'POST', '/api/kustuta_kasutaja/' )
    kustutaja.send( )

    let sobivad_tagastused = [ 500, 200, 400 ]

    kustutaja.onreadystatechange = _ => {
        if ( kustutaja.readyState !== XMLHttpRequest.DONE )
            return;

        const tagastus_json = JSON.parse( kustutaja.response )

        if ( !sobivad_tagastused.includes( tagastus_json.status ) )
            return;

        window.location.href = tagastus_json.suund
    }
}

let kasutaja_kustutamise_nupp = document.getElementById( 'kustuta_kasutaja' )

if ( kasutaja_kustutamise_nupp !== null ) {
    kasutaja_kustutamise_nupp.onclick = _ => {
        let kas_kustutada_kasutaja = window.confirm( 'Kas oled kindel, et soovid oma kasutaja kustutada?\nKasutaja kustutamisel kustutatakse kõik sinu üleslaetud failid. Jätka?' )

        if ( !kas_kustutada_kasutaja )
            return;

        kustuta_kasutaja( )
    }
}