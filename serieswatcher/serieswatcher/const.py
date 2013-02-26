#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

PATHS = ['USER', 'SERIES', 'SERIES_IMG', 'SERIES_BANNERS', 'ART',
         'CONFIG_FILE', 'LAST_VERIF_PATH', 'SERIES_DATABASE']
__all__ = ['VERSION', 'TEXT_VERSION', 'PATHS', 'EXTENSIONS',
           'VERSION_FILE', 'ERROR_PLAYER_LOAD'] + PATHS

EXTENSIONS = ('.mp4', '.avi', '.wmv', '.flv', '.mkv')

TEXT_VERSION = u'1.4 dev'
VERSION = '1.4.0'
RELEASE_DATE = u'Février 2013'

ROOT = os.path.abspath('.') + '/'
ART = os.path.abspath('art/') + '/'

USER = ROOT + 'user/'
SERIES = USER + 'series/'
SERIES_IMG = SERIES + 'img/'
SERIES_BANNERS = SERIES + 'banners/'
SERIES_DATABASE = SERIES + 'series.sqlite'

CONFIG_FILE = USER + 'series-watcher.cfg'
LAST_VERIF_PATH = SERIES + 'lastVerif.txt'
REFRESH_FILE = SERIES + 'updates.pkl'
VERSION_FILE = SERIES + 'VERSION'

ERROR_PLAYER_LOAD = u"Le lecteur intégré ne peut pas démarrer car" \
                  + u" la bibliothèque VLC ne s'est pas chargée" \
                  + u" correctement."