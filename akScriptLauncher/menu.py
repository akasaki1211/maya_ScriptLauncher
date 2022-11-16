# -*- coding: utf-8 -*-
import os, json
from maya import cmds

ROOTPATH = os.path.dirname(os.path.abspath(__file__))
TITLE = os.path.basename(ROOTPATH)
SETTINGS_FILE = os.path.join(ROOTPATH, 'settings.json')

class LauncherMenu(object):
    
    def __init__(self, *args):

        self.settings = LauncherSettings()
        self.scriptPath = self.settings.getScriptPath()
        
        if not self.scriptPath:
            self.scriptPath = cmds.internalVar(userScriptDir=True)
        
        if cmds.menu(TITLE, exists=True):
            cmds.deleteUI(TITLE)
        
        cmds.menu(TITLE, label=TITLE, 
                parent="MayaWindow", tearOff=True, 
                postMenuCommand=self.build_menu)

        print('{} | Create main menu.'.format(TITLE))

    def update_script_path(self, *args):
        self.settings.setScriptPath()
        self.scriptPath = self.settings.getScriptPath()
        self.build_menu()

    def build_menu(self, *args):
        cmds.menu(TITLE, e=True, deleteAllItems=True)
        cmds.menuItem(parent=TITLE, label='Settings', command=self.update_script_path)
        cmds.menuItem(parent=TITLE, divider=True)
        self.add_menu_item(TITLE, self.scriptPath)
        
        print('{} | Rebuild menu.'.format(TITLE))

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

    def create_mel_command(self, filePath, exec=True, *args):
        filePath = os.path.normpath(filePath)
        filePath = filePath.replace('\\','\\\\\\\\')
        cmd = 'from maya import mel\n'
        cmd += 'mel.eval(\'source \"{}\"\')'.format(filePath)

        if exec:
            name = os.path.splitext(os.path.basename(filePath))[0]
            cmd += '\nmel.eval(\'{}();\')'.format(name)
        
        return cmd

    def create_py_command(self, filePath, *args):
        cmd = 'from {} import run\n'.format(TITLE)
        cmd += 'run.execfile(r\'{}\')'.format(filePath)

        return cmd

class LauncherSettings(object):

    def __init__(self):
        self.settings_file = SETTINGS_FILE
        self.settings_dict = {
                'scriptPath' : ''
            }
        self.importSettingsFile()

    def getScriptPath(self, *args):
        return self.settings_dict['scriptPath']
    
    def setScriptPath(self, *args):
        startDir = self.settings_dict['scriptPath']
        if not startDir:
            startDir = cmds.internalVar(userScriptDir=True)

        path = cmds.fileDialog2(
            caption='Select Script Directory', 
            startingDirectory=startDir,
            fileMode=3)
        
        if not path:
            return
        
        self.settings_dict['scriptPath'] = path[0]
        
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