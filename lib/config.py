#!/usr/bin/env python

import os.path
import codecs
import sys
from configparser import SafeConfigParser
from const import *

class Config(object):
    _instance = None
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    
    @classmethod
    def setOption(cls, key, value):
        cls.config[key] = value
    
    
    @classmethod
    def save(cls):
        config = SafeConfigParser()
        
        # Make option section
        config.add_section('options')
        for key, value in cls.config.iteritems():
            config.set('options', str(key), unicode(value))
        
        # Make the series sections
        for name, title, path, TVDBID, lang in cls.series:
            name = str(name)
            config.add_section(name)
            config.set(name, 'title', unicode(title))
            config.set(name, 'theTvDb', str(TVDBID))
            config.set(name, 'videos', unicode(path))
            config.set(name, 'lang', unicode(lang))
        
        # Write the config
        with codecs.open(CONFIG_FILE, 'w+', encoding='utf-8') as f:
            config.write(f)
    
    
    @classmethod
    def loadConfig(cls):
        config = SafeConfigParser()
        if os.path.isfile(CONFIG_FILE):
            config.read_file(codecs.open(CONFIG_FILE, encoding='utf-8'))
        
        # The default config
        cls.config = {}
        cls.config['command_open'] = None
        cls.config['player'] = 1
        cls.config['debug'] = 0
        
        # Load the options
        if config.has_section('options'):
            for key, value in config.items('options'):
                cls.config[key] = value



if __name__ == '__main__':
    Config.loadConfig()