#!/bin/sh
#
# CONSEIL = Il est possible de renommer, pour am�liorer sa facilit� d'utilisation,
# ce fichier en � @i � par exemple :
#
#		mv import_via_github.sh @i
#
# Before using this file as a shell script you must change its access permissions :
#
# 		chmod u+rwx import_via_github.sh
#
# .. ou ( si le fichier a �t� renomm� ) :
#
# 		chmod u+rwx @i
#
echo

# On l�ve dor�navant l'ambiguit� qui existait avec la commande :
#
#		python import_via_github.py
#
# En effet, suivant les configurations machine et/ou les alias utilisateurs :
#
#		python pouvait repr�senter python2 ou python 3 !!!
#
# On d�signe donc nomm�ment python 3.
#
python3 import_via_github.py " " "import_via_github.sh" "skeleton.py" "skeleton.sh" "my Check-Lists.py" "admin.sh"
