#!/usr/bin/env python
# -*- coding: utf8 -*-
_mode_debug = False


import os
import sys
import urllib.request

from urllib.error import HTTPError, URLError
from http.client import InvalidURL, NotConnected
from socket import timeout


#url_base = 'https://www.google.com/'
#url_base = 'https://www.google.com/search?q=test'
url_base = "https://bonzzzy.github.io/"


# Le dictionnaire ci-dessous permet d'associer le type
# de fichier avec le jeu de charactères qu'il contient.
#
# CONVENTION : Lorsque le fichier est codé sous forme
# de « bytes » ( codage sous forme octale ), on code
# ceci par « None ».
#
# ATTENTION : Il serait possible de mettre « None »
# pour toutes les valeurs puisque :
#
#       . urllib.request.urlopen("...").read() renvoie
# une chaîne de caractères au format « bytes ».
#
#       . en mode "wb", écrire dans un fichier demande
# une chaîne au format b"...", ie au format « bytes ».
#
# Ainsi, indiquer qu'il faut traiter tous les types de
# fichiers au format « bytes » ( « None » ), revient à
# éviter le cycle intermédiaire de décodage des chaînes
# au format « bytes ».
#
# REMARQUE : Sous Unix, pour avoir une idée du jeu de
# caractères d'1 fichier, on utilise la cmd « file » :
#
#       $ file file1.txt file2.txt
#       file1.txt:    ASCII English text
#       file2.txt:    UTF-8 Unicode text
#
# ... Ceci dit, ce n'est pas toujours exact puisque,
# avec a-Shell sous iPad, en écrivant :
#
#       file import_via_github.sh
#
# .. on obtient en résultat :
#
#       import_via_github.sh: POSIX shell script, ASCII text executable
#
# .. alors que :
#
#       . si on associe, dans filetype_to_characterset,
# '.sh' à 'ASCII', ce script plante pour import_via_github.sh
# ( donc ce .sh n'est pas codé en 'ASCII'...).
#
#       . « Bash stores strings as byte strings ».
# Cf https://unix.stackexchange.com/questions/250366/how-to-force-shell-script-characters-encoding-from-within-the-script
#
filetype_to_characterset = {
    '.bat': 'ASCII',
    '.py': 'UTF-8',
    '.sh': None,
    '*': 'UTF-8'
}


def send_request(
    url: str,
    character_set: str = None
    ) -> str:
    """
    """
    html_string = ''

    try:
        response = urllib.request.urlopen(url_src, timeout = 3)

    except InvalidURL as error:
        print('')
        print('===>> InvalidURL =', error)

    except NotConnected as error:
        print('')
        print('===>> NotConnected =', error)

    except TimeoutError:
        print('')
        print('===>> Request timed out...')

    except HTTPError as error:
        print('')
        print('===>>', error.status, 'ERROR =', error.reason)

    except URLError as error:
        print('')
        if isinstance(error.reason, timeout):
            print('===>> Socket timeout error...')
        else:
            print('===>> URLError =', error.reason)

    else:
        html_bytes = response.read()

        if _mode_debug:
            print()
            print(html_bytes)

        set_for_chars = response.headers.get_content_charset()
        if set_for_chars is None:

            # Le "character encoding" n'est normalement pas
            # spécifié dans le fichier .py, pas en tout cas
            # à la façon d'un fichier HTML normal !!!
            #
            # Donc get_content_charset() ne devrait pas le
            # lire correctement si c'est un fichier script
            # Python, bash ou autres.
            #
            set_for_chars = character_set

        if set_for_chars is None:

            # Aucun décodage à faire car le jeu de caractères
            # qui nous concerne est celui des « byte strings ».
            #
            html_string = html_bytes

        else:
            html_string = html_bytes.decode(set_for_chars)

        if _mode_debug:
            print()
            print(html_string)

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
    file_name: str,
    content: str,
    character_set: str = None
    ):
    """
    """
    file_dst = file_name

    if os.path.exists(file_dst):

        if os.name == 'posix' \
            and 'm360173' in os.uname().nodename:
            # Sur mon iPad, j'écrase le fichier
            # déjà existant... car je ne fais
            # AUCUNE MODIFICATION depuis 1 iPad
            # ( ce n'est pas ergonomique puisque
            # je n'ai pas de clavier ).
            #
            print('')
            prompt = \
                'ATTENTION : on va écraser «' \
                + file_dst \
                + '» !!!'
            input(prompt)

        else:
            name, ext = os.path.splitext(file_dst)
            tmp_dst = name + " { new version }" + ext
            file_dst = get_unused_filename(tmp_dst)

    if character_set is None:

        # Le jeu de caractères qui nous concerne est
        # celui des « byte strings ». Donc on ouvre
        # notre fichier au format « b(yte) ».
        #
        flag = "wb"

    else:

        # On ouvre notre fichier au format « t(ext) ».
        #
        flag = "wt"

    with open(file_dst, flag) as new_file:

        new_file.write(content)


if __name__ == "__main__":

    file_lst = []
    default_src = os.path.basename(__file__)

    for counter, parameter in enumerate(sys.argv, start=0):

        if counter > 0:
            file_lst.append(parameter)

        if _mode_debug:
            print(
                'Paramètre n°',
                str(counter),
                'ie sys.argv[',
                str(counter),
                '] =',
                parameter
                )

    print()
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

        if len(file_lst) == 0:
            file_src = input('Fichier à télécharger ? ')

        else:
            file_src = file_lst[0]
            file_lst.pop(0)


        if file_src in ('.', ',', ';' ':', '!' ):
            break

        elif file_src == '':
            file_src = default_src


        prompt = 'Fichier à télécharger = « ' + \
            file_src + \
            ' » ---> GO = < Entrée > seulement. '

        if input(prompt) == '':

            url_src = url_base + file_src

            print()
            print('URL =', url_src)

            _, ext = os.path.splitext(file_src)

            if ext in filetype_to_characterset.keys():

                character_set = filetype_to_characterset[
                    ext
                    ]
                    
            else:

                character_set = filetype_to_characterset[
                    '*'
                    ]

            content = send_request(
                url_src,
                character_set
                )

            if content == '':

                if _mode_debug:
                    print()
                    print('Fichier source introuvable !!!')

            else:

                save_in_iPad(
                    file_src,
                    content,
                    character_set
                    )

                print('')
                print('===>> File saved')

                #os.startfile(file_dst)
