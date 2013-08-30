#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui


class Episode(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Episode, self).__init__(parent)
        
        self.img = QtGui.QLabel()
        self.img.setFixedWidth(120)
        
        self.title = QtGui.QLabel()
        self.title.setWordWrap(True)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.img)
        layout.addWidget(self.title)
        
        w = QtGui.QWidget()
        w.setLayout(layout)
        
        l = QtGui.QHBoxLayout()
        l.addWidget(w)
        
        self.setLayout(l)
        self.layout().setContentsMargins(0, 0, 0, 0)
    
    def setImage(self, path):
        pix = QtGui.QPixmap(path)
        pix = pix.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img.setPixmap(pix)
    
    def setTitle(self, title):
        self.title.setText(title)