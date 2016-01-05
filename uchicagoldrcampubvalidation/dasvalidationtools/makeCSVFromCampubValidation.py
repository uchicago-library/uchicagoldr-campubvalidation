from json import load
import argparse
from csv import DictWriter
from os.path import join

def main():
    parser = argparse.ArgumentParser(
        description='Read the validation produced by validating a campus \
        publication directory against a CSV and produce a report.'
    )
    parser.add_argument('inputFilePath',
                        help='The filepath of the JSON dump.')
    parser.add_argument('outputFilePath',
                        help='The filepath to write the resulting csv to')
    parser.add_argument('--errors', dest='just_errors', action='store_true',
                        default=False,
                        help='Print only rows which are invalid')

    args = parser.parse_args()
    inFile = args.inputFilePath
    outpath = args.outputFilePath

    wholeDict = load(open(inFile,'r'))

    with open(outpath, 'w') as csvfile:
        header = ['mvolID','objID','spec','valid','tif','jpg','pos','xml','alto']
        writer = DictWriter(csvfile, fieldnames=header)
        writer.writeheader()

        tote = len(wholeDict)
        current = 0
        keyList = []
        for entry in wholeDict:
            keyList.append(entry)
        keyList.sort()

        for entry in keyList:
            current += 1
            print(entry+": "+str(current)+"/"+str(tote))
            if "COMPLETELY MISSING" in wholeDict[entry]['critical']:
                rowDict = {}
                rowDict['mvolID'] = "-".join(entry.split("/")[0:4])
                for column in ['objID','valid','tif','jpg','pos','xml','alto','spec']:
                    rowDict[column] = 'MISSING'
                writer.writerow(rowDict)
                continue
            try:
                wholeDict[entry]['objIdents'].sort()
                for ident in wholeDict[entry]['objIdents']:
                    rowDict = {}
                    try:
                        if wholeDict[entry]['detected spec'] == 'through2014':
                            rowDict['mvolID'] = "-".join(entry.split("/")[0:4])
                            rowDict['objID'] = ident
                            rowDict['spec'] = wholeDict[entry]['detected spec']

#                            print('Looking for: '+join(entry,'tif',ident+".tif"))
                            if join(entry,'tif',ident+".tif") in wholeDict[entry]['areThere']:
                                rowDict['tif'] = 'Y'
                            else:
                                rowDict['tif'] = 'N'

                            if join(entry,'pos',ident+".pos") in wholeDict[entry]['areThere']:
                                rowDict['pos'] = 'Y'
                            else:
                                rowDict['pos'] = 'N'

                            if join(entry,'jpg',ident+".jpg") in wholeDict[entry]['areThere']:
                                rowDict['jpg'] = 'Y'
                            else:
                                rowDict['jpg'] = 'N'

                            if join(entry,'xml',ident+".xml") in wholeDict[entry]['areThere']:
                                rowDict['xml'] = 'Y'
                            else:
                                rowDict['xml'] = 'N'

                            if join(entry,'ALTO',ident+".xml") in wholeDict[entry]['areThere']:
                                rowDict['alto'] = 'Y'
                            else:
                                rowDict['alto'] = 'N'

                            if rowDict['tif'] == 'Y' and \
                                    rowDict['jpg'] == 'Y' and \
                                    rowDict['pos'] == 'Y' and \
                                    rowDict['xml'] == 'Y':
                                rowDict['valid'] = 'Y'
                            else:
                                rowDict['valid'] = 'N'

                        if wholeDict[entry]['detected spec'] == 'from2015':
                            rowDict['mvolID'] = "-".join(entry.split("/")[0:4])
                            rowDict['objID'] = ident
                            rowDict['spec'] = wholeDict[entry]['detected spec']

                            if join(entry,'ALTO',rowDict['mvolID']+"_"+ident[-4:]+'.xml') in wholeDict[entry]['areThere']:
                                rowDict['alto'] = 'Y'
                            else:
                                rowDict['alto'] = 'N'

                            if join(entry,'TIFF',rowDict['mvolID']+"_"+ident[-4:]+'.tif') in wholeDict[entry]['areThere']:
                                rowDict['tif'] = 'Y'
                            else:
                                rowDict['tif'] = 'N'

                            if join(entry,'JPEG',rowDict['mvolID']+"_"+ident[-4:]+'.jpg') in wholeDict[entry]['areThere']:
                                rowDict['jpg'] = 'Y'
                            else:
                                rowDict['jpg'] = 'N'

                            if join(entry,'XML',rowDict['mvolID']+"_"+ident[-4:]+'.xml') in wholeDict[entry]['areThere']:
                                rowDict['xml'] = 'Y'
                            else:
                                rowDict['xml'] = 'N'

                            if join(entry,'POS',rowDict['mvolID']+"_"+ident[-4:]+'.pos') in wholeDict[entry]['areThere']:
                                rowDict['pos'] = 'Y'
                            else:
                                rowDict['pos'] = 'N'

                            if rowDict['tif'] == 'Y' and \
                                    rowDict['jpg'] == 'Y' and \
                                    rowDict['alto'] == 'Y':
                                rowDict['valid'] = 'Y'
                            else:
                                rowDict['valid'] = 'N'

                            if args.just_errors:
                                if rowDict['valid'] == 'Y':
                                    continue

                            writer.writerow(rowDict)

                    except Exception as e:
                        print(e)
                        rowDict['mvolID'] = entry
                        rowDict['objID'] = ident
                        for column in ['spec','valid','tif','jpg','pos','xml','alto','spec']:
                            rowDict[column] = 'ident error'
                        writer.writerow(rowDict)

            except KeyError:
                print("Key Error")
                rowDict = {}
                rowDict['mvolID'] = entry
                for column in ['objID','spec','valid','tif','jpg','pos','xml','alto', 'spec']:
                    rowDict[column] = 'no struct md'

                writer.writerow(rowDict)

if __name__ == '__main__':
    main()
