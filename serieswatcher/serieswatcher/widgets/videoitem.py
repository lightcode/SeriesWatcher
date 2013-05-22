#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon
from PyQt4 import QtCore, QtGui
from ..const import ICONS


class VideoItem(QtGui.QWidget):
    def __init__(self, episode):
        super(VideoItem, self).__init__()
        
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
        episode = self.episode
        self.setStatus(episode.status)
        self.setFavorite(episode.favorite)
    
    def delImage(self):
        if self._coverShown:
            self.img.clear()
            self._coverShown = False
    
    def showImage(self):
        if not self._coverShown:
            image = QtGui.QImage(self.episode.cover)
            image = image.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setImage(image)
            self._coverShown = True
    
    def setImage(self, image):
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.img.setPixmap(pixmap)
    
    def setTitle(self, titleStr):
        maxWidth = self.title.width() * 1.5
        font = self.title.font()
        fontm = QtGui.QFontMetricsF(font)
        titleStr = fontm.elidedText(titleStr, Qt.ElideRight, maxWidth)
        self.title.setText(titleStr)
    
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