# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from serieswatcher.search import *


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
