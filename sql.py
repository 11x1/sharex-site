import os

from cryptography.fernet import Fernet
from mysql import connector
from mysql.connector import errorcode # https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html

import debug
from kasutaja import Kasutaja
from fail import Fail

PRAEGUNE_KAUST = os.path.dirname( os.path.abspath( __file__ ) )
ULESLAADIMISTE_KAUST = os.path.join( PRAEGUNE_KAUST, 'uleslaadimised' ) + '/'

Logija = debug.Logija( )
log = Logija.log

TABELI_NIMI = {
    'kasutajad'         : 'kasutajad',
    'uleslaadimised'    : 'uleslaadimised',
    'failid'            : 'failid'
}

# salvestame vajalikud tabelinimed listina et saaksime neid programmi kävivitades kontrollida
VAJALIKUD_TABELID = list( TABELI_NIMI.keys( ) )
LOO_TABEL = {
    "kasutajad": f"CREATE TABLE { TABELI_NIMI['kasutajad'] } ( id serial primary key not null, kasutajanimi varchar( 32 ) not null, parool varchar( 256 ) not null, api_voti varchar( 128 ) not null )",
    "uleslaadimised": f"CREATE TABLE { TABELI_NIMI['uleslaadimised'] } ( kasutaja_id int not null, faili_id int not null )",
    "failid": f"CREATE TABLE { TABELI_NIMI['failid'] } ( id serial primary key not null, nimi varchar( 128 ) not null, unikaalne_nimi varchar( 128 ) not null, failituup varchar( 32 ) not null )"
}

INDEKSID = {
    'kasutaja_id'           : 0,
    'kasutajanimi'          : 1,
    'parool'                : 2,
    'api_voti'              : 3,
    'faili_id'              : 1,
    'id'                    : 0,
    'failinimi'             : 1,
    'unikaalne_failinimi'   : 2,
    'failitüüp'             : 3
}

# väljad millega saame kasutajat otsida
LEIA_KASUTAJA = {
    'id'        : 'id',
    'nimi'      : 'kasutajanimi',
    'parool'    : 'parool',
    'api_voti'  : 'api_voti'
}

# väljad millega saame faili otsida
LEIA_FAIL = {
    'id'                : 'id',
    'nimi'              : 'nimi',
    'unikaalne_nimi'    : 'unikaalne_nimi',
    'failituup'         : 'failituup'
}

TUHI_KASUTAJA   = Kasutaja( None, None, None, None )
TUHI_FAIL       = Fail( None, None, None, None )

def kustuta_failid_kaustast( kausta_aadress: str ):
    for failinimi in os.listdir( kausta_aadress ):
        os.remove( os.path.join( kausta_aadress, failinimi ) )
    os.rmdir( kausta_aadress )

class AndmebaasiSild:
    def __init__( self, kasutajanimi: str, parool: str, andmebaas: str, host: str ) -> None:
        self.kasutajanimi = kasutajanimi
        self.parool = parool
        self.andmebaas = andmebaas
        self.host = host

        andmebaas_on_olemas = self.andmebaas_on_olemas() # kontrollib kas andmebaas on juba olemas

        if not andmebaas_on_olemas:
            self.loo_andmebaas( )

        vajalikud_tabelid = self.tagasta_vajalikud_tabelid() #
        for tabeli_nimi in vajalikud_tabelid:
            self.loo_tabel( tabeli_nimi )

    def loo_andmebaas( self ) -> None:
        try:
            # ei kasuta self.uhenda( ) sest meil on vaja luua andmebaas.
            # sest self.ühenda üritab juba andmebaasiga ühendada
            uhendus = connector.connect(
                user        = self.kasutajanimi,
                password    = self.parool,
                host        = self.host
            )

            looja = uhendus.cursor( )
            looja.execute( f'CREATE DATABASE `{ self.andmebaas }`' )
            log( f'Loodi andmebaas { self.andmebaas }' )

            looja.close( )
        except connector.Error as error:
            # Kui ei saa andmebaasiga ühendust luua siis lõpetame programmi töö
            if error.errno == errorcode.CR_CONN_HOST_ERROR:
                print( 'Host\'i ei leitud.' )
            elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print( 'Ei saanud andmebaasiga uhendust luua. Palun kontrolli oma kasutaja andmed ule.' )
            else:
                print( f'Ei saanud andmebaasiga uhendust luua.\n{ error }' )
            exit( )

    def loo_tabel( self, tabeli_nimi: str ) -> None:
        if not tabeli_nimi in VAJALIKUD_TABELID:
            print( 'Tabeli nimi ei ole vajalike tabelite hulgas.' )
            exit( )

        uhendus = self.uhenda( )

        looja = uhendus.cursor( )
        looja.execute( LOO_TABEL[ tabeli_nimi ] )
        looja.close( )

        uhendus.commit( ) # salvestame andmebaasis läbiviidud muudatused
        log( f'Loodi tabel { tabeli_nimi } käsuga { LOO_TABEL[ tabeli_nimi ] }' )

    def uhenda( self ):
        log( f'{ self.kasutajanimi }({ len( self.parool ) }) uhendab andmebaasiga { self.andmebaas }({ self.host })' )
        uhendus = connector.connect(
            user     = self.kasutajanimi,
            password = self.parool,
            host     = self.host,
            database = self.andmebaas,
        )

        return uhendus

    # tagastab kõik väljad
    def leia( self, tabel: str, vali: str, vaartus: any ) -> list:
        uhendus = self.uhenda( ) # ühendame andmebaasiga
        otsija = uhendus.cursor( ) # cursori abiga saame läbi viia käske andmebaasis

        log( f'Otsitakse { tabel }->{ vali } vaartust { vaartus }.' )
        data = {
            'vaartus': vaartus
        }
        otsija.execute( f'SELECT * FROM `{ tabel }` WHERE `{ tabel }`.`{ vali }` = %(vaartus)s', data ) # %(nimi)s on mysql mooduli poolt soovitatud formatiimisviis
        # "SELECT * FROM `tabelinimi` WHERE `tabelinimi`.`väli` = otsitav_väärtus"
        leitud = otsija.fetchall( )

        otsija.close( )
        uhendus.close( ) # siin ei pea muudatusi läbi viima sest tegu on ainult info tagastamisega

        log( f'Tagastati { len( leitud ) } valja.' )
        return leitud

    # tagastab ainult ühe välja
    def leia_uks( self, tabel: str, vali: str, vaartus: any ) -> tuple:
        leitud = self.leia( tabel, vali, vaartus )
        if len( leitud ) == 0:
            return ( )
        return leitud[ 0 ]

    def andmebaas_on_olemas( self ) -> bool:
        log( f'{ self.kasutajanimi }({ len( self.parool ) }) testib uhendust andmebaasiga { self.andmebaas }({ self.host }). ' )
        try:
            # proovime ühendada andmebaasiga
            self.uhenda( )
        except connector.Error as error:
            if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print( 'Ei saanud andmebaasiga uhendust luua. Palun kontrolli oma kasutaja andmed ule.' )
            elif error.errno == errorcode.ER_DATABASE_NAME:
                print( f'Andmebaasi "{ self.andmebaas }" ei leitud.' )
            else:
                print(f'Ei saanud andmebaasiga uhendust luua (error #{ error.errno }).')
            return False

        log( 'uhendus loodi edukalt.' )
        return True

    def tagasta_vajalikud_tabelid( self ) -> list:
        vajalikud_tabelid = [ ]
        try:
            uhendus = self.uhenda()
            for tabeli_nimi in VAJALIKUD_TABELID:
                otsija = uhendus.cursor()
                otsija.execute(f'SHOW TABLES LIKE %(tabel)s', { 'tabel': tabeli_nimi } )

                if len( otsija.fetchall( ) ) <= 0:
                    vajalikud_tabelid.append( tabeli_nimi )
        except Exception as e:
            print( e )
            exit( )

        if len( vajalikud_tabelid ) > 0:
            log( f'Tabeleid { ", ".join( vajalikud_tabelid ) } ei leitud.' )
            return vajalikud_tabelid
        else:
            log( f'Vajalikud tabelid on juba loodud. { VAJALIKUD_TABELID }' )
            return [ ]

    def leia_kasutaja( self, millega: LEIA_KASUTAJA, leitav_vaartus ) -> Kasutaja:
        if millega not in list( LEIA_KASUTAJA.values( ) ):
            log( f'Kasutajat üritati leida võtmega "{ millega }"("{ leitav_vaartus }")' )
            return TUHI_KASUTAJA

        leitud = self.leia_uks( TABELI_NIMI[ 'kasutajad' ], millega, leitav_vaartus )

        if leitud == ( ):
            return TUHI_KASUTAJA

        return Kasutaja( leitud[ INDEKSID[ 'kasutaja_id' ] ],
                         leitud[ INDEKSID[ 'kasutajanimi' ] ],
                         leitud[ INDEKSID[ 'api_voti' ] ],
                         leitud[ INDEKSID[ 'parool' ] ] )

    def leia_fail( self, millega: LEIA_FAIL, leitav_vaartus ) -> Fail:
        if millega not in LEIA_FAIL:
            log( f'Kasutajat üritati leida võtmega "{ millega }"("{ leitav_vaartus }")' )
            return TUHI_FAIL

        leitud = self.leia_uks( TABELI_NIMI[ 'failid' ], millega, leitav_vaartus )

        return Fail( leitud[ INDEKSID[ 'id' ] ],
                     leitud[ INDEKSID[ 'failinimi' ] ],
                     leitud[ INDEKSID[ 'unikaalne_failinimi' ] ],
                     leitud[ INDEKSID[ 'failitüüp' ] ] )

    def leia_uleslaetud_faili_kasutaja( self, fail: Fail ) -> Kasutaja:
        leitud = self.leia_uks( TABELI_NIMI[ 'uleslaadimised' ], 'faili_id', fail.id )
        if len( leitud ) == 0:
            return TUHI_KASUTAJA

        kasutaja_id = leitud[ INDEKSID[ 'kasutaja_id' ] ]
        kasutaja = self.leia_kasutaja( LEIA_KASUTAJA[ 'id' ], kasutaja_id )

        return kasutaja

    def leia_otsingu_failid( self, kasutaja: Kasutaja, failinimi: str, sildid: list, tuubid: list, start: int, lopp: int ) -> list:
        uhendus = self.uhenda( )
        otsija = uhendus.cursor( )

        info = {
            'failinimi'     : failinimi,
            'sildid'        : sildid[0],
            'kasutaja_id'   : kasutaja.id
        }

        jm = '"'

        otsing = f"SELECT { TABELI_NIMI[ 'failid' ] }.{ LEIA_FAIL[ 'id' ] }, { TABELI_NIMI[ 'failid' ] }.{ LEIA_FAIL[ 'nimi' ] }, { TABELI_NIMI[ 'failid' ] }.{ LEIA_FAIL[ 'unikaalne_nimi' ] }, { TABELI_NIMI[ 'failid' ] }.{ LEIA_FAIL[ 'failituup' ] } FROM { TABELI_NIMI[ 'failid' ] }, { TABELI_NIMI[ 'uleslaadimised' ] } WHERE { TABELI_NIMI[ 'failid' ] }.{ LEIA_FAIL[ 'nimi' ] } LIKE %(failinimi)s AND { TABELI_NIMI[ 'failid' ] }.{ LEIA_FAIL[ 'failituup' ] } IN ( { jm + ( jm + ', ' + jm).join( tuubid ) + jm } ) AND { TABELI_NIMI[ 'uleslaadimised' ] }.kasutaja_id = %(kasutaja_id)s AND { TABELI_NIMI[ 'uleslaadimised' ] }.faili_id = { TABELI_NIMI[ 'failid' ] }.{ LEIA_FAIL[ 'id' ] }"

        otsija.execute( otsing, info )

        leitud = otsija.fetchall( )

        failid = map( lambda faili_info: Fail(
            faili_info[ INDEKSID[ 'faili_id' ] ],
            faili_info[ INDEKSID[ 'failinimi' ] ],
            faili_info[ INDEKSID[ 'unikaalne_failinimi' ] ],
            faili_info[ INDEKSID[ 'failitüüp' ] ]
        ), leitud[ ::-1 ] )

        failid = list( failid )

        vahemik = lopp - start

        lehti_enne = start // vahemik
        lehti_parast = ( len( failid ) - lopp ) // vahemik + 1

        if start > len( failid ):
            return [ [ ], lehti_enne, 0 ]
        elif lopp > len( failid ):
            return [ failid[ start:len( failid ) ], lehti_enne, 0 ]

        return [ failid[ start:lopp ], lehti_enne, lehti_parast ]

    def kas_api_voti_on_legaalne( self, api_voti: str ) -> bool:
        leitud = self.leia( 'kasutajad', 'api_voti', api_voti )
        return len( leitud ) > 0

    def loo_kasutaja( self, kasutajanimi: str, plaintext_parool: str ) -> Kasutaja:
        # Eeldame, et kasutaja olemasolu on juba kontrollitud
        # Samuti on kontrollitud ka parooli tugevus
        api_voti = Fernet.generate_key( )

        krupter = Fernet( api_voti )
        parool = krupter.encrypt( plaintext_parool.encode( 'utf-8' ) )

        uhendus = self.uhenda( )

        sisestaja = uhendus.cursor( )
        sisestaja.execute( 'INSERT INTO kasutajad ( kasutajanimi, parool, api_voti ) VALUES ( %s, %s, %s )', ( kasutajanimi, parool, api_voti.decode( 'utf-8' ) ) )
        uhendus.commit( )

        log( f'kasutaja { kasutajanimi } loodi edukalt' )

        uhendus.close( )

        kasutaja = self.leia_kasutaja( LEIA_KASUTAJA[ 'api_voti' ], api_voti )

        return kasutaja

    def vaheta_kasutaja_parool( self, kasutaja: Kasutaja, parool ) -> None:
        uhendus = self.uhenda( )

        krupter = Fernet( kasutaja.api_voti )

        uus_parool = krupter.encrypt( parool.encode( 'utf-8' ) )

        sisestaja = uhendus.cursor( )
        sisestaja.execute(
            f'UPDATE { TABELI_NIMI[ "kasutajad" ] } SET { LEIA_KASUTAJA[ "parool" ] } = %(uus_parool)s WHERE { LEIA_KASUTAJA[ "id" ] } = %(kasutaja_id)s',
            { 'uus_parool': uus_parool, 'kasutaja_id': kasutaja.id }
        )
        uhendus.commit( )
        sisestaja.close( )
        uhendus.close( )

    def loo_fail( self, kasutaja: Kasutaja, failinimi, unikaalne_nimi, failituup ) -> bool:
        # Eeldame, et failinimi on ule vaadatud ja kasutaja on sisse logitud
        uhendus = self.uhenda( )

        if len( failituup ) > 32 or len( failinimi ) > 128 or len( unikaalne_nimi ) > 128:
            return False

        sisestaja = uhendus.cursor( )
        sisestaja.execute( "INSERT INTO failid ( nimi, unikaalne_nimi, failituup ) VALUES( %s, %s, %s )", ( failinimi, unikaalne_nimi, failituup ) )
        uhendus.commit( )

        fail = self.leia_fail( LEIA_FAIL[ 'unikaalne_nimi' ], unikaalne_nimi )

        if fail == TUHI_FAIL:
            return False

        sisestaja.execute( "INSERT INTO uleslaadimised ( kasutaja_id, faili_id ) VALUES( %s, %s )", ( kasutaja.id, fail.id ) )
        uhendus.commit( )
        uhendus.close( )
        return True

    def kustuta_fail( self, fail ) -> bool:
        uhendus = self.uhenda( )
        kustutaja = uhendus.cursor( )
        if fail == TUHI_FAIL:
            return False

        kasutaja_id = self.leia_uks( TABELI_NIMI[ 'uleslaadimised' ], 'faili_id', fail.id )[ INDEKSID[ 'kasutaja_id' ] ]
        kasutaja = self.leia_kasutaja( LEIA_KASUTAJA[ 'id' ], kasutaja_id )

        if kasutaja == TUHI_KASUTAJA:
            return False

        kustutaja.execute( f"DELETE FROM { TABELI_NIMI[ 'uleslaadimised' ] } WHERE faili_id = %(faili_id)s", { 'faili_id': fail.id } )
        kustutaja.execute( f"DELETE FROM { TABELI_NIMI[ 'failid' ] } WHERE { LEIA_FAIL[ 'unikaalne_nimi' ] } = %(faili_unikaalne_nimi)s", { 'faili_unikaalne_nimi': fail.unikaalne_nimi } )

        os.remove( os.path.join( ULESLAADIMISTE_KAUST, kasutaja.api_voti, f"{ fail.unikaalne_nimi }.{ fail.tuup }" ) )

        uhendus.commit( )
        uhendus.close( )
        log( f'fail { fail } kustutati edukalt' )

        return True

    def kustuta_kasutaja( self, kasutaja: Kasutaja ) -> bool:
        uhendus = self.uhenda( )
        kustutaja = uhendus.cursor( )

        valjad = {
            'kasutaja_id': kasutaja.id
        }

        # Kustutame kasutaja tabelist kasutajad
        kustutaja.execute(
            f'DELETE FROM { TABELI_NIMI[ "kasutajad" ] } WHERE '
            f'{ LEIA_KASUTAJA[ "id" ] } = %(kasutaja_id)s',
            valjad
        )

        # Kustutame koik faili viited failide tabelist
        kustutaja.execute(
            f'DELETE FROM { TABELI_NIMI[ "failid" ] } WHERE { TABELI_NIMI[ "failid" ] }.{ LEIA_FAIL[ "id" ] } in ( SELECT faili_id FROM uleslaadimised WHERE kasutaja_id = %(kasutaja_id)s )',
            valjad
        )

        kustutaja.execute(
            f'DELETE FROM { TABELI_NIMI[ "uleslaadimised" ] } WHERE kasutaja_id = %(kasutaja_id)s',
            valjad
        )

        # Kustutame failid serverist
        try:
            kustuta_failid_kaustast( os.path.join( ULESLAADIMISTE_KAUST, kasutaja.api_voti ) )
        except Exception as e:
            log( f'Kasutaja { kasutaja } kustutamisel tekkis viga({ e })' )
            return False

        # Kustutame kasutaja andmebaasist
        kustutaja.execute(
            f'DELETE FROM { TABELI_NIMI[ "kasutajad" ] } WHERE { LEIA_KASUTAJA[ "id" ] } = %(kasutaja_id)s',
            valjad
        )

        kustutaja.close( )
        uhendus.commit( )

        # Tagastame toevaartuse kui kasutaja kustutati edukalt
        return True

    def leia_info( self ) -> dict:
        andmed = {
            'kasutajaid': 0,
            'uleslaadimisi': 0,
            'maht': 0
        }

        uhendus = self.uhenda( )
        otsija = uhendus.cursor( )

        otsija.execute( f'SELECT { LEIA_KASUTAJA[ "api_voti" ] } FROM { TABELI_NIMI[ "kasutajad" ] }' )
        andmed[ 'kasutajaid' ] = len( otsija.fetchall( ) )

        otsija.execute( f'SELECT kasutaja_id FROM { TABELI_NIMI[ "uleslaadimised" ] }' )
        andmed[ 'uleslaadimisi' ] = len( otsija.fetchall( ) )

        uleslaadimiste_kaustad = os.listdir( ULESLAADIMISTE_KAUST )
        for kaust in uleslaadimiste_kaustad:
            kausta_path = os.path.join( ULESLAADIMISTE_KAUST, kaust )
            for failinimi in os.listdir( kausta_path ):
                andmed[ 'maht' ] += os.path.getsize( os.path.join( kausta_path, failinimi ) ) / ( 1024 * 1024 )

        andmed[ 'maht' ] = round( andmed[ 'maht' ], 2 )

        return andmed

    def kuva_kasutajad( self ) -> None:
        uhendus = self.uhenda( )

        otsija = uhendus.cursor( )
        otsija.execute( 'SELECT kasutajanimi FROM kasutajad' )

        print( otsija.fetchall( ) )