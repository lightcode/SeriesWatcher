#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon
from PyQt4 import QtCore, QtGui


class SelectFolder(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SelectFolder, self).__init__(parent)
        self.label = QtGui.QLineEdit()
        btn = QtGui.QPushButton('Parcourir')
        btn.clicked.connect(self.selectFolder)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(btn)
        self.setLayout(layout)
    
    def selectFolder(self):
        path = QtGui.QFileDialog.getExistingDirectory(self,
                                                      directory=self.path())
        self.label.setText(path)
    
    def path(self):
        return str(self.label.text())
    
    def setPath(self, path):
        self.label.setText(path)