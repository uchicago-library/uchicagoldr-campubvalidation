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
        if match("mvol-\d{4}-\d{4}-\d{4}\.struct\.txt$", filename) or \
        match("mvol-\d{4}-\d{4}-\d{4}\.txt$", filename):
            try:
                with open(join(dirpath, filename), 'r') as f:
                    reader = DictReader(f, delimiter='\t')
                    assert('object' in reader.fieldnames)
                    notzeropadded = False
                    for row in reader:
                        if len(row['object']) < 8:
                            notzeropadded = True
                            break
                    if notzeropadded:
                        print("Editing " + join(dirpath, filename))
                        with open(join(dirpath, filename)+".new",'w') as out:
                            with open(join(dirpath, filename),'r') as inFile:
                                newreader = DictReader(inFile, delimiter = '\t')
                                writer = DictWriter(out, fieldnames=newreader.fieldnames, delimiter='\t',quoting=QUOTE_MINIMAL)
                                writer.writeheader()
                                for row in newreader:
                                    rowDict = {}
                                    for header in newreader.fieldnames:
                                        if header == 'object':
                                            print(row[header])
                                            if len(row[header]) < 8:
                                                row[header] = row[header].zfill(8)
                                        rowDict[header] = row[header]
                                    writer.writerow(rowDict)
                        move(join(dirpath, filename), join(dirpath, filename+'.old'))
                        assert(isfile(join(dirpath, filename)) == False)
                        move(join(dirpath, filename+'.new'), join(dirpath, filename))
            except Exception as e:
                print(e)
