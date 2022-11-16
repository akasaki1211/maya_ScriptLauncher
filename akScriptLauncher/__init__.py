# -*- coding: utf-8 -*-
import os
from maya import utils

TITLE = os.path.basename(os.path.dirname(__file__))

print('\n============================================')
print(TITLE + '\n')
print('============================================\n')

def aksl_load(*args):
    from . import menu
    menu.LauncherMenu()

utils.executeDeferred(aksl_load)