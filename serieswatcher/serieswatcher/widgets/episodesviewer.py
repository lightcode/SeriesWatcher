#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon
from PyQt4 import QtCore, QtGui
from ..const import ICONS

class EpisodesViewer(QtGui.QTableWidget):
    pressEnter = QtCore.pyqtSignal('QModelIndex')
    refreshEpisodes = QtCore.pyqtSignal()
    viewStatusChanged = QtCore.pyqtSignal(bool)
    playClicked = QtCore.pyqtSignal()
    favoriteChanged = QtCore.pyqtSignal(bool)
    
    def __init__(self, parent = None):
        super(EpisodesViewer, self).__init__(parent)
        
        self.nbColumn = 3
        self.columnWidth = 260
        self.rowHeight = 100
        
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        
        self.resizeTimer = QtCore.QTimer(self)
        self.resizeTimer.timeout.connect(self.updateSize)
        self.resizeTimer.start(250)
        
        self.imageTimer = QtCore.QTimer(self)
        self.imageTimer.timeout.connect(self.redrawImages)
        self.imageTimer.start(250)
    
    def redrawImages(self):
        for r in xrange(self.rowCount()):
            posY = self.rowViewportPosition(r)
            for c in xrange(self.columnCount()):
                if -self.rowHeight <= posY <= self.height():
                    try:
                        self.cellWidget(r, c).showImage()
                    except AttributeError:
                        pass
                else:
                    try:
                        self.cellWidget(r, c).delImage()
                    except AttributeError:
                        pass
    
    def contextMenu(self, pos):
        nbEpisode = 0
        for item in self.selectedIndexes():
            (r, c) = (item.row(), item.column())
            if self.cellWidget(r, c):
                nbEpisode += 1
        if nbEpisode == 0:
            return
        
        btnMarkAsView = btnFavorite = True
        if nbEpisode == 1:
            episode = self.cellWidget(r, c).episode
            btnFavorite = not episode.favorite
            btnMarkAsView = not (episode.nbView > 0)
        
        menu = QtGui.QMenu()
        if btnMarkAsView or nbEpisode > 1:
            menu.addAction(QIcon(ICONS + 'check.png'), 'Marquer comme vu', self.markAsView)
        if not btnMarkAsView or nbEpisode > 1:
            menu.addAction(QIcon(ICONS + 'uncheck.png'), 'Marquer comme non vu', self.markAsNotView)
        menu.addAction(QIcon(ICONS + 'play.png'), 'Play', self.playClicked)
        if btnFavorite or nbEpisode > 1:
            menu.addAction(QIcon(ICONS + 'star.png'), 'Ajouter aux favoris', self.favorite)
        if not btnFavorite or nbEpisode > 1:
            menu.addAction(QIcon(ICONS + 'unstar.png'), 'Enlever des favoris', self.unfavorite)
        menu.addAction('Copier le titre', self.copyTitle)
        menu.exec_(self.mapToGlobal(pos))
    
    def favorite(self):
        self.favoriteChanged.emit(True)
    
    def unfavorite(self):
        self.favoriteChanged.emit(False)
    
    def copyTitle(self):
        self.pressPaper = QtGui.QApplication.clipboard()
        indexes = self.selectedIndexes()
        if len(indexes) == 1:
            r, c = indexes[0].row(), indexes[0].column()
            title = self.cellWidget(r, c).title.text()[17:]
            self.pressPaper.setText(title)
    
    def markAsView(self):
        self.viewStatusChanged.emit(True)
    
    def markAsNotView(self):
        self.viewStatusChanged.emit(False)
    
    def setRowCount(self, nbRows):
        QtGui.QTableWidget.setRowCount(self, nbRows)
        [self.setRowHeight(i, self.rowHeight) for i in xrange(nbRows)]
    
    def setColumnCount(self, nbColumn):
        QtGui.QTableWidget.setColumnCount(self, nbColumn)
        [self.setColumnWidth(i, self.columnWidth) for i in xrange(nbColumn)]
    
    def keyPressEvent(self, e):
        QtGui.QTableWidget.keyPressEvent(self, e)
        key = e.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.pressEnter.emit(self.currentIndex())
    
    def updateSize(self):
        oldNbColumn = self.columnCount()
        self.setColumnCount(self.nbColumn)
        if oldNbColumn != self.nbColumn:
            self.refreshEpisodes.emit()
    
    def resizeEvent(self, size):
        QtGui.QTableWidget.resizeEvent(self, size)
        self.nbColumn = size.size().width() // 260
        self.columnWidth = size.size().width() // self.nbColumn