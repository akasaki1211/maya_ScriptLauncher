# -*- coding: utf-8 -*-
import os
import json
import copy
from maya import cmds, OpenMayaUI

try:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance

ROOTPATH = os.path.dirname(os.path.abspath(__file__))
TITLE = os.path.basename(ROOTPATH)
SETTINGS_FILE = os.path.join(ROOTPATH, 'settings.json')

class LauncherMenu(object):
    
    def __init__(self, *args):

        self.settings = LauncherSettings()
        self.scriptPaths = self.settings.getScriptPaths()
        
        if not self.scriptPaths:
            self.scriptPaths = [cmds.internalVar(userScriptDir=True)]
        
        if cmds.menu(TITLE, exists=True):
            cmds.deleteUI(TITLE)
        
        cmds.menu(TITLE, label=TITLE, 
                parent="MayaWindow", tearOff=True, 
                postMenuCommand=self.build_menu)

        print('{} | Create main menu.'.format(TITLE))

    def update_script_path(self, *args):
        self.settings.setScriptPaths()
        self.scriptPaths = self.settings.getScriptPaths()
        self.build_menu()

    def build_menu(self, *args):
        cmds.menu(TITLE, e=True, deleteAllItems=True)
        cmds.menuItem(parent=TITLE, label='Settings', command=self.update_script_path)
        for sPath in self.scriptPaths:
            if os.path.isdir(sPath):
                cmds.menuItem(parent=TITLE, divider=True)
                self.add_menu_item(TITLE, sPath)

    def add_menu_item(self, parent, path, *args):
        dirs, files = self.load_scripts(path)
        
        for dir in dirs:
            label, dirPath = dir
            dirMenu = cmds.menuItem(parent=parent, label=label, 
                                    subMenu=True, tearOff=True)
            self.add_menu_item(dirMenu, dirPath)
        
        cmds.menuItem(parent=parent, divider=True)

        for file in files:
            label, ext, filePath, iconPath = file

            if ext == '.py':
                cmd = self.create_py_command(filePath)
            elif ext == '.mel':
                cmd = self.create_mel_command(filePath)

            cmds.menuItem(parent=parent, label=label, command=cmd, image=iconPath)

    def load_scripts(self, path, *args):
        dirs = []
        files = []

        for f in os.listdir(path):
            fullPath = os.path.join(path, f)
            if os.path.isdir(fullPath):
                dirs.append((f, fullPath))
            else:
                base, ext = os.path.splitext(f)
                if not ext in ['.py', '.mel']:
                    continue

                iconPath = os.path.join(path, base + '.ico')
                if not os.path.isfile(iconPath):
                    iconPath = os.path.join(path, base + '.png')
                if not os.path.isfile(iconPath):
                    iconPath = ''
                
                files.append((f, ext, fullPath, iconPath))

        return dirs, files

    def create_mel_command(self, filePath, execute=True, *args):
        filePath = os.path.normpath(filePath)
        filePath = filePath.replace('\\','\\\\\\\\')
        cmd = 'from maya import mel\n'
        cmd += 'mel.eval(\'source \"{}\"\')'.format(filePath)

        if execute:
            name = os.path.splitext(os.path.basename(filePath))[0]
            cmd += '\nmel.eval(\'{}();\')'.format(name)
        
        return cmd

    def create_py_command(self, filePath, *args):
        cmd = 'from {} import run\n'.format(TITLE)
        cmd += 'run.execfile(r\'{}\')'.format(filePath)

        return cmd

class LauncherSettings(object):

    def __init__(self):
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        self.mayaMainWindow = wrapInstance(int(ptr), QtWidgets.QMainWindow)
        self.settings_file = SETTINGS_FILE
        self.settings_dict = {
                'scriptPaths' : []
            }
        self.importSettingsFile()

    def getScriptPaths(self, *args):
        if 'scriptPaths' in self.settings_dict.keys():
            return copy.deepcopy(self.settings_dict['scriptPaths'])
        else:
            return []
    
    def setScriptPaths(self, *args):
        if 'scriptPaths' in self.settings_dict.keys():
            scriptPaths = copy.deepcopy(self.settings_dict['scriptPaths'])
        else:
            scriptPaths = []
        paths, accepted = ScriptPathDialog.setPath(parent=self.mayaMainWindow, paths=scriptPaths)
        
        if not accepted:
            return

        self.settings_dict['scriptPaths'] = paths        
        self.exportSettingsFile()

    def importSettingsFile(self, *args):
        if not os.path.isfile(self.settings_file):
            return

        try:
            with open(self.settings_file, 'r') as f:
                self.settings_dict = json.load(f)
            return True
        except:
            return

    def exportSettingsFile(self, *args):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings_dict, f, indent=4)
            return True
        except:
            return

class ScriptPathDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, *args):
        super(ScriptPathDialog, self).__init__(parent, *args)
        self.paths = []
        self.initUI()
    
    def initUI(self, *args):
        self.setWindowTitle('Script Path')
        self.resize(500, 100)

        self.listWidget = QtWidgets.QListWidget()
        
        addBtn = QtWidgets.QPushButton('Add')
        addBtn.clicked.connect(self.addPath)
        
        deleteBtn = QtWidgets.QPushButton('Delete')
        deleteBtn.clicked.connect(self.deletePath)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(addBtn)
        buttonLayout.addWidget(deleteBtn)
        
        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.accept)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.listWidget)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(saveBtn)

        self.setLayout(mainLayout)
        
    def addPath(self, *args):
        if self.paths:
            startDir = self.paths[-1]
        else:
            startDir = cmds.internalVar(userScriptDir=True)
        
        scriptDir = cmds.fileDialog2(
            caption='Select Script Directory', 
            startingDirectory=startDir,
            fileMode=3)
        
        if not scriptDir:
            return

        self.paths.append(scriptDir[0])
        self.listWidget.clear()
        self.listWidget.addItems(self.paths)
        
    def deletePath(self, *args):
        row = self.listWidget.currentRow()
        self.paths.pop(row)
        self.listWidget.clear()
        self.listWidget.addItems(self.paths)        
    
    @staticmethod
    def setPath(parent=None, paths=[], *args):
        dialog = ScriptPathDialog(parent)
        dialog.paths = paths
        dialog.listWidget.addItems(dialog.paths)
        result = dialog.exec_()

        return (dialog.paths, result == QtWidgets.QDialog.Accepted)