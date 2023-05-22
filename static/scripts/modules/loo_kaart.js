const loo_kaart = ( unikaalne_nimi, nimi, tuup, suurus ) => {
    const kaart_div = document.createElement( 'div' );
    kaart_div.classList.add( 'kaart' );

    const fail__esipilt = document.createElement( 'div' );
    fail__esipilt.classList.add( 'fail__esipilt' );

    const fail__link = document.createElement( 'a' );
    fail__link.href = `/fail/${ unikaalne_nimi }`;

    if (  tuup === 'mp4'  ) {
      fail__link.classList.add( 'video_link' );
    } else if (  tuup === 'gif'  ) {
      fail__link.classList.add( 'gif_link' );
    }

    if (  tuup === 'mp4'  ) {
      const video = document.createElement( 'video' );
      video.setAttribute( 'preload', 'auto' );
      const allikas = document.createElement( 'source' );
      allikas.src = `/fail/${ unikaalne_nimi }`;
      allikas.type = `video/${ tuup }`;
      const video_veatekst = document.createTextNode( 'Teie brauser ei toeta videosilti.' );
      video.appendChild( allikas );
      video.appendChild( video_veatekst );
      fail__link.appendChild( video );
    } else {
      const pilt = document.createElement( 'img' );
      pilt.setAttribute( 'loading', 'lazy' );
      pilt.src = `/fail/${ unikaalne_nimi }`;
      pilt.alt = nimi;
      fail__link.appendChild( pilt );
    }
    fail__esipilt.appendChild( fail__link );

    const fail__info = document.createElement( 'div' );
    fail__info.classList.add( 'fail__info' );

    const fail__tiitel = document.createElement( 'div' );
    fail__tiitel.classList.add( 'fail__tiitel' );
    const fail__nimi = document.createElement( 'div' );
    fail__nimi.classList.add( 'fail__nimi' );
    const nimi_tekst = document.createElement( 'p' );
    nimi_tekst.textContent = nimi;
    fail__nimi.appendChild( nimi_tekst );
    const fail__ilus = document.createElement( 'div' );
    fail__ilus.classList.add( 'fail__ilus' );
    fail__tiitel.appendChild( fail__nimi );
    fail__tiitel.appendChild( fail__ilus );

    const fail__juhend = document.createElement( 'div' );
    fail__juhend.classList.add( 'fail__juhend' );
    const fail__andmed = document.createElement( 'div' );
    fail__andmed.classList.add( 'fail__andmed' );
    const andmed__suurus = document.createElement( 'p' );
    andmed__suurus.textContent = suurus.toString(   ) + 'kb';
    const andmed__tuup = document.createElement( 'p' );
    andmed__tuup.textContent = tuup.toUpperCase(  );
    fail__andmed.appendChild( andmed__suurus );
    fail__andmed.appendChild( andmed__tuup );

    const fail__nupud = document.createElement( 'div' );
    fail__nupud.classList.add( 'fail__nupud' );

    const fail__kopeerilink = document.createElement( 'div' );
    fail__kopeerilink.classList.add( 'fail__kopeerilink' );
    const kopeerilink_nupp = document.createElement( 'button' );
    kopeerilink_nupp.setAttribute( 'onclick', 'sea_kopeerimine( this )' );
    kopeerilink_nupp.textContent = '🔗';
    fail__kopeerilink.appendChild( kopeerilink_nupp );

    const fail__kustuta = document.createElement( 'div' );
    fail__kustuta.classList.add( 'fail__kustuta' );
    const kustuta_nupp = document.createElement( 'button' );
    kustuta_nupp.setAttribute( 'onclick', `kustuta_fail( this, '${ unikaalne_nimi }' )` );
    kustuta_nupp.textContent = '🗑️';
    fail__kustuta.appendChild( kustuta_nupp );

    fail__nupud.appendChild( fail__kopeerilink )
    fail__nupud.appendChild( fail__kustuta )

    fail__juhend.appendChild( fail__andmed );
    fail__juhend.appendChild( fail__nupud );

    fail__tiitel.appendChild( fail__nimi );
    fail__tiitel.appendChild( fail__ilus );

    fail__info.appendChild( fail__tiitel );
    fail__info.appendChild( fail__juhend );

    kaart_div.appendChild( fail__esipilt );
    kaart_div.appendChild( fail__info );

    return kaart_div
}
