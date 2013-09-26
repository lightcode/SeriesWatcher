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


from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox, QDialogButtonBox
from languagescodes import codeToLocal
from serieswatcher.models import Serie
from serieswatcher.widgets.selectfolder import SelectFolder
from serieswatcher.worker import Runnable
from serieswatcher.tasks.makesearch import MakeSearch


class AddSerie(QtGui.QDialog):
    """Class to manipulate the window 'Add serie'."""
    serieAdded = QtCore.pyqtSignal(Serie)
    
    def __init__(self, parent=None):
        """Create the layout of the window 'Add serie'."""
        super(AddSerie, self).__init__(parent)
        self.setWindowTitle(u'Ajouter une série')
        self.setMinimumSize(400, 350)
        
        self.threadPool = QtCore.QThreadPool()
        self.seriesFound = []
        
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
        buttonBox = QDialogButtonBox()
        buttonBox.addButton('Annuler', QDialogButtonBox.RejectRole)
        self.forwardBtn = buttonBox.addButton('Suivant', 
                                              QDialogButtonBox.AcceptRole)
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
        
        # Buttons
        firstLayoutBtn = QtGui.QPushButton(u'Précédent')
        firstLayoutBtn.clicked.connect(self.goFirstPane)

        buttonBox = QDialogButtonBox()
        buttonBox.addButton('Annuler', QDialogButtonBox.RejectRole)
        buttonBox.addButton(u'Terminer', QDialogButtonBox.AcceptRole)
        buttonBox.rejected.connect(self.close)
        buttonBox.accepted.connect(self.validate)

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(firstLayoutBtn)
        buttonLayout.addWidget(buttonBox)
        
        # Layouts
        secondPaneLayout = QtGui.QVBoxLayout()
        secondPaneLayout.addWidget(groupSerie)
        secondPaneLayout.addWidget(groupDirectory)
        secondPaneLayout.addLayout(buttonLayout)
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
        """Disable the forward button."""
        self.forwardBtn.setDisabled(False)
    
    def goFirstPane(self):
        """Show the first pane."""
        self.stackedWidget.setCurrentIndex(0)
    
    def goSecondPane(self):
        """Show the second pane."""
        item = self.selectSerie.currentItem()
        if item:
            tvdbid, title, lang = item.serie
            self.title.setText(title)
            self.lang.clear()
            for serie in self.seriesFound:
                if serie[0] == tvdbid:
                    self.lang.addItem(codeToLocal(serie[2]),
                                      QtCore.QVariant(serie[2]))
            self.stackedWidget.setCurrentIndex(1)
    
    def search(self):
        """Perform a search on the TVDB.com."""
        userInput = self.searchTitle.text()
        task = MakeSearch(userInput)
        runnable = Runnable(task)
        runnable.task.searchFinished.connect(self.searchFinished)
        self.threadPool.tryStart(runnable)
    
    def searchFinished(self, seriesFound):
        self.seriesFound = seriesFound
        self.selectSerie.clear()
        if self.seriesFound:
            series = []
            for serie in self.seriesFound:
                if not [s for s in series if s[1] == serie[1]]:
                    item = QtGui.QListWidgetItem(serie[1])
                    setattr(item, 'serie', serie)
                    self.selectSerie.addItem(item)
                    series.append(serie)
        else:
            title = 'Erreur'
            message = u'Aucune série correspondante.'
            QMessageBox.critical(self, title, message)    
    
    def validate(self):
        """Check if the form is complete."""
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
            serie = Serie(pos=pos, title=title, tvdbID=tvdbID,
                          lang=lang, path=path)
            self.serieAdded.emit(serie)
            self.close()