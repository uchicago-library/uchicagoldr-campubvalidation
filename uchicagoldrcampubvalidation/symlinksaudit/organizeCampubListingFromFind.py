from sys import argv
from operator import itemgetter
from json import dumps

inFile = argv[1]

lines = []

with open(inFile,'r') as f:
    for line in f.readlines():
        line = line.rstrip('\n')
        splits = line.split("/")
        if len(splits) != 5:
            continue
        if splits[1] != "mvol":
            continue
        lines.append(splits)

lines.sort(key = itemgetter(2, 3, 4))

mvols = {}
mvolInfo = {}

for entry in lines:
    currentMvol = entry[2]
    currentVolume = entry[3]
    currentIssue = entry[4]

    if currentMvol not in mvols:
        mvols[currentMvol] = {}

    if currentVolume not in mvols[currentMvol]:
        mvols[currentMvol][currentVolume] = []

    mvols[currentMvol][currentVolume].append(currentIssue)

with open('thewholeofcampub.json','w') as out:
    out.write(dumps(mvols, indent=4, sort_keys=True))

mvolInfo = {}

for mvol in mvols:
    mvolInfo[mvol] = {}
    mvolInfo[mvol]['Volumes'] = {}
    mvolInfo[mvol]['vols start'] = sorted(list(mvols[mvol]))[0]
    mvolInfo[mvol]['vols end'] = sorted(list(mvols[mvol]))[-1]
    projectedRangeVols = []
    for i in range(int(mvolInfo[mvol]['vols start'].lstrip("0")),int(mvolInfo[mvol]['vols end'].lstrip("0"))):
        projectedRangeVols.append(i)
    potentiallyMissingVolumes = []
    for j in projectedRangeVols:
        if str(j).zfill(4) not in mvols[mvol]:
            potentiallyMissingVolumes.append(str(j).zfill(4))
    mvolInfo[mvol]['potentially missing volumes'] = potentiallyMissingVolumes
    for volume in mvols[mvol]:
        mvolInfo[mvol]['Volumes'][volume] = {}
        mvolInfo[mvol]['Volumes'][volume]['issues start'] = sorted(list(mvols[mvol][volume]))[0]
        mvolInfo[mvol]['Volumes'][volume]['issues end'] = sorted(list(mvols[mvol][volume]))[-1]
        projectedRangeIssues = []
        try:
            start = int(mvolInfo[mvol]['Volumes'][volume]['issues start'].lstrip("0"))
        except ValueError:
            start = 0

        try:
            end = int(mvolInfo[mvol]['Volumes'][volume]['issues end'].lstrip("0"))
        except ValueError:
            end = 0
        for i in range(start,end):
            projectedRangeIssues.append(i)
        potentiallyMissingIssues = []
        for j in projectedRangeIssues:
            if str(j).zfill(4) not in mvols[mvol][volume]:
                potentiallyMissingIssues.append(str(j).zfill(4))
        mvolInfo[mvol]['Volumes'][volume]['potentially missing issues'] = potentiallyMissingIssues


with open('whatsmissingfromcampub.json','w') as sparseout:
    sparseout.write(dumps(mvolInfo, indent=4, sort_keys=True))


