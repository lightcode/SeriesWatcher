#!/usr/bin/env python

import cPickle as pickle
import glob
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
        for f in glob.iglob(unicode(self.path)):
            if os.path.splitext(f)[1] in self.EXTENSION:
                tst = re.search(self.PATTERN_FILE, os.path.basename(f))
                if tst:
                    numbers = tst.groups()
                    episodeID = '-'.join(['%02d' % int(x) for x in numbers[0:2]])
                    self.downloadedEpisode[episodeID] = f
                    if numbers[2]:
                        n = (numbers[0], numbers[2])
                        episodeID = '-'.join(['%02d' % int(x) for x in n])
                        self.downloadedEpisode[episodeID] = f
    
    
    def loadEpisodes(self):
        nbSeason = nbEpisodeDL = nbEpisodeTotal = 0
        for i, e in enumerate(self.episodes):
            number = e['number']
            nbSeason = max(nbSeason, e['season'])
            infos = 0
            nbEpisodeTotal += 1
            if number in self.downloadedEpisode:
                self.episodes[i]['path'] = self.downloadedEpisode[number]
                infos = 1
                nbEpisodeDL += 1
                if e['number'] not in self.episodesViewed:
                    infos = 2
            self.episodes[i]['infos'] = infos
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