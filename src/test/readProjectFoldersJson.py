import os
import json
import shutil

            
#Read Project Structure form json file
projectStructureJson = "data/projectStructure.json"
with open(projectStructureJson, 'r') as f:
    structure = json.load(f)

initFiles = structure["initFiles"]


## Create project
def createProject(projectPath,folders):
    for folder in folders.keys():
        folderPath=projectPath+"/"+folder
        print(f"Create dir folderPath {folderPath}")
    print(f"{projectPath} Project created succesfully.\n")

#Get project
projectsPath = 'D:/Projects'  # Replace with the path where you want to recreate the directories
projectStructure = structure["project"]
projectName = "testProject"
projectPath = projectsPath+"/"+projectName
createProject(projectPath,projectStructure)




######Create asset
def createAssetDirs(projectName, basePath, assetType, assetName, assetStructure, initFiles, parent):
    
    for name, sub_structure in assetStructure.items():
        newName = name.replace("assetName",assetName).replace("assetType",assetType)
        newPath = os.path.join(basePath, newName)
        newPath = os.path.normpath(newPath).replace("\\", "/")
        
        if sub_structure == 'file':  # Check if it's a file
            #Asset step index
            newPathSplit = newPath.split("/")
            index = newPathSplit.index(assetName)
            
            #Get original init file
            orig_path = "C:/Users/pepeb/Desktop/PG-Pipeline/"+initFiles[name]
            extension = os.path.splitext(orig_path)[1]
            
            #Copy file with proper name
            if parent != "preview":
                newPath = f"{basePath}/{projectName}_{assetType}_{assetName}_{newPathSplit[index+1]}_master_v000{extension}"
            else:
                newPath = f"{basePath}/{projectName}_{assetType}_{assetName}_{newPathSplit[index+1]}_master_preview_v000{extension}"
            
            #shutil.copy2(orig_path, newPath)
            print("Create file "+newPath)
            pass
        else:
            #os.makedirs(newPath, exist_ok=True)
            print("Create dir "+newPath)
            createAssetDirs(projectName,newPath, assetType, assetName, sub_structure, initFiles, name)
           
            
assetName="irex"
assetStructure = projectStructure["assets"]
assetsPath=projectPath+"/assets"
assetType="char"
createAssetDirs(projectName, assetsPath, assetType, assetName, assetStructure, initFiles, "assets")




######Create shots
def numToStr(num):
    numStr=""
    if num < 10:
        numStr="00"+str(num)
    elif num < 100:
        numStr="0"+str(num)
    elif num < 1000:
        numStr=""+str(num)
    return numStr

def createShotsDirs(projectName, basePath, ep, seq, sh, shBegin, shEnd, shotsStructure, initFiles, parent):
    
    for name, sub_structure in shotsStructure.items():
        if name!="shXXX":
            epStr=numToStr(ep)
            seqStr=numToStr(seq)
            shStr=numToStr(sh)
            
            newName = name.replace("epXXX",f"ep{epStr}").replace("seqXXX",f"seq{seqStr}")
            newPath = os.path.join(basePath, newName)
            newPath = os.path.normpath(newPath).replace("\\", "/")
            
            if sub_structure == 'file':  # Check if it's a file
                #Asset step index
                newPathSplit = newPath.split("/")
                index = newPathSplit.index("shots")
                
                #Get original init file
                orig_path = "C:/Users/pepeb/Desktop/PG-Pipeline/"+initFiles[name]
                extension = os.path.splitext(orig_path)[1]
                
                #Copy file with proper name
                if parent != "preview":
                    newPath = f"{basePath}/{projectName}_ep{epStr}_seq{seqStr}_sh{shStr}_{newPathSplit[index+4]}_master_v000{extension}"
                else:
                    newPath = f"{basePath}/{projectName}_ep{epStr}_seq{seqStr}_sh{shStr}_{newPathSplit[index+4]}_master_preview_v000{extension}"
                #shutil.copy2(orig_path, new_path)
                print("Create file "+newPath)
                pass
            else:
                #os.makedirs(new_path, exist_ok=True)
                print("Create dir "+newPath)
                createShotsDirs(projectName,newPath, ep, seq, sh, shBegin, shEnd, sub_structure, initFiles, name)
        else:
            sh=shBegin
            while sh<=shEnd:
                shStr=numToStr(sh)
                newName = name.replace("shXXX",f"sh{shStr}")
                newPath = os.path.join(basePath, newName)
                newPath = os.path.normpath(newPath).replace("\\", "/")
                createShotsDirs(projectName,newPath, ep, seq, sh, shBegin, shEnd, sub_structure, initFiles, name)
                sh+=1
            return
        
def createRestDirs(projectName, basePath, projectStructure, initFiles, parent):
    for name, sub_structure in projectStructure.items():
        
        if name!="shots" and name!="assets":
            newPath = os.path.join(basePath, name)
            newPath = os.path.normpath(newPath).replace("\\", "/")
            
            if sub_structure == 'file':  # Check if it's a file
                #Asset step index
                newPathSplit = newPath.split("/")
                index = newPathSplit.index(projectName)
                
                #Get original init file
                orig_path = "C:/Users/pepeb/Desktop/PG-Pipeline/"+initFiles[name]
                extension = os.path.splitext(orig_path)[1]
                
                #Copy file with proper name
                if parent != "preview":
                    newPath = f"{basePath}/{projectName}_{newPathSplit[index+1]}_master_v000{extension}"
                else:
                    newPath = f"{basePath}/{projectName}_{newPathSplit[index+1]}_master_preview_v000{extension}"
                #shutil.copy2(orig_path, new_path)
                print("Create file "+newPath)
                pass
            else:
                #os.makedirs(new_path, exist_ok=True)
                print("Create dir "+newPath)
                createRestDirs(projectName, newPath, sub_structure, initFiles, name)


shotsPath=projectPath+"/shots"
ep=1
seq=1
shBegin=0
shEnd=2
shotsStructure = projectStructure["shots"]
createShotsDirs(projectName, shotsPath, ep, seq, 0, shBegin, shEnd, shotsStructure, initFiles, "shots")
createRestDirs(projectName, projectPath, projectStructure, initFiles, projectName)