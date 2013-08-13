#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import time
import random
import shutil
import os.path
from datetime import datetime
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox, QIcon
from .const import USER

USER_DIR_FOUND = False
if os.path.isdir(USER):
    USER_DIR_FOUND = True

import desktop
from .about import About
from .addserie import AddSerie
from .config import Config
from .const import *
from .editseries import EditSeries
from .models import Serie, databaseConnect
from .options import Options
from .player import Player
from .threads import *
from .widgets.videoitem import VideoItem
from .widgets.filtermenu import FilterMenu
from .widgets.episodesviewer import EpisodesViewer
from .worker import Runnable
from .tasks.checkserieupdate import CheckSerieUpdateTask


class Main(QtGui.QMainWindow):
    """Class that handle the main thread and create the layout
    of the main window.
    """
    
    def __init__(self):
        self.currentSerie = None
        self.map = {}
        self.threadPool = QtCore.QThreadPool()
        
        super(Main, self).__init__()
        self.setWindowTitle('Series Watcher %s' % TEXT_VERSION)
        self.setMinimumSize(820, 600)
        self.setWindowIcon(QIcon(THEME + 'sw.ico'))
        
        self.setup()
        Config.loadConfig()
        
        # Get the last window size
        if 'window_size' in Config.config:
            w, h = Config.config['window_size'].split('x')
            self.resize(int(w), int(h))
        
        # Load the main windows
        self.createWindow()
        self.startThreads()
        if not Serie.getSeries():
            self.openAddSerie()
        
        QtCore.QTimer.singleShot(5000, self.checkSerieUpdate)

        # Load the player
        try:
            self.player = Player(self)
        except:
            self.player = None

    def startThreads(self):
        """Start all threads."""
        self.commandOpen = QtCore.QProcess()
        
        self.episodesLoader = EpisodesLoaderThread(self)
        self.episodesLoader.episodeLoaded.connect(self.episodeLoaded)
        
        self.serieLoaderWorker = SerieLoaderWorker(self)
        self.serieLoaderWorker.serieLoaded.connect(self.serieLoaded)
        
        self.searchWorker = SearchWorker(self)
        self.searchWorker.searchFinished.connect(self.searchFinished)
    
        self.refreshSeries = RefreshSeriesWorker(self)
        self.refreshSeries.serieUpdateStatus.connect(self.serieUpdateStatus)
        self.refreshSeries.serieUpdated.connect(self.serieUpdated)
        
        self._thread = QtCore.QThread()
        self.syncDbWorker = SyncDbWorker()
        self.syncDbWorker.moveToThread(self._thread)
        self._thread.start()
    
    def checkSerieUpdate(self):
        task = CheckSerieUpdateTask()
        runnable = Runnable(task)
        runnable.task.updateRequired.connect(self.refreshSeries.addSerie)
        self.threadPool.tryStart(runnable)

    def currentSerieId(self):
        """Return the current serie ID."""
        return self.selectSerie.currentIndex()
    
    def createWindow(self):
        """Draw the main window."""
        self.createMenu()
        
        with open(THEME + 'serieswatcher.css') as file_:
            self.setStyleSheet(file_.read())
        
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
        
        layoutSerie = QtGui.QHBoxLayout()
        layoutSerie.addWidget(self.selectSerie, 2)
        
        self.description = QtGui.QLabel()
        self.description.setWordWrap(True)
        self.description.setAlignment(Qt.AlignTop)
        self.description.setScaledContents(True)
        
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
        
        hw = QtGui.QWidget()
        hw.setObjectName('header')
        hw.setLayout(header)
        hw.layout().setContentsMargins(8, 8, 8, 0)
        
        # Filters
        btnPlay = QtGui.QPushButton(QIcon(ICONS + 'forward.png'), '')
        btnPlay.setFlat(True)
        btnPlay.setToolTip(u"Jouer l'épisode suivant")
        btnPlay.clicked.connect(self.playFirstEpisode)
        
        btnRand = QtGui.QPushButton(QIcon(ICONS + 'random.png'), '')
        btnRand.setFlat(True)
        btnRand.setToolTip(u'Jouer un épisode au hasard')
        btnRand.clicked.connect(self.playRandomEpisode)
        
        self.searchBar = QtGui.QLineEdit()
        self.searchBar.setPlaceholderText('Rechercher...')
        self.searchBar.textChanged.connect(self.searchChanged)
        
        self.selectSeason = QtGui.QComboBox()
        self.selectSeason.currentIndexChanged.connect(self.refreshScreen)
        self.selectSeason.setMinimumContentsLength(18)
        
        self.filter = FilterMenu()
        self.filter.filterChanged.connect(self.refreshScreen)
        
        filterBar = QtGui.QHBoxLayout()
        filterBar.addWidget(btnPlay)
        filterBar.addWidget(btnRand)
        filterBar.addWidget(self.selectSeason)
        filterBar.addWidget(self.filter)
        filterBar.addStretch()
        filterBar.addWidget(self.searchBar)
        
        fbw = QtGui.QWidget()
        fbw.setObjectName('filterBar')
        fbw.setLayout(filterBar)
        fbw.layout().setContentsMargins(8, 4, 8, 4)
        fbw.setMinimumHeight(35)
        eff = QtGui.QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(3)
        eff.setOffset(0, 0)
        fbw.setGraphicsEffect(eff)
        
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
        body.layout().setContentsMargins(0, 0, 0, 0)
        
        # Footer
        self.selectionTitle = QtGui.QLabel()
        self.selectionTitle.setAlignment(Qt.AlignTop)
        self.selectionDescription = QtGui.QLabel()
        self.selectionDescription.setWordWrap(True)
        self.selectionDescription.setAlignment(Qt.AlignTop)
        
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.selectionDescription)
        
        self.selectionBtnFavorite = QtGui.QPushButton()
        self.selectionBtnFavorite.setFixedWidth(160)
        self.selectionBtnFavorite.setFlat(True)
        self.selectionBtnFavorite.clicked.connect(self.toggleSelectionFavorite)
        self.selectionBtnView = QtGui.QPushButton()
        self.selectionBtnView.setFlat(True)
        self.selectionBtnView.clicked.connect(self.toggleSelectionViewed)
        self.selectionNumberView = QtGui.QLabel()
        self.selectionLastView = QtGui.QLabel()
        
        self.selectionIconFavorite = QtGui.QLabel('<img src="%sstar.png" />'
                                                  % ICONS)
        self.selectionIconView = QtGui.QLabel('<img src="%scheck.png" />'
                                              % ICONS)
        
        episodeBarLayout = QtGui.QGridLayout()
        episodeBarLayout.addWidget(self.selectionIconFavorite, 0, 0)
        episodeBarLayout.addWidget(self.selectionBtnFavorite, 0, 1)
        episodeBarLayout.addWidget(self.selectionIconView, 1, 0)
        episodeBarLayout.addWidget(self.selectionBtnView, 1, 1)
        episodeBarLayout.addWidget(QtGui.QLabel('<img src="%seye.png" />'
                                                % ICONS), 2, 0)
        episodeBarLayout.addWidget(self.selectionNumberView, 2, 1)
        episodeBarLayout.addWidget(QtGui.QLabel('<img src="%scalendar.png" />'
                                                % ICONS), 3, 0)
        episodeBarLayout.addWidget(self.selectionLastView, 3, 1)
        
        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addWidget(scrollArea)
        bottomLayout.addLayout(episodeBarLayout)
        
        footerLayout = QtGui.QVBoxLayout()
        footerLayout.addWidget(self.selectionTitle)
        footerLayout.addLayout(bottomLayout)
        
        self.footer = QtGui.QWidget()
        self.footer.setObjectName('footer')
        self.footer.setLayout(footerLayout)
        self.footer.hide()
        
        # Layout
        window = QtGui.QVBoxLayout()
        window.layout().setContentsMargins(0, 0, 0, 8)
        window.addWidget(hw)
        window.addWidget(fbw)
        window.addLayout(body, 1)
        window.addWidget(self.footer)
        
        win = QtGui.QWidget()
        win.setLayout(window)
        self.setCentralWidget(win)
        
        # Shortcuts
        sortcuts = [
            ('Ctrl+F', self.searchBar.setFocus),
            ('F', self.toggleSelectionFavorite),
            ('V', self.toggleSelectionViewed),
            ('P', self.playClicked)
        ]
        for key, action in sortcuts:
            QtGui.QShortcut(key, self).activated.connect(action)

    def createMenu(self):
        """Add menu bar in the window."""
        self.menubar = self.menuBar()
        
        # Menu "Series"
        seriesMenu = self.menubar.addMenu(u'Séries')
        seriesMenu.addAction(QIcon(ICONS + 'add.png'), u'Nouvelle série',
                             self.openAddSerie).setShortcut('Ctrl+N')
        seriesMenu.addAction(QIcon(ICONS + 'edit.png'), u'Editer les séries',
                             self.openEditSerie).setShortcut('Ctrl+E')
        seriesMenu.addAction(u'Mettre à jour cette série',
                             self.updateSerieMenu).setShortcut('Ctrl+U')
        seriesMenu.addAction(u'Mettre à jour les séries',
                             self.updateAllSeriesMenu)
        
        # Menu "Episodes"
        episodesMenu = self.menubar.addMenu('Episodes')
        episodesMenu.addAction(QIcon(ICONS + 'reload.png'), u'Recharger',
                               self.reloadMenu).setShortcut('Ctrl+R')
        episodesMenu.addAction(QIcon(ICONS + 'check.png'),
                               u'Marquer comme vue',
                               self.viewSelectEpisodeMenu).setShortcut('Ctrl+K')
        episodesMenu.addAction(QIcon(ICONS + 'uncheck.png'),
                               u'Marquer comme non vue',
                               self.notViewSelectEpisodeMenu)
        episodesMenu.addAction(u'Marquer la série comme vue',
                               self.allEpisodeView)
        
        # Menu "Series Watcher"
        SWMenu = self.menubar.addMenu('Series Watcher')
        SWMenu.addAction(QIcon(ICONS + 'options.png'), 'Options',
                         self.openOptions)
        SWMenu.addAction(QIcon(ICONS + 'help.png'), 'A propos', self.openAbout)
    
    def openUpdateWindow(self):
        """Open a window that ask if the program must update the database."""
        r = QMessageBox.question(self, u'Mise à jour', u"Series Watcher a "
                             u"trouvé une ancienne base de données. "
                             u"Voulez-vous l'importer dans la nouvelle "
                             u"version ?",
                             QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            import upgrader
        elif r == QMessageBox.No:
            olduser = 'user.backup/'
            if os.path.isdir(olduser):
                shutil.rmtree(olduser)
            try:
                shutil.move('user/', olduser)
            except:
                pass
    
    def setup(self):
        """Some check when the program open."""
        if os.path.isfile(VERSION_FILE):
            with open(VERSION_FILE) as vf:
                if vf.read().strip() != VERSION:
                    self.openUpdateWindow()
        elif USER_DIR_FOUND:
            self.openUpdateWindow()
        else:
            with open(VERSION_FILE, 'w+') as f:
                f.write(VERSION)
        if not os.path.isdir(USER):
            os.mkdir(USER)
        if not os.path.isdir(SERIES):
            os.mkdir(SERIES)
        if not os.path.isdir(SERIES_IMG):
            os.mkdir(SERIES_IMG)
        if not os.path.isdir(SERIES_BANNERS):
            os.mkdir(SERIES_BANNERS)
        databaseConnect()
    
    def viewSelectEpisodeMenu(self):
        """Triggered when the user mark an episode as view."""
        self.viewStatusChanged(True)
    
    def notViewSelectEpisodeMenu(self):
        """Triggered when the user mark an episode as non-view."""
        self.viewStatusChanged(False)
    
    def clearSelectionInfos(self):
        self.selectionTitle.setText('')
        self.selectionDescription.setText('')
        self.footer.hide()
    
    def playFirstEpisode(self):
        """Play the first episode."""
        # Try to watch the first not viewed episode
        newEpisodes = (e for e in self.map.itervalues() if e.status == 2)
        try:
            firstNewEpisode = min(newEpisodes, key=lambda e: e.number)
        except ValueError:
            pass
        else:
            self.playEpisode(firstNewEpisode)
            return True
        
        # Try to watch the episode after last episode viewed
        episodes = (e for e in self.map.itervalues() if e.lastView)
        try:
            lastEpisode = max(episodes, key=lambda e: e.lastView).number
            nextEpisodes = \
                (e for e in self.map.itervalues() if e.number > lastEpisode)
            nextEpisode = min(nextEpisodes, key=lambda e: e.number)
        except ValueError:
            pass
        else:
            self.playEpisode(nextEpisode)
            return True
        
        episodes = (e for e in self.map.itervalues())
        try:
            nextEpisode = min(episodes, key=lambda e: e.number)
        except ValueError:
            pass
        else:
            self.playEpisode(nextEpisode)
            return True
        return False
    
    def playRandomEpisode(self):
        """Play a random episode."""
        episodesLongTime = []
        otherEpisodes = []
        
        limitDate = datetime.now()
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
            episode = random.choice(episodesLongTime)
        elif otherEpisodes:
            episodes = sorted(otherEpisodes, key=lambda e: e.lastView)[-15:]
            episode = random.choice(episodes)
        else:
            return False
        
        self.playEpisode(episode)
        self.player.btnRandom.setChecked(True)
        return True
    
    def allEpisodeView(self):
        """Mark all episode as 'view'."""
        for e in self.currentSerie.episodes:
            e.setView()
        self.refreshEpisodes()
    
    def reloadMenu(self):
        """Reload the window."""
        self.currentSerie.loadSerie()
        self.refreshEpisodes()
    
    def serieUpdateStatus(self, serieLocalID, status, args):
        """Update the satus in satus bar when the program perform
        an update.
        """
        messages = [
            u'%(title)s : téléchargement des informations sur la série...',
            u'%(title)s : téléchargement des informations sur les épisodes...',
            u'%(title)s : téléchargement des miniatures (%(nb)d/%(nbImages)d)...'
        ]
        message = messages[status] % args
        self.status.showMessage(message)
        if self.currentSerieId() == serieLocalID and status not in (0, 2):
            self.serieLoaderWorker.forceReload()
    
    def openEditSerie(self):
        """Open the window Edit Serie."""
        editSeries = EditSeries(self)
        editSeries.edited.connect(self.seriesEdited)
        editSeries.show()
    
    def seriesEdited(self):
        """Triggered when a serie is edited."""
        self.reloadSelectSerie()
        self.serieLoaderWorker.forceReload()
    
    def openAbout(self):
        """Open the window About."""
        about = About(self)
        about.show()
    
    def openOptions(self):
        """Open the window Options."""
        options = Options(self)
        options.show()
    
    def openAddSerie(self):
        """Open the window Add Serie."""
        addSerie = AddSerie(self)
        addSerie.serieAdded.connect(self.serieAdded)
        addSerie.show()
    
    def updateSerieMenu(self):
        """Force the update of the current serie."""
        self.refreshSeries.addSerie(self.currentSerieId())
    
    def updateAllSeriesMenu(self):
        """Force the update of all series."""
        for i, e in enumerate(Serie.getSeries()):
            self.refreshSeries.addSerie(i)
    
    def refreshSelectedEpisodes(self):
        """Refresh episodes that selected by the user."""
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = item.row(), item.column()
            try:
                self.episodes.cellWidget(r, c).refresh()
            except AttributeError:
                pass
    
    def getSelectedEpisode(self):
        """Return the selected episode."""
        indexes = self.episodes.selectedIndexes()
        if len(indexes) == 1:
            r, c = indexes[0].row(), indexes[0].column()
            if (r, c) in self.map:
                return self.map[r, c]
    
    def getSelectedEpisodes(self):
        """Generator that return the list of episodes."""
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = item.row(), item.column()
            if (r, c) in self.map:
                yield self.map[r, c]
    
    def showFooter(self):
        """Show the footer."""
        self.footer.show()
        pos = self.footer.geometry()
        self.hideAnimation = QtCore.QPropertyAnimation(self.footer, "geometry")
        self.hideAnimation.setDuration(150)
        self.footer.endGeometry = QtCore.QRect(pos)
        self.footer.startGeometry = QtCore.QRect(pos.x(),
                                        self.geometry().height(),
                                        self.footer.geometry().width(), 0)
        self.hideAnimation.setStartValue(self.footer.startGeometry)
        self.hideAnimation.setEndValue(self.footer.endGeometry)
        self.hideAnimation.start()
    
    def refreshFooter(self):
        """Refresh the footer informations."""
        episode = self.getSelectedEpisode()
        if episode:
            if self.footer.isHidden():
                self.showFooter()
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
                lastView = '-'
            self.selectionLastView.setText(lastView)
            if episode.favorite:
                self.selectionBtnFavorite.setText('Enlever des favoris')
                self.selectionIconFavorite.setText('<img src="%sstar.png" />'
                                                   % ICONS)
            else:
                self.selectionBtnFavorite.setText('Ajouter aux favoris')
                self.selectionIconFavorite.setText('<img src="%sunstar.png" />'
                                                   % ICONS)
            if episode.nbView == 0:
                self.selectionBtnView.setText('Marquer comme vu')
                self.selectionIconView.setText('<img src="%suncheck.png" />'
                                               % ICONS)
            else:
                self.selectionBtnView.setText('Marquer comme non vu')
                self.selectionIconView.setText('<img src="%scheck.png" />'
                                               % ICONS)
        else:
            self.clearSelectionInfos()
    
    def serieAdded(self, serie):
        """Triggered when a serie is added."""
        nbSeries = len(Serie.getSeries())
        self.reloadSelectSerie()
        self.selectSerie.setCurrentIndex(nbSeries)
    
    def reloadSelectSerie(self):
        """Reload the serie selector."""
        self.selectSerie.blockSignals(True)
        Serie.deleteSeriesCache()
        currentIndex = self.selectSerie.currentIndex()
        currentIndex = 0 if currentIndex < 0 else currentIndex
        currentIndex = len(Serie.getSeries())-1 if currentIndex >= len(Serie.getSeries()) else currentIndex
        self.selectSerie.clear()
        for s in Serie.getSeries():
            self.selectSerie.addItem(s.title)
        self.selectSerie.setCurrentIndex(currentIndex)
        self.selectSerie.blockSignals(False)
    
    def closeEvent(self, e):
        """Triggered before the window is close."""
        if not self.isMaximized():
            Config.config['window_size'] = '%dx%d' % (self.width(),
                                                      self.height())
            Config.save()

        self._thread.quit()
        self._thread.wait()

        QtGui.QMainWindow.closeEvent(self, e)
    
    def favoriteChanged(self, value):
        """Triggered when an episode is mark or unmark
        as favorite. This method save in database and refresh
        the window.
        """
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
        """Triggered when an episode is mark or unmark
        as view. This method save in database and refresh
        the window.
        """
        items = self.episodes.selectedIndexes()
        for item in items:
            r, c = coord = item.row(), item.column()
            video = self.episodes.cellWidget(r, c)
            if video is not None:
                if value:
                    self.map[coord].setView()
                    video.setStatus(1)
                else:
                    self.map[coord].setNotView()
                    video.setStatus(2)
        self.refreshFooter()
        self.refreshCount()
    
    def episodesDblClicked(self, n):
        """Triggered when the user double click on an episode."""
        coord = (n.row(), n.column())
        if coord in self.map:
            episode = self.map[coord]
            self.playEpisode(episode)
    
    def searchChanged(self, textSearch):
        """Triggered when the user change the text in the searchbar."""
        if self.currentSerie:
            textSearch = unicode(self.searchBar.text())
            self.searchWorker.changeText(textSearch)
    
    def searchFinished(self, listEpisodes):
        """Triggered when the search is finish."""
        if self.searchBar.text() == '':
            self.refreshEpisodes()
        else:
            self.showEpisode(listEpisodes)
    
    def playClicked(self):
        """Triggered when the user click on play in the
        right click menu.
        """
        items = self.episodes.selectedIndexes()
        for item in items:
            coord = (item.row(), item.column())
            if coord in self.map:
                episode = self.map[coord]
                self.playIntegratedPlayer(episode)
                self.markAsView(episode)
    
    def playEpisode(self, episode):
        """Open the player and open the episode."""
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
        """Play an episode in the integrated player."""
        if episode.path:
            if not (self.player or self.player.VLCLoaded):
                title = 'Erreur lors du chargement de VLC'
                QMessageBox.critical(self, title, ERROR_PLAYER_LOAD)
                return
            
            path = os.path.normpath(episode.path)
            self.player.addToPlayList(episode.number, episode.title,
                                      path, episode.cover)
            self.refreshCount()
            if not self.player.isVisible():
                self.player.show()
                self.player.tryToPlay()
    
    def toggleSelectionFavorite(self):
        """Toggle the selection in favorite or unfavorite.
        The choice is based on the number of favorite episode.
        """
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
    
    def toggleSelectionViewed(self):
        """Toggle the selection in viewed or non-viewed.
        The choice is based on the number of viewed episode.
        """
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
        """Mark the episode as view."""
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
        self._episodesOnScreen = list(episodes)
        self.refreshScreen()

    def refreshScreen(self):
        """Display episodes in the grid."""
        self.clearSelectionInfos()
        self.episodesLoader.newQuery()
        self.episodes.clear()
        self.map.clear()
        nbColumn = self.episodes.nbColumn
        count = 0
        for i, e in enumerate(self._episodesOnScreen):
            (x, y) = (i // nbColumn, i % nbColumn)
            self.map[x, y] = e
            self.episodesLoader.addEpisode(x, y, e)
            count += 1
        self.episodesLoader.start()
        self.refreshCount()
        nbRows = int(math.ceil(count / float(self.episodes.nbColumn)))
        self.episodes.setRowCount(nbRows)
    
    def refreshCount(self):
        """Refresh counters."""
        nbAv = self.currentSerie.nbEpisodeAvailable
        nbNotView = self.currentSerie.nbNotView
        nbEpisodeTotal = self.currentSerie.nbEpisodeTotal
        nbView = self.currentSerie.nbView
        self.filter.setCounters(nbEpisodeTotal,
                               self.currentSerie.nbEpisodeNotAvailable,
                               nbAv, nbNotView, self.currentSerie.nbFavorites)
        
        if nbEpisodeTotal > 0:
            percentageDL = (nbAv/float(nbEpisodeTotal)) * 100
            percentageView = (nbView/float(nbEpisodeTotal)) * 100
        else:
            percentageDL = percentageView = 0
        
        c = u"Série vue à %d %% | %d %% d'épisodes disponibles" \
                % (percentageView, percentageDL)
        self.nbEpisodes.setText(c)
    
    def episodeLoaded(self, x, y, episode):
        """This method add the episode in the episodes grid.
        
        Triggered when an episode is loaded.
        """
        item = VideoItem(episode)
        self.episodes.setCellWidget(x, y, item)
        item.setTitle(episode.title)
    
    def getEpisodes(self):
        """Return the generator of serie's episodes that filtered
        by current filters parameters.
        """
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
    
    def refreshEpisodes(self):
        """Refresh the sreen."""
        self.searchBar.clear()
        if self.currentSerie:
            self.showEpisode(self.getEpisodes())
    
    def clearSeries(self):
        """Clear all informations about the current serie."""
        self.map.clear()
        self.selectSeason.blockSignals(True)
        self.selectSeason.clear()
        self.selectSeason.addItem('Toutes les saisons')
        self.selectSeason.addItem('Bonus')
        self.selectSeason.blockSignals(False)
        
        self.description.setText(u"La série n'est pas encore chargée.")
        self.imageSerie.clear()
        self.episodes.clear()
        self.nbEpisodes.clear()
        
        self.filter.setCounters(0, 0, 0, 0, 0)

    def serieLoaded(self, serie):
        """Triggered when the serie is loaded."""
        self.currentSerie = serie
        
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
        desc = self.currentSerie.description.replace('\n', '<br/>')
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

        self.filter.blockSignals(True)
        if self.currentSerie.path:
            self.filter.setSelection(self.filter.dl)
        else:
            self.filter.setSelection(self.filter.all)
        self.filter.blockSignals(False)

        self.refreshEpisodes()
        
    def serieUpdated(self, serieLocalID):
        """Triggered when a serie is updated."""
        self.status.showMessage('')
        if self.currentSerieId() == serieLocalID:
            self.serieLoaderWorker.forceReload()