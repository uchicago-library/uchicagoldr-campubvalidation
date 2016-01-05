import sys
from os.path import join, isdir, exists, split

from uchicagoldr.bash_cmd import BashCommand

inFile = sys.argv[1]

fileList = []

stageRoot = '/Volumes/tr/campubplchldr'

with open(inFile, 'r') as f:
    for line in f.readlines():
        fileList.append(line.rstrip('\n'))

for entry in fileList:
    if not 'mvol' in entry:
        continue
    mvolDown = entry[entry.index('mvol'):]
    mvolDownDirs, filename = split(mvolDown)
    splits = mvolDownDirs.split("/")

    i = -1
    while i < len(splits):
        i+=1
        if not exists(join(stageRoot,*splits[0:i+1])):
            mkdirCmd = BashCommand(['mkdir', '-p', join(stageRoot,*splits[0:i+1])])
            assert(mkdirCmd.run_command()[0])

    lnCommand = BashCommand(['ln', '-s', entry, join(stageRoot,mvolDown)])
    assert(lnCommand.run_command()[0])
