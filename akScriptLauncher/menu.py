from pathlib import Path
from typing import List

from maya import cmds

from .constants import TITLE
from .settings import LauncherSettings
from . import file_utils


class LauncherMenu(object):
    
    def __init__(self, *args):

        self.settings = LauncherSettings()
        self.scriptPaths: List[Path] = self.settings.getScriptPaths()
        
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
        for script_path in self.scriptPaths:
            if script_path.is_dir():
                cmds.menuItem(parent=TITLE, divider=True, dividerLabel=f'From: {script_path.name}')
                self.add_menu_item(TITLE, script_path)

    def add_menu_item(self, parent: str, path: Path, *args):
        dirs, files = file_utils.load_scripts(path)
        
        for entry_dir in dirs:
            label, dirPath = entry_dir
            dirMenu = cmds.menuItem(parent=parent, label=label, 
                                    subMenu=True, tearOff=True)
            self.add_menu_item(dirMenu, dirPath)
        
        if dirs and files:
            cmds.menuItem(parent=parent, divider=True, longDivider=False)

        for entry_file in files:
            label, ext, filePath, iconPath = entry_file

            if ext == '.py':
                cmd = self.create_py_command(filePath)
            elif ext == '.mel':
                cmd = self.create_mel_command(filePath)

            cmds.menuItem(parent=parent, label=label, command=cmd, image=iconPath.as_posix() if iconPath else '')

    def create_mel_command(self, file_path: Path, execute: bool = True, *args) -> str:
        path_str = file_path.as_posix()
        lines = []
        lines.append('from maya import mel')
        lines.append(f'print(\'Running MEL Script: {path_str}\')')
        lines.append(f'mel.eval(\'source "{path_str}"\')')
        if execute:
            lines.append(f'mel.eval(\'{file_path.stem}();\')')
        return '\n'.join(lines)
    
    def create_py_command(self, file_path: Path, *args) -> str:
        path_str = file_path.as_posix()
        lines = []
        lines.append(f'from {TITLE} import run')
        lines.append(f'print(\'Running Python Script: {path_str}\')')
        lines.append(f'run.run_script(\'{path_str}\')')
        return '\n'.join(lines)
