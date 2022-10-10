#!/usr/bin/env python
# -*- coding: utf8 -*-


import os
from urllib.request import urlopen

page = urlopen("https://bonzzzy.github.io/import_via_github.py")

content = page.read

with open("newfile.py","w") as filex:

    filex.write(str(content))

print("File saved")
