#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Matthieu GAIGNIÈRE
#
# This file is part of SeriesWatcher.
#
# SeriesWatcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# SeriesWatcher is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# SeriesWatcher. If not, see <http://www.gnu.org/licenses/>.


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
RELEASE_DATE = u'Octobre 2013'

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