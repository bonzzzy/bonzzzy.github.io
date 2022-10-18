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


if __name__ == "__main__":

    skeleton.___debug___ = ___debug___

    _my_skeleton = skeleton.ScriptSkeleton(
        module_name = "Import using GitHub",
        module_file = __file__,
        arguments = sys.argv
        )

    _my_log = _my_skeleton.logItem
    default_src = os.path.basename(__file__)

    # On recherche les fichiers à importer qui seraient
    # indiqués dans notre ligne de commande...
    #
    file_lst = []
    for counter, parameter in enumerate(sys.argv, start=0):
        if counter > 0:
            file_lst.append(parameter.strip(' \t'))

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

                # Sur mon iPad, j'écrase le fichier
                # déjà existant... car je ne fais
                # AUCUNE MODIFICATION depuis 1 iPad
                # ( ce n'est pas ergonomique puisque
                # je n'ai pas de clavier ).
                #
                erase_file = os.name == 'posix' \
                    and 'm360173' in os.uname().nodename

                _my_skeleton.save_strings_to_file(
                    content,
                    destination = file_src,
                    ok_to_erase = erase_file,
                    ask_confirm = False,
                    coding = character_set
                    )

                print('')
                print('===>> File saved')

                #os.startfile(file_dst)
