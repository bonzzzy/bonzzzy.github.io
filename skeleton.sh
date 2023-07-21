#!/bin/sh
#
# CONSEIL = Il est possible de renommer, pour améliorer sa facilité d'utilisation,
# ce fichier en « @s » par exemple :
#
#		mv "skeleton.sh" @s
#
# Before using this file as a shell script you must change its access permissions :
#
# 		chmod u+rwx @s
#

# On lève dorénavant l'ambiguité qui existait avec la commande :
#
#		python "skeleton.py"
#
# En effet, suivant les configurations machine et/ou les alias utilisateurs :
#
#		python pouvait représenter python2 ou python 3 !!!
#
# On désigne donc nommément python 3.
#
python3 "skeleton.py"
