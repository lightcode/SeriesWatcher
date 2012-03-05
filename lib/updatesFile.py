import cPickle as pickle

class UpdatesFile(object):
    _instance = None
    REFRESH_FILE = 'database/updates.pkl'
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    @classmethod
    def loadUpdates(cls):
        # Open the updater PKL file
        try:
            with open(cls.REFRESH_FILE, 'rb') as f:
                cls.updates = pickle.load(f)
        except IOError:
            cls.updates = {}
        except EOFError:
            cls.updates = {}
    
    
    @classmethod
    def getLastUpdate(cls, serieName):
        if serieName in cls.updates:
            return int(cls.updates[serieName])
        else:
            return 0
    
    
    @classmethod
    def setLastUpdate(cls, serieName, newTime):
        cls.updates[serieName] = newTime
        cls.save()
    
    
    @classmethod
    def save(cls):
        with open(cls.REFRESH_FILE, 'w+b') as f:
            pickle.dump(cls.updates, f)