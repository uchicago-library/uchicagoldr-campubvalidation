from csv import DictReader
from os import walk
from os.path import exists, isdir, join, relpath
from json import dumps
from re import match
from xml.etree.ElementTree import Element, SubElement, ElementTree
import argparse

def relList(inList, stageRoot):
    index = -1
    for entry in inList:
        index += 1
        inList[index] = relpath(inList[index], stageRoot)
    return inList


def getObjIdents(path, relPath):
    objIdents = []
    critical = []
    with open(path, 'r') as f:
        try:
            reader = DictReader(f, delimiter='\t')
            for row in reader:
                try:
                    objIdents.append(row['object'])
                except KeyError:
                    if relPath + " STRUCTURAL METADATA MALFORMED: Keys" not in critical:
                        critical.append(relPath + " STRUCTURAL METADATA MALFORMED: Keys")
                        try:
                            objIdents.append(row['Object'])
                        except Exception:
                            if relPath + " STRUCTURAL METADATA MALFORMED: Keys" not in critical:
                                critical.append(relPath + " STRUCTURAL METADATA MALFORMED: Keys")
                            objIdents = []
                            break
        except:
            if relPath + " STRUCTURAL METADATA MALFORMED: Read" not in critical:
                critical.append(relPath + " STRUCURAL METADATA MALFORMED: Read")
                objIdents = []
    return (objIdents, critical)


def validateObjIdent(objIdent, critical, relPath):
    if len(objIdent) < 1:
        if relPath + " STRUCTURAL METADATA MALFORMED: BLANK IDENTS" not in critical:
            critical.append(relPath + " STRUCTURAL METADATA MALFORMED: BLANK IDENTS")
        return (critical, "Blank")
    if len(objIdent) != 8:
        if relPath + " STRUCTURAL METADATA MALFORMED: IDENT LENGTHS" not in critical:
            critical.append(relPath + " STRUCTURAL METADATA MALFORMED: IDENT LENGTHS")
        return (critical, "Length")
    return (critical, "True")


def makeDCXML(title, date, identification, description, root, dirs):
    rootNode = Element('metadata')
    titleNode = SubElement(rootNode, 'title')
    dateNode = SubElement(rootNode, 'date')
    identifierNode = SubElement(rootNode, 'identifier')
    descriptionNode = SubElement(rootNode, 'description')

    titleNode.text = title
    dateNode.text = date
    identifierNode.text = identification
    descriptionNode.text = description
#    with open(join(root, *dirs), 'w') as out:
#        ElementTree(rootNode).write(out)


def through2014validate(path):
    shouldBeThere = []
    areThere = []
    critical = []
    objIdents = []
    valid = True

    filePrefix = 'mvol-'+"-".join(path.split('/')[-3:])
    relPath = join('mvol', *path.split('/')[-3:])
    shouldBeThere.append('jpg')
    shouldBeThere.append('pos')
    shouldBeThere.append('tif')
    shouldBeThere.append('xml')
    shouldBeThere.append(filePrefix+".dc.xml")
    shouldBeThere.append(filePrefix+".pdf")
    shouldBeThere.append(filePrefix+".txt")

    if exists(join(path, filePrefix+".txt")):
        objIdents, objCrit = getObjIdents(join(path, filePrefix + ".txt"), relPath)
        critical.extend(objCrit)

        for entry in objIdents:
            critical, alrightIdent = validateObjIdent(entry, critical, relPath)
            if alrightIdent == 'True':
                shouldBeThere.append(join('jpg', entry+".jpg"))
                shouldBeThere.append(join('pos', entry+".pos"))
                shouldBeThere.append(join('tif', entry+".tif"))
                shouldBeThere.append(join('xml', entry+".xml"))
    else:
        critical.append(relPath + " HAS NO STRUCTURAL METADATA")

    for entry in shouldBeThere:
        shouldBeThere[shouldBeThere.index(entry)] = join(path, entry)

    for dirpath, dirnames, filenames in walk(path):
        for filename in filenames:
            if not (match(".*\.fits.xml$", filename) or
                    match(".*\_$", filename) or
                    match(".*X$", filename) or
                    match(".*Y$", filename)):
                areThere.append(join(dirpath, filename))
        for dirname in dirnames:
            areThere.append(join(dirpath, dirname))

    if set(shouldBeThere).issubset(areThere):
        valid = True
    else:
        valid = False

    if len(critical) > 0:
        valid = False

    return (valid, critical, shouldBeThere, areThere, objIdents)


def from2015validate(path):
    shouldBeThere = []
    areThere = []
    critical = []
    objIdents = []
    valid = True

    filePrefix = 'mvol-'+"-".join(path.split('/')[-3:])
    relPath = join('mvol', *path.split('/')[-3:])
    shouldBeThere.append('JPEG')
    shouldBeThere.append('ALTO')
    shouldBeThere.append('TIFF')
    shouldBeThere.append(filePrefix+".dc.xml")
    shouldBeThere.append(filePrefix+".mets.xml")
    shouldBeThere.append(filePrefix+".pdf")
    shouldBeThere.append(filePrefix+".struct.txt")
    shouldBeThere.append(filePrefix+".txt")

    if exists(join(path, filePrefix+".struct.txt")):
        objIdents, objCrit = getObjIdents(join(path, filePrefix + ".struct.txt"), relPath)
        critical.extend(objCrit)

        for entry in objIdents:
            critical, alrightIdent = validateObjIdent(entry, critical, relPath)
            if alrightIdent == 'True':
                pass
            if alrightIdent == 'Blank':
                continue
            if alrightIdent == 'Length':
                entry = entry.zfill(8)
            shouldBeThere.append(join('JPEG', filePrefix+"_"+entry[-4:]+".jpg"))
            shouldBeThere.append(join('ALTO', filePrefix+"_"+entry[-4:]+".xml"))
            shouldBeThere.append(join('TIFF', filePrefix+"_"+entry[-4:]+".tif"))
    else:
        critical.append(relPath + " HAS NO STRUCTURAL METADATA")

    for entry in shouldBeThere:
        shouldBeThere[shouldBeThere.index(entry)] = join(path, entry)

    for dirpath, dirnames, filenames in walk(path):
        for filename in filenames:
            if not (match(".*\.fits.xml$", filename) or
                    match(".*\_$", filename) or
                    match(".*X$", filename) or
                    match(".*Y$", filename)):
                areThere.append(join(dirpath, filename))
        for dirname in dirnames:
            areThere.append(join(dirpath, dirname))

    if set(shouldBeThere).issubset(areThere):
        valid = True
    else:
        valid = False

    if len(critical) > 0:
        valid = False

    return (valid, critical, shouldBeThere, areThere, objIdents)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a University of Chicago campus publication \
                     directory against a supplied CSV."
    )
    parser.add_argument('csv_file_path',
                        help='The file path to the CSV')
    parser.add_argument('stage_root',
                        help='The root path down to (but not including) \
                        the mvol directory')
    parser.add_argument('outfile',
                        help='The file path for the output file')
    args = parser.parse_args()
    csvFilePath = args.csv_file_path
    stageRoot = args.stage_root
    outfile = args.outfile
#    csvFilePath = argv[1]
#    stageRoot = argv[2]
#    outfile = argv[3]

    report = {}

    dirList = []

    with open(csvFilePath, 'r') as csvFile:
        reader = DictReader(csvFile)

        for row in reader:
            if row['Identification'] == "":
                continue

            dirs = row['Identification'].split("-")

            try:
                assert(isdir((join(stageRoot, *dirs))))
                dirList.append(join(stageRoot, *dirs))

            except AssertionError:
                report[join(*dirs)] = {}
                report[join(*dirs)]['valid'] = "False"
                report[join(*dirs)]['critical'] = ['COMPLETELY MISSING']
                report[join(*dirs)]['missing'] = []
                report[join(*dirs)]['superfluous'] = []
                report[join(*dirs)]['areThere'] = []
                report[join(*dirs)]['shouldBeThere'] = []
                continue

            try:
                makeDCXML(row['Title'], row['Date'],
                          row['Identification'], row['Description'],
                          stageRoot, dirs)
            except Exception as e:
                print(e)
                print("Creation of .dc.xml failed for " +
                      join(stageRoot, *dirs))

        for entry in dirList:
            print("checking " + entry)
            relPath = relpath(entry, stageRoot)

            report[relPath] = {}

            from2015 = False
            for dirpath, dirnames, filenames in walk(entry):
                for filename in filenames:
                    if bool(match(".*\.struct\.txt$", filename)):
                        from2015 = True

            through2014 = False
            for dirpath, dirnames, filenames in walk(entry):
                for filename in filenames:
                    if bool(match(".*\.txt$", filename)):
                        through2014 = True

            if from2015 and through2014:
                through2014 = False

            if from2015:
                report[relPath]['detected spec'] = 'from2015'
                result = from2015validate(entry)
            elif through2014:
                report[relPath]['detected spec'] = 'through2014'
                result = through2014validate(entry)
            else:
                report[relPath]['detected spec'] = 'undetermined'
                result = None

            if result:
                valid, critical, shouldBeThere, areThere, objIdents = result
            else:
                valid, critical, shouldBeThere, areThere, objIdents = (False,
                                                            ['NO SPECIFICATION \
                                                             DETECTED'], [], [],
                                                                       [])

            missing = set(shouldBeThere).difference(set(areThere))
            missing = list(missing)

            superfluous = set(areThere).difference(set(shouldBeThere))
            superfluous = list(superfluous)

            missing = relList(missing, stageRoot)
            superfluous = relList(superfluous, stageRoot)
            areThere = relList(areThere, stageRoot)
            shouldBeThere = relList(shouldBeThere, stageRoot)

            report[relPath]['valid'] = str(valid)
            report[relPath]['critical'] = critical
            report[relPath]['missing'] = missing
            report[relPath]['superfluous'] = superfluous
            report[relPath]['areThere'] = areThere
            report[relPath]['shouldBeThere'] = shouldBeThere
            report[relPath]['objIdents'] = objIdents

        with open(outfile, 'w') as out:
            out.write(dumps(report, sort_keys=True, indent=4))

if __name__ == '__main__':
    main()
