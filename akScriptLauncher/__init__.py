# -*- coding: utf-8 -*-
import os
from maya import utils

TITLE = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

print('\n============================================')
print(TITLE + '\n')
print('============================================\n')

def launcher_load(*args):
    from . import menu
    menu.LauncherMenu()

utils.executeDeferred(launcher_load)