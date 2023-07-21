#!/usr/bin/env python
# -*- coding: utf8 -*-


import sys
# import skeleton


# ---------------------------------------------------------------------------
#
#   PARTIE : DATA ( modèle )
#   ~~~~~~~~
#   Classes & fonctions relatives au stockage des données TÂCHES.
#
# ---------------------------------------------------------------------------

# Exemples du MVC :
#
#   -OK-    ( exemple ) Open-Source-ToDo-List-master.zip
#   -OK-    ( exemple ) QTodoTxt-master.zip => bordélique,
#                       mais qd même cf qtodotxt\lib\tasklib.py & filters.py
#   -OK-    ( exemple ) QTodoTxt2-master.zip => bordélique,
#                       mais qd même cf qtodotxt\lib\tasklib.py & filters.py

# C'est la liste des tâches qui conserve la liste des "listeners", et qui leur
# envoie 1 MESSAGE quand une tâche change, avec 1 dictionnaire pour transmettre
# les paramètres de ce changement ( id, nom, on/off, shown/hidden, priorité )...


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   .
#
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
#
#   Programme PRINCIPAL de ce module s'il est lancé en mode autonome...
#
# ---------------------------------------------------------------------------

from kivy import kivy_home_dir
from kivy.app import App
from kivy.uix.button import Button


class Window(App):

    def build(self):

        return Button(text = 'Hello World')


if __name__ == "__main__":

    print()
    print()
    print('INFORMATIONS :')
    print('==============')
    print()

    # Issues: In iOS, you cannot write in the ~ directory, only in ~/Documents/, ~/Library/ and ~/tmp.
    #
    # Cf 20230404 - 7 best free Python IDEs for iPad and iPhone --- ( mes ) NOTES, dont des infos IMPORTANTES sur des RESTRICTIONS sous iOS ---*
    # in _Know\Info\Outils\Dvpt\Éditeurs de CODE ( Python, etc ) - on iOS.rar\
    #
    print("\tkivy_home_dir =\t", kivy_home_dir)
    print()
    print()

    Window().run()


if False:

    my_skeleton = skeleton.ScriptSkeleton(
        module_name = "my-check-lists",
        module_file = __file__,
        arguments = sys.argv
        )

    log = my_skeleton.logItem


    log.info('')
    log.info('Mes ACTIONS :')
    log.info('=============')
    log.info('')


    log.info('Le problème est que je ne sais rien faire tout seul...')
    log.info('')


    log.info('... alors AU REVOIR !!!')
    log.info('')
