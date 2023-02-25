#!/bin/sh
#
# CONSEIL = Il est possible de renommer, pour améliorer sa facilité d'utilisation,
# ce fichier en « @i » par exemple :
#
#		mv import_via_github.sh @i
#
# Before using this file as a shell script you must change its access permissions :
#
# 		chmod u+rwx import_via_github.sh
#
# .. ou ( si le fichier a été renommé ) :
#
# 		chmod u+rwx @i
#
echo

python import_via_github.py " " "import_via_github.sh" "skeleton.py" "skeleton.sh" "my Check-Lists.py" "admin.sh"
