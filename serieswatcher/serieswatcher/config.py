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


import codecs
import os.path
from configparser import SafeConfigParser
from serieswatcher.const import *


class Config(object):
    """Singleton to handle the configuration file and use
    it in the all program.
    """
    
    config = {}
    _instance = None
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    @classmethod
    def setOption(cls, key, value):
        """Set an option."""
        cls.config[key] = value
    
    @classmethod
    def save(cls):
        """Save the all configuration in the config file."""
        config = SafeConfigParser()
        
        # Make option section
        config.add_section('options')
        for key, value in cls.config.iteritems():
            config.set('options', str(key), unicode(value))
        
        # Write the config
        with codecs.open(CONFIG_FILE, 'w+', encoding='utf8') as f:
            config.write(f)
    
    @classmethod
    def loadConfig(cls):
        """Load the all configuration from the config file."""
        config = SafeConfigParser()
        if os.path.isfile(CONFIG_FILE):
            with codecs.open(CONFIG_FILE, encoding='utf8') as file_:
                config.read_file(file_)
        
        # The default config
        cls.config = {}
        cls.config['command_open'] = None
        cls.config['player'] = 2
        cls.config['debug'] = 0
        cls.config['random_duration'] = 0
        cls.config['languages'] = 'fr,en'
        
        # Load the options
        if config.has_section('options'):
            for key, value in config.items('options'):
                value = None if value == 'None' else value
                cls.config[key] = value