# -*- coding: utf-8 -*-

# Package import order:
#   local -> django
#   test -> local -> django
#   debug -> local -> django
#
# sample.py - sample for local.py.
#
# run '--settings=bviewer.settings.test' for use `test` settings.
# run '--settings=bviewer.settings.debug' for use `debug` settings.

from bviewer.settings.local import *
