from json import load, dumps
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Read the validation produced by validating a campus \
        publication directory against a CSV and produce a report.'
    )
    parser.add_argument('inputFilePath',
                        help='The filepath of the JSON dump.')
    args = parser.parse_args()
    inFile = args.inputFilePath

    wholeDict = load(open(inFile,'r'))

    maxDispLen = 14

    valid = 0
    invalid = 0
    validIssues = []
    invalidIssues = []
    completelyMissing = []
    issuesWithSuperfluous = []
    issuesWithCritical = []

    keyList = []
    for entry in wholeDict:
        keyList.append(entry)
    keyList.sort()

    for entry in keyList:
        if wholeDict[entry]['valid'] == 'True':
            valid += 1
            validIssues.append(entry)
        else:
            invalid += 1
            invalidIssues.append(entry)

        if len(wholeDict[entry]['superfluous']) > 0:
            issuesWithSuperfluous.append(entry)

        if len(wholeDict[entry]['critical']) > 0:
            issuesWithCritical.append(entry)

        if 'COMPLETELY MISSING' in wholeDict[entry]['critical']:
            completelyMissing.append(entry)


    total = len(wholeDict)


    print("Valid: ".ljust(maxDispLen) + str(valid))
    print("Critical: ".ljust(maxDispLen) +str(len(issuesWithCritical)))
    print("Invalid: ".ljust(maxDispLen) + str(invalid))
    print("Total: ".ljust(maxDispLen) + str(total))
    print()

    print("---ERRORS---")
    print("--DIRECTORIES MISSING--")
    print("\tCount: "+str(len(completelyMissing)))
    for entry in completelyMissing:
        print("\t"+entry)

    print()

    print("--INVALID ISSUES--")
    for entry in invalidIssues:
        print(entry)
        print("\t--CRITICAL--")
        for crit in ["\t"+x for x in wholeDict[entry]['critical']]:
            print(crit)
        print()
        print("\t--MISSING--")
        for miss in sorted(["\t"+x for x in wholeDict[entry]['missing']]):
            print(miss)
        print('\n')

    #print("--ISSUES WITH SUPERFLUOUS FILES--")
    #for entry in issuesWithSuperfluous:
    #    print(entry)
    #    for sup in ["\t"+x for x in wholeDict[entry]['superfluous']].sort():
    #        print(sup)
    #    print('\n')

if __name__ == '__main__':
    main()
