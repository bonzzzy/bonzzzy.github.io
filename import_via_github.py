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


def save_in_iPad(
    file_src: str,
    content: str
    ):
    """
    """
    name, ext = os.path.splitext(file_src)

    file_dst = name + " { iPad }" + ext

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
