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

from qtpy.QtWidgets import QApplication, QLabel


def window(arguments):

    # Initialize application
    #
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    #
    app = QApplication(sys.argv)

    # Create label widget.
    #
    label = QLabel('Hello, world!')


    # IMPORTANT!!!!! Windows are hidden by default.
    #
    label.show()


    # Start the event loop.
    app.exec_()


if __name__ == "__main__":

    window(sys.argv)


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
