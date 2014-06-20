#!/usr/bin/env python
import maya.cmds as cmds
import os
import math

### global variables ###
### to DO####
# disable viewport

exportFilename = 'export.chan'   

workdir = cmds.workspace(q=True, directory=True )
dirname = os.path.dirname(workdir)

scenepath = os.path.join(dirname, 'exporter.chan')

global windowExporter
global dirPath
dirPath = ''
##################

def createWindow():
    global dirPath
    global windowExporter
    windowExporter = cmds.window(widthHeight=(600, 400), title="Locator & Camera to Nuke-Exporter")
    startframe = cmds.playbackOptions( query=True, animationStartTime=True )
    endframe = cmds.playbackOptions( query=True, animationEndTime=True )    
    cmds.columnLayout( adjustableColumn=True )
    cmds.text (label='')
    cmds.text (label='Locator & Camera to Nuke-Exporter')
    cmds.text (label='')
    cmds.text( label='   1.) select camera or locator you want to export', align='left')
    cmds.text( label='   2.) adjust framerange', align='left')
    cmds.text( label='   3.) change export directory', align='left')    
    cmds.text( label='   4.) hit "export" or "export & close"', align='left')
    cmds.text( label=' ', align='left')
    cmds.text( label='   NOTE: you may need to change axis order in Nuke to XYZ to get correct results \n', align='left')    
    
# start and end frame
    cmds.frameLayout( label='Framerange', borderStyle='in' )
    cmds.rowColumnLayout( nc=4, rowOffset=(1,'top',10) )
    cmds.text( label='   start frame:  ' )
    cmds.textField('startframeInput', text=int(startframe))
    cmds.text( label='   end frame:   ' )
    cmds.textField('endframeInput', text=int(endframe))
    cmds.text (label='')    
    cmds.setParent( '..' )
    cmds.setParent( '..' )    

# export path
    cmds.frameLayout( label='export path', borderStyle='in' )
    cmds.rowColumnLayout( nc=2,  columnWidth=(1, 500) )
    if len(dirPath):
        exportFilePath = cmds.textField('exportpath', text=str(dirPath))
    else:
        exportFilePath = cmds.textField('exportpath', text=str(scenepath))        
    cmds.button( label='browse directory', command=changePath )
    cmds.text (label='')
    cmds.setParent( '..' )
    cmds.setParent( '..' )        
# buttons    
    cmds.rowColumnLayout( nc=3, rowOffset=(1,'top',10) )
    cmds.button( label='Export', command=animationToNuke )
    cmds.button( label='Export & Close', command=animationToNukeClose )
    cmds.button( label='Close', command=deleteWindow )
    print dirPath + 'furz' + scenepath
    cmds.showWindow(windowExporter)
    return windowExporter

def changePath(*args):
    global dirPath
    directoryPath = cmds.fileDialog2(ds=2, fileMode=0, returnFilter=True, caption="select export path")
    print directoryPath[0]
    cmds.textField('exportpath', edit=True, text=directoryPath[0])
    # reset directory?
    
def deleteWindow(self):
    global dirPath
    global windowExporter
# why self???
    dirPath = cmds.textField('exportpath', q=True, text=True)
    cmds.deleteUI(windowExporter, window=True)

 
### exporter ###  
def animationToNuke(self):
    #eName = cmds.textField("exportname",query=True, text=True)
    ePath = cmds.textField("exportpath",query=True, text=True)
    #nameJoined = os.path.join(ePath, eName)     
   
    nameJoined = ePath   
    camExport = open(nameJoined, 'w')
    startframe = cmds.textField("startframeInput",query=True, text=True)
    endframe = cmds.textField("endframeInput",query=True, text=True)
    cmds.currentTime(startframe)

    x = cmds.ls(sl=True, l=True)
    a = cmds.listRelatives(x, s=True)

    for i in range(int(startframe),(int(endframe)+1)):
        cmds.setAttr('time1.outTime', 0)
        print cmds.getAttr('time1.outTime')
        t = cmds.currentTime(u=0, query=True)
    # translate
        translateX = cmds.getAttr('%s.translateX'% x[0], time=t)
        translateY = cmds.getAttr('%s.translateY'% x[0], time=t)
        translateZ = cmds.getAttr('%s.translateZ'% x[0], time=t)
    # rotate
        rotateX = cmds.getAttr('%s.rotateX'% x[0], time=t)
        rotateY = cmds.getAttr('%s.rotateY'% x[0], time=t)
        rotateZ = cmds.getAttr('%s.rotateZ'% x[0], time=t)
    # camera data
        if cmds.nodeType(a) == 'camera':
            vertAperture = cmds.getAttr('%s.verticalFilmAperture'% x[0], time=t)
            focalLength = cmds.getAttr('%s.focalLength'% x[0], time=t)
    # calculating verticalFOV atan is in radiant ==> math.degrees
            vertFOV = math.degrees(2*(math.atan(vertAperture * 25.4 * 0.5 / focalLength)))
           
    # frames
        framenumber = cmds.currentTime(query=True)

    # translation and rotation combined
        translate = str(translateX) + ' ' + str(translateY) + ' ' + str(translateZ)
        rotate = str(rotateX) + ' ' + str(rotateY) + ' ' + str(rotateZ)

    ###############################
    # writing file
    ###############################
        output =  str(int(framenumber)) + ' ' + translate  + ' ' + rotate
        if cmds.nodeType(a) == 'camera':
            output += ' ' + str(vertFOV) + '\n'
        else:
            output += ' ' + '\n'

    # disable viewports #
    #cmds.currentTime(update=False)

        cmds.currentTime(i+1, edit=True)
        camExport.write(output)
    #print 'export completed %s' % x[0]


    # enable viewport #
    #cmds.currentTime(update=True)
    # closing file
    camExport.close()
    dirPath = cmds.textField('exportpath', q=True, text=True) or ''
    print x[0] + "  exported successfully to: " + dirPath  

    
def animationToNukeClose(self):
    global dirPath
    global windowExporter
    animationToNuke(self)
    dirPath = cmds.textField('exportpath', q=True, text=True) or ''
    if windowExporter:
        cmds.deleteUI(windowExporter, window=True)

# launchProgram = createWindow()
