#!/usr/bin/env python

import cPickle as pickle
import glob
import os.path
import re

class Serie(object):
    EXTENSION = ('mp4', 'avi', 'wmv', 'flv', 'mkv')
    downloadedEpisode = {}
    episodesViewed = set()
    episodes = []
    infos = {}
    
    def __init__(self, param):
        self.name, self.title, self.path, self.TVDBID, self.lang = param
        self.loadDownloadedList()
        self.loadEpisodesViewed()
    
    
    def loadDownloadedList(self):
        self.downloadedEpisode = {}
        pattern = re.compile(r'(\d+)\D(\d+)')
        fileList = glob.glob(unicode(self.path))
        for f in fileList:
            if os.path.basename(f).split('.')[-1] in self.EXTENSION:
                tst = re.search(pattern, os.path.basename(f))
                if tst:
                    episodeID = ['%02d' % int(x) for x in tst.groups()][0:2]
                    episodeID = '-'.join(episodeID)
                    self.downloadedEpisode[episodeID] = f
    
    
    def loadEpisodes(self):
        nbSeason = 0
        for i, e in enumerate(self.episodes):
            number = e['number']
            nbSeason = max(nbSeason, e['season'])
            infos = 0
            if number in self.downloadedEpisode:
                self.episodes[i]['path'] = self.downloadedEpisode[number]
                infos = 1
                if e['number'] not in self.episodesViewed:
                    infos = 2
            self.episodes[i]['infos'] = infos
        self.infos['nbSeason'] = nbSeason
    
    
    def loadSerie(self):
        pkl = 'database/%s.pkl' % self.name
        if os.path.isfile(pkl):            
            pklFile = open(pkl, 'rb')
            serie = pickle.load(pklFile)
            
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