import os
import uuid

from flask import Flask, request, render_template, redirect, url_for, make_response, Response, abort, escape, send_from_directory, jsonify
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


from sql import AndmebaasiSild, log, LEIA_KASUTAJA, LEIA_FAIL
from parooli_kontroll import kontrolli_parool
from kasutaja import Kasutaja
from fail import Fail

Veebileht = Flask( __name__ )
Andmebaas = AndmebaasiSild( 'root', '', 'sharex_site', 'localhost' )

PRAEGUNE_KAUST = os.path.dirname(os.path.abspath(__file__))
ULESLAADIMISTE_KAUST = os.path.join( PRAEGUNE_KAUST, 'uleslaadimised' ) + '/'
AVALIKKUSE_TASEMED = {
    'avalik': 0,
    'privaatne': 2
}

LUBATUD_FAILITUUBID = [ 'IMAGE/PNG', 'IMAGE/GIF', 'IMAGE/JPEG', 'IMAGE/JPG' ]

# Funktsioon, et kontrollida kas kasutaja on sisse logitud
def on_sisse_logitud( ) -> bool:
    api_voti = request.cookies.get( 'api_voti' )
    if api_voti is None:
        return False
    return Andmebaas.kas_api_voti_on_legaalne( api_voti )


# Püütonid decorator
# Loodud selleks et vähendada koodi kirjutamist funktsioonides, mis nõuavad et kasutaja on sisse logitud
def peab_olema_sisse_logitud( funktsioon ):
    def kontrollija( *args, **kwargs ):
        if on_sisse_logitud( ):
            funktsioon( args, kwargs )

        tagastus = make_response( redirect( url_for( 'sisselogimine' ) ) )
        tagastus = kustuta_kupsised( tagastus )
        return tagastus
    return kontrollija

def pealeht_kui_kasutaja_on_sisse_loginud( funktsioon ):
    def kontrollija( *args, **kwargs ):
        if on_sisse_logitud( ):
            tagastus = make_response( redirect( url_for( 'index' ) ) )
            tagastus = kustuta_kupsised( tagastus )
            return tagastus

        funktsioon( args, kwargs )
    return kontrollija

def leia_kupsised( ) -> dict:
    kupsised = list( request.cookies.items( ) )

    tagastatavad_kupsised = { }
    for kupsis in kupsised:
        tagastatavad_kupsised[ kupsis[ 0 ] ] = kupsis[ 1 ]

    return tagastatavad_kupsised

# 🐷🍪
def sea_kupsis( tagastus: Response, kupsise_nimi: str, uus_vaartus: any ):
    tagastus.set_cookie( kupsise_nimi, uus_vaartus )
    log( f'kupsise uus vaartus { kupsise_nimi }->{ uus_vaartus }' )
    return tagastus

def kustuta_kupsised( tagastus: Response ):
    kupsised = leia_kupsised( )
    for kupsis in kupsised:
        tagastus.delete_cookie( kupsis )
    print( 'kustutati koik kupsised' )
    return tagastus

def lae_fail_ules( fail: FileStorage, kasutaja: Kasutaja ) -> dict:
    failinimi = fail.name
    failituup = fail.content_type

    korrastatud_failinimi = secure_filename( failinimi )

    # kas fail on lubatud
    if not failituup.upper( ) in LUBATUD_FAILITUUBID:
        return { 'laeti_ules': False }

    failituup = failituup.replace( 'image/', '' ) # korrastame failituubu salvestamise viisi
    # salvestatakse png/jpeg/mp4 vms

    unikaalne_nimi = str( uuid.uuid4( ) )

    api_voti = kasutaja.api_voti

    # tagastame True kui faili info loomine andmebaasis laks labi
    fail_loodi_andmebaasis = Andmebaas.loo_fail( kasutaja, korrastatud_failinimi, unikaalne_nimi, failituup )

    if not fail_loodi_andmebaasis:
        return { 'laeti_ules': False }

    # kui kasutajal pole uleslaadimiste kausta, loome selle
    kasutaja_kausta_path = os.path.join( ULESLAADIMISTE_KAUST, api_voti )
    if not os.path.isdir( kasutaja_kausta_path ):
        os.makedirs( kasutaja_kausta_path )

    fail.save( os.path.join( kasutaja_kausta_path, unikaalne_nimi + f'.{ failituup }' ) )
    return { 'laeti_ules': True, 'url': 'http://127.0.0.1:5000/fail/' + unikaalne_nimi  }

# Sharexi meediafailide vastuvotja
@Veebileht.post( '/lae_ules' )
def meediafailide_vastuvotja( ):
    # https://getsharex.com/docs/custom-uploader
    saadud_api_voti = request.headers.get( 'Authorization' )
    kasutaja_api_voti_on_olemas = Andmebaas.kas_api_voti_on_legaalne( saadud_api_voti )

    if not kasutaja_api_voti_on_olemas:
        log( f'API võtit "{ saadud_api_voti }" ei leitud.' )
        abort( 400, 'API võtit ei leitud.' )

    saadud_fail = request.files.get( 'file' )

    if saadud_fail is None:
        abort( 422, 'Faili ei leitud.' )

    # faili_avalikkus = AVALIKKUSE_TASEMED['avalik']

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], saadud_api_voti )

    uleslaadimine = lae_fail_ules( saadud_fail, kasutaja )

    if not uleslaadimine.get( 'laeti_ules' ):
        return jsonify( veateade='Serveri error.' )

    print( uleslaadimine.get( 'url' ) )
    return jsonify( url=uleslaadimine.get( 'url' ) )


@Veebileht.post( '/registreeri' ) # Lubame ainult POST requestid
def api_registreeri( ):
    lehele_saadetud_info = request.form

    kasutajanimi = lehele_saadetud_info[ 'kasutajanimi' ].lower( )
    kasutaja_on_olemas = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'nimi' ], kasutajanimi )

    tagastus = make_response( redirect( url_for( 'registreeri' ) ) )

    if kasutaja_on_olemas:
        tagastus = sea_kupsis( tagastus, 'veateade', 'Kasutajanimi on olemas.' )
        return tagastus

    parool = lehele_saadetud_info[ 'parool' ]
    [ parool_on_tugev, veateade ] = kontrolli_parool( parool )

    if not parool_on_tugev:
        tagastus = sea_kupsis( tagastus, 'veateade', veateade )
        return tagastus

    loodud_kasutaja = Andmebaas.loo_kasutaja( kasutajanimi, parool )

    if loodud_kasutaja.on_tuhi( ):
        tagastus = sea_kupsis( tagastus, 'veateade', 'Kasutaja loomisel esines viga.' )
        return tagastus

    tagastus = sea_kupsis( tagastus, 'veateade', '' )
    tagastus = sea_kupsis( tagastus, 'api_voti', loodud_kasutaja.api_voti )

    return tagastus

@Veebileht.post( '/sisselogimine' )
def api_login( ):
    lehele_saadetud_info = request.form
    parool = lehele_saadetud_info[ 'parool' ]
    kupsiste_haldaja = make_response( redirect( url_for( 'sisselogimine' ) ) )

    [ kas_parool_taidab_nouded, _ ] = kontrolli_parool( parool )
    if not kas_parool_taidab_nouded:
        kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', 'Parool ei täida nõudeid..' )
        return kupsiste_haldaja

    kasutajanimi = lehele_saadetud_info[ 'kasutajanimi' ].lower( )
    leitud_kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'nimi' ], kasutajanimi )
    print( kasutajanimi, leitud_kasutaja )

    if leitud_kasutaja.on_tuhi( ):
        kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', 'Kasutajanime ei ole olemas.' )
        return kupsiste_haldaja

    kas_parool_kattub = leitud_kasutaja.parool_kattub( parool )

    if not kas_parool_kattub:
        kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', 'Parool on vale.' )
        return kupsiste_haldaja

    kupsiste_haldaja = make_response( redirect( url_for( 'index' ) ) )
    kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', '' )
    kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'api_voti', leitud_kasutaja.api_voti )

    return kupsiste_haldaja

@pealeht_kui_kasutaja_on_sisse_loginud
@Veebileht.get( '/sisselogimine' )
def sisselogimine( ):
    kupsised = leia_kupsised( )
    return render_template( 'sisselogimine.html', kupsised=kupsised )

@pealeht_kui_kasutaja_on_sisse_loginud
@Veebileht.get( '/registreeri' )
def registreeri( ):
    kupsised = leia_kupsised( )
    return render_template( 'registreeri.html', kupsised=kupsised )

@peab_olema_sisse_logitud
@Veebileht.get( '/' )
def index( ):
    kupsised = leia_kupsised( )

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], kupsised.get( 'api_voti' ) )

    meediafailid = Andmebaas.leia_kasutaja_failid( kasutaja, 0, 12 )

    return render_template( 'index.html', kupsised=kupsised, meediafailid=meediafailid )

@peab_olema_sisse_logitud
@Veebileht.get( '/sharexi_konfiguratsioon' )
def tagasta_sharexi_config( ):
    api_voti = request.cookies.get( 'api_voti' )

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], api_voti )

    return {
        "Name": "localhost uploader",
        "DestinationType": "ImageUploader, TextUploader, FileUploader",
        "RequestMethod": "POST",
        "RequestURL": "http://127.0.0.1:5000" + url_for( 'meediafailide_vastuvotja' ),
        "Headers": {
            "Authorization": kasutaja.api_voti
        },
        "Body": "MultipartFormData",
        "FileFormName": "file",
        "URL": "$json:url",
        "ThumbnailURL": "$json:esipilt$",
        "Error": "$json:veateade$"
    }

@Veebileht.get( '/fail/<string:eriline_faili_nimi>' )
def failikuvaja( eriline_faili_nimi: str ):
    # Siin pole vaja vaadata kas kasutaja on sisse logitud sest praegu saavad pilte vaadata ukskoik kellel on pildi link
    faili_unikaalne_nimi = escape( eriline_faili_nimi )
    print( str( faili_unikaalne_nimi ) )
    fail = Andmebaas.leia_fail( LEIA_FAIL[ 'unikaalne_nimi' ], str( faili_unikaalne_nimi ) )

    if fail.on_tuhi( ):
        return 'Faili ei leitud.'

    kasutaja = Andmebaas.leia_uleslaetud_faili_kasutaja( fail )
    if kasutaja.on_tuhi( ):
        return 'Kasutajat ei leitud'

    kasutaja_api_voti = kasutaja.api_voti
    faili_tuup = fail.tuup

    return send_from_directory( os.path.join( ULESLAADIMISTE_KAUST, kasutaja_api_voti ),  f'{ eriline_faili_nimi }.{ faili_tuup }' )

@Veebileht.route( '/logout' )
def logi_valja( ):
    kupsiste_haldaja = make_response( redirect( url_for( 'sisselogimine' ) ) )
    kupsiste_haldaja = kustuta_kupsised( kupsiste_haldaja )
    return kupsiste_haldaja

if __name__ == "__main__":
    Veebileht.run( debug=True )