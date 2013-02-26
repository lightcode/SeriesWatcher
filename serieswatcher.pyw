#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import math
import os.path
import random
import sys
import time
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox, QIcon

USER_DIR_FOUND = False
if os.path.isdir('user'):
    USER_DIR_FOUND = True

from lib import desktop
from lib.about import About
from lib.addserie import AddSerie
from lib.config import Config
from lib.const import *
from lib.debug import Debug, DebugWindow
from lib.editseries import EditSeries
from lib.models import Serie, Episode
from lib.options import Options
from lib.player import Player
from lib.threads import *
from lib.widgets import EpisodesViewer, VideoItem, FilterMenu


class Main(QtGui.QMainWindow):
    currentSerie = None
    
    def __init__(self):
        super(Main, self).__init__()
        self.setWindowTitle('Series Watcher %s' % TEXT_VERSION)
        self.setMinimumSize(820, 600)
        self.setWindowIcon(QIcon('art/sw.ico'))
        
        self.setup()
        Config.loadConfig()
        
        # Get the last window size
        if 'window_size' in Config.config:
            w, h = Config.config['window_size'].split('x')
            self.resize(int(w), int(h))
        
        # Enable debug
        if int(Config.config['debug']):
            Debug.setEnabled(True)
            Debug.add(Debug.INFO, u'Debug activé')
        
        # Load the main windows
        QtCore.QTimer.singleShot(250, self.startTheads1)
        self.createWindow()
        QtCore.QTimer.singleShot(1000, self.startTheads2)
        if not Serie.getSeries():
            self.openAddSerie()
        
        # Load the player
        try:
            self.player = Player(self)
        except:
            self.player = None
    
    
    def startTheads1(self):
        """Start the first group of threads."""
        self.commandOpen = QtCore.QProcess()
        
        self.refreshSeries = RefreshSeriesThread(self)
        self.refreshSeries.serieUpdateStatus.connect(self.serieUpdateStatus)
        self.refreshSeries.serieUpdated.connect(self.serieUpdated)
        self.refreshSeries.start()
        
        self.episodesLoader = EpisodesLoaderThread(self)
        self.episodesLoader.episodeLoaded.connect(self.episodeLoaded)
        
        self.loaderThread = LoaderThread(self)
        self.loaderThread.serieLoaded.connect(self.serieLoaded)
        self.loaderThread.start()
        
        self.searchThread = SearchThread(self)
        self.searchThread.searchFinished.connect(self.searchFinished)
        self.searchThread.start()
    
    
    def startTheads2(self):
        """Start the second group of threads."""
        self.checkSerieUpdate = CheckSerieUpdateThread(self)
        self.checkSerieUpdate.updateRequired.connect(self.refreshSeries.addSerie)
        self.checkSerieUpdate.start()
        
        self.syncDBThead = SyncDBThead(self)
        self.syncDBThead.start()
    
    
    def currentSerieId(self):
        """Return the current serie ID."""
        return self.selectSerie.currentIndex()
    
    
    # =========================
    #  Window Manager
    # =========================
    def createWindow(self):
        """Draw the main window."""
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
        self.episodes.viewStatusChanged.connect(self.viewStatusChanged)
        self.episodes.doubleClicked.connect(self.episodesDblClicked)
        self.episodes.playClicked.connect(self.playClicked)
        self.episodes.itemSelectionChanged.connect(self.refreshFooter)
        self.episodes.favoriteChanged.connect(self.favoriteChanged)
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
        
        self.selectionBtnFavorite = QtGui.QPushButton('')
        self.selectionBtnFavorite.setFixedWidth(160)
        self.selectionBtnFavorite.setFlat(True)
        self.selectionBtnFavorite.setStyleSheet("text-align:left;padding-left:0px")
        self.selectionBtnFavorite.clicked.connect(self.toggleSelectionFavorite)
        self.selectionBtnView = QtGui.QPushButton('')
        self.selectionBtnView.setFlat(True)
        self.selectionBtnView.setStyleSheet("text-align:left;padding-left:0px")
        self.selectionBtnView.clicked.connect(self.toggleSelectionView)
        self.selectionNumberView = QtGui.QLabel('')
        self.selectionLastView = QtGui.QLabel('')
        
        self.selectionIconFavorite = QtGui.QLabel('<img src="art/star.png" />')
        self.selectionIconView = QtGui.QLabel('<img src="art/check.png" />')
        
        episodeBarLayout = QtGui.QGridLayout()
        episodeBarLayout.addWidget(self.selectionIconFavorite, 0, 0)
        episodeBarLayout.addWidget(self.selectionBtnFavorite, 0, 1)
        episodeBarLayout.addWidget(self.selectionIconView, 1, 0)
        episodeBarLayout.addWidget(self.selectionBtnView, 1, 1)
        episodeBarLayout.addWidget(QtGui.QLabel('<img src="art/eye.png" />'), 2, 0)
        episodeBarLayout.addWidget(self.selectionNumberView, 2, 1)
        episodeBarLayout.addWidget(QtGui.QLabel('<img src="art/calendar.png" />'), 3, 0)
        episodeBarLayout.addWidget(self.selectionLastView, 3, 1)
        
        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addWidget(scrollArea)
        bottomLayout.addLayout(episodeBarLayout)
        
        footerLayout = QtGui.QVBoxLayout()
        footerLayout.addWidget(self.selectionTitle)
        footerLayout.addLayout(bottomLayout)
        
        self.footer = QtGui.QWidget()
        self.footer.setFixedHeight(130)
        self.footer.setLayout(footerLayout)
        self.footer.hide()
        
        # Layout
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
        
        QtGui.QShortcut('F', self).activated.connect(self.toggleSelectionFavorite)
        QtGui.QShortcut('V', self).activated.connect(self.toggleSelectionView)
        QtGui.QShortcut('P', self).activated.connect(self.playClicked)
    
    
    def createMenu(self):
        """Add menu bar in the window."""
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
        episodesMenu.addAction(QIcon('art/reload.png'), u'Recharger',
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
            SWMenu.addAction(QIcon('art/bug.png'), 'Debug', self.openDebug)
    
    
    def openUpdateWindow(self):
        """Open a window that ask if the program must update the database."""
        r = QMessageBox.question(self, u'Mise à jour', u"Series Watcher a "
                             u"trouvé une ancienne base de données. "
                             u"Voulez-vous l'importer dans la nouvelle "
                             u"version ?",
                             QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            import lib.upgrader
        elif r == QMessageBox.No:
            with open('user/series/VERSION', 'w+') as f:
                f.write('1.3.0')
    
    
    def setup(self):
        """Some check when the program open."""
        if os.path.isfile(VERSION_FILE):
            with open(VERSION_FILE) as vf:
                if vf.read().strip() != VERSION:
                    self.openUpdateWindow()
        elif USER_DIR_FOUND:
            self.openUpdateWindow()
        else:
            with open('user/series/VERSION', 'w+') as f:
                f.write('1.3.0')
        if not os.path.isdir(USER):
            os.mkdir(USER)
        if not os.path.isdir(SERIES):
            os.mkdir(SERIES)
        if not os.path.isdir(SERIES_IMG):
            os.mkdir(SERIES_IMG)
        if not os.path.isdir(SERIES_BANNERS):
            os.mkdir(SERIES_BANNERS)
    
    
    # =================
    #  Slots
    # =================
    def viewSelectEpisodeMenu(self):
        self.viewStatusChanged(True)
    
    
    def notViewSelectEpisodeMenu(self):
        self.viewStatusChanged(False)
    
    
    def clearSelectionInfos(self):
        self.selectionTitle.setText("")
        self.selectionDescription.setText("")
        self.footer.hide()
    
    
    def playFirstEpisode(self):
        firstNewEpisode = None
        minSeason = minEpisode = 0
        for e in self.map.itervalues():
            if e.status == 2:
                season, episode = e.season, e.episode
                if (minSeason > season) \
                 or (minSeason == season and minEpisode > episode) \
                 or (minSeason == 0 and minEpisode == 0):
                    firstNewEpisode = e
                    minSeason, minEpisode = season, episode
        
        if firstNewEpisode:
            self.playEpisode(firstNewEpisode)
            return True
        return False
    
    
    def playRandomEpisode(self):
        episodesLongTime = []
        otherEpisodes = []
        
        rd = int(Config.config['random_duration'])
        if rd is not None:
            limitDate = datetime.fromtimestamp(time.time() - rd)
        
        # Search if there are long time viewed episode
        for e in self.map.itervalues():
            if e.status in (1, 2):
                if e.lastView is None or e.lastView <= limitDate:
                    episodesLongTime.append(e)
                else:
                    otherEpisodes.append(e)
        
        if episodesLongTime:
            self.playEpisode(random.choice(episodesLongTime))
        elif otherEpisodes:
            self.playEpisode(random.choice(sorted(otherEpisodes, key=lambda o: o.lastView)[:10]))
        else:
            return False
        
        self.player.btnRandom.setChecked(True)
        return True
    
    
    def allEpisodeView(self):
        for e in self.currentSerie.episodes:
            e.setView()
        self.refreshScreen()
    
    
    def reloadMenu(self):
        self.currentSerie.loadSerie()
        self.refreshScreen()
    
    
    def serieUpdateStatus(self, serieLocalID, title, status):
        messages = [
            u'%s : Téléchargement des informations sur la série...',
            u'%s : Téléchargement des informations sur les épisodes...',
            u'%s : Téléchargement des miniatures'
        ]
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
        for i, e in enumerate(Serie.getSeries()):
            self.refreshSeries.addSerie(i)
    
    
    def refreshSelectedEpisodes(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = item.row(), item.column()
            widget = self.episodes.cellWidget(r, c)
            if widget:
                widget.refresh()
    
    
    def getSelectedEpisode(self):
        indexes = self.episodes.selectedIndexes()
        if len(indexes) == 1:
            r, c = indexes[0].row(), indexes[0].column()
            if (r, c) in self.map:
                return self.map[r, c]
        return False
    
    
    def getSelectedEpisodes(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = item.row(), item.column()
            if (r, c) in self.map:
                yield self.map[r, c]
    
    
    def refreshFooter(self):
        episode = self.getSelectedEpisode()
        if episode:
            self.footer.show()
            title = '<b>%s</b>' % episode.title
            if episode.firstAired:
                firstAired = datetime.strftime(episode.firstAired, '%d/%m/%Y')
                title += '  -  %s' % firstAired
            self.selectionTitle.setText(title)
            self.selectionDescription.setText(episode.description)
            if episode.nbView > 1:
                self.selectionNumberView.setText('%d vues' % episode.nbView)
            else:
                self.selectionNumberView.setText('%d vue' % episode.nbView)
            if episode.lastView:
                lastView = datetime.strftime(episode.lastView, '%d/%m/%Y')
            else:
                lastView = 'Jamais vu'
            self.selectionLastView.setText(lastView)
            if episode.favorite:
                self.selectionBtnFavorite.setText('Enlever des favoris')
                self.selectionIconFavorite.setText('<img src="art/star.png" />')
            else:
                self.selectionBtnFavorite.setText('Ajouter aux favoris')
                self.selectionIconFavorite.setText('<img src="art/unstar.png" />')
            if episode.nbView == 0:
                self.selectionBtnView.setText('Marquer comme vu')
                self.selectionIconView.setText('<img src="art/uncheck.png" />')
            else:
                self.selectionBtnView.setText('Marquer comme non vu')
                self.selectionIconView.setText('<img src="art/check.png" />')
        else:
            self.clearSelectionInfos()
    
    
    def serieAdded(self):
        nbSeries = len(Serie.getSeries())
        self.reloadSelectSerie()
        self.selectSerie.setCurrentIndex(nbSeries)
    
    
    def reloadSelectSerie(self):
        self.selectSerie.blockSignals(True)
        self.selectSerie.clear()
        Serie.deleteSeriesCache()
        for s in Serie.getSeries():
            self.selectSerie.addItem(s.title)
        self.selectSerie.blockSignals(False)
    
    
    def closeEvent(self, e):
        if not self.isMaximized():
            Config.config['window_size'] = '%dx%d' % (self.width(), self.height())
            Config.save()
        QtGui.QMainWindow.closeEvent(self, e)
    

    def favoriteChanged(self, value):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = coord = item.row(), item.column()
            video = self.episodes.cellWidget(r, c)
            if video is not None:
                if value:
                    self.map[coord].setFavorite()
                else:
                    self.map[coord].setUnFavorite()
                video.setFavorite(value)
        self.refreshFooter()
        self.refreshCount()


    def viewStatusChanged(self, value):
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = coord = item.row(), item.column()
            video = self.episodes.cellWidget(r, c)
            if video is not None:
                if value:
                    number = self.map[coord].setView()
                    video.setStatus(1)
                else:
                    number = self.map[coord].setNotView()
                    video.setStatus(2)
        self.refreshFooter()
        self.refreshCount()
    
    
    def episodesDblClicked(self, n):
        coord = (n.row(), n.column())
        if coord in self.map:
            episode = self.map[coord]
            self.playEpisode(episode)
    
    
    def searchChanged(self, textSearch):
        if self.currentSerie:
            textSearch = unicode(self.searchBar.text())
            self.searchThread.changeText(textSearch)
    
    
    def searchFinished(self, listEpisodes):
        if self.searchBar.text() == '':
            self.refreshScreen()
        else:
            self.showEpisode(listEpisodes)
    
    
    # =================
    #  Episode play
    # =================
    def playClicked(self):
        items = self.episodes.selectedIndexes()
        for item in items:
            coord = (item.row(), item.column())
            if coord in self.map:
                episode = self.map[coord]
                self.playIntegratedPlayer(episode)
                self.markAsView(episode)
    
    
    def playEpisode(self, episode):
        command = Config.config['command_open']
        if episode.path:
            path = os.path.normpath(episode.path)
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
        if episode.path:
            if not self.player or not self.player.VLCLoaded:
                title = 'Erreur lors du chargement de VLC'
                QMessageBox.critical(self, title, ERROR_PLAYER_LOAD)
                return
            
            path = os.path.normpath(episode.path)
            self.player.addToPlayList(episode.number, episode.title, path, episode.cover)
            self.refreshCount()
            if not self.player.isVisible():
                self.player.show()
                self.player.tryToPlay()
    
    
    # ====================
    #  Episode properties
    # ====================
    def toggleSelectionFavorite(self):
        nbfav = nbunfav = 0
        for episode in self.getSelectedEpisodes():
            if episode:
                if episode.favorite:
                    nbfav += 1
                else:
                    nbunfav += 1
        
        for episode in self.getSelectedEpisodes():
            if episode:
                if nbfav > nbunfav:
                    episode.setUnFavorite()
                else:
                    episode.setFavorite()
            self.refreshSelectedEpisodes()
            self.refreshFooter()
            self.refreshCount()
    
    
    def toggleSelectionView(self):
        nbview = nbnotview = 0
        for episode in self.getSelectedEpisodes():
            if episode:
                if episode.nbView > 0:
                    nbview += 1
                else:
                    nbnotview += 1
        
        for episode in self.getSelectedEpisodes():
            if episode:
                if nbview > nbnotview:
                    episode.setNotView()
                else:
                    episode.setView()
            self.refreshSelectedEpisodes()
            self.refreshFooter()
            self.refreshCount()
    
    
    def markAsView(self, episode):
        for i, e in self.map.iteritems():
            if e == episode:
                try:
                    self.episodes.cellWidget(*i).setStatus(1)
                except AttributeError:
                    pass
                e.userPlayed()
                self.refreshCount()
                self.refreshFooter()
                return True
        return False
    
    
    def showEpisode(self, episodes):
        self.clearSelectionInfos()
        self.episodesLoader.newQuery()
        self.episodes.clear()
        self.map = {}
        serieUUID = self.currentSerie.uuid
        imgDir = '%s%s/%%s.jpg' % (SERIES_IMG, serieUUID)
        nbColumn = self.episodes.nbColumn
        count = 0
        for i, e in enumerate(episodes):
            (x, y) = (i // nbColumn, i % nbColumn)
            imgPath = imgDir % e.number
            self.map[x, y] = e
            self.episodesLoader.addEpisode(x, y, e, imgPath)
            count += 1
        self.episodesLoader.start()
        self.refreshCount()
        nbRows = int(math.ceil(count / float(self.episodes.nbColumn)))
        self.episodes.setRowCount(nbRows)
    
    
    def refreshCount(self):
        nbAv = self.currentSerie.nbEpisodeAvailable
        nbNotView = self.currentSerie.nbNotView
        self.filter.setCounters(self.currentSerie.nbEpisodeTotal,
                               self.currentSerie.nbEpisodeNotAvailable,
                               nbAv, nbNotView, self.currentSerie.nbFavorites)
        
        if self.currentSerie.nbEpisodeTotal > 0:
            percentageDL = (nbAv / float(self.currentSerie.nbEpisodeTotal)) * 100
            percentageView = (self.currentSerie.nbView / float(self.currentSerie.nbEpisodeTotal)) * 100
        else:
            percentageDL = percentageView = 0
        
        c = u"Série vue à %d %% | %d %% d'épisodes disponibles" \
                % (percentageView, percentageDL)
        self.nbEpisodes.setText(c)
        
        if nbNotView > 0:
            self.btnPlay.setEnabled(True)
        else:
            self.btnPlay.setEnabled(False)
    
    
    def episodeLoaded(self, args):
        (x, y, episode, image) = args
        item = VideoItem(episode)
        item.setImage(image)
        self.episodes.setCellWidget(x, y, item)
    
    
    def episodesGenerator(self):
        filterSeason = self.selectSeason.currentIndex() - 1
        filterID = self.filter.getFilterID()
        for e in self.currentSerie.episodes:
            (status, season) = (e.status, e.season)
            if (filterSeason == -1 or filterSeason == season) \
                and ((filterID == 0 and status in (1, 2)) \
                  or (filterID == 1 and status == 2) \
                  or (filterID == 2 and e.favorite) \
                  or (filterID == 3 and status == 0) or filterID == 4) \
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
        
        self.filter.setCounters(0, 0, 0, 0, 0)
    
    
    def serieLoaded(self, serie):
        self.currentSerie = serie
        self.currentSerie.loadSerie()
        
        if not self.currentSerie.isLoaded():
            self.refreshSeries.addSerie(self.currentSerieId())
            self.clearSeries()
        
        self.selectSeason.blockSignals(True)
        self.selectSeason.clear()
        self.selectSeason.addItem('Toutes les saisons')
        self.selectSeason.addItem('Bonus')
        
        # Show infos about the serie
        image = QtGui.QPixmap(self.currentSerie.bannerPath)
        self.imageSerie.setPixmap(image)
        desc = self.currentSerie.description.replace("\n", '<br/>')
        firstAired = self.currentSerie.firstAired
        if firstAired:
            firstAired = firstAired.strftime('%d/%m/%Y')
            self.description.setText(u'%s<hr/>Date de création : %s' \
                                                    % (desc, firstAired))
        else:
            self.description.setText(desc)
        
        nbSeasons = self.currentSerie.nbSeason
        listSeasons = ['Saison %d' % x for x in range(1, nbSeasons + 1)]
        self.selectSeason.addItems(listSeasons)
        self.selectSeason.setCurrentIndex(0)
        
        self.selectSeason.blockSignals(False)
        self.refreshScreen()
    
    
    def serieUpdated(self, serieLocalID):
        self.status.showMessage('')
        if self.currentSerieId() == serieLocalID:
            self.loaderThread.forceReload()



app = QtGui.QApplication(sys.argv)

locale = QtCore.QLocale.system().name()
translator = QtCore.QTranslator()
if os.path.splitext(sys.argv[0])[1] in ['.py', '.pyw']:
    reptrad = unicode(QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
else:
    reptrad = unicode("translations")
translator.load(QtCore.QString("qt_") + locale, reptrad)
app.installTranslator(translator)

window = Main()
window.show()
sys.exit(app.exec_())