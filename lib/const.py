#!/usr/bin/env python
# -*- coding: utf-8 -*-

PATHS = ['USER', 'SERIES', 'SERIES_IMG', 'SERIES_BANNERS', 'CONFIG_FILE', 'LAST_VERIF_PATH']
__all__ = ['VERSION', 'PATHS', 'ERROR_PLAYER_LOAD', 'EXTENSIONS'] + PATHS

EXTENSIONS = ('.mp4', '.avi', '.wmv', '.flv', '.mkv')

VERSION = u'1.3 dev'
RELEASE_DATE = u'Août 2012'

USER = 'user/'
SERIES = 'user/series/'
SERIES_IMG = 'user/series/img/'
SERIES_BANNERS = 'user/series/banners/'

CONFIG_FILE = 'user/series-watcher.cfg'
LAST_VERIF_PATH = 'user/series/lastVerif.txt'
REFRESH_FILE = 'user/series/updates.pkl'



ERROR_PLAYER_LOAD = u"Le lecteur intégré ne peut pas être démarrer car" \
                  + u" la bibliothèque VLC ne s'est pas chargée" \
                  + u" correctement."