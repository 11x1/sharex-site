class Fail:
    def __init__( self, id_, nimi, unikaalne_nimi, failituup ):
        self.id = id_
        self.nimi = nimi
        self.unikaalne_nimi = unikaalne_nimi
        self.tuup = failituup
        self.on_olemas = False

        if None in ( id_, nimi, unikaalne_nimi, failituup ):
            self.on_olemas = False

    def on_tuhi( self ):
        return self.on_olemas

    def __eq__( self, other ) -> bool:
        return self.on_olemas == other.on_olemas and self.id == other.id