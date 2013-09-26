#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Matthieu GAIGNIÈRE
#
# This file is part of SeriesWatcher.
#
# SeriesWatcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# SeriesWatcher is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# SeriesWatcher. If not, see <http://www.gnu.org/licenses/>.


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