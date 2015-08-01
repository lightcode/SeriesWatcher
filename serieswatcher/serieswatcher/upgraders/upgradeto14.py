# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.abspath('../..'))
from sqlobject import *

from serieswatcher.models import Serie, Episode
from serieswatcher.const import VERSION_FILE, SERIES_DATABASE

sqlhub.processConnection = connectionForURI('sqlite:///' + SERIES_DATABASE)

if not os.path.isfile(SERIES_DATABASE):
    Serie.createTable()
    Episode.createTable()

# Move the 1.3 database into 1.4
cols = [i.name for i in sqlhub.processConnection.columnsFromSchema(
        'episode', Episode)]
if 'lastUpdate' not in cols:
    Episode.sqlmeta.delColumn('lastUpdate')
    Episode.sqlmeta.addColumn(TimestampCol('lastUpdate'), changeSchema=True)

# Create file version
with open(VERSION_FILE, 'w+') as f:
    f.write('1.3.0')
