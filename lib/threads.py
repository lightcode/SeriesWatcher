#!/usr/bin/env python

import cPickle as pickle
import os.path
import time
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from config import Config
from updatesfile import UpdatesFile
from search import search, decompose
from thetvdb import TheTVDBSerie

__all__ = ['EpisodesLoaderThread', 'SearchThread', 'RefreshSeriesThread',
           'CheckSerieUpdate']

class CheckSerieUpdate(QtCore.QThread):
    # Signals :
    updateRequired = QtCore.pyqtSignal(int)
    TIME_BETWEEN_UPDATE = 86400 # a day
    LATS_VERIF_PATH = 'database/lastVerif.txt'
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        UpdatesFile.loadUpdates()
    
    
    def getLastVerification(self):
        try:
            with open(self.LATS_VERIF_PATH, 'r') as f:
                return int(''.join(f.readlines()).strip())
        except IOError:
            return 0
        except ValueError:
            return 0
    
    
    def updateLastVerif(self):
        with open(self.LATS_VERIF_PATH, 'w+') as f:
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
                    self.updateLastVerif()
                    self.updateRequired.emit(localeID)



class RefreshSeriesThread(QtCore.QThread):
    # Signals :
    serieLoaded = QtCore.pyqtSignal(int)
    serieLoadStarted = QtCore.pyqtSignal('QString')
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.toRefresh = []
    
    
    def downloadConfiguration(self, serieLocalID):
        serieInfos = Config.series[serieLocalID]
        serieName, title, serieID = serieInfos[0], serieInfos[1], serieInfos[3]
        self.serieLoadStarted.emit(title)
        
        imgDir = 'database/img/%s' % serieName
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        tvDb = TheTVDBSerie(serieInfos)
        tvDb.downloadFullSerie()
        serieInfos = tvDb.getInfosSerie()
        episodeList = tvDb.getEpisodes(imgDir)
        
        serie = {'serieInfos': serieInfos, 'episodes': episodeList}
        pkl = 'database/%s.pkl' % serieName
        with open(pkl, 'wb+') as pklFile:
            pickle.dump(serie, pklFile)
        
        UpdatesFile.setLastUpdate(serieName, serieInfos['lastUpdated'])


    def addSerie(self, serieLocalID):
        self.toRefresh.append(serieLocalID)
    
    
    def run(self):
        while True:
            for serieLocalID in self.toRefresh[:]:
                self.downloadConfiguration(serieLocalID)
                self.serieLoaded.emit(serieLocalID)
                del self.toRefresh[0]
            self.msleep(10)



class SearchThread(QtCore.QThread):
    # Signals :
    searchFinished = QtCore.pyqtSignal(list)
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.textSearch = ""
    
    
    def run(self):
        textSearch = ""
        while True:
            if textSearch != self.textSearch:
                textSearch = self.textSearch
                listEpisodes = []
                for e in self.episodes:
                    if search(textSearch, decompose(e['title'])):
                        listEpisodes.append(e)
                self.searchFinished.emit(listEpisodes)
            self.msleep(10)
    
    
    def changeText(self, search, episodes):
        self.episodes = episodes
        self.textSearch = search



class EpisodesLoaderThread(QtCore.QThread):
    # Signals :
    episodeLoaded = QtCore.pyqtSignal(tuple)
    episodes = []
    lastQuery = 0
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
    
    
    def run(self):
        param = (Qt.KeepAspectRatio, Qt.SmoothTransformation)
        for qId, x, y, title, infos, imgPath in self.episodes:
            if qId == self.lastQuery:
                image = QtGui.QImage(imgPath)
                if image != QtGui.QImage():
                    image = image.scaled(120, 90, *param)
                self.episodeLoaded.emit((x, y, title, infos, image))
    
    
    def newQuery(self):
        self.lastQuery += 1
    
    
    def addEpisode(self, x, y, title, infos, imgPath):
        self.episodes.append((self.lastQuery, x, y, title, infos, imgPath))