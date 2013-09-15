#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4 import QtCore
from serieswatcher.thetvdb import TheTVDB
from serieswatcher.config import Config


class MakeSearch(QtCore.QObject):
    searchFinished = QtCore.pyqtSignal(list)
    
    def __init__(self, userInput):
        super(MakeSearch, self).__init__()
        self._userInput = userInput
    
    def run(self):
        bdd = TheTVDB()
        languages = tuple(Config.config['languages'].split(','))
        seriesFound = []
        for lang in languages:
            seriesFound.extend(bdd.search_serie(self._userInput, lang))
        self.searchFinished.emit(seriesFound)