#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import xml.dom.minidom

def _get_data(elmt, tag_name, default=''):
    """Shortcut to get value in a node."""
    try:
        return elmt.getElementsByTagName(tag_name)[0].firstChild.nodeValue
    except AttributeError:
        return default


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
        search = xml.dom.minidom.parse(data)
        series_found = search.getElementsByTagName('Series')
        series = []
        for serie in series_found:
            lang = _get_data(serie, 'language')
            if lang_search == 'all' or lang_search == lang:
                serie_id = _get_data(serie, 'seriesid')
                title = _get_data(serie, 'SeriesName')
                series.append((serie_id, title, lang))
        return series
    
    def get_languages(self):
        """Return the list of languages available on The TVDB."""
        language_list = []
        xmlfile = '%s%s/languages.xml' % (self.URL_API, self.API_KEY)
        try:
            dom = xml.dom.minidom.parse(urllib.urlopen(xmlfile))
        except IOError:
            print "Can't find languages."
        else:
            languages = dom.getElementsByTagName('Languages')[0]
            languages = languages.getElementsByTagName('Language')
            for language in languages:
                language_list.append(_get_data(language, 'abbreviation'))
        return language_list


class TheTVDBSerie(TheTVDB):
    URL_SERIE = '%s%s/series/' % (TheTVDB.URL_API, TheTVDB.API_KEY)
    
    def __init__(self, tvdbid, lang):
        super(TheTVDBSerie, self).__init__()
        self.tvdbid, self.lang = tvdbid, lang
        self.miniatureToDL = []
        self.dom = None
    
    def download_serie(self):
        """Download the full serie in this object."""
        xmlfile = '%s%s/all/%s.xml' % (self.URL_SERIE, self.tvdbid, self.lang)
        try:
            self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlfile))
        except IOError:
            print 'Download serie informations error.'
    
    def last_update(self):
        """Return the timestamp of the last updated."""
        xmlfile = '%s%s/%s.xml' % (self.URL_SERIE, self.tvdbid, self.lang)
        try:
            self.dom = xml.dom.minidom.parse(urllib.urlopen(xmlfile))
        except IOError:
            print 'Download serie informations error.'
        else:
            series = self.dom.getElementsByTagName('Series')[0]
            return int(_get_data(series, 'lastupdated'))
    
    def infos_serie(self):
        """Return the serie informations."""
        if self.dom is None:
            return
        infos = {}
        series = self.dom.getElementsByTagName('Series')[0]
        infos['firstAired'] = _get_data(series, 'FirstAired')
        infos['description'] = _get_data(series, 'Overview')
        infos['lastUpdated'] = int(_get_data(series, 'lastupdated'))
        return infos
    
    def download_banner(self, banner_path):
        """Download the banner in the hard drive."""
        series = self.dom.getElementsByTagName('Series')[0]
        banner = _get_data(series, 'banner')
        if banner != '' and not os.path.isfile(banner_path):
            try:
                img = urllib.urlopen(self.URL_BANNER + banner).read()
                with open(banner_path, 'wb+') as file_:
                    file_.write(img)
            except:
                pass
    
    def download_miniatures(self):
        """Downloads all images and yield a tuple with the number of
        the picture and the number of images.
        """
        nbimages = len(self.miniatureToDL)
        i = 0
        for imgpath, urlmin in self.miniatureToDL:
            if not os.path.isfile(imgpath):
                try:
                    img = urllib.urlopen(self.URL_BANNER + urlmin).read()
                    with open(imgpath, 'wb+') as file_:
                        file_.write(img)
                except:
                    print 'Error download episode cover.'
            i += 1
            yield (i, nbimages)
    
    def episodes(self, imgDir):
        """Return the episodes list."""
        self.miniatureToDL = []
        episodes = self.dom.getElementsByTagName('Episode')
        for e in episodes:
            entry = {}
            entry['season'] = int(_get_data(e, 'SeasonNumber', 0))
            entry['episode'] = int(_get_data(e, 'EpisodeNumber', 0))
            entry['number'] = "%02d-%02d" % (entry['season'], entry['episode'])
            entry['title'] = _get_data(e, 'EpisodeName')
            if entry['title'] == '':
                continue
            entry['desc'] = _get_data(e, 'Overview')
            entry['firstAired'] = _get_data(e, 'FirstAired', None)
            # Miniature
            urlmin = _get_data(e, 'filename', None)
            if urlmin is not None:
                imgpath = '%s/%s.jpg' % (imgDir, entry['number'])
                self.miniatureToDL.append((imgpath, urlmin))
            yield entry