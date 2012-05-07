#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import math
import os.path
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from lib import *


class Main(QtGui.QMainWindow):
    currentSerie = None
    
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
        
        self.player = Player(self)
    
    
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
        
        self.checkSerieUpdate = CheckSerieUpdate()
        self.checkSerieUpdate.updateRequired.connect(self.refreshSeries.addSerie)
        self.checkSerieUpdate.start()
    
    
    def currentSerieId(self):
        return self.selectSerie.currentIndex()
    
    
    # =========================
    #  Window Manager
    # =========================
    def createWindow(self):
        self.createMenu()
        
        self.setStyleSheet('QScrollArea { border:none; }')
        
        # StatusBar
        self.status = self.statusBar()
        self.nbEpisodes = QtGui.QLabel()
        self.status.addPermanentWidget(self.nbEpisodes)
        
        # HEADER
        self.imageSerie = QtGui.QLabel()
        self.imageSerie.setFixedSize(758, 140)
        self.imageSerie.setAlignment(Qt.AlignTop)
        
        self.selectSerie = QtGui.QComboBox()
        self.reloadSelectSerie()
        self.selectSerie.currentIndexChanged.connect(self.serieChanged)
        
        self.btnPlay = QtGui.QPushButton(QtGui.QIcon('art/play.png'), '')
        self.btnPlay.setFlat(True)
        self.btnPlay.setToolTip(u"Jouer le premier épisode non vu")
        self.btnPlay.clicked.connect(self.playFirstEpisode)
        
        layoutSerie = QtGui.QHBoxLayout()
        layoutSerie.addWidget(self.selectSerie, 2)
        layoutSerie.addWidget(self.btnPlay)
        
        self.description = QtGui.QLabel()
        self.description.setWordWrap(True)
        self.description.setAlignment(Qt.AlignTop)
        self.description.setScaledContents(True)
        self.description.setStyleSheet('padding:2px')
        
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.description)
        scrollArea.setMinimumWidth(350)
        scrollArea.setFixedHeight(120)
        
        infos = QtGui.QVBoxLayout()
        infos.addLayout(layoutSerie)
        infos.addWidget(scrollArea)
        
        header = QtGui.QHBoxLayout()
        header.addLayout(infos)
        header.addWidget(self.imageSerie)
        
        # FILTER
        self.searchBar = QtGui.QLineEdit()
        self.searchBar.textChanged.connect(self.searchChanged)
        
        self.selectSeason = QtGui.QComboBox()
        self.selectSeason.currentIndexChanged.connect(self.refreshScreen)
        
        self.filter = FilterMenu()
        self.filter.filterChanged.connect(self.refreshScreen)
        
        filterBar = QtGui.QHBoxLayout()
        filterBar.addWidget(self.searchBar)
        filterBar.addWidget(self.selectSeason)
        filterBar.addWidget(self.filter)
        
        # BODY
        self.episodes = EpisodesViewer()
        self.episodes.refreshEpisodes.connect(self.refreshScreen)
        self.episodes.pressEnter.connect(self.episodesDblClicked)
        self.episodes.markedAsView.connect(self.viewSelectEpisodeMenu)
        self.episodes.markedAsNotView.connect(self.notViewSelectEpisodeMenu)
        self.episodes.doubleClicked.connect(self.episodesDblClicked)
        self.episodes.playClicked.connect(self.playClicked)
        self.episodes.currentCellChanged.connect(self.episodeChanged)
        body = QtGui.QHBoxLayout()
        body.addWidget(self.episodes)
        
        # FOOTER
        self.selectionTitle = QtGui.QLabel()
        self.selectionTitle.setAlignment(Qt.AlignTop)
        self.selectionDescription = QtGui.QLabel()
        self.selectionDescription.setWordWrap(True)
        self.selectionDescription.setAlignment(Qt.AlignTop)
        
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.selectionDescription)
        
        footerLayout = QtGui.QVBoxLayout()
        footerLayout.addWidget(self.selectionTitle)
        footerLayout.addWidget(scrollArea)
        self.footer = QtGui.QWidget()
        self.footer.setFixedHeight(130)
        self.footer.setLayout(footerLayout)
        
        window = QtGui.QVBoxLayout()
        window.addLayout(header)
        window.addLayout(filterBar)
        window.addLayout(body)
        window.addWidget(self.footer)
        
        win = QtGui.QWidget()
        win.setLayout(window)
        self.setCentralWidget(win)
        
        # Shortcut
        shortSearch = QtGui.QShortcut('Ctrl+F', self)
        shortSearch.activated.connect(self.searchBar.setFocus)
    
    
    def playClicked(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            coord = item.row(), item.column()
            if coord in self.map:
                self.playIntegratedPlayer(coord, self.map[coord])
    
    
    def createMenu(self):
        self.menubar = self.menuBar()
        
        ## MENU SERIES
        seriesMenu = self.menubar.addMenu('S\xE9ries')
        
        addSerie = seriesMenu.addAction(u'Nouvelle série', self.openAddSerie)
        addSerie.setIcon(QtGui.QIcon('art/add.png'))
        addSerie.setShortcut('Ctrl+N')
        
        edit = seriesMenu.addAction(QtGui.QIcon('art/edit.png'),
                                    u'Editer les séries', self.openEditSerie)
        edit.setShortcut('Ctrl+E')
        
        refresh = seriesMenu.addAction(u'Mettre à jour cette série')
        refresh.triggered.connect(self.updateSerieMenu)
        refresh.setShortcut('Ctrl+U')
        
        seriesMenu.addAction(u'Mettre à jour les séries',
                             self.updateAllSeriesMenu)
        
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
        
        episodesMenu.addAction(QtGui.QIcon('art/uncheck.png'),
                               u'Marquer comme non vue',
                               self.notViewSelectEpisodeMenu)
        
        episodesMenu.addAction(u'Marquer la série comme vue',
                               self.allEpisodeView)
        
        ## MENU AIDE
        helpMenu = self.menubar.addMenu('Series Watcher')
        helpMenu.addAction(QtGui.QIcon('art/options.png'),
                           'Options', self.openOptions)
        helpMenu.addAction(QtGui.QIcon('art/help.png'),
                           'A propos', self.openAbout)
    
    
    def clearSelectionInfos(self):
        self.selectionTitle.setText("")
        self.selectionDescription.setText("")
        self.footer.hide()
    
    
    # =================
    #  Config Manager
    # =================
    def setup(self):
        if not os.path.isdir('database'):
            os.mkdir('database')
        if not os.path.isdir('database/banners'):
            os.mkdir('database/banners')
        if not os.path.isdir('database/img'):
            os.mkdir('database/img')
    
    
    # =================
    #  Slots
    # =================
    def playFirstEpisode(self):
        episodes = {i:e for i, e in self.map.iteritems() if e['infos'] == 2}
        firstNewEpisode = []
        pos = None
        minSeason = minEpisode = 0
        for i, e in episodes.iteritems():
            season, episode = e['season'], e['episode']
            if (minSeason > season) \
             or (minSeason == season and minEpisode > episode) \
             or (minSeason == 0 and minEpisode == 0):
                pos, firstNewEpisode = i, e
                minSeason, minEpisode = season, episode
        
        if firstNewEpisode:
            self.playIntegratedPlayer(pos, firstNewEpisode)
    
    
    def allEpisodeView(self):
        episodesViewed = set()
        for number in self.currentSerie.downloadedEpisode.iterkeys():
            episodesViewed.add(number)
        self.currentSerie.episodesViewed = episodesViewed
        self.currentSerie.episodesViewedSave()
        self.refreshScreen()
    
    
    def reloadMenu(self):
        serieLocalID = self.currentSerieId()
        self.currentSerie.loadDownloadedList()
        self.currentSerie.loadEpisodes()
        self.refreshScreen()
    
    
    def serieLoadStarted(self, title):
        self.status.showMessage('Chargement de %s' % title)
    
    
    def openEditSerie(self):
        editSeries = EditSeries(self)
        editSeries.edited.connect(self.seriesEdited)
        editSeries.show()
    
    
    def seriesEdited(self):
        self.reloadSelectSerie()
        self.serieChanged()
    
    
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
            self.selectionTitle.setText('<b>%s</b>' % episode['title'])
            self.selectionDescription.setText(episode['desc'])
        else:
            self.clearSelectionInfos()
    
    
    def serieAdded(self, *serie):
        self.reloadSelectSerie()
        self.selectSerie.setCurrentIndex(len(Config.series) - 1)
    
    
    def reloadSelectSerie(self):
        self.selectSerie.blockSignals(True)
        self.selectSerie.clear()
        for e in Config.series:
            self.selectSerie.addItem(e[1])
        self.selectSerie.blockSignals(False)
    
    
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
        coord = n.row(), n.column()
        if coord in self.map:
            episode = self.map[coord]
            self.playEpisode(coord, episode)
    
    
    def episodeViewed(self, number):
        if number not in self.currentSerie.episodesViewed:
            self.currentSerie.episodesViewed.add(number)
            self.currentSerie.episodesViewedSave()
    
    
    def episodeNotViewed(self, number):
        if number in self.currentSerie.episodesViewed:
            self.currentSerie.episodesViewed.remove(number)
            self.currentSerie.episodesViewedSave()
    
    
    def searchChanged(self, textSearch):
        if self.currentSerie:
            episodes = self.currentSerie.episodes
            textSearch = unicode(self.searchBar.text())
            self.searchThread.changeText(textSearch, episodes)
    
    
    def searchFinished(self, listEpisodes):
        if self.searchBar.text() == '':
            self.refreshScreen()
        else:
            self.showEpisode(listEpisodes)
    
    
    # ===============
    #  Episode play
    # ===============
    def playEpisode(self, pos, episode):
        command = Config.config['command_open']
        if episode['path']:
            path = os.path.normpath(episode['path'])
            player = int(Config.config['player'])
            if player == 1:
                desktop.open(path)
            elif player == 2:
                self.playIntegratedPlayer(pos, episode)
            elif player == 3:
                if command is None:
                    desktop.open(path)
                else:
                    self.commandOpen.startDetached(command, [path])
            else:
                desktop.open(path)
            
            # Change the title
            self.episodes.cellWidget(*pos).setInfos(1)
            # Add the episode in the already view list
            self.episodeViewed(episode['number'])
            self.refreshCount()
    
    
    def playIntegratedPlayer(self, pos, episode):
        if episode['path']:
            self.episodes.cellWidget(*pos).setInfos(1)
            path = os.path.normpath(episode['path'])
            serieName = self.currentSerie.name
            imgPath = 'database/img/%s/%s.jpg' % (serieName, episode['number'])
            title = '<b>%s</b> %s' % (episode['number'], episode['title'])
            self.player.addToPlayList(title, path, imgPath)
            self.episodeViewed(episode['number'])
            self.refreshCount()
            if not self.player.isVisible():
                self.player.show()
            self.player.tryToPlay()
    
    
    # ===============
    #  Episode view
    # ===============
    def showEpisode(self, episodes):
        self.clearSelectionInfos()
        self.episodesLoader.newQuery()
        self.episodes.clear()
        self.map = {}
        serieName = self.currentSerie.name
        nbRows = int(math.ceil(len(episodes) / float(self.episodes.nbColumn)))
        self.episodes.setRowCount(nbRows)
        imgDir = 'database/img/%s/%s.jpg' % (serieName, '%s')
        nbColumn = self.episodes.nbColumn
        for i, e in enumerate(episodes):
            (x, y) = (i // nbColumn, i % nbColumn)
            imgPath = imgDir % e['number']
            titleStr = '<b>%s</b><br/>%s' % (e['number'], e['title'])
            self.map[x, y] = e
            self.episodesLoader.addEpisode(x, y, titleStr, e['infos'], imgPath)
        self.episodesLoader.start()
        self.refreshCount()
    
    
    def refreshCount(self):
        nbDL = self.currentSerie['nbEpisodeDL']
        allDl = {e['number'] for e in self.currentSerie.episodes if e['path']}
        nbNew = len(allDl - set(self.currentSerie.episodesViewed))
        self.filter.setCounters(self.currentSerie['nbEpisodeTotal'],
                               self.currentSerie['nbEpisodeNotDL'], nbDL, nbNew)
        
        percentageDL = (nbDL / float(self.currentSerie['nbEpisodeTotal'])) * 100
        percentageView = ((nbDL - nbNew) /\
            float(self.currentSerie['nbEpisodeTotal'])) * 100
        
        c = u'Série vue à %d %% | %d %% de la série téléchargé' \
                % (percentageView, percentageDL)
        self.nbEpisodes.setText(c)
        
        if nbNew > 0:
            self.btnPlay.setEnabled(True)
        else:
            self.btnPlay.setEnabled(False)    
    
    
    def episodeLoaded(self, episode):
        x, y, title, infos, image = episode
        item = VideoItem(title)
        item.setInfos(infos)
        item.setImage(image)
        self.episodes.setCellWidget(x, y, item)
    
    
    def refreshScreen(self):
        if self.currentSerie:
            filterSeason = self.selectSeason.currentIndex()
            filterID = self.filter.getFilterID()
            listEpisodes = []
            
            for e in self.currentSerie.episodes:
                if filterSeason == 0 or filterSeason == e['season']:
                    if (filterID == 0 and e['infos'] >= 1) \
                      or (filterID == 1 and e['infos'] == 2) \
                      or (filterID == 2 and e['infos'] == 0) or filterID == 3:
                        listEpisodes.append(e)
            
            self.showEpisode(listEpisodes)
    
    
    def serieChanged(self, serieLocalID=None, init=False):
        if not isinstance(serieLocalID, int):
            serieLocalID = self.currentSerieId()
        
        self.currentSerie = Serie(Config.series[serieLocalID])
        self.loadSerie(serieLocalID)
        
        self.selectSeason.blockSignals(True)
        self.selectSeason.clear()
        self.selectSeason.addItem('Toutes les saisons')
        
        # Show infos about the serie
        if self.currentSerie.infos:
            image = QtGui.QPixmap(self.currentSerie['bannerPath'])
            self.imageSerie.setPixmap(image)
            desc = self.currentSerie['desc'].replace("\n", '<br/>')
            firstAired = self.currentSerie['firstAired']
            firstAired = datetime.strptime(firstAired, '%Y-%m-%d')\
                                          .strftime('%d/%m/%Y')
            self.description.setText(u'%s<hr/>Date de création : %s' \
                                                    % (desc, firstAired))
            
            nbSeasons = self.currentSerie['nbSeason']
            listSeasons = ['Saison %d' % x for x in xrange(1, nbSeasons + 1)]
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