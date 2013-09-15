#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui


class GetCoverTask(QtCore.QObject):
    coverLoaded = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, coverPath):
        super(GetCoverTask, self).__init__()
        self._coverPath = coverPath
    
    def run(self):
        image = QtGui.QImage(self._coverPath)
        image = image.scaled(120, 120, Qt.KeepAspectRatio, 
                             Qt.SmoothTransformation)
        self.coverLoaded.emit(image)