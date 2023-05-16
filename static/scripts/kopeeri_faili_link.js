function sea_kopeerimine ( kopeerimise_nupp ) {
    let failikaart = kopeerimise_nupp.parentElement.parentElement.parentElement.parentElement.parentElement

    let link = failikaart.getElementsByTagName( 'a' ).item( 0 ).href

    navigator.clipboard.writeText( link ).catch( _ => alert( 'Ei saanud linki kopeerida. Kas veebilehele on õigus kopeerida antud?' ) )
}