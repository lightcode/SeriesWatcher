#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import xml.dom.minidom

class TheTVDB:
    URL_API = 'http://thetvdb.com/api/'
    URL_BANNER = 'http://thetvdb.com/banners/'
    
    def searchSearie(self, serieName):
        """Search a serie on TVDB by its name."""
        serieName = unicode(serieName).encode('utf8')
        url = self.URL_API + 'GetSeries.php?seriesname=%s&language=%s'
        url = url % (serieName, 'all')
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
        """Shortcut to get value in a node."""
        try:
            return elmt.getElementsByTagName(tagName)[0].firstChild.nodeValue
        except AttributeError:
            return default



class TheTVDBSerie(TheTVDB):
    API_KEY = 'F034441142EF8F93'
    URL_SERIE = '%s%s/series/' % (TheTVDB.URL_API, API_KEY)
    miniatureToDL = []
    dom = None
    
    def __init__(self, tvdbID, lang):
        self.tvdbID, self.lang = tvdbID, lang
    
    
    def downloadFullSerie(self):
        """Download the full serie in this object."""
        xmlFile = '%s%s/all/%s.xml' % (self.URL_SERIE, self.tvdbID, self.lang)
        try:
            self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlFile))
        except IOError:
            print 'Download serie informations error.'
    
    
    def getLastUpdated(self):
        """Return the timestamp of the last updated."""
        xmlFile = '%s%s/%s.xml' % (self.URL_SERIE, self.tvdbID, self.lang)
        try:
            self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlFile))
        except IOError:
            print 'Download serie informations error.'
        else:
            series = self.dom.getElementsByTagName('Series')[0]
            return int(self._getData(series, 'lastupdated'))
    
    
    def getInfosSerie(self):
        """Return the serie informations."""
        if self.dom is None:
            return
        infos = {}
        series = self.dom.getElementsByTagName('Series')[0]
        infos['firstAired'] = self._getData(series, 'FirstAired')
        infos['description'] = self._getData(series, 'Overview')
        infos['lastUpdated'] = int(self._getData(series, 'lastupdated'))
        return infos
    
    
    def downloadBanner(self, bannerPath):
        """Download the banner in the hard drive."""
        series = self.dom.getElementsByTagName('Series')[0]
        banner = self._getData(series, 'banner')
        if banner != '' and not os.path.isfile(bannerPath):
            try:
                img = urllib.urlopen(self.URL_BANNER + banner).read()
                with open(bannerPath, 'wb+') as f:
                    f.write(img)
            except:
                pass
    
    
    def downloadAllImg(self):
        for imgPath, urlMin in self.miniatureToDL:
            if not os.path.isfile(imgPath):
                try:
                    img = urllib.urlopen(self.URL_BANNER + urlMin).read()
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