#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Matthieu GAIGNIÈRE
#
# This file is part of SeriesWatcher.
#
# SeriesWatcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# SeriesWatcher is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# SeriesWatcher. If not, see <http://www.gnu.org/licenses/>.


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