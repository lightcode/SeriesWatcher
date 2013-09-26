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


from PyQt4 import QtGui


class SelectFile(QtGui.QWidget):
    def __init__(self, path='', parent=None):
        super(SelectFile, self).__init__(parent)
        self.label = QtGui.QLineEdit()
        btn = QtGui.QPushButton('Parcourir')
        btn.clicked.connect(self.selectFile)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(btn)
        self.setLayout(layout)
        self.setPath(path)
    
    def selectFile(self):
        directory = os.path.basename(self.path())
        path = QtGui.QFileDialog.getOpenFileName(self, directory=directory)
        self.label.setText(path)
    
    def path(self):
        return str(self.label.text())
    
    def setPath(self, path):
        if not path:
            path = ""
        self.label.setText(path)