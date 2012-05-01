#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

class SelectFolder(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.label = QtGui.QLineEdit()
        btn = QtGui.QPushButton('Parcourir')
        btn.clicked.connect(self.selectFolder)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(btn)
        self.setLayout(layout)
    
    
    def selectFolder(self):
        path = QtGui.QFileDialog.getExistingDirectory()
        path = '%s/*' % path
        self.label.setText(path)
    
    
    def path(self):
        return self.label.text()
    
    
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
        self.dl = QtGui.QAction(u'Episodes téléchargés', self)
        setattr(self.dl, 'filterID', 0)
        self.dl.setCheckable(True)
        self.setText(self.dl.text())
        self.dl.setChecked(True)
        
        self.new = QtGui.QAction('Nouveau', self)
        setattr(self.new, 'filterID', 1)
        self.new.setCheckable(True)
        
        self.notDL = QtGui.QAction(u'Episodes non téléchargés', self)
        setattr(self.notDL, 'filterID', 2)
        self.notDL.setCheckable(True)
        
        self.total = QtGui.QAction(u'Tous', self)
        setattr(self.total, 'filterID', 3)
        self.total.setCheckable(True)
        
        filters = QtGui.QActionGroup(self)
        filters.addAction(self.dl)
        filters.addAction(self.new)
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
        if self.notDL.isChecked():
            return 2
        if self.total.isChecked():
            return 3
    
    
    def getFilterAction(self):
        if self.dl.isChecked():
            return self.dl
        if self.new.isChecked():
            return self.new
        if self.notDL.isChecked():
            return self.notDL
        if self.total.isChecked():
            return self.total
    
    
    def setCounters(self, nbTotal, nbNotDL, nbDL, nbNew):
        self.dl.setText(u'Episodes téléchargés (%d)' % nbDL)
        self.new.setText(u'Nouveaux (%d)' % nbNew)
        self.notDL.setText(u'Episodes non téléchargés (%d)' % nbNotDL)
        self.total.setText(u'Tous (%d)' % nbTotal)
        self.setText(self.getFilterAction().text())


class EpisodesViewer(QtGui.QTableWidget):
    # Signals :
    pressEnter = QtCore.pyqtSignal('QModelIndex')
    refreshEpisodes = QtCore.pyqtSignal()
    markedAsView = QtCore.pyqtSignal()
    markedAsNotView = QtCore.pyqtSignal()
    playClicked = QtCore.pyqtSignal()
    
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
    
    
    def contextMenu(self, pos):
        globalPos = self.mapToGlobal(pos)
        
        nbNone = 0
        for item in self.selectedIndexes():
            (r, c) = (item.row(), item.column())
            if not self.cellWidget(r, c):
                nbNone += 1
        if nbNone == len(self.selectedIndexes()):
            return
        
        menu = QtGui.QMenu()
        markAsView = menu.addAction('Marquer comme vu')
        markAsView.setIcon(QtGui.QIcon('art/check.png'))
        markAsView.triggered.connect(self.markAsView)
        
        markAsNotView = menu.addAction('Marquer comme non vu')
        markAsNotView.setIcon(QtGui.QIcon('art/uncheck.png'))
        markAsNotView.triggered.connect(self.markAsNotView)
        
        play = menu.addAction('Play')
        play.setIcon(QtGui.QIcon('art/play.png'))
        play.triggered.connect(self.playClicked)
        menu.exec_(globalPos)
    
    
    def markAsView(self):
        self.markedAsView.emit()
    
    
    def markAsNotView(self):
        self.markedAsNotView.emit()
    
    
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
    
    
    def resizeEvent(self, size):
        QtGui.QTableWidget.resizeEvent(self, size)
        oldNbColumn = size.oldSize().width() // 260
        self.nbColumn = size.size().width() // 260
        self.columnWidth = size.size().width() // self.nbColumn
        self.setColumnCount(self.nbColumn)
        if oldNbColumn != self.nbColumn:
            self.setColumnCount(self.nbColumn)
            self.refreshEpisodes.emit()



class VideoItem(QtGui.QWidget):
    def __init__(self, titleStr):
        QtGui.QWidget.__init__(self)
        
        self.img = QtGui.QLabel()
        self.img.setMaximumWidth(120)
        
        self.title = QtGui.QLabel(titleStr)
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
    
    
    def setImage(self, image):
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.img.setPixmap(pixmap)
    
    
    def setTitle(self, titleStr):
        self.title.setText(titleStr)
    
    
    def setInfos(self, infos):
        text = ''
        commonStyle = 'padding-left:1px;padding-bottom:5px'
        if infos == 1:
            self.infos.setStyleSheet('color:#777;' + commonStyle)
            text = u'Téléchargé'
        elif infos == 2:
            self.infos.setStyleSheet('color:red;' + commonStyle)
            text = u'Téléchargé <sup>Nouveau</sup>'
        self.infos.setText(text)