def kontrolli_parool( parool: str ) -> list:
    # Tugeva parooli kontroll
    # >8 pikkune
    # 1 Suur taht
    # 1 Mark

    if len( parool ) < 8:
        return [ False, 'Parool on liiga lühike.' ]

    [ on_suur, on_mark ] = [ False, False ]
    for taht in parool:
        on_sobiv = taht.isascii( )

        if taht.isupper( ):
            on_suur = True
        elif on_sobiv and not taht.islower( ):
            on_mark = True

        if on_suur and on_mark:
            break

    pohjus = 'Paroolis ei ole suurt tähte.' if not on_suur else 'Paroolis ei ole märki.' if not on_mark else ''

    return [ on_suur and on_mark, pohjus ]

