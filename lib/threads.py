#!/usr/bin/env python

import cPickle as pickle
import os.path
import time
import xml
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from config import Config
from updatesfile import UpdatesFile
from search import *
from thetvdb import TheTVDBSerie
from serie import Serie
from const import *

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
            for localeID, serie in enumerate(Config.series):
                serieName, TVDBID = serie[0], serie[3]
                localTime = UpdatesFile.getLastUpdate(serieName)
                
                tvDb = TheTVDBSerie(serie)
                remoteTime = tvDb.getLastUpdate()
                
                if localTime < remoteTime:
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
        serieInfos = Config.series[serieLocalID]
        serieName, title, serieID = serieInfos[0], serieInfos[1], serieInfos[3]
        self.serieUpdateStatus.emit(serieLocalID, title, 201)
        
        imgDir = SERIES_IMG + serieName
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        tvDb = TheTVDBSerie(serieInfos)
        try:
            tvDb.downloadFullSerie()
        except xml.parsers.expat.ExpatError:
            return False
        
        pkl = '%s%s.pkl' % (SERIES_DB, serieName)
        
        # Info serie
        serieInfos = tvDb.getInfosSerie()
        serie = {'serieInfos': serieInfos, 'episodes': []}
        with open(pkl, 'wb+') as pklFile:
            pickle.dump(serie, pklFile)
        self.serieUpdateStatus.emit(serieLocalID, title, 202)
        
        # Info episode
        episodeList = tvDb.getEpisodes()
        serie = {'serieInfos': serieInfos, 'episodes': episodeList}
        with open(pkl, 'wb+') as pklFile:
            pickle.dump(serie, pklFile)
        self.serieUpdateStatus.emit(serieLocalID, title, 203)
        
        # Miniature DL
        tvDb.downloadAllImg(imgDir)
        self.serieUpdated.emit(serieLocalID)
        
        UpdatesFile.setLastUpdate(serieName, serieInfos['lastUpdated'])


    def addSerie(self, serieLocalID):
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
    
    lastCurrentSerieID = -1
    _forceReload = False
    
    def forceReload(self):
        self._forceReload = True
    
    
    def run(self):
        while True:
            currentSerieID = self.parent().currentSerieID
            if currentSerieID != self.lastCurrentSerieID or self._forceReload:
                try:
                    self.serieLoaded.emit(Serie(Config.series[currentSerieID]))
                except IndexError:
                    pass
                self.lastCurrentSerieID = currentSerieID
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
            score = 1000 if search(textSearch, decompose(e['title'])) else 0
            score += search2(textSearch, decompose(e['desc']))
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