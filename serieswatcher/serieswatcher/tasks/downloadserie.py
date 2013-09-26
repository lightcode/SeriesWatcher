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


import os.path
from datetime import datetime
from PyQt4 import QtCore
from PyQt4.QtCore import qDebug
from sqlobject.sqlbuilder import AND
from serieswatcher.const import *
from serieswatcher.models import Serie, Episode
from serieswatcher.thetvdb import TheTVDBSerie


class DownloadSerieTask(QtCore.QObject):
    """Task to update serie from the online database."""
    serieUpdated = QtCore.pyqtSignal(int)
    serieUpdateStatus = QtCore.pyqtSignal(int, int, dict)

    def __init__(self, serieLocalID, parent=None):
        super(DownloadSerieTask, self).__init__(parent)
        self.serieLocalID = serieLocalID

    def run(self):
        serie = Serie.getSeries()[self.serieLocalID]
        self.serieUpdateStatus.emit(self.serieLocalID, 0, 
                                    {'title': serie.title})

        try:
            tvDb = TheTVDBSerie(serie.tvdbID, serie.lang)
        except Exception as e:
            qDebug("Error download" + str(e))
            return False
        
        # Info serie
        serieInfos = tvDb.infos_serie()
        bannerPath = '%s%s.jpg' % (SERIES_BANNERS, serie.uuid)
        tvDb.download_banner(bannerPath)
        
        if serieInfos is None:
            return
        
        serie.description = serieInfos['description']
        serie.firstAired = datetime.strptime(serieInfos['firstAired'],
                                             '%Y-%m-%d')
        serie.lastUpdated = int(serieInfos['lastUpdated'])
        self.serieUpdateStatus.emit(self.serieLocalID, 1, 
                                    {'title': serie.title})
        
        # Info episode
        episodesDb = {(e.season, e.episode) for e in serie.episodes}
        episodeList = set()
        for e in tvDb.episodes():
            number = (e['season'], e['episode'])
            episodeList.add(number)
            if e['firstAired']:
                firstAired = datetime.strptime(e['firstAired'], '%Y-%m-%d')
            else:
                firstAired = None
            if number in episodesDb:
                episode = list(Episode.select(
                    AND(Episode.q.season==int(e['season']),
                    Episode.q.episode==int(e['episode']),
                    Episode.q.serie==serie)))[0]
                episode.firstAired = firstAired
                episode.title = unicode(e['title'])
                episode.description = unicode(e['description'])
            else:
                Episode(
                    title = unicode(e['title']),
                    description = unicode(e['description']),
                    season = int(e['season']),
                    episode = int(e['episode']),
                    firstAired = firstAired,
                    serie = serie
                )
        
        toDelete = episodesDb - episodeList
        for season, episode in toDelete:
            Episode.deleteBy(serie=serie, season=season, episode=episode)
        
        # Create image path
        imgDir = SERIES_IMG + serie.uuid
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        # Miniature DL
        self.serieUpdateStatus.emit(
            self.serieLocalID, 2, {'title': serie.title})

        for i, nbImages in tvDb.download_miniatures(imgDir):
            self.serieUpdateStatus.emit(
                self.serieLocalID, 3,
                {'title': serie.title, 'nb': i, 'nbImages': nbImages})
        
        self.serieUpdated.emit(self.serieLocalID)
        serie.lastUpdate = datetime.now()
        serie.setLoaded(True)