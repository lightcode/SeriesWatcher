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