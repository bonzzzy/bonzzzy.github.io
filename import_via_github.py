#!/usr/bin/env python
# -*- coding: utf8 -*-

#___debug___ = True
___debug___ = False
#___debug___ = __debug__


import os
import sys
import skeleton


#url_base = 'https://www.google.com/'
#url_base = 'https://www.google.com/search?q=test'
url_base = "https://bonzzzy.github.io/"


# On stocke en variable globale notre fichier
# de log, et ce afin de ne pas avoir à le passer
# en paramètres...
#
# Idem pour notre "squelette".
#
# Idem pour notre éventuel seul fichier temporaire.
#
_my_log = None
_my_skeleton = None


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
                'ATTENTION : on va écraser « ' \
                + file_dst \
                + ' » !!!'
            input(prompt)

        else:
            name, ext = os.path.splitext(file_dst)
            tmp_dst = name + " { new version }" + ext
            file_dst = _my_skeleton.get_unused_filename(tmp_dst)

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

    _my_skeleton = skeleton.ScriptSkeleton(
        module_name = "Import using GitHub",
        module_file = __file__,
        arguments = sys.argv
        )

    _my_log = _my_skeleton.logItem
    skeleton.___debug___ = ___debug___
    default_src = os.path.basename(__file__)

    # On recherche les fichiers à importer qui seraient
    # indiqués dans notre ligne de commande...
    #
    file_lst = []
    for counter, parameter in enumerate(sys.argv, start=0):
        if counter > 0:
            file_lst.append(parameter)

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


        prompt = \
            'Fichier à télécharger = « ' \
            + file_src \
            + ' ». OK ?'

        if _my_skeleton.ask_yes_or_no(prompt, 'o'):

            url_src = url_base + file_src

            print()
            print('URL =', url_src)

            _, ext = os.path.splitext(file_src)

            if ext in skeleton.filetype_to_coding.keys():

                character_set = skeleton.filetype_to_coding[ext]

            else:

                character_set = skeleton.coding_unknown

            content = _my_skeleton.send_request_http(
                url_src,
                character_set
                )

            if content == '':

                if ___debug___:
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
