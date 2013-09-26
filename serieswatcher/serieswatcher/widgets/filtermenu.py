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


from PyQt4 import QtCore, QtGui


class FilterMenu(QtGui.QPushButton):
    filterChanged = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(FilterMenu, self).__init__('Filtrer', parent)
        self.setFlat(True)
        self.setMenu(self.menu())
        self.setFixedWidth(180)
    
    def menu(self):
        self.dl = QtGui.QAction(u'Disponibles', self)
        setattr(self.dl, 'filterID', 0)
        self.dl.setCheckable(True)
        self.setText(self.dl.text())
        self.dl.setChecked(True)
        
        self.new = QtGui.QAction('Nouveau', self)
        setattr(self.new, 'filterID', 1)
        self.new.setCheckable(True)
        
        self.favorite = QtGui.QAction('Favoris', self)
        setattr(self.favorite, 'filterID', 2)
        self.favorite.setCheckable(True)
        
        self.notDL = QtGui.QAction(u'Non disponibles', self)
        setattr(self.notDL, 'filterID', 3)
        self.notDL.setCheckable(True)
        
        self.all = QtGui.QAction(u'Tous', self)
        setattr(self.all, 'filterID', 4)
        self.all.setCheckable(True)
        
        filters = QtGui.QActionGroup(self)
        filters.addAction(self.dl)
        filters.addAction(self.new)
        filters.addAction(self.favorite)
        filters.addAction(self.notDL)
        filters.addAction(self.all)
        filters.triggered.connect(self.filterTriggered)
        
        self._menu = QtGui.QMenu(self)
        self._menu.addActions(filters.actions())
        return self._menu
    
    def filterTriggered(self, action):
        self.setText(action.text())
        self.filterChanged.emit()

    def setSelection(self, action):
        action.setChecked(True)
        self.filterTriggered(action)
    
    def getFilterID(self):
        if self.dl.isChecked():
            return 0
        if self.new.isChecked():
            return 1
        if self.favorite.isChecked():
            return 2
        if self.notDL.isChecked():
            return 3
        if self.all.isChecked():
            return 4
    
    def getFilterAction(self):
        if self.dl.isChecked():
            return self.dl
        if self.new.isChecked():
            return self.new
        if self.notDL.isChecked():
            return self.notDL
        if self.favorite.isChecked():
            return self.favorite
        if self.all.isChecked():
            return self.all
    
    def setCounters(self, nball, nbNotDL, nbDL, nbNew, favorite):
        self.dl.setText(u'Disponibles (%d)' % nbDL)
        self.new.setText(u'Nouveaux (%d)' % nbNew)
        self.favorite.setText(u'Favoris (%d)' % favorite)
        self.notDL.setText(u'Non disponibles (%d)' % nbNotDL)
        self.all.setText(u'Tous (%d)' % nball)
        self.setText(self.getFilterAction().text())