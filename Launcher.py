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

## Get pipeSpecs
pipeSpecsJson = "data/pipeSpecs.json"
# Try to read the existing JSON file
try:
    with open(pipeSpecsJson, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
        data=[]

projectFolders = data['projectFolders']
assetTypes = data['assetTypes']
shotSteps = data['shotSteps']
assetSteps = data['assetSteps']

init_files = data['initFiles']


hipSrc = init_files.get('houdini')
purerefSrc = init_files.get('pureref')
videoSrc = init_files.get('video')
imageSrc = init_files.get('image')
nukeSrc = init_files.get('nuke')
davinciSrc = init_files.get('davinci')

##Get projects
#Get projects folder path
envVars = dotenv_values('data/.env')
projectsPath=envVars.get("PROJECTS")
projectsList=os.listdir(projectsPath)

if len(projectsList)==0:
    projectsList=[" "]
    
currentDir = os.getcwd()
print("PG Pipeline 1.0, built 2024.")
print(f"Directory: {currentDir}\n")

    
###############################################
#### END INIT ####




#### START GUI ####
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


##Create tab view
tabview = tk.CTkTabview(root, width=250)
tabview.pack(expand=1, fill='both')
tabview.add("Launcher")
tabview.add("Projects")
tabview.add("Shots")
tabview.add("Assets")



    
#### PROJECTS TAB ####
###############################################
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

#Create project function
def createProject():
    
    projectName=eProjectName.get()
    print("\n******************************")
    print("\nPROJECT BUILDER\n")
    if projectName!="" and len(projectName)>= 3 and any(char.isdigit() for char in projectName) == False:
        eProjectName.delete(0, tk.END)
        eProjectName.insert(0,"")
        projectPath=projectsPath+"/"+projectName
        print("\n******************************")
        print("\nPROJECT BUILDER\n")
        try:
            os.mkdir(projectPath)
        except OSError as error:
            message = "Error: "+projectName+" project already exists."
            print(message+"\n")
            messageWindow(root,"Project Creation Failed",message,"error")
        else:
            
            projectsList.append(projectName)
            optionmenu_Projects1.configure(values=projectsList)
            optionmenu_Projects2.configure(values=projectsList)
            optionmenu_Projects3.configure(values=projectsList)
            
            #Create project folders
            for f in projectFolders:
                folderPath=projectPath+"/"+f
                os.mkdir(folderPath)
                print("    -"+f+ " folder created at: "+folderPath)
                
            message = f"Project {projectName} created succesfully."
            print(message+"\n")
            messageWindow(root,"Shots Created",message,"info")
        
    else:
        message = "Error: The project name "+projectName+" is not a valid name.\nIt must have 3 or more letters and not contain digits."
        print(message+"\n")
        messageWindow(root,"Project Creation Failed",message,"error")
    print("******************************\n")       
#Button Create Project
buttonCreateProject=tk.CTkButton(frameProjects, text="Create New",command=createProject)
buttonCreateProject.grid(row=2,column=1,sticky="e")

###############################################
#### END PROJECTS TAB ####




#### SHOTS TAB ####
###############################################

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
    
#Create shot function
def createShot():
    print("\n******************************")
    print("\nSHOT BUILDER\n")
    
    if eEpisode.get().isdigit() and eSequence.get().isdigit() and eShotBegin.get().isdigit() and eShotEnd.get().isdigit():
    
        currentProject=optionmenu_Projects1.get()
        shotsPath=projectsPath+"/"+currentProject+"/shots"
        
        ep=int(eEpisode.get())
        seq=int(eSequence.get())
        shBegin=int(eShotBegin.get())
        shEnd=int(eShotEnd.get())
        
        
        epStr=numToStr(ep)
        seqStr=numToStr(seq)
        
        epPath=shotsPath+"/ep"+epStr
        seqPath=epPath+"/seq"+seqStr
        
        try:
            os.mkdir(epPath)
        except:
            pass
        else:
            editPath=projectsPath+"/"+currentProject+"/edit"
            editEpPath=editPath+"/ep"+epStr
            try:
                os.mkdir(editEpPath)
            except:
                pass
            
            editEpJobPath=editEpPath+"/job"
            try:
                os.mkdir(editEpJobPath)
            except:
                pass
            
            nukePath=editEpJobPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_edit_v000.nk"
            print("            Create nuke file at: ",nukePath)
            shutil.copyfile(nukeSrc, nukePath)
            
            editEpPubPath=editEpPath+"/pub"
            try:
                os.mkdir(editEpPubPath)
            except:
                pass
            
            videoPath=editEpPubPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_edit_v000.mp4"
            print("            Create video file at: ",videoPath)
            shutil.copyfile(videoSrc, videoPath)
            
            editEpPubPath=editEpPath+"/pub"
            print("Create Episode at: ",epPath)
            
        try:
            os.mkdir(seqPath)
        except:
            pass
        else:
            print("Create Sequence at: ",seqPath)
            
        sh=shBegin
        while sh<=shEnd:
            shStr=numToStr(int(sh))
            shPath=seqPath+"/sh"+shStr
            try:
                os.mkdir(shPath)
            except:
                pass
            else:
                print("Create Shot at: ",shPath)
                for s in shotSteps:
                    stepPath=shPath+"/"+s
                    os.mkdir(stepPath)
                    print("    Create "+s+" folder at: ",stepPath)
                    
                    #Create job folder
                    jobPath=stepPath+"/job"
                    os.mkdir(jobPath)
                    print("        Create job folder at: ",jobPath)
                    
                    if s != "cmp":
                        hipPath=jobPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_sh"+shStr+"_"+s+"_master_v000.hip"
                        print("            Create hip file at: ",hipPath)
                        shutil.copyfile(hipSrc, hipPath)
                    
                        purerefPath=jobPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_sh"+shStr+"_"+s+"_master_v000.pur"
                        print("            Create purRef file at: ",purerefPath)
                        shutil.copyfile(purerefSrc, purerefPath)
                    
                        workCachePath=jobPath+"/cache"
                        os.mkdir(workCachePath)
                        print("            Create work cache folder at: ",workCachePath)
                    
                        workFlipbookPath=jobPath+"/flipbook"
                        os.mkdir(workFlipbookPath)
                        print("            Create flipbook folder at: ",workFlipbookPath)
                        
                        videoPath=workFlipbookPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_sh"+shStr+"_"+s+"_master_flipbook_v000.mp4"
                        print("            Create video file at: ",videoPath)
                        shutil.copyfile(videoSrc, videoPath)
                    else:
                        nukePath=jobPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_sh"+shStr+"_"+s+"_master_v000.nk"
                        print("            Create nuke file at: ",nukePath)
                        shutil.copyfile(nukeSrc, nukePath)
                    
                    #Create pub folder
                    pubPath=stepPath+"/pub"
                    os.mkdir(pubPath)
                    print("        Create pub folder at: ",pubPath)
                    
                    if s != "cmp":
                        pubUSDPath=pubPath+"/usd"
                        os.mkdir(pubUSDPath)
                        print("            Create pub usd folder at: ",pubUSDPath)
                    else:
                        videoPath=pubPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_sh"+shStr+"_"+s+"_master_v000.mp4"
                        print("            Create video file at: ",videoPath)
                        shutil.copyfile(videoSrc, videoPath)
                    
                    #Create preview folder
                    previewPath=stepPath+"/preview"
                    os.mkdir(previewPath)
                    print("        Create preview folder at: ",previewPath)
                    
                    videoPath=previewPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_sh"+shStr+"_"+s+"_master_preview_v000.mp4"
                    print("            Create video file at: ",videoPath)
                    shutil.copyfile(videoSrc, videoPath)
                    
                    imagePath=previewPath+"/"+currentProject+"_ep"+epStr+"_seq"+seqStr+"_sh"+shStr+"_"+s+"_master_preview_v000.png"
                    print("            Create image file at: ",imagePath)
                    shutil.copyfile(imageSrc, imagePath)
                    
                        
            sh+=1
        message = f"Shots created succesfully."
        print(message+"\n")
        messageWindow(root,"Shots Created",message,"info")
    else:
        message = "Error: Please introduce positive integers only."
        print(message+"\n")
        messageWindow(root,"Project Creation Failed",message,"error")
    print("******************************\n")

#Button Create Shot
buttonCreateShot=tk.CTkButton(frameShots, text="Create",command=createShot)
buttonCreateShot.grid(row=4,column=2,sticky="e")

###############################################
#### END SHOTS TAB ####




#### ASSETS TAB ####
###############################################

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

#Create asset function
def createAsset():
    print("\n******************************")
    print("\nASSET BUILDER\n")
    
    assetName=eAssetName.get()
    
    if len(assetName) >= 2 and any(char.isdigit() for char in assetName) == False:
    
        assetType=optionmenu_assetTypes.get()    
        eAssetName.delete(0, tk.END)
        eAssetName.insert(0,"")
        currentProject=optionmenu_Projects2.get()
        assetsPath=projectsPath+"/"+currentProject+"/assets"
        
        assetTypeFolderPath=assetsPath+"/"+assetType
        try:
            os.mkdir(assetTypeFolderPath)
        except:
            pass
        else:
            print("Create "+assetType+" folder at : "+assetTypeFolderPath)
        
        assetPath=assetTypeFolderPath+"/"+assetName
        try:
            os.mkdir(assetPath)
        except:
            message = "Error: "+assetName+" asset already exists."
            print(message+"\n")
            messageWindow(root,"Asset Creation Failed",message,"error")
        else:
            print("Create asset "+assetName+" folder at: "+assetPath)
            
            for s in assetSteps:
                
                stepPath=assetPath+"/"+s
                print("    Create "+s+"+ folder at: "+stepPath)
                os.mkdir(stepPath)
                
                if s == "lookdev":
                    texturesPath=stepPath+"/textures"
                    os.mkdir(texturesPath)
                    print("    Create textures folder at: ",texturesPath)
                
                #Create job folder
                jobPath=stepPath+"/job"
                os.mkdir(jobPath)
                print("        Create job folder at: ",jobPath)
                
                jobCachePath=jobPath+"/cache"
                os.mkdir(jobCachePath)
                print("            Create cache folder at: ",jobCachePath)
                
                hipPath=jobPath+"/"+currentProject+"_"+assetType+"_"+assetName+"_"+s+"_master_v000.hip"
                print("            Create hip file at: ",hipPath)
                shutil.copyfile(hipSrc, hipPath)
                    
                purerefPath=jobPath+"/"+currentProject+"_"+assetType+"_"+assetName+"_"+s+"_master_v000.pur"
                print("            Create pureRef file at: ",purerefPath)
                shutil.copyfile(purerefSrc, purerefPath)
                
                #Create pub path
                pubPath=stepPath+"/pub"
                os.mkdir(pubPath)
                print("        Create pub folder at: ",pubPath)
                
                pubUSDPath=pubPath+"/usd"
                os.mkdir(pubUSDPath)
                print("            Create pub usd folder at: ",pubUSDPath)
                    
                pubABCPath=pubPath+"/abc"
                os.mkdir(pubABCPath)
                print("            Create pub abc folder at: ",pubABCPath)
                
                #Create preview folder
                previewPath=stepPath+"/preview"
                os.mkdir(previewPath)
                print("        Create preview folder at: ",previewPath)
                    
                videoPath=previewPath+"/"+currentProject+"_"+assetType+"_"+assetName+"_"+s+"_master_preview_v000.mp4"
                print("            Create video file at: ",videoPath)
                shutil.copyfile(videoSrc, videoPath)
                    
                imagePath=previewPath+"/"+currentProject+"_"+assetType+"_"+assetName+"_"+s+"_master_preview_v000.png"
                print("            Create image file at: ",imagePath)
                shutil.copyfile(imageSrc, imagePath)
                
            message = f"Asset {assetName} created succesfully."
            print(message+"\n")
            messageWindow(root,"Asset Created",message,"info")
    else:
        message = "Error: The asset name "+assetName+" is not a valid name.\nIt must have 2 or more letters and not contain digits."
        print(message+"\n")
        messageWindow(root,"Asset Creation Failed",message,"error")
    print("******************************\n")

#Button Create Asset
buttonCreateAsset=tk.CTkButton(frameAssets, text="Create",command=createAsset)
buttonCreateAsset.grid(row=3,column=1,sticky="e")

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

def addEnvVars():
    currentProject=optionmenu_Projects3.get()
    
    #Set env variables from .env file
    for var, value in envVars.items():
        # Optionally expand any environment variable references within the values
        expanded_var = os.path.expandvars(value)
        os.environ[var] = expanded_var
    
    #Set env variable of current project
    os.environ['PROJECT'] = projectsPath+"/"+currentProject
    
    #Set env variables from pipeSpecs.json file
    houdiniVars = data['houdiniVars']
    for var, value in houdiniVars.items():
        value = os.path.expandvars(value)
        if os.path.exists(value):
            value = os.path.abspath(value)
        os.environ[var] = value

#Execute apps function
def executeApp(app):
    print(f"Launching {app["name"]} ")
    # Set the environment variable
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
    labelAppPath = tk.CTkLabel(addAppWindow,text="Path ",font=("Arial",12),padx=20,pady=20,)
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

