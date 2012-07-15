#!/usr/bin/env python

import cPickle as pickle
from datetime import datetime
import os
import os.path
import re

class Serie(object):
    EXTENSION = ('.mp4', '.avi', '.wmv', '.flv', '.mkv')
    downloadedEpisode = {}
    episodesViewed = set()
    episodes = []
    infos = {}
    
    def __init__(self, param):
        self.name, self.title, self.path, self.TVDBID, self.lang = param
        self.loadDownloadedList()
        self.loadEpisodesViewed()
    
    
    PATTERN_FILE = re.compile(r'(\d+)\D(\d+)\+?(\d+)?')
    def loadDownloadedList(self):
        self.downloadedEpisode = {}
        for t in os.walk(unicode(self.path)):
            files = [t[0] + '/' + f for f in t[2]]
            for f in files:
                if os.path.splitext(f)[1] in self.EXTENSION:
                    numbers = re.findall(self.PATTERN_FILE, os.path.basename(f))
                    if numbers:
                        numbers = numbers[0]
                        episodeID = '%02d-%02d' % (int(numbers[0]), int(numbers[1]))
                        self.downloadedEpisode[episodeID] = f
                        if numbers[2]:
                            episodeID = '%02d-%02d' % \
                                        (int(numbers[0]), int(numbers[2]))
                            self.downloadedEpisode[episodeID] = f
    
    
    def loadEpisodes(self):
        nbSeason = nbEpisodeDL = nbEpisodeNew = nbEpisodeTotal = 0
        now = datetime.now()
        for i, e in enumerate(self.episodes):
            number = e['number']
            nbSeason = max(nbSeason, e['season'])
            status = 0
            if e['season'] > 0:
                nbEpisodeTotal += 1
            if self.episodes[i]['title'][:3].lower() == 'tba':
                del self.episodes[i]
                i -= 1
            if 'firstAired' in e:
                firstAired = e['firstAired']
                if isinstance(firstAired, unicode):
                    firstAired = datetime.strptime(firstAired, '%Y-%m-%d')
                    self.episodes[i]['firstAired'] = firstAired
                    if now < firstAired:
                        status = 3
                        nbEpisodeNew += 1
            else:
                self.episodes[i]['firstAired'] = None
            if number in self.downloadedEpisode:
                self.episodes[i]['path'] = self.downloadedEpisode[number]
                status = 1
                if e['season'] > 0:
                    nbEpisodeDL += 1
                if e['number'] not in self.episodesViewed:
                    status = 2
            self.episodes[i]['status'] = status
        
        nbEpisodeTotal -= nbEpisodeNew
        self.infos['nbSeason'] = nbSeason
        self.infos['nbEpisodeNotDL'] = nbEpisodeTotal - nbEpisodeDL
        self.infos['nbEpisodeDL'] = nbEpisodeDL
        self.infos['nbEpisodeTotal'] = nbEpisodeTotal
    
    
    def loadSerie(self):
        pkl = 'database/%s.pkl' % self.name
        if os.path.isfile(pkl):
            serie = pickle.load(open(pkl, 'rb'))
            
            # Serie's episodes
            self.episodes = serie['episodes']
            self.loadEpisodes()
            
            # Serie's informations
            self.infos.update(serie['serieInfos'])
            self.infos['bannerPath'] = 'database/banners/%s.jpg' % self.name
            self.infos['firstAired'] = datetime.strptime(\
                                        self.infos['firstAired'], '%Y-%m-%d')
        else:
            raise ValueError()
    
    
    def __getitem__(cls, key):
        return cls.infos[key]
    
    
    def __setitem__(cls, key, value):
        cls.infos[key] = value
    
    
    # =========================
    #  Episode viewed manager
    # =========================
    def loadEpisodesViewed(self):
        self.episodesViewed = set()
        pkl = 'database/view-%s.pkl' % self.name
        try:
            with open(pkl, 'rb') as pklFile:
                self.episodesViewed = set(pickle.load(pklFile))
        except IOError:
            pass
    
    
    def episodesViewedSave(self):
        pkl = 'database/view-%s.pkl' % self.name
        try:
            with open(pkl, 'wb+') as pklFile:
                pickle.dump(self.episodesViewed, pklFile)
            self.loadEpisodes()
        except IOError:
            pass