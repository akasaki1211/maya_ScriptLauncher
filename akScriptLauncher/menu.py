# -*- coding: utf-8 -*-
import os, glob
from maya import utils, cmds, mel

TITLE = os.path.basename(os.path.dirname(__file__))
DEFAULTPATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'launcherScripts')

class LauncherMenu(object):
    
    scriptPath = DEFAULTPATH

    def __init__(self, *args):
        
        if not self.scriptPath:
            self.scriptPath = cmds.internalVar(userScriptDir=True)
        
        if cmds.menu(TITLE, exists=True):
            cmds.deleteUI(TITLE)
        
        cmds.menu(TITLE, label=TITLE, 
                parent="MayaWindow", tearOff=True, 
                postMenuCommand=self.build_menu)

        print('{} | Create main menu.'.format(TITLE))

    def build_menu(self, *args):
        cmds.menu(TITLE, e=True, deleteAllItems=True)
        #cmds.menuItem(parent=TITLE, divider=True)
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