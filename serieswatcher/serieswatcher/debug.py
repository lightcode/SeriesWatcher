#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

class Debug(object):
    INFO, ERROR = 0, 1
    _instance = None
    LOG_FILE = 'errors.log'
    enable = False
    logs = []
    
    def __new__(cls): 
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    
    @classmethod
    def add(cls, level, *message):
        m = ' '.join(map(unicode, message))
        cls.logs.append((level, m))
    
    
    @classmethod
    def setEnabled(cls, booleen):
        cls.enable = booleen
    
    
    @classmethod
    def isEnabled(cls):
        return cls.enable



class DebugWindow(QtGui.QDialog):
    LEVELS = ['Info', 'Erreur']
    lastID = -1
    
    def __init__(self, parent=None):
        super(DebugWindow, self).__init__(parent)
        self.setWindowTitle('Debug')
        self.resize(800, 600)
        
        self.logs = QtGui.QTableWidget()
        self.logs.setColumnCount(2)
        self.logs.verticalHeader().hide()
        self.logs.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.logs.setHorizontalHeaderLabels(['Niveau', 'Message'])
        self.logs.setColumnWidth(0, 100)
        self.logs.setColumnWidth(1, 660)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.logs)
        
        self.setLayout(layout)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateLogs)
        self.timer.start()
    
    
    def updateLogs(self):
        for i, l in enumerate(Debug.logs):
            level, message = l
            if i > self.lastID:
                self.lastID = i
                nbRow = self.logs.rowCount()
                self.logs.setRowCount(nbRow + 1)
                item = QtGui.QTableWidgetItem(self.LEVELS[level])
                self.logs.setItem(nbRow, 0, item)
                item = QtGui.QTableWidgetItem(message)
                self.logs.setItem(nbRow, 1, item)