import os
from kasutaja import Kasutaja

ULESLAADIMISTE_KAUST = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), 'uleslaadimised' ) + '/'

class Fail:
    def __init__( self, id_, nimi, unikaalne_nimi, failituup, suurus_bitid=None ):
        self.id = id_
        self.nimi = nimi
        self.unikaalne_nimi = unikaalne_nimi
        self.tuup = failituup
        self.suurus_bitid = 45.67
        self.on_olemas = False

        if None in ( id_, nimi, unikaalne_nimi, failituup ):
            self.on_olemas = False

    def suurus( self, kasutaja_api_voti: str ):
        asukoht = os.path.join( ULESLAADIMISTE_KAUST, kasutaja_api_voti, f'{ self.unikaalne_nimi }.{ self.tuup }' )
        suurus_bitid = os.stat( asukoht ).st_size
        return round( suurus_bitid / 1000, 2 )

    def on_tuhi( self ):
        return self.on_olemas

    def json_formaat( self, kasutaja: Kasutaja ) -> dict:
        return {
            'nimi'          : self.nimi,
            'unikaalne_nimi': self.unikaalne_nimi,
            'tuup'          : self.tuup,
            'suurus'        : self.suurus( kasutaja.api_voti )
        }

    def __str__( self ) -> str:
        return f'{ "X | " if self.on_tuhi( ) else "" }{ self.id } { self.nimi }.{ self.tuup }< { self.unikaalne_nimi } >'

    def __eq__( self, other ) -> bool:
        return self.on_olemas == other.on_olemas and self.id == other.id
