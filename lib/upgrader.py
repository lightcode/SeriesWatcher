#!/usr/bin/env python

from glob import iglob as glob
import os
import shutil


def mkdir(p):
    if not os.path.isdir(p):
        os.mkdir(p)

def move(src, dst):
    try:
        shutil.move(src, dst)
    except:
        pass

# Create new folder `user`
USR = 'user/'
mkdir(USR)


# Move the config file
OLD_CFG = 'series-watcher.cfg'
NEW_CFG = USR + 'series-watcher.cfg'
move(OLD_CFG, NEW_CFG)


# Create new folder `user/series`
SERIES = 'user/series/'
mkdir(SERIES)


# Move old `img` in new folder
IMG_OLD = 'database/img'
IMG_NEW = SERIES + 'img/'
move(IMG_OLD, IMG_NEW)


# Move old `banners` in new folder
BANNERS_OLD = 'database/banners'
BANNERS_NEW = SERIES + 'banners/'
move(BANNERS_OLD, BANNERS_NEW)


# Move old `lastVerif` in new folder
UPD_OLD = 'database/updates.pkl'
UPD_NEW = SERIES + 'updates.pkl'
move(UPD_OLD, UPD_NEW)


# Move old `lastVerif` in new folder
LV_OLD = 'database/lastVerif.txt'
LV_NEW = SERIES + 'lastVerif.txt'
move(LV_OLD, LV_NEW)


# Move old `view` in new folder
VIEW_OLD = 'database/view-*'
VIEW_NEW = SERIES + '/view/'
mkdir(VIEW_NEW)
for f in glob(VIEW_OLD):
    move(f, VIEW_NEW  + os.path.basename(f))

# Move old 'series DB' in new folder
SERIES_DB_OLD = 'database/*.pkl'
SERIES_DB_NEW = SERIES + 'database/'
mkdir(SERIES_DB_NEW)
for f in glob(SERIES_DB_OLD):
    move(f, SERIES_DB_NEW  + os.path.basename(f))


# Delete old database
try:
    shutil.rmtree('database')
except:
    pass