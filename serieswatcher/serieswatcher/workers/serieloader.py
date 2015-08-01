# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from serieswatcher.models import Serie
from serieswatcher.tasks.serieloader import LoadSerieTask
from serieswatcher.worker import Runnable


class SerieLoaderWorker(QtCore.QObject):
    """Worker to load the current serie from the local database."""
    serieLoaded = QtCore.pyqtSignal(Serie)
    lastCurrentSerieId = -1
    _forceReload = False

    def __init__(self, parent=None):
        super(SerieLoaderWorker, self).__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.run)
        self._timer.start(100)

        self.threadPool = QtCore.QThreadPool()

    def run(self):
        currentSerieId = self.parent().currentSerieId()
        if currentSerieId != self.lastCurrentSerieId or self._forceReload:
            try:
                serie = Serie.getSeries()[currentSerieId]
            except IndexError:
                pass
            else:
                task = LoadSerieTask(serie)
                runnable = Runnable(task)
                runnable.task.serieLoaded.connect(self.serieLoaded)
                self.threadPool.tryStart(runnable)
            self.lastCurrentSerieId = currentSerieId
            self._forceReload = False

    def forceReload(self):
        self._forceReload = True
