#!/usr/bin/env python

import os
from const import VERSION_FILE, USER


def upgradeTo13():
    import upgraders.upgradeto13

def upgradeTo14():
    import upgraders.upgradeto14

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