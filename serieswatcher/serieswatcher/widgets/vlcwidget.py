#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QColor, QPalette

class VLCWidget(QtGui.QFrame):
    mouseMoved = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(VLCWidget, self).__init__(parent)
        self.setMouseTracking(True)
        # the UI player
        self._palette = self.palette()
        self._palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(self._palette)
        self.setAutoFillBackground(True)
    
    def mouseMoveEvent(self, e):
        self.mouseMoved.emit()