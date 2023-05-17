const loo_heateade = ( tekst ) => {
    let heateade = document.createElement( 'div' )
    heateade.classList.add( 'veateade' )
    heateade.classList.add( 'hea' )

    let tekstielement = document.createElement( 'p' )
    tekstielement.innerText = tekst

    let kustuta_heateade_nupp = document.createElement( 'button' )
    kustuta_heateade_nupp.id = 'kustuta_heateade'
    kustuta_heateade_nupp.innerText = 'X'

    kustuta_heateade_nupp.onclick = ( ) => kustuta_heateade( kustuta_heateade_nupp )

    heateade.append( tekstielement )
    heateade.append( kustuta_heateade_nupp )

    return heateade
}

const loo_veateade = ( tekst ) => {
    let veateade = document.createElement( 'div' )
    veateade.className = 'veateade'

    let tekstielement = document.createElement( 'p' )
    tekstielement.innerText = tekst

    let kustuta_veateade_nupp = document.createElement( 'button' )
    kustuta_veateade_nupp.id = 'kustuta_veateade'
    kustuta_veateade_nupp.innerText = 'X'
    kustuta_veateade_nupp.onclick = ( ) => kustuta_veateade( kustuta_veateade_nupp )

    veateade.append( tekstielement )
    veateade.append( kustuta_veateade_nupp )

    return veateade
}
