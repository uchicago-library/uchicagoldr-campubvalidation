from sys import argv
from re import match
from os.path import exists, join
from os import walk
from csv import DictReader
from shutil import move

def getRelPath(path):
    try:
        path.index('mvol')
    except ValueError:
        print('Invalid path')
        exit()

    testPath = path[path.index('mvol'):]
    if match("^mvol/\d{4}/\d{4}/\d{4}/$", testPath):
        return testPath
    else:
        return getRelPath("/".join(testPath.split("/")[1:]))

def main():
    issueFullPath = argv[1]
    issueRelPath = getRelPath(issueFullPath)
    print(issueRelPath)

    mvolNum = issueRelPath.split("/")[-4]
    volNum = issueRelPath.split("/")[-3]
    issNum = issueRelPath.split("/")[-2]

    filePrefix = "-".join(['mvol',mvolNum,volNum,issNum])

    if exists(join(issueFullPath,filePrefix+'.struct.txt')):
        structuralMetadata = join(issueFullPath,filePrefix+'.struct.txt')
        post2015 = True
    else:
        structuralMetadata = join(issueFullPath,filePrefix+'.txt')
        post2015 = False

    if post2015 ==  True:
        dirs = ['ALTO','JPEG','TIFF']
    else:
        dirs = ['jpg','pos','tif','xml']

    dirs = [join(issueFullPath,x) for x in dirs]

    idents = []
    with open(structuralMetadata,'r') as f:
        reader = DictReader(f, delimiter='\t')
        for row in reader:
            idents.append(row['object'])

    fileLists = {}
    for entry in dirs:
        fileLists[entry] = []
        for dirpath, dirnames, filenames in walk(entry):
            for filename in filenames:
                if not match(".*\.fits\.xml$", filename):
                    fileLists[entry].append(join(dirpath,filename))
        fileLists[entry].sort()

    for fileList in fileLists:
        assert(len(fileLists[fileList]) == len(idents))

    moveTups = []
    for fileList in fileLists:
        index = -1
        for filename in fileLists[fileList]:
            index += 1
            if post2015:
                newFileName = join(issueFullPath,fileList,filePrefix+"_"+idents[index][-4:])
                if 'ALTO' in fileList:
                    newFileName = newFileName + ".xml"
                if 'TIFF' in fileList:
                    newFileName = newFileName + ".tif"
                if 'JPEG' in fileList:
                    newFileName = newFileName + ".jpg"
                if newFileName != filename:
                    moveTups.append((filename, newFileName))

            else:
                newFileName = join(issueFullPath,fileList,idents[index]+"."+fileList.split("/")[-1])
                if newFileName != filename:
                    moveTups.append((filename, newFileName))

    with open(filePrefix+'.mvlog.txt','w') as f:
        for entry in moveTups:
            f.write(str(entry)+'\n')

    origins = []
    dests = []

    for entry in moveTups:
        origins.append(entry[0])
        dests.append(entry[1])

    origins=list(reversed(origins))
    dests=list(reversed(dests))

    assert(len(origins) == len(dests))

    for entry in moveTups:
        assert(origins.index(entry[0]) == dests.index(entry[1]))

    for i, origin in enumerate(origins):
        if exists(dests[i]):
            if dests[i] in origins:
                origins[origins.index(dest[i])] = dests[i]+".old"
            assert(exists(dests[i]+".old") == False)
            print(dests[i] + " --> " + dests[i] + ".old")
            move(dests[i], dests[i]+".old")
        assert(exists(dests[i]) == False)
        assert(len(origins) == len(dests))
        move(origin,dests[i])
        print(origin + " --> " + dests[i])


if __name__ == '__main__':
    main()
