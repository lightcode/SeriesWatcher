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
        path = QtGui.QFileDialog.getExistingDirectory(
            self, directory=self.path()
        )
        self.label.setText(path)
    
    def path(self):
        return str(self.label.text())
    
    def setPath(self, path):
        self.label.setText(path)