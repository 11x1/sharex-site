import json
import os  # Kasutajate failide leidmiseks kasutades
import uuid  # Eriliste failinimede genereerimine

from flask import Flask, request, render_template, redirect, url_for, make_response, Response, abort, escape, send_from_directory, jsonify
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from sql import AndmebaasiSild, log, LEIA_KASUTAJA, LEIA_FAIL
from parooli_kontroll import kontrolli_parool
from kasutaja import Kasutaja

Veebileht = Flask( __name__ )

absoluutne_path = os.path.dirname( os.path.abspath( __file__ ) )
sql_config_path = os.path.join( absoluutne_path, 'sql_config.json' )

andmebaasi_fail = open( sql_config_path, 'r' )
andmebaasi_andmed = json.load( andmebaasi_fail )
andmebaasi_fail.close( )

Andmebaas = AndmebaasiSild(
    kasutajanimi    = andmebaasi_andmed[ 'kasutajanimi' ],
    parool          = andmebaasi_andmed[ 'parool' ],
    andmebaas       = andmebaasi_andmed[ 'andmebaas' ],
    host            = andmebaasi_andmed[ 'host' ]
)

PRAEGUNE_KAUST = os.path.dirname(os.path.abspath(__file__))
ULESLAADIMISTE_KAUST = os.path.join( PRAEGUNE_KAUST, 'uleslaadimised' ) + '/'
AVALIKKUSE_TASEMED = {
    'avalik': 0,
    'privaatne': 2
}

LUBATUD_FAILITUUBID = [ 'IMAGE/PNG', 'IMAGE/GIF', 'IMAGE/JPEG', 'IMAGE/JPG', 'VIDEO/MP4' ]

def loo_json_tagastus( staatus, sonum, suund ):
    return jsonify( {
        'status': staatus,
        'sonum': sonum,
        'suund': suund
    } )

def on_sisse_logitud( ) -> bool:
    api_voti = request.cookies.get( 'api_voti' )
    if api_voti is None:
        return False
    return Andmebaas.kas_api_voti_on_legaalne( api_voti )

def suuna_pealehele( ):
    return make_response( redirect( url_for( 'index' ) ) )

def logi_valja( ) -> Response:
    tagastus = make_response(redirect(url_for('sisselogimine')))
    tagastus = kustuta_kupsised(tagastus)
    return tagastus

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
    return tagastus

def lae_fail_ules( fail: FileStorage, kasutaja: Kasutaja ) -> dict:
    failinimi = "".join( fail.filename.split( '.' )[ :-1 ] )
    failituup = fail.content_type

    korrastatud_failinimi = secure_filename( failinimi )

    # kas fail on lubatud
    if not failituup.upper( ) in LUBATUD_FAILITUUBID:
        return { 'laeti_ules': False }

    failituup = failituup.split( '/' )[ -1 ].lower( ) # korrastame failituubu salvestamise viisi
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

    url = request.base_url
    url = '/'.join( url.split( '/' )[ :-1 ] )

    fail.save( os.path.join( kasutaja_kausta_path, unikaalne_nimi + f'.{ failituup }' ) )
    return { 'laeti_ules': True, 'url': url + '/fail/' + unikaalne_nimi  }

def leia_failid( lehe_nr: int, kasutaja: Kasutaja, failinimi: str, sildid, tuubid ):
    limiit = 12
    algus = ( lehe_nr - 1 ) * limiit
    lopp = algus + limiit

    [ leitud_failid, lehti_enne, lehti_parast ] = Andmebaas.leia_otsingu_failid( kasutaja, failinimi,
                                                                                 sildid.split( ',' ), tuubid, algus,
                                                                                 lopp )

    failid_json = list( map( lambda fail: fail.json_formaat( ), leitud_failid ) )

    failid_json.append(
        { 'lehti': { 'enne': lehti_enne, 'parast': lehti_parast } }
    )

    return failid_json


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
        log( 'Faili ei leitud.' )
        abort( 422, 'Faili ei leitud.' )

    # faili_avalikkus = AVALIKKUSE_TASEMED['avalik']

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], saadud_api_voti )

    uleslaadimine = lae_fail_ules( saadud_fail, kasutaja )

    if not uleslaadimine.get( 'laeti_ules' ):
        log( 'Uleslaadimisel laks viltu.' )
        return jsonify( veateade='Serveri error.' )

    return jsonify( url=uleslaadimine.get( 'url' ) )

@Veebileht.post( '/registreeri' ) # Lubame ainult POST requestid
def api_registreeri( ):
    lehele_saadetud_info = request.form

    kasutajanimi = lehele_saadetud_info[ 'kasutajanimi' ].lower( )
    kasutaja_on_olemas = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'nimi' ], kasutajanimi )

    tagastus = make_response( redirect( url_for( 'registreeri' ) ) )
    tagastus = sea_kupsis( tagastus, 'heateade', '' )

    if not kasutaja_on_olemas.on_tuhi( ):
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

    tagastus = make_response( redirect( url_for( 'sisselogimine' ) ) )
    tagastus = sea_kupsis( tagastus, 'veateade', '' )
    tagastus = sea_kupsis( tagastus, 'heateade', 'Kasutaja loodi edukalt.' )
    tagastus = sea_kupsis( tagastus, 'api_voti', loodud_kasutaja.api_voti )

    return tagastus

@Veebileht.post( '/sisselogimine' )
def api_login( ):
    lehele_saadetud_info = request.form
    parool = lehele_saadetud_info[ 'parool' ]
    kupsiste_haldaja = make_response( redirect( url_for( 'sisselogimine' ) ) )

    if leia_kupsised( ).get( 'veateade' ) != '':
        kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'heateade', '' )

    [ kas_parool_taidab_nouded, _ ] = kontrolli_parool( parool )
    if not kas_parool_taidab_nouded:
        kupsiste_haldaja = sea_kupsis( kupsiste_haldaja, 'veateade', 'Parool ei täida nõudeid.' )
        return kupsiste_haldaja

    kasutajanimi = lehele_saadetud_info[ 'kasutajanimi' ].lower( )
    leitud_kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'nimi' ], kasutajanimi )

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

@Veebileht.post( '/api/otsi' )
def api_otsi( ):
    if not on_sisse_logitud( ):
        return logi_valja( )

    failinimi = request.form.get( 'failinimi' )
    sildid = request.form.get( 'sildid' )
    tuubid = request.form.get( 'tuup' ).split( '|' )
    lehe_nr = int( request.form.get( 'lehe_nr' ) )

    api_voti = leia_kupsised( ).get( 'api_voti' )

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], api_voti )

    if kasutaja.on_tuhi( ):
        return loo_json_tagastus( 500, 'Kasutajat ei leitud.', url_for( 'sisselogimine' ) )

    failid_json = leia_failid( lehe_nr, kasutaja, failinimi, sildid, tuubid )

    return jsonify( failid_json )

@Veebileht.post( '/api/kustuta_fail/' )  # Saaks teah samamoodi nagu on /kustuta_veateade aga
def api_kustuta_fail( ):
    if not on_sisse_logitud( ):
        return logi_valja( )

    eriline_faili_nimi = request.form.get( 'faili_eriline_nimi' )
    faili_eriline_nimi = escape( eriline_faili_nimi )

    saadud_api_voti = request.form.get( 'api_voti' )

    fail = Andmebaas.leia_fail( LEIA_FAIL[ 'unikaalne_nimi' ], str( faili_eriline_nimi ) )

    if fail.on_tuhi( ):
        return loo_json_tagastus( 500, 'Fail on tühi.', '/' )

    uleslaetud_faili_kasutaja = Andmebaas.leia_uleslaetud_faili_kasutaja( fail )

    if uleslaetud_faili_kasutaja.on_tuhi( ) or uleslaetud_faili_kasutaja.api_voti != saadud_api_voti:
        return loo_json_tagastus( 500, 'Te ei ole faili omanik', '/' )

    kas_fail_kustutati = Andmebaas.kustuta_fail( fail )
    if not kas_fail_kustutati:
        return loo_json_tagastus( 500, 'Faili ei kustutatud.', '/' )

    return loo_json_tagastus( 200, 'Fail kustutatud', '/' )

@Veebileht.post( '/api/kustuta_kasutaja/' )
def api_kustuta_kasutaja( ):
    if not on_sisse_logitud( ):
        return logi_valja( )

    api_voti = leia_kupsised( ).get( 'api_voti' )

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ "api_voti" ], api_voti )
    if kasutaja.on_tuhi( ):
        tagastus = loo_json_tagastus( 400, 'Kasutajat ei leitud', '/' )

        tagastus = sea_kupsis( tagastus, 'veateade', 'Kasutajat ei leitud.' )

        return tagastus

    kasutaja_kustutati = Andmebaas.kustuta_kasutaja( kasutaja )
    if not kasutaja_kustutati:
        tagastus = loo_json_tagastus( 500, 'Kellad 🔔🔔🔔', '/' )

        tagastus = sea_kupsis( tagastus, 'veateade', 'Serveri error.' )

        return tagastus

    tagastus = loo_json_tagastus( 200, 'Kasutaja kustutati edukalt', '/sisselogimine' )

    tagastus = sea_kupsis( tagastus, 'veateade', '' )
    tagastus = sea_kupsis( tagastus, 'heateade', 'Kasutaja kustutati edukalt!' )

    return tagastus

@Veebileht.get( '/api/kustuta_veateade/' )
def api_kustuta_veateade( ):
    tagastus = loo_json_tagastus( 200, 'Veateade kustutatud', '/' )
    tagastus = sea_kupsis( tagastus, 'veateade', '' )
    return tagastus

@Veebileht.get( '/api/kustuta_heateade/' )
def api_kustuta_heateade( ):
    tagastus = loo_json_tagastus( 200, 'Heateade kustutatud', '/' )
    tagastus = sea_kupsis( tagastus, 'heateade', '' )
    return tagastus

@Veebileht.post( '/api/vaheta_parool' )
def api_vaheta_parool( ):
    if not on_sisse_logitud( ):
        return logi_valja( )

    tagasisuunamine = redirect( url_for( 'profiil' ) )

    uus_parool = request.form.get( 'uus_parool' )
    api_voti = leia_kupsised( ).get( 'api_voti' )

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], api_voti )

    if kasutaja is None:
        return logi_valja( )

    [ uus_parool_ok, pohjus ] = kontrolli_parool( uus_parool )

    if not uus_parool_ok:
        tagasisuunamine = sea_kupsis( tagasisuunamine, 'veateade', pohjus )
        return tagasisuunamine

    Andmebaas.vaheta_kasutaja_parool( kasutaja, uus_parool )

    tagasisuunamine = sea_kupsis( tagasisuunamine, 'heateade', 'Parool vahetati edukalt!' )
    return tagasisuunamine

@Veebileht.get( '/sisselogimine' )
def sisselogimine( ):
    if on_sisse_logitud( ):
        return suuna_pealehele( )

    kupsised = leia_kupsised( )
    return render_template( 'sisselogimine.html', kupsised=kupsised )

@Veebileht.get( '/registreeri' )
def registreeri( ):
    if on_sisse_logitud( ):
        return suuna_pealehele( )

    kupsised = leia_kupsised( )
    return render_template( 'registreeri.html', kupsised=kupsised )

@Veebileht.get( '/' )
def index( ):
    if not on_sisse_logitud( ):
        return logi_valja( )

    kupsised = leia_kupsised( )
    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], kupsised.get( 'api_voti' ) )

    meediafailid = leia_failid( 1, kasutaja, '%', '', [ 'png', 'jpg', 'jpeg', 'mp4', 'mov', 'gif' ] )

    andmebaas_info = Andmebaas.leia_info( )

    return render_template( 'index.html',
                            kupsised=kupsised,
                            andmebaas_info=andmebaas_info,
                            kasutaja=kasutaja,
                            meediafailid=meediafailid[ :-1 ] )

@Veebileht.get( '/profiil' )
def profiil( ):
    if not on_sisse_logitud( ):
        return logi_valja( )

    kupsised = leia_kupsised( )
    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], kupsised.get( 'api_voti' ) )

    return render_template( 'profiil.html',
                            kupsised=kupsised,
                            kasutaja=kasutaja )

@Veebileht.get( '/sharexi_konfiguratsioon' )
def tagasta_sharexi_config( ):
    if not on_sisse_logitud( ):
        return logi_valja( )

    api_voti = request.cookies.get( 'api_voti' )

    kasutaja = Andmebaas.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], api_voti )

    url = request.base_url  # siin saame 'http(s)://url/sharexi_konfiguratsioon' sest request route on /sharexi_konfiguratsioon

    # saaks strip-i kasutada aga testimise jarel kaotas see ka http alguse
    url = '/'.join( url.split( '/' )[ :-1 ] ) + url_for( "meediafailide_vastuvotja" )  # url mis on valmis seattud vast votma uleslaadimisi

    return {
        "Name": "localhost uploader",
        "DestinationType": "ImageUploader, FileUploader",
        "RequestMethod": "POST",
        "RequestURL": url,
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