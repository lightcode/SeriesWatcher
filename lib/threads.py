import os.path
import time
import cPickle as pickle
from config import Config
from search import search, decompose
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from theTvDb import TheTvDbSerie


class CheckSerieUpdate(QtCore.QThread):
    REFRESH_TIME = 7200
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        
        # Open the updater PKL file
        with open('updates.pkl', 'rwb+') as f:
            pickle.load(f)
    
    def run(self):
        while True:
            time.sleep(REFRESH_TIME)


class RefreshSeriesThread(QtCore.QThread):
    # Signals :
    serieLoaded = QtCore.pyqtSignal(int)
    serieLoadStarted = QtCore.pyqtSignal('QString')
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.toRefresh = []
    
    
    def downloadConfiguration(self, serieLocalID):
        serieInfos = Config.series[serieLocalID]
        title = serieInfos[1]
        serieID = serieInfos[3]
        self.serieLoadStarted.emit(title)
        
        imgDir = 'img/' + serieInfos[0]
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        tvDb = TheTvDbSerie(serieInfos)
        
        serieInfos = tvDb.getInfosSerie()
        episodeList = tvDb.getEpisodes(imgDir)
        
        pkl = 'tmp/%s.pkl' % serieID
        serie = {'serieInfos': serieInfos, 'episodes': episodeList}
        with open(pkl, 'wb+') as pklFile:
            pickle.dump(serie, pklFile)


    def addSerie(self, serieLocalID):
        self.toRefresh.append(serieLocalID)
    
    
    def run(self):
        while True:
            for serieLocalID in self.toRefresh[:]:
                self.downloadConfiguration(serieLocalID)
                self.serieLoaded.emit(serieLocalID)
                del self.toRefresh[0]
            time.sleep(0.01)



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
            time.sleep(0.01)
    
    
    def changeText(self, search, episodes):
        self.episodes = episodes
        self.textSearch = search



class EpisodesLoaderThread(QtCore.QThread):
    # Signals :
    episodeLoaded = QtCore.pyqtSignal(int, int, 'QString', int, 'QImage')
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.episodes = []
        self.lastLine = 0
        self.lastQuery = 0
    
    
    def run(self):
        self.episodeInLastLine = {}
        param = (Qt.KeepAspectRatio, Qt.SmoothTransformation)
        for qId, x, y, title, infos, imgPath in self.episodes:
            if qId == self.lastQuery:
                image = QtGui.QImage()
                if os.path.isfile(imgPath):
                    image.load(imgPath)
                    image = image.scaled(120, 90, *param)
                self.episodeLoaded.emit(x, y, title, infos, image)
                if self.lastLine == x:
                    if qId not in self.episodeInLastLine:
                        self.episodeInLastLine[qId] = 0
                    self.episodeInLastLine[qId] += 1
    
    
    def newQuery(self):
        self.lastQuery += 1
    
    
    def addEpisode(self, x, y, title, infos, imgPath):
        self.lastLine = max(self.lastLine, x)
        self.episodes.append((self.lastQuery, x, y, title, infos, imgPath))