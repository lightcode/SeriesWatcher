#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QIcon
from config import Config
from widgets import SelectFolder
from addserie import AddSerie
from models import Serie, Episode

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
        tool.addAction(QIcon('art/plus.png'), u'Ajouter une série', self.add)
        tool.addSeparator()
        tool.addAction(QIcon('art/arrow-up.png'), 'Monter', self.upItem)
        tool.addAction(QIcon('art/arrow-down.png'), 'Descendre', self.downItem)
        tool.addAction(QIcon('art/delete.png'), u'Supprimer', self.delete)
        
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
    
    
    def serieAdded(self, uuid, title, TVDBID, lang, path):
        item = QtGui.QListWidgetItem(title)
        setattr(item, 'uuid', uuid)
        setattr(item, 'path', path)
        setattr(item, 'lang', lang)
        setattr(item, 'TVDBID', TVDBID)
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



class EditSeries(QtGui.QDialog):
    edited = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(EditSeries, self).__init__(parent)
        self.setWindowTitle(u'Editer les séries')
        
        # Select serie pannel
        self.listSeries = ListSeries()
        self.listSeries.itemSelectionChanged.connect(self.itemSelectionChanged)
        
        # Edit serie pannel
        self.title = QtGui.QLineEdit()
        self.title.textChanged.connect(self.listSeries.setTitle)
        self.lang = QtGui.QLineEdit()
        self.lang.textChanged.connect(self.listSeries.setLang)
        self.path = SelectFolder()
        self.path.label.textChanged.connect(self.listSeries.setPath)
        
        groupSerie = QtGui.QGroupBox(u'Information de la série')
        form = QtGui.QFormLayout()
        form.addRow('Titre', self.title)
        form.addRow('Langue', self.lang)
        groupSerie.setLayout(form)
        
        groupDownload = QtGui.QGroupBox(u'Répertoire')
        layoutDl = QtGui.QVBoxLayout()
        layoutDl.addWidget(self.path)
        groupDownload.setLayout(layoutDl)
        
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Sauvegarder', QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.save)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.close)
        
        editSeriePannel = QtGui.QVBoxLayout()
        editSeriePannel.addWidget(groupSerie)
        editSeriePannel.addWidget(groupDownload)
        
        # Make a layout and go...
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.listSeries)
        layout.addLayout(editSeriePannel)
        
        bigLayout = QtGui.QVBoxLayout()
        bigLayout.addLayout(layout)
        bigLayout.addWidget(buttonBox)
        
        self.setLayout(bigLayout)
        
        # Select the first serie
        self.listSeries.listWidget.setCurrentRow(0)
    
    
    def itemSelectionChanged(self, title, path, lang):
        self.title.setText(title)
        self.lang.setText(lang)
        self.path.setPath(path)
    
    
    def save(self):
        for pos, serie in enumerate(self.listSeries.getItems()):
            uuid, title, path, tvdbID, lang = serie
            sdb = list(Serie.select(Serie.q.uuid==uuid))[0]
            sdb.title = title
            sdb.path = path
            sdb.tvdbID = tvdbID
            sdb.lang = lang
            sdb.pos = pos
        for item in self.listSeries.getItemsDeleted():
            sdb = list(Serie.select(Serie.q.uuid==item.uuid))[0]
            Episode.deleteBy(serie=sdb)
            Serie.delete(sdb.id)
        self.edited.emit()
        self.close()