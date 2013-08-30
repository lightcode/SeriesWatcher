#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4 import QtCore
from sqlobject.dberrors import OperationalError
from serieswatcher.models import Episode


class SyncDbWorker(QtCore.QObject):
    """Worker to commit changes in a serie to the
    local database.
    """
    def __init__(self, parent=None):
        super(SyncDbWorker, self).__init__(parent)
        self.run()

    def run(self):
        for episode in Episode.select():
            try:
                episode.syncUpdate()
            except OperationalError as msg:
                qDebug('SQLObject Error : %s' % msg)
        QtCore.QTimer.singleShot(2000, self.run)