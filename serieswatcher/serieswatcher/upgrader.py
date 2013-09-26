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
from const import VERSION_FILE, USER


def upgradeTo13():
    import serieswatcher.upgraders.upgradeto13

def upgradeTo14():
    import serieswatcher.upgraders.upgradeto14

def get_version():
    database_version = None
    if os.path.isfile(VERSION_FILE):
        with open(VERSION_FILE) as f:
            database_version = ''.join(f.readlines()).strip()
    elif os.path.isdir(USER):
        database_version = '1.2'
    else:
        database_version = None
    return database_version

if get_version() and get_version().startswith('1.2'):
    print '-- upgrade to 1.3 --'
    upgradeTo13()
if get_version() and get_version().startswith('1.3'):
    print '-- upgrade to 1.4 --'
    upgradeTo14()