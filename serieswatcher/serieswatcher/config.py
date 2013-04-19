#!/usr/bin/env python

import os.path
import codecs
from configparser import SafeConfigParser
from const import *

class Config(object):
    '''Singleton to handle the configuration file and use
    it in the all program.'''
    _instance = None
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    
    @classmethod
    def setOption(cls, key, value):
        '''Set an option.'''
        cls.config[key] = value
    
    
    @classmethod
    def save(cls):
        '''Save the all configuration in the config file.'''
        config = SafeConfigParser()
        
        # Make option section
        config.add_section('options')
        for key, value in cls.config.iteritems():
            config.set('options', str(key), unicode(value))
        
        # Write the config
        with codecs.open(CONFIG_FILE, 'w+', encoding='utf-8') as f:
            config.write(f)
    
    
    @classmethod
    def loadConfig(cls):
        '''Load the all configuration from the config file.'''
        config = SafeConfigParser()
        if os.path.isfile(CONFIG_FILE):
            config.read_file(codecs.open(CONFIG_FILE, encoding='utf-8'))
        
        # The default config
        cls.config = {}
        cls.config['command_open'] = None
        cls.config['player'] = 1
        cls.config['debug'] = 0
        cls.config['random_duration'] = 0
        cls.config['sync_server'] = None
        cls.config['sync_user'] = None
        cls.config['sync_password'] = None
        
        # Load the options
        if config.has_section('options'):
            for key, value in config.items('options'):
                value = None if value == 'None' else value
                cls.config[key] = value



if __name__ == '__main__':
    Config.loadConfig()