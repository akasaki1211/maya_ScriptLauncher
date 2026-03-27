from maya import utils

def initialize():
    from .menu import LauncherMenu
    LauncherMenu()

utils.executeDeferred(initialize)