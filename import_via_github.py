#!/usr/bin/env python
# -*- coding: utf8 -*-

#___debug___ = True
___debug___ = False
#___debug___ = __debug__


import os
import sys
import skeleton


url_base = "https://bonzzzy.github.io/"


if __name__ == "__main__":

    _my_skeleton = skeleton.ScriptSkeleton(
        module_name = "Import using GitHub",
        module_file = __file__,
        arguments = sys.argv,
        debug_mode = ___debug___
        )

    _my_log = _my_skeleton.logItem
    _leaf = _my_skeleton.files.node

    #default_src = os.path.basename(__file__)
    default_src = _leaf(__file__).name

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


        prompt = 'Fichier à télécharger = « ' + file_src + ' ». OK ?'

        if _my_skeleton.ask_yes_or_no(prompt, 'o'):

            url_src = url_base + file_src

            #_, ext = os.path.splitext(file_src)
            ext = _leaf(file_src).suffix

            if ext in skeleton.filetype_to_coding.keys():

                set_of_chars = skeleton.filetype_to_coding[ext]

            else:

                set_of_chars = skeleton.coding_unknown

            content, charset = _my_skeleton.send_request_http(
                url_src,
                set_of_chars
                )

            if content == '':

                if ___debug___:
                    print('===>> Fichier source introuvable !!!')

            else:

                # Sur mon iPad, j'écrase le fichier
                # déjà existant... car je ne fais
                # AUCUNE MODIFICATION depuis 1 iPad
                # ( ce n'est pas ergonomique puisque
                # je n'ai pas de clavier ).
                #
                erase_file = (
                        os.name == 'posix'
                    and 'm360173' in os.uname().nodename
                    )

                _my_skeleton.save_strings_to_file(
                    content,
                    destination = file_src,
                    ok_to_erase = erase_file,
                    ask_confirm = False,
                    coding = charset
                    )

                print('===>> File saved')

                #os.startfile(file_dst)
