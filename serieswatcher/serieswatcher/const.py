# -*- coding: utf-8 -*-

__all__ = (
    'ART', 'CONFIG_FILE', 'ERROR_PLAYER_LOAD', 'EXTENSIONS', 'ICONS',
    'LAST_VERIF_PATH', 'SERIES', 'SERIES_BANNERS', 'SERIES_DATABASE',
    'SERIES_IMG', 'TEXT_VERSION', 'THEME', 'USER', 'VERSION',
    'VERSION_FILE'
)


import os.path


EXTENSIONS = ('.mp4', '.avi', '.wmv', '.flv', '.mkv')

TEXT_VERSION = u'1.5.1'
VERSION = '1.4.0'
RELEASE_DATE = u'Juillet 2015'

ROOT = os.path.abspath('.') + '/'
ART = os.path.abspath('art/') + '/'

USER = ROOT + 'user/'
SERIES = USER + 'series/'
SERIES_IMG = SERIES + 'img/'
SERIES_BANNERS = SERIES + 'banners/'
SERIES_DATABASE = SERIES + 'series.sqlite'

THEMES = ROOT + 'themes/'
THEME = THEMES + 'default/'
ICONS = THEME + 'icons/'

CONFIG_FILE = USER + 'series-watcher.cfg'
LAST_VERIF_PATH = SERIES + 'lastVerif.txt'
VERSION_FILE = SERIES + 'VERSION'

ERROR_PLAYER_LOAD = (u"Le lecteur intégré ne peut pas démarrer car la "
                     u"bibliothèque VLC ne s'est pas chargée correctement.")
