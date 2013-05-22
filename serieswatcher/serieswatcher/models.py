#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import os.path
from glob import iglob
from uuid import uuid1
from itertools import chain
from datetime import datetime, date
from .const import *

sys.path.insert(0, os.path.abspath('..'))
from sqlobject import *

if not os.path.isdir(USER):
    os.mkdir(USER)
if not os.path.isdir(SERIES):
    os.mkdir(SERIES)


class Serie(SQLObject):
    """Model Serie."""
    PATTERN_FILE = re.compile(r'(\d+)\D(\d+)\+?(\d+)?')
    
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
    _cacheEpisodes = None
    episodesAvailable = {}
    
    class sqlmeta:
        defaultOrder = 'pos'
        lazyUpdate = True
    
    def isLoaded(self):
        """Return True if the serie is completly
        loaded from TVDB.
        """
        return self.loadCompleted
    
    def setLoaded(self, v):
        """Mark the serie as loaded."""
        self.loadCompleted = v
    
    @classmethod
    def deleteSeriesCache(cls):
        """Clear the cache."""
        cls._seriesCache = None
    
    @classmethod
    def getSeries(cls):
        """Returns the list of series."""
        if cls._seriesCache is None:
            cls._seriesCache = list(cls.select())
        return cls._seriesCache
    
    def loadAvailableList(self):
        """Load the serie's episodes in the path
        registred in the database.
        """
        self.episodesAvailable.clear()
        if not self.path and not os.path.isdir(self.path):
            return
        
        files = chain(iglob(self.path + '/*'), iglob(self.path + '/*/*'))
        for f in files:
            if os.path.splitext(f)[1] in EXTENSIONS:
                try:
                    numbers = re.search(self.PATTERN_FILE, os.path.basename(f)).groups()
                except AttributeError:
                    continue
                else:
                    episodeID = '%02d-%02d' % (int(numbers[0]), int(numbers[1]))
                    self.episodesAvailable[episodeID] = f
                    if numbers[2]:
                        episodeID = '%02d-%02d' % \
                                    (int(numbers[0]), int(numbers[2]))
                        self.episodesAvailable[episodeID] = f    
    
    def loadEpisodes(self):
        """Load episodes from the database and cache them."""
        nbEpisodeTotal = nbEpisodeNotAvailable = nbEpisodeAvailable = 0
        nbFavorites = nbNotView = nbView = 0
        nbSeason = 0
        today = date.today()
        for e in self.episodes:
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
                if e.season > 0 \
                        and e.firstAired and today > e.firstAired:
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
        """Load available episodes list and load episodes."""
        self.loadAvailableList()
        self.loadEpisodes()
    
    def _get_bannerPath(self):
        """Returns the path to the banner image."""
        return SERIES_BANNERS + '%s.jpg' % self.uuid
    
    def _get_episodes(self):
        """Returns the episode list."""
        if self._cacheEpisodes is None:
            self._cacheEpisodes = list(Episode.select(Episode.q.serieID==self.id))
        return self._cacheEpisodes


class Episode(SQLObject):
    """Model Episode."""
    title = UnicodeCol()
    description = UnicodeCol()
    season = IntCol()
    episode = IntCol()
    nbView = IntCol(default=0)
    lastView = TimestampCol()
    firstAired = DateCol(default=None)
    favorite = BoolCol(default=False)
    serie = ForeignKey('Serie')
    lastUpdate = TimestampCol()
    path = None
    
    class sqlmeta:
        defaultOrder = ('season', 'episode')
        lazyUpdate = True
    
    def userPlayed(self):
        """Set the date and add view on the episode."""
        if self.isAvailable():
            self.lastView = datetime.now()
            self.addView()
    
    def addView(self):
        """Add a view and refresh counters."""
        if self.isAvailable():
            if self.nbView == 0:
                self.serie.nbNotView -= 1
                self.serie.nbView += 1
            self.nbView += 1
            self._setLastUpdate()
    
    def setView(self):
        """Set the view number at 1 if the episode is not view."""
        if self.isAvailable() and self.nbView == 0:
            self.serie.nbNotView -= 1
            self.serie.nbView += 1
            self.nbView = 1
            self._setLastUpdate()
    
    def setNotView(self):
        """Unmark the episode as view."""
        if self.nbView > 0 and self.isAvailable():
            self.serie.nbNotView += 1
            self.serie.nbView -= 1
            self.lastView = None
            self.nbView = 0
            self._setLastUpdate()
    
    def isAvailable(self):
        """Return true if the episode is in the hard drive."""
        return self.path is not None
    
    def setFavorite(self):
        """Mark the episode as favorite."""
        if not self.favorite:
            self.favorite = True
            self.serie.nbFavorites += 1
            self._setLastUpdate()
    
    def setUnFavorite(self):
        """Unmark the episode as favorite."""
        if self.favorite:
            self.favorite = False
            self.serie.nbFavorites -= 1
            self._setLastUpdate()
    
    def _setLastUpdate(self):
        """Set the last view date at now."""
        self.lastUpdate = datetime.now()
    
    def _get_status(self):
        """Return the status of episode.
                1 -> Not in the hard drive
                2 -> In the hard drive but not view
                3 -> First aired date in the future
        """
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
        """Return the formated episode number."""
        return '%02d-%02d' % (self.season, self.episode)
    
    def _get_cover(self):
        """Return the path to the episode cover."""
        return u'%s%s/%s.jpg' % (SERIES_IMG, self.serie.uuid, self.number)


def databaseConnect():
    sqlhub.processConnection = connectionForURI('sqlite:///' + SERIES_DATABASE)
    
    if not os.path.isfile(SERIES_DATABASE):
        Serie.createTable()
        Episode.createTable()
    
#Serie._connection.debug = True
#Episode._connection.debug = True