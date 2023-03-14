from sql import Andmebaas
from parooli_kontroll import kontrolli_parool

from flask import Flask, request, render_template, redirect, url_for, make_response

Veebileht = Flask( __name__ )
Andmebaas = Andmebaas( 'root', '', 'sharex_site', 'localhost' )

Andmebaas.kuva_kasutajad( )

# Funktsioon, et kontrollida kas kasutaja on sisse logitud
def on_sisse_logitud( r: request ) -> bool:
    api_voti = r.cookies.get( 'api_voti' )
    [ legaalne_voti, kasutajanimi ] = Andmebaas.kas_api_voti_on_legaalne( api_voti )
    return [ legaalne_voti, kasutajanimi ]

# API route'id
@Veebileht.post( '/registreeri' ) # Lubame ainult POST requestid
def api_registreeri( ):
    lehele_saadetud_info = request.form

    kasutajanimi = lehele_saadetud_info[ 'kasutajanimi' ].lower( )
    kasutaja_on_olemas = Andmebaas.kas_kasutaja_on_olemas( kasutajanimi )

    veateade = 'Kasutajanimi on olemas.' if kasutaja_on_olemas else ''

    if kasutaja_on_olemas:
        return render_template( 'registreeri.html', veateade=veateade )

    parool = lehele_saadetud_info[ 'parool' ]
    [ parool_on_tugev, veateade ] = kontrolli_parool( parool )

    veateade = veateade if not parool_on_tugev else ''

    if not parool_on_tugev:
        return render_template( 'registreeri.html', veateade=veateade )

    kasutaja_loodi_edukalt = Andmebaas.loo_kasutaja( kasutajanimi=kasutajanimi, plaintext_parool=parool )

    veateade = 'Kasutaja loomisel esines viga.' if not kasutaja_loodi_edukalt else ''

    if not kasutaja_loodi_edukalt:
        return render_template( 'registreeri.html', veateade=veateade )

    tagastus = make_response( 'Registreeritud.' )
    tagastus.set_cookie( 'api_voti', Andmebaas.leia_kasutaja_api_voti( kasutajanimi ) )

    return redirect( url_for( 'index' ) )

@Veebileht.get( '/sisselogimine' )
def sisselogimine( ):
    if on_sisse_logitud( request ):
        return redirect( url_for( 'index' ) )

    return 'logi sisse'

@Veebileht.get( '/registreeri' )
def registreeri( ):
    if on_sisse_logitud( request ):
        return redirect( url_for( 'index' ) )

    Andmebaas.kuva_kasutajad( )
    return render_template( 'registreeri.html' )

@Veebileht.get( '/' )
def index( ):
    if not on_sisse_logitud( request ):
        return redirect( url_for( 'sisselogimine' ) )

    cookies = request.cookies.get( 'api_voti' )
    return str( cookies )

if __name__ == "__main__":
    Veebileht.run( debug=True )