#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


__all__ = ['EpisodesLoaderThread', 'SearchWorker', 'RefreshSeriesWorker',
           'SerieLoaderWorker', 'SyncDbWorker']

import time
import os.path
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtCore import qDebug
from sqlobject.dberrors import OperationalError
from serieswatcher.const import *
from serieswatcher.models import Serie, Episode
from serieswatcher.search import *
from serieswatcher.worker import Runnable
from serieswatcher.tasks.downloadserie import DownloadSerieTask


class SyncDbWorker(QtCore.QObject):
    """Worker to commit changes in a serie to the
    local database.
    """
    def __init__(self, parent=None):
        super(SyncDbWorker, self).__init__(parent)
        self.run()

    def run(self):
        for episode in Episode.select():
            try:
                episode.syncUpdate()
            except OperationalError as msg:
                qDebug('SQLObject Error : %s' % msg)
        QtCore.QTimer.singleShot(2000, self.run)


class RefreshSeriesWorker(QtCore.QObject):
    """Worker to update the serie from the online database."""
    serieUpdated = QtCore.pyqtSignal(int)
    serieUpdateStatus = QtCore.pyqtSignal(int, int, dict)

    def __init__(self, parent=None):
        super(RefreshSeriesWorker, self).__init__(parent)
        self.toRefresh = set()
        self.updateInProgress = set()
        self.threadPool = QtCore.QThreadPool()
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.run)
        self._timer.start(500)

    def run(self):
        for serieLocalID in self.toRefresh.copy():
            if serieLocalID in self.updateInProgress:
                continue
            task = DownloadSerieTask(serieLocalID)
            runnable = Runnable(task)
            runnable.task.serieUpdated.connect(self._serieUpdated)
            runnable.task.serieUpdateStatus.connect(self.serieUpdateStatus)
            self.threadPool.tryStart(runnable)
            self.toRefresh.discard(serieLocalID)
            self.updateInProgress.add(serieLocalID)
    
    def _serieUpdated(self, serieLocalID):
        self.updateInProgress.discard(serieLocalID)
        self.serieUpdated.emit(serieLocalID)

    def addSerie(self, serieLocalID):
        if serieLocalID not in self.updateInProgress:
            self.toRefresh.add(serieLocalID)


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


class SearchTask(QtCore.QObject):
    searchFinished = QtCore.pyqtSignal(list)

    def __init__(self, textSearch, parent=None):
        super(SearchTask, self).__init__(parent)
        self.textSearch = textSearch

    def run(self):
        textSearch = self.textSearch
        listEpisodes = []
        for e in self.episodes:
            score = 1000 if search(textSearch, split(e.title)) else 0
            score += search2(textSearch, split(e.description))
            if score > 0:
                listEpisodes.append((score, e))
        
        listEpisodes.sort(key=lambda e: e[0], reverse=True)
        listEpisodes = [e for score, e in listEpisodes]
        self.searchFinished.emit(listEpisodes)


class SearchWorker(QtCore.QObject):
    """Thread to search in the database."""
    searchFinished = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(SearchWorker, self).__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.run)
        self._timer.start(500)
        self.textSearch = ''
        self.lastTextSearch = ''
        self.threadPool = QtCore.QThreadPool()

    def run(self):
        if self.lastTextSearch != self.textSearch:
            self.lastTextSearch = self.textSearch

            task = SearchTask(self.lastTextSearch)
            runnable = Runnable(task)
            runnable.task.searchFinished.connect(self.searchFinished)
            runnable.task.episodes = self.parent().currentSerie.episodes
            self.threadPool.tryStart(runnable)

    def changeText(self, search):
        self.textSearch = search


class EpisodesLoaderThread(QtCore.QThread):
    """Thread to create miniature of the episode."""
    episodeLoaded = QtCore.pyqtSignal(int, int, Episode)
    episodes = []
    lastQuery = 0
    
    def run(self):
        for episode in self.episodes:
            qId, x, y, episode = episode
            if qId == self.lastQuery:
                self.episodeLoaded.emit(x, y, episode)
                self.msleep(15)
        self.episodes = []
    
    def newQuery(self):
        self.lastQuery += 1
    
    def addEpisode(self, x, y, episode):
        self.episodes.append((self.lastQuery, x, y, episode))