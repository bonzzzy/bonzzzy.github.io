#!/bin/sh
#


rename_to_file() {

	if [ -e "$1" ]
	then
		if [ -e "$2" ]; then rm "$2"; fi
		mv "$1" "$2"
	fi

}


rename_to_cmd() {

	rename_to_file "$1" "$2"
	if [ -e "$2" ]; then chmod u+rwx "$2"; fi

}


#
# Nettoyage des LOG et des fichiers temporaires de TESTS
#
rm -f "#_LOG_*"

rm -f "#_TESTS_*"


#
# On renomme nos fichiers avec des noms courts car la saisie sous iPad c'est CHIANT !!!
#
rename_to_cmd "import_via_github.sh" "@i"

rename_to_cmd "my%20Check-Lists.sh" "@c"

rename_to_cmd "my Check-Lists.sh" "@c"

rename_to_cmd "skeleton.sh" "@s"

rename_to_file "my%20Check-Lists.py" "my Check-Lists.py"


#
# ATTENTION : Cette ligne doit être la dernière puisque elle ECRASE le script que nous
# sommes en train d'exécuter, ce qui va causer ( probablement ) sa fin ou, à minima, le
# système risque d'y perdre ses petits... ???
#
rename_to_cmd "admin.sh" "@a"
