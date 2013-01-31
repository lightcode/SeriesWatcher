#!/usr/bin/env python

import json
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from models import Serie, Episode


class SyncSWThead(QtCore.QThread):
    def _getSerieSummary(self):
        print json.dumps(list(Serie.getSummary()))
    
    def run(self):
        self._getSerieSummary()