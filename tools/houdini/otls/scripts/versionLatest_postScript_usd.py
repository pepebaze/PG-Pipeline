import hou
import os
from pathlib import Path

ropName = hou.pwd().path()
rn= hou.node(ropName)
fname=rn.parm("lopoutput")
path=fname.eval()

pathSplit=path.split("/")
filename = pathSplit[len(pathSplit)-1]

folderPathSplit=pathSplit[:-1]
folderPath='/'.join(folderPathSplit)

version=folderPathSplit[len(folderPathSplit)-1]

folderLatest="/".join(folderPathSplit).replace(version,"latest")

try:
    os.mkdir(folderLatest)
except:
    pass

filenameLatest=filename.replace(version,"latest")

linkPath=folderLatest+"/"+filenameLatest

try:
    os.remove(linkPath)
except Exception as error:
    print(error)

try:
    os.link(path,linkPath)
except:
    pass
else:
    print("Asset/Shot published at: "+linkPath+"\n")