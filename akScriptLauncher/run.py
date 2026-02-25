# -*- coding: utf-8 -*-

def execfile(filePath, globals=None, locals=None):
    if globals is None:
        globals = {}
        
    globals.setdefault('__name__', '__main__')
    globals.setdefault('__file__', filePath)
    
    with open(filePath, 'rb') as f:
        code = compile(f.read(), filePath, 'exec')
        
    exec(code, globals, locals)