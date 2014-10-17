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
from serieswatcher.config import Config
from serieswatcher.thetvdb import TheTVDB


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