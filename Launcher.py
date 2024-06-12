import os
import json
import math
import shutil
import subprocess
from pathlib import Path
import customtkinter as tk
from PIL import Image, ImageTk
from dotenv import dotenv_values
from tkinter.filedialog import askopenfilename

#### INIT ####
###############################################

## Read Project Structure form json file
projectStructureJson = "data/projectStructure.json"
try:    
    with open(projectStructureJson, 'r') as f:
        structure = json.load(f)
except FileNotFoundError:
        structure={}
projectStructure = structure["project"]
assetStructure = projectStructure["assets"]
shotsStructure = projectStructure["shots"]

initFiles = structure["initFiles"]
hipSrc = initFiles.get('houdini')
purerefSrc = initFiles.get('pureref')
videoSrc = initFiles.get('video')
imageSrc = initFiles.get('image')
nukeSrc = initFiles.get('nuke')
davinciSrc = initFiles.get('davinci')

assetTypes=structure["assetTypes"]

##Get projects
#Get projects folder path
envVars = dotenv_values('data/.env')
projectsPath=envVars.get("PROJECTS")

try:
    projectsList=os.listdir(projectsPath)
except:
    projectsList=[" "]

if len(projectsList)==0:
    projectsList=[""]
    
currentDir = os.getcwd()
print("PG Pipeline 1.0, built 2024.")
print(f"Directory: {currentDir}\n")

    
###############################################
#### END INIT ####




#### START GUI INIT ####
###############################################

##Define root
def center_window(root, width=300, height=200):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y-100))
    
    
def messageWindow(root, title, text, type):
    addAppWindow = tk.CTkToplevel(root)
    addAppWindow.title(title)
    center_window(addAppWindow,700,150)
    addAppWindow.resizable(False,False)
    addAppWindow.attributes('-topmost',True)
    addAppWindow.focus()
    
    iconPath = "data/icons/"+type
    addAppWindow.after(250, lambda: addAppWindow.iconbitmap(iconPath+".ico"))
    
        
    frame = tk.CTkFrame(addAppWindow,bg_color="transparent",fg_color="transparent")
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    icon = Image.open(iconPath+".png").resize((24,24))
    icon_picture = tk.CTkImage(icon,size=(24,24))
    
    icon = tk.CTkLabel(frame,image=icon_picture,text="")
    icon.grid(row=0,column=0)
    label = tk.CTkLabel(frame,text=text,padx=10,)
    label.grid(row=0,column=1)
    

    
root = tk.CTk()
root.title("PG Pipeline")
root.iconbitmap("data/icons/appIcon.ico")
root.resizable(False,True)
center_window(root,720,375)

if os.path.exists(projectsPath)==False:
    messageWindow(root, "Launch Failed", f"Warning: Projects dir {projectsPath} doesn't exists.", "warning")


##Create tab view
tabview = tk.CTkTabview(root, width=250)
tabview.pack(expand=1, fill='both')
tabview.add("Launcher")
tabview.add("Projects")
tabview.add("Shots")
tabview.add("Assets")

###############################################
#### END GUI INIT ####



    
#### PROJECTS TAB ####
###############################################

##GUI##
frameProjects=tk.CTkFrame(master=tabview.tab('Projects'))
frameProjects.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#Insert path
labelPath = tk.CTkLabel(frameProjects,text="Create New Project",font=("Arial",16),padx=20,pady=20,)
labelPath.grid(row=0,column=0,sticky="w")

#Insert project name
labelProjectName = tk.CTkLabel(frameProjects,text="Project Name ",font=("Arial",12),padx=20,pady=20,)
eProjectName = tk.CTkEntry(frameProjects,width=200,font=("Arial",12))
eProjectName.insert(0,"projectName")
labelProjectName.grid(row=1,column=0,sticky="w")
eProjectName.grid(row=1,column=1)

#Button Create Project
buttonCreateProject=tk.CTkButton(frameProjects, text="Create New",command=lambda : createProject())
buttonCreateProject.grid(row=2,column=1,sticky="e")
##END GUI##

##FUNCTIONS##
## Create project dirs
def createProjectDirs(projectPath,projectStructure):
    try:
        os.mkdir(projectPath)
    except OSError as error:
        return False
        
    for folder in projectStructure.keys():
        folderPath=projectPath+"/"+folder
        try:
            os.mkdir(folderPath)
        except OSError as error:
            return False
        print(f"Create dir {folderPath}")
    return True

#Create rest project dirs
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
                origPath = "C:/Users/pepeb/Desktop/PG-Pipeline/"+initFiles[name]
                extension = os.path.splitext(origPath)[1]
                
                #Copy file with proper name
                if parent != "preview":
                    newPath = f"{basePath}/{projectName}_{newPathSplit[index+1]}_master_v000{extension}"
                else:
                    newPath = f"{basePath}/{projectName}_{newPathSplit[index+1]}_master_preview_v000{extension}"
                    
                if os.path.exists(newPath) == False:
                    try:
                        shutil.copy2(origPath, newPath)
                        print("Create file "+newPath)
                    except:
                        pass
                
            else:
                try:
                    os.mkdir(newPath)
                    print("Create dir "+newPath)
                except:
                    pass
                createRestDirs(projectName, newPath, sub_structure, initFiles, name)
    

#Create project
def createProject():
    
    if os.path.exists(projectsPath)==False:
        messageWindow(root, "Error", f"Error: Projects dir {projectsPath} doesn't exists.", "error")
        return
    
    projectName=eProjectName.get()
    projectPath=projectsPath+"/"+projectName
    
    if projectName in projectsList:
        messageWindow(root, "Error", f"Error: Project {projectName} already exists.", "error")
        return
    
    print("\n******************************")
    print("\nPROJECT BUILDER\n")
    
    if projectName!="" and len(projectName)>= 3 and any(char.isdigit() for char in projectName) == False:
        
        if createProjectDirs(projectPath,projectStructure) == False:        
            message = "Error: Failed to create "+projectName+" project.\n"
            print(message+"\n")
            messageWindow(root,"Project Creation Failed",message,"error")
        else:
            createRestDirs(projectName, projectPath, projectStructure, initFiles, projectName)
            projectsList.append(projectName)
            optionmenu_Projects1.configure(values=projectsList)
            optionmenu_Projects2.configure(values=projectsList)
            optionmenu_Projects3.configure(values=projectsList)
                
            message = f"Project {projectName} has been successfully created."
            print(message+"\n")
            messageWindow(root,"Project Created",message,"info")
            
            eProjectName.delete(0, tk.END)
            eProjectName.insert(0,"")
        
    else:
        message = "Error: The project name "+projectName+" is not a valid name.\nIt must have 3 or more letters and not contain digits."
        print(message+"\n")
        messageWindow(root,"Project Creation Failed",message,"error")
    print("******************************\n")     
##END FUNCTIONS##


###############################################
#### END PROJECTS TAB ####




#### SHOTS TAB ####
###############################################

##GUI##
frameShots=tk.CTkFrame(master=tabview.tab('Shots'))
frameShots.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
labelProject = tk.CTkLabel(frameShots,text="Project ",font=("Arial",12),padx=20,pady=20,)
labelProject.grid(row=0,column=0,sticky="w")
optionmenu_Projects1 = tk.CTkOptionMenu(frameShots,dynamic_resizing=False,values=projectsList)
optionmenu_Projects1.grid(row=0,column=1,sticky="w")

#Insert Episode
labelEspisode = tk.CTkLabel(frameShots,text="Episode ",font=("Arial",12),padx=20,pady=20,)
eEpisode = tk.CTkEntry(frameShots,width=140,font=("Arial",12))
eEpisode.insert(0,"0")
labelEspisode.grid(row=1,column=0,sticky="w")
eEpisode.grid(row=1,column=1,sticky="w")

#Insert Sequence
labelSequence = tk.CTkLabel(frameShots,text="Sequence ",font=("Arial",12),padx=20,pady=20,)
eSequence = tk.CTkEntry(frameShots,width=140,font=("Arial",12))
eSequence.insert(0,"0")
labelSequence.grid(row=2,column=0,sticky="w")
eSequence.grid(row=2,column=1,sticky="w")

#Insert Shot
labelShot = tk.CTkLabel(frameShots,text="Shots ",font=("Arial",12),padx=20,pady=20,)
eShotBegin = tk.CTkEntry(frameShots,width=140,font=("Arial",12))
eShotBegin.insert(0,"0")
eShotEnd = tk.CTkEntry(frameShots,width=140,font=("Arial",12))
eShotEnd.insert(0,"0")
labelShot.grid(row=3,column=0,sticky="w")
eShotBegin.grid(row=3,column=1,sticky="w")
eShotEnd.grid(row=3,column=2,sticky="w")

#Button Create Shot
buttonCreateShot=tk.CTkButton(frameShots, text="Create",command=lambda : createShot())
buttonCreateShot.grid(row=4,column=2,sticky="e")

##END GUI##

##FUNCTIONS##
#Num to str function -> Converts 23 to 023, 7 to 007, etc.
def numToStr(num):
    numStr=""
    if num < 10:
        numStr="00"+str(num)
    elif num < 100:
        numStr="0"+str(num)
    elif num < 1000:
        numStr=""+str(num)
    return numStr

#Create shots dirs
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
                origPath = "C:/Users/pepeb/Desktop/PG-Pipeline/"+initFiles[name]
                extension = os.path.splitext(origPath)[1]
                
                #Copy file with proper name
                if parent != "preview":
                    newPath = f"{basePath}/{projectName}_ep{epStr}_seq{seqStr}_sh{shStr}_{newPathSplit[index+4]}_master_v000{extension}"
                else:
                    newPath = f"{basePath}/{projectName}_ep{epStr}_seq{seqStr}_sh{shStr}_{newPathSplit[index+4]}_master_preview_v000{extension}"
                    
                if os.path.exists(newPath) == False:
                    try:
                        shutil.copy2(origPath, newPath)
                        print("Create file "+newPath)
                    except:
                        pass
            else:
                if os.path.exists(newPath) == False:
                    try:
                        os.makedirs(newPath, exist_ok=True)
                        print("Create dir "+newPath)
                    except:
                        pass
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


#Create shots
def createShot():
    
    if os.path.exists(projectsPath)==False:
        messageWindow(root, "Error", f"Error: Projects dir {projectsPath} doesn't exists.", "error")
        return
    
    print("\n******************************")
    print("\nSHOT BUILDER\n")
    currentProject=optionmenu_Projects1.get()
    if currentProject=="":
        messageWindow(root, "Error", f"Error: Select a valid Project or create a new one first.", "error")
        return
    
    if eEpisode.get().isdigit() and eSequence.get().isdigit() and eShotBegin.get().isdigit() and eShotEnd.get().isdigit() and int(eShotBegin.get())<=int(eShotEnd.get()):
        currentProject=optionmenu_Projects1.get()
        shotsPath=projectsPath+"/"+currentProject+"/shots"
        
        ep=int(eEpisode.get())
        seq=int(eSequence.get())
        shBegin=int(eShotBegin.get())
        shEnd=int(eShotEnd.get())
        
        createShotsDirs(currentProject, shotsPath, ep, seq, 0, shBegin, shEnd, shotsStructure, initFiles, "shots")
        
        message = f"Shots have been successfully created."
        print(message+"\n")
        messageWindow(root,"Shots Created",message,"info")
    else:
        message = "Error: Please introduce positive integers only.\nShot Begin should be less or equal than Shot End."
        print(message+"\n")
        messageWindow(root,"Project Creation Failed",message,"error")
    print("******************************\n")
##END FUNCTIONS##

###############################################
#### END SHOTS TAB ####




#### ASSETS TAB ####
###############################################

##START GUI##
frameAssets=tk.CTkFrame(master=tabview.tab('Assets'))
frameAssets.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

labelProject2 = tk.CTkLabel(frameAssets,text="Project ",font=("Arial",12),padx=20,pady=20,)
labelProject2.grid(row=0,column=0,sticky="w")
optionmenu_Projects2 = tk.CTkOptionMenu(frameAssets,dynamic_resizing=False,values=projectsList)
optionmenu_Projects2.grid(row=0,column=1)

labelassetType = tk.CTkLabel(frameAssets,text="Asset Type ",font=("Arial",12),padx=20,pady=20,)
labelassetType.grid(row=1,column=0,sticky="w")
optionmenu_assetTypes = tk.CTkOptionMenu(frameAssets,dynamic_resizing=False,values=assetTypes)
optionmenu_assetTypes.grid(row=1,column=1)

#Insert Asset Name
labelAssetName = tk.CTkLabel(frameAssets,text="Asset Name ",font=("Arial",12),padx=20,pady=20,)
eAssetName = tk.CTkEntry(frameAssets,width=140,font=("Arial",12))
eAssetName.insert(0,"assetName")
labelAssetName.grid(row=2,column=0,sticky="w")
eAssetName.grid(row=2,column=1,sticky="w")

#Button Create Asset
buttonCreateAsset=tk.CTkButton(frameAssets, text="Create",command=lambda : createAsset())
buttonCreateAsset.grid(row=3,column=1,sticky="e")

##END GUI##

##FUNCTIONS##
##Create asset dirs
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
            origPath = "C:/Users/pepeb/Desktop/PG-Pipeline/"+initFiles[name]
            extension = os.path.splitext(origPath)[1]
            
            #Copy file with proper name
            if parent != "preview":
                newPath = f"{basePath}/{projectName}_{assetType}_{assetName}_{newPathSplit[index+1]}_master_v000{extension}"
            else:
                newPath = f"{basePath}/{projectName}_{assetType}_{assetName}_{newPathSplit[index+1]}_master_preview_v000{extension}"
            
            if os.path.exists(newPath) == False:
                try:
                    shutil.copy2(origPath, newPath)
                    print("Create file "+newPath)
                except:
                    pass
        else:
            if os.path.exists(newPath) == False:
                try:
                    os.makedirs(newPath, exist_ok=True)
                    print("Create dir "+newPath)
                except:
                    pass
            createAssetDirs(projectName,newPath, assetType, assetName, sub_structure, initFiles, name)
            
#Create asset
def createAsset():
    
    if os.path.exists(projectsPath)==False:
        messageWindow(root, "Error", f"Error: Projects dir {projectsPath} doesn't exists.", "error")
        return
    
    print("\n******************************")
    print("\nASSET BUILDER\n")
    
    currentProject=optionmenu_Projects2.get()
    if currentProject=="":
        messageWindow(root, "Error", f"Error: Select a valid Project or create a new one first.", "error")
        return
    
    assetName=eAssetName.get()
    
    if len(assetName) >= 2 and any(char.isdigit() for char in assetName) == False:
        
        assetType=optionmenu_assetTypes.get()    
        
        
        assetsPath=projectsPath+"/"+currentProject+"/assets"
        assetPath=assetsPath+"/"+assetType+"/"+assetName
        
        if os.path.exists(assetPath) == False:
            createAssetDirs(currentProject, assetsPath, assetType, assetName, assetStructure, initFiles, "assets")
            eAssetName.delete(0, tk.END)
            eAssetName.insert(0,"")
            message = "Asset "+assetName+" has been successfully created."
            print(message+"\n")
            messageWindow(root,"Asset Created",message,"info")
        else:
            message = "Error: "+assetName+" asset already exists."
            print(message+"\n")
            messageWindow(root,"Asset Creation Failed",message,"error")
        
    else:
        message = "Error: The asset name "+assetName+" is not a valid name.\nIt must have 2 or more letters and not contain digits."
        print(message+"\n")
        messageWindow(root,"Asset Creation Failed",message,"error")
    print("******************************\n")
    
##END FUNCTIONS##

###############################################
#### END ASSETS TAB ####




#### LAUNCHER TAB ####
###############################################

frameLauncher=tk.CTkFrame(tabview.tab('Launcher'))
frameLauncher.pack(fill="both",expand=1)

optionmenu_Projects3 = tk.CTkOptionMenu(frameLauncher,dynamic_resizing=False,values=projectsList)
optionmenu_Projects3.pack()

#Add Scroll Frame
scrollFrame = tk.CTkScrollableFrame(frameLauncher)
scrollFrame.pack(fill="both",expand=1)

appsFrame = tk.CTkFrame(scrollFrame)
appsFrame.pack()

#Apply environment variables in ".env" file
def addEnvVars():
    currentProject=optionmenu_Projects3.get()
    
    #Set current project env variables
    os.environ['PROJECT'] = projectsPath+"/"+currentProject
    
    #Set env variables from .env file
    for var, value in envVars.items():
        # Optionally expand any environment variable references within the values
        expanded_var = os.path.expandvars(value)
        
        if os.path.exists(expanded_var):
            expanded_var = os.path.abspath(expanded_var)
            
        expanded_var = os.path.normpath(expanded_var).replace("\\", "/")
        os.environ[var] = expanded_var
        print(expanded_var)
    

#Execute apps function
def executeApp(app):
    
    if os.path.exists(projectsPath)==False:
        messageWindow(root, "Error", f"Error: Projects dir {projectsPath} doesn't exists.", "error")
        return
    currentProject=optionmenu_Projects3.get()
    if currentProject=="":
        messageWindow(root, "Error", f"Error: Select a valid Project or create a new one first.", "error")
        return
    
    print(f"Launching {app["name"]} ")
    # Set the environment variables
    addEnvVars()

    # Path to the .exe file
    exe_path = app["path"]
    HOMEDRIVE = os.getenv('HOMEDRIVE')
    HOMEPATH = os.getenv('HOMEPATH')
    dir_path = HOMEDRIVE+HOMEPATH

    # Check if the .exe file exists
    try:
        # Launch the .exe file
        subprocess.Popen([exe_path], cwd=dir_path)
        print(f"Successfully launched {exe_path}")
    except Exception as e:
        message = f"Failed to launch {app["name"]} {app["version"]}: \n{e}"
        print(message+"\n")
        messageWindow(root,"App Launch Failed",message,"error")

#Clear frame function
def clearFrame(frame):
   for widgets in frame.winfo_children():
      widgets.destroy()

#Add apps to scroll frame function
def addAppsButtons(apps):
    clearFrame(appsFrame)
    for index, (app_key, app_info) in enumerate(apps.items()):
        # Load app icon
        appIcon = Image.open(app_info["icon"]).resize((128,128))
        button_picture = tk.CTkImage(appIcon,size=(128,128))
        
        # Load info
        version = app_info["version"]
        name = app_info["name"]
        button = tk.CTkButton(appsFrame,image=button_picture,text=name+" "+version,fg_color="transparent",compound="top",command=lambda app=app_info : executeApp(app))
        button.grid(row=math.floor(index/3),column=index%3,pady=10,padx=25)

# Get apps dictionary
appsJson = "data/apps.json"
# Try to read the existing JSON file
try:
    with open(appsJson, 'r') as json_file:
        apps = json.load(json_file)
        num=len(apps)
except FileNotFoundError:
    # If the file does not exist, initialize an empty dictionary
    apps = {}
    
addAppsButtons(apps)

#Add New App function
def getFilePath(entry,rel):
    absolute_path = askopenfilename()
    if rel == True:
        try:
            relative_path = os.path.relpath(absolute_path, start=currentDir)
        except:
            relative_path=absolute_path
    else:
        relative_path=absolute_path

    if absolute_path != "":
        entry.delete(0,tk.END)
        entry.insert(0,relative_path)
    
    
    
#Add App function
def addAppEvent():
    buttonAddApp.configure(state="disabled")
    
    def closeAddAppWindow():
        buttonAddApp.configure(state="enable")
        
    
    #filename = askopenfilename()
    addAppWindow = tk.CTkToplevel(frameLauncher)
    addAppWindow.title("Add App")
    center_window(addAppWindow,325,250)
    addAppWindow.resizable(False,False)
    addAppWindow.attributes('-topmost',True)
    
    def closeAddAppWindow():
        buttonAddApp.configure(state="enable")
        addAppWindow.destroy()
        
    addAppWindow.protocol("WM_DELETE_WINDOW",closeAddAppWindow)
    
    #App Name
    labelAppName = tk.CTkLabel(addAppWindow,text="Name ",font=("Arial",12),padx=20,pady=20,)
    eAppName = tk.CTkEntry(addAppWindow,width=200,font=("Arial",12))
    eAppName.insert(0,"")
    labelAppName.grid(row=1,column=0,sticky="w")
    eAppName.grid(row=1,column=1)
    
    #App Version
    labelAppVersion = tk.CTkLabel(addAppWindow,text="Version ",font=("Arial",12),padx=20,pady=20,)
    eAppVersion = tk.CTkEntry(addAppWindow,width=200,font=("Arial",12))
    eAppVersion.insert(0,"")
    labelAppVersion.grid(row=2,column=0,sticky="w")
    eAppVersion.grid(row=2,column=1)
    
    #Get App Path
    labelAppPath = tk.CTkLabel(addAppWindow,text="Exe ",font=("Arial",12),padx=20,pady=20,)
    eAppPath = tk.CTkEntry(addAppWindow,width=200,font=("Arial",12))
    eAppPath.insert(0,"")
    labelAppPath.grid(row=3,column=0,sticky="w")
    eAppPath.grid(row=3,column=1)
    
    buttonAppPathBrowse=tk.CTkButton(addAppWindow, text="...",command=lambda entry=eAppPath : getFilePath(entry,False),width=10)
    buttonAppPathBrowse.grid(row=3,column=2)
    
    #Get App Icon
    labelAppIcon = tk.CTkLabel(addAppWindow,text="Icon ",font=("Arial",12),padx=20,pady=20,)
    eAppIcon = tk.CTkEntry(addAppWindow,width=200,font=("Arial",12))
    eAppIcon.insert(0,"")
    labelAppIcon.grid(row=4,column=0,sticky="w")
    eAppIcon.grid(row=4,column=1)
    
    buttonAppIconBrowse=tk.CTkButton(addAppWindow, text="...",command=lambda entry=eAppIcon : getFilePath(entry,True),width=10)
    buttonAppIconBrowse.grid(row=4,column=2)
    
    #Close Add App Window function
    def addApp():
        name = eAppName.get()
        path = eAppPath.get()
        version = eAppVersion.get()
        icon = eAppIcon.get()
        
        if os.path.exists(path) and os.path.exists(icon) and len(name)>=2 and len(version)>=1:
        
            num=0
            # Try to read the existing JSON file
            try:
                with open(appsJson, 'r') as json_file:
                    apps = json.load(json_file)
                    num=len(apps)
            except FileNotFoundError:
                # If the file does not exist, initialize an empty dictionary
                apps = {}

            # Add a new application to the dictionary
            entryName = "app"+str(num+1)
            
            
            apps[entryName] = {
                "name": name,
                "path": path,
                "version": version,
                "icon": icon
            }

            # Save the updated dictionary back to the JSON file
            with open(appsJson, 'w') as json_file:
                json.dump(apps, json_file, indent=4)
                
            addAppsButtons(apps)
            addAppWindow.destroy()
            addAppWindow.update()
            
            message = f"Succesfully added {name} {version} app."
            print(message+"\n")
            messageWindow(root,"Add App Failed",message,"info")
            buttonAddApp.configure(state="enable")
        else:
            message = f"Failed to add the app. Check if you missed any field or paths doesn't exist."
            print(message+"\n")
            messageWindow(root,"Add App Failed",message,"error")
        
    
    #Button Add App and Close window
    buttonAddAndClose=tk.CTkButton(addAppWindow, text="Add", command=addApp)
    buttonAddAndClose.grid(row=5,column=1)

#Button Add App
buttonAddApp=tk.CTkButton(frameLauncher, text="Add App",command=addAppEvent)
buttonAddApp.pack()

###############################################
#### END LAUNCHER TAB ####

root.mainloop()

