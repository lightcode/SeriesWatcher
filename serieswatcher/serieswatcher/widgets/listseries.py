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


from PyQt4.QtGui import QIcon
from PyQt4 import QtCore, QtGui
from serieswatcher.windows.addserie import AddSerie
from serieswatcher.const import ICONS
from serieswatcher.models import Serie


class ListSeries(QtGui.QWidget):
    itemSelectionChanged = QtCore.pyqtSignal('QString', 'QString', 'QString')
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self._itemsDeleted = []
        
        self.listWidget = QtGui.QListWidget()
        for serie in Serie.getSeries():
            item = QtGui.QListWidgetItem(serie.title)
            setattr(item, 'uuid', serie.uuid)
            setattr(item, 'path', serie.path)
            setattr(item, 'lang', serie.lang)
            setattr(item, 'TVDBID', serie.tvdbID)
            self.listWidget.addItem(item)
        self.listWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        
        tool = QtGui.QToolBar()
        tool.setStyleSheet('QToolBar { border:none; }')
        tool.addAction(QIcon(ICONS + 'plus.png'),
                       u'Ajouter une série', self.add)
        tool.addSeparator()
        tool.addAction(QIcon(ICONS + 'arrow-up.png'), 'Monter', self.upItem)
        tool.addAction(QIcon(ICONS + 'arrow-down.png'),
                       'Descendre', self.downItem)
        tool.addAction(QIcon(ICONS + 'delete.png'), u'Supprimer', self.delete)
        
        layoutButton = QtGui.QHBoxLayout()
        layoutButton.addWidget(tool)
        
        layoutList = QtGui.QVBoxLayout()
        layoutList.addWidget(self.listWidget)
        layoutList.addLayout(layoutButton)
        
        self.setLayout(layoutList)
    
    def add(self):
        addSerie = AddSerie(self)
        addSerie.serieAdded.connect(self.serieAdded)
        addSerie.open()
    
    def delete(self):
        currentIndex = self.listWidget.currentIndex().row()
        item = self.listWidget.takeItem(currentIndex)
        self._itemsDeleted.append(item)
        del item
    
    def getItemsDeleted(self):
        return self._itemsDeleted
    
    def serieAdded(self, serie):
        item = QtGui.QListWidgetItem(serie.title)
        setattr(item, 'uuid', serie.uuid)
        setattr(item, 'path', serie.path)
        setattr(item, 'lang', serie.lang)
        setattr(item, 'TVDBID', serie.tvdbID)
        self.listWidget.addItem(item)
    
    def _itemSelectionChanged(self):
        currentIndex = self.listWidget.currentIndex().row()
        title = self.listWidget.item(currentIndex).text()
        path = self.listWidget.item(currentIndex).path
        lang = self.listWidget.item(currentIndex).lang
        self.itemSelectionChanged.emit(title, path, lang)
    
    def upItem(self):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.takeItem(currentIndex)
        self.listWidget.insertItem(currentIndex - 1, currentItem)
        self.listWidget.setCurrentRow(currentIndex - 1)
    
    def downItem(self):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.takeItem(currentIndex)
        self.listWidget.insertItem(currentIndex + 1, currentItem)
        self.listWidget.setCurrentRow(currentIndex + 1)
    
    def setTitle(self, title):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.item(currentIndex)
        currentItem.setText(title)
    
    def setLang(self, lang):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.item(currentIndex)
        currentItem.lang = lang
    
    def setPath(self, path):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.item(currentIndex)
        currentItem.path = path
    
    def getItems(self):
        nb = self.listWidget.count()
        items = []
        for i in xrange(nb):
            title = unicode(self.listWidget.item(i).text())
            uuid = str(self.listWidget.item(i).uuid)
            path = unicode(self.listWidget.item(i).path)
            lang = unicode(self.listWidget.item(i).lang)
            TVDBID = self.listWidget.item(i).TVDBID
            items.append([uuid, title, path, TVDBID, lang])
        return items