#!/usr/bin/env python

from configparser import SafeConfigParser
import os.path
import codecs

class Config(object):
    _instance = None
    CONFIG_FILE = 'series-watcher.cfg'
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    
    @classmethod
    def addSerie(cls, *serie):
        serie = map(unicode, serie)
        serie[0], serie[3] = str(serie[0]), str(serie[3])
        cls.series.append(serie)
        cls.save()
    
    
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
        for name, title, path, tvDbId, lang in cls.series:
            name = str(name)
            config.add_section(name)
            config.set(name, 'title', unicode(title))
            config.set(name, 'theTvDb', str(tvDbId))
            config.set(name, 'videos', unicode(path))
            config.set(name, 'lang', unicode(lang))
        
        # Write the config
        with codecs.open(cls.CONFIG_FILE, 'w+', encoding='utf-8') as f:
            config.write(f)
    
    
    @classmethod
    def loadConfig(cls):
        config = SafeConfigParser()
        if os.path.isfile(cls.CONFIG_FILE):
            config.read_file(codecs.open(cls.CONFIG_FILE, encoding='utf-8'))
        
        # The default config
        cls.config = {}
        cls.config['command_open'] = None
        cls.config['player'] = 1
        
        # Load the options
        if config.has_section('options'):
            for key, value in config.items('options'):
                cls.config[key] = value
        
        # Load the series
        cls.series = []
        for section in config.sections():
            if section != 'options':
                title = config.get(section, 'title')
                videos = config.get(section, 'videos')
                theTvDb = config.getint(section, 'theTvDb')
                lang = config.get(section, 'lang')
                cls.series.append([section, title, videos, theTvDb, lang])


if __name__ == '__main__':
    Config.loadConfig()
    print Config.series