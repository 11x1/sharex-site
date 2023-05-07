const loo_kaart = (  unikaalne_nimi, nimi, tuup  ) => {
    const kaart_div = document.createElement( 'div' )
    kaart_div.classList.add( 'kaart', 'failikaart' )

    const faili_link = document.createElement( 'a' )
    faili_link.classList.add( 'faili_link' )
    faili_link.href = `/fail/${ unikaalne_nimi }`

    if ( tuup === 'mp4' ) {
        faili_link.classList.add( 'video_link' )
        const video = document.createElement( 'video' )
        video.preload = 'auto'

        const video_src = document.createElement( 'source' )
        video_src.src = `/fail/${ unikaalne_nimi }`
        video_src.type = `video/${ tuup }`

        video.appendChild( video_src )
        faili_link.appendChild( video )
    } else {
        if ( tuup === 'gif' )
            faili_link.classList.add( 'gif_link' )
        const pilt = document.createElement( 'img' )
        pilt.classList.add( 'esituspilt' )
        pilt.src = `/fail/${ unikaalne_nimi }`
        pilt.alt = nimi

        faili_link.appendChild( pilt )
    }


    kaart_div.appendChild( faili_link )

    const nimi_p = document.createElement( 'p' )
    nimi_p.classList.add( 'nimi' )
    nimi_p.textContent = `${ nimi }.${ tuup }`
    kaart_div.appendChild( nimi_p )

    const sildid_ja_nupud = document.createElement( 'div' )
    sildid_ja_nupud.classList.add( 'sildid-ja-nupud' )

    const sildid = document.createElement( 'div' )
    sildid.classList.add( 'sildid' )
    sildid_ja_nupud.appendChild( sildid )

    const nupud = document.createElement( 'div' )
    nupud.classList.add( 'nupud' )

    const kustuta_fail_nupp = document.createElement( 'button' )
    kustuta_fail_nupp.classList.add( 'kustuta_fail' )
    kustuta_fail_nupp.style = '--aaris_kaart: var( --viga ); --taust_kaart: var( --viga ); --tekst_kaart: var( --taust-tavaline )'

    const kustuta_fail_pilt = document.createElement( 'img' )
    kustuta_fail_pilt.src = './../static/assets/trash.svg'
    kustuta_fail_pilt.alt = 'Kustuta'
    kustuta_fail_nupp.appendChild( kustuta_fail_pilt )
    nupud.appendChild( kustuta_fail_nupp )

    const kopeeri_link_nupp = document.createElement( 'button' )
    kopeeri_link_nupp.classList.add( 'kopeeri_link' )
    kopeeri_link_nupp.style = '--aaris_kaart: black; --taust_kaart: var( --taust-peamine ); --tekst_kaart: var( --tekst )'

    const kopeeri_link_pilt = document.createElement( 'img' )
    kopeeri_link_pilt.src = './../static/assets/link.svg'
    kopeeri_link_pilt.alt = 'Kopeeri link'

    kopeeri_link_nupp.appendChild( kopeeri_link_pilt )
    nupud.appendChild( kopeeri_link_nupp )

    sildid_ja_nupud.appendChild( nupud )
    kaart_div.appendChild( sildid_ja_nupud )

    sea_kopeerimine( kaart_div )
    sea_kustutamine( kaart_div )

    return kaart_div
}