import os, fnmatch

ANIMATION_LIST = []

files = os.listdir(os.path.dirname(__file__))
for entry in files:
    if fnmatch.fnmatch(entry, "*.gif"):
        ANIMATION_LIST.append(entry)
