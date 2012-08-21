#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
from uuid import uuid1
from const import *
from datetime import datetime
import re
from itertools import chain
from glob import iglob
from datetime import datetime

sys.path.append(os.path.abspath('.'))
from sqlobject import *

PATH_TO_DATABASE = os.path.abspath('user/series/series.sqlite')
sqlhub.processConnection = connectionForURI('sqlite:///' + PATH_TO_DATABASE)


class Serie(SQLObject):
    uuid = StringCol(default=lambda : str(uuid1()))
    title = UnicodeCol()
    description = UnicodeCol(default='')
    path = UnicodeCol()
    lang = UnicodeCol()
    tvdbID = IntCol()
    lastUpdate = TimestampCol()
    firstAired = DateCol(default=None)
    loadCompleted = BoolCol(default=False)
    episodes = MultipleJoin('Episode')
    
    nbSeason = 0
    nbEpisodeTotal = nbEpisodeNotAvailable = nbEpisodeAvailable = nbNotView = 0
    _seriesCache = None
    _episodesCache = None
    episodesAvailable = {}
    
    
    class sqlmeta:
        pass
        #lazyUpdate = True
    
    def isLoaded(self):
        return self.loadCompleted
    
    
    def setLoaded(self, v):
        self.loadCompleted = v
    
    
    @classmethod
    def getSeries(cls):
        if cls._seriesCache is None:
            cls._seriesCache = list(cls.select())
        return cls._seriesCache
    
    
    PATTERN_FILE = re.compile(r'(\d+)\D(\d+)\+?(\d+)?')
    def loadAvailableList(self):
        self.episodesAvailable = {}
        
        if not self.path:
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
        #return
        nbEpisodeTotal = nbEpisodeNotAvailable = nbEpisodeAvailable = nbNotView = 0
        nbSeason = 0
        now = datetime.now()
        for i, e in enumerate(self.episodes):
            number = e.number
            nbSeason = max(nbSeason, e.season)
            status = 0
            if e.season > 0:
                nbEpisodeTotal += 1
            if self.episodes[i].title[:3].lower() == 'tba':
                del self.episodes[i]
                i -= 1
            #if e.firstAired and now < e.firstAired:
            #    status = 3
            if number in self.episodesAvailable:
                self.episodes[i].path = self.episodesAvailable[number]
                status = 1
                if e.season > 0:
                    nbEpisodeAvailable += 1
                if e.nbView == 0:
                    status = 2
                    nbNotView += 1
            else:
                self.nbEpisodeNotAvailable += 1
            self.episodes[i].status = status
        
        self.nbSeason = nbSeason
        self.nbEpisodeTotal = nbEpisodeTotal
        self.nbEpisodeNotAvailable = nbEpisodeNotAvailable
        self.nbEpisodeAvailable = nbEpisodeAvailable
        self.nbNotView = nbNotView
    
    
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
    
    '''
    def __repr__(self):
        return u'<Serie %s>' % self.title'''



class Episode(SQLObject):
    title = UnicodeCol()
    description = UnicodeCol()
    season = IntCol()
    episode = IntCol()
    nbView = IntCol(default=0)
    lastView = TimestampCol()
    firstAired = DateCol(default=None)
    serie = ForeignKey('Serie')
    
    status = 0
    path = None
    
    
    class sqlmeta:
        defaultOrder = ('season', 'episode')
        lazyUpdate = False
    
    
    def userPlayed(self):
        if self.isAvailable():
            self.lastView = datetime.now()
            self.setView()
    
    
    def setView(self):
        if self.nbView == 0 and self.isAvailable():
            self.serie.nbNotView -= 1
            self.nbView += 1
    
    
    def isAvailable(self):
        return self.path is not None
    
    
    def setNotView(self):
        if self.nbView > 0 and self.isAvailable():
            self.serie.nbNotView += 1
            self.lastView = None
            self.nbView = 0
    
    
    def _get_number(self):
        return '%02d-%02d' % (self.season, self.episode)
    
    
    def _get_cover(self):
        return u'%s%s/%s.jpg' % (SERIES_IMG, self.serie.uuid, self.number)
    
    '''
    def __repr__(self):
        return u'<Episode (%d) [%02d-%02d] %s>' % (self.id, self.season, \
                                                  self.episode, self.title)'''


if not os.path.isfile(PATH_TO_DATABASE):
    Serie.createTable()
    Episode.createTable()


Serie._connection.debug = True
Episode._connection.debug = True
if __name__ == '__main__':
    pass

    def foo():
        episodes = Serie.get(3).episodes
        for e in episodes:
            yield e
    
    
    for e in foo():
        pass