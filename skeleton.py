#!/usr/bin/env python
# -*- coding: utf8 -*-

# Positionner la variable ___debug___ ci-dessous suivant les besoins...
#
# RQ : « ___debug___ = __debug__ » implique que le mode choisi dépend
# des paramètres de lancement de Python. Ainsi :
#
#       __debug__
#       This constant is true if Python was not started with an -O option.
#       See also the assert statement.
#
#       Cf https://docs.python.org/3/library/constants.html
#
#___debug___ = True
#___debug___ = False
___debug___ = __debug__


import os
import sys

import time
import datetime

from string import whitespace

import tempfile
import subprocess

import logging
import logging.handlers

import urllib.request

from urllib.error import HTTPError, URLError
from http.client import InvalidURL, NotConnected
from socket import timeout


# ===========================================================================
#
#   SKELETON.PY = SQUELETTE réutilisable pour débuter rapidement le codage
#   ~~~~~~~~~~~~~                                d'une  application PYTHON.
#
# Les différentes PARTIES sont :
#
#   - Constantes & Définitions ( dont celle de la classe ScriptSkeleton )
#
#   - Fonctions d'initialisation des EXÉCUTABLES et RÉPERTOIRES utilisés
#
#   - Fonctions pour journalisation des WARNINGS et ERREURS ( DÉBOGAGE )
#
#   - Fonctions spécifiques à l'OPERATING SYSTEM ( bip, shutdown, ... )
#
#   - Fonctions de SAISIE de DONNÉES
#
#   - Fonctions de GESTION de FICHIERS
#
#   - Fonctions spécifiques au WEB ( browser, HTML, HTTP, etc )
#
# ===========================================================================
#
#   - Fonctions d'initialisation des EXÉCUTABLES et RÉPERTOIRES utilisés :
#
#   ( in autotests )    . def set_paths_and_miscellaneous
#                       . def get_paths_and_miscellaneous
#                       . def show_paths_and_miscellaneous
#                       . def check_paths_and_miscellaneous
#
# ===========================================================================
#
#   - Fonctions pour journalisation des WARNINGS et ERREURS ( DÉBOGAGE ) : 
#
#   ( in autotests )    . def on_ouvre_le_journal
#   ( in autotests )    . def on_se_presente
#                       . def debug_mode
#   ( in autotests )    . def on_dit_au_revoir
#
# ===========================================================================
#
#   - Fonctions spécifiques à l'OPERATING SYSTEM ( bip, shutdown, ... ) :
#
#   ( in autotests )    . def on_sonne_le_reveil
#   ( in autotests )    . def shutdown_please
#
# ===========================================================================
#
#   - Fonctions spécifiques au TEMPS :
#
#                       . def build_now_string
#
# ===========================================================================
#
#   - Fonctions de SAISIE de DONNÉES :
#
#   ( in autotests )    . def ask_yes_or_no
#   ( in autotests )    . def choose_in_a_list
#   ( in autotests )    . def choose_in_a_dict
#
# ===========================================================================
#
#   - Fonctions de GESTION de FICHIERS :
#
#   ( in autotests )    . def search_files_from_a_mask
#   ( in autotests )    . def convert_to_pdf_init
#   ( in autotests )    . def convert_to_pdf_run
#   ( in autotests )    . def edit_file_txt
#   ( in autotests )    . def compare_files
#   ( in autotests )    . def get_unused_filename
#                       . def save_strings_to_file
#
# ===========================================================================
#
#   - Fonctions spécifiques au WEB ( browser, HTML, HTTP, etc ) :
#
#                       . def url_to_valid
#                       . def send_request_http
#
# ===========================================================================


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Constantes & Définitions ( dont celle de la classe ScriptSkeleton ).
#
# ---------------------------------------------------------------------------


# Types de SHUTDOWN possibles.
#
# Mais ils ne sont utilisés que dans les scripts PYTHON destinés à servir en
# mode BATCH, et qui peuvent donc avoir à éteindre la machine surlaquelle ils
# tournent une fois leurs traitements achevés.
#
shutdown_TYPE = 'shutdown_TYPE'
shutdown_none = 'none'
shutdown_complete = 'complete'
shutdown_hibernate = 'hibernate'


# Les multiples façons de dire OUI ou NON.
#
yes_or_no = {
    'eng'   : {
        'y'     : True,
        'yes'   : True,
        'ok'    : True,
        'n'     : False,
        'no'    : False,
        'nope'  : False,
        },
    'fre'   : {
        'o'     : True,
        'oui'   : True,
        'n'     : False,
        'non'   : False
        }
}


# Le dictionnaire ci-dessous permet d'associer le type
# de fichier avec le jeu de charactères qu'il contient.
#
# CONVENTION : Lorsque le fichier est codé sous forme
# de « bytes » ( codage sous forme octale ), on code
# ceci par « None ».
#
# ATTENTION : Ce script s'attend à ce que « None »
# soit la valeur de l'encodage en « byte strings ».
#
#       Des tests type « if ... is None » sont ainsi
#       codés dans ce script !!!
#
#       La valeur « coding_bytes » ci-dessous ne doit
#       donc pas être modifiée & est donnée simplement
#       ci-dessous pour mémoire !!!
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
#       . si on associe, dans filetype_to_coding, '.sh'
# à 'ASCII', ce script plante pour import_via_github.sh
# ( donc ce .sh n'est pas codé en 'ASCII'...).
#
#       . « Bash stores strings as byte strings ».
# Cf https://unix.stackexchange.com/questions/250366/how-to-force-shell-script-characters-encoding-from-within-the-script
#
coding_unknown = '?'
coding_default = 'UTF-8'
coding_bytes = None

filetype_to_coding = {
    '.bat': 'ASCII',
    '.py': 'UTF-8',
    '.sh': coding_bytes
}


# Fonction d'affichage.
#
def _show_(msg, journal):
    """ Pour afficher un msg, tout en le journalisant en
    même temps.
    """

    print(msg)
    if journal is not None:
        journal.debug(msg)


# Notre classe principale ScriptSkeleton.
#
class ScriptSkeleton:
    """ Squelette d'un script Python, avec différentes
    propriétés et méthodes pour faciliter les traitements
    de base.
    """

    def __init__(
        self,
        module_name: str = None,
        module_file: str = __file__,
        arguments: list = None,
        debug_mode: bool = ___debug___
        ):
        """
        :param module_name:

        :param module_file: nom du fichier appelant ( sa valeur
        de __file__ en général ).

        :param arguments: les arguments avec lesquels le module
        principal qui nous appelle a lui-même été appelé ( i-e
        sys.argv en général ).

        :param debug_mode: ce « squelette » va-t-il s'exécuter
        en mode DEBUG ( True or False ) ? Par défaut, il prend
        le mode de ce script ( défini par ___debug___ )...
        Un autre nom pour ce paramètre pourrait être :

                VERBOSE = True / False...
        """

        # On personnalise notre mode de déboggage.
        #
        self._debug_ = debug_mode

        # Sommes-nous dans notre méthode __del__ ?
        #
        # Non, bien sûr... !!!
        #
        self._we_are_inside_del_method = False
        self._we_already_said_bye = False

        # Variables internes pour stockage du journal des opérations :
        #
        #       _logHandler pointe sur le fichier TXT temporaire de log ;
        #
        #       _logFile contient le nom du fichier log créé ;
        #
        #       logItem contient l'objet journal ;
        #
        # Ce module ne gère en effet qu'un journal, et ceci afin de ne pas avoir
        # plusieurs journaux créés ( par erreur par exemple ) en //, ce qui causerait
        # la création de plusieurs fichiers log temporaires, et donc rendrait le
        # déroulé des opérations plus difficile à suivre !!!
        #
        self._logHandler = None
        self._logFile = None

        # Nous sommes obligés d'initialiser logItem à None, et ce afin que Python sache
        # que ScriptSkeleton possède un attribut de ce nom.
        #
        # En effet, dans la fonction on_ouvre_le_journal(), on nomme cet attribut !!!
        # Alors s'il n'a pas été déclaré dans la fonction __init__, avant l'appel, le
        # script va planter car Python ne saura pas que cet attribut existe...
        #
        if module_name is None:

            module_name = os.path.basename(
                os.path.splitext(
                    module_file
                    )[0]
                )

        self.logItem = None
        self.logItem = self.on_ouvre_le_journal(module_name)

        # ATTENTION : Lorsque nous serons dans notre méthode __del__() et donc dans le
        # ramasse-miettes de Python = POTENTIELLEMENT, les objets LOG seront aussi en
        # train d’être détruits, voire l'auront déjà été... !!!
        #
        # Donc nous nous prémunissons contre cela via des fonctions LAMBDA qui feront
        # ou pas référence à notre log, suivant le cas.
        #
        # D'expérience, appeler dans notre __del__() le module LOG ne pose en fait pas
        # de pb sous Python 3.10 et Windows 10.
        #
        # Par contre, sous Python 3.9 ( a-Shell ) et iOS, cela provoque des bugs d'appels
        # dans le module LOG qui ne retrouve plus ses petits...
        #
        # Pour l'instant, notre LOG vient d'être créé, donc pas de souci !!!
        #
        self.shw = lambda x: _show_(x, self.logItem)
        self.shw_info = lambda x: self.logItem.info(x)
        self.shw_debug = lambda x: self.logItem.debug(x)
        #
        # Dans notre méthode __del__(), nous attribuerons d'autres valeurs à self.shw_info
        # et à self.shw_debug.
        #
        # Par ailleurs, ces 2 fonctions sont ( actuellement ) utilisées seulement dans nos
        # méthodes invoquées directement ou indirectement depuis notre méthode __del__()
        # i.e :
        #
        #       - on_dit_au_revoir()
        #       - on_sonne_le_reveil()
        #       - edit_file_txt()
        #       - get_paths_and_miscellaneous()

        if self._debug_:

            # On affiche notre mode de déboggage quand il est actif.
            #
            self.debug_mode(True)

        # Le dictionnaire « paths_and_miscellaneous » contiendra la liste des fichiers
        # & répertoires utiles, i-e il contiendra à minima les entrées suivantes :
        #
        #       - working_SYSTEM,
        #       - working_RELEASE,
        #       - working_VERSION,
        #       - working_MACHINE_NAME,
        #       - working_MACHINE_TYPE,
        #       - working_PATH_FULL,
        #       - working_PATH_DSK_ONLY,
        #       - working_PATH_DIRS_ONLY,
        #       - EXE_txt_editor,
        #       - EXE_(..),
        #       - DIR_(..),
        #       - DLL_(..),
        #       - ARG_(..).
        #
        # Il est aussi possible de se servir de ce dictionnaire pour conserver des
        # paramètres généraux du programme, tels que ceux par exemple lus dans une
        # section 'GENERAL SETTINGS' d'un fichiers de configuration. Les entrées
        # suivantes sont ainsi aussi possibles :
        #       - shutdown_TYPE.
        #
        self.shutdown_dflt = shutdown_none

        self.paths_and_miscellaneous = {}

        self.set_paths_and_miscellaneous()
        
        self.nb_parameters_in = self.on_se_presente(module_file, arguments)


    def __del__(self):
        """
        """

        self._we_are_inside_del_method = True

        # ATTENTION : Dans notre méthode __del__() et donc dans le ramasse-miettes
        # de Python = POTENTIELLEMENT, les objets LOG sont aussi en train d’être
        # détruits, voire l'ont déjà été... !!!
        #
        # Donc nous choisissons d'autres façons d'afficher le LOG en cette toute
        # fin de script !!!
        #
        self.shw_info = lambda x: print(x)
        self.shw_debug = lambda x: print(x) if self._debug_ else None

        # On quitte l'application...
        #
        self.on_dit_au_revoir()


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Fonctions d'initialisation des EXÉCUTABLES et RÉPERTOIRES utilisés.
#
# ---------------------------------------------------------------------------


    def show_paths_and_miscellaneous(
        self,
        printer = print, # function
        jumper = print, # function
        intro: str = None
        ):
        """ Pour "imprimer" ou sauvegarder le contenu de
        notre dictionnaire.

        :param printer: la fonction qui doit permettre de
        sauvegarder ou imprimer ce résumé là où l'on veut
        ( un fichier log, un widget, ...).

        :param jumper: la fonction qui permet de "sauter
        une ligne" afin d'améliorer la présentation.

        :param sous_titre: un message que l'on souhaite
        éventuellement afficher en introduction.

        :return: None
        """

        printer('Configuration des exécutables & répertoires :')
        printer('=============================================')
        jumper()

        if intro is not None:
            printer(intro)
            jumper()

        for key, value in self.paths_and_miscellaneous.items():
            printer(f'{key} = {value}')

        jumper()


    def check_paths_and_miscellaneous(
        self,
        printer = print, # function
        jumper = print, # function
        alert = print # function
        ) -> bool:
        """ Pour vérifier que notre dictionnaire est correct.

        On va tester le contenu des clefs commençant par :

            . 'DIR_',
            . 'EXE_',
            . 'DLL_'.

        On teste l'existence des répertoires & fichiers définis,
        autres que ceux relatifs au répertoire de travail ( car
        on est sûr que ces derniers existent puisqu'ils ont été
        construits à partir de la fonction os.getcwd() ou que l'
        on a déjà vérifié leur existence.

        :param printer: la fonction qui doit permettre de sauver
        ou imprimer les messages relatifs à nos traitements là où
        l'on veut ( un fichier log, un widget, ...).

        :param jumper: la fonction qui permet de "sauter 1 ligne"
        afin d'améliorer la présentation.

        :param alert: la fonction qui nous permet d'alerter si ns
        trouvons un pb.

        :return: True si les tests ok ; False si on a rencontré
        une erreur .
        """

        no_error = True

        for key, value in self.paths_and_miscellaneous.items():

            if value is None:
                pass

            else:
                name = None
                key_short = key[0:4]

                if key_short in ('DIR_', 'EXE_', 'DLL_'):

                    printer(f"Test de l'existence de {key}...")

                if key_short == 'DIR_' and not os.path.isdir(value):
                    name = 'répertoire'

                elif key_short == 'EXE_' and not os.path.isfile(value):
                    name = 'fichier'

                elif key_short == 'DLL_' and not os.path.isfile(value):
                    name = 'module DLL'

                if name is not None:

                    no_error = False

                    alert(f"Le {name} suivant n'existe pas :")
                    #
                    # On impose une tabulation de 6 espaces car, suivant
                    # les systèmes, \t ne représente pas toujours le même
                    # nombre de ceux-ci...
                    #
                    alert(f"{'':>6}{value}")

                    jumper()

        return no_error


    def set_paths_and_miscellaneous(
        self,
        directory: str = '',
        print_configuration: bool = None
        ) -> str:
        """ Définitions des différents exécutables dont se sert ce script.
    
        :param directory: répertoire où il faut lire & écrire les fichiers. Si ce
        paramètre est omis, ou que le répertoire désigné n'existe pas, on fixera
        le répertoire de lecture / création au répertoire courant...
    
        :param print_configuration: faut-il ou non afficher la configuration construite ?
    
        :return: le répertoire de travail, ce qui est utile s'il n'a pas été passé en
        paramètre d'entrée...
        """

        log = self.logItem

        # ATTENTION : PERSONNALISATION de notre mode DEBUG
        # -----------
        # Si aucune valeur ne nous est précisée pour l'affichage
        # ou pas de la configuration, nous faisons en fonction de
        # notre propre mode de déboggage...
        #
        # Nous sommes obligé de faire ainsi car la déclaration de
        # set_paths_and_miscellaneous() ne peut prendre la forme :
        #
        #   def set_paths_and_miscellaneous(
        #       self,
        #       directory: str = '',
        #       print_configuration: bool = self.debug
        #       ) -> str:
        #
        # ... c'est une syntaxe que Python n'autorise pas d'indiquer
        # comme valeur par défaut, une valeur ( self.debug ) extraite
        # de l'un même des autres paramètres ( self ).
        #
        # Si nous n'avions qu'un seul mode DEBUG pour l'entièreté de
        # notre script, et non un mode DEBUG pour chacun des objets
        # ScriptSkeleton, nous aurions pu écrire plus simplement :
        #
        #   def set_paths_and_miscellaneous(
        #       self,
        #       directory: str = '',
        #       print_configuration: bool = ___debug___
        #       ) -> str:
        #
        # ... mais chacun de ces objets à son propre mode !!!
        #
        # Donc nous sommes obligés de donner la valeur « None » dans
        # la définition de fonction au booléen en question, puis de
        # tester ici si cette valeur est à None ou pas.
        #
        if print_configuration is None:
            print_configuration = self._debug_

        # Où sommes-nous ?
        #
        try:
            module = 'OS'
            where_are_we = os.uname()

            our_system = where_are_we.sysname
            our_release = where_are_we.release
            our_version = where_are_we.version
            our_machine = where_are_we.machine
            our_nodename = where_are_we.nodename

        except AttributeError:

            from platform import uname
            log.debug('« os.uname() » inconnu.')
            log.debug('')

            module = 'PLATFORM'
            where_are_we = uname()

            our_system = where_are_we.system
            our_release = where_are_we.release
            our_version = where_are_we.version
            our_machine = where_are_we.machine
            our_nodename = where_are_we.node

        log.debug('Dixit « %s » : %s', module, where_are_we)
        log.debug('Système « %s » « %s » version « %s ».',
            our_system,
            our_release,
            our_version
            )
        log.debug("Notre machine est de type « %s » et s'appelle :",
            our_machine
            )
        log.debug('\t« %s »', our_nodename)
        log.debug('')

        self.paths_and_miscellaneous['working_SYSTEM'] = our_system
        self.paths_and_miscellaneous['working_RELEASE'] = our_release
        self.paths_and_miscellaneous['working_VERSION'] = our_version
        self.paths_and_miscellaneous['working_MACHINE_TYPE'] = our_machine
        self.paths_and_miscellaneous['working_MACHINE_NAME'] = our_nodename

        # Sommes-nous 32 ou 64 bits ?
        #
        is_64bits = sys.maxsize > 2 ** 32
        size = '64' if is_64bits else '32'
        msg_architecture = f'ARCHITECTURE {size} bits sur OS « {our_system} ».'

        # On initialise le répertoire de travail de ce programme.
        #
        if directory == '' or not os.path.isdir(directory):
            working_path = os.getcwd()
        else:
            working_path = directory

        self.paths_and_miscellaneous['working_PATH_FULL'] = working_path

        # Avant étaient utilisées les 2 instructions ci-dessous :
        #
        #   directories_and_files['working_PATH_DSK_ONLY'] = working_path[0:2]
        #   directories_and_files['working_PATH_DIRS_ONLY'] = working_path[3:]
        #
        # Maintenant, on est passé à os.path.splitdrive, afin d'être plus PORTABLE...
        #
        (path_drive, path_tail) = os.path.splitdrive(working_path)
        self.paths_and_miscellaneous['working_PATH_DSK_ONLY'] = path_drive
        self.paths_and_miscellaneous['working_PATH_DIRS_ONLY'] = path_tail

        # On initialise les comportements généraux de ce programme.
        #
        self.paths_and_miscellaneous[shutdown_TYPE] = self.shutdown_dflt


        #
        ###########################################################
        ########## INITIALISATION dans le cas de WINDOWS ##########
        ###########################################################
        #


        # On définit les autres répertoires & fichiers utilisés.
        #
        if os.name.upper() == 'NT':

            root = os.environ['SYSTEMROOT']

            # On considère que LibreOffice est tjrs au même endroit...
            #
            libre_office_dir = r"C:\Program Files\LibreOffice\program"
            libre_office_exec = os.path.join(libre_office_dir, "soffice.exe")
            libre_writer_exec = os.path.join(libre_office_dir, "swriter.exe")

            # Edit Pad Pro peut-être "rangé" / installé dans plusieurs
            # répertoires différents suivant les machines, suivant que
            # j'ai utilisé le répertoire par défaut lors de l'installation,
            # ou que j'ai pensé à modifier ce répertoire ( pour coller à mon
            # ancienne habitude... ).
            #
            # Le mieux serait ici de lire dans le registre Windows l'endroit
            # où se trouve Edit Pad Pro !!! ( plutôt que cette infâme verrue ).
            #
            # Cela dit, il peut y avoir plusieurs version d'EditPad Pro hébergées
            # sur une même machine...
            #
            editpad_dir_list = [
                # On liste ici les différents répertoires possibles, par ordre
                # de la version la plus récente ( préférée ) à la plus ancienne.
                #
                r'C:\Program Files\Just Great Software\EditPad Pro',
                r'C:\Program Files\EditPad Pro',
                r'C:\Program Files\EditPadPro',
                r'C:\Program Files\Just Great Software\EditPad Pro 8',
                r'C:\Program Files\EditPad Pro 8',
                r'C:\Program Files\EditPadPro8',
                r'C:\Program Files\Just Great Software\EditPad Pro 7',
                r'C:\Program Files\EditPad Pro 7',
                r'C:\Program Files\EditPadPro7',
                r'C:\Program Files\Just Great Software\EditPad Pro 6',
                r'C:\Program Files\EditPad Pro 6',
                r'C:\Program Files\EditPadPro6',
                r'C:\Program Files\Just Great Software\EditPad Pro 5',
                r'C:\Program Files\EditPad Pro 5',
                r'C:\Program Files\EditPadPro5'
            ]

            editpad_exe_list = [
                # On liste ici les différents exécutables possibles, par ordre
                # de la version la plus récente ( préférée ) à la plus ancienne.
                #
                'EditPadPro8.exe',
                'EditPadPro7.exe',
                'EditPadPro.exe'
            ]

            dir_txt_editor = None
            exe_txt_editor = None

            log.debug("Recherche d'EditPad Pro :")
        
            for dir_to_try in editpad_dir_list:
                log.debug('Répertoire testé = %s', dir_to_try)
                if os.path.isdir(dir_to_try):
                    dir_txt_editor = dir_to_try
                    log.debug('Répertoire retenu = %s', dir_txt_editor)
                    break
    
            if dir_txt_editor is not None:
                for exe_to_try in editpad_exe_list:
                    log.debug('Fichier testé = %s', exe_to_try)
                    file_to_test = os.path.join(dir_txt_editor, exe_to_try)
                    if os.path.isfile(file_to_test):
                        exe_txt_editor = file_to_test
                        log.debug('Fichier retenu = %s', exe_txt_editor)
                        break

            if exe_txt_editor is None:
                # Si l'on n'a pas trouvé EditPadPro, on se rabat sur Notepad.
                #
                exe_txt_editor = os.path.join(root, 'notepad.exe')
                log.debug('Fichier retenu = %s', exe_txt_editor)

            log.debug('')

            # Seulement dans le cas de Windows XP, et ceci afin de jouer
            # un son, on a besoin d'un player et d'un fichier multimédia.
            # ( cf la fonction "on_sonne_le_reveil" ).
            #
            if our_system == 'Windows' and our_release == 'XP':

                # Sous Windows XP, on joue un son d'une autre façon que
                # sur les autres plateformes car le son généré par un
                # "\a" y est peu audible...
                #
                # Je n'ai testé le "mplay32.exe" que sous Windows XP,
                # c'est pour cela que je ne me sers de ce logiciel que
                # dans ce cas, mais il doit fonctionner sous beaucoup
                # de versions de Windows avant XP voire qq unes après
                # (ou au moins son ancêtre i.e mplay.exe)... Par contre,
                # à partir de Windows 7, il faut utiliser le lecteur
                # Windows Media ou une autre solution...
                #
                # Donc ici, pour réveiller l'utilisateur, on joue une
                # mélodie sous Windows via le Media Player l'avantage
                # de cette méthode est que le son est réglable et que
                # cela marche sur un PC de bureau comme sur un portable...
                #
                player_exe = os.path.join(root, 'System32', 'mplay32.exe')
                player_arg = ['/play', '/close']
                played = os.path.join(root, 'Media', 'Windows XP Battery Low.wav')

            else:
                player_exe = None
                player_arg = None
                played = None


        #
        ###########################################################
        ########## INITIALISATION pour un OS INCONNU  #############
        ###########################################################
        #


        else:
            log.critical('UNSUPPORTED SYSTEM :')
            log.critical('')
            log.critical(
                "Les programmes nécessaires à ce module sont à définir pour l'OS « %s ».",
                os.name.upper()
                )
            log.critical('')

            # On ne lève dorénavant plus une exception :
            #
            #   raise AssertionError
            #
            # ... car :
            #
            #   - Cela faisait planter le script dans ce cas, i-e en fin
            # de script, lorsque l'on passait dans notre méthode __del__,
            # celle-ci apelait « self.on_dit_au_revoir() », qui elle-même
            # lançait « self.edit_file_txt() », qui elle-même invoquait :
            #
            #   self.paths_and_miscellaneous['EXE_txt_editor']
            #
            # ... qui n'avait pas été défini !!!
            #
            # On ne peut donc lever une exception qu'après avoir défini tous
            # les « paths and miscellaneous » !!!
            #
            # Sinon, on va droit au PLANTAGE !!!
            #
            exe_txt_editor = None

            libre_office_dir = None
            libre_office_exec = None
            libre_writer_exec = None

            player_exe = None
            player_arg = None
            played = None


        #
        ###########################################################
        ########## CLÔTURE de notre INITIALISATION ################
        ###########################################################
        #


        self.paths_and_miscellaneous['EXE_txt_editor'] = exe_txt_editor

        self.paths_and_miscellaneous['DIR_libre_office'] = libre_office_dir
        self.paths_and_miscellaneous['EXE_libre_office'] = libre_office_exec
        self.paths_and_miscellaneous['EXE_libre_writer'] = libre_writer_exec

        self.paths_and_miscellaneous['EXE_player'] = player_exe
        self.paths_and_miscellaneous['ARG_player'] = player_arg
        self.paths_and_miscellaneous['EXE_played'] = played

        # Si c'est demandé, on imprime le dictionnaire.
        #
        printing_function = lambda x: log.debug(x)
        jumping_function = lambda: log.debug('')
        alert_function = lambda x: log.critical(x)

        if print_configuration:

            jumping_function()

            self.show_paths_and_miscellaneous(
                printing_function,
                jumping_function,
                msg_architecture
                )

        # On vérifie que notre dictionnaire soit correct.
        #
        all_ok = self.check_paths_and_miscellaneous(
            printing_function,
            jumping_function,
            alert_function
            )

        if all_ok:
            log.debug('-> Ok, présence de tous les fichiers & répertoires.')
            jumping_function()

        else:
            log.critical('-> Certains FICHIERS requis sont MANQUANTS.')
            log.critical('')

        return working_path


    def get_paths_and_miscellaneous(
        self,
        index: str
        ) -> str:
        """ Pour retrouver de façon « protégée » une valeur de notre
        dictionnaire : on va ainsi, par exemple, tester si l'index
        est bien présent dans le dictionnaire...
        
        :param index: l'index de la valeur souhaitée.

        :return: la valeur souhaitée.
        """

        value = None

        if self.paths_and_miscellaneous is None \
            or len(self.paths_and_miscellaneous) == 0:

            self.shw_debug(f'« {index} » est inconnu.')
            self.shw_debug("« paths_and_miscellaneous » est vide.")
            self.shw_debug('')

        else:

            keys = self.paths_and_miscellaneous.keys()

            if index in keys:

                value = self.paths_and_miscellaneous[index]

            if value is None:

                # Si l'index n'a pas été trouvé, ou que la valeur dans
                # le dictionnaire est None, alors on informe.
                #
                msg = f'« {index} » est inconnu'

                if 'working_SYSTEM' in keys and 'working_MACHINE_TYPE' in keys:

                    msg = '{} sur {} et {}.'.format(
                        msg,
                        self.paths_and_miscellaneous['working_SYSTEM'],
                        self.paths_and_miscellaneous['working_MACHINE_TYPE']
                        )

                else:
                    msg = f'{msg} sur {os.name.upper()}.'

                self.shw_debug(msg)
                self.shw_debug('')
            
        return value


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Fonctions pour journalisation des WARNINGS et ERREURS ( DÉBOGAGE ).
#
# ---------------------------------------------------------------------------


    def on_ouvre_le_journal(
        self,
        log_name,
        directory: str = '',
        also_on_screen: bool = None,
        warning_on_reopen: bool = None
        ) -> logging.Logger:
        """ Pour initialiser la journalisation des messages dans un fichier,
            voire également à l'écran.

        Cette fonction est initialement basée sur un exemple trouvé sur le web :

            http://sametmax.com/ecrire-des-logs-en-python/
            (..)\Src\_Python\( help ) Functions of Python.rar\LOG - Écrire des logs en Python*.pdf

        On ne gère par contre qu'un unique journal, et ceci afin de ne pas avoir
        plusieurs journaux créés ( par erreur par exemple ) en //, ce qui causerait
        la création de plusieurs fichiers log temporaires, et donc rendrait le
        déroulé des opérations plus difficile à suivre !!!

        :param log_name: nom qui sera donné au logger et qui permettra de le retrouver,
        si nécessaire, via la fonction logging.getLogger(name).

        :param directory: répertoire où il faut créé le journal. Si ce paramètre est
        vide, ou que le répertoire n'existe pas, on fixera le répertoire de création
        au répertoire courant...

        :param also_on_screen: les messages de log doivent-ils également apparaître
        à l'écran ( ou ne seront-ils stockés sinon que dans un fichier ).

        :param warning_on_reopen: si ce booléen est à vrai, un WARNING s'affichera
        en gros si le journal avait déjà été ouvert. Sinon, il y aura seulement
        un message de deboggage qui sera émis.

        :return: l'objet logger en lui-même, qu'il ait été créé à cette occasion
        ou que, ayant déjà été créé, on renvoie à nouveau le même.
        """

        # On définit nos paramètres en fonction de notre mode de DEBUG personnel.
        # ( cf ci-dessus « ATTENTION : PERSONNALISATION de notre mode DEBUG » )
        #
        if also_on_screen is None:
            also_on_screen = self._debug_

        if warning_on_reopen is None:
            warning_on_reopen = self._debug_

        # On crée l'objet JOURNAL si besoin.
        #
        if self.logItem is None:

            # Création de l'objet logger qui va nous servir à écrire dans les logs.
            #
            journal = logging.getLogger(log_name)
            self.logItem = journal

            # On met le niveau du logger à DEBUG, comme ça il écrit tout.
            #
            journal.setLevel(logging.DEBUG)

            # Création d'un formateur qui va ajouter le temps, le niveau
            # de chaque message quand on écrira un message dans le log.
            #
            file_format = logging.Formatter(
                fmt = '%(asctime)s - %(levelname)-9s %(message)s',
                datefmt = '%d-%m %H:%M:%S'
                )

            # Création d'un fichier temporaire qui va nous servir d
            # journal d'exécution.
            #
            if directory == '' or not os.path.isdir(directory):
        
                directory = os.getcwd()

            file_prefix = f'#_LOG_for_{log_name}_#_'
            file_object = tempfile.NamedTemporaryFile(
                mode = 'w+t',
                encoding = 'utf-8',
                prefix = file_prefix,
                suffix = '.log',
                dir = directory,
                delete = False
                )

            # Création d'un handler qui va rediriger une écriture du log vers
            # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo.
            #
            file_handler = logging.handlers.RotatingFileHandler(
                file_object.name,
                'a',
                1000000,
                1
                )

            # On met le niveau du handler fichier sur DEBUG, on lui dit qu'il doit
            # utiliser le formateur créé précédement et on ajoute ce handler au
            # logger
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_format)
            journal.addHandler(file_handler)
            self._logHandler = file_handler

            # Création d'un second handler qui va rediriger chaque écriture de log
            # sur la console.
            #
            # On ne crée toutefois ce second handler que si l'appelant veut également
            # que les messages apparaissent à l'écran...
            #
            if also_on_screen:
        
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(logging.INFO)
                journal.addHandler(stream_handler)

            journal.info('')

            journal.debug('')
            journal.debug('OUVERTURE du journal « %s »...', log_name)
            journal.debug('')
            journal.debug('... tenu via PYTHON version %s.', sys.version)
            journal.debug('')

            self._logFile = file_object.name
            journal.info(
                'Les messages seront stockés dans le fichier : %s.',
                file_object.name
                )
            journal.info('')

        else:

            # Un journal existe déjà donc c'est celui-ci que l'on retourne.
            # Par ailleurs, on affiche un warning...
            #
            journal = self.logItem

            if warning_on_reopen:
        
                journal.warning("TENTATIVE d'OUVERTURE d'1 NOUVEAU JOURNAL...")
                journal.warning('ATTENTION : Un journal a déjà été ouvert !!!')
                journal.warning('')
                journal.warning('Nous allons donc nous servir du journal nommé « %s ».',
                                journal.name)
                journal.warning("Par contre, on IGNORE la demande de création d'un journal « %s ».",
                                log_name)
                journal.warning('')

        return journal


    def on_se_presente(
        self,
        module_file: str,
        arguments: list
        ) -> int:
        """ Fonction permettant d'afficher des informations d'ordre général ( nom du module,
        ses arguments, ... ) lorsqu'un module est appelé en tant que __main__.
    
        :param module_file: le nom du fichier appelant ( la valeur de __file__ en général ).
    
        :param arguments: les arguments avec lesquels le module principal qui nous appelle
        a lui-même été appelé ( sys.argv en général ).
    
        :return: le nombre d'éléments contenu dans la liste d'arguments « arguments » qui
        nous a été passée en paramètre. Il s'agit d'un simple len(arguments), mais que
        l'appelant n'aura ainsi pas à refaire...
        """

        log = self.logItem

        # On affiche le nom du module en lettres capitales, i.e le nom du fichier, mais sans
        # son extension.
        #
        (short_name, _) = os.path.splitext(module_file)
        short_name = os.path.basename(short_name)

        log.debug('')
        log.debug('Je me présente :')
        log.debug('================')
        log.debug('')
        log.debug("!!! Hello world, I'm « %s » in Python !!!", short_name.upper())
        log.debug('')

        log.debug('')
        log.debug('Exécution de : %s', module_file)
        log.debug('==============')
        log.debug('')
        log.debug('Ce module est exécuté en tant que MODULE PRINCIPAL.')
        log.debug('')

        # On affiche la liste des paramètres reçus.
        #
        log.debug('')
        log.debug('Paramètres reçus :')
        log.debug('==================')
        log.debug('')

        nb_parameters_in = 0 if arguments is None else len(arguments)

        log.debug('Nombre de paramètres = %s', nb_parameters_in)
        log.debug('Liste des paramètres = %s', arguments)
        log.debug('')

        if arguments is not None:

            for counter, parameter in enumerate(arguments, start=0):

                log.debug(
                    'Paramètre n° %s ie sys.argv[ %s ] = %s',
                    counter,
                    counter,
                    parameter
                    )

        log.debug('')

        return nb_parameters_in


    def debug_mode(
        self,
        state: bool = True
        ):
        """ Pour lancer / arrêter notre mode DEBUG depuis le script
        appelant.

        Cela permet au script appelant de moduler les informations
        que nous émettons, au regard des parties de son corps, plus
        ou moins sensibles / nouvelles, qu'il veut observer.

        :param state: True pour (re)démarrer le mode, False pour
        le stopper.
        """

        self._debug_ = state

        action = 'start' if state else 'stop'
        deco = 22 * '#'
        msg = f'{deco} Mode DEBUG ( {action} ) {deco}'

        self.shw('#' * len(msg))
        self.shw(msg)
        self.shw('#' * len(msg))
        self.shw('')


    def on_dit_au_revoir(
        self,
        log_to_open: bool = None,
        log_to_remove: bool = None,
        pause_to_make: bool = None
        ):
        """ Fonction a appeler avant de quitter ce module. Elle permet
        essentiellement de lancer l'affichage du fichier de LOG... et
        de rendre la main à l'environnement appelant.

        :param log_to_open: faut-il afficher ou non le fichier LOG dans
        un éditeur de TXT.

        :param log_to_remove: faut-il détruire ou non le fichier LOG.

        :param pause_to_make: faut-il marquer une pause en demandant
        à l'utilisateur de frapper sur la touche ENTRÉE, et ce à la
        toute fin des traitements.

        :return:
        """

        # On définit nos paramètres en fonction de notre mode de DEBUG personnel.
        # ( cf ci-dessus « ATTENTION : PERSONNALISATION de notre mode DEBUG » )
        #
        if log_to_open is None:
            log_to_open = self._debug_

        if log_to_remove is None:
            log_to_remove = not self._debug_

        if pause_to_make is None:
            pause_to_make = self._debug_

        # Pour ne pas dire 2 fois au revoir, ni détruire 2 fois
        # le fichier LOG...
        #
        # Normalement, l'utilisateur de ce module doit appeler
        # on_dit_au_revoir() lorsqu’il a fini... mais, au cas où
        # il ne le ferait pas, nous appelons aussi cette fonction
        # dans notre méthode __del__(). Nous réalisons alors ce
        # que nous pouvons encore faire...
        #
        if self._we_already_said_bye:

            # La fonction on_dit_aurevoir() a déjà été appelée
            # par l'utilisateur de ce module. Nous revenons ici
            # probablement depuis notre méthode __del__ qui nous
            # appelle aussi, et ce afin que nous puissions faire
            # ce que nous pouvons encore faire si l’utilisateur
            # du module n’a pas appeler on_dit_aurevoir(), comme
            # il le devrait...
            #
            self.shw_debug('Nous avons déjà dit au revoir...')

        else:

            # Nous sommes ici sûrs que c'est la première
            # fois que nous parcourons cette fonction.
            #
            self._we_already_said_bye = True

            self.shw_info('BYE')
            self.shw_info('')

            # S'il est demandé d'afficher le journal en
            # fin de traitements, on le fait.
            #
            # ... sauf si nous sommes déjà dans notre
            # méthode __del__(), sinon cela va planter car
            # beaucoup d'objets sont déjà potentiellement
            # en cours de destruction !!!
            #
            # CHANGEMENT : Dorénavant, grâce aux fonctions
            # self.shw_info() et self.shw_debug(), on peut
            # appeler edit_file_txt() même depuis __del__().
            #
            if log_to_open:

                # On lance l'éditeur de texte afin que l'
                # utilisateur puisse voir le fichier log.
                #
                self.edit_file_txt(
                    self._logFile,
                    wait = False
                    )

            # On libère le fichier LOG de sa fonction de
            # handler.
            #
            # Ce qui permettra que ce fichier soit détruit
            # s'il est devenu inutile...
            #
            # ... sauf si nous sommes déjà dans notre
            # méthode __del(), sinon cela va planter car
            # bcp d'objets sont déjà potentiellement en
            # cours de destruction !!!
            #
            if self._we_are_inside_del_method:

                pass

            else:

                self.logItem.removeHandler(
                    self._logHandler
                    )

            self._logHandler.close()

            #
            ################################################
            ########## ATTENTION : Cette limite dépassée, il
            ########## ne faut plus écrire dans le LOG car
            ########## Python peut avoir détruit toutes les
            ########## classes qui le gère !!!
            ##########
            ########## En effet, nous avons libéré ci-dessus
            ########## la dernière dépendance à celui-ci, si
            ########## nous n'avions pas demandé à ce que le
            ########## LOG apparaisse aussi à l'écran...
            ################################################
            #

            # On va adopter un comportement final différent
            # suivant que ce script est lancé au travers de
            # Python IDLE ou pas.
            #
            idle_windows = 'pythonw.exe'

            if idle_windows in sys.executable:

                # Lorsque nous sommes sous IDLE, nous en
                # tenons pas compte du paramètre demandant
                # de détruire ou pas le fichier LOG...
                #
                # Dans ce cas, il s'agit en effet, souvent,
                # d'une phase de mise au point d'un script,
                # donc nous laissons quoi qu'il arrive le
                # LOG, afin qu'il puisse être examiné.
                #
                # ATTENTION : Finalement, même sous IDLE, on
                # détruit le fichier LOG si telle est le choix
                # de l'utilisateur. En effet, même s'il s'agit
                # de phases de mises au point, on peut avoir
                # envie de détruire le LOG car il ne va rien
                # nous apporter et que l'on devra le détruire
                # à chaque nouvelle exécution...
                #
                #   self.shw_debug('PS: Je ne détruis pas le LOG')
                #   self.shw_debug('')
                #
                if log_to_remove and os.path.isfile(
                    self._logFile
                    ):

                    self.shw_debug('Destruction du LOG même sous IDLE.')
                    self.shw_debug('')
                    os.remove(self._logFile)

                # Nous sommes sous IDLE donc nous affichons
                # seulement un message avant de rendre la
                # main à cette console.
                #
                #   self.shw_debug('... et je rends la main à IDLE.')
                #
                self.shw_debug('Puis je rends la main à IDLE.')
                self.shw_debug('')

                # Sous IDLE, l'instruction « exit() » ci-
                # dessous aurait aussi tué IDLE... !!!
                #
                # exit()

            else:
    
                # Tout s'est bien passé donc on détruit le
                # fichier LOG, pour ne pas encombrer...
                #
                # On ne va toutefois pas détruire ce fichier
                # tant que l'utilisateur n'a pas frappé la
                # touche entrée.
                #
                if log_to_remove and os.path.isfile(
                    self._logFile
                    ):

                    self.shw_debug('Destruction du LOG.')
                    self.shw_debug('')

                # Nous ne sommes pas sous IDLE, donc nous
                # marquons une pause afin que la fenêtre
                # d'exécution ne disparaisse pas subitement.
                #
                if pause_to_make:

                    input('PRESS ENTER TO CONTINUE...')
                    print()

                # On a laissé le temps à l'utilisateur de
                # consulter le fichier LOG. On peut donc
                # le détruire.
                #
                if log_to_remove and os.path.isfile(self._logFile):

                    os.remove(self._logFile)

                self.shw_debug('FIN DU SCRIPT')
                self.shw_debug('')

                if self._we_are_inside_del_method:

                    self.shw_debug(
                        'Nous nous AUTO-DÉTRUISONS ( __del__ ).'
                        )
                    self.shw_debug(
                        'Pas de « exit() » lancé : sinon cela bug !'
                        )
                    self.shw_debug('')

                    # Nous sommes dans la méthode __del__, nous
                    # ne pouvons lancer le « exit() » de fin.
                    #
                    # En effet, si on l'exécute dans __del__,
                    # Python affiche les msgs suivants :
                    #
                    #       FIN DU SCRIPT
                    #
                    #       Exception ignored in: <function ScriptSkeleton.__del__ at 0x0000021D99CC1510>
                    #       Traceback (most recent call last):
                    #         File "C:\Program Files\make_movie\skeleton.py", line 167, in __del__
                    #         File "C:\Program Files\make_movie\skeleton.py", line 729, in on_dit_au_revoir
                    #       NameError: name 'exit' is not defined
                    #
                    # ... ou ( dans je ne sais plus quelle autre
                    # configuration ) :
                    #
                    #       FIN DU SCRIPT
                    #
                    #       Exception ignored in: <function ScriptSkeleton.__del__ at 0x0000026AC1D11750>
                    #       Traceback (most recent call last):
                    #         File "K:\_Know\Info\Dvpt\RALISA~1\Src\_Python\my Crew History\skeleton.py", line 168, in __del__
                    #         File "K:\_Know\Info\Dvpt\RALISA~1\Src\_Python\my Crew History\skeleton.py", line 722, in on_dit_au_revoir
                    #         File "C:\Program Files\Python310\lib\_sitebuiltins.py", line 26, in __call__
                    #       SystemExit: None
                    #
                    # exit()

                else:

                    self.shw_debug("Ciel ! On m'a tué...")
                    self.shw_debug('')

                    # Finalement, ici aussi nous n'exécutons plus
                    # l'instruction « exit() » ci-dessous...
                    #
                    # exit()

                    # Le mieux est probablement de ne pas lancer
                    # du tout « exit() » !!!
                    #
                    # En effet, cf :
                    #
                    #   https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used/
                    #   in _Know\Info\Dvpt\Réalisation\Langages\Python\- et - exit(), system.exit(), raise SystemExit, etc.rar
                    #
                    #   « Nevertheless, quit should not be used in production code.
                    #   This is because it only works if the site module is loaded.
                    #   Instead, this function should only be used in the interpreter.
                    #   [..]
                    #   However, like quit, exit is considered bad to use in production
                    #   code and should be reserved for use in the interpreter. This is
                    #   because it too relies on the site module. »
                    #
                    # Par ailleurs, si on utilise l'une ou l'
                    # autre des syntaxes suivantes :
                    #
                    #   . raise SystemExit
                    #
                    #   . sys.exit()
                    #
                    # Python communiquera les msgs suivants :
                    #
                    #       FIN DU SCRIPT
                    #
                    #       Exception ignored in: <function ScriptSkeleton.__del__ at 0x000002DBEEB616C0>
                    #       Traceback (most recent call last):
                    #         File "K:\_Know\Info\Dvpt\RALISA~1\Src\_Python\my Crew History\skeleton.py", line 176, in __del__
                    #         File "K:\_Know\Info\Dvpt\RALISA~1\Src\_Python\my Crew History\skeleton.py", line 730, in on_dit_au_revoir
                    #       SystemExit:
                    #
                    # DONC, FINALEMENT, DANS CETTE BRANCHE, ON
                    # NE FAIT PLUS RIEN ( à part des msgs ) !!!
                    #
                    # On pourrait même virer tout le code de
                    # cette fonction à partir du dernier :
                    #
                    #       if self._we_are_inside_del_method:
                    #
                    # J'ai toutefois gardé tout ce code et ces
                    # infos ( commentaires ) pour me souvenir
                    # de tout cela.
                    #


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Fonctions spécifiques à l'OPERATING SYSTEM ( bip, shutdown, ... ).
#
# ---------------------------------------------------------------------------


    def on_sonne_le_reveil(self):
        """ Pour émettre un "beep" afin de prévenir l'utilisateur qu'une action
        lui est demandée...

        :return:
        """

        log = self.logItem

        player = self.get_paths_and_miscellaneous('EXE_player')

        if player is None:

            # Sur la plupart des OS, on utilise une commande
            # très générique, ie envoyer le caractère ASCII
            # \a sur le port de sortie...
            #
            sys.stdout.write('\a')
            sys.stdout.flush()

        else:

            # Sur certains OS, on utilise un logiciel audio,
            # qui va jouer un fichier bien précis.
            #
            # Ainsi, sous Windows XP, on joue un son d'une autre
            # façon que "\a" ci-dessous, car le son généré par 1
            # "\a" y est peu audible...
            #
            # Jouer une mélodie via un player a pour avantage que
            # le son est réglable et que cela marche sur un PC de
            # bureau comme sur un portable...
            #
            cmd_line = [player]

            args = self.get_paths_and_miscellaneous('ARG_player')

            if args is None:
                pass

            elif type(args) in (list, tuple):

                cmd_line += args
                #cmd_line += list(args)
                #
                # Si "args" est un tuple :
                #
                #   cmd_line += args
                #
                # ... est compris par Python.
                #
                # Par contre, dans ce même cas :
                #
                #   cmd_line = cmd_line + args
                #
                # ... provequera une exception !!!
                #
                #   >>> args=('-f', 456,'param', 56)
                #   >>> cmd = ['player']
                #   >>> cmd = cmd + args
                #   Traceback (most recent call last):
                #     File "<pyshell#2>", line 1, in <module>
                #       cmd = cmd + args
                #   TypeError: can only concatenate list (not "tuple") to list
                #   >>> cmd += args
                #   >>> cmd
                #   ['player', '-f', 456, 'param', 56]
                #

            else:
                cmd_line.append(args)

            played = self.get_paths_and_miscellaneous('EXE_played')

            if played is None:
                pass

            else:
                cmd_line.append(played)

            self.shw_debug(f'Player\t= {player}')
            self.shw_debug(f'Played\t= {played}')
            self.shw_debug(f'Args  \t= {args}')
            self.shw_debug(f'liste?\t= {isinstance(args, list)}')
            self.shw_debug('')

            log.debug("Commande exécutée = %s", cmd_line)

            process = subprocess.Popen(cmd_line)
            log.debug('Code Retour : « %s ».', process.returncode)
            log.debug('')


    def shutdown_please(
        self,
        how: str = None
        ):
        """ Pour éteindre la machine hôte lorsque l'on est sous Windows.
    
        Cette fonction ne marche pas dans tous les cas, il faut les privilèges
        "root" pour cela...
    
        Sinon, sous Windows, il faut écrire une fonction plus compliquée qui
        utilise les modules win32security & win32api.
    
        Sous Unix, Linux ou Mac OS, c'est encore autre chose...
    
        :param how: précisions sur la façon de réaliser l'arrêt i-e =
            . 'complete'    : on arrête complètement la machine hôte.
            . 'hibernate'   : on met la machine en veille prolongée.
            . 'none'        : on ne fait rien en fait...
    
        :return:
        """

        log = self.logItem

        if how is None:
            log.debug('SHUTDOWN « par défaut » demandé.')
            how = self.shutdown_dflt

        log.debug('TYPE de SHUTDOWN réalisé : « %s ».', how)
        log.debug('')

        # On attendra 9 mn 33 secondes avant l'arrêt.
        #
        delai_9mn33_en_secondes = 573
        delay_performed_by_system = False

        if os.name.upper() == 'NT':

            # On analyse la façon dont l'arrêt doit être
            # configuré.
            #
            how_lower = how.lower()

            if how_lower == shutdown_complete:

                # On demande l'arrêt total de la machine dans 9 mn.
                #
                command_line = [
                    'shutdown',
                    '-s',
                    '-f',
                    '-t', str(delai_9mn33_en_secondes)
                    ]

                # La temporisation est incluse dans la commande
                # ci-dessus, donc pas besoin que nous la prenions
                # en charge.
                #
                delay_performed_by_system = True

            elif how_lower == shutdown_hibernate:

                # On demande l'hibernation de la machine après une
                # temporisation.
                #
                # RQ : Sous Windows, la demande d'hibernation n'est
                # pas compatible avec le paramètre de temporisation
                # ( '-t' ). Donc on temporisera nous-mêmes avant la
                # demande d'hibernation immédiate...
                #
                command_line = ['shutdown', '-h', '-f']
                delay_performed_by_system = False

            elif how_lower == shutdown_none:
                command_line = None

            else:
                log.warning('UNSUPPORTED PARAMETER :')
                log.warning('')
                log.warning("Le type d'arrêt « %s » est inconnu...", how)
                log.warning('... alors on ne fait rien !!!')
                log.warning('')
                command_line = None

            if command_line is not None:

                self.on_sonne_le_reveil()

                log.info('----------- ARRET EN COURS ------------')
                log.info('')

                if delay_performed_by_system:

                    log.info("Taper une touche pour annuler l'arrêt")
                    log.info('')

                else:

                    log.info("Taper < CTRL + C > pour annuler l'arrêt")
                    log.info('')

                    log.debug("Cause restrictions de Windows...")
                    log.debug("... on va dormir AVANT la demande d'hibernation.")
                    log.debug('')

                    self.shw("J'attends...")
                    self.shw('')

                    try:
                        time.sleep(delai_9mn33_en_secondes)

                    except KeyboardInterrupt:
                        # Si l'utilisateur à frapper < CTRL + C >, on intercepte
                        # cette interruption et on rend la main au programme, sans
                        # mettre la machine en hibernation...
                        #
                        log.debug("HIBERNATION INTERROMPUE")
                        log.debug('')
                        command_line = None

            # Si l'arrêt du système n'a pas été interrompu lors de la temporisation
            # ci-dessus ( qui n'a elle-même eu lieu que si la command_line d'arrêt
            # ne prend pas en charge cette temporisation ), on en vient enfin à cet
            # arrêt.
            #
            if command_line is not None:

                log.debug("Commande exécutée = %s", command_line)
                log.debug('')

                process = subprocess.Popen(command_line)

                log.debug('Code Retour de la commande : « %s ».',
                          process.returncode)
                log.debug('')

                # Si la temporisation a été faite par ce programme, pas besoin d'
                # attendre une nouvelle temporisation.
                #
                # Par contre, si la temporisation est réalisée par le système ( et
                # donc par la dernière commande lancée ), on va ici attendre la fin
                # de cette temporisation...
                #
                if delay_performed_by_system:

                    input("J'attends...")
                    print()

                    # On annule l'arrêt si l'utilisateur l'a demandé.
                    #
                    command_line = ['shutdown', '-a']

                    log.debug("Commande exécutée = %s", command_line)
                    log.debug('')

                    process = subprocess.Popen(command_line)

                    log.debug('Code Retour de la commande : « %s ».',
                              process.returncode)
                    log.debug('')

        else:
            log.critical('UNSUPPORTED SYSTEM :')
            log.critical('')
            log.critical(
                "La procédure d'arrêt machine pour l'OS « %s » n'est pas définie.",
                os.name.upper()
                )
            log.critical('')

            # On ne lève plus d'exception dans ce cas.
            #
            # raise AssertionError


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   - Fonctions spécifiques au TEMPS.
#
# ---------------------------------------------------------------------------


    def build_now_string(
        self,
        desired_form: str = "%Y%m%d - %Hh%Mmn%Ss%fms"
        ) -> str:
        """ Fonction produisant une chaîne de caractère contenant la
        date et l'heure au format désiré.
        
        :param desired_form: format voulu tel que défini dans la doc
        Python pour la fonction « strftime() ».

        :return: la chaîne désirée.
        """

        now = datetime.datetime.now()

        return now.strftime(desired_form)


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Fonctions de SAISIE de DONNÉES.
#
# ---------------------------------------------------------------------------


    def ask_yes_or_no(
        self,
        prompt: str,
        #
        default = None, # Type = BOOL ou STR
        #default: str = None,
        #
        # Permettre que default soit une string OU un booléen ?
        # Afin que la fonction puisse tout simplement retourner
        # « default », sans avoir à chercher sa correspondance
        # dans le dictionnaire de LOCALISATION ( yes_or_no ).
        #
        # « default » ne serait pas typé :
        #
        #   default = None
        #
        # et son type serait testé en entrée de fonction :
        #
        #   if type(default) == bool:
        #       [..]
        #   elif type(default) == str:
        #       [..]
        #
        # ... afin d'adapter notre comportement.
        #
        # => C'est finalement cette dernière solution qui a été
        # retenue.
        #
        langage: str = 'fre',
        retries: int = 3,
        reminder: str = 'Please try again !',
        play_sound: bool = None,
        raise_on_retry_error: bool = False
        ) -> bool:
        """

        // TODO : Cette fonction ask_yes_or_no est à RETRAVAILLER & FINALISER !!!

        :param prompt: le texte de la question.

        :param default: la réponse par défaut.
        Si la valeur spécifiée est de type BOOL, on l'interprète
        telle quelle.
        Si la valeur spécifiée est de type STR, elle doit être une
        des clés présentes dans notre dictionnaire de LOCALISATION
        ( skeleton.yes_or_no ) sinon, en mode DEBUG, on lèvera une
        exception AssertionError via l'instruction « assert ».
        HORS du mode DEBUG, on laissera le script se poursuivre.

        :param langage: le langage qui sera utilisé pour la saisie
        ( en, fr, etc... ) afin d'interroger notre dictionnaire de
        LOCALISATION ( skeleton.yes_or_no ) en conséquence.

        :param retries: le nombre d'essais autorisés.

        :param reminder: le texte à afficher si un essai échoue.

        :param play_sound: faut-il « réveiller » l'utilisateur via
        une sonnerie avant de poser la question la 1ère fois ?

        :param raise_on_retry_error: faut-il lever une exception de
        type ValueError si l'utilisateur dépasse le nombre d'essais
        autorisés ?
        Si FALSE, on renverra la valeur définie par défaut dès que
        ce nombre sera dépassé.
        Si toutefois la valeur par défaut est elle-même incorrecte,
        alors on lèvera l'exception AssertionError via l'instruction
        « assert » : donc en mode DEBUG seul !!!
        HORS du mode DEBUG, toujours pour une valeur par défaut non
        valide, le script plantera sur une exception KeyError à :

            return our_yes_or_no[default]

        Nous aurions pu choisir la solution d'1 fonction ask_yes_or_no
        retournant 3 valeurs possibles : True, False, Invalid. Mais
        cela aurait complexifié le test en retour de cette fonction,
        qui pour l'intant peut simplement être :

            if ask_yes_or_no(...):

        Cette complexification ne semble pas souhaitable pour juste
        parer à une éventualité très rare et, qui plus est, aisément
        détectable et reproductible en mode DEBUG...

        AUTRE SOLUTION POSSIBLE = Renvoyer tout simplement « default »
        si « default » n'est pas 1 clé présente dans yes_or_no[langage].
        Toutefois, nous sommes sûr que « default » n'est pas un booléen
        [ retour attendu de ask_yes_or_no() ] mais plutôt de type STR.
        Il faudrait donc avoir une valeur par défaut qui serait soit un
        booléen, soit un STR : donc un objet dont on testerait le type
        lors des tests sur la validité du paramètre « default ».

        ==> C'est ce qui a finalement été choisi, « default » peut être
        BOOL ou STR, mais le PB reste le MÊME s'il n'est ni l'un ni l'
        autre, ou s'il est STR sans être une clef de yes_or_no[langage],
        c-a-d il y aura plantage du script sur une EXCEPTION KeyError.       

        :return: True ( YES ) or False ( NO ).
        """

        # On définit nos paramètres en fonction de notre mode de DEBUG personnel.
        # ( cf ci-dessus « ATTENTION : PERSONNALISATION de notre mode DEBUG » )
        #
        if play_sound is None:
            play_sound = self._debug_

        # On sonne le réveil si désiré.
        #
        if play_sound:
            self.on_sonne_le_reveil()

        # On vérifie si nous connaissons la liste des façons de dire OUI ou NON
        # dans le langage désiré de la réponse.
        #
        # Si le langage n'est pas référencé, nous présupposons l'anglais.
        #
        if langage not in yes_or_no.keys():

            self.shw(f'Unknown language « {langage} »... Using english...')
            self.shw('')
            langage = 'eng'

        our_yes_or_no = yes_or_no[langage]

        # On vérifie la validité de la réponse par défaut.
        #
        # On affiche cette valeur par défaut en conséquence.
        #
        if default is None:

            dflt_type = None
            dflt_valid = False

        else:

            dflt_type = type(default)

            assert dflt_type in (bool, str), (
                "\n\t Invalid default value = Must be None, bool, or str."
                f"\n\t Here type is = « {dflt_type} »."
                )

            if dflt_type == bool:

                dflt_valid = True

            elif dflt_type == str:

                default = default.strip(whitespace)
                dflt_valid = default != ''

                if dflt_valid:

                    assert default in our_yes_or_no.keys(), (
                        f"\n\t Invalid default value = « {default} »"
                        f" not in « {langage} » dictionary !"
                        )

        if dflt_valid:

            prompt = f'{prompt} [« {default} » par défaut] '

        # On initialise la liste des OUI & NON acceptés.
        # ( en fonction du langage qui a été fixé ).
        #
        # Cette initialisation pourrait se réaliser via deux compréhensions de
        # liste :
        #
        #   our_yes = [ key for key, value in our_yes_or_no.items() if value ]
        #   our_no = [ key for key, value in our_yes_or_no.items() if not value ]
        #
        # ... mais on parcourt alors 2 fois la liste !
        #
        # Avec la solution ci-dessous ( boucle FOR ), la liste n'est parcourue
        # qu'une seule fois.
        #
        # // TODO : Tester laquelle des 2 solutions est la plus rapide ???
        #
        # Cela dit, nous allons ensuite attendre une saisie humaine, donc la
        # rapidité n'est pas ici un facteur discriminant !!!
        #
        # La solution avec une boucle FOR semble aussi la plus lisible.
        #
        our_yes = []
        our_no = []

        for key, value in our_yes_or_no.items():

            if value:
                our_yes.append(key)

            else:
                our_no.append(key)

        # On attend & on traite la réponse de l'utilisateur.
        #
        while True:

            answer = input(prompt)
            print()

            if answer.strip(whitespace) == '':
                answer = default

            if answer in (True, False):
                return answer

            elif answer in our_yes_or_no.keys():
                return our_yes_or_no[answer]

            retries = retries - 1

            if retries <= 0:

                if raise_on_retry_error:
                    raise ValueError('Too much retry...')

                else:
                    assert dflt_valid, (
                        'Too much retry and no correct default value !'
                        )

                    self.shw('Too much retry... Using default !')
                    self.shw('')

                    return (
                        default
                        if dflt_type == bool 
                        else our_yes_or_no[default]
                        )

            self.shw(reminder)
            self.shw(f'OK = {our_yes}')
            self.shw(f'NO = {our_no}')
            self.shw('')


    def choose_in_a_list(
        self,
        choices: list, 
        default_choice: int = -1
        ) -> int:
        """ Prend en charge le choix par l'utilisateur d'une valeur dans une liste.
    
        Cette fonction va afficher la liste d'une manière qui permette à l'utilisateur
        d'exprimer son choix.
    
        REMARQUE : Si la liste n'est constituée que d'un seul élément, alors le choix
        est automatique & cette fonction renvoie aussitôt l'index de cet élément ( ie
        0 donc ).
    
        :param choices: la liste dans laquelle une valeur doit être choisie.
    
        :param default_choice: index du choix par défaut. Cette valeur doit être fixée à -1
        si aucun choix par défaut n'est défini.
    
        :return: l'index dans la liste correspondant au choix ou, sinon, -1 si aucun
        choix possible ( liste vide par exemple ).
        """

        log = self.logItem

        list_length = len(choices)

        # Si la liste est vide, le retour vaudra -1 car pas de choix possible.
        # Si la liste n'a qu'1 élément, le retour vaudra 0 car 1 seul choix possible.
        #
        # Cela se résume en peu de mots... :
        #
        #       if list_length < 2:
        #           the_choice_is = list_length - 1
        #
        # ... mais en fait le code s'est compliqué afin de pouvoir afficher à
        # chaque fois la raison du choix ou du non choix.
        #
        if list_length == 0:
            the_choice_is = - 1
            log.info('Aucun choix disponible...')
            log.info('')

        elif list_length == 1:
            the_choice_is = 0
            log.info('Un seul choix disponible...')
            log.info('')

        # Plusieurs valeurs sont présents dans la liste donc on doit choisir.
        #
        # On présente pour ceci la liste à l'utilisateur afin qu'il fasse son
        # choix.
        #
        else:
            self.shw('Veuillez choisir parmi les réponses suivantes :')
            self.shw('')

            # // TODO : Il serait bon ici de limiter le nombre de réponses affichées
            # et ceci au cas où la LISTE SERAIT TROP LONGUE. Reste à trouver comment...
            #
            for index, an_answer in enumerate(choices, start=0):
                self.shw(f'{index:>3} - {an_answer}')
            self.shw('')

            # On demande son choix à l'utilisateur, i-e le n° de la réponse dans la
            # liste affichée.
            #
            # Via les exceptions et des tests, on va vérifier que l'utilisateur
            # fourni bien une réponse sous forme d'entier, et que cet entier soit
            # compris dans les bornes des index de la liste...
            #
            msg = 'Veuillez indiquer le n° de la réponse choisie '

            if 0 <= default_choice < list_length:
                msg += f'( « {choices[default_choice]} » par défaut ) '

            while True:

                index_given = input(msg + ': ')
                print()

                if index_given == '' and 0 <= default_choice < list_length:
                    the_choice_is = default_choice
                    break

                else:
                    try:
                        index = int(index_given)

                    except ValueError:
                        log.warning(
                            "La donnée saisie n'est pas un entier : « %s » !!!",
                            index_given
                            )
                        log.warning('')

                    else:
                        if 0 <= index < list_length:
                            the_choice_is = index
                            break

                        else:
                            log.warning(
                                "Veuillez indiquer un nombre compris entre 0 et %s.",
                                #str(list_length - 1)
                                list_length - 1
                                )
                            log.warning('')

            log.debug('Index choisi     : %s', the_choice_is)
            log.debug('Valeur associée  : %s', choices[the_choice_is])
            log.debug('')

        return the_choice_is


    def choose_in_a_dict(
        self,
        dict_of_choices: dict,
        default_key: object = None,
        restricted: bool = True
        ) -> object:
        """ Prend en charge le choix par l'utilisateur d'une valeur dans un dictionnaire.

        Cette fonction va afficher le dictionnaire d'une manière qui permette à
        l'utilisateur d'exprimer son choix.

        REMARQUE : Si le dictionnaire n'est constitué que d'un seul élément, alors le
        choix est automatique & cette fonction renvoie aussitôt la clé de cet élément.

        :param dict_of_choices: le dictionnaire dans lequel une valeur doit être choisie.

        :param default_key: clé du choix par défaut. Cette valeur doit être fixée à
        None si aucun choix par défaut n'est défini.

        :param restricted: faut-il restreindre le choix aux seules valeurs présentes
        dans le dictionnaire, ou l'utilisateur peut-il saisir une clé inconnue ?
        Si "restricted" vaut True, seules les valeurs du dictionnaire sont acceptées.

        :return: la clé choisie ou, sinon, None si aucun choix possible ( dictionnaire
        vide par exemple ).
        """

        log = self.logItem

        dict_length = len(dict_of_choices)
    
        # Si le dictionnaire est vide, le retour vaudra None car pas de choix possible.
        # Si la liste n'a qu'1 élément, le retour vaudra sa clé car 1 seul choix possible.
        #
        if dict_length == 0:
            the_choice_is = None
            log.info('Aucun choix disponible...')
            log.info('')

        elif dict_length == 1:
            the_choice_is = list(dict_of_choices.keys())[0]
            log.info('Un seul choix disponible...')
            log.info('')

        # Plusieurs valeurs sont présents dans le dictionnaire donc on doit choisir.
        #
        # On présente pour ceci le dictionnaire à l'utilisateur afin qu'il fasse son
        # choix.
        #
        else:
            self.shw('Veuillez choisir parmi les réponses suivantes :')
            self.shw('')
            self.shw('  N° -   CLEF   =   VALEUR')
            self.shw(' ' + 33 * '-')

            # // TODO : Il serait bon ici de limiter le nombre de réponses affichées
            # et ceci au cas où la LISTE SERAIT TROP LONGUE. Reste à trouver comment...
            #
            for idx, item in enumerate(sorted(dict_of_choices.items()), start=0):
                self.shw(f' {idx:>3} - {item[0]:>8} = {item[1]}')
            self.shw('')

            # On demande son choix à l'utilisateur, i-e le n° de la réponse dans la
            # liste affichée.
            #
            # L'utilisateur peut aussi saisir directement l'une des clés ( on va
            # considérer qu'il a saisi une clé si sa réponse n'est pas un entier
            # compris dans la liste des index affichés ).
            #
            msg = 'Veuillez indiquer un n° de réponse ou une clef '

            if not restricted or default_key in dict_of_choices:
                msg += f'( « {default_key} » par défaut ) '
 
            while True:

                answer = input(msg + ': ')
                print()

                log.debug("La donnée saisie est : « %s ».", answer)
                log.debug('')

                if answer == '':
                    # Si la réponse est vide et qu'il existe une
                    # réponse par défaut digne de ce nom, on peut
                    # enregistrer cette réponse.
                    #
                    if not restricted or default_key in dict_of_choices:
                        the_choice_is = default_key
                        break

                else:
                    # Par défaut, on considère que la réponse est une
                    # clé & non un des index leur faisant face, mais
                    # l'on va vérifier cela en analysant la réponse...
                    #
                    the_choice_is = answer

                    try:
                        index = int(the_choice_is)

                    except ValueError:
                        # La réponse n'est pas un entier, l'utilisateur a donc bien
                        # voulu signifier une clé , qu'elle existe déjà ou qu'elle
                        # soit nouvelle. On en prend bonne note...
                        #
                        log.debug("La réponse n'est pas un entier donc c'est une clef.")
                        log.debug('')

                    else:
                        if 0 <= index < dict_length:
                            # La réponse est un entier qui correspond aux index
                            # affichés en face des clés, on retrouve donc la clé
                            # associées.
                            #
                            # On pourrait pour ceci écrire :
                            #
                            #       list(sorted(dict_of_choices.keys()))[index]
                            #
                            # ... toutefois, comme c'est une autre formule qui a
                            # été utilisée pour l'affichage, et comme on veut être
                            # sûr que l'on retrouvera exactement la clé en face de
                            # l'index donné, on réutilise exactement la formule qui
                            # a servie à l'affichage pour retrouver cette clé.
                            #
                            the_choice_is = list(sorted(dict_of_choices.items()))[index][0]
                            log.debug("La réponse est un index.")
                            log.debug('')

                        else:
                            # La réponse est bien un entier, mais qui ne peut
                            # représenter l'un des index affichés en face d'une
                            # clé, nous allons donc supposer que l'utilisateur
                            # a voulu signifier une clé, qu'elle existe ou qu'
                            # elle soit nouvelle. On la retient donc.
                            #
                            log.debug("La réponse est un entier hors index donc une clef.")
                            log.debug('')

                    finally:
                        # On a traduit la réponse sous forme de clé. Si cette
                        # clé existe déjà, tout va bien ; sinon on demande
                        # confirmation qu'il s'agit bien d'une nouvelle clé et
                        # non d'une erreur de frappe.
                        #
                        # Si c'est une erreur, on reboucle...
                        #
                        # Si les réponses sont en fait restreintes au dictionnaire,
                        # on reboucle aussi...
                        #
                        if the_choice_is in dict_of_choices:
                            break

                        else:
                            log.warning(
                                "« %s » n'est pas une clef connue...",
                                #str(the_choice_is)
                                the_choice_is
                                )

                            if restricted:
                                # Si les clés inconnues ne sont pas autorisées, alors
                                # on reboucle.
                                #
                                log.warning("... or les clefs inconnues sont interdites !")
                                log.warning('')

                            else:
                                # Si cette nouvelle clé est confirmée par l'utilisateur,
                                # on pourra quitter. Sinon on redemande une nouvelle
                                # réponse...
                                #
                                log.warning('')
                                prompt = 'Confirmez-vous cette réponse ?'

                                if ask_yes_or_no(prompt, 'o'):
                                    break

            log.debug('Clef choisie    : %s', the_choice_is)
            if the_choice_is in dict_of_choices:
                log.debug(
                    'Valeur associée : %s',
                    dict_of_choices[the_choice_is]
                    )
            log.debug('')

        return the_choice_is


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Fonctions de GESTION de FICHIERS.
#
# ---------------------------------------------------------------------------


    def search_files_from_a_mask(
        self,
        directory: str = None,
        mask: str = '*'
        ) -> list:
        """ Cherche dans un répertoire tous les fichiers qui
        correspondent à un certain masque.

        :param directory: le répertoire à explorer.

        :param mask: le masque de recherche.

            Masques de recherche acceptés :

                - "*" : tous les fichiers.

                - "*.xxx" : les fichiers d'un certain type.

                - "title*.m*" : masque plus complexe.

        :return: la liste des fichiers trouvés.
        """

        log = self.logItem

        if directory is None:

            log.debug('Pas de répertoire de recherche indiqué.')
            log.debug('Donc ce sera le répertoire de travail.')

            # On n'appelle pas ici get_paths_and_miscellaneous()
            # car on sait que 'working_PATH_FULL' est toujours
            # défini à ce stade...
            #
            directory = self.paths_and_miscellaneous[
                'working_PATH_FULL'
                ]

        log.debug('Recherche de fichiers dans : %s.', directory)

        # On initialise la liste des fichiers trouvés.
        #
        found_files = []

        # On regarde si l'on est face à une recherche simple
        # ( du type "*" ou "*.nnn" ) ou face à une recherche
        # plus complexe ( du type "title*.m*" ).
        #
        # On a séparé ces 2 cas pour des raisons de performance
        # mais le 1er n'est qu'un sous cas du 2nd, et on pourrait
        # donc les réunir ( si l'on veut plus de simplicité du
        # code )...
        #
        if mask == '*':

            # Cas d'1 chaîne de recherche très simple i-e : « * ».
            #
            simple_search = True
            suffix = ''
            log.debug('On accepte ici tous les fichiers.')

        elif mask[0] == '*' and not '*' in mask[1:]:

            # Cas d'1 chaîne de recherche simple i-e : « *< suffix > ».
            #
            simple_search = True
            suffix = mask[1:]
            log.debug("Recherche des fichiers d'extension : « %s ».", suffix)

        else:

            # Cas d'1 chaîne de recherche complexe telle : « title_t*.mkv ».
            #
            simple_search = False

            index_suffix = mask.rfind('.')
            if index_suffix >= 0:
                suffix = mask[index_suffix:]
            else:
                suffix = ''

            log.debug('Recherche de fichiers du type : « %s ».', mask)
            log.debug('... donc avec « %s » comme extension.', suffix)

        # On lance la recherche dans le répertoire.
        #
        if simple_search:

            suffix_lower = suffix.lower()

            for file_or_dir in os.listdir(directory):

                # Si le fichier a le suffixe voulu, on l'intègre à la liste.
                #
                # Pour ceci, le plus "universel" est de vérifier que l'on trouve
                # bien le suffixe cherché en toute fin du nom du fichier et, pour
                # réaliser ce test, on utilise ici la méthode rfind().
                #
                # Cette fonction va trouver l'occurence, si elle existe, du suffixe
                # que nous cherchons et qui serait située la plus à droite dans
                # le nom du fichier. Si cette occurence est trouvée, rfind() nous
                # informe de l'index dans le nom de fichier où l'on peut trouver
                # cette occurence. Or si cet index est égal à la soustraction de
                # la longueur du nom de fichier par la longueur du suffixe, c'est
                # que le suffixe est bien situé en toute fin du nom de fichier...
                #
                # PAR CONTRE, pour réaliser la comparaison via rfind(), on convertit
                # d'abord les 2 chaînes en minuscules, et ceci afin que, par exemple :
                #
                #       - si suffix = « .mkv » ;
                #
                #       - si certains fichiers finissent en « .mkv », d'autres en
                # « .MKV », et d'autres en « .Mkv » ;
                #
                #       - alors tous ces fichiers ressortent dans la liste !!!
                #
                # Bien sûr, avant d'intégrer le fichier à la liste, on vérifie que
                # c'est bien un fichier et non un répertoire !!! ( opération qui
                # est certainement plus longue que les autres opérations de test
                # donc on la réalise en dernier )
                #
                # ATTENTION : Avant, au regard de l'algorithme décrit ci-dessus,
                # le test effectué était :
                #
                #       if suffix == '' or \
                #       (file_or_dir.lower().rfind(suffix_lower) == len(file_or_dir) - len(suffix)):
                #
                # ... mais, pour des noms de fichiers courts, type « @i », ce test
                # ( sa 2ème partie ) ne marchait pas avec, par exemple, « *.py » :
                #
            	#	    - file_or_dir = @i
            	#	    - suffix_lower = .py
            	#	    - file_or_dir.lower().rfind(suffix_lower) = -1 [ car échec de la recherche ]
            	#	    - len(file_or_dir) - len(suffix) = 2 - 3 = -1
                #
                # ... d'où la réécriture de ce test ci-dessous.
                #
                # Ce teste marche d'ailleurs pour des données telles :
                #
                #       - masque = « *.py »
                #       - fichier = « .py »
                #
                suffix_place = file_or_dir.lower().rfind(suffix_lower)

                if suffix == '' or \
                    (suffix_place >= 0 and \
                     len(file_or_dir) >= len(suffix) and \
                     suffix_place == len(file_or_dir) - len(suffix)):

                    if os.path.isfile(file_or_dir):
                        found_files.append(file_or_dir)

        else:

            # Conversion de la chaîne de recherche demandée en une liste afin
            # de faciliter, par la suite, les comparaisons des noms de fichiers
            # avec le masque de recherche...
            #
            # On découpe ainsi le masque de recherche en considérant le caractère
            # joker '*' comme un délimiteur.
            #
            mask_list = mask.split('*')
            log.debug('Le masque de recherche changé en liste vaut : %s.', mask_list)

            # PAR CONTRE, pour réaliser les comparaisons, on va convertir les
            # éléments en minuscules...
            #
            # Cf ci-dessus « PAR CONTRE, pour réaliser la comparaison via rfind() ».
            #
            for idx, mask_part in enumerate(mask_list, start=0):
                mask_list[idx] = mask_part.lower()
            log.debug('La liste de recherche convertie en minuscules vaut : %s.', mask_list)

            for file_or_dir in os.listdir(directory):
                # Si on est face à un fichier ( et non un répertoire ), on va ici
                # comparer si le nom de ce fichier correspond au masque désiré.
                #
                if os.path.isfile(file_or_dir):

                    file_ok = True

                    # Pour réaliser les comparaisons, on va convertir en minuscules.
                    # Cf ci-dessus « PAR CONTRE, pour réaliser la comparaison via rfind() ».
                    #
                    file_name = file_or_dir.lower()

                    # On va chercher si le nom du fichier contient chacune des
                    # sous-chaînes de la liste correspondant au masque de recherche.
                    #
                    # ATTENTION : On ne teste ici "que" si la sous-chaîne se trouve
                    # dans le nom de fichier. Pour être plus exact, il faudrait
                    # vérifier, quand le masque est de type « xxx*(..)*zzz », si la
                    # 1ère sous-chaîne est bien le début ( et exactement le début )
                    # du nom de fichier...
                    #
                    #       en utilisant : file_name.startswith(mask_part)
                    #
                    # ... mais également vérifier que la dernière sous-chaîne est bien
                    # la fin ( et exactement la fin ) du nom de fichier...
                    #
                    #       en utilisant : file_name.endswith(mask_part)
                    #
                    # ... Cela pourra faire l'objet, si nécessaire, d'1 développement
                    # ultérieur.
                    #
                    # Pour l'instant, ce n'est pas très dérangeant, donc on laisse tel
                    # quel. Du coup, pour les masques du type « xxx*(..)*zzz », cette
                    # fonction réalise en fait une recherche du type :
                    #
                    #       « *xxx*(..)*zzz* »
                    #
                    # ADDENDUM : Le fait de réaliser une recherche type « *xxx*(..)*zzz* »
                    # alors que nous a été demandé une recherche « xxx*(..)*zzz » est en
                    # fait plus dérangeant que prévu. Ainsi, lors d'une recherche ayant
                    # pour masque « title_t*.mkv », les solutions suivantes sont sorties
                    # à l'écran ( !!! ) :
                    #
                    #       - ( 2 ) what to encode - from « title_t00.mkv ».cfg
                    #       - title_t03.mkv
                    #       - >>> CRÉATION d'un fichier de configuration [..] <<<
                    #
                    # EXPLICATIONS : Nous avons demandé « title_t*.mkv » donc, avec une
                    # recherche « xxx*(..)*zzz », seul "title_t03.mkv" serait apparu.
                    #
                    # Mais comme nous avons réalisé une recherche « *xxx*(..)*zzz* »,
                    # "( 2 ) what to encode - from « title_t00.mkv ».cfg" est aussi
                    # valide dans ce cadre !!!
                    #
                    # Nous avons donc renvoyé à notre appelant ces 2 solutions...
                    #
                    # Or, search_files_from_a_mask() était alors appelée depuis le point
                    # "3ème partie : On cherche" de la fonction MediaFile.choose_file(),
                    # ce qui a provoqué, dans la suite des traitements ( "4ème partie :
                    # On ajoute éventuellement des solutions possibles..." ) de choose_file(),
                    # que la solution ">>> CRÉATION d'un fichier de configuration [..] <<<"
                    # soit ajoutée. En effet, cette dernière est ajoutée automatiquement
                    # si apparaît dans la liste des fichiers résultat au moins un .CFG !!!
                    #
                    # CONCLUSION : Il a fallu rendre plus exact l'algorithme ci-dessous
                    # afin qu'une recherche type « xxx*(..)*zzz » ne soit plus traitée
                    # comme une recherche type « *xxx*(..)*zzz* ».
                    #
                    # D'où l'ajout des 2 "if" couplés aux fonctions startswith() et
                    # endswith().
                    #
                    # Il aurait été probablement plus efficace d'intégrer les tests
                    # de ces "if" à la boucle "for" qui suit : en effet, dans cette
                    # boucle "for", on teste de nouveau la 1ère et la dernière sous-
                    # chaînes de recherche ( déjà testées dans les "if" ).
                    #
                    # Toutefois, d'une part, ces 2 "if" facilitent la lecture de l'
                    # algorithme et, d'autre part, ils sont plus rapides à écrire !!!
                    #
                    # Lorsque j'aurais plus de temps, il sera possible d'améliorer
                    # cet algorithme...
                    #
                    if mask[0] != '*' and not file_name.startswith(mask_list[0]):
                        file_ok = False

                    elif mask[len(mask) - 1] != '*' and \
                            not file_name.endswith(mask_list[len(mask_list) - 1]):
                        file_ok = False

                    else:
                        for mask_part in mask_list:

                            if mask_part in file_name:
                                # On trouve bien la sous-chaîne considérée dans le nom de
                                # fichier. On retire alors du nom de fichier la séquence
                                # "*<cette sous-chaîne>", puis on va continuer la boucle
                                # afin de vérifier que les sous-chaînes suivantes sont bien
                                # présentes dans ce qui reste du nom de fichier...
                                #
                                part_index_begin = file_name.index(mask_part)
                                part_index_end = part_index_begin + len(mask_part)
                                file_name = file_name[part_index_end:]

                            else:
                                # Une des sous-chaînes recherche n'est pas présente dans
                                # le nom du fichier. On ne retient donc pas ce fichier...
                                #
                                file_ok = False
                                break

                    if file_ok:
                        # Si toutes les sous-chaînes recherche étaient présentes dans
                        # le nom du fichier, on ajoute ce fichier à la liste de retour...
                        #
                        found_files.append(file_or_dir)
                        log.debug('Nouveau fichier trouvé : « %s ».', file_or_dir)

        return found_files


    def convert_to_pdf_init(
        self
        ) -> bool:
        """ Conversion de fichier(s) DOCX ( ou ODT, TXT, etc )
        en fichier(s) PDF :

                PHASE D'INITIALISATION

        :return: opération réussie ou non.
        """

        log = self.logItem
        no_error = True

        # Pour convertir en PDF, on va faire appel à LibreOffice.
        # En effet, le format PDF est complexe à gérer !!!
        # Créer un PDF avec beaucoup de lignes TXT me semble
        # compliqué !!!
        #
        # Cf :
        #
        #   _Know\Info\Dvpt\Réalisation\Langages\Python\- et - PDF.rar
        #
        # On lance donc dès que possible LibreOffice. Comme cela,
        # lorsque nos traitements seront finis, ce logiciel aura
        # certainement achevé son initialisation...
        #
        # Il nous suffira de communiquer avec lui pour lui demander
        # la conversion.
        #
        log.debug('Initialisation de LibreOffice :')
        log.debug('')

        libre_office_exec = self.get_paths_and_miscellaneous(
            'EXE_libre_office'
            )

        if libre_office_exec is None:
            no_error = False

        else:

            log.debug('... i-e lancement de : « %s »', libre_office_exec)
            log.debug('')

            command_line = [
                libre_office_exec,
                #
                # --headless permet de lancer LibreOffice sans son
                # interface utilisateur. ( Starts in "headless mode"
                # which allows using the application without user
                # interface. This special mode can be used when the
                # application is controlled by external clients via
                # the API https://api.libreoffice.org/ )
                #
                '--headless',
                '--nocrashreport',
                '--nodefault',
                '--nofirststartwizard',
                '--nolockcheck',
                '--nologo',
                '--norestore'
                ]

            log.debug("Commande exécutée = %s", command_line)
            log.debug('')

            # On utilise Popen() car run() attend lui que Libre
            # Office nous rende la main, ce qu'il ne fait que si
            # on le ferme... puisqu'on ne lui demande rien de
            # spécifique à faire et que donc Libre Office garde
            # la main !!!
            #
            #   process = subprocess.run(command_line)
            #
            # Cela dit, il doit y avoir un paramètre de run() qui
            # permet cela.
            #
            process = subprocess.Popen(command_line)

            log.debug('Code Retour : « %s ».', process.returncode)
            log.debug('')

        return no_error


    def convert_to_pdf_run(
        self,
        *args,
        wait: bool = True
        ) -> bool:
        """ Conversion de fichier(s) DOCX ( ou ODT, TXT, etc )
        en fichier(s) PDF :

                PHASE DE CONVERSION

        :param *args: tuple des fichiers à convertir.

        :param wait: attend-t-on la fin de la conversion pour
        rendre la main à la fonction appelante ? ou pas...

        :return: opération réussie ou non.
        """

        log = self.logItem
        no_error = True

        # On demande à LibreOffice de convertir nos fichiers
        # en PDF.
        #
        # Pour ceci, j'ai choisi de simplement relancer Libre
        # Office avec les paramètres adéquats. Comme il est
        # déjà en tâche de fond ( grâce à l'initialisation via
        # convert_to_pdf_init ), Libre Office va alors attraper
        # cet appel et le réaliser...
        #
        # RQ : Si convert_to_pdf_init() n'a pas été déjà lancée,
        # pas de souci... Ça marchera, quand même, mais ce sera
        # certainement bien plus long car il faudra attendre le
        # lancement de LibreOffice.
        #
        log.debug("Conversion de fichier(s) en PDF via LibreOffice :")
        log.debug('')

        libre_office_exec = self.get_paths_and_miscellaneous(
            'EXE_libre_office'
            )

        if libre_office_exec is None:
            no_error = False

        else:

            # Cf https://wiki.openoffice.org/wiki/API/Tutorials/PDF_export
            # Cf https://www.libreofficehelp.com/batch-convert-writer-documents-pdf-libreoffice/
            # Cf https://stackoverflow.com/questions/30349542/command-libreoffice-headless-convert-to-pdf-test-docx-outdir-pdf-is-not
            #
            #   --convert-to pdf:writer_pdf_Export:{"Magnification":{"type":"long","value":"2"}}
            #   --convert-to pdf:writer_pdf_Export:{"Zoom":{"type":"long","value":"75"}}
            #
            format_cible = 'pdf:writer_pdf_Export'
            #format_cible += ':{'
            #format_cible += '"Magnification":{"type":"long","value":"4"}'
            #format_cible += ','
            #format_cible += '"Zoom":{"type":"long","value":"75"}'
            #format_cible += '}'
            #
            # Je n'ai pas réussi à faire fonctionner les configurations PDF
            # ci-dessus... Il faut probablement utiliser les UNO tools pour
            # finement choisir nos paramètres.
            #
            # Cf - et - Communications ( pipe, socket ).rar\UNO tools = unotools-0.3.3\
            # in _Know\Info\Dvpt\Réalisation\Langages\Python\
            #
            # L'utilisation des UNO tools PERMETTRAIT PAR EXEMPLE DE CHOISIR
            # LA FONT POUR CONVERSION D'UN FICHIER .TXT vers PDF, ODT, ...
            #

            for file_in in args:

                command_line = [
                    libre_office_exec,
                    #
                    # --invisible :
                    #
                    #   Drapeau que j'utilisais dans mon ancien batch DOS
                    #   "INVENTAIRE - #NotSynchronized.bat" ie je lançais :
                    #
                    #   SET LiO_DEFAULT="C:\Program Files\LibreOffice 5\program\soffice.exe"
                    #   [..]
                    #   SET LibreOffice=%LiO_DEFAULT%
                    #   SET NOM_LENOVO_S340=BONZZZ-7
                    #   SET LiO_LENOVO_S340="C:\Program Files\LibreOffice\program\soffice.exe"
                    #   [..]
                    #   IF '%PC_NAME%' == '%NOM_LENOVO_S340%' SET LibreOffice=%LiO_LENOVO_S340%
                    #   [..]
                    #   %LibreOffice% --invisible macro:///Standard.Convert.ConvertTXTtoPDF(%RESULT_FILE_TXT%)
                    #
                    # ... mais que j'ai finalement retiré car, après, si
                    # je souhaitais lancer LibreOffice en interactif, je
                    # n'y avais plus accès, à moins de tuer chaque process
                    # LibreOffice avant de le lancer !
                    #
                    #'--invisible',
                    '--convert-to', format_cible,
                    '--outdir', '.',
                    file_in
                    ]

                log.debug("Fichier à traiter = %s", file_in)
                log.debug("Commande exécutée = %s", command_line)

                if wait:

                    # Il est ici demandé que convert_to_pdf_run()
                    # garde la main tant que la conversion n'est
                    # achevée.
                    #
                    # J'utilise donc run() et non Popen(), car c'
                    # est ainsi ce que LibreOffice va faire.
                    #
                    # C'est parfait puisque lorsque l'on va enfin
                    # retrouver la main, on saura que la conversion
                    # sera achevée ( et donc on sera sûr que le PDF
                    # est bien présent... ).
                    #
                    log.debug('... exécution SYNCHRONE.')
                    process = subprocess.run(command_line)

                else:

                    # On rend la main à l'appelant dès que l'on
                    # a lancé la conversion, sans se soucier de
                    # si elle est achevée ni comment...
                    #
                    log.debug('... exécution ASYNCHRONE.')
                    process = subprocess.Popen(command_line)

                log.debug('')
                log.debug('Code Retour : « %s ».', process.returncode)
                log.debug('')

        return no_error


    def edit_file_txt(
        self,
        *args,
        wait: bool = True
        ):
        """ Édition d'un ou plusieurs fichiers au format TXT.

        :param *args: tuple des fichiers à éditer.

        :param wait: attend-t-on la fin de l'édition pour
        rendre la main à la fonction appelante ? ou pas...
        """

        self.shw_debug('Édition de fichier(s) TXT :')
        self.shw_debug('')

        # On retrouve l'éditeur de texte.
        #
        exe_txt_editor = self.get_paths_and_miscellaneous(
            'EXE_txt_editor'
            )

        if exe_txt_editor is None:
            pass
        else:

            for file_to_edit in args:

                # On lance l'éditeur de texte avec notre fichier
                # comme paramètre.
                #
                command_line = [exe_txt_editor, file_to_edit]

                self.shw_debug(
                    f'Fichier à traiter = {file_to_edit}'
                    )
                self.shw_debug(
                    f'Commande exécutée = {command_line}'
                    )

                if wait:

                    # Il est demandé que edit_file_txt() garde la
                    # main tant que la conversion n'est achevée.
                    #
                    # J'utilise donc run() et non Popen(), car c'
                    # est ainsi ce que LibreOffice va faire.
                    #
                    # C'est parfait puisque lorsque l'on va enfin
                    # retrouver la main, on saura que la conversion
                    # sera achevée ( et donc on sera sûr que le PDF
                    # est bien présent... ).
                    #
                    self.shw_debug('... exécution SYNCHRONE.')
                    process = subprocess.run(command_line)

                else:

                    # On rend la main à l'appelant dès que l'on
                    # a lancé la conversion, sans se soucier de
                    # si elle est achevée ni comment...
                    #
                    self.shw_debug('... exécution ASYNCHRONE.')
                    process = subprocess.Popen(command_line)

                self.shw_debug('')
                self.shw_debug(
                    f'Code Retour : « {process.returncode} ».'
                    )
                self.shw_debug('')


    def compare_files(
        self,
        *args,
        action: str = 'difference',
        txt_compare: bool = True
        ) -> set:
        """ Comparaison de 2 ou plusieurs fichiers.

        :param *args: tuple des fichiers à comparer.

        :param action: comment veut-on comparer ?
        ( le fichier figurant en 1er constitue la RÉFÉRENCE )
            . intersection,
            . difference ( par défaut ),
            . difference symétrique
            . union.

        :param txt_compare: faut-il comparer au format texte
        ( par défaut ) ou au format binaire...

        :return: le résultat de la comparaison.
        """

        if txt_compare:
            flag = 'rt'
        else:
            flag = 'rb'


        # On ouvre les 2 fichiers, on les
        # transforme en ensembles, puis on
        # utilise les fonctions prédéfinies
        # sur les ensembles pour obtenir le
        # résultat cherché...
        #
        with open(args[0], flag) as file1:
            with open(args[1], flag) as file2:

                if action == 'intersection':
                    # comparaison = set(file1).intersection(file2)
                    comparaison = set(file1) & set(file2)
                
                elif action == 'difference':
                    # comparaison = set(file1).difference(file2)
                    comparaison = set(file1) - set(file2)

                elif action == 'difference symétrique':
                    # comparaison = set(file1)
                    #                .symmetric_difference(file2)
                    comparaison = set(file1) ^ set(file2)

                elif action == 'union':
                    # comparaison = set(file1).union(file2)
                    comparaison = set(file1) | set(file2)

                else:
                    raise ValueError


        # On supprime les lignes vides de
        # l'ensemble résultat.
        #
        comparaison.discard('\n')

        return comparaison


    def get_unused_filename(
        self,
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
            # RQ : Nous sommes obligés de doubler
            # les accolades ( {{ et }} ) ci-dessous
            # dans la définition de format_mask afin
            # de signifier à cette F-STRING que nous
            # voulons le caractère spécial accolade
            # en tant que tel ( et que ce n'est pas
            # un nom de variable qui va être inclus
            # entre accolades à cet endroit )... La
            # F-STRING ne va donc interpréter que la
            # partie {idx_size}.
            #
            basename, ext = os.path.splitext(filename)
            format_mask = f' - {{:0{idx_size}d}}'

            suffix_n = idx_start

            while True:

                # Nous construisons d'abord le suffix
                # sous format de chaîne.
                #
                # Puis nous ajoutons ce suffixe au nom
                # de fichier.
                #
                # Nous avons séparé cette opération en
                # 2 ( nous aurions pu utiliser .format
                # pour tout faire en 1 seule fois ) car
                # basename peut contenir « { » ou « } »
                # ( ce qui ferait planter .format !!! ).
                #
                # Il aurait probablement été possible de
                # réaliser cette concaténation en 1 fois
                # via une F-STRING, mais c'est beaucoup
                # moins lisible...
                #
                suffix = format_mask.format(suffix_n)
                alt_name = basename + suffix + ext

                if not os.path.exists(alt_name):
                    break

                suffix_n += 1

        # Nous retournons le nom de fichier qui
        # convient.
        #
        return alt_name


    def save_strings_to_file(
        self,
        *args,
        destination: str,
        ok_to_erase: bool = False,
        ask_confirm: bool = True,
        must_be_new: bool = False,
        new_suffix: str = ' { new version }',
        coding: str = coding_default,
        ) -> str:
        """ Pour sauvegarder une ou des chaînes de
        caractères dans un fichier.

        :param *args: la suite de strings à stocker.

        :param destination: nom du fichier à créer.
        S'il existe déjà, un nouveau nom de fichier
        sera bâti à partir de destination, sauf si
        ok_to_erase ci-dessous est à True.

        :param ok_to_erase: True si l'on veut que le
        fichier soit écrasé s'il existe déjà.

        :param ask_confirm: True si l'on veut qu'une
        confirmation soit demandée avant d'écraser le
        fichier.

        :param must_be_new: si l'on veut forcément que
        le nom de fichier soit « inspiré », dérivé, du
        nom qui nous a été fourni, sans être le même...
        i-e s'il faut forcément créé un nouveau nom.

        :param new_suffix: le suffix qui doit être accolé
        au nom de fichier qui nous a été fourni, si l'on
        doit bâtir un nouveau nom.

        :param coding: quel est le jeu de caractères
        du fichier à créer ? Cela nous permet surtout
        de savoir s'il faut créer un fichier « byte »
        ou un fichier texte...

            !!! ATTENTION !!!
            D'après la CONVENTION adoptée dans ce script,
            None ou coding_bytes indique un encodage en
            « byte strings ».

        :return: le nom du fichier créé (au cas où nous
        ayions dû bâtir un nouveau nom...).
        """

        log = self.logItem
        new_name = os.path.exists(destination)

        if new_name:

            new_name = not ok_to_erase
            
            if ok_to_erase and ask_confirm:

                msg = (
                    'ATTENTION : Nous allons écraser'
                    f' « {destination} » !!!'
                    )

                new_name = not self.ask_yes_or_no(msg, 'n')

        if new_name or must_be_new:

            # On créé un nouveau nom de fichier si celui
            # qui nous a été donné ne peut être utilisé.
            #
            name, ext = os.path.splitext(destination)

            tmp_dst = name + new_suffix + ext

            file_dst = self.get_unused_filename(
                tmp_dst,
                idx_force = True
                )

        else:

            # On peut se servir tel quel du nom de fichier
            # qui nous a été fourni.
            #
            file_dst = destination

        if coding is None:

            # Le jeu de caractères qui nous concerne est
            # celui des « byte strings ». Donc on ouvre
            # notre fichier au format « b(yte) ».
            #
            flag = "wb"

        else:

            # On ouvre notre fichier au format « t(ext) ».
            #
            flag = "wt"

        log.debug('Coding en entrée = « %s »', coding)
        log.debug('Format en sortie = « %s »', flag)
        log.debug('')

        self.shw(f'Destination = {file_dst}')
        self.shw_debug(f'Format = « {flag} »')
        self.shw('')

        with open(file_dst, flag) as new_file:

            for content in args:

                new_file.write(content)

        return file_dst


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Fonctions spécifiques au WEB ( browser, HTML, HTTP, etc ).
#
# ---------------------------------------------------------------------------


    def url_to_valid(
        self,
        url: str
        ) -> str:
        """ S'assure qu'une URL soit valide, i.e
        ne comporte pas de caractères interdits,
        et renvoie si nécessaire l'URL adéquate,
        ou l'URL inchangée si elle était déjà
        valide.

        Cf par exemple le message d'erreur suivant
        si l'URL contient un espace :

            InvalidURL = URL can't contain control characters. '/my Check-Lists.py' (found at least ' ')

        :return: une URL valide.
        """

        valid_url = url

        if ' ' in url:

            valid_url = valid_url.replace(
                ' ',
                '%20'
                )

        return valid_url


    def send_request_http(
        self,
        url: str,
        coding: str = coding_unknown
        ) -> (str, str):
        """ Pour envoyer une requête HTTP et en recevoir le résultat.

        :param url: la requête à lancer.

        :param coding: l'encodage attendu de la réponse.

        :return: la réponse + le format de cette réponse.
        Ce format correspondra au format souhaité, sauf si nous avons
        eu à le modifier. Ce qui sera par exemple le cas si celui qui
        nous a été transmis était « coding_unknown ».
        """

        log = self.logItem
        url_string = ''

        url_valid = self.url_to_valid(url)
        self.shw(f'URL get = {url}')
        self.shw(f'URL ok  = {url_valid}')
        self.shw('')

        try:

            # Pour économiser les ressources, on utilise WITH... ie
            # l'objet réponse sera libéré dès la sortie du bloc.
            #
            # « Using the context manager with, you make a request and
            # receive a response with urlopen(). Then you read the body
            # of the response and close the response object. »
            #
            with urllib.request.urlopen(url_valid, timeout=3) as data:

                url_bytes = data.read()
                url_coding = data.headers.get_content_charset()

        except InvalidURL as error:
            self.shw(f'===>> InvalidURL = {error}')
            self.shw('')

        except NotConnected as error:
            self.shw(f'===>> NotConnected = {error}')
            self.shw('')

        except TimeoutError:
            self.shw('===>> Request timed out...')
            self.shw('')

        except HTTPError as error:
            self.shw(
                f'===>> HTTP {error.status} ERROR = {error.reason}'
                )
            self.shw('')

        except URLError as error:

            if isinstance(error.reason, timeout):
                self.shw('===>> Socket timeout error...')

            else:
                self.shw(f'===>> URLError = {error.reason}')

            self.shw('')

        else:

            log.debug('Début de « url_bytes » :')
            log.debug(url_bytes[0:99])
            log.debug('')

            self.shw(f'Coding en entrée = « {coding} »')

            if coding == coding_unknown:

                # headers.get_content_charset() sait lire les
                # fichiers au format HTML.
                #
                # Le "character encoding" n'est normalement pas
                # spécifié dans le fichier .py, pas en tout cas
                # à la façon d'un fichier HTML normal !!!
                #
                # Donc get_content_charset() ne devrait pas le
                # lire correctement si c'est un fichier script
                # Python, bash ou autres.
                #
                # Dans le cas où get_content_charset() ne peut
                # donner de réponse, il renverra « None ».
                #
                coding = url_coding

            self.shw(f'Coding calculé = « {coding} »')
            self.shw('')

            if coding is None:

                # Aucun décodage à faire car le jeu de caractères
                # qui nous concerne est celui des « byte strings ».
                #
                url_string = url_bytes

            else:
                url_string = url_bytes.decode(coding)

            log.debug('Début de « url_string » :')
            log.debug(url_string[0:99])
            log.debug('')

        return (url_string, coding)


# ---------------------------------------------------------------------------
#
#   Programme PRINCIPAL de ce module s'il est lancé en mode autonome...
#
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    skull = ScriptSkeleton(
        arguments = sys.argv,
        debug_mode = True
        )

    log = skull.logItem


    # Les fichiers d'auto-test auront
    # un nom qui débute par :
    #
    it_begins_with = '#_TESTS_( skeleton )'


    # On affiche un peu de bla-bla.
    #
    log.info('')
    log.info('AUTOTESTS de : %s', __file__)
    log.info('==============')
    log.info('')
    log.info('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise mes AUTOTESTS de SAISIE ?",
        'non'
        )

    if user_answer:

        # On appelle choose_in_a_list() pour vérifier
        # que Python ne plante pas en le parcourant.
        #
        log.info('')
        log.info('\t==================================')
        log.info('\t>>> TEST de choose_in_a_list() <<<')
        log.info('\t==================================')
        log.info('')
        log.info('')

        fruits = ['apple', 'banana', 'cherry']
        idx = skull.choose_in_a_list(fruits, 1)

        if idx >= 0:
            skull.shw(f'Votre réponse = {fruits[idx]}')

        skull.shw('')

        # On appelle choose_in_a_dict() pour vérifier
        # que Python ne plante pas en le parcourant.
        #
        log.info('')
        log.info('\t==================================')
        log.info('\t>>> TEST de choose_in_a_dict() <<<')
        log.info('\t==================================')
        log.info('')
        log.info('')

        capitals = {
            "USA":"Washington D.C.",
            "France":"Paris",
            "India":"New Delhi"
            }
        key = skull.choose_in_a_dict(capitals, 'India')

        if key is not None:
            skull.shw(f'Votre réponse = {capitals[key]}')

        skull.shw('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise mes AUTOTESTS de RECHERCHE de fichiers & ÉDITION format texte ?",
        'non'
        )

    if user_answer:

        # On appelle search_files_from_a_mask() pour vérifier
        # que Python ne plante pas en le parcourant.
        #
        log.info('')
        log.info('\t==========================================')
        log.info('\t>>> TEST de search_files_from_a_mask() <<<')
        log.info('\t==========================================')
        log.info('')
        log.info('')

        files_found = skull.search_files_from_a_mask(
            mask = '*.py'
            )

        log.debug('')

        skull.shw('Fichier(s) trouvé(s) [ *.py ] :')
        skull.shw('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        for file_name in sorted(files_found):
            skull.shw('\t' + file_name)

        skull.shw('')

        user_answer = skull.ask_yes_or_no(
            "Éditons-nous ces fichiers ( via notre éditeur de TXT ) ?",
            'oui'
            )

        if user_answer:

            log.info('')
            log.info('\t===============================')
            log.info('\t>>> TEST de edit_file_txt() <<<')
            log.info('\t===============================')
            log.info('')
            log.info('')

            skull.edit_file_txt(
                *files_found,
                wait = False
                )


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise mes AUTOTESTS de PDF ?",
        'non'
        )

    if user_answer:

        # On appelle les fonctions convert_to_pdf_*() pour
        # vérifier que Python ne plante pas en leur sein.
        #
        log.info('')
        log.info('\t==================================')
        log.info('\t>>> TEST de convert_to_pdf_*() <<<')
        log.info('\t==================================')
        log.info('')
        log.info('')

        if skull.convert_to_pdf_init():

            f_name = '{} - {}.txt'.format(
                it_begins_with,
                skull.build_now_string()
                )

            with open(f_name, "wt") as f_test:

                f_test.write(
                    '#\n'
                    '# =================\n'
                    "# FICHIER DE TEST :\n"
                    '# =================\n'
                    '#\n'
                    '# Bonjour, je suis un fichier totalement inutile.\n'
                    "# J'ai vocation à être détruit après ma création.\n"
                    '#\n'
                    '\n'
                    'Lorem ipsum (également appelé faux-texte, lipsum, ou bolo bolo)\n'
                    'https://fr.wikipedia.org/wiki/Lorem_ipsum\n'
                    '\n'
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus.\n"
                    "Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies\n"
                    "sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a,\n"
                    "semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie,\n"
                    "enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper.\n"
                    "Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque\n"
                    "congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum\n"
                    "augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque\n"
                    "sed dui ut augue blandit sodales. Vestibulum ante ipsum primis in faucibus orci\n"
                    "luctus et ultrices posuere cubilia Curae; Aliquam nibh. Mauris ac mauris sed\n"
                    "pede pellentesque fermentum. Maecenas adipiscing ante non diam sodales hendrerit.\n"
                    '\n'
                    "Ut velit mauris, egestas sed, gravida nec, ornare ut, mi. Aenean ut orci vel\n"
                    "massa suscipit pulvinar. Nulla sollicitudin. Fusce varius, ligula non tempus\n"
                    "aliquam, nunc turpis ullamcorper nibh, in tempus sapien eros vitae ligula.\n"
                    "Pellentesque rhoncus nunc et augue. Integer id felis. Curabitur aliquet\n"
                    "pellentesque diam. Integer quis metus vitae elit lobortis egestas.\n"
                    '\n'
                    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Morbi vel erat non\n"
                    "mauris convallis vehicula. Nulla et sapien. Integer tortor tellus, aliquam\n"
                    "faucibus, convallis id, congue eu, quam. Mauris ullamcorper felis vitae erat.\n"
                    "Proin feugiat, augue non elementum posuere, metus purus iaculis lectus, et\n"
                    "tristique ligula justo vitae magna.\n"
                    '\n'
                    "Aliquam convallis sollicitudin purus. Praesent aliquam, enim at fermentum\n"
                    "mollis, ligula massa adipiscing nisl, ac euismod nibh nisl eu lectus. Fusce\n"
                    "vulputate sem at sapien. Vivamus leo. Aliquam euismod libero eu enim. Nulla\n"
                    "nec felis sed leo placerat imperdiet. Aenean suscipit nulla in justo. Suspendisse\n"
                    "cursus rutrum augue. Nulla tincidunt tincidunt mi. Curabitur iaculis, lorem vel\n"
                    "rhoncus faucibus, felis magna fermentum augue, et ultricies lacus lorem varius\n"
                    "purus. Curabitur eu amet.\n"
                    '\n')

            # ATTENTION = On réalise dorénavant :
            #
            #       une exécution SYNCHRONE ( wait = True ) !!!
            #
            # ... En effet, si l'exécution est asynchrone, Libre Office ne
            # va en général convertir qu'un seul des 2 fichiers ( soit le
            # fichier temporaire f_name, soit __file__ ). Et on ne peut pas
            # savoir lequel des 2 aura sa préférence...
            #
            # Il semble que cela soit dû au fait que Libre Office reçoit
            # trop rapidement & trop consécutivement les deux demandes de
            # conversion et que, dans la « précipitation », il perde ses
            # billes, en oublie un ( le 1er ou le 2ème, il n'y a pas de
            # règle à ce sujet ) : Libre Office ne convertit que l'autre.
            #
            skull.convert_to_pdf_run(f_name, __file__, wait = True)

            skull.shw(f'Fichier converti : {f_name}')
            skull.shw(f'Fichier converti : {__file__}')

        else:
            skull.shw('Conversion PDF impossible sur ce terminal.')

        skull.shw('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise mes AUTOTESTS de COMPARAISON de FICHIERS ?",
        'non'
        )
    
    if user_answer:

        # On appelle & teste la fonction compare_files().
        #
        log.info('')
        log.info('\t=======================================')
        log.info('\t>>> TEST de COMPARAISON de FICHIERS <<<')
        log.info('\t=======================================')
        log.info('')
        log.info('')

        reference = (
            "Ve 29 feb AF 134 CDG (1,0) BOM    09h30 18h00 77W TVSV :  8h30 \n"
            "\n"
            "\tEquipage PNC\n"
            "DEI CAS  LAURENT  36017312     B  EN SUPPLEM  P  IMPOS COMM.   UEKR  AMERIQUES  2EJ  \n"
            "######### FIN #########"
            )

        transformation = (
            "Ve 29 feb AF 134 CDG (1,0) BOM    09h30 18h00 77W TVSV :  8h30 \n"
            "\n"
            "\tEquipage PNC\n"
            "DEI CAS LAURENT                   36017312                      B EN SUPPLEM P IMPOS COMM.     UEKR AMERIQUES        2EJ\n"
            "\n"
            "\tEquipage PNC\n"
            "DEI CAS LAURENT                   36017312   A350 359       C/C                                KDKR CAR/OCEAN INDIEN 3DD\n"
            "######### FIN #########"
            )


        # On créé & on log le fichier de référence.
        #
        f_reference = '{} - ( 1 ) contenu de référence - {}.txt'.format(
            it_begins_with,
            skull.build_now_string()
            )

        with open(f_reference, "wt") as new_file:
            new_file.write(reference)

        log.debug('')
        log.debug('Fichier de référence :')
        log.debug('~~~~~~~~~~~~~~~~~~~~~~')
        log.debug('«')
        log.debug('%s', reference)
        log.debug('»')
        log.debug('')

        with open(f_reference, "rt") as new_file:
            log.debug('')
            log.debug('Fichier de référence tel que converti en ENSEMBLE :')
            log.debug('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            log.debug('«')
            for elt in set(new_file):
                log.debug('%s', str(elt).rstrip('\r\n'))
            log.debug('»')
            log.debug('')


        # On créé & on log le fichier à comparer.
        #
        f_transformation = '{} - ( 2 ) contenu transformé - {}.txt'.format(
            it_begins_with,
            skull.build_now_string()
            )

        with open(f_transformation, "wt") as new_file:
            new_file.write(transformation)

        log.debug('')
        log.debug('Fichier transformé :')
        log.debug('~~~~~~~~~~~~~~~~~~~~')
        log.debug('«')
        log.debug('%s', transformation)
        log.debug('»')
        log.debug('')

        with open(f_transformation, "rt") as new_file:
            log.debug('')
            log.debug('Fichier transformé tel que converti en ENSEMBLE :')
            log.debug('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            log.debug('«')
            for elt in set(new_file):
                log.debug('%s', str(elt).rstrip('\r\n'))
            log.debug('»')
            log.debug('')


        # On compare les 2 fichiers : INTERSECTION.
        #
        skull.shw('')
        skull.shw("RÉSULTAT de l'INTERSECTION des deux FICHIERS :")
        skull.shw('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        skull.shw('«')
 
        intersection = skull.compare_files(
            f_reference,
            f_transformation,
            action = 'intersection'
            )

        for elt in intersection:
            skull.shw(str(elt).rstrip('\r\n'))
        skull.shw('»')
        skull.shw('')


        # On compare les 2 fichiers : DIFFÉRENCE / au fichier référence.
        #
        skull.shw('')
        skull.shw('LIGNES de la RÉFÉRENCE NON PRÉSENTES dans le fichier transformé :')
        skull.shw('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        skull.shw('«')

        difference = skull.compare_files(
            f_reference,
            f_transformation,
            action = 'difference'
            )

        for elt in difference:
            skull.shw(str(elt).rstrip('\r\n'))
        skull.shw('»')
        skull.shw('')


        # On compare les 2 fichiers : DIFFÉRENCE / au 2ème fichier.
        #
        # C-a-d que l'on va ici donner les lignes en plus dans le
        # 2ème fichier...
        #
        skull.shw('')
        skull.shw('LIGNES AJOUTÉES / MODIFIÉES dans le FICHIER TRANSFORMÉ :')
        skull.shw('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        skull.shw('«')
 
        ajouts = skull.compare_files(
            f_transformation,
            f_reference,
            action = 'difference'
            )

        for elt in ajouts:
            skull.shw(str(elt).rstrip('\r\n'))
        skull.shw('»')
        skull.shw('')


        # On compare les 2 fichiers : DIFFÉRENCE SYMÉTRIQUE.
        #
        skull.shw('')
        skull.shw('RÉSULTAT de la DIFFÉRENCE SYMÉTRIQUE entre les deux FICHIERS :')
        skull.shw('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        skull.shw('«')
 
        intersection = skull.compare_files(
            f_reference,
            f_transformation,
            action = 'difference symétrique'
            )

        for elt in intersection:
            skull.shw(str(elt).rstrip('\r\n'))
        skull.shw('»')
        skull.shw('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise les AUTOTESTS de get_unused_filename() ?",
        'non'
        )

    if user_answer:

        # On appelle les fonctions convert_to_pdf_*() pour
        # vérifier que Python ne plante pas en leur sein.
        #
        log.info('')
        log.info('\t=====================================')
        log.info('\t>>> TEST de get_unused_filename() <<<')
        log.info('\t=====================================')
        log.info('')
        log.info('')

        f_name = f'{it_begins_with}.tmp'

        skull.shw(f'Nom de référence = « {f_name} »')
        skull.shw('')

        f_tmp = skull.get_unused_filename(
            f_name,
            idx_force = False
            )

        skull.shw(f'Prochain nom disponible = « {f_tmp} »')
        skull.shw('')

        skull.shw(f'Création de « {f_tmp} »')
        skull.shw('')

        with open(f_tmp, "wt") as f_test:
            f_test.write('Dummy')

        skull.shw(f'Prochain nom après « {f_tmp} » ...')
        skull.shw('')

        skull.shw(
            '\t* sur 3 chiffres, base 0 : « {} »'.format(
                skull.get_unused_filename(f_name)
                )
            )
        skull.shw('')

        skull.shw(
            '\t* sur 18 chiffres, base 33 : « {} »'.format(
                skull.get_unused_filename(f_name, 18, 33)
                )
            )
        skull.shw('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise mes AUTOTESTS de SHUTDOWN ?",
        'non'
        )

    if user_answer:

        # On appelle shutdown_please() pour vérifier
        # que Python ne plante pas en le parcourant.
        #
        log.info('')
        log.info('\t=================================')
        log.info('\t>>> TEST de shutdown_please() <<<')
        log.info('\t=================================')
        log.info('')
        log.info('')

        skull.shw('SHUTDOWN « par défaut » ( rien )')
        skull.shw('')

        skull.shutdown_please()

        skull.shw('')
        skull.shw('SHUTDOWN « complet »')
        skull.shw('')

        skull.shutdown_please(shutdown_complete)

        skull.shw('')
        skull.shw('SHUTDOWN « hibernation »')
        skull.shw('')

        skull.shutdown_please(shutdown_hibernate)

        skull.shw('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = (os.name.upper() == 'NT')

    if user_answer:

        print(
            "\nATTENTION : Le test suivant demande à ce que :",
            "\t- mplay32.exe soit dans le répertoire de travail,",
            "\t- ainsi que « Windows XP Battery Low.wav ».",
            sep = '\n\n',
            end = '\n\n'
            )

        user_answer = skull.ask_yes_or_no(
            "Voulez-vous que je teste le réveil via mplay32.exe ?",
            'non'
            )

    if user_answer:

        # On sauvegarde les vraies valeurs.
        #
        real_exe = skull.paths_and_miscellaneous['EXE_player']
        real_arg = skull.paths_and_miscellaneous['ARG_player']
        real_played = skull.paths_and_miscellaneous['EXE_played']

        # On affecte des valeurs permettant le test.
        #
        working_path = skull.paths_and_miscellaneous['working_PATH_FULL']

        player_exe = os.path.join(working_path, 'mplay32.exe')
        player_arg = ['/play', '/close']
        played = os.path.join(working_path, 'Windows XP Battery Low.wav')

        skull.paths_and_miscellaneous['EXE_player'] = player_exe
        skull.paths_and_miscellaneous['ARG_player'] = player_arg
        skull.paths_and_miscellaneous['EXE_played'] = played

        # On teste l'émission via mplay32.exe d'un son de réveil.
        #
        if os.path.isfile(player_exe) and os.path.isfile(played):

            skull.on_sonne_le_reveil()

            # On marque une pause le temps que l'utilisateur puisse entendre
            # le son ( et donc que mplay32.exe puisse le jouer... ).
            #
            input('Frapper <Entrée> une fois le son entendu...')

        else:
            skull.shw('Certains fichiers demandés sont ABSENTS !!!')
            skull.shw('')

        # On restaure les vraies valeurs.
        #
        skull.paths_and_miscellaneous['EXE_player'] = real_exe
        skull.paths_and_miscellaneous['ARG_player'] = real_arg
        skull.paths_and_miscellaneous['EXE_played'] = real_played


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    # On teste l'émission « normale » ( par défaut ) d'un son de réveil.
    #
    skull.on_sonne_le_reveil()

    log.info('')
    log.info('Le problème est que je ne sais rien faire tout seul...')
    log.info('')
    log.info('... excepté des AUTOTESTS')
    log.info('')
    log.info('... alors AU REVOIR !!!')
    log.info('')
    log.info('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "En sortant, voulez-vous dire AU REVOIR ?",
        'non'
        )

    if user_answer:

        # On appelle shutdown_please() pour vérifier
        # que Python ne plante pas en le parcourant.
        #
        log.info('')
        log.info('\t==================================')
        log.info('\t>>> TEST de on_dit_au_revoir() <<<')
        log.info('\t==================================')
        log.info('')
        log.info('')

        skull.shw('Nous invoquons donc on_dit_au_revoir().')
        skull.shw('')

        skull.on_dit_au_revoir()

    else:

        # On quitte l'application...
        #
        # Et l'appel au Garbage Collector par Python
        # va appeler la méthode __del() de skull.
        #
        # Elle-même appellera on_dit_au_revoir()
        #
        skull.shw('On laisse donc le script le faire tout seul.')
        skull.shw('')
