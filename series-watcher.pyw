# -*- coding: utf8 -*-
import cPickle as pickle
import math
import os.path
import sys
import time
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from lib.config import Config
from lib.serie import Serie
from lib.threads import EpisodesLoaderThread, SearchThread, RefreshSeriesThread
from lib.addSerie import AddSerie
from lib.about import About
from lib.options import Options
from lib.widgets import EpisodesViewer, VideoItem
import desktop

class Main(QtGui.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setWindowTitle('Series Watcher')
        self.setMinimumSize(820, 600)
        self.resize(1150, 780)
        self.setWindowIcon(QtGui.QIcon('art/film.png'))
        
        self.setup()
        Config.loadConfig()
        self.startTheads()
        self.createWindow()
        if Config.series:
            self.serieChanged(0, True)
        else:
            self.openAddSerie()
    
    
    def startTheads(self):
        self.commandOpen = QtCore.QProcess()
        
        self.episodesLoader = EpisodesLoaderThread()
        self.episodesLoader.episodeLoaded.connect(self.episodeLoaded)
        
        self.searchThread = SearchThread()
        self.searchThread.start()
        self.searchThread.searchFinished.connect(self.searchFinished)
        
        self.refreshSeries = RefreshSeriesThread()
        self.refreshSeries.serieLoadStarted.connect(self.serieLoadStarted)
        self.refreshSeries.serieLoaded.connect(self.serieLoaded)
        self.refreshSeries.start()
    
    
    def currentSerieId(self):
        return self.selectSerie.currentIndex()
    
    
    # =========================
    #  Window Manager
    # =========================
    def createWindow(self):
        self.createMenu()
        
        # StatusBar
        self.status = self.statusBar()
        self.nbEpisodes = QtGui.QLabel()
        self.status.addPermanentWidget(self.nbEpisodes)
        
        # HEADER
        self.imageSerie = QtGui.QLabel()
        self.imageSerie.setFixedSize(758, 140)
        
        self.selectSerie = QtGui.QComboBox()
        for e in Config.series:
            self.selectSerie.addItem(e[1])
        self.selectSerie.currentIndexChanged.connect(self.serieChanged)
        
        self.description = QtGui.QLabel()
        self.description.setMinimumWidth(350)
        self.description.setWordWrap(True)
        self.description.setAlignment(Qt.AlignTop)
        
        infos = QtGui.QVBoxLayout()
        infos.addWidget(self.selectSerie)
        infos.addWidget(self.description)
        
        header = QtGui.QHBoxLayout()
        header.addLayout(infos)
        header.addWidget(self.imageSerie)
        
        # FILTER
        self.searchBar = QtGui.QLineEdit()
        self.searchBar.textChanged.connect(self.searchChanged)
        
        self.selectSeason = QtGui.QComboBox()
        self.selectSeason.currentIndexChanged.connect(self.refreshScreen)
        
        self.filterDL = QtGui.QCheckBox(u'Episodes téléchargés')
        self.filterDL.setChecked(True)
        self.filterDL.toggled.connect(self.filterDL_toggled)
        
        self.filterNew = QtGui.QCheckBox(u'Nouveaux')
        self.filterNew.toggled.connect(self.filterNew_toggled)
        
        filterBar = QtGui.QHBoxLayout()
        filterBar.addWidget(self.searchBar)
        filterBar.addWidget(self.selectSeason)
        filterBar.addWidget(self.filterDL)
        filterBar.addWidget(self.filterNew)
        
        # BODY
        self.episodes = EpisodesViewer()
        self.episodes.refreshEpisodes.connect(self.refreshScreen)
        self.episodes.pressEnter.connect(self.episodesDblClicked)
        self.episodes.markedAsView.connect(self.viewSelectEpisodeMenu)
        self.episodes.markedAsNotView.connect(self.notViewSelectEpisodeMenu)
        self.episodes.doubleClicked.connect(self.episodesDblClicked)
        self.episodes.currentCellChanged.connect(self.episodeChanged)
        body = QtGui.QHBoxLayout()
        body.addWidget(self.episodes)
        
        # FOOTER
        self.selectionTitle = QtGui.QLabel()
        self.selectionTitle.setAlignment(Qt.AlignTop)
        self.selectionDescription = QtGui.QLabel()
        self.selectionDescription.setMinimumWidth(350)
        self.selectionDescription.setFixedHeight(100)
        self.selectionDescription.setWordWrap(True)
        self.selectionDescription.setAlignment(Qt.AlignTop)
        footerLayout = QtGui.QHBoxLayout()
        footerLayout.addWidget(self.selectionTitle)
        footerLayout.addWidget(self.selectionDescription)
        self.footer = QtGui.QWidget()
        self.footer.setLayout(footerLayout)
        
        window = QtGui.QVBoxLayout()
        window.addLayout(header)
        window.addLayout(filterBar)
        window.addLayout(body)
        window.addWidget(self.footer)
        
        win = QtGui.QWidget()
        win.setLayout(window)
        self.setCentralWidget(win)
    
    
    def createMenu(self):
        self.menubar = self.menuBar()
        
        ## MENU SERIES
        seriesMenu = self.menubar.addMenu('S\xE9ries')
        
        addSerie = seriesMenu.addAction(u'Nouvelle série')
        addSerie.triggered.connect(self.openAddSerie)
        addSerie.setShortcut('Ctrl+N')
        
        refresh = seriesMenu.addAction(u'Mettre à jour cette série')
        refresh.triggered.connect(self.updateSerieMenu)
        refresh.setShortcut('Ctrl+U')
        
        refreshAll = seriesMenu.addAction(u'Mettre à jour les séries')
        refreshAll.triggered.connect(self.updateAllSeriesMenu)
        
        ## MENU EPISODES
        episodesMenu = self.menubar.addMenu('Episodes')
        
        refresh = episodesMenu.addAction(u'Recharger')
        refresh.triggered.connect(self.reloadMenu)
        refresh.setIcon(QtGui.QIcon('art/refresh.png'))
        refresh.setShortcut('Ctrl+R')        
        
        view = episodesMenu.addAction(u'Marquer comme vue')
        view.triggered.connect(self.viewSelectEpisodeMenu)
        view.setIcon(QtGui.QIcon('art/check.png'))
        view.setShortcut('Ctrl+K')
        
        view = episodesMenu.addAction(u'Marquer comme non vue')
        view.setIcon(QtGui.QIcon('art/uncheck.png'))
        view.triggered.connect(self.notViewSelectEpisodeMenu)
        
        view = episodesMenu.addAction(u'Marquer la série comme vue')
        view.triggered.connect(self.allEpisodeView)
        
        ## MENU AIDE
        helpMenu = self.menubar.addMenu('Series Watcher')
        helpMenu.addAction(u'Options', self.openOptions)
        helpMenu.addAction(u'A propos', self.openAbout)
    
    
    def clearSelectionInfos(self):
        self.selectionTitle.setText("")
        self.selectionDescription.setText("")
        self.footer.hide()
    
    
    # =================
    #  Config Manager
    # =================
    def setup(self):
        if not os.path.isdir('banners'):
            os.mkdir('banners')
        if not os.path.isdir('img'):
            os.mkdir('img')
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
    
    
    # =================
    #  Slots
    # =================
    def filterNew_toggled(self):
        self.filterDL.blockSignals(True)
        self.filterDL.setChecked(True)
        self.refreshScreen()
        self.filterDL.blockSignals(False)
    
    
    def filterDL_toggled(self):
        self.filterNew.blockSignals(True)
        self.filterNew.setChecked(False)
        self.refreshScreen()
        self.filterNew.blockSignals(False)
    
    
    def allEpisodeView(self):
        episodesViewed = []
        for number in self.currentSerie.downloadedEpisode.iterkeys():
            episodesViewed.append(number)
        self.currentSerie.episodesViewed = episodesViewed
        self.currentSerie.episodesViewedSave()
    
    
    def reloadMenu(self):
        serieLocalID = self.currentSerieId()
        self.currentSerie.loadDownloadedList(serieLocalID)
        self.loadSerie(serieLocalID)
        self.refreshScreen()
    
    
    def serieLoadStarted(self, title):
        self.status.showMessage('Chargement de %s' % title)
    
    
    def openAbout(self):
        about = About(self)
        about.show()


    def openOptions(self):
        options = Options(self)
        options.show()


    def openAddSerie(self):
        s = AddSerie(self)
        s.serieAdded.connect(self.serieAdded)
        s.show()
    
    
    def updateSerieMenu(self):
        self.refreshSeries.addSerie(self.currentSerieId())
    
    
    def updateAllSeriesMenu(self):
        for e in range(len(Config.series)):
            self.refreshSeries.addSerie(e)
    
    
    def episodeChanged(self, r, c):
        nbItemSelect = len(self.episodes.selectedIndexes())
        if (r, c) in self.map and nbItemSelect <= 1:
            episode = self.map[r, c]
            self.footer.show()
            self.selectionTitle.setText(episode['title'])
            self.selectionDescription.setText(episode['desc'])
        else:
            self.clearSelectionInfos()
    
    
    def serieAdded(self, name, title, theTvDb, lang, path):
        Config.addSerie(name, title, theTvDb, lang, path)
        self.selectSerie.clear()
        for e in Config.series:
            self.selectSerie.addItem(e[1])
        self.selectSerie.setCurrentIndex(len(Config.series) - 1)
    
    
    def viewSelectEpisodeMenu(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = coord = item.row(), item.column()
            video = self.episodes.cellWidget(r, c)
            if video is not None:
                number = self.map[coord]['number']
                if number in self.currentSerie.downloadedEpisode:
                    video.setInfos(1)
                    self.episodeViewed(number)
        self.refreshCount()
    
    
    def notViewSelectEpisodeMenu(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = coord = item.row(), item.column()
            video = self.episodes.cellWidget(r, c)
            if video is not None:
                number = self.map[coord]['number']
                if number in self.currentSerie.downloadedEpisode:
                    video.setInfos(2)
                    self.episodeNotViewed(self.map[coord]['number'])
        self.refreshCount()
    
    
    def episodesDblClicked(self, n):
        command = Config.config['command_open']
        r, c = coord = n.row(), n.column()
        if coord in self.map:
            episode = self.map[coord]
            if episode['path'] is not None:
                # Open the file
                path = os.path.normpath(episode['path'])
                if command is None:
                    desktop.open(path)
                else:
                    self.commandOpen.startDetached(command, [path])
                # Change the title
                self.episodes.cellWidget(r, c).setInfos(1)
                # Add the episode in the already view list
                self.episodeViewed(episode['number'])
                self.refreshCount()
    
    
    def episodeViewed(self, number):
        if number not in self.currentSerie.episodesViewed:
            self.currentSerie.episodesViewed.add(number)
            self.currentSerie.episodesViewedSave()
    
    
    def episodeNotViewed(self, number):
        if number in self.currentSerie.episodesViewed:
            self.currentSerie.episodesViewed.remove(number)
            self.currentSerie.episodesViewedSave()
    
    
    def searchChanged(self, textSearch):
        if self.currentSerie.serie is None:
            return
        serie = self.currentSerie.serie
        episodes = serie['episodes']
        textSearch = unicode(self.searchBar.text())
        self.searchThread.changeText(textSearch, episodes)
    
    
    def searchFinished(self, listEpisodes):
        if self.searchBar.text() == '':
            self.refreshScreen()
        else:
            self.showEpisode(listEpisodes)
    
    
    # ===============
    #  Episode view
    # ===============
    def showEpisode(self, episodes):
        self.clearSelectionInfos()
        self.episodesLoader.newQuery()
        self.episodes.clear()
        self.map = {}
        serieLocalID = self.currentSerieId()
        serieName = Config.series[serieLocalID][0]
        nbRows = int(math.ceil(len(episodes) / float(self.episodes.nbColumn)))
        self.episodes.setRowCount(nbRows)
        imgDir = 'img/' + serieName
        for i, e in enumerate(episodes):
            (x, y) = (i // self.episodes.nbColumn, i % self.episodes.nbColumn)
            imgPath = '%s/%s.jpg' % (imgDir, e['number'])
            titleStr = '<b>%s</b><br/>%s' % (e['number'], e['title'])
            self.map[x, y] = e
            infos = 0
            if e['path'] is not None:
                infos = 1
                if e['number'] not in self.currentSerie.episodesViewed:
                    infos = 2
            
            self.episodesLoader.addEpisode(x, y, titleStr, infos, imgPath)
        self.episodesLoader.start()
        self.refreshCount()
    
    
    def refreshCount(self):
        allDl = {e['number'] for e in self.map.itervalues() if e['path']}
        nbShow = len(self.map)
        nbNew = len(allDl - set(self.currentSerie.episodesViewed))
        if nbShow > 1:
            count = u'%d épisodes affichés' % nbShow
        else:
            count = u'%d épisode affiché' % nbShow
        if nbNew == 1:
            count += ' dont un nouveau'
        elif nbNew > 1:
            count += ' dont %d nouveaux' % nbNew
        self.nbEpisodes.setText(count)
    
    
    def episodeLoaded(self, x, y, title, infos, image = None):
        item = VideoItem(title)
        item.setInfos(infos)
        if image is not None:
            item.setImage(image)
        self.episodes.setCellWidget(x, y, item)
    
    
    def refreshScreen(self):
        if self.currentSerie.serie is None:
            return
        
        serieLocalID = self.currentSerieId()
        episodes = self.currentSerie.serie['episodes']
        filterSeason = self.selectSeason.currentIndex()
        isFilterDL = self.filterDL.isChecked()
        isFilterNew = self.filterNew.isChecked()
        
        listEpisodes = []
        for e in episodes:
            if (filterSeason == 0 or filterSeason == e['season']) \
            and (not isFilterDL or e['path'] is not None) \
            and (not isFilterNew or e['number'] not in self.currentSerie.episodesViewed):
                listEpisodes.append(e)
        
        self.showEpisode(listEpisodes)
    
    
    def serieChanged(self, serieLocalID = None, init = False):
        if not isinstance(serieLocalID, int):
            serieLocalID = self.currentSerieId()
        
        self.currentSerie = Serie(Config.series[serieLocalID])
        self.loadSerie(serieLocalID)
        
        self.selectSeason.clear()
        self.selectSeason.addItem('Toutes les saisons')
        
        # Show infos about the serie
        if 'serieInfos' in self.currentSerie.serie:
            imgPath = 'banners/%s.jpg' % Config.series[serieLocalID][0]
            image = QtGui.QPixmap(imgPath)
            self.imageSerie.setPixmap(image)
            
            serieInfos = self.currentSerie.serie['serieInfos']
            desc = serieInfos['desc'].replace("\n", '<br/>')
            firstAired = serieInfos['firstAired']
            self.description.setText('%s<hr/>%s' % (desc, firstAired))
            
            self.selectSeason.blockSignals(True)
            episodes = self.currentSerie.serie['episodes']
            nbSeasons = max([e['season'] for e in episodes])
            listSeasons = ['Saison %d' % (x + 1) for x in xrange(nbSeasons)]
            self.selectSeason.addItems(listSeasons)
            self.selectSeason.setCurrentIndex(0)
            self.selectSeason.blockSignals(False)
        
        if not init:
            self.refreshScreen()
    
    
    def serieLoaded(self, serieLocalID):
        self.status.showMessage('')
        if self.currentSerieId() == serieLocalID:
            self.serieChanged()
    
    
    def loadSerie(self, serieLocalID):
        try:
            self.currentSerie.loadSerie()
        except ValueError:
            self.refreshSeries.addSerie(serieLocalID)



app = QtGui.QApplication(sys.argv)
window = Main()
window.show()
sys.exit(app.exec_())