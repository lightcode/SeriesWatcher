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
from PyQt4 import QtGui
from serieswatcher.const import ICONS


class VideoItem(QtGui.QWidget):
    def __init__(self, episode):
        super(VideoItem, self).__init__()

        self.episode = episode
        self.coverShown = False
        
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
        
        self.refresh()

    
    def resizeEvent(self, event):
        super(VideoItem, self).resizeEvent(event)
        self.setTitle(self.episode.title)
    
    def refresh(self):
        self.setStatus(self.episode.status)
        self.setFavorite(self.episode.favorite)
    
    def setImage(self, image):
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.img.setPixmap(pixmap)

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
            head = '<b>%s <img src="%sstar.min.png"/></b>' % \
                                        (self.episode.number, ICONS)
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