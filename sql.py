from mysql import connector
from mysql.connector import errorcode # https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
import debug

Logija = debug.Logija( )
log = Logija.log

VAJALIKUD_TABELID = [ 'kasutajad' ]
LOO_TABEL = {
    "kasutajad": "CREATE TABLE kasutajad ( id serial primary key not null, kasutajanimi varchar( 32 ) not null, parool varchar( 256 ) not null, api-võti varchar( 128 ) not null )"
}

class Andmebaas:
    def __init__( self, kasutajanimi, parool, andmebaas, host ) -> None:
        self.kasutajanimi = kasutajanimi
        self.parool = parool
        self.andmebaas = andmebaas
        self.host = host

        peaks_looma_andmebaasi = self.test( )

        if peaks_looma_andmebaasi:
            self.loo_andmebaas( )

        vajalikud_tabelid = self.test_tabelid( )
        for tabeli_nimi in vajalikud_tabelid:
            self.loo_tabel( tabeli_nimi )

    def loo_andmebaas( self ):
        try:
            # ei kasuta self.ühenda( ) sest meil on vaja luua andmebaas.
            ühendus = connector.connect(
                user=self.kasutajanimi,
                password=self.parool,
                host=self.host
            )

            looja = ühendus.cursor( )
            looja.execute( f'CREATE DATABASE { self.andmebaas }' )
            log( f'Loodi andmebaas { self.andmebaas }' )

            looja.close( )
        except connector.Error as error:
            if error.errno == errorcode.CR_CONN_HOST_ERROR:
                print( 'Host\'i ei leitud.' )
            elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print( 'Ei saanud andmebaasiga ühendust luua. Palun kontrolli oma kasutaja andmed üle.' )
            else:
                print( f'Ei saanud andmebaasiga ühendust luua.\n{ error }' )
            exit( )

    def loo_tabel( self, tabeli_nimi ):
        if not tabeli_nimi in VAJALIKUD_TABELID:
            print( 'Tabeli nimi ei ole vajalike tabelite hulgas.' )
            exit( )

        ühendus = self.ühenda( )

        looja = ühendus.cursor( )
        looja.execute( f'CREATE TABLE { LOO_TABEL[ tabeli_nimi ] }' )
        looja.close( )
        log( f'Loodi tabel { tabeli_nimi } käsuga { LOO_TABEL[ tabeli_nimi ] }' )

    def ühenda( self ):
        log( f'{ self.kasutajanimi }({ len( self.parool ) }) ühendab andmebaasiga { self.andmebaas }({ self.host })' )
        return connector.connect(
            user     = self.kasutajanimi,
            password = self.parool,
            host     = self.host,
            database = self.andmebaas
        )

    @staticmethod
    def leia( ühendus, tabel: str, väli: str, väärtus ):
        otsija = ühendus.cursor( )

        log( f'Otsitakse { tabel }->{ väli } väärtust { väärtus }.' )
        otsija.execute( f'SELECT { väli } FROM { tabel } WHERE { väli } = { väärtus }' )

        leitud = [ ]
        for value in otsija:
            leitud.append( value )

        otsija.close( )

        log( f'Tagastati { len( leitud ) } välja.' )
        return leitud

    def test( self ) -> bool:
        log( f'{ self.kasutajanimi }({ len( self.parool ) }) testib ühendust andmebaasiga { self.andmebaas }({ self.host }). ' )
        try:
            self.ühenda( )
        except connector.Error as error:
            if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print( 'Ei saanud andmebaasiga ühendust luua. Palun kontrolli oma kasutaja andmed üle.' )
            elif error.errno == errorcode.ER_DATABASE_NAME:
                print( f'Andmebaasi "{ self.andmebaas }" ei leitud.' )
            else:
                print(f'Ei saanud andmebaasiga ühendust luua (error #{ error.errno }).')
            return True

        log( 'Ühendus loodi edukalt.' )
        return False

    def test_tabelid( self ) -> list:
        vajalikud_tabelid = [ ]
        try:
            ühendus = self.ühenda()
            for tabeli_nimi in VAJALIKUD_TABELID:
                    otsija = ühendus.cursor()
                    otsija.execute(f'SHOW TABLES LIKE "{tabeli_nimi}"')

                    if otsija.rowcount == 0:
                        vajalikud_tabelid.append( tabeli_nimi )
        except Exception as e:
            print( e )
            exit( )

        log( f'Tabeleid { ", ".join( vajalikud_tabelid ) } ei leitud.' )
        return vajalikud_tabelid

    def user_exists( self, kasutajanimi ) -> bool:
        ühendus = self.ühenda( )

        leitud = self.leia( ühendus, 'kasutajad', 'kasutajanimi', kasutajanimi )

        print( leitud )

        return False
