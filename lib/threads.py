#!/usr/bin/env python

import cPickle as pickle
from datetime import datetime
import os.path
import time
import xml
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from config import Config
from updatesfile import UpdatesFile
from search import *
from thetvdb import TheTVDBSerie
from const import *
from models import Serie, Episode

__all__ = ['EpisodesLoaderThread', 'SearchThread', 'RefreshSeriesThread',
           'CheckSerieUpdate', 'LoaderThread']


class CheckSerieUpdate(QtCore.QThread):
    # Signals :
    updateRequired = QtCore.pyqtSignal(int)
    TIME_BETWEEN_UPDATE = 86400 # a day
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
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
                
                tvDb = TheTVDBSerie(serie)
                try:
                    remoteTime = datetime.fromtimestamp(tvDb.getLastUpdate())
                except TypeError:
                    print 'Get last update failed.'
                else:
                    if not localTime or localTime < remoteTime:
                        self.updateRequired.emit(localeID)
            self.updateLastVerif()



class RefreshSeriesThread(QtCore.QThread):
    # Signals :
    serieUpdated = QtCore.pyqtSignal(int)
    serieUpdateStatus = QtCore.pyqtSignal(int, 'QString', int)
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.toRefresh = []
    
    
    def downloadConfiguration(self, serieLocalID):
        serie = Serie.getSeries()[serieLocalID]
        self.serieUpdateStatus.emit(serieLocalID, serie.title, 0)
        
        tvDb = TheTVDBSerie(serie)
        try:
            tvDb.downloadFullSerie()
        except xml.parsers.expat.ExpatError:
            print "Error download"
            return False
        
        # Info serie
        serieInfos = tvDb.getInfosSerie()
        
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
            if e['number'] in episodesDb:
                continue
            if e['firstAired']:
                firstAired = datetime.strptime(e['firstAired'], '%Y-%m-%d')
            else:
                firstAired = None
            Episode(
                title = unicode(e['title']),
                description = unicode(e['desc']),
                season = int(e['season']),
                episode = int(e['episode']),
                firstAired = firstAired,
                serie = serie
            )
        
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
    # Signals :
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
                    self.serieLoaded.emit(Serie.getSeries()[currentSerieId])
                except IndexError:
                    pass
                self.lastCurrentSerieId = currentSerieId
                self._forceReload = False
            self.msleep(100)



class SearchThread(QtCore.QThread):
    # Signals :
    searchFinished = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
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
    # Signals :
    episodeLoaded = QtCore.pyqtSignal(tuple)
    episodes = []
    lastQuery = 0
    
    def run(self):
        param = (Qt.KeepAspectRatio, Qt.SmoothTransformation)
        for qId, x, y, title, status, imgPath in self.episodes:
            if qId == self.lastQuery:
                image = QtGui.QImage(imgPath)
                if image != QtGui.QImage():
                    image = image.scaled(120, 90, *param)
                self.episodeLoaded.emit((x, y, title, status, image))
    
    
    def newQuery(self):
        self.lastQuery += 1
    
    
    def addEpisode(self, x, y, title, infos, imgPath):
        self.episodes.append((self.lastQuery, x, y, title, infos, imgPath))