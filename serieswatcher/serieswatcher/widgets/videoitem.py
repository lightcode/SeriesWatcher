#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon
from PyQt4 import QtCore, QtGui
from ..const import ICONS
from ..worker import Runnable


class GetCover(QtCore.QObject):
    coverLoaded = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, coverPath):
        super(GetCover, self).__init__()
        self._coverPath = coverPath
    
    def run(self):
        image = QtGui.QImage(self._coverPath)
        image = image.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.coverLoaded.emit(image)


class VideoItem(QtGui.QWidget):
    def __init__(self, episode):
        super(VideoItem, self).__init__()

        self.threadPool = QtCore.QThreadPool()
        
        self.episode = episode
        self._coverShown = False
        
        self.img = QtGui.QLabel()
        self.img.setFixedWidth(120)
        
        number = '<b>%s</b>' % episode.number
        self.head = QtGui.QLabel(number)
        
        self.title = QtGui.QLabel()
        self.title.setAlignment(Qt.AlignTop)
        self.title.setMaximumHeight(55)
        self.title.setWordWrap(True)
        
        self.infos = QtGui.QLabel()
        self.infos.setAlignment(Qt.AlignBottom)
        
        text = QtGui.QVBoxLayout()
        text.addWidget(self.head)
        text.addWidget(self.title, 10)
        text.addWidget(self.infos)
        
        cell = QtGui.QHBoxLayout()
        cell.addWidget(self.img)
        cell.addLayout(text)
        self.setLayout(cell)
        
        # Set params :
        self.setStatus(episode.status)
        self.setFavorite(episode.favorite)
    
    def refresh(self):
        self.setStatus(self.episode.status)
        self.setFavorite(self.episode.favorite)
    
    def delImage(self):
        if self._coverShown:
            self.img.clear()
            self._coverShown = False
    
    def showImage(self):
        if not self._coverShown:
            task = GetCover(self.episode.cover)
            runnable = Runnable(task)
            runnable.task.coverLoaded.connect(self.setImage)
            self.threadPool.tryStart(runnable)
            self._coverShown = True
    
    def setImage(self, image):
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.img.setPixmap(pixmap)
    
    def resizeEvent(self, event):
        super(VideoItem, self).resizeEvent(event)
        self.setTitle(self.episode.title)

    def setTitle(self, titleStr):
        lines = []
        currentSize = []
        font = self.title.font()
        fontm = QtGui.QFontMetricsF(font)
        maxWidth = self.title.width()
        words = titleStr.split(' ')
        
        for i in range(2):
            lines.append('')
            currentSize.append(0)
            for word in words[:]:
                newSize = currentSize[i] + fontm.width(word) + fontm.width(' ')
                if newSize < maxWidth:
                    del words[0]
                    lines[i] += word + ' '
                    currentSize[i] = newSize
                else:
                    break

        title = '\n'.join(lines) + ('...' if words else '')
        self.title.setText(title)
    
    def setFavorite(self, value):
        if value:
            head = '<b>%s <img src="%sstar.min.png"/></b>' % (self.episode.number, ICONS)
        else:
            head = '<b>%s</b>' % (self.episode.number)
        self.head.setText(head)
    
    def setStatus(self, status):
        self.infos.setProperty('class', 'status')
        text = ''
        if status == 1:
            self.infos.setProperty('status', 'available')
            text = u'Disponible'
        elif status == 2:
            self.infos.setProperty('status', 'new')
            text = u'Disponible <sup>Nouveau</sup>'
        elif status == 3:
            self.infos.setProperty('status', 'original')
            text = u'Inédit'
        # Force the CSS refresh
        self.infos.setStyleSheet('')
        self.infos.setText(text)