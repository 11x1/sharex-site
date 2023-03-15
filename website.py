from sql import Andmebaas, log
from parooli_kontroll import kontrolli_parool

from flask import Flask, request, render_template, redirect, url_for, make_response, Response

Veebileht = Flask( __name__ )
Andmebaas = Andmebaas( 'root', '', 'sharex_site', 'localhost' )

# Funktsioon, et kontrollida kas kasutaja on sisse logitud
def on_sisse_logitud( ) -> list[ bool, str ]:
    api_voti = request.cookies.get( 'api_voti' )
    if api_voti is None:
        return [ False, '' ]
    [ legaalne_voti, kasutajanimi ] = Andmebaas.kas_api_voti_on_legaalne( api_voti )
    return [ legaalne_voti, kasutajanimi ]

def leia_kupsised( ) -> dict:
    kupsised = list( request.cookies.items( ) )

    tagastatavad_kupsised = { }
    for kupsis in kupsised:
        tagastatavad_kupsised[ kupsis[ 0 ] ] = kupsis[ 1 ]

    return tagastatavad_kupsised

def sea_kupsis( tagastus: Response, nimi: str, vaartus: any ):
    tagastus.set_cookie( nimi, vaartus )
    log( f'kupsise uus vaartus { nimi }->{ vaartus }' )
    return tagastus

def kustuta_kupsised( tagastus: Response ):
    kupsised = leia_kupsised( )
    for kupsis in kupsised:
        tagastus.delete_cookie( kupsis )
    print( 'kustutati koik kupsised' )
    return tagastus


# API route'id
@Veebileht.post( '/registreeri' ) # Lubame ainult POST requestid
def api_registreeri( ):
    lehele_saadetud_info = request.form

    kasutajanimi = lehele_saadetud_info[ 'kasutajanimi' ].lower( )
    kasutaja_on_olemas = Andmebaas.kas_kasutaja_on_olemas( kasutajanimi )

    tagastus = make_response( redirect( url_for( 'registreeri' ) ) )

    if kasutaja_on_olemas:
        tagastus = sea_kupsis( tagastus, 'veateade', 'Kasutajanimi on olemas.' )
        return tagastus

    parool = lehele_saadetud_info[ 'parool' ]
    [ parool_on_tugev, veateade ] = kontrolli_parool( parool )

    if not parool_on_tugev:
        tagastus = sea_kupsis( tagastus, 'veateade', veateade )
        return tagastus

    kasutaja_loodi_edukalt = Andmebaas.loo_kasutaja( kasutajanimi=kasutajanimi, plaintext_parool=parool )

    if not kasutaja_loodi_edukalt:
        tagastus = sea_kupsis( tagastus, 'veateade', 'Kasutaja loomisel esines viga.' )
        return tagastus

    tagastus = sea_kupsis( tagastus, 'veateade', '' )
    tagastus = sea_kupsis( tagastus, 'api_voti', Andmebaas.leia_kasutaja_api_voti( kasutajanimi ) )

    return tagastus

@Veebileht.post( '/sisselogimine' )
def api_login( ):
    lehele_saadetud_info = request.form

    kasutajanimi = lehele_saadetud_info[ 'kasutajanimi' ].lower( )
    kasutaja_on_olemas = Andmebaas.kas_kasutaja_on_olemas( kasutajanimi )

    kupsiste_haldaja = make_response( redirect( url_for( 'sisselogimine' ) ) )

    if not kasutaja_on_olemas:
        kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', 'Kasutajanime ei ole olemas.' )
        return kupsiste_haldaja

    parool = lehele_saadetud_info[ 'parool' ]

    kas_parool_kattub = Andmebaas.kas_kasutaja_parool_kattub( kasutajanimi, parool )

    if not kas_parool_kattub:
        kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', 'Parool on vale.' )
        return kupsiste_haldaja

    kupsiste_haldaja = make_response( redirect( url_for( 'index' ) ) )
    kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', '' )
    kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'api_voti', Andmebaas.leia_kasutaja_api_voti( kasutajanimi ) )

    return kupsiste_haldaja


@Veebileht.get( '/sisselogimine' )
def sisselogimine( ):
    [ sisselogitud, kasutajanimi ] = on_sisse_logitud( )

    if sisselogitud:
        tagastus = make_response( redirect( url_for( 'index' ) ) )
        tagastus = kustuta_kupsised( tagastus )
        return tagastus

    kupsised = leia_kupsised( )

    return render_template( 'sisselogimine.html', kupsised=kupsised )

@Veebileht.get( '/registreeri' )
def registreeri( ):
    [ sisselogitud, kasutajanimi ] = on_sisse_logitud( )

    if sisselogitud:
        return redirect( url_for( 'index' ) )

    kupsised = leia_kupsised( )

    return render_template( 'registreeri.html', kupsised=kupsised )

@Veebileht.get( '/' )
def index( ):
    [ sisselogitud, kasutajanimi ] = on_sisse_logitud( )

    if not sisselogitud:
        tagastus = make_response( redirect( url_for( 'sisselogimine' ) ) )
        tagastus = kustuta_kupsised( tagastus )
        return tagastus

    kupsised = leia_kupsised( )
    return render_template( 'index.html', kupsised=kupsised )

@Veebileht.route( '/logout' )
def logi_valja( ):
    kupsiste_haldaja = make_response( redirect( url_for( 'sisselogimine' ) ) )
    kupsiste_haldaja = kustuta_kupsised( kupsiste_haldaja )
    return kupsiste_haldaja

if __name__ == "__main__":
    Veebileht.run( debug=True )