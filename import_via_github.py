#!/usr/bin/env python
# -*- coding: utf8 -*-


import os
import urllib.request

from urllib.error import HTTPError, URLError


#url = 'https://www.google.com/'
#url = 'https://www.google.com/search?q=test'
url_base = "https://bonzzzy.github.io/"
default_src = 'import_via_github.py'


def send_request(
    url: str
    ) -> str:
    """
    """
    html_string = ''

    try:
        response = urllib.request.urlopen(url_src)

    except HTTPError as error:
        print('===>>', error.status, 'ERROR =', error.reason)

    except URLError as error:
        print('===>> ERROR =', error.reason)

    except TimeoutError:
        print('===>> Request timed out...')

    else:
        html_bytes = response.read()

        character_set = response.headers.get_content_charset()
        if character_set is None:

            # Le "character encoding" n'est normalement pas
            # spécifié dans le fichier .py, pas en tout cas
            # à la façon d'un fichier HTML normal !!!
            #
            # Donc get_content_charset() ne devrait pas le
            # lire correctement si c'est bien un fichier de
            # code Python.
            #
            character_set = 'UTF-8'

        html_string = html_bytes.decode(character_set)

        #print()
        #print(html_bytes)
    
        #print()
        #print(html_string)

    return html_string


#############################################################################################
######################## FONCTION copiée / collée depuis skeleton.py ########################
#############################################################################################
def get_unused_filename(
    filename: str,
    idx_size: int = 3,
    idx_start: int = 0,
    idx_force: bool = True
    ) -> str:
    """ Permet de trouver un nom de fichier disponible,
    similaire au « filename » fourni.
    
    ATTENTION : filename contient le nom ( « basename » )
    du fichier + son extension ( « ext » ).

    Ainsi, si « filename » n'existe pas, nous renverrons
    « filename » lui-même ( sauf si idx_force = True ).

    Sinon, nous renverrons le 1er nom de fichier disponible
    et du type :

        - « basename - 0###.ext » où ### est un entier.

    :param filename: le modèle de nom de fichier ie le nom
    de fichier ET SON EXTENSION.

    :param idx_size: le nombre minimum de caractères dont doit
    être composé l'index ajouté ( s'il existe ). Par exemple,
    si idx_size = 2, nous aurons possiblement à minima en sortie
    « basename - 00.ext » ( si « filename » existe ou « idx_force
    = True » ).

    :param idx_start: faut-il commencer notre recherche de suffixe
    à 0, à 1, ... ? C-a-d « basename - 0.ext » conviendrait-il ?
    Ou faut-il « basename - 1.ext » à minima ? ...

    :param idx_force: faut-il ou pas forcément ajouter un index
    à « filename » ? Si non, on pourra renvoyer « filename » en
    sortie. Si oui, nous aurons à minima en sortie un nom du type
    « basename - #.ext »

    :return: le nom de fichier désiré.
    """

    # On regarde tout d'abord si le nom qui
    # nous est donné n'est pas tout simplement
    # celui que nous recherchons...
    #
    alt_name = filename
    if idx_force or os.path.exists(alt_name):

        # Nous sommes ici dans le cas où nous
        # devons construire un nom de fichier
        # alternatif ( ie le fichier existe
        # déjà ou cela nous est demandé d'une
        # façon impérative ).
        #
        basename, ext = os.path.splitext(filename)
        format_mask = ' - {:0' + str(idx_size) + 'd}'

        suffix_n = idx_start

        while True:

            suffix = format_mask.format(suffix_n)
            alt_name = basename + suffix + ext

            if not os.path.exists(alt_name):
                break

            suffix_n += 1

    # Nous retournons le nom de fichier qui
    # convient.
    #
    return alt_name


def save_in_iPad(
    file_src: str,
    content: str
    ):
    """
    """
    if os.name == 'posix' \
        and 'posix' and 'm360173' in os.uname().nodename:
        # Sur mon iPad, j'écrase le fichier
        # déjà existant... car je ne fais
        # AUCUNE MODIFICATION depuis 1 iPad
        # ( ce n'est pas ergonomique puisque
        # je n'ai pas de clavier ).
        #
        print()
        input('ATTENTION : on va écraser le fichier source !!!')
        file_dst = file_src
        
    elif os.path.exists(file_src):
        name, ext = os.path.splitext(file_src)
        tmp_dst = name + " { new version }" + ext
        file_dst = get_unused_filename(tmp_dst)

    else:
        file_dst = file_src

    with open(file_dst, "wt") as new_file:

        new_file.write(content)


if __name__ == "__main__":

    print()
    print('AIDE :')
    print('======')
    print()
    print('\tABANDON\t\t\t= « . » / « , » / « ; » / « : » / « ! »')
    print('\tFichier par défaut\t=', default_src)
    print()
    print()
    print('Site web =', url_base)


    while True:

        print()
        print()
        file_src = input('Fichier à télécharger ? ')


        if file_src in ('.', ',', ';' ':', '!' ):
            break

        elif file_src == '':
            file_src = default_src


        url_src = url_base + file_src

        print()
        print('URL =', url_src)


        content = send_request(url_src)

        #print()
        #print(content)


        if content == '':
            #print()
            #print('Fichier source introuvable !!!')
            pass


        else:
            save_in_iPad(file_src, content)

            print('===>> File saved')

            #os.startfile(file_dst)
