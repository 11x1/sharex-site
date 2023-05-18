function kopeeri_kutse( element ) {
    navigator.clipboard.writeText( element.innerText ).catch( _ => alert( 'Ei saanud linki kopeerida. Kas veebilehele on õigus kopeerida antud?' ) )
}