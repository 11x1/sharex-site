from cryptography.fernet import Fernet
from mysql import connector
from mysql.connector import errorcode # https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
import debug

Logija = debug.Logija( )
log = Logija.log

VAJALIKUD_TABELID = [ 'kasutajad', 'uleslaadimised', 'failid' ]
LOO_TABEL = {
    "kasutajad": "CREATE TABLE kasutajad ( id serial primary key not null, kasutajanimi varchar( 32 ) not null, parool varchar( 256 ) not null, api_voti varchar( 128 ) not null )",
    "uleslaadimised": "CREATE TABLE uleslaadimised ( kasutaja_id int not null, faili_id int not null )",
    "failid": "CREATE TABLE failid ( id serial primary key not null, nimi varchar( 128 ) not null, unikaalne_nimi varchar( 128 ) not null, failituup varchar( 32 ) not null )"
}

class AndmebaasiSild:
    def __init__( self, kasutajanimi: str, parool: str, andmebaas: str, host: str ) -> None:
        self.kasutajanimi = kasutajanimi
        self.parool = parool
        self.andmebaas = andmebaas
        self.host = host

        peaks_looma_andmebaasi = self.test( )

        if peaks_looma_andmebaasi:
            self.loo_andmebaas( )

        vajalikud_tabelid = self.test_tabelid( )
        for tabeli_nimi in vajalikud_tabelid:
            print( tabeli_nimi )
            self.loo_tabel( tabeli_nimi )

    def loo_andmebaas( self ):
        try:
            # ei kasuta self.uhenda( ) sest meil on vaja luua andmebaas.
            uhendus = connector.connect(
                user=self.kasutajanimi,
                password=self.parool,
                host=self.host
            )

            looja = uhendus.cursor( )
            looja.execute( f'CREATE DATABASE %(andmebaas)s', { 'andmebaas': self.andmebaas } )
            log( f'Loodi andmebaas { self.andmebaas }' )

            looja.close( )
        except connector.Error as error:
            if error.errno == errorcode.CR_CONN_HOST_ERROR:
                print( 'Host\'i ei leitud.' )
            elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print( 'Ei saanud andmebaasiga uhendust luua. Palun kontrolli oma kasutaja andmed ule.' )
            else:
                print( f'Ei saanud andmebaasiga uhendust luua.\n{ error }' )
            exit( )

    def loo_tabel( self, tabeli_nimi: str ):
        if not tabeli_nimi in VAJALIKUD_TABELID:
            print( 'Tabeli nimi ei ole vajalike tabelite hulgas.' )
            exit( )

        uhendus = self.uhenda( )

        looja = uhendus.cursor( )
        looja.execute( LOO_TABEL[ tabeli_nimi ] )
        looja.close( )
        log( f'Loodi tabel { tabeli_nimi } kasuga { LOO_TABEL[ tabeli_nimi ] }' )

    def uhenda( self ):
        log( f'{ self.kasutajanimi }({ len( self.parool ) }) uhendab andmebaasiga { self.andmebaas }({ self.host })' )
        uhendus = connector.connect(
            user     = self.kasutajanimi,
            password = self.parool,
            host     = self.host,
            database = self.andmebaas,
        )

        return uhendus

    @staticmethod
    def leia( uhendus, tabel: str, vali: str, vaartus: any ) -> list:
        otsija = uhendus.cursor( )

        log( f'Otsitakse { tabel }->{ vali } vaartust { vaartus }.' )
        data = {
            'vaartus': vaartus
        }
        otsija.execute( f'SELECT * FROM `{ tabel }` WHERE `{ tabel }`.`{ vali }` = %(vaartus)s', data )

        leitud = otsija.fetchall( )

        otsija.close( )

        log( f'Tagastati { len( leitud ) } valja.' )
        return leitud

    def test( self ) -> bool:
        log( f'{ self.kasutajanimi }({ len( self.parool ) }) testib uhendust andmebaasiga { self.andmebaas }({ self.host }). ' )
        try:
            self.uhenda( )
        except connector.Error as error:
            if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print( 'Ei saanud andmebaasiga uhendust luua. Palun kontrolli oma kasutaja andmed ule.' )
            elif error.errno == errorcode.ER_DATABASE_NAME:
                print( f'Andmebaasi "{ self.andmebaas }" ei leitud.' )
            else:
                print(f'Ei saanud andmebaasiga uhendust luua (error #{ error.errno }).')
            return True

        log( 'uhendus loodi edukalt.' )
        return False

    def test_tabelid( self ) -> list:
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

    def kas_kasutaja_on_olemas( self, kasutajanimi: str ) -> bool:
        uhendus = self.uhenda( )

        leitud = AndmebaasiSild.leia( uhendus, 'kasutajad', 'kasutajanimi', kasutajanimi )

        uhendus.close( )

        return len( leitud ) == 1

    def leia_kasutaja_api_voti( self, kasutajanimi_voi_kasutajaId: str | int ) -> str:
        # eeldame et kasutaja ON olemas ning kasutaja on juba sisse loginud
        uhendus = self.uhenda( )

        vali = 'kasutajanimi' if type( kasutajanimi_voi_kasutajaId ) == type('') else 'id'
        leitud = AndmebaasiSild.leia( uhendus, 'kasutajad', vali, kasutajanimi_voi_kasutajaId )
        uhendus.close( )

        return leitud[ 0 ][ 3 ]

    def leia_kasutaja_parool( self, kasutajanimi: str ) -> str:
        uhendus = self.uhenda( )
        leitud = AndmebaasiSild.leia( uhendus, 'kasutajad', 'kasutajanimi', kasutajanimi )
        uhendus.close( )
        return leitud[ 0 ][ 2 ]

    def leia_faili_id( self, faili_unikaalne_nimi: str ) -> int:
        uhendus = self.uhenda( )
        leitud = AndmebaasiSild.leia( uhendus, 'failid', 'unikaalne_nimi', faili_unikaalne_nimi )
        uhendus.close( )

        if len( leitud ) == 0:
            return -1
        return leitud[ 0 ][ 0 ]

    def leia_faili_nimi( self, faili_id: int ) -> str:
        uhendus = self.uhenda( )
        leitud = AndmebaasiSild.leia( uhendus, 'failid', 'id', faili_id )
        uhendus.close( )

        if len( leitud ) == 0:
            return ''
        return leitud[ 0 ][ 1 ]

    def leia_faili_tuup( self, faili_id: int ) -> str:
        uhendus = self.uhenda( )
        leitud = AndmebaasiSild.leia( uhendus, 'failid', 'id', faili_id )
        uhendus.close( )

        if len( leitud ) == 0:
            return ''
        return leitud[ 0 ][ 3 ]

    def leia_uleslaetud_faili_kasutaja_id( self, faili_id ) -> int:
        uhendus = self.uhenda( )

        leitud = self.leia( uhendus, 'uleslaadimised', 'faili_id', faili_id )
        uhendus.close( )

        if len( leitud ) == 0:
            return -1

        return leitud[ 0 ][ 0 ]

    def kas_api_voti_on_legaalne( self, api_voti: str ) -> [ bool, str, int ]:
        uhendus = self.uhenda( )

        leitud = AndmebaasiSild.leia( uhendus, 'kasutajad', 'api_voti', api_voti )

        uhendus.close( )
        on_olemas = len( leitud ) == 1
        return [ on_olemas, leitud[ 0 ][ 3 ] if on_olemas else '', leitud[ 0 ][ 0 ] if on_olemas else -1 ]

    def kas_kasutaja_parool_kattub( self, kasutajanimi: str, plaintext_parool: str ) -> bool:
        # eeldame et kasutaja olemasolu on juba vaadatud
        api_voti = self.leia_kasutaja_api_voti( kasutajanimi ).encode( )
        kruptitud_parool_salvestatud = self.leia_kasutaja_parool( kasutajanimi )

        krupter = Fernet( api_voti )

        return krupter.decrypt( kruptitud_parool_salvestatud ).decode( 'utf-8' ) == plaintext_parool

    def loo_kasutaja( self, kasutajanimi: str, plaintext_parool: str ) -> bool:
        # Eeldame, et kasutaja olemasolu on juba kontrollitud
        # Samuti on kontrollitud ka parooli tugevus
        api_voti = Fernet.generate_key( )
        print( 'loodi voti: ', api_voti )

        krupter = Fernet( api_voti )

        parool = krupter.encrypt( plaintext_parool.encode( 'utf-8' ) )

        uhendus = self.uhenda( )

        sisestaja = uhendus.cursor( )

        sisestaja.execute( 'INSERT INTO kasutajad ( kasutajanimi, parool, api_voti ) VALUES ( %s, %s, %s )', ( kasutajanimi, parool, api_voti.decode( 'utf-8' ) ) )

        uhendus.commit( )

        log( f'kasutaja { kasutajanimi } loodi edukalt' )

        uhendus.close( )

        return self.kas_kasutaja_on_olemas( kasutajanimi )

    def loo_fail( self, kasutaja_id: int, failinimi: str, failituup: str, unikaalne_nimi: str ) -> bool:
        # Eeldame, et failinimi on ule vaadatud
        uhendus = self.uhenda( )

        if len( failituup ) > 32 or len( failinimi ) > 128 or len( unikaalne_nimi ) > 128:
            return False

        sisestaja = uhendus.cursor( )
        sisestaja.execute( "INSERT INTO failid ( nimi, unikaalne_nimi, failituup ) VALUES( %s, %s, %s )", ( failinimi, unikaalne_nimi, failituup ) )
        uhendus.commit( )

        faili_id = self.leia_faili_id( unikaalne_nimi )

        if faili_id == -1:
            return False

        sisestaja.execute( "INSERT INTO uleslaadimised ( kasutaja_id, faili_id ) VALUES( %s, %s )", ( kasutaja_id, faili_id ) )
        uhendus.commit( )
        uhendus.close( )
        return True

    def kuva_kasutajad( self ) -> None:
        uhendus = self.uhenda( )

        otsija = uhendus.cursor( )
        otsija.execute( 'SELECT kasutajanimi FROM kasutajad' )

        print( otsija.fetchall( ) )