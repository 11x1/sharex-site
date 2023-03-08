class Logija:
    def __init__( self, peaks_logima=True ) -> None:
        self.peaks_logima = peaks_logima

    def log( self, *args ):
        if self.peaks_logima:
            print( f'[ DEBUG ] { "".join( *args ) }' )