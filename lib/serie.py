import glob
import cPickle as pickle
import os.path
import re

class Serie(object):
    EXTENSION = ('mp4', 'avi', 'wmv', 'flv', 'mkv')
    downloadedEpisode = {}
    episodesViewed = set()
    episodes = []
    infos = {}
    
    def __init__(self, param):
        self.name, self.title, self.path, self.tvDbId, self.lang = param
        self.loadDownloadedList()
        self.loadEpisodesViewed()
    
    
    def loadDownloadedList(self):
        pattern = re.compile(r'(\d+)\D(\d+)')
        fileList = glob.glob(self.path)
        for f in fileList:
            if os.path.basename(f).split('.')[-1] in self.EXTENSION:
                tst = re.search(pattern, os.path.basename(f))
                if tst:
                    episodeID = ['%02d' % int(x) for x in tst.groups()][0:2]
                    episodeID = '-'.join(episodeID)
                    self.downloadedEpisode[episodeID] = f
    
    
    def loadSerie(self):
        pkl = 'database/%s.pkl' % self.name
        if os.path.isfile(pkl):
            nbSeason = 0
            
            pklFile = open(pkl, 'rb')
            serie = pickle.load(pklFile)
            
            # Serie's episodes
            self.episodes = serie['episodes']
            for i, e in enumerate(self.episodes):
                number = e['number']
                nbSeason = max(nbSeason, e['season'])
                if number in self.downloadedEpisode:
                    self.episodes[i]['path'] = self.downloadedEpisode[number]
            
            # Serie's informations
            self.infos.update(serie['serieInfos'])
            self.infos['bannerPath'] = 'database/banners/%s.jpg' % self.name
            self.infos['nbSeason'] = nbSeason
        else:
            raise ValueError()
    
    
    def __getitem__(self, key):
        return self.infos[key]
    
    
    def __setitem__(self, key, value):
        self.infos[key] = value
    
    
    # =========================
    #  Episode viewed manager
    # =========================
    def loadEpisodesViewed(self):
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
        except IOError:
            pass