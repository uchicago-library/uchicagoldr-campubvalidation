from sys import argv
from os.path import isdir, join, isfile
from os import walk
from re import match
from shutil import move

root = argv[1]

assert(isdir(root))

for dirpath, dirnames, filenames in walk(root):
    if match(".*\/mvol\/\d{4}\/\d{4}\/\d{4}", dirpath):
        print("Stopping recursion at "+dirpath)
        del dirnames[:]

    for filename in filenames:
        if match("mvol-\d{4}-\d{4}-\d{4}\.struct\.txt$", filename) or \
        match("mvol-\d{4}-\d{4}-\d{4}\.txt$", filename):
            try:
                print("Checking "+join(dirpath, filename))
                containsWhiteSpaceLines = False
                with open(join(dirpath, filename), 'r') as f:
                    for line in f.readlines():
                        if match("^\s*$",line):
                            containsWhiteSpaceLines = True
                            break
                if containsWhiteSpaceLines:
                    print("Editing "+join(dirpath, filename))
                    with open(join(dirpath, filename), 'r') as inFile:
                        with open(join(dirpath, filename+'.new'), 'w') as outFile:
                            for line in inFile.readlines():
                                if not match("^\s*$",line):
                                    outFile.write(line)
                    move(join(dirpath, filename), join(dirpath, filename+'.old'))
                    move(join(dirpath, filename+'.new'), join(dirpath, filename))
            except:
                pass
