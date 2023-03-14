import hashlib

import bcrypt as bcrypt
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

    def loo_tabel( self, tabeli_nimi ):
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
        return connector.connect(
            user     = self.kasutajanimi,
            password = self.parool,
            host     = self.host,
            database = self.andmebaas,
        )

    @staticmethod
    def leia( uhendus, tabel: str, vali: str, vaartus ) -> list:
        otsija = uhendus.cursor( )

        log( f'Otsitakse { tabel }->{ vali } vaartust { vaartus }.' )
        data = {
            'vali': vali,
            'tabel': tabel,
            'vaartus': vaartus
        }
        otsija.execute( f'SELECT %(vali)s FROM %(tabel)s WHERE %(vali)s = %(vaartus)s', data )

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

    def kas_kasutaja_on_olemas( self, kasutajanimi ) -> bool:
        uhendus = self.uhenda( )

        leitud = self.leia( uhendus, 'kasutajad', 'kasutajanimi', kasutajanimi )

        print( leitud )

        return len( leitud ) == 1

    def loo_kasutaja( self, kasutajanimi, plaintext_parool ) -> bool:
        # Eeldame, et kasutaja olemasolu on juba kontrollitud
        # Samuti on kontrollitud ka parooli tugevus
        api_voti = bcrypt.gensalt( ).decode( 'utf-8' )

        md5 = hashlib.md5( )
        md5.update( plaintext_parool.encode( 'utf-8' ) )

        parool = md5.hexdigest( )

        uhendus = self.uhenda( )

        sisestaja = uhendus.cursor( )

        sisestaja.execute( 'INSERT INTO kasutajad ( kasutajanimi, parool, api_voti ) VALUES ( %s, %s, %s )', ( kasutajanimi, parool, api_voti ) )
        log( f'kasutaja { kasutajanimi } loodi edukalt' )
        uhendus.close( )

        return self.kas_kasutaja_on_olemas( kasutajanimi )

    def kuva_kasutajad( self ) -> None:
        uhendus = self.uhenda( )

        otsija = uhendus.cursor( )
        otsija.execute( 'SELECT kasutajanimi FROM kasutajad' )

        print( otsija.fetchall( ) )