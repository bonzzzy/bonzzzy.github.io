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

import json

import time
import datetime

from string import whitespace

import tempfile
import subprocess

import logging
import logging.handlers

import socket
import http.client
import http.server
import urllib.request
import urllib.error


if ___debug___:

    # L'utilisation de traceback.print_exc(), traceback.format_exc(), ... est
    # généralement utile pour le débogage et le développement, mais ne devrait
    # pas être utilisée dans du code de production pour des raisons de sécurité.
    #
    import traceback


# Les modules suivants ne sont pas importés par défaut, ils ne le seront que
# sur demande expresse de l'utilisateur de ce script...
#
# Toutefois, on déclare des variables globales les concernant afin que, s'ils
# sont importés ( dans la classe FileSystemTree ), ils puissent être visibles
# dans tout le reste de ce script !!!
#
pathlib = None
fnmatch = None
glob = None

# Pour ce qui est du module PATHLIB, faudra-t-il l'importer pour l'utiliser ?
# Si oui, devra-t-il être utilisé directement ( via des objets pathlib.PATH )
# ou devra-t-on l'encapsuler dans un objet _FileSystemLeaf ?
#
# ATTENTION : Si le module PATHLIB est importé, certaines fonctions de notre
# script renverront des valeurs de type PATHLIB.PATH en tant que paths, sinon
# ces valeurs seront de type STRING !!!
#
# Il font donc être prêt à gérer ces 2 types de valeurs lorsque nous traitons
# des paths ( d'autant plus dans le cas du mode « pathlib_direct » ), SAUF si
# nous ne demandons jamais à ce que la librairie PATHLIB soit utilisée.
#
pathlib_ignore = None
pathlib_direct = 'pathlib_direct'
pathlib_deeply = 'pathlib_embedded'

# Quel comportement vis-à-vis du module PATHLIB notre ScriptSkeleton va-t-il
# utiliser par défaut ?
#
___dflt_pathlib___ = pathlib_ignore
#___dflt_pathlib___ = pathlib_deeply
#___dflt_pathlib___ = pathlib_direct

# Si nous parcourons un répertoire en utilisant le module OS.PATH, le ferons
# -nous via la la fonction os.listdir() ou via os.scandir() ?
#
walking_ignore = None
walking_via_listdir = 'os.listdir'
walking_via_scandir = 'os.scandir'


# ===========================================================================
#
#   SKELETON.PY = SQUELETTE réutilisable pour débuter rapidement le codage
#   ~~~~~~~~~~~~~                                d'une  application PYTHON.
#
# Les différentes PARTIES sont :
#
#   - CONSTANTES et fonctions générales ( _show_(), etc )
#
#   - Définition et fonctions des classes FileSystemTree + _FileSystemLeaf
#
#   - Définition de la classe ScriptSkeleton ( __init__() et __del__() )
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
#                       . def search_path_from_masks
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
#   ( in autotests )    . def build_now_string
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
#   ( in autotests )    . def file_system_mode
#   ( in autotests )    . def search_files_from_a_mask
#   ( in autotests )    . def convert_to_pdf_init
#   ( in autotests )    . def convert_to_pdf_run
#   ( in autotests )    . def edit_file_txt
#   ( in autotests )    . def compare_files
#   ( in autotests )    . def get_unused_filename
#   ( in autotests )    . def save_strings_to_file
#
# ===========================================================================
#
#   - Fonctions spécifiques au WEB ( browser, HTML, HTTP, etc ) :
#
#                       . def url_to_valid
#   ( in autotests )    . def send_request_http
#
# ===========================================================================


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   CONSTANTES et fonctions générales ( _show_(), etc ).
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
    # [ ENGLISH ]
    'eng'   : {
        'y'     : True,
        'yes'   : True,
        'ok'    : True,
        'n'     : False,
        'no'    : False,
        'nope'  : False,
        },
    # [ FRENCH ]
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
# ATTENTION : Il est possible d'affecter « coding_bytes »
# à toutes les valeurs puisque :
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
coding_bytes = 'bytes'      # Codage sous forme octale
coding_default = 'UTF-8'
coding_unknown = '?'

filetype_to_coding = {
    '.bat': 'ASCII',
    '.py': 'UTF-8',
    '.sh': coding_bytes
}


# Fonction d'affichage.
#
def _show_(msg, journal = None):
    """ Pour afficher un msg, tout en le journalisant en
    même temps.
    """

    msg_to_print = '' if msg is None else str(msg)

    print(msg_to_print)

    if journal is not None:
        journal.debug(msg_to_print)


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Définition et fonctions des classes FileSystemTree + _FileSystemLeaf.
#
# ---------------------------------------------------------------------------


# Si nous demandons une recherche de path via wildcards
# ( i-e 1 recherche GLOB de style Unix ) via la méthode
# < FileStyleLeaf >._fake_iglob(), alors nous pouvons
# préciser si nous désirons que nous soient retournés :
#
#   . tous les fichiers et répertoires correspondant au
#   masque fourni.
#
#   . seulement les répertoires.
#
#   . seulement les fichiers.
#
_glob_all_nodes = 0
_glob_only_dirs = 1
_glob_only_files = 2


# Si nous demandons une recherche de path via wildcards
# ( i-e 1 recherche GLOB de style Unix ) via la méthode
# < FileStyleLeaf >._fake_iglob(), alors nous pouvons
# préciser si nous souhaitons forcer une utilisation du
# module FNMATCH. Pour cela, nous utiliserons la valeur
# _search_fnmatch lors du lancement des traitements via 
# la méthode < FileStyleLeaf >._parse_mask() :
#
#   _fake_iglob( n_type, **_parse_mask( mask, _search_fnmatch ) )
#
# Les autres valeurs ( _search_simple, _search_complex,
# ... ) ne sont qu'à usage interne.
#
_search_fnmatch = 0
_search_complex = 1
_search_simple = 2

_searches_lst = (
    _search_simple,
    _search_complex,
    _search_fnmatch
)


# Itérateur / GÉNÉRATEUR vide.
#
# Il s'agit du générateur qui sera renvoyé par la méthode
# Glob() de la classe FileSystemTree._FileSystemLeaf dans
# certains où son résultat serait vide.
#
def _generator_empty():
    # -> None
    """ Pour 1 explication sur la forme de ce générateur,
    voir le post suivant :

        https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/

    ... dont surtout :

        https://stackoverflow.com/a/13243870/3840170
        -> analyse des différents « empty generator »
        possibles.
        
        https://stackoverflow.com/a/61496399/577088
        -> analyse du meilleur « empty generator » sous
        l'angle du code CPython généré.

    Tous ces posts se retrouvent dans :

        - GÉNÉRATEURS - How to define an EMPTY GENERATOR function *
        in - et - ITÉRATEUR ou GÉNÉRATEUR.rar
        in _Know\Info\Dvpt\Réalisation\Langages\Python

    Dans ce script, nous aurions toutefois pu opter pour
    renvoyer une liste vide, ou plutôt 1 itérateur vide :

        iter(())

    mais ce _generator_empty() a été choisi pour raison
    didactique...

    Nous aurions également pu choisir la forme suivante
    ( peut-être plus compréhensible ) :

        def _generator_empty():
            yield from ()
    """
    return
    yield


# Création paramétrée d'un GÉNÉRATEUR.
#
def _generator_create(
    iterable = list(),          # iterable, iterator, generator
    yield_fct = os.path.abspath # function
    ):
    # -> Return = « Type( yield_fct() ) »
    """ Nous créons ici 1 générateur via 2 paramètres :

    :param iterable: l'itérable, l'itérateur, ou le générateur
    qui sera utilisé pour fournir une suite de valeurs. Nous
    subodorons que la suite de valeurs fournies sera de type
    noeud d'un système de fichiers ( ie des répertoires et /
    ou des fichiers ).

    :param yield_fct: la fonction qui sera appliquée à chaque
    valeur, avant qu'elle ne soit retournée à l'appelant.
    """
    for node in iterable:

        #if str(node) in {'.', '..'}: continue
        #
        # Yielding a path object for these makes
        # little sense [ '.', '..' ne sont pas ici
        # parcourus ].
        #
        # Mais l'instruction ci-dessus ( relative
        # à « {'.', '..'} » ) ne marche pas dans
        # tous les cas, nous l'avons donc mise en
        # commentaire.
        #
        # En effet, il faut que « str(node) » donne
        # le nom du noeud. Ce qui n'est pas le cas
        # si « node » est de type os.DirEntry. Il
        # faudrait dans ce cas écrire « node.name ».
        #
        # Cela ne fonctionne pas non plus si nous
        # est transmise une information sous forme
        # de path ABSOLU...
        #
        # Il faudrait donc ajouter un paramètre à
        # ce générateur de GENERATOR, et ce afin
        # de pouvoir lire le nom seul du noeud,
        # sans son chemin !!!
        #
        # De toute façon, cette situation ne devrait
        # pas se présenter car « os.listdir [..] does
        # not include the special entries '.' and '..'
        # even if they are present ».
        #
        # Cf https://docs.python.org/3/library/os.html#os.listdir
        #
        # Pas plus que os.scandir() ou la méthode
        # pathlib.Path.iterdir(), d'ailleurs.
        #
        # Cf https://docs.python.org/3/library/os.html#os.scandir
        # Cf https://docs.python.org/3/library/pathlib.html#pathlib.Path.iterdir

        yield yield_fct(node)


class FileSystemTree:
    """ Cette classe permet de gérer répertoires et fichiers.
    Pour ceci, suivant sa configuration, elle s'appuie soit
    sur la librairie OS.PATH, soit sur le module PATHLIB.

    Elle peut également utiliser les modules FNMATCH ou GLOB,
    pour des fonctions annexes.

    Ces différentes possibilités permettent de s'adapter aux
    versions de Python et aux différents OS.

    Pour des tests sur ce sujet :

        Cf * - TESTS --- ( import + PATHLIB + GLOB + fnmatch ) ---.py
        in --- [ skeleton ] = 2Do & NOTES.rar\( TESTS ) dont « mplay32.exe »
        in _Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]

        ou

        Cf --- FILES and PATH --- ( mes ) NOTES = os.path, PATHLIB, fnmatch, GLOB*.py
        in _Know\Info\Dvpt\Réalisation\Langages\Python\- et - FICHIERS.rar

    REMARQUE : L'importation du module OS est toujours demandée
    par skeleton.py. Pour les autres, cela dépend du bon vouloir
    des utilisateurs de ce script.

    REMARQUE : Par CONVENTION, les méthodes de FileSystemTree et
    celles de sa « inner class » _FileSystemLeaf, sont IDENTIQUES
    ( i.e ont le même nom, la même définition ) que les méthodes
    présentes dans le module PATHLIB.

        Cf https://docs.python.org/3/library/pathlib.html#correspondence-to-tools-in-the-os-module

    ATTENTION : Si le module PATHLIB est importé, certaines des
    méthodes de cet objet renverront en guise de paths ( chemin
    de fichiers ) des valeurs type PATHLIB.PATH, sinon ces mêmes
    valeurs seront de type STRING !!!

        Il font donc être prêt à gérer ces deux types de valeurs
        lorsque nous traitons des path ( d'autant plus si notre
        mode est « pathlib_direct » ), SAUF si nous ne demandons
        pas à ce que la librairie PATHLIB soit utilisée.

    ATTENTION : Si l'import direct de PATHLIB est demandé ( mode
    « pathlib_direct » ), toute fonction fournie par PATHLIB sera
    accessible, même si non déclarées / surchargées dans la classe
    incluse _FileSystemLeaf !!!

        En effet, si l'on travaille de façon directe avec le module
        PATHLIB, alors FileSystemTree.node() renvoie directement un
        objet PATHLIB et cela va shunter la classe _FileSystemLeaf &
        ses méthodes. L'objet pathlib.Path sera en effet directement
        appelé !!!

        Toutes les fonctions PATHLIB sont alors disponibles, en tout
        cas pour celles au niveau d'une instance ( ie du même niveau
        que nos objets _FileSystemLeaf ). Pour les méthodes de classe
        ( telles cwd(), home(), ... ), elles doivent être codées au
        niveau de notre classe FileSystemTree.
    """

    def __init__(
        self,
        walking_mode: str = walking_via_listdir,
        with_pathlib: str = pathlib_ignore,
        with_fnmatch: bool = False,
        with_glob: bool = False,
        log: logging.Logger = None
        ):
        """
        :param walking_mode: si cet objet n'utilise que le module
        OS.PATH, pour parcourir 1 répertoire utilisera-t-il la fct
        os.listdir() ou os.scandir() ?

            * walking_via_listdir : os.listdir() utilisée.

            * walking_via_scandir : os.scandir() utilisée.

            * walking_ignore : peu importe ( cas où module PATHLIB
            est utilisé pour gérer les fichiers... ) et, si nous
            arrivons tout de même dans une partie de code utilisant
            cette informat°, la méthode par défaut ( ie os.listdir()
            sera utilisée ).

            RQ = Cf FileSystemTree._FileSystemLeaf.iterdir()

            RQ = Si les modules GLOB ou FNMATCH sont importés, cela
            n'impose pas le walking_mode et il faut le spécifier !

        :param with_pathlib: cet objet va-t-il utiliser PATHLIB ou
        simplement se servir de la librairie OS.PATH ? Les valeurs
        autorisées pour « with_pathlib » sont :

            * pathlib_ignore ( None ) : nous n'utiliserons pas le
            module PATHLIB.

            * pathlib_direct : nous utiliserons le module PATHLIB &
            notre méthode FileSystemTree.node() renverra directement
            des objets de type pathlib.Path, sans filtre.

            * pathlib_deeply : nous utiliserons le module PATHLIB &
            notre méthode FileSystemTree.node() renverra des objets
            de type _FileSystemLeaf ( qui inqueront eux-même 1 objet
            pathlib.Path interne ).

        :param with_fnmatch: cet objet peut-il utiliser FNMATCH ?

        :param with_glob: cet objet peut-t-il utiliser GLOB ?

        :param log: identifiant d'un fichier de journalisation des
        messages, s'il en existe un.
        """

        self.write_in_log = None
        self.register_log(log)
        log_debug = self.write_in_log

        # On importe les modules PATHLIB, FNMATCH et GLOB si tel
        # doit être le cas.
        #
        log_debug("Configuration de la GESTION des FICHIERS :")
        log_debug('==========================================')

        self.walking_mode = walking_mode

        log_debug('\tWALKING MODE\t= ' + str(walking_mode))

        self.with_pathlib = with_pathlib
        self.pathlib_import = not (with_pathlib == pathlib_ignore)
        self.pathlib_direct = (with_pathlib == pathlib_direct)
        if self.pathlib_import:

            global pathlib
            try: pathlib.PurePath()
            except AttributeError: import pathlib

        log_debug('\tPATHLIB\t\t= ' + str(pathlib))

        self.with_fnmatch = with_fnmatch
        if with_fnmatch:

            global fnmatch
            try: fnmatch.translate('test_if*already_imported')
            except AttributeError: import fnmatch

        log_debug('\tFNMATCH\t\t= ' + str(fnmatch))

        self.with_glob = with_glob
        if with_glob:

            global glob
            try: glob.iglob('test_if*already_imported')
            except AttributeError: import glob

        log_debug('\tGLOB\t\t= ' + str(glob))
        log_debug('')
 

    def register_log(
        self,
        log: logging.Logger = None
        ):        
        """ Pour affecter un ( nouveau ) fichier JOURNAL
        à l'enregistrement de nos événements.
        """

        if log is None:
            log_debug = _show_
        else:
            log_debug = log.debug

        self.write_in_log = log_debug


    def cwd(self) -> os.PathLike:
        # -> _FileSystemLeaf [ ou ] PATHLIB.PATH
        """ Pour connaître le RÉPERTOIRE de TRAVAIL.

        RQ : Les méthodes de classe ( telles cwd() ou home() )
        doivent être codées au niveau de FileSystemTree, et ce
        quel que soit le module sous-jacent utilisé pour gérer
        les fichiers et répertoires ( OS.PATH, PATHLIB, ...).
        Rechercher « classmethod » dans :

            https://docs.python.org/fr/3/library/pathlib.html

        :return: le répertoire de travail, au format pathlib.Path
        ou _FileSystemLeaf...
        """

        if self.pathlib_import:
            return pathlib.Path.cwd()

        else:
            return self._FileSystemLeaf(self, os.getcwd())
  

    def home(self) -> os.PathLike:
        # -> _FileSystemLeaf [ ou ] PATHLIB.PATH
        """ Pour connaître le RÉPERTOIRE de l'UTILISATEUR.

        RQ : Les méthodes de classe ( telles cwd() ou home() )
        doivent être codées au niveau de FileSystemTree, et ce
        quel que soit le module sous-jacent utilisé pour gérer
        les fichiers et répertoires ( OS.PATH, PATHLIB, ...).
        Rechercher « classmethod » dans :

            https://docs.python.org/fr/3/library/pathlib.html

        :return: le « home directory », au format pathlib.Path
        ou _FileSystemLeaf...
        """

        if self.pathlib_import:
            return pathlib.Path.home()

        else:
            # RQ : Sous Windows, on ne peut pas invoquer le seul
            # os.environ['HOMEPATH'] car ce dernier renvoie qqch
            # comme '\\Users\\bonzz', au lieu de 'C:\\Users\\...'.
            # Il manque donc le disque dans la réponse, et il faut
            # également se référer à HOMEDRIVE.
            #
            #   Sous Unix, la / les variable(s) d'environnement
            # sont différentes...
            #
            #   Bref, autant utiliser expanduser('~') !!!
            #
            return self._FileSystemLeaf(self, os.path.expanduser('~'))


    def node(
        self,
        location = None     # _FileSystemLeaf [ ou ] os.PathLike
        ) -> object:
        # -> _FileSystemLeaf [ ou ] PATHLIB.PATH
        """ Pour créer un objet de GESTION d'un NOEUD du système
        de fichiers ( fichiers ou répertoires ), afin de pouvoir
        accéder à ce noeud et / ou le manipuler.

        Si nous sommes en mode « pathlib_direct », cette méthode
        renverra 1 objet de type « pathlib.Path » & notre classe
        interne _FileSystemLeaf ne sera donc pas utilisée pour la
        gestion du système de fichiers.

        Dans tous les autres cas, _FileSystemLeaf sera l'objet qui
        permettra d'accéder au noeud défini par « location ». Cet
        objet appelera les fonctions adéquates des modules OS.PATH
        ou PATHLIB.

        Cf https://docs.python.org/3/library/pathlib.html#correspondence-to-tools-in-the-os-module
       
        ATTENTION ( !!! ) : PRUDENCE LORSQUE L'ON STOCKE UNE VALEUR
        DU TYPE ScriptSkeleton.file_system_mode(). En effet, si l'
        on modifie par la suite le comportement interne de skeleton
        ( via notre méthode ScriptSkeleton.file_system_mode() ), on
        peut se retrouver avec des BUGS dus à des types qui ne sont
        PAS COMPATIBLES ( _FileSystemLeaf vs pathlib.Path ) !!!

            Cf « ( ! ) ATTENTION ( ! ) : Choix a été fait de stocker »

        :param location: la localisation du fichier ou répertoire
        à gérer. Cette donnée peut-être au format « os.PathLike »
        ( ie « string » ou « pathlib.Path » ) voire être du type
        « _FileSystemLeaf ». Dans ce dernier cas, notre fonction
        node() renverra l'objet « _FileSystemLeaf » lui-même !!!

        :param return: l'objet pour GESTION du répertoire ou du
        fichier sous-jacent.
        """

        # Si aucune localisation n'est indiquée, nous considérons
        # qu'il s'agit du répertoire courant.
        #        
        if location is None or str(location) == '':
            location = '.'

        # Si l'on travaille en direct avec le module PATHLIB, alors
        # on renvoie l'objet PATHLIB créé, ce qui va shunter notre
        # classe _FileSystemLeaf & ses méthodes. L'objet pathlib.Path
        # sera en effet directement appelé !!!
        #
        # Toutes les fonctions PATHLIB sont alors disponibles, en tout
        # cas pour celles au niveau d'une instance. Pour les méthodes
        # de classe ( cwd(), home(), ... ), elles doivent être codées
        # au niveau de notre classe FileSystemTree.
        #
        # => Rechercher « classmethod » dans :
        #
        #   https://docs.python.org/fr/3/library/pathlib.html
        #
        if self.pathlib_direct: 
            # Dans ce cas, « location » est obligatoirement du type
            # « os.PathLike », car les objets « _FileSystemLeaf »
            # sont shuntés et ne sont jamais créés.
            #
            # On peut donc donner directement « location » comme
            # information à pathlib.Path().
            #
            return pathlib.Path(location)

        # Si la localisation est déjà un objet _FileSystemLeaf,
        # alors il n'y a aucune transformation à faire !!!
        #
        elif isinstance(location, FileSystemTree._FileSystemLeaf):
            return location

        # Nous créons sinon un objet _FileSystemLeaf, dont la tâche
        # sera d'encapsuler le module OS.PATH ou le module PATHLIB.
        # La tâche de cet objet _FileSystemLeaf est d'offrir une API
        # ( interface ) similaire à celle de PATHLIB ( au moins pour
        # les méthodes implémentées dans _FileSystemLeaf : les autres
        # fonctions de PATHLIB ne seront pas disponibles tant que non
        # présentes parmi les méthodes de _FileSystemLeaf ).
        #
        else:
            return self._FileSystemLeaf(self, location)


    class _FileSystemLeaf:
        """ _FileSystemLeaf est une classe d'objets qui permettent
        d'accéder à un noeud ( fichier, répertoire ) du système de
        fichiers. Cet objet appelle la fonction adéquate du module
        sous-jacent ( OS.PATH ou PATHLIB ).

        ATTENTION : Lorsque nous sommes en mode « pathlib_direct »,
        cette classe n'est pas utilisée pour la gestion du système
        de fichiers. FileSystemTree ne manipulera que des objets du
        type « pathlib.Path ».

        REMARQUE : Par CONVENTION, les méthodes de _FileSystemLeaf
        sont IDENTIQUES ( i.e même nom, même définition ) à celles
        équivalents présentes dans PATHLIB. Nous avons choisi de
        coder la même API ( interface ).

            Cf https://docs.python.org/3/library/pathlib.html#correspondence-to-tools-in-the-os-module

        REMARQUE : J'aurais pu « désindenter » cette classe afin
        d'en faire une classe à part entière, non incluse, mais
        j'ai préféré garder cette construction car _FileSystemLeaf
        n'est utilisée qu'avec FileSystemTree...

        J'ai donc gardé ce système de « nested class », bien qu'il
        soit peu utilisé en Python, à part pour créer des itérateurs.

        Cf :

            https://stackoverflow.com/questions/30376127/is-it-a-good-practice-to-nest-classes
            ( Most Python developers do not nest classes, so when you do so you break convention and increase maintenance cost )

            http://www.xavierdupre.fr/app/teachpyx/helpsphinx/c_classes/classes.html#classe-incluse

        ATTENTION : Pour des restrictions dans la gestions des PATHS
        ABSOLUS et RELATIFS, cf l'entête de notre méthode resolve()
        où est expliqué l'une des restrictions de _FileSystemLeaf ie
        cf :
                « ATTENTION = Lorsqu'un path n'est pas absolu »

        Il y est ainsi suggéré une évolution de _FileSystemLeaf...
        """

        # La définition suivante :
        #
        #   def __init__(self, tree: FileSystemTree, location):
        #
        # ... provoque à l'exécution l'erreur :
        #
        #   File "K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\skeleton { SRC }.py", line 330, in _ileSystemLeaf
        #       def __init__(self, tree: FileSystemTree, location):
        #       NameError: name 'FileSystemTree' is not defined
        #
        # Il y a donc un problème de visibilité du nom de la classe
        # FileSystemTree dans sa classe incluse _FileSystemLeaf ( ie
        # « nested class » ou « inner class » ).
        #
        # Je n'ai pas trouvé la notation qui permettrait de spécifier
        # que le paramètre « tree » ci-dessous est une instance de la
        # classe FileSystemTree.
        #
        # J'ai donc adopté la définition ci-dessous, plus floue qui,
        # elle, fonctionne bien.
        #
        def __init__(
            self,
            tree: object,
            location: os.PathLike
            ):
            """
            :param tree: l'objet FileSystemTree dont nous dépendons.

            :param location: la localisation ( sous forme de STRING
            ou de pathlib.PATH ) de l'objet que nous représentons.
            Pour expliciter ce path, le mieux est de le fournir à la
            mode UNIX ( avec « / » comme séparateur ) plutôt qu'avec
            la façon Windows ( avec « \ » comme séparateur ), même si
            nous sommes sur un système Windows.

                En effet, Python dispose d'une fonction pour changer
                la notation UNIX en celle Windows ( os.path.normpath )
                mais pas pour l'inverse. Or nous travaillons aussi,
                entre autres, sur iPad + iOS, où « \ » ne sera pas
                compris comme séparateur de PATH...
            """

            self.tree = tree

            # Si nous parcourons un répertoire en utilisant OS.PATH
            # [ cf notre méthode iterdir() ], le ferons-nous via la
            # la fonction os.listdir() ou via os.scandir() ?
            #
            self.walking_mode = tree.walking_mode

            # Cf https://docs.python.org/3/library/os.html#os.fspath
            #
            # os.fspath(path)
            # Return the file system representation of the path.
            #
            # +
            #
            # Les PATH peuvent être écrits à la mode UNIX ( ie avec
            # « / » comme séparateur ) ou celle Windows ( avec « \ »
            # comme séparateur ).
            #
            # Cf ainsi :
            #
            #   https://docs.python.org/3/library/os.path.html#os.path.normpath
            #
            #   Normalize a pathname by collapsing redundant separators
            #   and up-level references so that A//B, A/B/, A/./B and
            #   A/foo/../B all become A/B. This string manipulation may
            #   change the meaning of a path that contains symbolic links.
            #
            #   ON WINDOWS, IT CONVERTS FORWARD SLASHES TO BACKWARD SLASHES.
            #
            #   To normalize case, use normcase().
            #
            # Bref, nous mettons ceinture & bretelles pour nous assurer
            # que le path indiqué soit bien compris !!!
            #
            location = os.path.normpath(os.fspath(location))

            # Quel que soit le type de « location » ( pathlib.Path,
            # str, ... ) l'affectation suivante fonctionnera.
            #
            self.location_string = str(location)

            if tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers.
                #
                # Nous créons ( ou enregistrons ) l'objet interne, de
                # type pathlib.Path, qui va nous permettre toutes ces
                # manipulations via des appels à ses méthodes.
                #
                if isinstance(location, str):
                    self.location_object = pathlib.Path(self.location_string)

                elif isinstance(location, pathlib.PurePath):
                    self.location_object = location

                else:
                    raise TypeError(
                        "Argument should be a str object or a Path"
                        " object, not {}".format(type(location))
                        )

            else:
                # Nous sommes ici dans le mode « pathlib_ignore »,
                # donc pas d'objet interne à créer ou enregistrer.
                #
                self.location_object = None


        def __str__(self) -> str:
            """ Return the string representation of the path, suitable
            for passing to system calls.
            """

            return self.location_string


        def __truediv__(
            self,
            #path: os.PathLike
            path: object     # _FileSystemLeaf [ ou ] os.PathLike
            ) -> object:
            # -> _FileSystemLeaf [ ou ] NotImplemented
            """ Tout comme dans PATHLIB, nous utilisons l'opérateur de
            division ( / ) pour concaténer des localisations ( path ).

            Ainsi :

                _FileSystemLeaf(« Z:\woah_wouh\ ») / str(« ESSAI_n°4 »)

                = _FileSystemLeaf(« Z:\woah_wouh\ESSAI_n°4 »)
            """

            try:
                p = path if isinstance(path, os.PathLike) else str(path)

            except TypeError:
                return NotImplemented

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return FileSystemTree._FileSystemLeaf(
                    self.tree,
                    self.location_object.__truediv__(p)
                    )

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                return FileSystemTree._FileSystemLeaf(
                    self.tree,
                    os.path.join(self.location_string, p)
                    )


        def __rtruediv__(
            self,
            #path: os.PathLike
            path: object     # _FileSystemLeaf [ ou ] os.PathLike
            ) -> object:
            # -> _FileSystemLeaf [ ou ] NotImplemented
            """ Tout comme dans PATHLIB, nous utilisons l'opérateur de
            division ( / ) pour concaténer des localisations ( path ).

            Ainsi :

                str(« Z:\woah_wouh\ ») / _FileSystemLeaf(« ESSAI_n°4 »)

                = _FileSystemLeaf(« Z:\woah_wouh\ESSAI_n°4 »)
            """

            try:
                p = path if isinstance(path, os.PathLike) else str(path)

            except TypeError:
                return NotImplemented

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return FileSystemTree._FileSystemLeaf(
                    self.tree,
                    self.location_object.__rtruediv__(p)
                    )

            elif isinstance(path, str):
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                return FileSystemTree._FileSystemLeaf(
                    self.tree,
                    os.path.join(p, self.location_string)
                    )


        def is_dir(self) -> bool:
            """ Sommes-nous un RÉPERTOIRE ?
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return self.location_object.is_dir()

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                return os.path.isdir(self.location_string)


        def is_file(self) -> bool:
            """ Sommes-nous un FICHIER ?
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return self.location_object.is_file()

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                return os.path.isfile(self.location_string)


        def exists(self) -> bool:
            """ Existons-nous PHYSIQUEMENT ?
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return self.location_object.exists()

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                return os.path.exists(self.location_string)


        @property
        def drive(self) -> str:
            """ Quel est notre DISQUE ?
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return self.location_object.drive

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                drive, _ = os.path.splitdrive(self.location_string)
                return drive


        @property
        def parent(self) -> object:
            # -> _FileSystemLeaf
            """ Quel est notre RÉPERTOIRE parent ?
            ( notre arborescence, sans notre nom ni, bien sûr, notre
            extension )

            ATTENTION : Tout comme le module PATHLIB, le retour de
            cette méthode est un objet de notre classe et donc son
            type sera _FileSystemLeaf ( voire pathlib.Path si nous
            sommes "shuntés" ).
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                path = self.location_object.parent

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                path = os.path.dirname(self.location_string)

            return FileSystemTree._FileSystemLeaf(self.tree, path)


        @property
        def name(self) -> str:
            """ Quel est notre NOM ?
            ( sans mention de l'arborescence mais extension incluse
            pour les fichiers )
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return self.location_object.name

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                return os.path.basename(self.location_string)


        @property
        def stem(self) -> str:
            """ Quel est notre NOM ?
            ( sans mention de l'arborescence ET extension exclue pour
            les fichiers )
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return self.location_object.stem

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                stem, _ = os.path.splitext(self.name)
                return stem


        @property
        def suffix(self) -> str:
            """ Quel est notre EXTENSION ?
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return self.location_object.suffix

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                _, extension = os.path.splitext(self.location_string)
                return extension


        def with_name(
            self,
            new_name: str
            ) -> object:
            # -> _FileSystemLeaf
            """ Pour créer un nouvel objet, conservant le même chemin
            mais avec un NOUVEAU NOM.
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return FileSystemTree._FileSystemLeaf(
                    self.tree,
                    self.location_object.with_name(new_name)
                    )

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                parent = os.path.dirname(self.location_string)
                baby = os.path.join(parent, new_name)

                return FileSystemTree._FileSystemLeaf(self.tree, baby)


        def with_suffix(
            self,
            new_suffix: str
            ) -> object:
            # -> _FileSystemLeaf
            """ Pour créer un nouvel objet, conservant le même chemin
            et le même « stem » mais avec un NOUVEAU SUFFIXE.
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                return FileSystemTree._FileSystemLeaf(
                    self.tree,
                    self.location_object.with_suffix(new_suffix)
                    )

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                base, _ = os.path.splitext(self.location_string)
                base += new_suffix

                return FileSystemTree._FileSystemLeaf(self.tree, base)


        #def resolve(self) -> _FileSystemLeaf:
        #def resolve(self) -> FileSystemTree._FileSystemLeaf:
        #
        # Les 2 définitions ci-dessus génèrent un plantage du script
        # dès sa lecture par Python ( sans même exécution... ) :
        #
        #   . NameError: name '_FileSystemLeaf' is not defined
        #   . NameError: name 'FileSystemTree' is not defined
        #
        # ... d'où la définition ci-dessous.
        #
        def resolve(self) -> object:
            """ Cette fonction émule la méthode pathlib.Path.resolve()
            et renvoie donc un objet qui contient un PATH ABSOLU :

            « Make the path absolute, resolving all symlinks on the way
            and also normalizing it (for example turning slashes into
            backslashes under Windows). »

            Nous avons choisi d'émuler cette méthode plutôt que l'autre
            méthode transformant un path relatif en path absolu ( c-a-d
            pathlib.Path.absolute() ) car nous voulions forcer la réponse
            sous la forme d'un path ABSOLU simple, normalisé.

            Or, pathlib.Path.absolute() fournit parfois des réponses du
            type :

                K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\..\all files to one PDF\skeleton.py

            Cf Python310\lib\pathlib.py :

                def absolute(self):
                [..] Return an absolute version of this path.  This function
                works even if the path doesn't point to anything.

                No normalization is done, i.e. all '.' and '..' will be kept
                along. Use resolve() to get the canonical path to a file.

            Avec la méthode resolve(), par contre :

                « “..” components are also eliminated (this is the only method to do so) »

                Cf https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve

            ... et le résultat ci-dessus serait normalisé en :

                K:\_Know\Info\Dvpt\Réalisation\Src\_Python\all files to one PDF\skeleton.py

            C'est donc elle que nous utilisons.

            :return: Un objet _FileSystemLeaf contenant un path absolu
            et normalisé.
            
            ATTENTION = Lorsqu'un path n'est pas absolu, la fonction
            os.path.abspath() renvoie un chemin ayant pour référence
            le répertoire courant. Si ce n'était pas le répertoire
            réel de référence de cet objet _FileSystemLeaf, le calcul
            du résultat sera alors FAUX !!!

            Cf https://docs.python.org/3/library/os.path.html#os.path.abspath

                « Return a normalized absolutized version of the pathname path.
                On most platforms, this is equivalent to calling the function
                normpath() as follows: normpath(join(os.getcwd(), path)). »

            DONC même si nous émulons la méthode pathlib.Path.resolve()
            nous travaillons plutôt comme la méthode pathlib.absolute() :

                Cf Python310\lib\pathlib.py

                def absolute(self):
                [..]
                    return self._from_parts([self._accessor.getcwd()] + self._parts)

            Pour faire mieux, il nous faudrait changer la structure de
            données de _FileSystemLeaf et scanner / conserver toutes les
            parties du chemin qu'elle représente ( tout comme cela est
            fait dans PATHLIB en fait !!! ).

            Il faudrait, si nous ne sommes PAS ABSOLUS, conserver notre
            PATH de RÉFÉRENCE ie quel était le chemin courant / de travail
            / référent ( explicite ou sous entendu ) quand nous avons été
            créé...

            Par exemple, si nous sommes issus d'un appel à une méthode type
            ITERDIR(), scandir() ou autres, il nous faudrait conserver le
            PATH ABSOLU du répertoire ainsi parcouru...
            """

            # Si nous possédons déjà un PATH ABSOLU, rien à faire...
            #
            if os.path.isabs(self.location_string):

                return self


            # XXX --- FIX ME ---
            #
            # Notre méthode resolve() souffre d'un PB de repère ( i-e
            # elle ne sait calculer les paths absolus que par rapport
            # au path courant ) tel que c'est expliqué ci-dessus dans
            # son cartouche.
            #
            # Actuellement, l'unique endroit où cette méthode .resolve()
            # est susceptible d'être appelée se situe dans notre méthode
            # _fake_iglob() à :
            #
            #   yield str(file_or_dir.resolve())
            #
            # ... mais, à cet endroit, nous sommes sûrs que l'objet en
            # question dispose déjà d'un path ABSOLU, donc pas de pb.
            # Ce cas est traité par le « return self » ci-dessus, nous
            # ne devrions donc, actuellement, JAMAIS ATTEINDRE le code
            # ci-dessous !!!
            #
            # D'ailleurs, .resolve est invoquée à l'endroit en question
            # uniquement au cas où l'objet ne soit pas un _FileSystemLeaf
            # mais un objet de type pathlib.PATH...
            #
            # Les lignes ci-dessous ne seront donc atteintes que si nous
            # utilisons notre méthode .resolve() ailleurs, sans avoir pris
            # garde de modifier le code de _FileSystemLeaf.
            #
            log_debug = self.tree.write_in_log

            log_debug('\tATTENTION : Suite à un problème de structure de données,')
            log_debug('\t< _FileSystemLeaf >.resolve() ne sait PAS garantir un PATH')
            log_debug('\tabsolu CORRECT... !!!')
            log_debug('')
            log_debug('\tCf les remarques contenues dans « skeleton { SRC }.py » à :')
            log_debug('')
            log_debug("\t\t« ATTENTION = Lorsqu'un path n'est pas absolu »")

            if __debug__:
                
                raise NotImplementedError


            # Hors déboggage, nous ne terminons pas le script sur ce
            # problème, nous notons tout simplement dans notre log
            # celui-ci, puis advienne que pourra !!!
            #
            # Nous renvoyons ainsi un nouvel objet construit sur un
            # path que nous espérons CORRECT, avec les restrictions
            # exposées ci-dessus dans le cartouche de cette fonction.
            #
            log_debug('')
            log_debug('\tNous ne terminons pas le script pour autant.')

            return FileSystemTree._FileSystemLeaf(
                        self.tree,
                        os.path.abspath(self.location_string)
                        )


        def iterdir(self) -> object:
            # ( itérateur / générateur ) -> _FileSystemLeaf [ ou ] PATHLIB.PATH
            """Iterate over the files in this directory. Does not
            yield any result for the special paths '.' and '..'.

            Cette fonction renvoie un GÉNÉRATEUR ( ie un ITÉRATEUR
            créé grâce à l'instruction YIELD présente dans son code ).

            Ce générateur renvoie alors une suite de données soit de
            type _FileSystemLeaf, soit de type PATHLIB.PATH.

            Pour être plus précis, iterdir() renvoie, dans certains
            cas, directement un itérateur :

                . si notre mode d'exécution est « pathlib_deeply »,
                alors nous renvoyons directement le résultat de la
                méthode pathlib.Path.iterdir().

                . si notre mode d'exécution est « pathlib_direct »,
                cette méthode < _FileSystemLeaf >.iterdir() ne sera
                pas appelée, pathlib.Path.iterdir() va la shunter
                et donc ce sera aussi directement un itérateur qui
                donnera les résultats.

            Mais que ce soit un GÉNÉRATEUR ou un ITÉRATEUR, c'est
            transparent pour notre appelant : dans les 2 cas, il
            verra défiler soit une suite de _FileSystemLeaf, soit
            une suite de variables PATHLIB.PATH.

            Cf :

                https://docs.python.org/3/library/os.html#os.listdir
                https://docs.python.org/3/library/os.html#os.scandir
                https://docs.python.org/3/library/pathlib.html#pathlib.Path.iterdir

            :return: les valeurs retournées par l'itérateur seront
            une suite soit de _FileSystemLeaf, soit de PATHLIB.PATH.

                Lorsqu'il s'agit de variables _FileSystemLeaf, nous
                nous assurons que la valeur retournée contienne un
                PATH ABSOLU.

                Si les données retournées sont de type PATHLIB.PATH
                alors ce sera le comportement intrinsèque du module
                PATHLIB qui définira s'il s'agit de PATHS ABSOLUS ou
                RELATIFS. En effet, dans ce cas, les résultats seront
                directement ceux de la méthode pathlib.Path.iterdir(),
                que ce soit en mode « pathlib_deeply » ( mode que nous
                pourrions contrôler via < _FileSystemLeaf >.iterdir() )
                ou en « pathlib_direct » ( mode que nous ne savons pas
                contrôler puisque direct : d'où le choix de conserver
                le fonctionnement intrinsèque de PATHLIB ).

                RQ : pathlib.Path(x).iterdir() donne 1 suite de paths
                ABSOLUS si son paramètre « x » est absolu. Le résultat
                sera un path RELATIF sinon.

                Il suffit de comparer sous IDLE les résultats de :

                    for i in pathlib.Path('K:\\_Backup.CDs').iterdir(): print(i)
                    for i in pathlib.Path('..').iterdir(): print(i)
                    for i in pathlib.Path().iterdir(): print(i)

                ... pour s'en convaincre.
            """

            log_debug = self.tree.write_in_log

            if self.tree.pathlib_import:

                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                log_debug('ITÉRATEUR = pathlib.iterdir()')
                generator = self.location_object.iterdir()


            # Nous sommes ici dans le mode « pathlib_ignore » et
            # nous n'utilisons que les fonctions de OS.PATH pour
            # émuler les méthodes de PATHLIB.
            #
            elif self.walking_mode == walking_via_scandir:

                # La fonction os.scandir() renvoie un itérateur mais
                # nous ne pouvons simplement en faire notre valeur de
                # retour ( tel « self.location_object.iterdir() » ci-
                # dessus ).
                #
                # En effet, notre appelant s'attend à recevoir 1 path,
                # or l'itérateur de os.scandir fourni des valeurs de
                # type « os.DirEntry ».
                #
                # Il nous faut donc retraiter les valeurs fournies par
                # cet itérateur ( via os.DirEntry.path ) puisque, qui
                # plus est, nous avons fait le choix d'alimenter notre
                # appelant en chemins absolus.
                #
                # Cf https://docs.python.org/3/library/os.html#os.DirEntry
                # Cf https://docs.python.org/3/library/os.html#os.scandir
                #
                # Return an iterator of os.DirEntry objects corresponding
                # to the entries in the directory given by path. The entries
                # are yielded in arbitrary order, and the special entries '.'
                # and '..' are not included.
                #
                log_debug('ITÉRATEUR = os.scandir()')
                iterator = os.scandir(path = self.location_string)

                # « x » sera de type os.DirEntry, il connaîtra donc son
                # répertoire et le fournira à os.path.abspath().
                #
                # Pas besoin donc d'écrire :
                #
                #   yield os.path.abspath(os.path.join(..))
                #
                # ... comme c'est le cas ci-dessous avec la fonct°
                # os.path.listdir().
                #
                # Cf les tests présents dans :
                #
                #   Cf  --- FILES and PATH --- ( mes ) NOTES = path ABSOLU [ vs ] RELATIF in os, pathlib, fnmatch + CONCATÉNATION de paths absolu et relatif.txt
                #   in _Know\Info\Dvpt\Réalisation\Langages\Python\- et - FICHIERS.rar
                #
                fct = lambda x: FileSystemTree._FileSystemLeaf(
                        self.tree,
                        os.path.abspath(x.path)
                        )

                generator = _generator_create(iterator, fct)


            else:

                # Nous allons parcourir le répertoire via la fonction
                # os.listdir() ( qui est donc la fonction par DÉFAUT
                # puisqu'elle est la dernière de cette séquence de IF
                # ... ELIF ... ELSE ).
                #
                # Nous pouvons ainsi éventuellement nous retrouver ici
                # dans 1 cas « walking_ignore » qui serait mal maîtrisé
                # et arriverait dans cette branche alors que, dans l'
                # absolu, un tel cas signifie que nous utilisons autre
                # chose que le module OS.PATH pour parcourir le système
                # de fichiers...
                #
                log_debug('ITÉRATEUR = os.listdir()')
                our_path = self.location_string
                iterator = os.listdir(path = our_path)

                # Nous renvoyons un chemin absolu car, après des
                # tests, il est apparu que c'était le moyen le
                # plus sûr de ne pas créer d'erreurs !!!
                #
                #   Cf * - TESTS --- ( pathlib.ITERDIR [ vs ] os.LISTDIR [ vs ] os.SCANDIR = PATH affiché en ABSOLU ou RELATIF ) ---.py
                #   in --- [ skeleton ] = 2Do & NOTES.rar\( TESTS ) dont « mplay32.exe »
                #   in _Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]
                #
                # ou
                #
                #   Cf --- FILES and PATH --- ( mes ) NOTES = pathlib.ITERDIR [ vs ] os.LISTDIR [ vs ] os.SCANDIR = PATH affiché en ABSOLU ou RELATIF ---.py
                #   in _Know\Info\Dvpt\Réalisation\Langages\Python\- et - FICHIERS.rar
                #
                fct = lambda x: FileSystemTree._FileSystemLeaf(
                        self.tree,
                        os.path.abspath(
                            os.path.join(
                                our_path,
                                x
                                )
                            )
                        )

                generator = _generator_create(iterator, fct)


            # La PRÉSENCE de YIELD dans le reste de cette fonction
            # impliquerait que le CODE de cette FONCTION ne SERAIT
            # EXÉCUTÉ que LORSQUE le GÉNÉRATEUR serait PARCOURU d'1
            # façon ( via un FOR ) ou d'1 autre ( via 1 liste... ).
            #
            # Il faut donc que cette fonction créé 1 générateur là
            # où dans les fichiers précédents elle créait 1 liste
            # et « yieldait » ( itérait ) sur cette liste.
            #
            # Il faut donc faire DISPARAÎTRE toute instruction YIELD
            # du corps de cette fonction en les déménageant ailleurs
            # ( dans 1 sous-fonction, dans 1 fonction globale, ... ) !!!
            #
            # Cf - GÉNÉRATEURS - Comment FONCTIONNE l'instruction YIELD *.py
            # in - et - ITÉRATEUR ou GÉNÉRATEUR.rar
            # in _Know\Info\Dvpt\Réalisation\Langages\Python
            #
            # Ici nous retournons donc bien le générateur créé ou
            # l'itérateur qui existe déjà. C'est ainsi dans notre
            # code que nous ne devons pas utiliser de YIELD mais
            # plutôt renvoyer 1 itérateur / générateur !!!
            #
            return generator


        def _parse_mask(
            self,
            mask: str = '*',
            s_type: int = None
            ) -> dict:
            """ Analyse un masque de recherche destiné à _fake_iglob()
            et renvoie un dictionnaire contenant le résultat de notre
            analyse. Ce dictionnaire pourra ensuite être passé en tant
            que paramètre à _fake_iglob() sous la forme :

                _fake_iglob( .., **_parse_mask( .. ) )

            :param mask: le masque de recherche & sont acceptés :

                - « * » : tous les fichiers.

                - « *.xxx » : les fichiers d'un certain type.

                - « title*.m* » : masque plus complexe.

                - n'importe quel masque interprétable via la méthode
                fnmatch() du module FNMATCH si la valeur de « s_type »
                est « _search_fnmatch ».

            :param s_type: ce paramètre n'a à être fourni que si nous
            désirons forcer la lecture du masque via le module FNMATCH
            ( valeur _search_fnmatch ). Sinon, il ne sera pas pris en
            compte.

            :return: un dictionnaire résultant de notre analyse de mask
            et qui peut être transmis à _fake_iglob().
            """

            log_debug = self.tree.write_in_log
            log_debug(f'ANALYSE du masque de recherche « {mask} »')

            mask_lst = None
            test_fct = None


            #
            # NOUS ALLONS IDENTIFIER QUEL EST LE TYPE DE RECHERCHE.
            #


            # L'appelant veut forcer ponctuellement une recherche
            # via le module FNMATCH...
            #
            if s_type == _search_fnmatch:

                log_debug('On force une lecture du masque via FNMATCH !!!')

                suffix = None

                global fnmatch
                try: fnmatch.translate('test_if*already_imported')
                except AttributeError: import fnmatch

                try: test_fct = _test_via_fnmatch
                except NameError:

                    # On testera le nom du fichier ou du répertoire
                    # via le module FNMATCH.
                    #
                    # Nous n'avons donc besoin que du nom et de la
                    # valeur du masque dans ce cas, tout autre data
                    # est ignorée...
                    #
                    def _test_via_fnmatch(
                        name: str,
                        mask: str,
                        **kwargs
                        ) -> bool:

                        return fnmatch.fnmatch(name, mask)

                    test_fct = _test_via_fnmatch


            # Nous n'utilisons pas le module FNMATCH.
            #
            # On regarde si l'on est face à une recherche simple
            # ( du type "*" ou "*.nnn" ) ou face à une recherche
            # plus complexe ( du type "title*.m*" ).
            #
            # On a séparé ces 2 cas pour des raisons de performance
            # mais le 1er n'est qu'un sous cas du 2nd & on pourrait
            # donc les réunir ( si l'on veut plus de simplicité du
            # code )...
            #
            # Actuellement, ce code est plus à visée didactique que
            # pour une mise en production !!!
            #
            elif mask == '*':

                # Cas d'1 chaîne de recherche très SIMPLE i-e : « * ».
                #
                suffix = ''
                s_type = _search_simple
                log_debug('Recherche de type SIMPLE !!!')
                log_debug('On accepte ici tous les noms.')


            elif mask[0] == '*' and not '*' in mask[1:]:

                # Cas d'1 chaîne de recherche SIMPLE i-e : « *< suffix > ».
                #
                suffix = mask[1:]
                s_type = _search_simple
                log_debug('Recherche de type SIMPLE !!!')
                log_debug(f"Recherche des noms avec l'extension : « {suffix} ».")


            else:

                # Cas d'1 chaîne de recherche COMPLEXE telle : « title*.m* ».
                #
                s_type = _search_complex

                suffix_idx = mask.rfind('.')
                if suffix_idx >= 0:
                    suffix = mask[suffix_idx:]
                else:
                    suffix = ''

                log_debug('Recherche de type COMPLEXE !!!')
                log_debug(f'Recherche de noms du type : « {mask} ».')
                log_debug(f'... donc avec « {suffix} » comme extension.')

                # Conversion de la chaîne de recherche demandée en une liste afin
                # de faciliter, par la suite, les comparaisons des noms de fichiers
                # avec le masque de recherche...
                #
                # On découpe ainsi le masque de recherche en considérant le caractère
                # joker '*' comme un délimiteur.
                #
                # PAR CONTRE, pour réaliser les comparaisons, on va convertir les
                # éléments en minuscules...
                #
                # Cf ci-dessous « PAR CONTRE, pour réaliser la comparaison via rfind ».
                #
                mask_lst = mask.lower().split('*')
                #
                # Avant nous trouvions le même résultat via une expression beaucoup
                # plus complexe :
                #
                #   mask_lst = list(map(str.lower, mask.split('*')))
                #
                log_debug(f'Le masque convertit en liste et minuscules vaut : {mask_lst}.')


            #
            # NOUS ALLONS CONSTRUIRE LA FONCTION DE TEST.
            #


            # En fonction du type de recherche qui a été identifié, on construit
            # la FONCTION qui sera utilisée par _fake_iglob() pour TESTER si le
            # nom d'un noeud ( fichier ou répertoire ) correspond au masque...
            #
            # Dans le cas d'une recherche type _search_fnmatch, cette fonction a
            # déjà été affectée et construite ci-dessus, dès l'identification de
            # la recherche. Ceci s'explique par le fait qu'une telle recherche
            # ne donne lieu qu'à un seul cas d'identification, donc on peut dès
            # ce cas définir la fonction...
            #
            # Pour les autres types de recherche, plusieurs branche du code sont
            # suceptibles de donner la même recherche. On attend donc cet endroit
            # du code pour définir la fonction de test, i-e une fois que toutes
            # les branches ont été parcourues.


            # FONCTION de TEST pour une RECHERCHE SIMPLE.
            #
            # On construit notre algorithme de recherche dite « SIMPLE » dans le
            # répertoire. _fake_iglob() l'appelera avec les paramètres adéquats.
            #
            if s_type == _search_simple:

                try: test_fct = _test_simple
                except NameError:

                    # Nous n'avons ici besoin que du nom, du masque, et de qq
                    # infos sur le suffixe ( nous aurions pu recalculer lors de
                    # chaque appel ces informations, mais au prix d'une perte de
                    # temps & nous avons choisi de perdre de la mémoire plutôt ).
                    #
                    def _test_simple(
                        name: str,
                        mask: str,
                        suffix_len: int,
                        suffix_lower: int,
                        **kwargs
                        ) -> bool:

                        # Si le fichier a le suffixe voulu, on l'intègre à la
                        # liste.
                        #
                        # Pour ceci, le plus "universel" est de vérifier que
                        # l'on trouve bien le suffixe cherché en toute fin du
                        # nom du fichier et, pour réaliser ce test, on utilise
                        # ici la méthode rfind().
                        #
                        # Cette fonction va trouver l'occurence, si elle existe,
                        # du suffixe que nous cherchons et qui serait située la
                        # plus à droite dans le nom du fichier. Si cette occurence
                        # est trouvée, rfind() nous informe de l'index dans le nom
                        # de fichier où l'on peut trouver cette occurence. Or si
                        # cet index est égal à la soustraction de la longueur du
                        # nom de fichier par la longueur du suffixe, c'est que le
                        # suffixe est bien situé en toute fin du nom de fichier...
                        #
                        # PAR CONTRE, pour réaliser la comparaison via rfind, on
                        # convertit d'abord les 2 chaînes en minuscules, et ceci
                        # afin que, par exemple :
                        #
                        #       - si suffix = « .mkv » ;
                        #
                        #       - si certains fichiers finissent en « .mkv », d'
                        #       autres en « .MKV », et d'autres en « .Mkv » ;
                        #
                        # ... alors tous ces fichiers ressortent dans la liste !
                        #
                        # ATTENTION : Avant, au regard de l'algorithme décrit ci-
                        # dessus, le test effectué était :
                        #
                        #       if suffix == '' or \
                        #       (file_or_dir.lower().rfind(suffix_lower) == len(file_or_dir) - len(suffix)):
                        #
                        # ... mais, pour des noms de fichiers courts, type « @i »,
                        # ce test ( sa deuxième partie ) ne marchait pas avec, par
                        # exemple, « *.py » :
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
                        name = name.lower()
                        suffix_idx = name.rfind(suffix_lower)

                        return suffix == '' or (
                                    suffix_idx >= 0 and \
                                    len(name) >= suffix_len and \
                                    suffix_idx == len(name) - suffix_len
                                    )

                    test_fct = _test_simple


            # FONCTION de TEST pour une RECHERCHE COMPLEXE.
            #
            # On construit notre algorithme de recherche dite « COMPLEXE » dans
            # le répertoire. _fake_iglob l'appelera avec les paramètres adéquats.
            #
            elif s_type == _search_complex:

                try: test_fct = _test_complex
                except NameError:

                    # Nous n'avons ici besoin que du nom, du masque, et de la
                    # décomposition de ce masque en une liste ( nous aurions pu
                    # recalculer lors de chaque appel cette liste, mais au prix
                    # d'une perte de temps & nous avons choisi de perdre de la
                    # mémoire plutôt ).
                    #
                    def _test_complex(
                        name: str,
                        mask: str,
                        mask_lst: list,
                        **kwargs
                        ) -> bool:

                        # Pour réaliser les comparaisons, on va convertir en le
                        # nom en minuscules. Cf ci-dessus :
                        #
                        #   « PAR CONTRE, pour réaliser la comparaison via rfind ».
                        #
                        name = name.lower()
                        node_ok = True

                        # On va chercher si le nom du fichier contient chacune
                        # des sous-chaînes de la liste correspondant au masque
                        # de recherche.
                        #
                        # ATTENTION : On ne teste ici "que" si la sous-chaîne
                        # se trouve dans le nom de fichier. Pour être plus exact,
                        # il faudrait vérifier, quand le masque est de type :
                        #
                        #   « xxx*(..)*zzz »,
                        #
                        # ... si la 1ère sous-chaîne est bien le début ( et le
                        # début exactement ) du nom de fichier en utilisant :
                        #
                        #   file_name.startswith(mask_part)
                        #
                        # ... mais également vérifier que la dernière sous-chaîne
                        # est la fin ( et exactement la fin ) du nom de fichier,
                        # en utilisant :
                        #
                        #   file_name.endswith(mask_part)
                        #
                        # Cela pourrait être l'objet d'1 développement ultérieur.
                        #
                        # Pour l'instant, ce n'est pas très dérangeant, donc on
                        # laisse tel quel. Du coup, pour les masques ayant comme
                        # type « xxx*(..)*zzz », cette fonction réalise en fait
                        # une recherche du type :
                        #
                        #   « *xxx*(..)*zzz* »
                        #
                        # ADDENDUM : Le fait de réaliser une recherche du type
                        # « *xxx*(..)*zzz* » alors que nous a été demandé une
                        # recherche « xxx*(..)*zzz » est en fait plus dérangeant
                        # que prévu. Ainsi, lors d'1 recherche ayant pour masque
                        # « title_t*.mkv », les solutions suivantes sont sorties
                        # à l'écran ( !!! ) :
                        #
                        #       - ( 2 ) what to encode - from « title_t00.mkv ».cfg
                        #       - title_t03.mkv
                        #       - >>> CRÉATION d'un fichier de configuration [..] <<<
                        #
                        # EXPLICATIONS : Nous avons demandé « title_t*.mkv » donc,
                        # avec une recherche « xxx*(..)*zzz », seul "title_t03.mkv"
                        # serait apparu.
                        #
                        # Mais nous avons réalisé 1 recherche « *xxx*(..)*zzz* »,
                        # donc "( 2 ) what to encode - from « title_t00.mkv ».cfg"
                        # est aussi valide dans ce cadre !!!
                        #
                        # Nous avons donc renvoyé à notre appelant ces 2 solutions...
                        #
                        # Or, search_files_from_a_mask() était alors appelée depuis
                        # le point :
                        #
                        #   « 3ème partie : On cherche » de MediaFile.choose_file()
                        #
                        # ... ce qui a provoqué, dans la suite des traitements ( ie
                        # « 4ème partie : On ajoute éventuellement des solutions » )
                        # de choose_file(), que la solution :
                        #
                        #   « >>> CRÉATION d'un fichier de configuration [..] <<< »
                        #
                        # ... soit ajoutée. En effet, cette ligne est automatiquement
                        # ajoutée si apparaît dans la liste des fichiers résultat au
                        # moins un .CFG !!!
                        #
                        # CONCLUSION : Il a fallu rendre plus exact l'algorithme ci-
                        # dessous afin qu'une recherche type « xxx*(..)*zzz » ne soit
                        # plus traitée comme une recherche type « *xxx*(..)*zzz* ».
                        #
                        # D'où l'ajout des 2 "if" couplés aux fonctions startswith()
                        # et endswith().
                        #
                        # Il aurait été probablement plus efficace d'intégrer ces "if"
                        # à la boucle "for" qui suit : en effet, dans cette boucle,
                        # on teste de nouveau la 1ère et la dernière sous-chaînes de
                        # recherche ( déjà testées dans les "if" ).
                        #
                        # Toutefois, d'une part, ces 2 "if" facilitent la lecture de
                        # l'algorithme et, d'autre part, ils sont bien plus rapides
                        # à écrire !!!
                        #
                        # Lorsque j'aurais du temps, il sera possible d'améliorer
                        # cet algorithme...
                        #
                        if mask[0] != '*' and not name.startswith(mask_lst[0]):
                            node_ok = False

                        elif mask[-1] != '*' and not name.endswith(mask_lst[-1]):
                            node_ok = False

                        else:
                            for mask_part in mask_lst:

                                if mask_part in name:
                                    # On trouve bien la sous-chaîne considérée dans
                                    # le nom de fichier. On retire alors du nom de
                                    # fichier la séquence "*<cette sous-chaîne>", et
                                    # on va continuer la boucle afin de vérifier que
                                    # les sous-chaînes suivantes sont bien présentes
                                    # dans ce qui reste du nom de fichier...
                                    #
                                    # Algorithme :
                                    #
                                    #   part_index_begin = name.index(mask_part)
                                    #   part_index_end = part_index_begin + len(mask_part)
                                    #   name = name[part_index_end:]
                                    #
                                    # Sa simplification :
                                    #
                                    name = name[
                                        name.index(mask_part) + len(mask_part)
                                        :
                                        ]

                                else:
                                    # Une des sous-chaînes recherche n'est pas présente
                                    # dans le nom du fichier. On ne retient donc pas ce
                                    # fichier...
                                    #
                                    node_ok = False
                                    break

                        return node_ok

                    test_fct = _test_complex


            # On construit le dictionnaire qui va nous permettre de transmettre
            # notre analyse à _fake_iglob().
            #
            return {
                'mask'      :   mask,
                's_type'    :   s_type,
                'suffix'    :   suffix,
                'mask_lst'  :   mask_lst,
                'test_fct'  :   test_fct,
            }


        def _fake_iglob(
            self,
            n_type: int = _glob_all_nodes,
            #
            # Si avant l'appel à _fake_iglob(), _parse_mask() a été
            # appelée, point n'est besoin de fournir à nouveau la
            # valeur de « mask » puisqu'elle aura déjà été donnée à
            # _parse_mask() !!!
            #
            mask: str = '*',
            #
            # Les paramètres suivants n'ont pas à être indiqués par
            # l'appelant, sauf via 1 dictionnaire qui lui aurait été
            # transmis après un appel à notre méthode _parse_mask() :
            #
            #   _fake_iglob( .., **_parse_mask( .. ) )
            #
            # Un tel appel à _parse_mask() autorise en fait à tester
            # la bonne rédaction de « mask », ainsi qu'à initialiser
            # à l'avance les données nécessaires au bon déroulé de la
            # recherche.
            #
            # Nous aurions pu réaliser cette fonctionnalité d'1 façon
            # différente ( via des fonctions LAMBDA par exemple, ou
            # via le transfert en paramètre d'un dictionnaire ) mais
            # nous avons choisi cette manière à des fins didactiques
            # i.e pour tester les possibilités type « KWARGS » qui
            # sont offertes par Python.
            #
            s_type: int = None,
            suffix: str = None,
            mask_lst: list = None,
            test_fct: object = None, # function
            ) -> list:
            # -> list( STR )
            """ Cherche dans un répertoire tous les noeuds dont le
            nom correspond à un certain masque. Renvoie 1 itérateur
            ( ou plutôt un générateur ) sur ces noeuds ( fichiers ou
            répertoires ), dont les chemins seront exprimés en paths
            ABSOLUS.

            Cette méthode émule glob.iglob(), fnmatch.filter() ou
            pathlib.glob().
            Cf :

                https://docs.python.org/3/library/glob.html#glob.iglob
                https://docs.python.org/3/library/fnmatch.html#fnmatch.filter
                https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob

            Pour le détail des masques acceptés, cf la définition
            ci-dessous de notre paramètre mask ( « :param mask: » ).

            En terme de puissance d'écriture du masque, _fake_iglob
            n'offre toutefois pas toutes les possibilités présentes
            chez les fonctions qu'elle émule.

            Par exemple, actuellement, elle ne sait interpréter les
            caractères spéciaux ( wildcards ) suivants :

                ?           matches any single character
                [seq]       matches any character in seq
                [!seq]      matches any character not in seq

            SAUF SI NOUS IMPOSONS EN AMONT L'UTILISATION DE FNMATCH
            VIA UN APPEL DU TYPE :

                 _fake_iglob( n_type, **_parse_mask( mask, _search_fnmatch ) )


            :param n_type: voulons-nous que soient retournés :

                - _glob_all_nodes = les fichiers et répertoires
                correspondant au masque fourni.

                - _glob_only_dirs = seulement les répertoires.

                - _glob_only_files = seulement les fichiers.


            :param mask: le masque de recherche & sont acceptés :

                - « * » : tous les fichiers.

                - « *.xxx » : les fichiers d'un certain type.

                - « title*.m* » : masque plus complexe.

                Si avant l'appel à _fake_iglob(), _parse_mask a été
                invoquée, point n'est besoin de donner à nouveau la
                valeur de « mask » puisqu'elle aura déjà été fournie
                à _parse_mask() !!!


            :param s_type:
            :param suffix:
            :param mask_lst:
            :param test_fct:
                Les paramètres ci-dessus n'ont pas à être indiqués
                par notre appelant, sauf via 1 dictionnaire qui lui
                aurait été transmis après un appel à _parse_mask().
                Cf commentaire ci-dessus inclus dans la définition
                de notre grammaire d'appel ( def _fake_iglob ... ).


            :return: la liste des fichiers trouvés, dont toutes les
            valeurs seront de type STRING, et représenteront un path
            ABSOLU.
            """

            leaf = self.tree.node

            log_debug = self.tree.write_in_log
            log_debug('Recherche de fichiers via « _fake_iglob »')
            log_debug('... avec des résultats sous forme de PATHS ABSOLUS')
            log_debug(f'... avec itération via « {self.walking_mode} ».')


            # On indique si tous les noeuds seront recherchés, seulement les
            # fichiers, ou seulement les répertoires.
            #
            if n_type == _glob_all_nodes:
                log_debug("Fichiers ET répertoires acceptés.")

            elif n_type == _glob_only_dirs:
                log_debug("RÉPERTOIRES seuls acceptés.")

            else:
                log_debug("FICHIERS seuls acceptés.")


            # Si les paramètres de notre recherche n'ont pas été initialisés,
            # nous nous en chargeons...
            #
            if s_type is None or test_fct is None:

                log_debug("Nous devons en premier lieu analyser le masque.")

                mask_dct = self._parse_mask(mask)
                s_type = mask_dct['s_type']
                suffix = mask_dct['suffix']
                mask_lst = mask_dct['mask_lst']
                test_fct = mask_dct['test_fct']

            else:
                log_debug("Le masque a déjà été analysé.")


            # On lance notre recherche grâce à l'initialisation qui résulte
            # de l'appel en amont à _parse_mask().
            #
            if s_type in _searches_lst:

                log_debug(f"Fonction de « match » : {test_fct}")

                s_len = len(suffix) if suffix is not None else 0
                s_lower = suffix.lower() if suffix is not None else None

                for file_or_dir in self.iterdir():

                    # Le noeud du système de fichier dont nous allons inspecter
                    # le nom est-il bien du type recherché ?
                    #
                    # C-a-d cherchons-nous tous les noeuds ? les fichiers ou les
                    # répertoires seulement ?
                    #
                    node_ok = (n_type == _glob_all_nodes) \
                        or (n_type == _glob_only_dirs and file_or_dir.is_dir()) \
                        or (n_type == _glob_only_files and file_or_dir.is_file())

                    # On teste si le nom du fichier ou du répertoire correspond au
                    # masque indiqué.
                    #
                    # Nous fournissons à la fonction de test toutes les infos dont
                    # elle pourrait avoir besoin. Certaines de celles-ci auraient
                    # pu être recalculées lors de chaque appel, au prix d'1 perte
                    # de temps. Nous avons choisi de perdre de la mémoire plutôt.
                    #
                    # Nous aurions pu transmettre à la fonction « test_fct » ces
                    # paramètres d'une façon différente ( via une fonction LAMBDA
                    # définie ds _parse_mask avec les bons arguments par exemple,
                    # ou via le transfert en paramètre d'1 dictionnaire ) mais ns
                    # avons opté pour cette méthode à des fins didactiques ie pour
                    # tester les possibilités type « KWARGS » offertes par Python.
                    #
                    # Par contre, nous n'aurions pu utiliser des variables d'un
                    # type « NON LOCAL » à l'intérieur de _parse_mask() et de sa
                    # fonction imbriquée choisie pour les tests. En effet, nous
                    # aurions alors pu nous confronter à des effets de bord non
                    # désirés dans le cas d'exécution en // ou asynchrone !!!
                    #
                    if node_ok and test_fct(
                                        file_or_dir.name,
                                        mask = mask,
                                        mask_lst = mask_lst,
                                        suffix_len = s_len,
                                        suffix_lower = s_lower,
                                        ):

                        log_debug(f'Nouveau fichier trouvé : « {file_or_dir} ».')
                        log_debug(f'\t\t=> DATATYPE = {type(file_or_dir)}')

                        # Notre méthode .iterdir() ne fournit un PATH ABSOLU
                        # que dans le cas où elle renvoie des _FileSystemLeaf.
                        # Dans ce cas, nous pourrions donc n'écrire que :
                        #
                        #   yield str(file_or_dir)
                        #                        
                        # Mais si notre squelette est configuré pour travailler
                        # avec le module PATHLIB, alors les objets file_or_dir
                        # sont de type pathlib.PATH : aucune garantie qu'ils ne
                        # soient en ce cas avec un path absolu, d'où l'appel à
                        # la méthode .resolve() pour cela...
                        #
                        # Pour plus d'explications, cf la partie « :return: »
                        # dans l'entête de notre méthode .iterdir() :
                        #
                        #   « def iterdir(self) -> object: »
                        #
                        yield str(file_or_dir.resolve())
                        #
                        # Cf aussi la mise en garde ds notre méthode .resolve :
                        #
                        #   « ATTENTION = Lorsqu'un path n'est pas absolu »


            # Si le type de recherche ne nous est pas connu, nous devrions
            # lancer une exception. Nous avons ici choisi de ne renvoyer
            # aucun résultat.
            #
            else:
                log_debug(f"Type de recherche inconnu : {s_type}.")
                log_debug("AUCUN RÉSULTAT NE SERA DONC FOURNI !!!")

                yield from ()


        def glob(self, mask: str = '*') -> os.PathLike:
            # -> ( itérateur / générateur ) STR [ ou ] PATHLIB.PATH
            """ Glob the given relative pattern in the directory
            represented by this path, yielding all matching files
            (of any kind).

            Cf https://docs.python.org/3/library/glob.html#glob.glob
            Cf https://docs.python.org/3/library/glob.html#glob.iglob
            Cf https://docs.python.org/3/library/fnmatch.html#fnmatch.filter
            Cf https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob

            ATTENTION : Cette méthode retourne...

                . soit une liste de path sous forme de STRING
                ( cas « pathlib_ignore », « with_glob », « with_fnmatch » )

                . soit une liste de path sous forme de pathlib.PATH
                ( cas « pathlib_direct » ou « pathlib_deeply » )

                En effet, pathlib.glob() retourne une liste de valeurs
                de type pathlib.PATH et non de type STRING !!!

            ... donc il faut tenir compte de cela lorsque l'on traite
            la liste des résultats, sous peine de PLANTAGE !!!

            Par exemple, si l'on concatène chacun des résultats avec
            une chaîne de caractères ( STRING ) pour écrire 1 message,
            dans le 2nd cas cela lèvera une exception car l'opération
            « STRING » + « pathlib.PATH » n'est pas définie.

            Qq chose comme :

                for name in < FileSystemTree._FileSystemLeaf >.glob('*.py'):
                    print('\t' + name)

            ... pourrait ainsi planter notre script dans le 2nd cas.

            :param mask: le masque de recherche, qui peut contenir
            des « wildcards ». Ces wildcards sont soit ceux compris
            par pathlib.glob(), glob.glob() ou fnmatch.filter(), soit
            ceux compris par notre méthode _fake_iglob(). Cela dépend
            si nous avons ou pas importé les modules PATHLIB ou GLOB,
            voire FNMATCH.

            :return: un itérateur sur la liste des répertoires ou des
            fichiers trouvés, et cette suite de valeurs sera de type
            STRING ou PATHLIB.PATH. Nous essayerons par ailleurs au
            maximum que ces valeurs soient des paths ABSOLUS.

                Lorsqu'il s'agit de STRINGS, nous nous assurons que
                la valeur retournée soit un PATH ABSOLU.

                Si les données retournées sont de type PATHLIB.PATH,
                la valeur retournée sera un PATH ABSOLU ( ie en mode
                « pathlib_deeply ) de type PATHLIB.PATH.

                Par contre, en mode « pathlib_direct », mode que nous
                ne savons pas contrôler puisqu'il est direct et shunte
                cette fonction, alors les paths seront absolus si le
                module pathlib l'entend de cette oreille, ils seront
                relatifs sinon...

            RQ : Le comportement intrinsèque du module PATHLIB est le
            suivant = pathlib.Path(x).glob(..) donne 1 suite de paths
            ABSOLUS si son paramètre « x » est absolu. Les résultats
            seront des paths RELATIFS sinon.

            Il suffit de comparer sous IDLE les résultats de :

                for i in pathlib.Path('K:\\_Backup.CDs').glob('*.rar'): print(i)
                for i in pathlib.Path('..').glob('*.zip'): print(i)
                for i in pathlib.Path().glob('*.py'): print(i)

            ... pour s'en convaincre.
            """

            log_debug = self.tree.write_in_log

            if not self.is_dir():

                log_debug("Configuration d'une recherche - Répertoire non valide :")
                log_debug(f"« {self} »")

                # Dans ce script, nous aurions toutefois pu opter
                # pour renvoyer une liste vide :
                #
                #   return list()
                #
                # ... ou plutôt un itérateur vide :
                #
                #   iter(())
                #
                # mais l'utilisation de ce _generator_empty() a
                # été choisi pour des raisons didactiques...
                #
                generator = _generator_empty()


            elif self.tree.with_glob:

                # Nous avons l'autorisation de nous servir de la
                # librairie GLOB de Python.
                #
                log_debug("Configuration d'une recherche - via « glob.iglob »")
                log_debug('... avec des résultats sous forme de PATHS ABSOLUS')

                # glob.iglob() fourni un itérateur, nous pourrions
                # donc écrire :
                #
                #   generator = glob.iglob(..)
                #
                # Toutefois, nous sommes obligés de l'encapsuler,
                # car nous voulons transformer la suite de paths
                # RELATIFS fournie par glob.iglob() en des PATHS
                # ABSOLUS !!!
                #
                # Nous encapsulons donc l'itérateur fourni par
                # glob.iglob() dans notre propre générateur.
                #
                dir = self.location_string
                iterator = glob.iglob(mask, root_dir = dir)
                fct = lambda x: os.path.abspath(os.path.join(dir, x))

                generator = _generator_create(iterator, fct)


            elif self.tree.with_fnmatch:

                # Nous avons l'autorisation de nous servir de la
                # librairie FNMATCH de Python.
                #
                log_debug("Configuration d'une recherche - via « fnmatch.filter »")
                log_debug('... avec des résultats sous forme de PATHS ABSOLUS')
                log_debug(f'... avec itération via « {self.walking_mode} »')

                # fnmatch.filter() construit & renvoie une liste.
                #
                #
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # !!! EXEMPLE D'UTILISATION DE LA FONCTION MAP() !!!
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                #
                #
                # En 1er paramètre, fnmatch.filter attend une liste
                # d'objets os.Pathlike. Or notre méthode iterdir()
                # fournit 1 liste d'objets soit typés pathlib.Path
                # ( classe incluse dans os.Pathlike ), soit typés
                # _FileSystemLeaf ( classe inconnue de os.Pathlike )
                # donc nous utilisons la fonction MAPS() afin que
                # soit appliquée la méthode STR() à chacun de ces
                # objets, et ainsi que fnmatch.filter() puisse les
                # comprendre, même s'ils sont typés _FileSystemLeaf,
                # car le type STRING est inclus dans os.Pathlike.
                #
                # D'où la 1ère solution adoptée :
                #
                #   iterable = fnmatch.filter(map(str, self.iterdir()), mask)
                #
                #
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # !!! EXEMPLE D'UTILISATION D'UNE COMPRÉHENSION DE LISTE !!!
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                #
                #
                # Pour autant, par la suite, notre fonction iterdir()
                # a renvoyé des PATHS ABSOLUS, ce qui a eu pour effet
                # que la fonction fnmatch.filter() reconnaisse moins
                # bien les fichiers / répertoires cherchés. Ainsi, si
                # l'on recherche un masque « Sk*lE*.py » et que :
                #
                #   map(str, self.iterdir())
                #
                # ... nous fournit comme liste :
                #
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\__pycache__
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\#_LOG_for_skeleton { SRC }_#_nzhx35c8.log
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\( outils ) DEPLOY - skeleton.bat
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\( outils ) RUN from anywhere - skeleton - via Python 3.11.bat
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\( tool ) EDIT script ( in current directory ) using IDLE and Python 3.11.lnk
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\--- [ skeleton ] = 2Do & NOTES.rar
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\skeleton { SRC }.py
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\skeleton.py
                #
                # ... alors fnmatch.filter ne trouvera aucun résultat
                # puisque perturbé par le chemin en début de chacune
                # des STRINGS.
                #
                # Nous avions donc besoin de fournir à fnmatch.filter()
                # la liste des noms de fichiers SANS leur chemin c-a-d
                # la 2ème solution :
                #
                #   iterable = [str(n) for n in self.iterdir() if fnmatch.fnmatch(n.name, mask)]
                #
                # Cette dernière solution permet de renvoyer str(n)
                # donc les PATHS ABSOLUS puisque self.iterdir() le
                # fait autant que faire se peut.
                #
                # Pour autant, dans la documentation de fnmatch.filter(),
                # on lit :
                #
                #   fnmatch.filter(names, pattern)¶
                #   Construct a list from those elements of the iterable names that match pattern.
                #   It is the same as [n for n in names if fnmatch(n, pattern)], but implemented
                #   more efficiently.
                #
                # ... MORE EFFICIENTLY, donc nous avons choisi d'adopter
                # une 3ème solution, utilisant fnmatch.filter() au lieu de
                # fnmatch.fnmatch(), d'où la 3ème solution :
                #
                iterable = fnmatch.filter([n.name for n in self.iterdir()], mask)
                #
                # Cette solution crée une liste de noms de fichiers ou de
                # répertoires seuls ( sans leur chemin ) mais cela sera
                # corrigé par la fonction lambda « fct » ci-dessous...
                #
                fct = lambda x: os.path.abspath(
                        os.path.join(
                            self.location_string,
                            x
                            )
                        )

                generator = _generator_create(iterable, fct)


            elif self.tree.pathlib_import:

                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                log_debug("Configuration d'une recherche - via « pathlib.glob »")
                log_debug('... avec des résultats sous forme de PATHS ABSOLUS')

                # pathlib.Path.glob() construit & renvoie 1 générateur.
                #
                # Cf (..)\Python310\lib\pathlib.py
                #
                # Les tests suivants sous IDDLE le confirment :
                #
                #   import pathlib
                #   lst = pathlib.Path('.').glob('*')
                #   type(lst)
                #
                # -> result = <class 'generator'>
                #
                #   print(lst)
                #
                # -> result = <generator object Path.glob at 0x00000182FFB63A00>
                #
                # Par ailleurs, pathlib.Path(x).glob() donne des paths
                # ABSOLUS si son paramètre « x » est absolu, sinon les
                # paths seront RELATIFS.
                #
                # Il suffit de comparer sous IDLE les résultats de :
                #
                #   for i in pathlib.Path('K:\\_Backup.CDs').glob('*.rar'): print(i)
                #   for i in pathlib.Path('..').glob('*.zip'): print(i)
                #   for i in pathlib.Path().glob('*.py'): print(i)
                #
                # ... pour s'en convaincre.
                #
                # Pour forcer la réponse sous forme de path ABSOLU, nous
                # utilisons les méthodes de pathlib transformant un path
                # relatif en path absolu.
                #
                # Toutefois, nous n'avons pas choisi Path.absolute() :
                #
                #   generator = pathlib.Path(x).absolute().glob()
                #
                # En effet, cette méthode fournit parfois des réponses du
                # type :
                #
                #   K:\_Know\Info\Dvpt\Réalisation\Src\_Python\[ skeleton ]\..\all files to one PDF\skeleton.py
                #
                # Avec la méthode resolve(), par contre :
                #
                #   « “..” components are also eliminated (this is the only method to do so) »
                #
                #   Cf https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve
                #
                # C'est donc elle que nous utilisons.
                #
                generator = self.location_object.resolve().glob(mask)


            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                log_debug("Configuration d'une recherche - via « _fake_iglob »")

                # Nous ne pouvons nous servir du paramètre « n_type »
                # de _fake_iglob() car notre méthode glob ne propose
                # pas ce type de paramètre ( et ce car ni glob.glob,
                # ni pathlib.glob ne proposent une telle info... ).
                #
                # Nous demandons donc la recherche de tous les types
                # de noeuds ( fichiers et répertoires ).
                #
                generator = self._fake_iglob(**self._parse_mask(mask))


            # La PRÉSENCE de YIELD dans le reste de cette fonction
            # impliquerait que le CODE de cette FONCTION ne SERAIT
            # EXÉCUTÉ que LORSQUE le GÉNÉRATEUR serait PARCOURU d'1
            # façon ( via un FOR ) ou d'1 autre ( via 1 liste... ).
            #
            # Il faut donc que cette fonction créé 1 générateur là
            # où dans les fichiers précédents elle créait 1 liste
            # et « yieldait » ( itérait ) sur cette liste.
            #
            # Il faut donc faire DISPARAÎTRE toute instruction YIELD
            # du corps de cette fonction en les déménageant ailleurs
            # ( dans 1 sous-fonction, dans 1 fonction globale, ... ) !!!
            #
            # Cf - GÉNÉRATEURS - Comment FONCTIONNE l'instruction YIELD *.py
            # in - et - ITÉRATEUR ou GÉNÉRATEUR.rar
            # in _Know\Info\Dvpt\Réalisation\Langages\Python
            #
            # Ici nous retournons donc bien le générateur créé ou
            # l'itérateur qui existe déjà. C'est ainsi dans notre
            # code que nous ne devons pas utiliser de YIELD mais
            # plutôt renvoyer 1 itérateur / générateur !!!
            #
            return generator


        def touch(self):
            """ Pour CRÉER un fichier.

            ATTENTION : Contrairement à pathlib.Path.touch(), nous avons
            choisi de ne pas autoriser l'écrasement du fichier s'il existe
            déjà ( « exist_ok = False » ) !!!

            Cf https://docs.python.org/3/library/pathlib.html#pathlib.Path.touch
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                self.location_object.touch(exist_ok = False)

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                if self.is_file():
                    raise FileExistsError

                else:
                    with open(self.location_string, "wt") as fd:
                        #fd.write('Dummy for debug')
                        fd.write('')


        def rename(
            self,
            #target: os.PathLike
            target: object     # _FileSystemLeaf [ ou ] os.PathLike
            ):
            """ Pour RENOMMER un fichier.

            ATTENTION : Avant Python version 3.8, pathlib.Path.rename()
            ne renvoyait aucune valeur... donc nous faisons de même.

            Cf https://docs.python.org/3/library/pathlib.html#pathlib.Path.rename
            """

            try:
                t = target if isinstance(target, os.PathLike) else str(target)

            except TypeError:
                return NotImplemented

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                self.location_object.rename(t)

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                os.rename(self.location_string, t)


        def unlink(self):
            """ Pour DÉTRUIRE un fichier.
            """

            if self.tree.pathlib_import:
                # Lorsque nous nous trouvons ici, alors notre mode
                # d'exécution est « pathlib_deeply ».
                #
                # Ainsi, nous utilisons le module PATHLIB, mais pas
                # directement. Un objet _FileSystemLeaf est créé afin
                # d'accéder et / ou manipuler un noeud du système de
                # fichiers, via les méthodes du module PATHLIB.
                #
                self.location_object.unlink(missing_ok = False)

            else:
                # Nous sommes ici dans le mode « pathlib_ignore » et
                # nous n'utilisons que les fonctions de OS.PATH pour
                # émuler les méthodes de PATHLIB.
                #
                os.remove(self.location_string)


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Définition de la classe ScriptSkeleton ( __init__() et __del__() ).
#
# ---------------------------------------------------------------------------


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
        debug_mode: bool = ___debug___,
        walking_mode: str = walking_via_listdir,
        with_pathlib: str = ___dflt_pathlib___,
        with_fnmatch: bool = False,
        with_glob: bool = False
        ):
        """
        :param module_name: nom du module.

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

        :param walking_mode: si ce « squelette » n'utilise que le
        module OS.PATH, pour parcourir 1 répertoire utilisera-t-il
        la fct os.listdir() ou os.scandir() ?

            * walking_via_listdir : os.listdir() utilisée.

            * walking_via_scandir : os.scandir() utilisée.

            * walking_ignore : peu importe ( cas où module PATHLIB
            est utilisé pour gérer les fichiers... ) et, si nous
            arrivons tout de même dans 1 partie de code utilisant
            cette informat°, la méthode par défaut ( ie os.listdir()
            sera utilisée ).

            RQ = Si les modules GLOB ou FNMATCH sont importés, cela
            n'impose pas le walking_mode et il faut le spécifier !

            RQ = Cf FileSystemTree._FileSystemLeaf.iterdir()

        :param with_pathlib: ce « squelette » va-t-il s'appuyer sur
        le module PATHLIB, ou simplement se servir de la librairie
        OS.PATH ? Valeurs possibles :

            * pathlib_ignore ( None ) : pas de module PATHLIB.

            * pathlib_direct : module PATHLIB sans filtre.

            * pathlib_deeply : module PATHLIB incorporé.

        :param with_fnmatch: ce « squelette » va-t-il s'appuyer sur
        le module FNMATCH ?

        :param with_glob: ce « squelette » va-t-il s'appuyer sur le
        module GLOB ?
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

        # On créé l'objet qui va nous permettre d'accéder à la gestion des répertoires
        # et des fichiers.
        #
        self.files = FileSystemTree(
            walking_mode = walking_mode,
            with_pathlib = with_pathlib,
            with_fnmatch = with_fnmatch,
            with_glob = with_glob
            )

        # Nous sommes obligés d'initialiser logItem à None, et ce afin que Python sache
        # que ScriptSkeleton possède un attribut de ce nom.
        #
        # En effet, dans la fonction on_ouvre_le_journal(), on nomme cet attribut !!!
        # Alors s'il n'a pas été déclaré dans la fonction __init__, avant l'appel, le
        # script va planter car Python ne saura pas que cet attribut existe...
        #
        if module_name is None:

            # On donne comme nom de module, le nom de base ( sans extension ) de notre
            # nom de fichier ( module_file ).
            #
            module_name = self.files.node(module_file).stem

        self.logItem = None
        self.logItem = self.on_ouvre_le_journal(module_name)
        self.files.register_log(self.logItem)

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

        self.nb_parameters_in = self.on_se_presente(module_file, arguments)

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
        #       - EXE_txt_editor,
        #       - EXE_(..),
        #       - DIR_(..),
        #       - DLL_(..),
        #       - ARG_(..),
        #       - NOD_(..).
        #
        # Il est aussi possible de se servir de ce dictionnaire pour conserver des
        # paramètres généraux du programme, tels que ceux par exemple lus dans une
        # section 'GENERAL SETTINGS' d'un fichiers de configuration. Les entrées
        # suivantes sont ainsi aussi possibles :
        #       - shutdown_TYPE.
        #
        # ( ! ) ATTENTION ( ! ) : Choix a été fait de stocker dans ce dictionnaire
        # des variables telles que renvoyées par :
        #
        #       ScriptSkeleton.files.node()
        #
        # ... i.e :
        #
        #       des variables de type _FileSystemLeaf ou pathlib.Path
        #
        # ... par convention, ces variables ont pour clés :
        #
        #       NOD_(..)
        #
        # ... or un appel subséquent à :
        #
        #       ScriptSkeleton.file_system_mode()
        #
        # ... pourrait changer le type de ces variables, et donc occasionnerait
        # des BUGS ( !!! )
        #
        # Nous convertissons pour autant le dictionnaire « paths_and_miscellaneous » 
        # afin d'éviter cela. Cette conversion est réalisée directement dans notre
        # méthode file_system_mode().
        #
        # Pour autant, le script qui nous utilise pourrait avoir lui-même conservé
        # de telles variables par ailleurs, et ne pourrait-il alors planter par la
        # suite, dans des cas à la marge ( ??? ) :
        #
        #       - exemple : tentative de comparaison de 2 de ces objets alors que
        # leur type serait différent.
        #
        #       - exemple : tentative de concaténation de 2 paths alors que leur
        # type serait différent.
        #
        # ( !!! ) PRUDENCE DONC LORSQUE L'ON CONSERVE UNE VALEUR DU TYPE :
        #
        #        ScriptSkeleton.file_system_mode()
        #
        # Cependant, à part ces cas à la marge :
        #
        #       _FileSystemLeaf & pathlib.Path PEUVENT COHABITER DANS 1 MÊME SCRIPT
        #
        # ... en effet, ces objets sont plutôt utilisés pour accéder aux noeuds
        # du système de gestion de fichiers eux-mêmes, via leurs méthodes, et ce
        # afin d'en obtenir des informations.
        #
        self.shutdown_dflt = shutdown_none

        self.paths_and_miscellaneous = {}

        self.set_paths_and_miscellaneous()


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


    def search_path_from_masks(
        self,
        root,           # _FileSystemLeaf, pathlib.Path
        masks,          # iterable, iterator, generator
        ) -> (
            object,     # _FileSystemLeaf, pathlib.Path
            os.PathLike # chemin du fichier recherché
        ):
        """ Cette fonction permet de rechercher un fichier ( une DLL ou
        un exécutable par exemple ) à partir d'une certaine localisation
        et en cheminant le long d'un chemin indiqué par des masques.

        Par exemple, pour trouver EditPadPro?.exe, à partir du répertoire
        « Program Files », nous aurons comme paramètres :

            root = r"C:\Program Files"
            masks = ( 'Just*Great*Software', 'EditPad*Pro*', 'EditPadPro*.exe' )

        Puisque plusieurs versions de EditPad Pro peuvent être présentes
        sur une même machine, cette façon de faire trouvera :

            C:\Program Files\Just Great Software\EditPad Pro 8\EditPadPro8.exe
            C:\Program Files\Just-Great-Software\EditPadPro 7\EditPadPro7.exe
            C:\Program Files\Just_Great_Software\EditPadPro6\EditPadPro6.exe
            ...

        Puisque nous parcourons l'arborescence en ordre décroissant, et
        car nous stoppons au 1er fichier trouvé, search_path_from_masks()
        répondra alors :

            C:\Program Files\Just Great Software\EditPad Pro 8\EditPadPro8.exe

        :param root: la racine à partir de laquelle nous devons débuter
        nos recherches.

        :param masks: une suite de valeurs (toutes au format STRING )
        décrivant le cheminement dont nous pensons qu'il peut nous mener
        depuis « root » au fichier recherché. La dernière de ces valeurs
        doit expliciter le nom du fichier cherché. Ainsi :

            ( 'Libre*Office*', '*program*', 's*office.exe' )

        :return: un t-uple contenant 2 valeurs =

                - l'objet répertoire contenant le fichier trouvé ( objet
                de type _FileSystemLeaf ou pathlib.Path ).

                - le chemin complet du fichier recherché.
        """

        log = self.logItem
        leaf = self.files.node
        last_level = ( len(masks) == 1 )

        # On recherche le premier masque dans la racine, car il faut bien
        # commencer nos recherches qq part !!!
        #
        # Pour chacun des noeuds dont le nom correspond à ce masque, nous
        # allons en explorer l'arborescence.
        #
        for n in sorted(root.glob(masks[0]), reverse = True):

            # « n » est de type STRING ou PATHLIB.PATH.
            #
            log.debug('')
            log.debug('NOEUD TESTÉ = %s', n)
            log.debug('')

            # S'il n'y a qu'un seul masque dans la liste, nous comprenons
            # qu'il s'agit d'un masque de fichier... Nous cherchons alors
            # s'il existe dans « root » un fichier correspondant au masque
            # recherché.
            #
            if last_level:

                if leaf(n).is_file():
                    # Nous avons trouvé le 1er fichier qui correspond à
                    # notre recherche : comme nous avons trié en ordre
                    # décroissant, on peut espérer qu'il s'agit de la
                    # version la plus récente...
                    #
                    log.debug('Répertoire retenu = %s', root)
                    log.debug('Fichier retenu = %s', n)

                    return root, n

            # Sinon, on parcourt les répertoires dont le nom commence par
            # le masque voulu...
            #
            # On descend ainsi dans l'arborescence, on met donc le premier
            # masque de côté, et on examine les suivants.
            #
            else:

                dir, exe = self.search_path_from_masks(root / n, masks[1:])

                if exe is not None:
                    # Si la recherche dans l'arborescence a trouvé une
                    # valeur, nous la retournons.
                    #
                    return dir, exe

        return None, None


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
            printer(f'\t{type(value)}')
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
        leaf = self.files.node

        for key, value in self.paths_and_miscellaneous.items():

            if value is None:
                pass

            else:
                name = None
                key_short = key[0:4]

                if key_short in ('DIR_', 'EXE_', 'DLL_'):

                    printer(f"Test de l'existence de {key}...")
                    node = leaf(value)

                    # Nous testons différemment chaque type de noeuds du
                    # système de fichiers afin de pouvoir adapter le msg
                    # d'erreur potentiel.
                    #
                    # En effet, nous pourrions écrire plus simplement :
                    #
                    #   if not node.exists():
                    #       name = 'noeud'
                    #
                    if key_short == 'DIR_' and not node.is_dir():
                        name = 'répertoire'

                    elif key_short == 'EXE_' and not node.is_file():
                        name = 'fichier'

                    elif key_short == 'DLL_' and not node.is_file():
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
        directory: str = None,
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
        leaf = self.files.node

        os_dir = None
        os_node = None
        l_office_exe = None
        l_writer_exe = None
        exe_txt_editor = None

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

        # Les modules optionnels sont-ils chargés ?
        #
        self.paths_and_miscellaneous['walking_MODE'] = str(self.files.walking_mode)
        self.paths_and_miscellaneous['module_PATHLIB'] = str(pathlib)
        self.paths_and_miscellaneous['module_FNMATCH'] = str(fnmatch)
        self.paths_and_miscellaneous['module_GLOB'] = str(glob)

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
        if directory is None or not leaf(directory).is_dir():
            working_node = self.files.cwd()
        else:
            working_node = leaf(directory)

        working_path = str(working_node)

        self.paths_and_miscellaneous['NOD_working'] = working_node
        self.paths_and_miscellaneous['working_PATH_FULL'] = working_path

        # Avant étaient utilisées les 2 instructions ci-dessous :
        #
        #   directories_and_files['working_PATH_DSK_ONLY'] = working_path[0:2]
        #   directories_and_files['working_PATH_DIRS_ONLY'] = working_path[3:]
        #
        # Ensuite, on est passé à os.path.splitdrive, pour être plus PORTABLE :
        #
        #   (path_drive, path_tail) = os.path.splitdrive(working_path)
        #   self.paths_and_miscellaneous['working_PATH_DSK_ONLY'] = path_drive
        #   self.paths_and_miscellaneous['working_PATH_DIRS_ONLY'] = path_tail
        #
        # Puis l'on est passé à l'utilisation de notre classe FileSystemTree,
        # et l'on a alors supprimé l'affectation relative au « path_tail » car
        # « working_PATH_DIRS_ONLY » n'était utilisé nulle part et car cette
        # donnée / attribut n'est pas présente dans le module PATHLIB !!!
        #
        self.paths_and_miscellaneous[
            'working_PATH_DSK_ONLY'
            ] = working_node.drive

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

            os_dir = os.environ['SYSTEMROOT']
            os_node = leaf(os_dir)
            programs = leaf(r"C:\Program Files")

            # On recherche le répertoire de LibreOffice.
            #
            log.debug("Recherche de LIBRE OFFICE :")
            log.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~")

            # Description du cheminement dont nous pensons qu'il peut nous
            # mener depuis « Program Files » à l'exécutable de LibreOffice.
            #
            masks = ( "Libre*Office*", "program", "soffice.exe" )

            dir, exe = self.search_path_from_masks(programs, masks)

            if exe is not None:
                l_office_exe = str(exe)
                l_writer_exe = str(dir / "swriter.exe")

            log.debug('')

            # « Edit Pad Pro » peut être "rangé" / installé dans plusieurs
            # répertoires différents suivant les machines, suivant que j'ai
            # utilisé le répertoire par défaut lors de l'installation, ou
            # que j'ai pensé à modifier ce répertoire ( pour coller à mon
            # ancienne habitude... ).
            #
            # Le mieux serait ici de lire dans le registre Windows l'endroit
            # où se trouve Edit Pad Pro !!!
            #
            # Cela dit, il peut y avoir plusieurs version d'EditPad Pro
            # hébergées sur une même machine...
            #
            # AVANT nous utilisions 2 listes pour retrouver « Edit Pad Pro »
            # ( une infâme verrue en fait... ), 2 listes que nous parcourions
            # l'une après l'autre, via 2 boucles « for » :
            #
            #   editpad_dir_list = [
            #       # On liste ici les différents répertoires possibles, par ordre
            #       # de la version la plus récente ( préférée ) à la plus ancienne.
            #       #
            #       r"C:\Program Files\Just Great Software\EditPad Pro",
            #       r"C:\Program Files\EditPad Pro",
            #       r"C:\Program Files\EditPadPro",
            #       r"C:\Program Files\Just Great Software\EditPad Pro 8",
            #       r"C:\Program Files\EditPad Pro 8",
            #       r"C:\Program Files\EditPadPro8",
            #       r"C:\Program Files\Just Great Software\EditPad Pro 7",
            #       (..)
            #   ]
            #
            #   editpad_exe_list = [
            #       # On liste ici les différents exécutables possibles, par ordre
            #       # de la version la plus récente ( préférée ) à la plus ancienne.
            #       #
            #       'EditPadPro8.exe',
            #       'EditPadPro7.exe',
            #       (..)
            #   ]
            #
            # PUIS la méthode search_path_from_masks() a été écrite et cela
            # a simplifié la recherche...
            #
            log.debug("Recherche de EDIT PAD PRO : dans « Just*Great*Software* »")
            log.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~")

            # Description du cheminement dont nous pensons qu'il peut nous
            # mener depuis « Program Files » à l'exécutable de Edit Pad Pro.
            #
            masks = ( "Just*Great*Software*", "Edit*Pad*Pro*", "Edit*Pad*Pro*.exe" )

            _, exe = self.search_path_from_masks(programs, masks)

            if exe is None:
                # En cas d'échec, nous testons un chemin alternatif : il se peut
                # que le sous-répertoire soit directement dans « Program Files ».
                #
                log.debug('')
                log.debug("Recherche de EDIT PAD PRO : dans « Program Files »")
                log.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~")

                _, exe = self.search_path_from_masks(programs, masks[1:])

            if exe is None:
                # Si l'on n'a pas trouvé EditPadPro, on se rabat sur Notepad.
                #
                log.debug('')
                log.debug("Recherche de EDIT PAD PRO : ÉCHEC")
                log.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                log.debug('Fichier retenu = %s', exe)

                exe = str(os_node / 'notepad.exe')

            log.debug('')
            exe_txt_editor = exe

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
                player_exe = str(os_node / 'System32' / 'mplay32.exe')
                player_arg = ['/play', '/close']
                played = str(os_node / 'Media' / 'Windows XP Battery Low.wav')

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
            player_exe = None
            player_arg = None
            played = None


        #
        ###########################################################
        ########## CLÔTURE de notre INITIALISATION ################
        ###########################################################
        #


        self.paths_and_miscellaneous['DIR_os'] = os_dir
        self.paths_and_miscellaneous['NOD_os'] = os_node

        self.paths_and_miscellaneous['EXE_txt_editor'] = exe_txt_editor

        self.paths_and_miscellaneous['EXE_libre_office'] = l_office_exe
        self.paths_and_miscellaneous['EXE_libre_writer'] = l_writer_exe

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
        directory: str = None,
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
            if directory is None or not self.files.node(directory).is_dir():
                directory = str(self.files.cwd())

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
        short_name = self.files.node(module_file).stem

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
            myLogFile = self.files.node(self._logFile)

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
                if log_to_remove and myLogFile.is_file():

                    self.shw_debug('Destruction du LOG même sous IDLE.')
                    self.shw_debug('')

                    myLogFile.unlink()

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
                if log_to_remove and myLogFile.is_file():

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
                if log_to_remove and myLogFile.is_file():

                    myLogFile.unlink()

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
                # ... provoquera une exception !!!
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

            answer = input(prompt).lower()
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
    
        :param default_choice: index du choix par défaut. Cette valeur doit être fixée
        à -1 si aucun choix par défaut n'est défini.
    
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


    def file_system_mode(
        self,
        walking_mode: str = walking_via_listdir,
        with_pathlib: str = pathlib_ignore,
        with_fnmatch: bool = False,
        with_glob: bool = False
        ):
        """
        Cette méthode permet de modifier le fonctionnement interne
        de ScriptSkeleton i-e notre gestion de fichiers va-t-elle
        s'appuyer sur la librairie OS.PATH seule, ou plutôt sur les
        modules PATHLIB, FNMATCH et GLOB ?

        :param walking_mode: si ce « squelette » n'utilise que le
        module OS.PATH, pour parcourir 1 répertoire utilisera-t-il
        la fct os.listdir() ou os.scandir() ?

            * walking_via_listdir : os.listdir() utilisée.

            * walking_via_scandir : os.scandir() utilisée.

            * walking_ignore : peu importe ( cas où un autre module
            que OS.PATH est utilisé pour gérer les fichiers... ) et
            si nous arrivons tout de même dans une partie de code
            utilisant cette information, la méthode par défaut ( ie
            os.listdir() sera utilisée ).

            RQ = Si les modules GLOB ou FNMATCH sont importés, cela
            n'impose pas le walking_mode et il faut le spécifier !

            RQ = Cf FileSystemTree._FileSystemLeaf.iterdir()

        :param with_pathlib: ce « squelette » va-t-il s'appuyer sur
        le module PATHLIB, ou simplement se servir de la librairie
        OS.PATH ? Valeurs possibles :

            * pathlib_ignore ( None ) : pas de module PATHLIB.

            * pathlib_direct : module PATHLIB sans filtre.

            * pathlib_deeply : module PATHLIB incorporé.

        :param with_fnmatch: ce « squelette » va-t-il s'appuyer sur
        le module FNMATCH ?

        :param with_glob: ce « squelette » va-t-il s'appuyer sur le
        module GLOB ?
        """

        log = self.logItem
        tree_old = self.files

        # Si l'un des paramètres a changé, on recréé l'objet qui nous
        # permet d'accéder à la gestion des répertoires et fichiers.
        #
        if (tree_old.walking_mode == walking_mode) \
            and (tree_old.with_pathlib == with_pathlib) \
            and (tree_old.with_fnmatch == with_fnmatch) \
            and (tree_old.with_glob == with_glob):
            #
            # Rien n'a changé donc rien à faire !!!
            #
            log.debug("Configuration de la GESTION des FICHIERS :")
            log.debug('==========================================')
            log.debug("\tAUCUN des paramètres n'a été modifié.")
            log.debug('\tDonc pas de changement dans la gestion')
            log.debug('\t...... des répertoires et fichiers !!!')
            log.debug('')

        else:
            # On créé un nouvel objet de gestion des noeuds de notre
            # système de fichiers.
            #
            node_type_old = type(tree_old.node())

            self.files = FileSystemTree(
                walking_mode = walking_mode,
                with_pathlib = with_pathlib,
                with_fnmatch = with_fnmatch,
                with_glob = with_glob,
                log = log
                )

            # Si l'on a changé le type de stockage de la description
            # des noeuds de notre système de fichier ( pathlib.Path
            # vs _FileSystemLeaf ) alors nous convertissons dans le
            # dictionnaire « paths_and_miscellaneous » les valeurs
            # qui en auraient besoin !!!
            #
            #   Cf « ( ! ) ATTENTION ( ! ) : Choix a été fait de stocker »
            #
            tree_new = self.files
            node_type_new = type(tree_new.node())

            if node_type_new != node_type_old:

                log.critical('')
                log.critical("\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                log.critical("\tMODIFICATION DU TYPE DES NOEUDS !!!")
                log.critical("\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                log.critical("\t... = ATTENTION AUX EFFETS DE BORDS")
                log.critical('')

                my_dict = self.paths_and_miscellaneous

                for key, value in my_dict.items():
                    if type(value) == node_type_old:
                        log.critical("\tConversion de « %s »...", key)
                        my_dict[key] = tree_new.node(str(value))

                log.critical("\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                log.critical('')
                log.critical('')


    def search_files_from_a_mask(
        self,
        #directory: os.PathLike = None,
        directory: object = None,
        mask: str = '*'
        ) -> list:
    	# -> list( STR ) [ ou ] list( PATHLIB.PATH )
        """ Cherche dans un répertoire tous les FICHIERS qui
        correspondent à un certain masque.

        :param directory: le répertoire à explorer, au format
        STRING, PATHLIB.PATH, voire _FileSystemLeaf....

        :param mask: le masque de recherche, qui peut contenir
        des « wildcards ». Ces wildcards sont soit ceux compris
        par pathlib.glob(), glob.glob() ou fnmatch.filter(), soit
        ceux compris par la méthode _FileSystemLeaf._fake_iglob().
        Dans ce dernier cas, les masques de recherche interprétés
        sont :

            - « * » : tous les fichiers.

            - « *.xxx » : les fichiers d'un certain type.

            - « title*.m* » : masque plus complexe.

        Dans les autres cas ( i-e lorsque nous avons importé les
        modules GLOB ou FNMATCH ou PATHLIB ), cf :

            Cf https://docs.python.org/3/library/glob.html#glob.glob
            Cf https://docs.python.org/3/library/fnmatch.html#fnmatch.filter
            Cf https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob
        
        :return: la liste des chemins des fichiers trouvés, au
        format STRING ou PATHLIB.PATH, et ces fichiers seront
        exprimés via un PATH ABSOLU.

        ATTENTION : search_files_from_a_mask() ne renvoie QUE
        des fichiers, tout répertoire est écarté du résultat !

        ATTENTION : Si notre objet ScriptSkeleton est configuré
        afin d'utiliser le module PATHLIB ( cf notre propriété
        « with_pathlib » ) alors la liste en retour contiendra
        des valeurs de type PATHLIB.PATH, sinon les valeurs de
        la liste seront de type STRING !!!

            Lorsqu'il s'agit de STRINGS, nous nous assurons que
            les valeurs retournées soient des PATHS ABSOLUS.

            Si les données retournées sont de type PATHLIB.PATH,
            les valeurs retournées seront également de type PATH
            ABSOLU ( obtenues via leur méthode « resolve » ).
        """

        log = self.logItem
        leaf = self.files.node

        if directory is None:

            log.debug('Pas de répertoire de recherche indiqué.')
            log.debug('Donc ce sera le répertoire de travail.')

            # On n'appelle pas ici get_paths_and_miscellaneous()
            # car on sait que 'working_PATH_FULL' est toujours
            # défini à ce stade...
            #
            dir_n = self.paths_and_miscellaneous['NOD_working']

        else:
            dir_n = leaf(directory)

        log.debug('Recherche de fichiers dans : %s.', dir_n)

        # Nous imposons que le retour de notre fonction soit
        # une liste.
        #
        # En effet, si « self.with_pathlib == pathlib_direct » :
        #
        #   self.files.node(directory).glob(mask)
        #   = < pathlib.Path >.glob(mask)
        #   = un itérateur !!!
        #
        # En effet, sous Python IDLE :
        #
        #   import pathlib
        #   lst = pathlib.Path('.').glob('*')
        #   type(lst)
        #
        # -> result = <class 'generator'>
        #
        # ... Donc, si notre appelant s'attend à avoir 1 liste
        # qu'il puisse réutiliser, alors il sera très surpris
        # puisqu'une fois parcourue, cette liste deviendra vide
        # ( propriété des itérateurs qui ne conservent pas leurs
        # valeurs et ne peuvent donc les afficher qu'une fois et
        # une seule ) !!! 
        #
        # Ainsi, sous IDLE :
        #
        #   for i in lst: print(i)
    	#
        # -> result =
    	#	skeleton { SRC }.py
    	#	skeleton.py
    	#
    	# ... puis :
    	#
        #	list(lst)
    	#
        # -> result = []
    	#
    	# Donc lorsque nous parcourons la liste, cela la vide !!!
    	# Ce qui est bien le principe des itérateurs / générateurs.
	    #
        # D'où la syntaxe :
        #
        #   return list(self.files.node(directory).glob(mask))
        #
        # RQ : Depuis qu'1 compréhension de liste est utilisée,
        # la syntaxe ci-dessus a disparu puisqu'1 compréhension
        # fournit 1 liste en retour ( que sa syntaxe soit basée
        # sur une liste ou sur un itérateur !!! ).
        #
        # RQ : Depuis, < _FileSystemLeaf >.glob s'est mise aussi
        # à renvoyer un itérateur ou générateur en retour ( et
        # seulement cela ) et dans aucun cas une liste, ce qui
        # justifie d'autant plus que nous transformions ceci
        # en liste au regard de ce qu'attend notre appelant...
        #
        #
        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #   !!! EXEMPLE D'UTILISATION D'UNE COMPRÉHENSION DE LISTE !!!
        #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        #
        only_files = [
            #
            # Nous utilisons une « compréhension de liste » pour
            # écarter tout répertoire du résultat. En effet, nous
            # ne souhaitons conserver que les fichiers.
            #
            # node(directory).glob(mask) renvoie en effet autant
            # des fichiers que des répertoires, puisque c'est le
            # cas de :
            #
            #   . pathlib.glob()
            #   . fnmatch.filter()
            #   . glob.iglob()
            #   . glob.glob()
            #
            # ... qui ne font pas le distingo entre les fichiers
            # et les répertoires !!!
            #
            # Cf :
            #
            #   . https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob
            #   . https://docs.python.org/3/library/fnmatch.html#fnmatch.filter
            #   . https://docs.python.org/3/library/glob.html#glob.iglob
            #   . https://docs.python.org/3/library/glob.html#glob.glob
            #
            # Seule la fonction < _FileSystemLeaf >._fake_iglob()
            # permet d'indiquer si l'on veut récupérer tous les
            # noeuds, les répertoires seuls, ou seulement les
            # fichiers.
            #
            # Par ailleurs, nous voulons être sûrs de ne fournir
            # que des paths ABSOLUS, d'où l'utilisation de la fct
            # os.path.abspath() qui accepte en entrée autant des
            # STRING que des pathlib.PATH. Ainsi, sous IDLE :
            #
            #   os.path.abspath('.')
            # > 'K:\\_Know\\Info\\Dvpt\\Réalisation\\Src\\_Python\\[ skeleton ]'
            #
            #   pathlib.Path('.')
            # > WindowsPath('.')
            #
            #   os.path.abspath(pathlib.Path('.'))
            # > 'K:\\_Know\\Info\\Dvpt\\Réalisation\\Src\\_Python\\[ skeleton ]'
            #
            # La formule est donc devenue :
            #
            #   [ os.path.abspath(n)
            #       for n in node(directory).glob(mask) \
            #       if node(n).is_file() ]
            #
            # RQ : < FileSystemTree >.node() fournit des STRINGS
            # ou des objets de type PATHLIB.PATH.
            #
            # Par la suite, pour une formulation respectueuse
            # des différents types possibles, nous avons choisi
            # d'écrire :
            #
            #   [ os.path.abspath(n) if type(n) == str else n.resolve() \
            #     for n in node(directory).glob(mask) if node(n).is_file() ]
            #
            # On peut en effet tester les expresions suivantes
            # sous IDLE :
            #
            #   [ os.path.abspath(n) if type(n) == str else n.resolve() \
            #     for n in pathlib.Path().glob('*') if n.is_file() ]
            #
            #   [ os.path.abspath(n) if type(n) == str else n.resolve() \
            #     for n in glob.glob('*') if os.path.isfile(n) ]
            #
            # Cela a considérablement alourdi la syntaxe, mais
            # c'est à visée didactique.
            #
            os.path.abspath(n) if type(n) == str else n.resolve()
                for n in dir_n.glob(mask) \
                if leaf(n).is_file()
            ]
        return only_files


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

        :param *args: tuple des fichiers à convertir, dont les
        path seront du type STRING ou PATHLIB.PATH....

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
                    str(file_in)
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

        :param *args: tuple des fichiers à éditer, dont les
        path seront du type STRING, PATHLIB.PATH, voire même
        _FileSystemLeaf....

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
                command_line = [exe_txt_editor, str(file_to_edit)]

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

        :param *args: tuple des fichiers à comparer, dont les
        path seront du type STRING ou PATHLIB.PATH....

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
        with open(str(args[0]), flag) as file1:

            with open(str(args[1]), flag) as file2:

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
        #filename: str,
        pattern: object,       # _FileSystemLeaf [ ou ] os.PathLike
        file_ext: str = None,
        idx_size: int = 3,
        idx_start: int = 0,
        idx_force: bool = True
	    ) -> str:
        """ Permet de trouver un nom de fichier disponible, similaire
        au « pattern » fourni, avec l'extension demandée.

        ATTENTION : pattern contient un nom ( « basename » ) de fichier
        AVEC OU SANS extension. L'extension cible ( « ext » ) sera, elle,
        lue dans « file_ext ».

        ATTENTION : si « file_ext » n'est pas fournie ( None ) alors nous
        reprendrons l'extension de « pattern ». Par ailleurs, si nous est
        fournie la chaîne vide ( « file_ext = '' » ) alors le fichier n'
        aura aucune extension.

        Quand « basename.ext » n'existe pas, nous renvoyons ce nom ( sauf
        si idx_force = True ).

        Sinon, nous renvoyons le 1er nom de fichier disponible du type :

            « basename - 0###.ext » où ### est un entier.

        :param pattern: le modèle de nom ( AVEC OU SANS EXTENSION ).

        :param idx_size: le nombre minimum de caractères dont doit être
        composé l'index ajouté ( s'il existe ). Par exemple, si idx_size
        vaut 2, nous aurons possiblement à minima en sortie =

            « basename - 00.ext »
            ( si « basename.ext » existe ou « idx_force = True » ).

        :param idx_start: faut-il commencer notre recherche de suffixe
        à 0, à 1, ... ? C-a-d « basename - 0.ext » conviendrait-il ?
        Ou faut-il « basename - 1.ext » à minima ? ...

        :param idx_force: faut-il ou pas forcément ajouter un index
        à « basename » ? Si non, on pourra renvoyer « basename.ext »
        en sortie. Si oui, nous aurons à minima en sortie un nom du
        type « basename - #.ext »

        :return: le nom de fichier désiré.
        """

        leaf = self.files.node

        # Quel que soit le type en entrée ( STRING, pathlib.Path, ... )
        # l'appel ci-dessous construit un objet fichier.
        #
        node = leaf(pattern)
        ext = node.suffix if file_ext is None else file_ext
        alt_node = node.with_suffix(ext)

        # Si le fichier existe, ou si l'on veut absolument qu'un nom
        # de fichier avec index soit renvoyé, alors nous construisons
        # ce nom...
        #
        # ( Sinon le nom qui nous a été fourni est celui recherché ! )
        #
        if idx_force or alt_node.exists():

            # Nous sommes ici dans le cas où nous devons construire un
            # nom de fichier alternatif ( ie le fichier existe déjà ou
            # cela nous est demandé d'une façon impérative ).
            #
            # RQ : Nous sommes obligés de doubler les accolades ( {{ et
            # }} ) ci-dessous dans la définition de format_mask afin de
            # signifier à cette F-STRING que nous voulons le caractère
            # spécial accolade en tant que tel ( et que ce n'est pas un
            # nom de variable qui va être inclus entre accolades à cet
            # endroit )... La F-STRING ne va donc interpréter que la
            # partie {idx_size}.
            #
            format_mask = f' - {{:0{idx_size}d}}'

            # Nous aurions pu écrire ci-dessous :
            #
            #   next = lambda x: alt_node.with_stem(base + x)
            #
            # mais PurePath.with_stem(stem) n'existe que depuis Python
            # version 3.9...
            #
            # Cf https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.with_stem
            #
            base = node.stem
            next = lambda x: node.with_name(base + x).with_suffix(ext)

            suffix_n = idx_start

            while True:

                # Nous construisons d'abord le suffix sous format de
                # chaîne.
                #
                # Puis nous ajoutons ce suffixe au nom de fichier.
                #
                # Nous avons séparé cette opération en deux ( nous
                # aurions pu utiliser .format pour tout faire en une
                # seule fois ) car basename peut contenir « { » ou
                # « } » ( ce qui ferait planter .format !!! ).
                #
                # Il aurait probablement été possible de réaliser
                # cette concaténation en une fois via une F-STRING,
                # mais c'est beaucoup moins lisible...
                #
                suffix = format_mask.format(suffix_n)
                alt_node = next(suffix)

                if not alt_node.exists():
                    break

                suffix_n += 1

        # Nous retournons le nom de fichier qui convient.
        #
        return str(alt_node)


    def save_strings_to_file(
        self,
        *args,
        #destination: os.PathLike,
        destination: object,       # _FileSystemLeaf [ ou ] os.PathLike
        ok_to_erase: bool = False,
        ask_confirm: bool = True,
        must_be_new: bool = False,
        new_suffix: str = ' { new version }',
        data_type: str = None,
        data_fmt: str = coding_default,
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

        :param data_type: quel est le type du contenu
        que nous devons sauvegarder dans le fichier ?
        ( HTML, JSON, ... ou None )

        :param data_fmt: quel est le jeu de caractères
        du fichier à créer ? Cela nous permet surtout
        de savoir s'il faut créer un fichier « byte »
        ou un fichier texte...

        :return: le nom du fichier créé (au cas où nous
        ayions dû bâtir un nouveau nom...).
        """

        log = self.logItem
        node = self.files.node(destination)
        new_name = node.exists()

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
            tmp_dst = node.stem + new_suffix + node.suffix

            file_dst = self.get_unused_filename(
                tmp_dst,
                idx_force = True
                )

        else:

            # On peut se servir tel quel du nom de fichier
            # qui nous a été fourni.
            #
            file_dst = str(destination)

        if (data_fmt is None) or (data_fmt == coding_bytes):

            # Le jeu de caractères qui nous concerne est
            # celui des « byte strings ». Donc on ouvre
            # notre fichier au format « b(yte) ».
            #
            f_actual = 'BYTES'
            f_other = 'TEXTE'
            f_flag = 'wb'

        else:

            # On ouvre notre fichier au format « t(ext) ».
            #
            f_actual = 'TEXTE'
            f_other = 'BYTES'
            f_flag = 'wt'

        log.debug('Format en entrée = « %s »', data_fmt)
        log.debug('Format en sortie = « %s »', f_flag)
        log.debug('')

        self.shw(f'Destination = {file_dst}')
        self.shw_debug(f'Format = « {f_flag} »')
        self.shw('')

        with open(file_dst, f_flag) as new_file:

            for content in args:

                if f_flag == 'wt' \
                    and data_type is not None \
                    and 'json' in data_type.lower():

                    log.debug("Fichier destination format TEXTE")
                    log.debug("+ Contenu à écrire format JSON")
                    log.debug("= Nous utilisons le module JSON.")
                    log.debug('')

                    # Nous utilisons le module JSON si le contenu à écrire est
                    # de type JSON ( en espérant que le traitement soit ainsi
                    # accéléré ).
                    #
                    # Par contre, ce module JSON ne sait traiter que des datas
                    # au format TXT...
                    #
                    # Cf https://docs.python.org/fr/3/library/json.html#basic-usage :
                    #
                    #   json.dump(obj, fp, [..]
                    #   Le module json produit toujours des objets str, et non
                    #   des objets bytes. fp.write() doit ainsi prendre en charge
                    #   un objet str en entrée.
                    #
                    json.dump(content, new_file)

                else: 
                    try:
                        new_file.write(content)

                    except UnicodeEncodeError as erreur:
                        # Exception qui se rencontre par exemple si l'on essaye
                        # d'écrire dans un fichier TXT ( « wt » ) le caractère
                        # '\U0001f496' ( ou SPARKLING HEART c-a-d ❤️ ) qui est,
                        # pourtant, Unicode !!!
                        #
                        # Il suffit d'exécuter sous IDLE le code suivant pour
                        # s'en rendre compte :
                        #
                        #        with open('tmp.txt', 'wt') as f:
                        #            c = '❤'     # ou « c = '\U0001f496' »
                        #            try:
                        #                f.write(c)
                        #            except UnicodeEncodeError:
                        #                print('Caractère NON UNICODE rencontré.')
                        #            else:
                        #                print('Tout va bien.')
                        #            finally:
                        #                print('FIN !!!')
                        #
                        # Cf aussi les remarques concernant :
                        #
                        #       'https://jsonplaceholder.typicode.com/'
                        #
                        # ... dans nos « AUTOTESTS de REQUÊTES HTTP ».
                        #
                        self.shw("\t\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        self.shw("\t\tATTENTION = ERREUR À L'ENREGISTREMENT")
                        self.shw("\t\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        self.shw('')
                        self.shw(f"\t« {erreur} »")
                        self.shw('')
                        self.shw("\tCaractère NON UNICODE rencontré à l'enregistrement.")
                        self.shw("\tUne partie du contenu sera ignorée, non sauvegardée.")
                        self.shw('')

                        log.debug("\tNous ne prenons pas le risque de logger ce contenu")
                        log.debug("\t... qui pourrait faire planter le module de LOG !!!")
                        log.debug('')

                        if ___debug___:
                            # Nous allons sauvegarder la pile d'exécution.
                            #
                            # Pour cela, nous la découpons en lignes afin
                            # d'en améliorer la présentation.
                            #
                            traceback_string = traceback.format_exc()
                            trace_lines = traceback_string.rstrip(whitespace).split('\n')

                            log.debug("\tNous journalisons toutefois la trace d'exécution :")
                            log.debug('')
                            for line in trace_lines:
                                if line != '':
                                    log.debug("\t\t%s", line)
                            log.debug('')

                        self.shw(f"\tCodage actuel pour écriture dans le fichier = « {f_actual} ».")
                        self.shw(f"\tNe faudrait-il pas plutôt utiliser le format « {f_other} » ?")
                        self.shw('')

        return file_dst


# ---------------------------------------------------------------------------
#
#   PARTIE :
#   ~~~~~~~~
#   Fonctions spécifiques au WEB ( browser, HTML, HTTP, etc ).
#
# ---------------------------------------------------------------------------


    # Caractères interdits dans les URL, ainsi que leur transcription.
    #
    # Pour une liste des caractères qui devraient être présents dans
    # ce dictionnaire, cf :
    #
    #   https://en.wikipedia.org/wiki/URL_encoding
    #
    _url_forbiddens = {
        ' ': '%20',
        #
        # Sous Firefox, lorsque l'on écrit une URL avec un « ! », ce dernier n'est
        # pas transformé par le browser. Ainsi :
        #
        #   https://www.google.com/search?q=( ! )
        #
        # ... devient :
        #
        #   https://www.google.com/search?q=(%20!%20)
        #
        # ... donc nous ne transformons pas non plus « ! ».
        #
        # ATTENTION : Après l'avoir saisie, lorsque l'on observe la première URL ci-
        # dessus dans la barre d'adresses de Firefox, on lit « ( ! ) » mais si l'on
        # copy / paste cette URL du browser vers un éditeur de texte, apparaît alors
        # « (%20!%20) ». L'URL a donc bien été modifiée.
        #
#       '!': '%21',
        '"': '%22',
        #
        # Le caractère suivant « # » permet de donner des indications dans certaines
        # URL : il ne faut donc pas le traduire !!! Ainsi, cf :
        #
        #   https://mybox.airfrance.fr/MyBoxWeb/accueil.do#toRead
        #
#       '#': '%23',
        '$': '%24',
        #
        # Le caractère « % » permet de coder les caractères spéciaux dans les URL :
        # il ne faut donc pas le traduire !!! Ainsi, cf :
        #
        #   https://fr.search.yahoo.com/search?p=dei%20cas
        #
#       '%': '%25',
        #
        # Le caractère suivant « & » est parfois utilisé dans les URL pour, par
        # exemple, indiquer une recherche :
        #
        #   https://www.google.com/search?client=firefox-b-d&q=test
        #
#       '&': '%26',
        "'": '%27',
        #
        # Pour « ( » et « ) », cf les remarques ci-dessus relatives à « ! ».
        #
#       '(': '%28',
#       ')': '%29',
        '*': '%2A',
        '+': '%2B',
        ',': '%2C',
        #
        # Certains caractères sont parties intégrantes d'une adresse web... !!!
        # Donc mieux vaut ne pas les traiter, sinon l'URL sera incompréhensible
        # lors de sa lecture. C'est le cas de « / » et « : » i.e « https:// ».
        #
#       '/': '%2F',
#       ':': '%3A',
        ';': '%3B',
        #
        # Tout comme « & » ci-dessus, les caractères suivants « = » et « ? » font
        # partie du langage parfois utilisé dans les URL pour une recherche.
        #
#       '=': '%3D',
#       '?': '%3F',
        '@': '%40',
        '[': '%5B',
        ']': '%5D',
        #
        # Le caractère « \ » peut être utilisé dans des requêtes, cf :
        #
        #   https://www.google.com/search?q=\U0001f496
        #   https://www.google.com/search?q=%5CU0001f496
        #   = Emoji Unicode Character 'SPARKLING HEART' (U+1F496)
        #
        # ... donc nous l'avons ajouté au dictionnaire alors qu'il ne se trouve
        # pas dans la table « Reserved characters after percent-encoding » de :
        #
        #   https://en.wikipedia.org/wiki/URL_encoding
        #
        # Il se trouve par contre dans la table :
        #
        #   « Common characters after percent-encoding (ASCII or UTF-8 based)  »
        #
        # ... de cette même page.
        #
        '\\': '%5C',        
    }


    def url_to_valid(
        self,
        url: str
        ) -> str:
        """ S'assure qu'une URL soit valide, i.e ne comporte pas de caractères
        interdits, et renvoie si nécessaire l'URL adéquate, ou l'URL inchangée
        si elle était déjà valide.

        Cf par exemple le message d'erreur suivant si l'URL contient 1 espace :

            InvalidURL = URL can't contain control characters. '/my Check-Lists.py' (found at least ' ')

        :return: une URL valide.
        """

        valid_url = url

        for key, value in self._url_forbiddens.items():

            if key in url:

                valid_url = valid_url.replace(key, value)

        return valid_url


    def send_request_http(
        self,
        url: str,
        coding: str = coding_unknown
        ) -> (str, str, str):
        """ Pour envoyer une requête HTTP et en recevoir le résultat.

        :param url: la requête à lancer.

        :param coding: l'encodage attendu de la réponse.

        :return: la réponse + son type de contenu + son format.
        Le format correspondra au format souhaité, sauf si nous avons
        eu à le modifier. Ce qui sera par exemple le cas si celui qui
        nous a été transmis était « coding_unknown ».
        """

        log = self.logItem
        url_string = ''
        url_content = None

        url_valid = self.url_to_valid(url)
        self.shw(f'URL get  = {url}')
        self.shw(f'URL ok   = {url_valid}')

        # Nous encapsulons l'URL dans la structure urllib.request.Request
        # du module, au cas où nous souhaitions plus tard utiliser cette
        # classe afin de transmettre des paramètres à l'URL contactée...
        #
        # Si nous voulions ne pas utiliser cette structure et rester simple
        # dans nos syntaxes, il suffirait alors de directement passer à l'
        # appel urllib.request.urlopen() ci-dessous l'adresse url_valid.
        #
        request = urllib.request.Request(url=url_valid)

        try:

            # Pour économiser les ressources, on utilise WITH... ie
            # l'objet réponse sera libéré dès la sortie du bloc.
            #
            # « Using the context manager with, you make a request and
            # receive a response with urlopen(). Then you read the body
            # of the response and close the response object. »
            #
            #with urllib.request.urlopen(url_valid, timeout=3) as data:
            with urllib.request.urlopen(request, timeout=3) as data:

                url_bytes = data.read()

                # data.url = URL of the resource retrieved, commonly used
                # to determine if a redirect was followed.
                #
                url_address = data.url

                # status = Status code returned by server.
                # ( New in version 3.9 )
                #
                # code = Deprecated in favor of status.
                # ( Deprecated since version 3.9 )
                #
                # getstatus() = Deprecated in favor of status.
                # ( Deprecated since version 3.9 )
                #
                # Cf https://docs.python.org/3.9/library/urllib.request.html#module-urllib.response
                #
                if hasattr(data, 'status'):
                    url_status = data.status
                elif hasattr(data, 'code'):
                    url_status = data.code
                else:
                    url_status = data.getstatus()

                # Returns the headers of the response in the form of an
                # EmailMessage instance.
                #
                # Cf https://docs.python.org/3/library/email.message.html#email.message.EmailMessage
                #
                url_header = data.headers

                # headers.get_content_charset() sait lire les fichiers au
                # format HTML.
                #
                # Le "character encoding" n'est normalement pas spécifié
                # dans le fichier .py, pas en tout cas à la façon d'un
                # fichier HTML normal !!!
                #
                # Donc get_content_charset() ne devrait pas le lire de
                # façon correcte si c'est un fichier script Python, bash
                # ou autres.
                #
                # Dans le cas où get_content_charset() ne peut donner de
                # réponse, il renverra « None ».
                #
                url_charset = url_header.get_content_charset()
                url_content = url_header.get_content_type()

        except TimeoutError:
            self.shw('')
            self.shw('===>> Request timed out at the SYSTEM level...')
            self.shw('')

        except http.client.InvalidURL as error:
            self.shw('')
            self.shw(f'===>> InvalidURL ( http.client ) = {error}')
            self.shw('')

        except http.client.NotConnected as error:
            self.shw('')
            self.shw(f'===>> NotConnected ( http.client ) = {error}')
            self.shw('')

        # The except HTTPError must come first, otherwise except URLError
        # will also catch an HTTPError.
        #
        # Cf https://docs.python.org/3/howto/urllib2.html#wrapping-it-up
        #
        # Though being an exception (a subclass of URLError), an HTTPError
        # [..]
        #
        # Cf https://docs.python.org/3/library/urllib.error.html#urllib.error.HTTPError
        #
        # FINALEMENT : le traitement des erreurs HTTPError a été reporté
        # dans celui des erreurs URLError ( puisque HTTPError est une ss-
        # classe de URLError ). C'est plus propre.
        #
        # Cf https://docs.python.org/3/howto/urllib2.html#wrapping-it-up
        # Cf https://docs.python.org/3/howto/urllib2.html#number-2
        #
        #except urllib.error.HTTPError as error:
        #    self.shw('')
        #    self.shw(
        #        f'===>> HTTP {error.status} ERROR = {error.reason}'
        #        )
        #    self.shw('')
        #
        except urllib.error.URLError as error:
            self.shw('')

            # On gère ici aussi bien les HTTPError que les URLError.
            #
            # Cf https://docs.python.org/3/library/urllib.error.html#urllib.error.URLError
            # Cf https://docs.python.org/3/library/urllib.error.html#urllib.error.HTTPError
            # Cf https://docs.python.org/3/howto/urllib2.html#wrapping-it-up
            # Cf https://docs.python.org/3/howto/urllib2.html#error-codes
            # Cf https://docs.python.org/3/library/http.server.html#http.server.BaseHTTPRequestHandler.responses
            #
            if isinstance(error.reason, socket.timeout):
                self.shw('===>> Socket timeout error...')

            elif hasattr(error, 'code'):
                self.shw(
                    f'===>> HTTP {error.code} ERROR = {error.reason}'
                    )
                self.shw("The server couldn't fulfill the request.")

                # On inscrit dans le LOG le maximum d'informations
                # concernant cette erreur...
                #
                if error.code in http.server.BaseHTTPRequestHandler.responses:

                    msgs = http.server.BaseHTTPRequestHandler.responses[
                        error.code
                        ]

                    log.debug(f'Short reason = {msgs[0]}')
                    log.debug(f'Full reason = {msgs[1]}')

            else:
                self.shw(f'===>> URLError = {error.reason}')
                self.shw("We failed to reach a server.")

            self.shw('')
            log.debug(f'Error TYPE = {type(error)}')
            log.debug(f'Reason TYPE = {type(error.reason)}')
            log.debug('')

        else:
            # EVERYTHING IS FINE : la requête a donné un résultat.

            # On informe si l'URL originale a été redirigée vers
            # une autre adresse.
            #
            # ATTENTION : Ce test ne détecte pas si le préfix http
            # change !! Ainsi, la requête 'http://www.google.com/'
            # est toujours remplacée par 'https://www.google.com'
            # mais le test « url_address != url_valid » ne saura
            # voir que le préfixe HTTP est devenu HTTPS.
            #
            if url_address != url_valid:
                self.shw(f'URL real = {url_address}')
                self.shw( '[ i.e a redirect was followed... ]')

            self.shw('')

            log.debug(f'Status code returned by server = {url_status}')
            log.debug(f'Content type returned by server = {url_content}')
            log.debug(f'Content charset returned by server = {url_charset}')
            log.debug('')

            log.debug('Début de « url_bytes » :')
            log.debug(url_bytes[0:99])
            log.debug('')

            self.shw(f'Coding en entrée = « {coding} »')

            if coding == coding_unknown:
                coding = url_charset

            self.shw(f'Coding calculé = « {coding} »')
            self.shw('')

            if (coding is None) or (coding == coding_bytes):

                # Aucun décodage à faire car le jeu de caractères
                # qui nous concerne est celui des « byte strings ».
                #
                url_string = url_bytes

            else:
                url_string = url_bytes.decode(coding)

            log.debug('Début de « url_string » :')
            log.debug(url_string[0:99])
            log.debug('')

        return (url_string, url_content, coding)


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


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    log.info('')
    log.info('\t=================================')
    log.info('\t>>> CHOIX DE LA CONFIGURATION <<<')
    log.info('\t=================================')
    log.info('')
    log.info('')

    config_choice = [
        'Module OS seul + os.listdir',
        'Module OS seul + os.scandir',
        'Utilisation du module GLOB',
        'Utilisation du module FNMATCH + os.listdir',
        'Utilisation du module FNMATCH + os.scandir',
        'Utilisation du module PATHLIB « enfoui »',
        'Utilisation du module PATHLIB « direct »',
        ]

    # Les tuples ci-dessous correspondent à l'initialisation
    # des différentes variables ( avec l'ordre = with_glob,
    # with_fnmatch, with_pathlib, walking_mode ) de chacune
    # des configurations ci-dessus.
    #
    config_init = [
        #
        # Module OS seul + os.listdir
        (False, False, pathlib_ignore, walking_via_listdir),
        #
        # Module OS seul + os.scandir
        (False, False, pathlib_ignore, walking_via_scandir),
        #
        # Utilisation du module GLOB
        (True,  False, pathlib_ignore, walking_via_listdir),
        #
        # Utilisation du module FNMATCH + os.listdir
        (False, True,  pathlib_ignore, walking_via_listdir),
        #
        # Utilisation du module FNMATCH + os.scandir
        (False, True,  pathlib_ignore, walking_via_scandir),
        #
        # Utilisation du module PATHLIB « enfoui »
        (False, False, pathlib_deeply, walking_ignore),
        #
        # Utilisation du module PATHLIB « direct »
        (False, False, pathlib_direct, walking_ignore),
    ]

    idx = skull.choose_in_a_list(config_choice, 0)

    if idx < 0:
        skull.shw("Aucun choix n'a été fait...")
        skull.shw('-> « OS seul + os.listdir » imposé.')
        idx = 0

    else:
        skull.shw(f'Votre réponse = {config_choice[idx]}')

    skull.shw('')

    w_glob, w_fnmatch, w_pathlib, walking_mode = config_init[idx]

    skull.file_system_mode(
        walking_mode = walking_mode,
        with_pathlib = w_pathlib,
        with_fnmatch = w_fnmatch,
        with_glob = w_glob
        )

    if (w_pathlib == pathlib_direct):

        node_file = skull.files.node(__file__ + '.test')

        skull.shw('\tTOUTES les méthodes de PATHLIB sont alors disponibles.')
        skull.shw(f'\tpath          = {node_file}')
        skull.shw(f'\tpath.SUFFIXES = {node_file.suffixes}')
        skull.shw(f'\tpath.PARENTS  = {len(list(node_file.parents))}'
                    ' [ c-a-d len(list(path.parents)) ]')

        log.debug('\tcar .PARENTS  = ')
        for parent in list(node_file.parents):
            log.debug('\t\t%s', parent)

        skull.shw('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise les TESTS de COMPRÉHENSIONS de LISTE ?",
        'non'
        )

    if user_answer:

        # On affiche des résultats de compréhensions de
        # liste à titre dicdactique.
        #
        # Ici, nous ne sommes donc pas vraiment dans de
        # l'autotest... mais plus dans de la pédagogie.
        #
        log.info('')
        log.info('\t===============================')
        log.info('\t>>> COMPRÉHENSIONS de LISTE <<<')
        log.info('\t===============================')
        log.info('')
        log.info('')

        mask = "*[[@]*"

        log.info('Test et RÉSULTAT de :')
        log.info('')
        log.info(f'\t[ n for n in < current directory > if fnmatch.fnmatch( n.name, "{mask}" ) ]')
        log.info('')
        log.info('... où « n » est de type « FileSystelLeaf » ou « pathlib.Path » :')
        log.info('')

        try: fnmatch.translate('test_if*already_imported')
        except AttributeError: import fnmatch

        our_dir = skull.files.node().iterdir
        our_lst = [n for n in our_dir() if fnmatch.fnmatch(n.name, mask)]

        if len(our_lst) > 0:

            for n in our_lst:
                skull.shw(f'\t{n}')

            skull.shw('')
            skull.shw(f'\t=> DATATYPE for ALL objects = {type(our_lst[0])}')

        else:
            skull.shw('\tNO SUCH FILES OR DIRECTORIES')

        skull.shw('')


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
        "Voulez-vous que je réalise mes AUTOTESTS de CONCATÉNATIONS de PATH ?",
        'non'
        )

    if user_answer:

        log.info('')
        log.info('\t==============================')
        log.info('\t>>> CONCATÉNATIONS de PATH <<<')
        log.info('\t==============================')
        log.info('')
        log.info('')

        leaf = skull.files.node

        skull.shw('EXEMPLE 1 : Opérateur « / » + Opérandes « FileSystelLeaf » et « STRING »')
        skull.shw('')

        # Nous écrivons nos PATH à la mode UNIX ( ie avec
        # « / » comme séparateur ) car Python fournit des
        # fonctions pour transformer cette notation UNIX
        # vers celle Windows ( ie « \ » comme séparateur )
        # mais pas pour l'inverse. Or nous lançons aussi,
        # entre autres, ces tests sur iPad + iOS, où « \ »
        # ne sera pas compris comme séparateur de PATH...
        #
        # Cf ainsi :
        #
        #   https://docs.python.org/3/library/os.path.html#os.path.normpath
        #
        #   (..) On Windows, it converts forward slashes
        #   to backward slashes.
        #
        operande_1 = leaf(r"A:/blah/bleh/blih")
        operande_2 = "ESSAI_n°1"
        result = operande_1 / operande_2

        skull.shw(f'\t« {str(operande_1)} »\tconcaténé avec\t« {str(operande_2)} »')
        skull.shw(f'\t=> Résultat        = « {result} »')
        skull.shw(f'\toù Type Opérande 1 = « {type(operande_1)} »')
        skull.shw(f'\tet Type Opérande 2 = « {type(operande_2)} »')
        skull.shw(f'\tet Type Résultat   = « {type(result)} »')
        skull.shw('')

        skull.shw('EXEMPLE 2 : Opérateur « / » + Opérandes « STRING » et « FileSystelLeaf » ( mais BUG car 2 disques indiqués !!! )')
        skull.shw('')

        operande_1 = r"B:/ESSAI_n°2"
        operande_2 = leaf(r"C:/problème/car/deux/disques")
        result = operande_1 / operande_2

        skull.shw(f'\t« {str(operande_1)} »\tconcaténé avec\t« {str(operande_2)} »')
        skull.shw(f'\t=> Résultat        = « {result} »')
        skull.shw(f'\toù Type Opérande 1 = « {type(operande_1)} »')
        skull.shw(f'\tet Type Opérande 2 = « {type(operande_2)} »')
        skull.shw(f'\tet Type Résultat   = « {type(result)} »')
        skull.shw('')

        skull.shw(r"EXEMPLE 3 : Idem et 1er BUG réglé ( mais 2nd BUG car le « \ » de l'opérande 2 masque « problème\réglé » !!! )")
        skull.shw('')

        operande_1 = r"D:/problème/réglé"
        operande_2 = leaf(r"/ESSAI_n°3")
        result = operande_1 / operande_2

        skull.shw(f'\t« {str(operande_1)} »\tconcaténé avec\t« {str(operande_2)} »')
        skull.shw(f'\t=> Résultat        = « {result} »')
        skull.shw(f'\toù Type Opérande 1 = « {type(operande_1)} »')
        skull.shw(f'\tet Type Opérande 2 = « {type(operande_2)} »')
        skull.shw(f'\tet Type Résultat   = « {type(result)} »')
        skull.shw('')

        skull.shw('EXEMPLE 4 : Opérateur « /= »')
        skull.shw('')

        operande_1 = leaf("Z://woah_wouh//")
        operande_2 = "ESSAI_n°4"
        result = operande_1
        result /= operande_2

        skull.shw(f'\t« {str(operande_1)} »\tconcaténé avec\t« {str(operande_2)} »')
        skull.shw(f'\t=> Résultat        = « {result} »')
        skull.shw(f'\toù Type Opérande 1 = « {type(operande_1)} »')
        skull.shw(f'\tet Type Opérande 2 = « {type(operande_2)} »')
        skull.shw(f'\tet Type Résultat   = « {type(result)} »')
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

        # Dans un 1er temps, nous limitions le test de notre
        # méthode _fake_iglob() aux seuls cas où la gestion
        # du système de fichiers ne dépendait que du module
        # OS ( et de os.path ) :
        #
        #   if not (w_glob or w_fnmatch) and w_pathlib == pathlib_ignore:
        #
        # Nous avons depuis élargi le nombre des cas où nous
        # testions _fake_iglob(). Pour autant, ns ne testons
        # pas cette méthode dans le mode « pathlib_direct »
        # puisque, dans ce mode, la gestion du système de
        # fichiers est totalement déléguée au module PATHLIB
        # et à ses objets pathlib.PATH qui ne disposent pas
        # d'une méthode _fake_iglob()... !!!
        # 
        if not (w_pathlib == pathlib_direct):

            # On appelle _fake_iglob() pour vérifier que
            # Python n'y plante pas.
            #
            log.info('')
            log.info('\t=============================')
            log.info('\t>>> TEST de _fake_iglob() <<<')
            log.info('\t=============================')
            log.info('')
            log.info('Version FRUSTRE :')
            log.info('-----------------')
            log.info('')
            log.info('Nous testons cette méthode dans le cas de fichiers ou répertoires seuls.')
            log.info('Le cas « indifférencié » est scanné via « search_files_from_a_mask() ».')
            log.info('')
            log.info('')

            t_name = {
                _glob_only_dirs: 'SOUS-RÉPERTOIRES',
                _glob_only_files: 'FICHIERS'
            }

            our_dir = skull.files.node()

            for t in (_glob_only_dirs, _glob_only_files):

                msg = t_name[t] + ' du répertoire courant :'

                log.info('\t' + msg)
                log.info('\t' + '~' * len(msg))

                for n in sorted(our_dir._fake_iglob(n_type = t)):
                    skull.shw(f'\t{n}')

                skull.shw('')

            print()
            input("--- PAUSE avant la recherche suivante ---")
            print()

            log.info('')
            log.info('Version FNMATCH :')
            log.info('-----------------')
            log.info('')

            mask = '*[{(@]*'
            mask_dct = our_dir._parse_mask(mask, _search_fnmatch)

            log.info(f'Masque = {mask}')
            log.info('')

            for n in sorted(our_dir._fake_iglob(**mask_dct)):
                skull.shw(f'\t{n}')

            skull.shw('')

            print()
            input("--- PAUSE avant la recherche suivante ---")
            print()

        # On appelle search_files_from_a_mask() pour
        # vérifier que Python n'y plante pas.
        #
        log.info('')
        log.info('\t==========================================')
        log.info('\t>>> TEST de search_files_from_a_mask() <<<')
        log.info('\t==========================================')
        log.info('')
        log.info('')

        # On défini dans la liste ( de n-uplets nommés )
        # suivante toutes les recherches que nous allons
        # mener. Ainsi :
        #
        #   1 - On va chercher tout d'abord des fichiers
        #       *.ISO dans un répertoire lointain...
        #
        #   2 - Ensuite : tous les fichiers ( * ) dans un
        #       répertoire proche...
        #
        #   3 - ...
        #
        #   x - Enfin : les fichiers *.py du répertoire de
        #       travail.
        #
        try: collections
        except NameError: import collections

        Search = collections.namedtuple(
            "Search",
            ['mask', 'dir']
            )

        # Nous écrivons nos PATH à la mode UNIX ( ie avec
        # « / » comme séparateur ) car Python fournit des
        # fonctions pour transformer cette notation UNIX
        # vers celle Windows ( ie « \ » comme séparateur )
        # mais pas pour l'inverse. Or nous lançons aussi,
        # entre autres, ces tests sur iPad + iOS, où « \ »
        # ne sera pas compris comme séparateur de PATH...
        #
        # Cf ainsi :
        #
        #   https://docs.python.org/3/library/os.path.html#os.path.normpath
        #
        #   (..) On Windows, it converts forward slashes
        #   to backward slashes.
        #
        searches_todo = (
            Search('*',     __file__),  # ERREUR = dans 1 fichier, non 1 répertoire
            Search('*.iso', r"K:/_Backup.CDs/Comptabilité"),
            Search('*.*',   r"../tmp"),
            Search('(*',    r"../all files to one PDF"),
            Search('r*',    r"../StoreKit"),            
            #
            # Ajouter ci-dessus d'éventuelles nouvelles
            # recherches. Laisser les 2 recherches qui
            # suivent en dernière position.
            #
            # En effet, la dernière ( sk*le*.py ) de la
            # liste = son résultat nourrit le traitement
            # qui la suit.
            #
            # Par ailleurs, l'avant-dernière recherche
            # ( Sk*lE*.py ) permet, elle, de tester si l'
            # OS est sensible à la casse en fonction des
            # différentes options choisies ( avec glob
            # ou pas, avec fnmatch ou pas, ... ). C'est
            # par exple le cas sous iPadOS 16.3.1 ( ie
            # Darwin Kernel Version 22.3.0 avec PYTHON
            # version 3.11.0 ).
            #
            Search('Sk*lE*.py',  None),
            Search('sk*le*.py',  None)
            )

        for idx, s in enumerate(searches_todo, start=0):

            if idx > 0:
                input("--- PAUSE avant la recherche suivante ---")
                print()
                print()

            files_found = skull.search_files_from_a_mask(
                directory = s.dir,
                mask = s.mask
                )

            msg_dir = f"« {s.mask} » in « {'.' if s.dir is None else s.dir} »"
            msg_find = 9 * ' ' + f'---> Fichier(s) trouvé(s) :'
            len_maxi = max(len(msg_dir), len(msg_find))

            log.debug('')
            skull.shw('~' * len_maxi)
            skull.shw(msg_dir)
            skull.shw(msg_find)
            skull.shw('~' * len_maxi)

            if files_found is None or len(files_found) == 0:
                skull.shw('\tNO SUCH FILES or DIRECTORIES...')

            else:
                for file_name in sorted(files_found):
                    skull.shw(f'\t{file_name}')
                    skull.shw(f'\t\t=> DATATYPE = {type(file_name)}')

            skull.shw('')
            skull.shw('')

        user_answer = skull.ask_yes_or_no(
            f"Édition des fichiers {s.mask} ( via l'éditeur de TXT ) ?",
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

        f_ext = '.blah-blah'
        f_tmp = skull.get_unused_filename(f_name, f_ext, idx_force = False)

        skull.shw(f'Prochain nom disponible = « {f_tmp} »')
        skull.shw(f"\t[ avec l'extension « {f_ext} » ]")
        skull.shw('')

        skull.shw(f'Création de « {f_tmp} »')
        skull.shw('')

        skull.files.node(f_tmp).touch()

        skull.shw(f'Prochain nom après « {f_tmp} » ...')
        skull.shw('')

        skull.shw(
            '\t* sur 18 chiffres, base 33 : « {} »'.format(
                skull.get_unused_filename(f_name, '', 18, 33)
                )
            )
        skull.shw(f"\t[ SANS extension ]")
        skull.shw('')

        f_tmp = skull.get_unused_filename(f_name)

        skull.shw(f'\t* sur 3 chiffres, base 0 : « {f_tmp} »')
        skull.shw(f"\t[ avec l'extension par DÉFAUT ]")
        skull.shw('')

        skull.shw(f'Création de « {f_tmp} »')
        skull.shw('')

        skull.files.node(f_tmp).touch()

        skull.shw(f'Re-Création de « {f_tmp} »')
        skull.shw('')

        try:
            skull.files.node(f_tmp).touch()

        except FileExistsError:
            skull.shw(f'\tINTERDITE CAR CE FICHIER EXISTE !!!')
            skull.shw('')

        skull.shw(f'Prochain nom après « {f_tmp} » ...')
        skull.shw('')

        f_tmp = skull.get_unused_filename(f_name)

        skull.shw(f'\t* sur 3 chiffres, base 0 : « {f_tmp} »')
        skull.shw(f"\t[ avec l'extension par DÉFAUT ]")
        skull.shw('')


    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    # -----------------------------------------------------------------------
    # #######################################################################
    #
    user_answer = skull.ask_yes_or_no(
        "Voulez-vous que je réalise mes AUTOTESTS de REQUÊTES HTTP ?",
        'non'
        )

    if user_answer:

        # On appelle les fonctions convert_to_pdf_*() pour
        # vérifier que Python ne plante pas en leur sein.
        #
        log.info('')
        log.info('\t=============================')
        log.info('\t>>> TEST de REQUÊTES HTTP <<<')
        log.info('\t=============================')
        log.info('')
        log.info('')

        url_dict = {
            'git_bnz'   : 'https://bonzzzy.github.io/',
            # Notre GitHub...
            # ( HTML lisible = Contenu ULTRA-simple + TXT seul )
            #
            'exple'     : 'https://www.example.com/',
            # Example Domain = This domain is for use in illustrative
            # examples in documents.
            # ( HTML lisible = Contenu simple + TXT seul )
            #
            'iana'      : 'https://www.iana.org/domains/reserved',
            # Internet Assigned Numbers Authority (IANA)
            # = HTML OFFICIEL tel qu'il est NORMALISÉ !!!
            # ( HTML lisible = Contenu COMPLEXE + TXT multi-alphabet )
            #
            'tst_fr'    : 'http://www.tst.fr/m" ! "',
            # URL qui va être transformée
            # ... via notre méthode url_to_valid() :
            #
            #   http://www.tst.fr/m%22%20!%20%22
            #
            # ... et l'URL existe ( redirection ) :
            #
            #   https://tst.fr/m%22%20!%20%22
            #
            # ... pour être elle-même redirigée vers :
            #
            #   https://tst.fr/nos-metiers/manchette/
            #
            # = HTML probablement GÉNÉRÉ par un OUTIL.
            # ( HTML à peu près lisible = Contenu COMPLEXE + IMG aussi )
            #
            'json_do_1' : 'https://jsonplaceholder.typicode.com/todos/1',
            # Contenu JSON ultra-simple, i.e 1 seul enregistrement...
            # {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": false}'
            #
            'json_do_a' : 'https://jsonplaceholder.typicode.com/todos/',
            # Contenu JSON toujours simple, mais avec 200 enregistrements.
            #
            'pb_aslash' : 'https://fr.search.yahoo.com/search?p=\\U0001f496',
            # Le caractère antislash « \ » peut être utilisé dans certaines
            # requêtes. On vérifie ici que notre script l'accepte bien et le
            # traite via une conversion :
            #
            #    https://fr.search.yahoo.com/search?p=\U0001f496
            # -> https://fr.search.yahoo.com/search?p=%5CU0001f496
            #
            'pb_dummy'  : 'http://www.dummy.tmp/',
            # Fausse adresse = URLError 11001
            #
            'pb_uni'    : 'https://jsonplaceholder.typicode.com/',
            # Cette page HTML indique en entête, comme beaucoup :
            #
            #   « meta charset="UTF-8" »
            #
            # Pour autant, dans son corps, se retrouve le caractère « ❤️ »
            # ( '\U0001f496' ) qui n'est pas inclus dans la table UTF-8 de
            # Python ( alors qu'il devrait ? ).
            #
            #   https://www.google.com/search?q=\U0001f496
            #   https://www.google.com/search?q=%5CU0001f496
            #   = Emoji Unicode Character 'SPARKLING HEART' (U+1F496)
            #
            # La présence de ce caractère faisait alors planter l'exécution
            # lorsque, dans ce script, on essayait d'écrire dans un fichier
            # en mode TEXTE ( ouvert via « wt » ) le résultat de la requête
            # GET pour cette page, via les appels successifs aux méthodes :
            #
            # result = skeleton.send_request_http('jsonplaceholder.typicode.com')
            # [ puis ] skeleton.save_strings_to_file(result).
            #
            # Le message d'erreur était :
            #
            #   UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f496' in position 2185: character maps to <undefined>
            #
            # Cf la partie :
            #
            #   « except UnicodeEncodeError: »
            #
            # ... dans notre méthode « save_strings_to_file() ».
            #
            # D'où le fait que, dorénavant, lors de nos tests ci-dessous,
            # nous imposons le format « coding_bytes » comme format pour
            # l'expression du résultat de la requête, puis, par la suite,
            # comme format pour l'écriture dans le fichier. Aucun encodage
            # / décodage n'est alors réalisé :
            #
            #       . urllib.request.urlopen("...").read() renvoie une
            # chaîne de caractères au format « bytes »,
            #
            #       . en mode "wb", écrire dans un fichier demande une
            # chaîne au format b"...", ie au format « bytes ».
            #
            # Pas besoin donc de passer par la table UTF-8 de Python,
            # table qui semble incomplète.
            #
            'g_403'     : 'https://www.google.com/search?q=test',
            # Adresse interdite via Python = HTTP 403 ERROR
            # ... pour éviter les attaques par surcharge ??
            # ... car cette requête marche sous Firefox !!!
            #
            'g_403_fox' : 'https://www.google.com/search?client=firefox-b-d&q=test',
            # Tout comme la précédente, cette requête n'est pas acceptée
            # bien qu'un CLIENT FIREFOX soit indiqué = HTTP 403 ERROR !!!
            #
            'g_404'     : 'https://www.google.com/search-q-test',
            # Adresse inconnue = HTTP 404 ERROR
            #
            'g_www'     : 'http://www.google.com/',
            # Google.com
            # ... page bien plus complexe que son simple affichage ne le
            # laisse penser.
            # ... Elle se redirige vers https://www.google.com mais notre
            # méthode send_request_http() ne le détecte pas ( la méthode
            # ne fait pas la différence entre HTTP et HTTPS ).
            # ( HTML TOTALEMENT ILLISIBLE )
            #
            'AF_saml'   : 'https://intralignes.airfrance.fr/',
            # Air France = Authentification SAML 2.
            # ( HTML ILLISIBLE = SAMLRequest codée en Base64 )
            # > Cf https://www.dcode.fr/code-base-64 pour décodage.
            #
        }

        model = f'{it_begins_with}_HTML_answer_for_.html'
        out_files = list()

        # Suivant la façon choisie de parcourir la boucle FOR ci-dessous,
        # nous allons tester toutes les requêtes ou seulement certaines.
        #
        #keys = url_dict.keys()
        keys = ('json_do_1', 'git_bnz', 'exple')
        #keys = ('json_do_a', 'git_bnz', 'exple', 'iana', 'tst_fr')
        #keys = sorted(('pb_dummy', 'g_403', 'g_403_fox', 'g_404'))
        #keys = [ k for k in url_dict.keys() if k.startswith('g_') ]
        #keys = [ k for k in url_dict.keys() if k.startswith('pb_') ]

        for key in keys:

            url = url_dict[key]
            name = key.upper()

            log.info(f'Nouvelle requête : {url}')
            log.info('~~~~~~~~~~~~~~~~~~~')
            log.info('')
            log.info(f'« NOM interne » de cette requête = {name}')
            log.info('')

            # Cf ci-dessus les remarques concernant :
            #
            #       'https://jsonplaceholder.typicode.com/'
            #
            #coding = coding_unknown
            coding = coding_bytes

            #rep, _, charset = skull.send_request_http(url)
            #rep, _, _ = skull.send_request_http(url, coding=coding_bytes)
            rep, chartype, charset = skull.send_request_http(url, coding=coding)

            if rep != '':

                out = skull.save_strings_to_file(
                    rep,
                    destination=model,
                    must_be_new=True,
                    new_suffix=f'{{ {name} }}',
                    data_type=chartype,
                    #data_fmt=coding_bytes
                    data_fmt=charset
                    )

                out_files.append(out)

            log.info('')

        if len(out_files) > 0:
            skull.edit_file_txt(*out_files, wait=False)


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
        working_node = skull.paths_and_miscellaneous['NOD_working']

        player_exe = str(working_node / 'mplay32.exe')
        player_arg = ['/play', '/close']
        played = str(working_node / 'Windows XP Battery Low.wav')

        skull.paths_and_miscellaneous['EXE_player'] = player_exe
        skull.paths_and_miscellaneous['ARG_player'] = player_arg
        skull.paths_and_miscellaneous['EXE_played'] = played

        # On teste l'émission via mplay32.exe d'un son de réveil.
        #
        if leaf(player_exe).is_file() and leaf(played).is_file():

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
