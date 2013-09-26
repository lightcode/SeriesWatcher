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