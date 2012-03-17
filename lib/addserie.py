#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox
from widgets import SelectFolder
from thetvdb import TheTVDB
from camelcase import getCamelCase
from config import Config

class AddSerie(QtGui.QDialog):
    # Signals :
    serieAdded = QtCore.pyqtSignal('QString', 'QString', int, 'QString', 'QString')
    
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Ajouter une série')
        
        self.name = QtGui.QLineEdit()
        
        # Title & search
        self.title = QtGui.QLineEdit()
        search = QtGui.QPushButton('Rechercher')
        search.clicked.connect(self.search)
        title = QtGui.QHBoxLayout()
        title.addWidget(self.title)
        title.addWidget(search)
        
        self.theTVDB = QtGui.QLineEdit()
        self.lang = QtGui.QLineEdit()
        self.selectFolder = SelectFolder()
        
        groupSerie = QtGui.QGroupBox(u'Information de la série')
        form = QtGui.QFormLayout()
        form.addRow('Titre', title)
        form.addRow('Nom', self.name)
        form.addRow('ID OpenTV', self.theTVDB)
        form.addRow('Langue', self.lang)
        groupSerie.setLayout(form)
        
        groupDownload = QtGui.QGroupBox(u'Vos téléchargements')
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.selectFolder)
        groupDownload.setLayout(layout)
        
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Sauvegarder', QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.validate)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.close)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(groupSerie)
        layout.addWidget(groupDownload)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)
    
    
    def search(self):
        userInput = self.title.text()
        bdd = TheTVDB()
        seriesFound = bdd.searchSearie(userInput)
        self.choiceSerie(seriesFound)
    
    
    def choiceSerie(self, seriesFound):
        if len(seriesFound) > 1:
            titles = []
            for serie in seriesFound:
                titles.append(u'%s (%s)' % (serie[1], serie[2]))
            
            title = u'Ajouter une série'
            label = u'Choisissez votre série :'
            r = QtGui.QInputDialog.getItem(self, title, label, titles, 0, False)
            select = unicode(r[0])
            index = titles.index(select)
            infos = seriesFound[index]
        elif len(seriesFound) == 1:
            infos = seriesFound[0]
        
        if len(seriesFound) > 0:
            serieId, serieName, lang = infos
            self.lang.setText(lang)
            self.title.setText(serieName)
            self.theTVDB.setText(serieId)
            self.name.setText(getCamelCase(serieName))
        else:
            title = 'Erreur'
            message = u'Aucune série correspondante'
            QMessageBox.critical(self, title, message)
    
    
    def validate(self):
        nbErrors = 0
        name = self.name.text()
        if name == '':
            nbErrors += 1
        
        title = self.title.text()
        if title == '':
            nbErrors += 1
        
        try:
            theTVDB = int(self.theTVDB.text())
        except ValueError:
            nbErrors += 1
        
        lang = self.lang.text()
        if lang == '':
            nbErrors += 1
        
        path = self.selectFolder.path()
        if path == '':
            nbErrors += 1
        
        if nbErrors > 0:
            title = u"Données incorrectes"
            message = u"Certaines données sont erronées."
            QMessageBox.critical(self, title, message)
        else:
            Config.addSerie(name, title, path, theTVDB, lang)
            self.serieAdded.emit(name, title, theTVDB, lang, path)
            self.close()