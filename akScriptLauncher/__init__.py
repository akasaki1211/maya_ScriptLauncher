from pathlib import Path
from maya import utils

TITLE = Path(__file__).parent.name

print('\n============================================')
print(TITLE + '\n')
print('============================================\n')

def launcher_load(*args):
    from . import menu
    menu.LauncherMenu()

utils.executeDeferred(launcher_load)