import glob
import cPickle as pickle
import os.path
import re

class Serie:
    ext = ('mp4', 'avi', 'wmv', 'flv', 'mkv')
    serie = {"episodes":[]}
    
    def __init__(self, param):
        self.name, self.title, self.path, self.tvDbId, self.lang = param
        self.loadDownloadedList()
        self.loadEpisodesViewed()
    
    
    def loadDownloadedList(self):
        self.downloadedEpisode = {}
        pattern = re.compile(r'(\d+)\D(\d+)')
        fileList = glob.glob(self.path)
        for f in fileList:
            if os.path.basename(f).split('.')[-1] in self.ext:
                tst = re.search(pattern, os.path.basename(f))
                if tst:
                    episodeID = ['%02d' % int(x) for x in tst.groups()][0:2]
                    episodeID = '-'.join(episodeID)
                    self.downloadedEpisode[episodeID] = f
    
    
    def loadSerie(self):
        pkl = 'tmp/%s.pkl' % self.tvDbId
        if os.path.isfile(pkl):
            pklFile = open(pkl, 'rb')
            serie = pickle.load(pklFile)
            for i, e in enumerate(serie['episodes']):
                number = e['number']
                if number in self.downloadedEpisode:
                    serie['episodes'][i]['path'] = self.downloadedEpisode[number]
            self.serie = serie
        else:
            raise ValueError()
    
    # =========================
    #  Episode viewed manager
    # =========================
    def loadEpisodesViewed(self):
        self.episodesViewed = set()
        pkl = 'tmp/dl-%s.pkl' % self.name
        try:
            with open(pkl, 'rb') as pklFile:
                self.episodesViewed = set(pickle.load(pklFile))
        except IOError:
            pass
    
    
    def episodesViewedSave(self):
        pkl = 'tmp/dl-%s.pkl' % self.name
        try:
            with open(pkl, 'wb+') as pklFile:
                pickle.dump(self.episodesViewed, pklFile)
        except IOError:
            pass