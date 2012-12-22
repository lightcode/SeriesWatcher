#!/usr/bin/env python

import codecs
from configparser import SafeConfigParser
import cPickle as pickle
from datetime import datetime
from itertools import chain
from glob import iglob
import os
import re
import sys
from const import *

ROOT = os.path.abspath('.') + '/'
USER = ROOT + 'user.backup/'
SERIES = USER + 'series/'
SERIES_IMG = USER + 'series/img/'
SERIES_BANNERS = USER + 'series/banners/'
SERIES_VIEW = USER + 'series/view/'
SERIES_DB = USER + 'series/database/'
CONFIG_FILE = USER + 'series-watcher.cfg'
REFRESH_FILE = USER + 'series/updates.pkl'
VERSION_FILE = USER + 'VERSION'


class Config(object):
    _instance = None
    
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    
    @classmethod
    def addSerie(cls, *serie):
        serie = map(unicode, serie)
        serie[0], serie[3] = str(serie[0]), str(serie[3])
        cls.series.append(serie)
        cls.save()
    
    
    @classmethod
    def setOption(cls, key, value):
        cls.config[key] = value
    
    
    @classmethod
    def save(cls):
        config = SafeConfigParser()
        
        # Make option section
        config.add_section('options')
        for key, value in cls.config.iteritems():
            config.set('options', str(key), unicode(value))
        
        # Make the series sections
        for name, title, path, TVDBID, lang in cls.series:
            name = str(name)
            config.add_section(name)
            config.set(name, 'title', unicode(title))
            config.set(name, 'theTvDb', str(TVDBID))
            config.set(name, 'videos', unicode(path))
            config.set(name, 'lang', unicode(lang))
        
        # Write the config
        with codecs.open(CONFIG_FILE, 'w+', encoding='utf-8') as f:
            config.write(f)
    
    
    @classmethod
    def loadConfig(cls):
        config = SafeConfigParser()
        if os.path.isfile(CONFIG_FILE):
            config.read_file(codecs.open(CONFIG_FILE, encoding='utf-8'))
        
        # The default config
        cls.config = {}
        cls.config['command_open'] = None
        cls.config['player'] = 1
        cls.config['debug'] = 0
        
        # Load the options
        if config.has_section('options'):
            for key, value in config.items('options'):
                cls.config[key] = value
        
        # Load the series
        cls.series = []
        for section in config.sections():
            if section != 'options':
                title = config.get(section, 'title')
                videos = config.get(section, 'videos')
                theTvDb = config.getint(section, 'theTvDb')
                lang = config.get(section, 'lang')
                cls.series.append([section, title, videos, theTvDb, lang])



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
        
        if not self.path:
            return
        
        self.path = unicode(self.path)
        files = chain(iglob(self.path + '/*'), iglob(self.path + '/*/*'))
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
        pkl = '%s%s.pkl' % (SERIES_DB, self.name)
        if os.path.isfile(pkl):
            serie = pickle.load(open(pkl, 'rb'))
            
            # Serie's episodes
            self.episodes = serie['episodes']
            self.loadEpisodes()
            
            # Serie's informations
            self.infos.update(serie['serieInfos'])
            self.infos['bannerPath'] = '%s%s.jpg' % (SERIES_BANNERS, self.name)
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
        pkl = '%s/view-%s.pkl' % (SERIES_VIEW, self.name)
        try:
            with open(pkl, 'rb') as pklFile:
                self.episodesViewed = set(pickle.load(pklFile))
        except IOError:
            pass
    
    
    def episodesViewedSave(self):
        pkl = '%s/view-%s.pkl' % (SERIES_VIEW, self.name)
        try:
            with open(pkl, 'wb+') as pklFile:
                pickle.dump(self.episodesViewed, pklFile)
            self.loadEpisodes()
        except IOError:
            pass