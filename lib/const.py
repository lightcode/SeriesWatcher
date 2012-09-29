#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

PATHS = ['USER', 'SERIES', 'SERIES_IMG', 'SERIES_BANNERS', 'ART',
'SERIES_VIEW', 'SERIES_DB', 'CONFIG_FILE', 'LAST_VERIF_PATH']
__all__ = ['VERSION', 'PATHS', 'EXTENSIONS', 'VERSION_FILE'] + PATHS

EXTENSIONS = ('.mp4', '.avi', '.wmv', '.flv', '.mkv')

VERSION = u'1.3 bêta'
RELEASE_DATE = u'Septembre 2012'

ROOT = os.path.abspath('.') + '/'
ART = os.path.abspath('art/') + '/'

USER = ROOT + 'user/'
SERIES = ROOT + 'user/series/'
SERIES_IMG = ROOT + 'user/series/img/'
SERIES_BANNERS = ROOT + 'user/series/banners/'
SERIES_VIEW = ROOT + 'user/series/view/'
SERIES_DB = ROOT + 'user/series/database/'

CONFIG_FILE = ROOT + 'user/series-watcher.cfg'
LAST_VERIF_PATH = ROOT + 'user/series/lastVerif.txt'
REFRESH_FILE = ROOT + 'user/series/updates.pkl'
VERSION_FILE = ROOT + 'user/VERSION'

ERROR_PLAYER_LOAD = u"Le lecteur intégré ne peut pas être démarrer car" \
                  + u" la bibliothèque VLC ne s'est pas chargée" \
                  + u" correctement."