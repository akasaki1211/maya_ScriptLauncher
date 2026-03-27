import json
import copy
from pathlib import Path
from typing import List, Tuple, Optional

from maya import cmds, OpenMayaUI

try:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance

ROOTPATH = Path(__file__).parent
TITLE = ROOTPATH.name
SETTINGS_FILE = ROOTPATH / 'settings.json'

class LauncherMenu(object):
    
    def __init__(self, *args):

        self.settings = LauncherSettings()
        self.scriptPaths: List[Path] = self.settings.getScriptPaths()

        if not self.scriptPaths:
            self.scriptPaths = [Path(cmds.internalVar(userScriptDir=True))]
        
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
                cmds.menuItem(parent=TITLE, divider=True)
                self.add_menu_item(TITLE, script_path)

    def add_menu_item(self, parent: str, path: Path, *args):
        dirs, files = self.load_scripts(path)
        
        for entry_dir in dirs:
            label, dirPath = entry_dir
            dirMenu = cmds.menuItem(parent=parent, label=label, 
                                    subMenu=True, tearOff=True)
            self.add_menu_item(dirMenu, dirPath)
        
        cmds.menuItem(parent=parent, divider=True)

        for entry_file in files:
            label, ext, filePath, iconPath = entry_file

            if ext == '.py':
                cmd = self.create_py_command(filePath)
            elif ext == '.mel':
                cmd = self.create_mel_command(filePath)

            cmds.menuItem(parent=parent, label=label, command=cmd, image=iconPath.as_posix() if iconPath else '')

    def _find_icon(self, script_path: Path) -> Optional[Path]:
        ico = script_path.with_suffix('.ico')
        if ico.is_file():
            return ico
        png = script_path.with_suffix('.png')
        if png.is_file():
            return png
        return None

    def load_scripts(self, path: Path, *args) -> Tuple[List[Tuple[str, Path]], List[Tuple[str, str, Path, Optional[Path]]]]:

        dirs: List[Tuple[str, Path]] = []
        files: List[Tuple[str, str, Path, Optional[Path]]] = []

        for f in sorted(path.iterdir()):
            if f.is_dir():
                dirs.append((f.name, f))
            else:
                ext = f.suffix.lower()
                if ext not in ['.py', '.mel']:
                    continue

                files.append((f.name, ext, f, self._find_icon(f)))

        return dirs, files

    def create_mel_command(self, file_path: Path, execute: bool = True, *args) -> str:
        cmd = 'from maya import mel\n'
        cmd += 'print(f\'Running MEL Script: {}\')\n'.format(file_path.as_posix())
        cmd += 'mel.eval(\'source "{}"\')'.format(file_path.as_posix())
        if execute:
            name = file_path.stem
            cmd += '\nmel.eval(\'{}();\')'.format(name)
        return cmd

    def create_py_command(self, file_path: Path, *args) -> str:
        cmd = 'from {} import run\n'.format(TITLE)
        cmd += 'print(f\'Running Python Script: {}\')\n'.format(file_path.as_posix())
        cmd += 'run.run_script(r\'{}\')'.format(file_path.as_posix())
        return cmd

class LauncherSettings(object):

    def __init__(self):
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        self.mayaMainWindow = wrapInstance(int(ptr), QtWidgets.QMainWindow)
        self.settings_file: Path = SETTINGS_FILE
        self.settings_dict = {
                'scriptPaths' : []
            }
        self.importSettingsFile()

    def getScriptPaths(self, *args) -> List[Path]:
        if 'scriptPaths' in self.settings_dict.keys():
            return [Path(p) for p in copy.deepcopy(self.settings_dict['scriptPaths'])]
        else:
            return []
    
    def setScriptPaths(self, *args) -> None:
        if 'scriptPaths' in self.settings_dict.keys():
            scriptPaths = copy.deepcopy(self.settings_dict['scriptPaths'])
        else:
            scriptPaths = []
        paths, accepted = ScriptPathDialog.setPath(parent=self.mayaMainWindow, paths=scriptPaths)
        
        if not accepted:
            return

        self.settings_dict['scriptPaths'] = paths        
        success = self.exportSettingsFile()
        if not success:
            QtWidgets.QMessageBox.warning(
                self.mayaMainWindow,
                'Warning!',
                'Failed to save script paths settings.\nCheck if the settings file directory is writable.'
            )

    def importSettingsFile(self, *args) -> bool:
        if not self.settings_file.is_file():
            return False

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings_dict = json.load(f)
            return True
        except Exception as e:
            print('Failed to load settings:', str(e))
            return False

    def exportSettingsFile(self, *args) -> bool:
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_dict, f, indent=4)
            return True
        except Exception as e:
            print('Failed to save settings:', str(e))
            return False

class ScriptPathDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, *args):
        super(ScriptPathDialog, self).__init__(parent, *args)
        self.paths: List[str] = []
        self.initUI()
    
    def initUI(self, *args):
        self.setWindowTitle('Script Path')
        self.resize(500, 100)

        self.listWidget = QtWidgets.QListWidget()
        
        addBtn = QtWidgets.QPushButton('Add')
        addBtn.clicked.connect(self._addPath)
        
        deleteBtn = QtWidgets.QPushButton('Delete')
        deleteBtn.clicked.connect(self._deletePath)
        
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
        
    def _addPath(self, *args):
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
        
    def _deletePath(self, *args):
        row = self.listWidget.currentRow()
        if row < 0:
            return
        self.paths.pop(row)
        self.listWidget.clear()
        self.listWidget.addItems(self.paths)        
    
    @staticmethod
    def setPath(parent = None, paths: Optional[List[str]] = None, *args) -> Tuple[List[str], bool]:
        if paths is None:
            paths = []

        dialog = ScriptPathDialog(parent)
        dialog.paths = paths
        dialog.listWidget.addItems(dialog.paths)
        result = dialog.exec_()

        return (dialog.paths, result == QtWidgets.QDialog.Accepted)