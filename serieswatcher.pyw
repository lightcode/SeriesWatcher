#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
from PyQt4 import QtCore, QtGui

sys.path.insert(0, os.path.abspath('serieswatcher/'))
from serieswatcher.main import Main

app = QtGui.QApplication(sys.argv)

locale = QtCore.QLocale.system().name()
translator = QtCore.QTranslator()
if os.path.splitext(sys.argv[0])[1] in ('.py', '.pyw'):
    reptrad = unicode(QtCore.QLibraryInfo.location(
        QtCore.QLibraryInfo.TranslationsPath))
else:
    reptrad = unicode("translations")
translator.load(QtCore.QString("qt_") + locale, reptrad)
app.installTranslator(translator)

window = Main()
window.show()
sys.exit(app.exec_())