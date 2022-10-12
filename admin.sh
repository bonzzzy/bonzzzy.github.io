#!/bin/sh
#

if [ -e "import_via_github.sh" ]
then
	if [ -e @i ]; then rm @i; fi
	mv "import_via_github.sh" @i
	chmod u+rwx @i
fi

if [ -e "my%20Check-Lists.py" ]
then
	if [ -e "my Check-Lists.py" ]; then rm "my Check-Lists.py"; fi
	mv "my%20Check-Lists.py" "my Check-Lists.py"
fi

if [ -e "my%20Check-Lists.sh" ]
then
	if [ -e @c ]; then rm @c; fi
	mv "my%20Check-Lists.sh" @c
	chmod u+rwx @c
fi
