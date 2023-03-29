from cryptography.fernet import Fernet

class Kasutaja:
    def __init__( self, id_: int | None, nimi: str | None, api_voti: str | None, parool: str | None ):
        self.id = id_
        self.nimi = nimi
        self.api_voti = api_voti
        self.parool = parool
        self.on_olemas = True

        if None in ( id_, nimi, api_voti ):
            self.on_olemas = False

    def on_tuhi( self ):
        return not self.on_olemas

    def parool_kattub( self, antud_parool: str ):
        dekodeerija = Fernet( self.api_voti.encode( ) )
        return dekodeerija.decrypt( self.parool ).decode( 'utf-8' ) == antud_parool

    def __eq__( self, other ) -> bool:
        return self.on_olemas == other.on_olemas and self.id == self.id # and self.nimi == other.nimi and self.api_voti == other.api_voti

    def __str__( self ):
        return f'{ "X | " if self.on_tuhi( ) else "" }{ self.id } { self.nimi }< { self.api_voti } >'