#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


import os
import urllib
from xml.etree import cElementTree


class TheTVDB(object):
    """Class to manipulate the online TVDB Database."""
    API_KEY = 'F034441142EF8F93'
    URL_API = 'http://thetvdb.com/api/'
    URL_BANNER = 'http://thetvdb.com/banners/'
    
    def __init__(self):
        pass
    
    def search_serie(self, serie_name, lang_search='all'):
        """Search a serie on The TVDB by its name."""
        serie_name = unicode(serie_name).encode('utf8')
        url = self.URL_API + 'GetSeries.php?seriesname=%s&language=%s'
        url = url % (serie_name, lang_search)
        data = urllib.urlopen(url)
        root = cElementTree.parse(data).getroot()
        for serie in root.iter('Series'):
            lang = serie.find('language').text
            if lang_search == 'all' or lang_search == lang:
                serie_id = serie.find('seriesid').text
                title = serie.find('SeriesName').text
                yield (serie_id, title, lang)
    
    def get_languages(self):
        """Return the list of languages available on The TVDB."""
        language_list = []
        url = '%s%s/languages.xml' % (self.URL_API, self.API_KEY)
        data = urllib.urlopen(url)
        root = cElementTree.parse(data).getroot()
        for language in root.iter('Language'):
            language_list.append(language.find('abbreviation').text)
        return language_list


class TheTVDBSerie(TheTVDB):
    URL_SERIE = '%s%s/series/' % (TheTVDB.URL_API, TheTVDB.API_KEY)
    
    def __init__(self, tvdbid, lang):
        super(TheTVDBSerie, self).__init__()
        self.tvdbid, self.lang = tvdbid, lang
        self._root = None
        
        xmlurl = '%s%s/all/%s.xml' % (self.URL_SERIE, self.tvdbid, self.lang)
        xml = urllib.urlopen(xmlurl)
        self._root = cElementTree.parse(xml).getroot()
    
    def episodes(self):
        """Return the episodes list."""
        for episode in self._root.iter('Episode'):
            entry = {}
            entry['season'] = int(episode.find('SeasonNumber').text)
            entry['episode'] = int(episode.find('EpisodeNumber').text)
            entry['title'] = unicode(episode.find('EpisodeName').text)
            if entry['title'] == '':
                continue
            entry['description'] = unicode(episode.find('Overview').text)
            entry['firstAired'] = episode.find('FirstAired').text
            yield entry
    
    def infos_serie(self):
        """Return the serie informations."""
        if self._root is None:
            return
        
        infos = {}
        serie = self._root.find('Series')
        infos['firstAired'] = serie.find('FirstAired').text
        infos['description'] = unicode(serie.find('Overview').text)
        infos['lastUpdated'] = int(serie.find('lastupdated').text)
        return infos
    
    def last_update(self):
        """Return the timestamp of the last updated."""
        serie = self._root.find('Series')
        return int(serie.find('lastupdated').text)
    
    def download_banner(self, banner_path):
        """Download the banner in the hard drive."""
        serie = self._root.find('Series')
        banner = unicode(serie.find('banner').text)
        if banner != '' and not os.path.isfile(banner_path):
            urllib.urlretrieve(self.URL_BANNER + banner, banner_path)
    
    def download_miniatures(self, folder):
        """Downloads all images and yield a tuple with the number of
        the picture and the number of images.
        """
        miniaturesToDownload = []
        for episode in self._root.iter('Episode'):
            seasonNumber = int(episode.find('SeasonNumber').text)
            episodeNumber = int(episode.find('EpisodeNumber').text)
            imgpath = '%s/%02d-%02d.jpg' % (folder, seasonNumber, episodeNumber)
            urlmin = unicode(episode.find('filename').text)
            if urlmin and not os.path.isfile(imgpath):
                miniaturesToDownload.append((self.URL_BANNER + urlmin, imgpath))
        
        n = 0
        nbMiniatures = len(miniaturesToDownload)
        for urlmin, imgpath in miniaturesToDownload:
            urllib.urlretrieve(urlmin, imgpath)
            yield n, nbMiniatures
            n += 1


if __name__ == '__main__':
    tvdb = TheTVDB()
    tvdb.get_languages()