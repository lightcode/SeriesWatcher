#!/usr/bin/env python

from datetime import datetime
import os.path
import time
import xml
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from updatesfile import UpdatesFile
from search import *
from thetvdb import TheTVDBSerie
from const import *
from models import Serie, Episode
from sqlobject.dberrors import OperationalError
from sqlobject.sqlbuilder import AND

__all__ = ['EpisodesLoaderThread', 'SearchThread', 'RefreshSeriesThread',
           'CheckSerieUpdateThread', 'LoaderThread', 'SyncDBThead', 'RemoteSyncThead']


class RemoteSyncThead(QtCore.QThread):
    def run(self):
        # 1. Connect to the API
        
        # 2. Get the series summary for this user
        
        # 3. Update the local database
        
        # 4. Send to the server updates
        pass



class SyncDBThead(QtCore.QThread):
    def run(self):
        while True:
            for s in Serie.getSeries():
                try:
                    s.syncUpdate()
                except OperationalError as msg:
                    print 'SQLObject Error : %s' % msg
            try:
                for e in self.parent().currentSerie.episodes:
                    try:
                        e.syncUpdate()
                    except sqlobject.dberrors.OperationalError as msg:
                        print 'SQLObject Error : %s' % msg
            except AttributeError:
                pass
            self.msleep(500)


class CheckSerieUpdateThread(QtCore.QThread):
    TIME_BETWEEN_UPDATE = 86400 # a day
    updateRequired = QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None):
        super(CheckSerieUpdateThread, self).__init__(parent)
        UpdatesFile.loadUpdates()
    
    
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
                    remoteTime = datetime.fromtimestamp(tvDb.getLastUpdated())
                except TypeError:
                    print 'Get last update failed.'
                else:
                    if not localTime or localTime < remoteTime:
                        self.updateRequired.emit(localeID)
            self.updateLastVerif()



class RefreshSeriesThread(QtCore.QThread):
    serieUpdated = QtCore.pyqtSignal(int)
    serieUpdateStatus = QtCore.pyqtSignal(int, 'QString', int)
    
    def __init__(self, parent=None):
        super(RefreshSeriesThread, self).__init__(parent)
        self.toRefresh = []
    
    
    def downloadConfiguration(self, serieLocalID):
        serie = Serie.getSeries()[serieLocalID]
        self.serieUpdateStatus.emit(serieLocalID, serie.title, 0)
        
        tvDb = TheTVDBSerie(serie.tvdbID, serie.lang)
        try:
            tvDb.downloadFullSerie()
        except xml.parsers.expat.ExpatError:
            print "Error download"
            return False
        
        # Info serie
        serieInfos = tvDb.getInfosSerie()
        bannerPath = '%s%s.jpg' % (SERIES_BANNERS, serie.uuid)
        tvDb.downloadBanner(bannerPath)
        
        if serieInfos is None:
            return
        
        serie.description = serieInfos['description']
        serie.firstAired = datetime.strptime(serieInfos['firstAired'], '%Y-%m-%d')
        serie.lastUpdated = int(serieInfos['lastUpdated'])
        self.serieUpdateStatus.emit(serieLocalID, serie.title, 1)
        
        episodesDb = {e.number for e in serie.episodes}       
        
        # Create image path
        imgDir = SERIES_IMG + serie.uuid
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        # Info episode
        episodeList = tvDb.getEpisodes(imgDir)
        for e in episodeList:
            if e['firstAired']:
                firstAired = datetime.strptime(e['firstAired'], '%Y-%m-%d')
            else:
                firstAired = None
            if e['number'] in episodesDb:
                episode = list(Episode.select(AND(Episode.q.season==int(e['season']),
                    Episode.q.episode==int(e['episode']), Episode.q.serie==serie)))[0]
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
        self.serieUpdateStatus.emit(serieLocalID, serie.title, 2)
        
        # Miniature DL
        tvDb.downloadAllImg()
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



class LoaderThread(QtCore.QThread):
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
                    self.serieLoaded.emit(serie)
                except IndexError:
                    pass
                self.lastCurrentSerieId = currentSerieId
                self._forceReload = False
            self.msleep(100)



class SearchThread(QtCore.QThread):
    searchFinished = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        super(SearchThread, self).__init__(parent)
        self.textSearch = ""
    
    
    def run(self):
        textSearch = ""
        while True:
            if textSearch != self.textSearch:
                textSearch = self.textSearch
                self.search(textSearch)
            self.msleep(100)
    
    
    def search(self, textSearch):
        listEpisodes = []
        episodes = self.parent().currentSerie.episodes
        for e in episodes:
            score = 1000 if search(textSearch, decompose(e.title)) else 0
            score += search2(textSearch, decompose(e.description))
            if score > 0:
                listEpisodes.append((score, e))
        
        func = lambda x: x[0]
        listEpisodes = sorted(listEpisodes, key=func, reverse=True)
        listEpisodes = [e for t, e in listEpisodes]
        self.searchFinished.emit(listEpisodes)


    def changeText(self, search):
        self.textSearch = search



class EpisodesLoaderThread(QtCore.QThread):
    episodeLoaded = QtCore.pyqtSignal(tuple)
    episodes = []
    lastQuery = 0
    
    def run(self):
        param = (Qt.KeepAspectRatio, Qt.SmoothTransformation)
        for qId, x, y, episode, imgPath in self.episodes:
            if qId == self.lastQuery:
                image = QtGui.QImage(imgPath)
                if image != QtGui.QImage():
                    image = image.scaled(120, 90, *param)
                self.episodeLoaded.emit((x, y, episode, image))
    
    
    def newQuery(self):
        self.lastQuery += 1
    
    
    def addEpisode(self, x, y, episode, imgPath):
        self.episodes.append((self.lastQuery, x, y, episode, imgPath))