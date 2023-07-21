#!/bin/sh
#
# CONSEIL = Il est possible de renommer, pour am�liorer sa facilit� d'utilisation,
# ce fichier en � @c � par exemple :
#
#		mv "my Check-Lists.sh" @c
#
# Before using this file as a shell script you must change its access permissions :
#
# 		chmod u+rwx @c
#
echo

# On l�ve dor�navant l'ambiguit� qui existait avec la commande :
#
#		python "my Check-Lists.py"
#
# En effet, suivant les configurations machine et/ou les alias utilisateurs :
#
#		python pouvait repr�senter python2 ou python 3 !!!
#
# On d�signe donc nomm�ment python 3.
#
python3 "my Check-Lists.py"
