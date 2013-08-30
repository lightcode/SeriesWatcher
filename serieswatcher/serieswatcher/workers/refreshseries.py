#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4 import QtCore
from serieswatcher.tasks.downloadserie import DownloadSerieTask
from serieswatcher.worker import Runnable


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