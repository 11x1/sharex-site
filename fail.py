class Fail:
    def __init__( self, id_, nimi, unikaalne_nimi, failituup, suurus_bitid=None ):
        self.id = id_
        self.nimi = nimi
        self.unikaalne_nimi = unikaalne_nimi
        self.tuup = failituup
        self.suurus = round( suurus_bitid / 8000, 2 ) if suurus_bitid is not None else round( 45678 / 8000, 2 )
        self.on_olemas = False

        if None in ( id_, nimi, unikaalne_nimi, failituup ):
            self.on_olemas = False

    def on_tuhi( self ):
        return self.on_olemas

    def json_formaat( self ) -> dict:
        return {
            'nimi'          : self.nimi,
            'unikaalne_nimi': self.unikaalne_nimi,
            'tuup'          : self.tuup,
            'suurus'        : self.suurus
        }

    def __str__( self ) -> str:
        return f'{ "X | " if self.on_tuhi( ) else "" }{ self.id } { self.nimi }.{ self.tuup }< { self.unikaalne_nimi } >'

    def __eq__( self, other ) -> bool:
        return self.on_olemas == other.on_olemas and self.id == other.id