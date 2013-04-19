#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox
from widgets.selectfolder import SelectFolder
from thetvdb import TheTVDB
from models import Serie
from languagescodes import codeToLocal

class AddSerie(QtGui.QDialog):
    '''Class to manipulate the window "Add serie".'''
    serieAdded = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        '''Create the layout of the window "Add serie".'''
        super(AddSerie, self).__init__(parent)
        self.setWindowTitle(u'Ajouter une série')
        self.setMinimumSize(400, 350)
        
        ######################
        # First panel
        ######################
        # Title & search
        search = QtGui.QPushButton('Rechercher')
        search.clicked.connect(self.search)
        self.searchTitle = QtGui.QLineEdit()
        self.searchTitle.returnPressed.connect(search.click)
        self.searchTitle.setPlaceholderText(u'Titre de la série...')
        title = QtGui.QHBoxLayout()
        title.addWidget(self.searchTitle)
        title.addWidget(search)
        searchLayout = QtGui.QVBoxLayout()
        searchLayout.addLayout(title)
        groupSearch = QtGui.QGroupBox(u'Recherchez votre série')
        groupSearch.setLayout(searchLayout)
        
        # Select the serie
        self.selectSerie = QtGui.QListWidget()
        self.selectSerie.currentItemChanged.connect(self.disableForwardBtn)
        selectLayout = QtGui.QVBoxLayout()
        selectLayout.addWidget(self.selectSerie)
        groupSelect = QtGui.QGroupBox(u'Sélectionner votre série')
        groupSelect.setLayout(selectLayout)
        
        # Button box
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        self.forwardBtn = buttonBox.addButton('Suivant', QtGui.QDialogButtonBox.AcceptRole)
        self.forwardBtn.clicked.connect(self.goSecondPane)
        self.forwardBtn.setDisabled(True)
        buttonBox.rejected.connect(self.close)
        
        # Layouts
        firstPaneLayout = QtGui.QVBoxLayout()
        firstPaneLayout.addWidget(groupSearch)
        firstPaneLayout.addWidget(groupSelect)
        firstPaneLayout.addWidget(buttonBox)
        firstPane = QtGui.QWidget()
        firstPane.setLayout(firstPaneLayout)
        
        ######################
        # Second panel
        ######################
        # Serie Information
        self.lang = QtGui.QComboBox()
        self.title = QtGui.QLineEdit()
        form = QtGui.QFormLayout()
        form.addRow('Titre', self.title)
        form.addRow('Langue', self.lang)
        groupSerie = QtGui.QGroupBox(u'Information de la série')
        groupSerie.setLayout(form)
        
        # Folder selection
        self.selectFolder = SelectFolder()
        layoutDir = QtGui.QVBoxLayout()
        layoutDir.addWidget(self.selectFolder)
        groupDirectory = QtGui.QGroupBox(u'Répertoire')
        groupDirectory.setLayout(layoutDir)
        
        # Button box
        buttonBox = QtGui.QDialogButtonBox()
        firstLayoutBtn = buttonBox.addButton(u'Précédent', QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.addButton(u'Terminé', QtGui.QDialogButtonBox.AcceptRole)
        firstLayoutBtn.clicked.connect(self.goFirstPane)
        buttonBox.rejected.connect(self.close)
        buttonBox.accepted.connect(self.validate)
        
        # Layouts
        secondPaneLayout = QtGui.QVBoxLayout()
        secondPaneLayout.addWidget(groupSerie)
        secondPaneLayout.addWidget(groupDirectory)
        secondPaneLayout.addWidget(buttonBox)
        secondPane = QtGui.QWidget()
        secondPane.setLayout(secondPaneLayout)
        
        ##############################
        # Create the stacked widget
        ##############################
        self.stackedWidget = QtGui.QStackedLayout(self)
        self.stackedWidget.addWidget(firstPane)
        self.stackedWidget.addWidget(secondPane)
        
        self.setLayout(self.stackedWidget)
    
    
    def disableForwardBtn(self):
        '''Disable the forward button.'''
        self.forwardBtn.setDisabled(False)
    
    
    def goFirstPane(self):
        '''Show the first pane.'''
        self.stackedWidget.setCurrentIndex(0)
    
    
    def goSecondPane(self):
        '''Show the second pane.'''
        item = self.selectSerie.currentItem()
        if item:
            tvdbid, title, lang = item.serie
            self.title.setText(title)
            self.lang.clear()
            for serie in self.seriesFound:
                if serie[0] == tvdbid:
                    self.lang.addItem(codeToLocal(serie[2]), QtCore.QVariant(serie[2]))
            self.stackedWidget.setCurrentIndex(1)
    
    
    def search(self):
        '''Perform a search on the TVDB.com.'''
        userInput = self.searchTitle.text()
        bdd = TheTVDB()
        self.seriesFound = bdd.searchSearie(userInput)
        
        self.selectSerie.clear()
        if self.seriesFound:
            s = []
            for serie in self.seriesFound:
                if not [_s for _s in s if _s[1] == serie[1]]:
                    item = QtGui.QListWidgetItem(serie[1])
                    setattr(item, 'serie', serie)
                    self.selectSerie.addItem(item)
                    s.append(serie)
        else:
            title = 'Erreur'
            message = u'Aucune série correspondante.'
            QMessageBox.critical(self, title, message)
    
    
    def validate(self):
        '''Check if the form is complete.'''
        title = unicode(self.title.text())
        lang = unicode(self.lang.itemData(self.lang.currentIndex()).toString())
        path = unicode(self.selectFolder.path())
        
        if title == '':
            title = u"Données incorrectes"
            message = u"Certaines données sont erronées."
            QMessageBox.critical(self, title, message)
        else:
            pos = len(Serie.getSeries())
            tvdbID = int(self.selectSerie.currentItem().serie[0])
            Serie(pos=pos, title=title, tvdbID=tvdbID, lang=lang, path=path)
            self.serieAdded.emit()
            self.close()