#!/usr/bin/env python

__all__ = ['EpisodesLoaderThread', 'SearchWorker', 'RefreshSeriesWorker',
           'SerieLoaderWorker', 'SyncDbWorker']

import time
import os.path
from PyQt4.QtCore import Qt
from datetime import datetime
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import qDebug
from sqlobject.sqlbuilder import AND
from sqlobject.dberrors import OperationalError
from .const import *
from .models import Serie, Episode
from .search import *
from .thetvdb import TheTVDBSerie
from .worker import Runnable


class DownloadSerieTask(QtCore.QObject):
    serieUpdated = QtCore.pyqtSignal(int)
    serieUpdateStatus = QtCore.pyqtSignal(int, int, dict)

    def __init__(self, serieLocalID, parent=None):
        super(DownloadSerieTask, self).__init__(parent)
        self.serieLocalID = serieLocalID

    def run(self):
        serie = Serie.getSeries()[self.serieLocalID]
        self.serieUpdateStatus.emit(self.serieLocalID, 0, {'title': serie.title})
        
        try:
            tvDb = TheTVDBSerie(serie.tvdbID, serie.lang)
        except Exception as e:
            qDebug("Error download" + e)
            return False
        
        # Info serie
        serieInfos = tvDb.infos_serie()
        bannerPath = '%s%s.jpg' % (SERIES_BANNERS, serie.uuid)
        tvDb.download_banner(bannerPath)
        
        if serieInfos is None:
            return
        
        serie.description = serieInfos['description']
        serie.firstAired = datetime.strptime(serieInfos['firstAired'],
                                             '%Y-%m-%d')
        serie.lastUpdated = int(serieInfos['lastUpdated'])
        self.serieUpdateStatus.emit(self.serieLocalID, 1, {'title': serie.title})
        
        # Info episode
        episodesDb = {(e.season, e.episode) for e in serie.episodes}
        episodeList = set()
        for e in tvDb.episodes():
            number = (e['season'], e['episode'])
            episodeList.add(number)
            if e['firstAired']:
                firstAired = datetime.strptime(e['firstAired'], '%Y-%m-%d')
            else:
                firstAired = None
            if number in episodesDb:
                episode = list(Episode.select(
                    AND(Episode.q.season==int(e['season']),
                    Episode.q.episode==int(e['episode']),
                    Episode.q.serie==serie)))[0]
                episode.firstAired = firstAired
                episode.title = unicode(e['title'])
                episode.description = unicode(e['description'])
            else:
                Episode(
                    title = unicode(e['title']),
                    description = unicode(e['description']),
                    season = int(e['season']),
                    episode = int(e['episode']),
                    firstAired = firstAired,
                    serie = serie
                )
        
        toDelete = episodesDb - episodeList
        for season, episode in toDelete:
            Episode.deleteBy(serie=serie, season=season, episode=episode)
        
        # Create image path
        imgDir = SERIES_IMG + serie.uuid
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        # Miniature DL
        for i, nbImages in tvDb.download_miniatures(imgDir):
            self.serieUpdateStatus.emit(self.serieLocalID, 2,
                {'title': serie.title, 'nb': i, 'nbImages': nbImages})
        
        self.serieUpdated.emit(self.serieLocalID)
        serie.lastUpdate = datetime.now()
        serie.setLoaded(True)


class SyncDbWorker(QtCore.QObject):
    """Worker to commit changes in a serie to the
    local database.
    """
    def __init__(self, parent=None):
        super(SyncDbWorker, self).__init__(parent)
        self.run()

    def run(self):
        for serie in Serie.getSeries():
            try:
                serie.syncUpdate()
            except OperationalError as msg:
                qDebug('SQLObject Error : %s' % msg)
        for episode in Episode.select():
            try:
                episode.syncUpdate()
            except OperationalError as msg:
                qDebug('SQLObject Error : %s' % msg)
        QtCore.QTimer.singleShot(500, self.run)


class RefreshSeriesWorker(QtCore.QObject):
    """Worker to update the serie from the online database."""
    serieUpdated = QtCore.pyqtSignal(int)
    serieUpdateStatus = QtCore.pyqtSignal(int, int, dict)

    def __init__(self, parent=None):
        super(RefreshSeriesWorker, self).__init__(parent)
        self.toRefresh = []
        self.threadPool = QtCore.QThreadPool()
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.run)
        self._timer.start(500)

    def run(self):
        for serieLocalID in self.toRefresh[:]:
            task = DownloadSerieTask(serieLocalID)
            runnable = Runnable(task)
            runnable.task.serieUpdated.connect(self.serieUpdated)
            runnable.task.serieUpdateStatus.connect(self.serieUpdateStatus)
            self.threadPool.tryStart(runnable)
            del self.toRefresh[0]

    def addSerie(self, serieLocalID):
        if serieLocalID not in self.toRefresh:
            self.toRefresh.append(serieLocalID)


class SerieLoaderWorker(QtCore.QObject):
    """Thread to load the current serie from the local database."""
    serieLoaded = QtCore.pyqtSignal(Serie)
    lastCurrentSerieId = -1
    _forceReload = False
    
    def __init__(self, parent=None):
        super(SerieLoaderWorker, self).__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.run)
        self._timer.start(100)

    def run(self):
        currentSerieId = self.parent().currentSerieId()
        if currentSerieId != self.lastCurrentSerieId or self._forceReload:
            try:
                serie = Serie.getSeries()[currentSerieId]
            except IndexError:
                pass
            else:
                serie.clearEpisodeCache()
                serie.loadSerie()
                self.serieLoaded.emit(serie)
            self.lastCurrentSerieId = currentSerieId
            self._forceReload = False
    
    def forceReload(self):
        self._forceReload = True


class SearchWorker(QtCore.QObject):
    """Thread to search in the database."""
    searchFinished = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(SearchWorker, self).__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.run)
        self._timer.start(100)
        self.textSearch = ''
        self.lastTextSearch = ''

    def run(self):
        if self.lastTextSearch != self.textSearch:
            self.lastTextSearch = self.textSearch
            self.search(self.lastTextSearch)
    
    def search(self, textSearch):
        listEpisodes = []
        for e in self.parent().currentSerie.episodes:
            score = 1000 if search(textSearch, split(e.title)) else 0
            score += search2(textSearch, split(e.description))
            if score > 0:
                listEpisodes.append((score, e))
        
        func = lambda x: x[0]
        listEpisodes = sorted(listEpisodes, key=func, reverse=True)
        listEpisodes = [e for t, e in listEpisodes]
        self.searchFinished.emit(listEpisodes)

    def changeText(self, search):
        self.textSearch = search


class EpisodesLoaderThread(QtCore.QThread):
    """Thread to create miniature of the episode."""
    episodeLoaded = QtCore.pyqtSignal(int, int, Episode)
    episodes = []
    lastQuery = 0
    
    def run(self):
        def map_(episode):
            qId, x, y, episode = episode
            if qId == self.lastQuery:
                self.episodeLoaded.emit(x, y, episode)
        map(map_, self.episodes)
    
    def newQuery(self):
        self.lastQuery += 1
    
    def addEpisode(self, x, y, episode):
        self.episodes.append((self.lastQuery, x, y, episode))