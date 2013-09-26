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