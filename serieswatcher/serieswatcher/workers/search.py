# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from serieswatcher.tasks.search import SearchTask
from serieswatcher.worker import Runnable


class SearchWorker(QtCore.QObject):
    """Worker to search in the database."""
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
