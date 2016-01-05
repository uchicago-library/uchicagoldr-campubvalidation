from sys import argv
from os.path import isdir, join, isfile
from os import walk
from re import match
from shutil import move

root = argv[1]

assert(isdir(root))

for dirpath, dirnames, filenames in walk(root):
    for filename in filenames:
        if match(".*\.alto$", filename):
            newfilename = filename.replace('.alto','.xml')
            move(join(dirpath,filename), join(dirpath,newfilename))
