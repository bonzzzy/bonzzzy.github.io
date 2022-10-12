#!/bin/sh
#

if [ -e "import_via_github.sh" ]
then
	rm @i
	mv "import_via_github.sh" @i
	chmod u+rwx @i
fi

if [ -e "mv my%20Check-Lists.py" ]
then
	rm "my Check-Lists.py"
	mv "my%20Check-Lists.py" "my Check-Lists.py"
fi

if [ -e "mv my%20Check-Lists.py" ]
then
	rm @c
	mv "my%20Check-Lists.sh" @c
	chmod u+rwx @c
fi
