import os, fnmatch

FONT_LIST = []

files = os.listdir(os.path.dirname(__file__))
for entry in files:
    if fnmatch.fnmatch(entry, "*.ttf"):
        FONT_LIST.append(entry)
