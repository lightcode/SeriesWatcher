#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Logs(object):
    _instance = None
    LOG_FILE = 'errors.log'
    enable = False
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    
    @classmethod
    def add(cls, *infos):
        if cls.enable:
            infos = map(unicode, infos)
            with open(cls.LOG_FILE, 'a+') as log:
                log.write(u''.join(infos) + '\n')