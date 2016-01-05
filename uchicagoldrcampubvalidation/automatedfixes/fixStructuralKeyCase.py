from sys import argv
from os.path import isdir, join, isfile
from os import walk
from re import match
from csv import DictReader, QUOTE_MINIMAL, DictWriter
from shutil import move

root = argv[1]

assert(isdir(root))

structuralMetadataFiles = []

for dirpath, dirnames, filenames in walk(root):
    if match(".*\/mvol\/\d{4}\/\d{4}\/\d{4}", dirpath):
        print("Stopping recursion at "+dirpath)
        del dirnames[:]
    for filename in filenames:
        print("Scanning " + filename)
        if match("mvol-\d{4}-\d{4}-\d{4}\.struct\.txt$", filename) or \
        match("mvol-\d{4}-\d{4}-\d{4}\.txt$", filename):
            print("Acting on " + filename)
            try:
                with open(join(dirpath, filename), 'r') as f:
                    reader = DictReader(f, delimiter='\t')
                    assert('object' in reader.fieldnames or
                           'Object' in reader.fieldnames)
                    if reader.fieldnames != [x.lower() for x in reader.fieldnames]:
                        print("Editing " + join(dirpath, filename))
                        reader.fieldnames = [x.lower() for x in reader.fieldnames]
                        with open(join(dirpath, filename)+".new",'w') as out:
                            writer = DictWriter(out, fieldnames=reader.fieldnames, delimiter='\t',quoting=QUOTE_MINIMAL)
                            writer.writeheader()
                            for row in reader:
                                rowDict = {}
                                for header in reader.fieldnames:
                                    rowDict[header] = row[header]
                                writer.writerow(rowDict)
                        move(join(dirpath, filename), join(dirpath, filename+'.old'))
                        assert(isfile(join(dirpath, filename)) == False)
                        move(join(dirpath, filename+'.new'), join(dirpath, filename))
            except Exception as e:
                print(e)
