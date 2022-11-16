# -*- coding: utf-8 -*-

def execfile(filePath, globals=None, locals=None):
    if globals is None:
        globals = {'__name__': '__main__'}
        exec(compile(open(filePath, 'rb').read(), filePath, 'exec'), globals, locals)