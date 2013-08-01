#!/usr/bin/env python

import codecs
import os.path
from configparser import SafeConfigParser
from .const import *


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