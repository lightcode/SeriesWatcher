#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


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