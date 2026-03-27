import json
import copy
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance

from .constants import SETTINGS_FILE


def get_user_script_dir() -> str:
    from maya import cmds
    return cmds.internalVar(userScriptDir=True)


def get_maya_window() -> QtWidgets.QMainWindow:
    from maya import OpenMayaUI
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)


class LauncherSettings(object):

    def __init__(self):
        self.mayaMainWindow = get_maya_window()
        self.settings_file: Path = SETTINGS_FILE
        self.settings_dict = {
                'scriptPaths' : []
            }
        self._importSettingsFile()

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
        success = self._exportSettingsFile()
        if not success:
            QtWidgets.QMessageBox.warning(
                self.mayaMainWindow,
                'Warning!',
                'Failed to save script paths settings.\nCheck if the settings file directory is writable.'
            )

    def _importSettingsFile(self, *args) -> bool:
        if not self.settings_file.is_file():
            return False

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings_dict = json.load(f)
            return True
        except Exception as e:
            print('Failed to load settings:', str(e))
            return False

    def _exportSettingsFile(self, *args) -> bool:
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
        self._initUI()
    
    def _initUI(self, *args):
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
        startDir = self.paths[-1] if self.paths else get_user_script_dir()
        
        scriptDir = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            'Select Script Directory', 
            startDir
        )
        
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