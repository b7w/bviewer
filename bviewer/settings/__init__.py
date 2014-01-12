# -*- coding: utf-8 -*-

# Package import order:
#   local -> project -> django
#   test -> local -> project -> django
#   debug -> local -> project -> django
#
# sample.py - sample for local.py.
#
# run '--settings=bviewer.settings' for use `local` settings.
# run '--settings=bviewer.settings.test' for use `test` settings.
# run '--settings=bviewer.settings.debug' for use `debug` settings.
import imp
import sys
import os

settings_path = os.environ.get('DJANGO_SETTINGS_FILE', None)

# if env.DJANGO_SETTINGS_FILE we need to get config file,
# compile it and put instead of bviewer.settings.local
# It is hack that allow run installed app from script.
if settings_path and 'bviewer.settings.local' not in sys.modules:
    module = imp.new_module('bviewer.settings.local')
    with open(settings_path) as f:
        code = compile(f.read(), 'local.py', 'exec')
        exec(code, globals(), module.__dict__)
    sys.modules['bviewer.settings.local'] = module
from bviewer.settings.local import *
