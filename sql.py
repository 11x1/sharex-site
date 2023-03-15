from cryptography.fernet import Fernet
from mysql import connector
from mysql.connector import errorcode # https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
import debug

Logija = debug.Logija( )
log = Logija.log

VAJALIKUD_TABELID = [ 'kasutajad' ]
LOO_TABEL = {
    "kasutajad": "CREATE TABLE kasutajad ( id serial primary key not null, kasutajanimi varchar( 32 ) not null, parool varchar( 256 ) not null, api_voti varchar( 128 ) not null )"
}

class Andmebaas:
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

        leitud = Andmebaas.leia( uhendus, 'kasutajad', 'kasutajanimi', kasutajanimi )

        uhendus.close( )

        return len( leitud ) == 1

    def leia_kasutaja_api_voti( self, kasutajanimi ) -> str:
        # eeldame et kasutaja ON olemas ning kasutaja on juba sisse loginud
        uhendus = self.uhenda( )

        leitud = Andmebaas.leia( uhendus, 'kasutajad', 'kasutajanimi', kasutajanimi )

        uhendus.close( )
        return leitud[ 0 ][ 3 ]

    def leia_kasutaja_parool( self, kasutajanimi ) -> str:
        uhendus = self.uhenda( )
        leitud = Andmebaas.leia( uhendus, 'kasutajad', 'kasutajanimi', kasutajanimi )
        return leitud[ 0 ][ 2 ]

    def kas_api_voti_on_legaalne( self, api_voti ) -> [ bool, str ]:
        uhendus = self.uhenda( )

        leitud = Andmebaas.leia( uhendus, 'kasutajad', 'api_voti', api_voti )

        uhendus.close( )
        on_olemas = len( leitud ) == 1
        return [ on_olemas, leitud[ 0 ][ 3 ] if on_olemas else '' ]

    def kas_kasutaja_parool_kattub( self, kasutajanimi: str, plaintext_parool: str ) -> bool:
        # eeldame et kasutaja olemasolu on juba vaadatud
        api_voti = self.leia_kasutaja_api_voti( kasutajanimi ).encode( )
        kruptitud_parool_salvestatud = self.leia_kasutaja_parool( kasutajanimi )
        print( 'saadud voti: ', api_voti )

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

    def kuva_kasutajad( self ) -> None:
        uhendus = self.uhenda( )

        otsija = uhendus.cursor( )
        otsija.execute( 'SELECT kasutajanimi FROM kasutajad' )

        print( otsija.fetchall( ) )