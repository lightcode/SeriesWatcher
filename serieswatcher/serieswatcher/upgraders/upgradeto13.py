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


import os
import shutil
from serieswatcher.const import VERSION_FILE
from serieswatcher.models import Serie, Episode
from upgraders.compatserie import Config as OldConfig
from upgraders.compatserie import Serie as OldSerie

# 1.2 to 1.3 upgrader

def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

olduser = 'user.backup/'
if os.path.isdir(olduser):
    shutil.rmtree(olduser)

try:
    shutil.move('user/', olduser)
except:
    pass

mkdir('user')
oldseries = olduser + 'series/'

if os.path.isfile(olduser + 'series-watcher.cfg'):
    shutil.copy(olduser + 'series-watcher.cfg', 'user/series-watcher.cfg')

mkdir('user/series')
mkdir('user/series/banners')
mkdir('user/series/img')

# Create new DB file
if not os.path.isfile('user/series/series.sqlite'):
    Serie.createTable()
    Episode.createTable()


OldConfig.loadConfig()
for pos, oldserieconfig in enumerate(OldConfig.series):
    uuid, title, path, thetvdbid, lang = oldserieconfig
    # Move old directory
    srcimg = 'user.backup/series/img/%s' % uuid
    dstimg = 'user/series/img/%s' % uuid
    if os.path.isdir(srcimg) and not os.path.isdir(dstimg):
        shutil.copytree(srcimg, dstimg)
    srcbanner = 'user.backup/series/banners/%s.jpg' % uuid
    dstbanner = 'user/series/banners/%s.jpg' % uuid
    if os.path.isfile(srcbanner) and not os.path.isfile(dstbanner):
        shutil.copy(srcbanner, dstbanner)
    
    oserie = OldSerie(oldserieconfig)
    oserie.loadSerie()
    oserie.loadEpisodes()
    
    newserie = Serie(uuid=uuid, title=title, path=path, lang=lang,
          tvdbID=thetvdbid, pos=pos)
    
    # Import episodes
    for episode in oserie.episodes:
        nbView = 0
        if episode['status'] == 1:
            nbView = 1
        
        Episode(title=episode['title'], description=episode['desc'],
                season=episode['season'], episode=episode['episode'],
                nbView=nbView, firstAired=episode['firstAired'],
                serie=newserie)
    
    # Create file version
    with open(VERSION_FILE, 'w+') as f:
        f.write('1.3.0')