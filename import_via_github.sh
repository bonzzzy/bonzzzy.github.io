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

python import_via_github.py "skeleton.py" "my Check-Lists.py" "import_via_github.sh"
