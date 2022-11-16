# -*- coding: utf-8 -*-
import os, glob
from maya import utils, cmds, mel

TITLE = os.path.basename(os.path.dirname(__file__))
DEFAULTPATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'launcherScripts')

class LauncherMenu(object):

    def __init__(self, *args):
        self.create()

    def create(self, *args):
        if cmds.menu(TITLE, exists=True):
            cmds.deleteUI(TITLE)

        cmds.menu(TITLE, label=TITLE, parent="MayaWindow", tearOff=True, postMenuCommand=self.rebuild_item)
        
        print('{} | Create main menu.'.format(TITLE))
        
        #self.rebuild_item()

    def rebuild_item(self, *args):
        dirs, files = self.load_scripts()
        
        #print(dirs)
        #print(files)

        cmds.menu(TITLE, e=True, deleteAllItems=True)
        cmds.setParent(TITLE, menu=True)
        
        for file in files:
            label, ext, filePath, iconPath = file

            if ext == '.py':
                command = self.create_py_command(filePath)
            elif ext == '.mel':
                command = self.create_mel_command(filePath)

            cmds.menuItem(label=label, command=command, image=iconPath)

        #cmds.menuItem(divider=True)
        
        print('{} | Rebuild sub menu.'.format(TITLE))

    def load_scripts(self, *args):
        scriptPath = DEFAULTPATH
        if not scriptPath:
            scriptPath = cmds.internalVar(userScriptDir=True)

        dirs = []
        files = []

        for f in os.listdir(scriptPath):
            fullPath = os.path.join(scriptPath, f)
            if os.path.isdir(fullPath):
                dirs.append((f, fullPath))
            else:
                base, ext = os.path.splitext(f)
                if not ext in ['.py', '.mel']:
                    continue

                iconPath = os.path.join(scriptPath, base + '.ico')
                if not os.path.isfile(iconPath):
                    iconPath = os.path.join(scriptPath, base + '.png')
                if not os.path.isfile(iconPath):
                    iconPath = ''
                
                files.append((f, ext, fullPath, iconPath))

        return dirs, files

    def create_mel_command(self, filePath, *args):
        filePath = os.path.normpath(filePath)
        filePath = filePath.replace('\\','\\\\\\\\')
        command = 'from maya import mel\n'
        command += 'mel.eval(\'source \"{}\"\')'.format(filePath)

        # for AriTools
        baseName = os.path.basename(filePath)
        if baseName.startswith('Ari'):
            command += '\n'
            command += 'mel.eval(\'{}();\')'.format(os.path.splitext(baseName)[0])
        
        return command

    def create_py_command(self, filePath, *args):
        command = 'from {} import run\n'.format(TITLE)
        command += 'run.execfile(r\'{}\')'.format(filePath)
        return command