#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
from uuid import uuid1
from const import *
from datetime import datetime, date
import re
from itertools import chain
from glob import iglob
from datetime import datetime

sys.path.append(os.path.abspath('.'))
from sqlobject import *

if not os.path.isdir(USER):
    os.mkdir(USER)
if not os.path.isdir(SERIES):
    os.mkdir(SERIES)
PATH_TO_DATABASE = os.path.abspath('user/series/series.sqlite')


class Serie(SQLObject):
    uuid = StringCol(default=lambda : str(uuid1()))
    title = UnicodeCol()
    description = UnicodeCol(default='')
    path = UnicodeCol()
    lang = UnicodeCol()
    tvdbID = IntCol()
    pos = IntCol(default=0)
    lastUpdate = TimestampCol()
    firstAired = DateCol(default=None)
    loadCompleted = BoolCol(default=False)
    episodes = MultipleJoin('Episode')
    
    nbSeason = 0
    nbEpisodeTotal = nbEpisodeNotAvailable = nbEpisodeAvailable = 0
    nbFavorites = nbNotView = nbView = 0
    _seriesCache = None
    _episodesCache = None
    episodesAvailable = {}
    
    
    class sqlmeta:
        defaultOrder = 'pos'
        lazyUpdate = True
    
    def isLoaded(self):
        return self.loadCompleted
    
    
    def setLoaded(self, v):
        self.loadCompleted = v
    
    
    @classmethod
    def deleteSeriesCache(cls):
        cls._seriesCache = None
    
    
    @classmethod
    def getSeries(cls):
        if cls._seriesCache is None:
            cls._seriesCache = list(cls.select())
        return cls._seriesCache
    
    
    PATTERN_FILE = re.compile(r'(\d+)\D(\d+)\+?(\d+)?')
    def loadAvailableList(self):
        self.episodesAvailable = {}
        
        if not self.path and not os.path.isdir(self.path):
            return
        
        files = chain(iglob(self.path + '/*'), iglob(self.path + '/*/*'))
        for f in files:
            if os.path.splitext(f)[1] in EXTENSIONS:
                numbers = re.findall(self.PATTERN_FILE, os.path.basename(f))
                if numbers:
                    numbers = numbers[0]
                    episodeID = '%02d-%02d' % (int(numbers[0]), int(numbers[1]))
                    self.episodesAvailable[episodeID] = f
                    if numbers[2]:
                        episodeID = '%02d-%02d' % \
                                    (int(numbers[0]), int(numbers[2]))
                        self.episodesAvailable[episodeID] = f    
    
    
    def loadEpisodes(self):
        self._cacheEpisodes = None
        nbEpisodeTotal = nbEpisodeNotAvailable = nbEpisodeAvailable = 0
        nbFavorites = nbNotView = nbView = 0
        nbSeason = 0
        for i, e in enumerate(self.episodes):
            number = e.number
            nbSeason = max(nbSeason, e.season)
            if e.season > 0:
                nbEpisodeTotal += 1
            if number in self.episodesAvailable:
                e.path = self.episodesAvailable[number]
                if e.season > 0:
                    nbEpisodeAvailable += 1
                if e.nbView == 0:
                    nbNotView += 1
                else:
                    nbView += 1
            else:
                if e.season > 0:
                    nbEpisodeNotAvailable += 1
            if e.favorite:
                nbFavorites += 1
        
        self.nbSeason = nbSeason
        self.nbFavorites = nbFavorites
        self.nbEpisodeTotal = nbEpisodeTotal
        self.nbEpisodeNotAvailable = nbEpisodeNotAvailable
        self.nbEpisodeAvailable = nbEpisodeAvailable
        self.nbNotView = nbNotView
        self.nbView = nbView
    
    
    def loadSerie(self):
        self.loadAvailableList()
        self.loadEpisodes()
    
    
    def _get_bannerPath(self):
        return SERIES_BANNERS + '%s.jpg' % self.uuid
    
    
    _cacheEpisodes = None
    def _get_episodes(self):
        if self._cacheEpisodes is None:
            self._cacheEpisodes = list(Episode.select(Episode.q.serieID==self.id))
        return self._cacheEpisodes



class Episode(SQLObject):
    title = UnicodeCol()
    description = UnicodeCol()
    season = IntCol()
    episode = IntCol()
    nbView = IntCol(default=0)
    lastView = TimestampCol()
    firstAired = DateCol(default=None)
    favorite = BoolCol(default=False)
    serie = ForeignKey('Serie')
    path = None
    
    
    class sqlmeta:
        defaultOrder = ('season', 'episode')
        lazyUpdate = True
    
    
    def userPlayed(self):
        if self.isAvailable():
            self.lastView = datetime.now()
            self.setView()
    
    
    def setView(self):
        if self.isAvailable():
            if self.nbView == 0:
                self.serie.nbNotView -= 1
                self.serie.nbView += 1
            self.nbView += 1
    
    
    def setNotView(self):
        if self.nbView > 0 and self.isAvailable():
            self.serie.nbNotView += 1
            self.serie.nbView -= 1
            self.lastView = None
            self.nbView = 0
    
    
    def isAvailable(self):
        return self.path is not None
    
    
    def setFavorite(self):
        if not self.favorite:
            self.favorite = True
            self.serie.nbFavorites += 1
    
    
    def setUnFavorite(self):
        if self.favorite:
            self.favorite = False
            self.serie.nbFavorites -= 1
    
    
    def _get_status(self):
        status = 0
        if self.path is not None:
            status = 1
            if self.nbView == 0:
                status = 2
        now = date.today()
        if self.firstAired and now < self.firstAired:
            status = 3
        return status
    
    
    def _get_number(self):
        return '%02d-%02d' % (self.season, self.episode)
    
    
    def _get_cover(self):
        return u'%s%s/%s.jpg' % (SERIES_IMG, self.serie.uuid, self.number)


sqlhub.processConnection = connectionForURI('sqlite:///' + PATH_TO_DATABASE)
if not os.path.isfile(PATH_TO_DATABASE):
    Serie.createTable()
    Episode.createTable()


#Serie._connection.debug = True
#Episode._connection.debug = True
if __name__ == '__main__':
    pass
    print Serie.get(3).episodes