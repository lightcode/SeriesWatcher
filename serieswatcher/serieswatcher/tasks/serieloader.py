#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4 import QtCore
from serieswatcher.models import Serie


class LoadSerieTask(QtCore.QObject):
    serieLoaded = QtCore.pyqtSignal(Serie)

    def __init__(self, serie, parent=None):
        super(LoadSerieTask, self).__init__(parent)
        self._serie = serie

    def run(self):
        serie = self._serie
        serie.clearEpisodeCache()
        serie.loadSerie()
        self.serieLoaded.emit(serie)