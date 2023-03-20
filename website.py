import os
import uuid

from sql import AndmebaasiSild, log
from parooli_kontroll import kontrolli_parool

from flask import Flask, request, render_template, redirect, url_for, make_response, Response, abort, escape, send_from_directory, jsonify
from werkzeug.utils import secure_filename

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
def on_sisse_logitud( ) -> list[ bool, str ]:
    api_voti = request.cookies.get( 'api_voti' )
    if api_voti is None:
        return [ False, '' ]
    [ legaalne_voti, kasutajanimi, _ ] = Andmebaas.kas_api_voti_on_legaalne( api_voti )
    return [ legaalne_voti, kasutajanimi ]

def leia_kupsised( ) -> dict:
    kupsised = list( request.cookies.items( ) )

    tagastatavad_kupsised = { }
    for kupsis in kupsised:
        tagastatavad_kupsised[ kupsis[ 0 ] ] = kupsis[ 1 ]

    return tagastatavad_kupsised

# 🐷🍪
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

def lae_fail_ules( fail, kasutaja_id: int ) -> dict:
    failinimi = fail.name
    failituup = fail.content_type

    korrastatud_failinimi = secure_filename( failinimi )

    if not failituup.upper( ) in LUBATUD_FAILITUUBID:
        return { 'laeti_ules': False }

    failituup = failituup.replace( 'image/', '' ) # korrastame failituubu salvestamise viisi
    # salvestatakse png/jpeg/mp4 vms

    eriline_nimi = str( uuid.uuid4( ) )

    api_voti = Andmebaas.leia_kasutaja_api_voti( kasutaja_id )

    # tagastame True kui faili info loomine andmebaasis laks labi
    fail_loodi_andmebaasis = Andmebaas.loo_fail( kasutaja_id, korrastatud_failinimi, failituup, eriline_nimi )

    if not fail_loodi_andmebaasis:
        return { 'laeti_ules': False }

    # kui kasutajal pole uleslaadimiste kausta, loome selle
    kasutaja_kausta_path = os.path.join( ULESLAADIMISTE_KAUST, api_voti )
    if not os.path.isdir( kasutaja_kausta_path ):
        os.makedirs( kasutaja_kausta_path )

    fail.save( os.path.join( kasutaja_kausta_path, eriline_nimi + f'.{ failituup }' ) )
    return { 'laeti_ules': True, 'url': 'http://127.0.0.1:5000/fail/' + eriline_nimi  }

# Sharexi meediafailide vastuvotja
@Veebileht.post( '/lae_ules' )
def meediafailide_vastuvotja( ):
    # https://getsharex.com/docs/custom-uploader
    saadud_api_voti = request.headers.get( 'Authorization' )
    [ on_olemas, _, kasutaja_id ] = Andmebaas.kas_api_voti_on_legaalne( saadud_api_voti )
    print( on_olemas, kasutaja_id, saadud_api_voti  )
    if not on_olemas:
        log( f'API võtit "{ saadud_api_voti }" ei leitud.' )
        abort( 400, 'API võtit ei leitud.' )

    fail = request.files.get( 'file' )

    if fail is None:
        abort( 422, 'Faili ei leitud.' )

    # faili_avalikkus = AVALIKKUSE_TASEMED['avalik']

    uleslaadimine = lae_fail_ules( fail, kasutaja_id )

    if not uleslaadimine.get( 'laeti_ules' ):
        abort( 422, 'Serveri error.' )

    print( uleslaadimine.get( 'url' ) )
    return jsonify( url=uleslaadimine.get( 'url' ) )


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
    [ sisselogitud, _ ] = on_sisse_logitud( )

    if sisselogitud:
        tagastus = make_response( redirect( url_for( 'index' ) ) )
        tagastus = kustuta_kupsised( tagastus )
        return tagastus

    kupsised = leia_kupsised( )

    return render_template( 'sisselogimine.html', kupsised=kupsised )

@Veebileht.get( '/registreeri' )
def registreeri( ):
    [ sisselogitud, _ ] = on_sisse_logitud( )

    if sisselogitud:
        return redirect( url_for( 'index' ) )

    kupsised = leia_kupsised( )

    return render_template( 'registreeri.html', kupsised=kupsised )

@Veebileht.get( '/' )
def index( ):
    [ sisselogitud, _ ] = on_sisse_logitud( )

    if not sisselogitud:
        tagastus = make_response( redirect( url_for( 'sisselogimine' ) ) )
        tagastus = kustuta_kupsised( tagastus )
        return tagastus

    kupsised = leia_kupsised( )
    return render_template( 'index.html', kupsised=kupsised )

@Veebileht.get( '/sharexi_konfiguratsioon' )
def tagasta_sharexi_config( ):
    [ sisse_logitud, kasutajanimi ] = on_sisse_logitud( )
    if not sisse_logitud:
        tagastus = make_response( redirect( url_for( 'logi_valja' ) ) )
        tagastus = kustuta_kupsised( tagastus )
        return tagastus

    return {
        "Name": "awawawawawaw lahe uploader!!!!",
        "DestinationType": "ImageUploader, TextUploader, FileUploader",
        "RequestMethod": "POST",
        "RequestURL": "http://127.0.0.1:5000" + url_for( 'meediafailide_vastuvotja' ),
        "Headers": {
            "Authorization": Andmebaas.leia_kasutaja_api_voti( kasutajanimi )
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
    faili_id = Andmebaas.leia_faili_id( str( faili_unikaalne_nimi ) )

    if faili_id == -1:
        return 'Faili ei leitud.'

    kasutaja_id = Andmebaas.leia_uleslaetud_faili_kasutaja_id( faili_id )
    if kasutaja_id == -1:
        return 'Faili ei leitud'

    kasutaja_api_voti = Andmebaas.leia_kasutaja_api_voti( kasutaja_id )

    faili_tuup = Andmebaas.leia_faili_tuup( faili_id )

    return send_from_directory( os.path.join( ULESLAADIMISTE_KAUST, kasutaja_api_voti ),  f'{ eriline_faili_nimi }.{ faili_tuup }' )

@Veebileht.route( '/logout' )
def logi_valja( ):
    kupsiste_haldaja = make_response( redirect( url_for( 'sisselogimine' ) ) )
    kupsiste_haldaja = kustuta_kupsised( kupsiste_haldaja )
    return kupsiste_haldaja

if __name__ == "__main__":
    Veebileht.run( debug=True )