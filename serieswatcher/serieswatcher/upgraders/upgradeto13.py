# -*- coding: utf-8 -*-

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
