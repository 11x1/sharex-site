if ( failikaardid === undefined ) {
    let failikaardid = document.getElementsByClassName( 'failikaart' )
}

const sea_kopeerimine = ( failikaart ) => {
    let link = failikaart.getElementsByClassName( 'faili_link' ).item( 0 ).href
    let kopeerimise_nupp = failikaart.getElementsByClassName( 'kopeeri_link' ).item( 0 )

    // nupu klikkamisel kopeerime faililingi lõikelauale
    kopeerimise_nupp.onclick = ( _ ) => { // "_" parameeter, sest me ei kasuta parameetrit ning (teoreetiliselt) anname compilerile teada et, jou, pole vaja midagi tegelt (naeb parem valja)
        navigator.clipboard.writeText( link ).catch( _ => alert( 'Ei saanud linki kopeerida. Kas veebilehele on õigus kopeerida antud?' ) )
    }
}

for ( let failikaart of failikaardid ) {
    // leiame esimese elemendi, mille klassiks on 'faili_link' ja krabame selle ümbersuunamise lingi
    // praegusel juhul on esimene vastav element pildi "wrapper" element sildiga "a"
    // ning mille ümbersuunamise link viitab faili kuvamise lehele
    sea_kopeerimine( failikaart )
}