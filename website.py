from sql import Andmebaas
from flask import Flask

Veebileht = Flask( __name__ )
Andmebaas = Andmebaas( 'root', '', 'sharex_site', 'localhost' )

Andmebaas.kuva_kasutajad( )

@Veebileht.route('/registreeri')
def registreeri( ):
    pass

if __name__ == "__main__":
    Veebileht.run( debug=True )