#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import math
import os.path
import random
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox, QIcon
from lib import *
from lib.const import *

class Main(QtGui.QMainWindow):
    currentSerie = None
    currentSerieID = -1
    
    def __init__(self):
        super(Main, self).__init__()
        self.setWindowTitle('Series Watcher %s' % VERSION)
        self.setMinimumSize(820, 600)
        self.setWindowIcon(QIcon('art/film.png'))
        
        self.setup()
        Config.loadConfig()
        
        if 'window_size' in Config.config:
            w, h = Config.config['window_size'].split('x')
            self.resize(int(w), int(h))
        
        if int(Config.config['debug']):
            Debug.setEnabled(True)
            Debug.add(Debug.INFO, u'Debug activé')
        
        self.createWindow()
        self.startTheads()
        if Config.series:
            self.serieChanged(0)
        else:
            self.openAddSerie()
        
        # Load the player
        try:
            self.player = Player(self)
        except:
            self.player = None
    
    
    def startTheads(self):
        self.commandOpen = QtCore.QProcess()
        
        self.episodesLoader = EpisodesLoaderThread(self)
        self.episodesLoader.episodeLoaded.connect(self.episodeLoaded)
        
        self.searchThread = SearchThread(self)
        self.searchThread.searchFinished.connect(self.searchFinished)
        self.searchThread.start()
        
        self.refreshSeries = RefreshSeriesThread(self)
        self.refreshSeries.serieUpdateStatus.connect(self.serieUpdateStatus)
        self.refreshSeries.serieUpdated.connect(self.serieUpdated)
        self.refreshSeries.start()
        
        self.checkSerieUpdate = CheckSerieUpdate(self)
        self.checkSerieUpdate.updateRequired.connect(self.refreshSeries.addSerie)
        self.checkSerieUpdate.start()
        
        self.loaderThread = LoaderThread(self)
        self.loaderThread.serieLoaded.connect(self.serieLoaded)
        self.loaderThread.start()
    
    
    def currentSerieId(self):
        return self.selectSerie.currentIndex()
    
    
    # =========================
    #  Window Manager
    # =========================
    def createWindow(self):
        self.createMenu()
        
        self.setStyleSheet('QScrollArea { border:none; }')
        
        # Status Bar
        self.status = self.statusBar()
        self.nbEpisodes = QtGui.QLabel()
        self.status.addPermanentWidget(self.nbEpisodes)
        
        # Header
        self.imageSerie = QtGui.QLabel()
        self.imageSerie.setFixedHeight(140)
        self.imageSerie.setMaximumWidth(758)
        self.imageSerie.setAlignment(Qt.AlignTop)
        
        self.selectSerie = QtGui.QComboBox()
        self.reloadSelectSerie()
        self.selectSerie.currentIndexChanged.connect(self.serieChanged)
        
        self.btnPlay = QtGui.QPushButton(QtGui.QIcon('art/play.png'), '')
        self.btnPlay.setFlat(True)
        self.btnPlay.setToolTip(u"Jouer le premier épisode disponible non vu")
        self.btnPlay.clicked.connect(self.playFirstEpisode)
        
        btnRand = QtGui.QPushButton(QtGui.QIcon('art/random.png'), '')
        btnRand.setFlat(True)
        btnRand.setToolTip(u"Jouer un épisode au hasard")
        btnRand.clicked.connect(self.playRandomEpisode)
        
        layoutSerie = QtGui.QHBoxLayout()
        layoutSerie.addWidget(self.selectSerie, 2)
        layoutSerie.addWidget(self.btnPlay)
        layoutSerie.addWidget(btnRand)
        
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
        
        # Filters
        self.searchBar = QtGui.QLineEdit()
        self.searchBar.setPlaceholderText('Rechercher...')
        self.searchBar.textChanged.connect(self.searchChanged)
        
        self.selectSeason = QtGui.QComboBox()
        self.selectSeason.currentIndexChanged.connect(self.refreshScreen)
        self.selectSeason.setMinimumContentsLength(18)
        
        self.filter = FilterMenu()
        self.filter.filterChanged.connect(self.refreshScreen)
        
        filterBar = QtGui.QHBoxLayout()
        filterBar.addWidget(self.searchBar)
        filterBar.addWidget(self.selectSeason)
        filterBar.addWidget(self.filter)
        
        # Body
        self.episodes = EpisodesViewer()
        self.episodes.refreshEpisodes.connect(self.refreshScreen)
        self.episodes.pressEnter.connect(self.episodesDblClicked)
        self.episodes.markedAsView.connect(self.viewSelectEpisodeMenu)
        self.episodes.markedAsNotView.connect(self.notViewSelectEpisodeMenu)
        self.episodes.doubleClicked.connect(self.episodesDblClicked)
        self.episodes.playClicked.connect(self.playClicked)
        self.episodes.itemSelectionChanged.connect(self.episodeChanged)
        body = QtGui.QHBoxLayout()
        body.addWidget(self.episodes)
        
        # Footer
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
        
        # Shortcuts
        shortSearch = QtGui.QShortcut('Ctrl+F', self)
        shortSearch.activated.connect(self.searchBar.setFocus)
    
    
    def playClicked(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            coord = item.row(), item.column()
            if coord in self.map:
                self.playIntegratedPlayer(self.map[coord])
                self.markAsView(episode)
    
    
    def createMenu(self):
        self.menubar = self.menuBar()
        
        # Menu "Series"
        seriesMenu = self.menubar.addMenu(u'Séries')
        seriesMenu.addAction(QIcon('art/add.png'), u'Nouvelle série',
                             self.openAddSerie).setShortcut('Ctrl+N')
        seriesMenu.addAction(QIcon('art/edit.png'), u'Editer les séries',
                             self.openEditSerie).setShortcut('Ctrl+E')
        seriesMenu.addAction(u'Mettre à jour cette série',
                             self.updateSerieMenu).setShortcut('Ctrl+U')
        seriesMenu.addAction(u'Mettre à jour les séries',
                             self.updateAllSeriesMenu)
        
        # Menu "Episodes"
        episodesMenu = self.menubar.addMenu('Episodes')
        episodesMenu.addAction(QIcon('art/refresh.png'), u'Recharger',
                               self.reloadMenu).setShortcut('Ctrl+R')
        episodesMenu.addAction(QIcon('art/check.png'), u'Marquer comme vue',
                               self.viewSelectEpisodeMenu).setShortcut('Ctrl+K')
        episodesMenu.addAction(QIcon('art/uncheck.png'), u'Marquer comme non vue',
                               self.notViewSelectEpisodeMenu)
        episodesMenu.addAction(u'Marquer la série comme vue',
                               self.allEpisodeView)
        
        # Menu "Series Watcher"
        SWMenu = self.menubar.addMenu('Series Watcher')
        SWMenu.addAction(QIcon('art/options.png'), 'Options', self.openOptions)
        SWMenu.addAction(QIcon('art/help.png'), 'A propos', self.openAbout)
        if Debug.isEnabled():
            SWMenu.addSeparator()
            SWMenu.addAction('Debug', self.openDebug)
    
    
    def clearSelectionInfos(self):
        self.selectionTitle.setText("")
        self.selectionDescription.setText("")
        self.footer.hide()
    
    
    # =================
    #  Config Manager
    # =================
    def setup(self):
        if not os.path.isdir(USER):
            os.mkdir(USER)
        if not os.path.isdir(SERIES):
            os.mkdir(SERIES)
        if not os.path.isdir(SERIES_IMG):
            os.mkdir(SERIES_IMG)
        if not os.path.isdir(SERIES_BANNERS):
            os.mkdir(SERIES_BANNERS)
        if not os.path.isdir(SERIES_VIEW):
            os.mkdir(SERIES_VIEW)
        if not os.path.isdir(SERIES_DB):
            os.mkdir(SERIES_DB)
    
    
    # =================
    #  Slots
    # =================
    def playFirstEpisode(self):
        episodes = {i:e for i, e in self.map.iteritems() if e['status'] == 2}
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
            self.playEpisode(firstNewEpisode)
            return True
        return False
    
    
    def playRandomEpisode(self):
        episodes = [e for i, e in self.map.iteritems() if e['status'] == 1]
        if episodes:
            self.playEpisode(random.choice(episodes))
            self.player.btnRandom.setChecked(True)
            return True
        return False
    
    
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
    
    
    def serieUpdateStatus(self, serieLocalID, title, status):
        messages = {
            201: u'%s : Téléchargement des informations sur la série...',
            202: u'%s : Téléchargement des informations sur les épisodes...',
            203: u'%s : Téléchargement des miniatures'
        }
        message = messages[status] % title
        self.status.showMessage(message)
        if self.currentSerieId() == serieLocalID:
            self.loaderThread.forceReload()
    
    
    def openEditSerie(self):
        editSeries = EditSeries(self)
        editSeries.edited.connect(self.seriesEdited)
        editSeries.show()
    
    
    def seriesEdited(self):
        self.loaderThread.forceReload()
        self.reloadSelectSerie()
    
    
    def openAbout(self):
        about = About(self)
        about.show()
    
    
    def openOptions(self):
        options = Options(self)
        options.show()
    
    
    def openDebug(self):
        debug = DebugWindow(self)
        debug.show()
    
    
    def openAddSerie(self):
        addSerie = AddSerie(self)
        addSerie.serieAdded.connect(self.serieAdded)
        addSerie.show()
    
    
    def updateSerieMenu(self):
        self.refreshSeries.addSerie(self.currentSerieId())
    
    
    def updateAllSeriesMenu(self):
        for e in range(len(Config.series)):
            self.refreshSeries.addSerie(e)
    
    
    def episodeChanged(self):
        indexes = self.episodes.selectedIndexes()
        if len(indexes) == 1:
            r, c = indexes[0].row(), indexes[0].column()
            if (r, c) in self.map:
                episode = self.map[r, c]
                self.footer.show()
                
                title = '<b>%s</b>' % episode['title']
                if episode['firstAired']:
                    firstAired = datetime.strftime(episode['firstAired'],
                                                   '%d/%m/%Y')
                    title += '  -  %s' % firstAired
                
                self.selectionTitle.setText(title)
                self.selectionDescription.setText(episode['desc'])
            else:
                self.clearSelectionInfos()
        else:
            self.clearSelectionInfos()
    
    
    def serieAdded(self, *serie):
        nbSeries = len(Config.series)
        self.reloadSelectSerie()
        self.selectSerie.setCurrentIndex(nbSeries - 1)
        if nbSeries == 1:
            self.loaderThread.forceReload()
    
    
    def reloadSelectSerie(self):
        self.selectSerie.blockSignals(True)
        self.selectSerie.clear()
        for e in Config.series:
            self.selectSerie.addItem(e[1])
        self.selectSerie.blockSignals(False)
    
    
    def closeEvent(self, e):
        if not self.isMaximized():
            Config.config['window_size'] = '%dx%d' % (self.width(), self.height())
            Config.save()
        QtGui.QMainWindow.closeEvent(self, e)
    
    
    def viewSelectEpisodeMenu(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = coord = item.row(), item.column()
            video = self.episodes.cellWidget(r, c)
            if video is not None:
                number = self.map[coord]['number']
                if number in self.currentSerie.downloadedEpisode:
                    video.setStatus(1)
                    self.currentSerie.episodesViewed.add(number)
        self.currentSerie.episodesViewedSave()
        self.refreshCount()
    
    
    def notViewSelectEpisodeMenu(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = coord = item.row(), item.column()
            video = self.episodes.cellWidget(r, c)
            if video is not None:
                number = self.map[coord]['number']
                if number in self.currentSerie.episodesViewed:
                    video.setStatus(2)
                    self.currentSerie.episodesViewed.remove(number)
        self.currentSerie.episodesViewedSave()
        self.refreshCount()
    
    
    def episodesDblClicked(self, n):
        coord = n.row(), n.column()
        if coord in self.map:
            episode = self.map[coord]
            self.playEpisode(episode)
    
    
    def episodeViewed(self, number):
        if number not in self.currentSerie.episodesViewed:
            self.currentSerie.episodesViewed.add(number)
            self.currentSerie.episodesViewedSave()
    
    
    def searchChanged(self, textSearch):
        if self.currentSerie:
            textSearch = unicode(self.searchBar.text())
            self.searchThread.changeText(textSearch)
    
    
    def searchFinished(self, listEpisodes):
        if self.searchBar.text() == '':
            self.refreshScreen()
        else:
            self.showEpisode(listEpisodes)
    
    
    # ===============
    #  Episode play
    # ===============
    def markAsView(self, episode):
        for i, e in self.map.iteritems():
            if e == episode:
                try:
                    self.episodes.cellWidget(*i).setStatus(1)
                except AttributeError:
                    pass
                self.episodeViewed(episode['number'])
                return True
        return False
    
    
    def playEpisode(self, episode):
        command = Config.config['command_open']
        if episode['path']:
            path = os.path.normpath(episode['path'])
            player = int(Config.config['player'])
            if player == 1:
                desktop.open(path)
            elif player == 2:
                self.playIntegratedPlayer(episode)
            elif player == 3:
                if command is None:
                    desktop.open(path)
                else:
                    self.commandOpen.startDetached(command, [path])
            else:
                desktop.open(path)
            
            self.markAsView(episode)
            self.refreshCount()
    
    
    def playIntegratedPlayer(self, episode):
        if episode['path']:
            if not self.player or not self.player.VLCLoaded:
                title = 'Erreur lors du chargement de VLC'
                message = u"Le lecteur intégré ne peut pas être démarrer car" \
                          + u" la bibliothèque VLC ne s'est pas chargée" \
                          + u" correctement."
                QMessageBox.critical(self, title, message)
                return
            
            path = os.path.normpath(episode['path'])
            serieName = self.currentSerie.name
            imgPath = '%s%s/%s.jpg' % (SERIES_IMG, serieName, episode['number'])
            title = episode['title']
            self.player.addToPlayList(episode['number'], title, path, imgPath)
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
        imgDir = '%s%s/%%s.jpg' % (SERIES_IMG, serieName)
        nbColumn = self.episodes.nbColumn
        count = 0
        for i, e in enumerate(episodes):
            (x, y) = (i // nbColumn, i % nbColumn)
            imgPath = imgDir % e['number']
            title = u'<b>{0}</b><br/>{1}'.format(e['number'], e['title'])
            self.map[x, y] = e
            self.episodesLoader.addEpisode(x, y, title, e['status'], imgPath)
            count += 1
        self.episodesLoader.start()
        self.refreshCount()
        nbRows = int(math.ceil(count / float(self.episodes.nbColumn)))
        self.episodes.setRowCount(nbRows)
    
    
    def refreshCount(self):
        nbDL = self.currentSerie['nbEpisodeDL']
        allDl = {e['number'] for e in self.currentSerie.episodes \
                                if e['path'] and e['season'] > 0}
        nbNew = len(allDl - set(self.currentSerie.episodesViewed))
        self.filter.setCounters(self.currentSerie['nbEpisodeTotal'],
                               self.currentSerie['nbEpisodeNotDL'], nbDL, nbNew)
        
        if self.currentSerie['nbEpisodeTotal'] > 0:
            percentageDL = (nbDL / float(self.currentSerie['nbEpisodeTotal'])) * 100
            percentageView = ((nbDL - nbNew) /\
                float(self.currentSerie['nbEpisodeTotal'])) * 100
        else:
            percentageDL = percentageView = 0
        
        c = u"Série vue à %d %% | %d %% d'épisodes disponibles" \
                % (percentageView, percentageDL)
        self.nbEpisodes.setText(c)
        
        if nbNew > 0:
            self.btnPlay.setEnabled(True)
        else:
            self.btnPlay.setEnabled(False)
    
    
    def episodeLoaded(self, episode):
        x, y, title, status, image = episode
        item = VideoItem(title)
        item.setStatus(status)
        item.setImage(image)
        self.episodes.setCellWidget(x, y, item)
    
    
    def episodesGenerator(self):
        filterSeason = self.selectSeason.currentIndex() - 1
        filterID = self.filter.getFilterID()
        for e in self.currentSerie.episodes:
            status, season = e['status'], e['season']
            if (filterSeason == -1 or filterSeason == season) \
                and ((filterID == 0 and status in (1, 2)) \
                  or (filterID == 1 and status == 2) \
                  or (filterID == 2 and status == 0) or filterID == 3) \
                and (season != 0 or filterSeason == 0):
                    yield e
    
    
    def refreshScreen(self):
        self.searchBar.clear()
        if self.currentSerie:
            self.showEpisode(self.episodesGenerator())
    
    
    def clearSeries(self):
        self.map = {}
        
        self.selectSeason.blockSignals(True)
        self.selectSeason.clear()
        self.selectSeason.addItem('Toutes les saisons')
        self.selectSeason.addItem('Bonus')
        self.selectSeason.blockSignals(False)
        
        self.btnPlay.setEnabled(False)
        self.description.setText(u"La série n'est pas encore chargée.")
        self.imageSerie.clear()
        self.episodes.clear()
        self.nbEpisodes.clear()
        
        self.filter.setCounters(0, 0, 0, 0)
    
    
    def serieLoaded(self, serie):
        self.currentSerie = serie
        serieLocalID = self.currentSerieId()
        try:
            self.currentSerie.loadSerie()
        except ValueError:
            self.refreshSeries.addSerie(serieLocalID)
            self.clearSeries()
            return
        
        self.selectSeason.blockSignals(True)
        self.selectSeason.clear()
        self.selectSeason.addItem('Toutes les saisons')
        self.selectSeason.addItem('Bonus')
        
        # Show infos about the serie
        if self.currentSerie.infos:
            image = QtGui.QPixmap(self.currentSerie['bannerPath'])
            self.imageSerie.setPixmap(image)
            desc = self.currentSerie['desc'].replace("\n", '<br/>')
            firstAired = self.currentSerie['firstAired'].strftime('%d/%m/%Y')
            self.description.setText(u'%s<hr/>Date de création : %s' \
                                                    % (desc, firstAired))
            nbSeasons = self.currentSerie['nbSeason']
            listSeasons = ['Saison %d' % x for x in range(1, nbSeasons + 1)]
            self.selectSeason.addItems(listSeasons)
            self.selectSeason.setCurrentIndex(0)
        
        self.selectSeason.blockSignals(False)
        self.refreshScreen()
    
    
    def serieChanged(self, serieLocalID=None):
        if not isinstance(serieLocalID, int):
            serieLocalID = self.currentSerieId()
        self.currentSerieID = serieLocalID
    
    
    def serieUpdated(self, serieLocalID):
        self.status.showMessage('')
        if self.currentSerieId() == serieLocalID:
            self.loaderThread.forceReload()



app = QtGui.QApplication(sys.argv)
window = Main()
window.show()
sys.exit(app.exec_())