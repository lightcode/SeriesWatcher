#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import os
from PyQt4 import QtCore, QtGui
from widgets.selectfolder import SelectFolder
from widgets.listseries import ListSeries
from models import Serie, Episode
from const import SERIES_IMG, SERIES_BANNERS

class EditSeries(QtGui.QDialog):
    '''Class to create and manipulate the window "Edit serie".'''
    edited = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        '''Create the window layout.'''
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
        '''Trigged when the selection change. Update informations
        in the form.'''
        self.title.setText(title)
        self.lang.setText(lang)
        self.path.setPath(path)
    
    
    def save(self):
        '''Save the modifications in the database.'''
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
            img = '%s/%s' % (SERIES_IMG, item.uuid)
            if os.path.isdir(img):
                shutil.rmtree('%s/%s' % (SERIES_IMG, item.uuid))
            banners = '%s/%s.jpg' % (SERIES_BANNERS, item.uuid)
            if os.path.isfile(banners):
                os.remove(banners)
        self.edited.emit()
        self.close()