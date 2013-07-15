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

from bviewer.settings.local import *
