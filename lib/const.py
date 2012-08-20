#!/usr/bin/env python
# -*- coding: utf-8 -*-

PATHS = ['USER', 'SERIES', 'SERIES_IMG', 'SERIES_BANNERS',
'SERIES_VIEW', 'SERIES_DB', 'CONFIG_FILE', 'LAST_VERIF_PATH']
__all__ = ['VERSION', 'PATHS'] + PATHS

VERSION = u'1.3 dev'
RELEASE_DATE = u'Août 2012'

USER = 'user/'
SERIES = 'user/series/'
SERIES_IMG = 'user/series/img/'
SERIES_BANNERS = 'user/series/banners/'
SERIES_VIEW = 'user/series/view/'
SERIES_DB = 'user/series/database/'

CONFIG_FILE = 'user/series-watcher.cfg'
LAST_VERIF_PATH = 'user/series/lastVerif.txt'
REFRESH_FILE = 'user/series/updates.pkl'