import ConfigParser
import os.path

class Config(object):
    _instance = None
    CONFIG_FILE = 'series-watcher.cfg'
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    
    @classmethod
    def addSerie(cls, name, title, theTvDb, lang, path):
        config = ConfigParser.SafeConfigParser()
        name = str(name)
        config.read(cls.CONFIG_FILE)
        config.add_section(name)
        config.set(name, 'videos', str(path))
        config.set(name, 'theTvDb', str(theTvDb))
        config.set(name, 'lang', str(lang))
        config.set(name, 'title', str(title))
        with open(Config.CONFIG_FILE, 'wb') as configFile:
            config.write(configFile)
        cls.loadConfig()
    
    
    @classmethod
    def setOption(cls, key, value):
        cls.config[key] = value
    
    
    @classmethod
    def save(cls):
        config = ConfigParser.SafeConfigParser()
        
        # Make option section
        config.add_section('options')
        for key, value in cls.config.iteritems():
            config.set('options', str(key), str(value))
        
        # Make the series sections
        for name, title, path, tvDbId, lang in cls.series:
            config.add_section(name)
            config.set(name, 'title', str(title))
            config.set(name, 'theTvDb', str(tvDbId))
            config.set(name, 'videos', str(path))
            config.set(name, 'lang', str(lang))
        
        # Write the config
        with open(Config.CONFIG_FILE, 'wb+') as configFile:
            config.write(configFile)
    
    
    @classmethod
    def loadConfig(cls):
        # Add config file if not already exist
        if not os.path.isfile(cls.CONFIG_FILE):
            config = ConfigParser.SafeConfigParser()
            config.add_section('options')
            with open(cls.CONFIG_FILE, 'wb+') as configFile:
                config.write(configFile)
        
        # The default config
        cls.config = {}
        cls.config['command_open'] = None
        
        # Load the options
        config = ConfigParser.SafeConfigParser()
        config.read(cls.CONFIG_FILE)
        try:
            for key, value in config.items('options'):
                cls.config[key] = value
        except ConfigParser.NoSectionError:
            config.add_section('options')
            with open(cls.CONFIG_FILE, 'wb+') as configFile:
                config.write(configFile)
        
        # Load the series
        cls.series = []
        for section in config.sections():
            if section != 'options':
                title = config.get(section, 'title')
                videos = config.get(section, 'videos')
                theTvDb = config.getint(section, 'theTvDb')
                lang = config.get(section, 'lang')
                cls.series.append([section, title, videos, theTvDb, lang])