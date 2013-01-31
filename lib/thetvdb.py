#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import xml.dom.minidom
from const import SERIES_BANNERS

class TheTVDB:
    URL_ROOT = 'http://www.thetvdb.com/api/'
    
    def searchSearie(self, userInput):
        userInput = unicode(userInput).encode('utf8')
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



class TheTVDBSerie(TheTVDB):
    URL_BANNER = 'http://thetvdb.com/banners/'
    URL_ROOT = 'http://www.thetvdb.com/api/F034441142EF8F93/series/'
    miniatureToDL = []
    dom = None
    
    def __init__(self, serie):
        # This is to adapt this API for the new database
        self.serieInfos = (serie.uuid, None, None, serie.tvdbID, serie.lang)
    
    
    def downloadFullSerie(self):
        TVDBID = self.serieInfos[3]
        lang = self.serieInfos[4]
        xmlFile = '%s%s/all/%s.xml' % (self.URL_ROOT, TVDBID, lang)
        try:
            self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlFile))
        except IOError:
            print 'Download serie informations error.'
    
    
    def getLastUpdate(self):
        TVDBID = self.serieInfos[3]
        lang = self.serieInfos[4]
        xmlFile = '%s%s/%s.xml' % (self.URL_ROOT, TVDBID, lang)
        try:
            self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlFile))
        except IOError:
            print 'Download serie informations error.'
        else:
            series = self.dom.getElementsByTagName('Series')[0]
            return int(self._getData(series, 'lastupdated'))
    
    
    def getInfosSerie(self):
        '''Return the serie informations'''
        if self.dom is None:
            return
        
        infos = {}
        name = self.serieInfos[0]
        series = self.dom.getElementsByTagName('Series')[0]
        infos['firstAired'] = self._getData(series, 'FirstAired')
        infos['description'] = self._getData(series, 'Overview')
        banner = self._getData(series, 'banner')
        infos['lastUpdated'] = int(self._getData(series, 'lastupdated'))
        bannerPath = '%s%s.jpg' % (SERIES_BANNERS, name)
        if banner != '' and not os.path.isfile(bannerPath):
            try:
                o = urllib.urlopen(self.URL_BANNER + banner)
                img = o.read()
                with open(bannerPath, 'wb+') as f:
                    f.write(img)
            except:
                pass
        return infos
    
    
    def downloadAllImg(self):
        for imgPath, urlMin in self.miniatureToDL:
            if not os.path.isfile(imgPath):
                try:
                    o = urllib.urlopen(self.URL_BANNER + urlMin)
                    img = o.read()
                    with open(imgPath, 'wb+') as f:
                        f.write(img)
                except:
                    print 'Error download episode cover.'
    
    
    def getEpisodes(self, imgDir):
        self.miniatureToDL = []
        episodeList = []
        episodes = self.dom.getElementsByTagName('Episode')
        
        for e in episodes:
            entry = {}
            entry['season'] = int(self._getData(e, 'SeasonNumber', 0))
            entry['episode'] = int(self._getData(e, 'EpisodeNumber', 0))
            entry['number'] = "%02d-%02d" % (entry['season'], entry['episode'])
            entry['title'] = self._getData(e, 'EpisodeName')
            if entry['title'] == '':
                continue
            entry['desc'] = self._getData(e, 'Overview')
            entry['firstAired'] = self._getData(e, 'FirstAired', None)
            # Miniature
            urlMin = self._getData(e, 'filename', None)
            if urlMin is not None:
                imgPath = '%s/%s.jpg' % (imgDir, entry['number'])
                self.miniatureToDL.append((imgPath, urlMin))
            episodeList.append(entry)
        return episodeList