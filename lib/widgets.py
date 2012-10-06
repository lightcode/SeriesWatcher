#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon


class SelectFile(QtGui.QWidget):
    def __init__(self, path='', parent=None):
        QtGui.QWidget.__init__(self, parent)
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
        self.label.setText(path)


class SelectFolder(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.label = QtGui.QLineEdit()
        btn = QtGui.QPushButton('Parcourir')
        btn.clicked.connect(self.selectFolder)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(btn)
        self.setLayout(layout)
    
    
    def selectFolder(self):
        path = QtGui.QFileDialog.getExistingDirectory(self, directory=self.path())
        self.label.setText(path)
    
    
    def path(self):
        return str(self.label.text())
    
    
    def setPath(self, path):
        self.label.setText(path)



class FilterMenu(QtGui.QPushButton):
    filterChanged = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        super(FilterMenu, self).__init__('Filtrer', parent)
        self.setFlat(True)
        self.setMenu(self.menu())
        self.setFixedWidth(180)
    
    
    def menu(self):
        self.dl = QtGui.QAction(u'Episodes disponibles', self)
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
        
        self.notDL = QtGui.QAction(u'Episodes non disponibles', self)
        setattr(self.notDL, 'filterID', 3)
        self.notDL.setCheckable(True)
        
        self.total = QtGui.QAction(u'Tous', self)
        setattr(self.total, 'filterID', 4)
        self.total.setCheckable(True)
        
        filters = QtGui.QActionGroup(self)
        filters.addAction(self.dl)
        filters.addAction(self.new)
        filters.addAction(self.favorite)
        filters.addAction(self.notDL)
        filters.addAction(self.total)
        filters.triggered.connect(self.filterTriggered)
        
        menu = QtGui.QMenu(self)
        menu.addActions(filters.actions())
        return menu
    
    
    def filterTriggered(self, action):
        self.setText(action.text())
        self.filterChanged.emit()
    
    
    def getFilterID(self):
        if self.dl.isChecked():
            return 0
        if self.new.isChecked():
            return 1
        if self.favorite.isChecked():
            return 2
        if self.notDL.isChecked():
            return 3
        if self.total.isChecked():
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
        if self.total.isChecked():
            return self.total
    
    
    def setCounters(self, nbTotal, nbNotDL, nbDL, nbNew, favorite):
        self.dl.setText(u'Episodes disponibles (%d)' % nbDL)
        self.new.setText(u'Nouveaux (%d)' % nbNew)
        self.favorite.setText(u'Favoris (%d)' % favorite)
        self.notDL.setText(u'Episodes non disponibles (%d)' % nbNotDL)
        self.total.setText(u'Tous (%d)' % nbTotal)
        self.setText(self.getFilterAction().text())



class EpisodesViewer(QtGui.QTableWidget):
    # Signals :
    pressEnter = QtCore.pyqtSignal('QModelIndex')
    refreshEpisodes = QtCore.pyqtSignal()
    viewStatusChanged = QtCore.pyqtSignal(bool)
    playClicked = QtCore.pyqtSignal()
    favoriteChanged = QtCore.pyqtSignal(bool)
    
    nbColumn = 3
    columnWidth = 260
    rowHeight = 100
    
    def __init__(self, parent = None):
        super(EpisodesViewer, self).__init__(parent)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        
        self.resizeTimer = QtCore.QTimer(self)
        self.resizeTimer.setInterval(200)
        self.resizeTimer.timeout.connect(self.updateSize)
        self.resizeTimer.start()
    
    
    def contextMenu(self, pos):
        nbEpisode = 0
        for item in self.selectedIndexes():
            (r, c) = (item.row(), item.column())
            if self.cellWidget(r, c):
                nbEpisode += 1
        if nbEpisode > 1:
            return
        
        btnMarkAsView = btnFavorite = True
        if nbEpisode == 1:
            episode = self.cellWidget(r, c).episode
            btnFavorite = not episode.favorite
            btnMarkAsView = not (episode.nbView > 0)
        
        menu = QtGui.QMenu()
        if btnMarkAsView:
            menu.addAction(QIcon('art/check.png'), 'Marquer comme vu', self.markAsView)
        else:
            menu.addAction(QIcon('art/uncheck.png'), 'Marquer comme non vu', self.markAsNotView)
        menu.addAction(QIcon('art/play.png'), 'Play', self.playClicked)
        if btnFavorite:
            menu.addAction(QIcon('art/star.png'), 'Ajouter en favoris', self.favorite)
        else:
            menu.addAction(QIcon('art/unstar.png'), 'Enlever des favoris', self.unfavorite)
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



class VideoItem(QtGui.QWidget):
    def __init__(self, episode):
        QtGui.QWidget.__init__(self)
        
        self.episode = episode
        
        self.img = QtGui.QLabel()
        self.img.setFixedWidth(120)
        
        title = '<b>%s</b><br/>%s' % (episode.number, episode.title)
        
        self.title = QtGui.QLabel(title)
        self.title.setAlignment(Qt.AlignTop)
        self.title.setStyleSheet('padding-top:10px')
        self.title.setMaximumHeight(55)
        self.title.setWordWrap(True)
        
        self.infos = QtGui.QLabel()
        self.infos.setAlignment(Qt.AlignBottom)
        
        text = QtGui.QVBoxLayout()
        text.addWidget(self.title)
        text.addWidget(self.infos)
        
        cell = QtGui.QHBoxLayout()
        cell.addWidget(self.img)
        cell.addLayout(text)
        
        self.setLayout(cell)
        
        # Set params :
        self.setStatus(episode.status)
        self.setFavorite(episode.favorite)
    
    
    def refresh(self):
        episode = self.episode
        self.setStatus(episode.status)
        self.setFavorite(episode.favorite)
    
    
    def setImage(self, image):
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.img.setPixmap(pixmap)
    
    
    def setTitle(self, titleStr):
        self.title.setText(titleStr)
    
    
    def setFavorite(self, value):
        if value:
            title = '<b>%s <img src="art/star.min.png"/></b><br/>%s' % (self.episode.number, self.episode.title)
        else:
            title = '<b>%s</b><br/>%s' % (self.episode.number, self.episode.title)
        self.title.setText(title)
    
    
    def setStatus(self, status):
        text = ''
        commonStyle = 'padding-left:1px;padding-bottom:5px'
        if status == 1:
            self.infos.setStyleSheet('color:#777;' + commonStyle)
            text = u'Disponible'
        elif status == 2:
            self.infos.setStyleSheet('color:red;' + commonStyle)
            text = u'Disponible <sup>Nouveau</sup>'
        elif status == 3:
            self.infos.setStyleSheet('color:#777;' + commonStyle)
            text = u'Inédit'
        self.infos.setText(text)