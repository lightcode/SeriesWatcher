import os
import urllib
import xml.dom.minidom

class TheTvDb:
    URL_ROOT = 'http://www.thetvdb.com/api/'
    
    def searchSearie(self, userInput):
        url = self.URL_ROOT + 'GetSeries.php?seriesname=%s&language=%s'
        url = url % (userInput, 'all')
        search = xml.dom.minidom.parse(urllib.urlopen(url))
        seriesFound = search.getElementsByTagName('Series')
        series = []
        for serie in seriesFound:
            serieId = self._getData(serie, 'seriesid')
            title = self._getData(serie, 'SeriesName')
            lang = self._getData(serie, 'language')
            series.append((serieId, title, lang))
        return series
    
    
    def _getData(self, elmt, tagName, default=''):
        try:
            return elmt.getElementsByTagName(tagName)[0].firstChild.nodeValue
        except AttributeError:
            return default



class TheTvDbSerie(TheTvDb):
    URL_BANNER = 'http://thetvdb.com/banners/'
    URL_ROOT = 'http://www.thetvdb.com/api/F034441142EF8F93/series/'
    
    def __init__(self, serieInfos):
        self.serieInfos = serieInfos
    
    
    def downloadFullSerie(self):
        tvDbId = self.serieInfos[3]
        lang = self.serieInfos[4]
        xmlFile = '%s%s/all/%s.xml' % (self.URL_ROOT, tvDbId, lang)
        self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlFile))
    
    
    def getLastUpdate(self):
        tvDbId = self.serieInfos[3]
        lang = self.serieInfos[4]
        xmlFile = '%s%s/%s.xml' % (self.URL_ROOT, tvDbId, lang)
        self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlFile))
        series = self.dom.getElementsByTagName('Series')[0]
        return int(self._getData(series, 'lastupdated'))
    
    
    def getInfosSerie(self):
        '''Return the serie informations'''
        infos = {}
        name = self.serieInfos[0]
        series = self.dom.getElementsByTagName('Series')[0]
        infos['firstAired'] = self._getData(series, 'FirstAired')
        infos['desc'] = self._getData(series, 'Overview')
        banner = self._getData(series, 'banner')
        infos['lastUpdated'] = int(self._getData(series, 'lastupdated'))
        bannerPath = 'database/banners/%s.jpg' % name
        if not os.path.isfile(bannerPath) and banner != '':
            try:
                o = urllib.urlopen(self.URL_BANNER + banner)
                img = o.read()
                with open(bannerPath, 'wb+') as f:
                    f.write(img)
            except:
                pass
        return infos
    
    
    def getEpisodes(self, imgDir):
        episodeList = []
        episodes = self.dom.getElementsByTagName('Episode')
        
        for e in episodes:
            entry = {}
            entry['season'] = int(self._getData(e, 'SeasonNumber', 0))
            if entry['season'] == 0:
                continue
            
            entry['episode'] = int(self._getData(e, 'EpisodeNumber', 0))
            entry['number'] = "%02d-%02d" % (entry['season'], entry['episode'])
            entry['title'] = self._getData(e, 'EpisodeName')
            if entry['title'] == '':
                continue
            entry['desc'] = self._getData(e, 'Overview')
            entry['path'] = None
            imgPath = '%s/%s.jpg' % (imgDir, entry['number'])
            filename = self._getData(e, 'filename', None)
            if not os.path.isfile(imgPath) and filename is not None:
                try:
                    o = urllib.urlopen(self.URL_BANNER + filename)
                    img = o.read()
                    with open(imgPath, 'wb+') as f:
                        f.write(img)
                except:
                    pass
            episodeList.append(entry)
        return episodeList