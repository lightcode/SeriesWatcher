#!/usr/bin/env python

__all__ = ['EpisodesLoaderThread', 'SearchThread', 'RefreshSeriesThread',
           'CheckSerieUpdateThread', 'SerieLoaderThread', 'SyncDBThead',
           'RemoteSyncThead']

import xml
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


class RemoteSyncThead(QtCore.QThread):
    """Thread to synchronize the local database to a
    remote database.
    """
    def run(self):
        # 1. Connect to the API
        
        # 2. Get the series summary for this user
        
        # 3. Update the local database
        
        # 4. Send to the server updates
        pass


class SyncDBThead(QtCore.QThread):
    """Thread to commit changes in a serie to the
    local database.
    """
    def run(self):
        while True:
            for s in Serie.getSeries():
                try:
                    s.syncUpdate()
                except OperationalError as msg:
                    qDebug('SQLObject Error : %s' % msg)
            try:
                for e in self.parent().currentSerie.episodes:
                    try:
                        e.syncUpdate()
                    except sqlobject.dberrors.OperationalError as msg:
                        qDebug('SQLObject Error : %s' % msg)
            except AttributeError:
                pass
            self.msleep(500)


class CheckSerieUpdateThread(QtCore.QThread):
    """Thread to check updates on the series database and
    synchronize with the local database.
    """
    TIME_BETWEEN_UPDATE = 86400 # a day
    updateRequired = QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None):
        super(CheckSerieUpdateThread, self).__init__(parent)
    
    def getLastVerification(self):
        try:
            with open(LAST_VERIF_PATH, 'r') as f:
                return int(''.join(f.readlines()).strip())
        except IOError:
            return 0
        except ValueError:
            return 0
    
    def updateLastVerif(self):
        with open(LAST_VERIF_PATH, 'w+') as f:
            f.write("%d" % time.time())
    
    def run(self):
        lastVerification = self.getLastVerification()
        if int(time.time() - lastVerification) >= self.TIME_BETWEEN_UPDATE:
            for localeID, serie in enumerate(Serie.getSeries()):
                localTime = serie.lastUpdate
                tvDb = TheTVDBSerie(serie.tvdbID, serie.lang)
                try:
                    remoteTime = datetime.fromtimestamp(tvDb.last_update())
                except TypeError:
                    qDebug('Get last update failed.')
                else:
                    if not localTime or localTime < remoteTime:
                        self.updateRequired.emit(localeID)
            self.updateLastVerif()


class RefreshSeriesThread(QtCore.QThread):
    """Thread to update the serie from the online database."""
    serieUpdated = QtCore.pyqtSignal(int)
    serieUpdateStatus = QtCore.pyqtSignal(int, int, dict)
    
    def __init__(self, parent=None):
        super(RefreshSeriesThread, self).__init__(parent)
        self.toRefresh = []
    
    def downloadConfiguration(self, serieLocalID):
        serie = Serie.getSeries()[serieLocalID]
        self.serieUpdateStatus.emit(serieLocalID, 0, {'title': serie.title})
        
        tvDb = TheTVDBSerie(serie.tvdbID, serie.lang)
        try:
            tvDb.download_serie()
        except xml.parsers.expat.ExpatError:
            qDebug("Error download")
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
        self.serieUpdateStatus.emit(serieLocalID, 1, {'title': serie.title})
        
        # Create image path
        imgDir = SERIES_IMG + serie.uuid
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        # Info episode
        episodesDb = {e.number for e in serie.episodes} 
        episodeList = list(tvDb.episodes(imgDir))
        for e in episodeList:
            if e['firstAired']:
                firstAired = datetime.strptime(e['firstAired'], '%Y-%m-%d')
            else:
                firstAired = None
            if e['number'] in episodesDb:
                episode = list(Episode.select(
                    AND(Episode.q.season==int(e['season']),
                    Episode.q.episode==int(e['episode']),
                    Episode.q.serie==serie)))[0]
                episode.firstAired = firstAired
                episode.title = unicode(e['title'])
                episode.description = unicode(e['desc'])
            else:
                Episode(
                    title = unicode(e['title']),
                    description = unicode(e['desc']),
                    season = int(e['season']),
                    episode = int(e['episode']),
                    firstAired = firstAired,
                    serie = serie
                )
        
        toDelete = episodesDb - {e['number'] for e in episodeList}
        for number in toDelete:
            season, episode = map(int, number.split('-'))
            Episode.deleteBy(serie=serie, season=season, episode=episode)
        
        # Miniature DL
        self.serieUpdateStatus.emit(serieLocalID, 2, {'title': serie.title})
        for i, nbImages in tvDb.download_miniatures():
            self.serieUpdateStatus.emit(serieLocalID, 3,
                {'title': serie.title, 'nb': i, 'nbImages': nbImages})
        
        self.serieUpdated.emit(serieLocalID)
        serie.lastUpdate = datetime.now()
        serie.setLoaded(True)

    def addSerie(self, serieLocalID):
        if serieLocalID not in self.toRefresh:
            self.toRefresh.append(serieLocalID)
    
    def run(self):
        while True:
            for serieLocalID in self.toRefresh[:]:
                self.downloadConfiguration(serieLocalID)
                del self.toRefresh[0]
            self.msleep(50)


class SerieLoaderThread(QtCore.QThread):
    """Thread to load the current serie from the local database."""
    serieLoaded = QtCore.pyqtSignal(Serie)
    lastCurrentSerieId = -1
    _forceReload = False
    
    def forceReload(self):
        self._forceReload = True
    
    def run(self):
        while True:
            currentSerieId = self.parent().currentSerieId()
            if currentSerieId != self.lastCurrentSerieId or self._forceReload:
                try:
                    serie = Serie.getSeries()[currentSerieId]
                    serie.loadSerie()
                    self.serieLoaded.emit(serie)
                except IndexError:
                    pass
                self.lastCurrentSerieId = currentSerieId
                self._forceReload = False
            self.msleep(100)


class SearchThread(QtCore.QThread):
    """Thread to search in the database."""
    searchFinished = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        super(SearchThread, self).__init__(parent)
        self.textSearch = ''
    
    def run(self):
        textSearch = ''
        while True:
            if textSearch != self.textSearch:
                textSearch = self.textSearch
                self.search(textSearch)
            self.msleep(100)
    
    def search(self, textSearch):
        listEpisodes = []
        episodes = self.parent().currentSerie.episodes
        for e in episodes:
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
    episodeLoaded = QtCore.pyqtSignal(int, int, Episode, QtGui.QImage)
    episodes = []
    lastQuery = 0
    
    def run(self):
        param = (Qt.KeepAspectRatio, Qt.SmoothTransformation)
        def map_(episode):
            qId, x, y, episode, imgPath = episode
            if qId == self.lastQuery:
                image = QtGui.QImage(imgPath)
                try:
                    image = image.scaled(120, 120, *param)
                except:
                    pass
                self.episodeLoaded.emit(x, y, episode, image)
        map(map_, self.episodes)
    
    def newQuery(self):
        self.lastQuery += 1
    
    def addEpisode(self, x, y, episode, imgPath):
        self.episodes.append((self.lastQuery, x, y, episode, imgPath))