# -*- coding: utf-8 -*-

import time
from datetime import datetime
from PyQt4 import QtCore
from PyQt4.QtCore import qDebug
from serieswatcher.const import *
from serieswatcher.models import Serie
from serieswatcher.thetvdb import TheTVDBSerie


class CheckSerieUpdateTask(QtCore.QObject):
    """Task to check updates on the series database and
    synchronize with the local database.
    """
    TIME_BETWEEN_UPDATE = 86400 # a day
    updateRequired = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(CheckSerieUpdateTask, self).__init__(parent)

    def run(self):
        lastVerification = self.getLastVerification()
        if int(time.time() - lastVerification) >= self.TIME_BETWEEN_UPDATE:
            for localeID, serie in enumerate(Serie.getSeries()):
                localTime = serie.lastUpdate
                try:
                    tvDb = TheTVDBSerie(serie.tvdbID, serie.lang)
                except IOError as e:
                    qDebug('Cannot join TVDB server: %s' % str(e))
                    continue

                try:
                    remoteTime = datetime.fromtimestamp(tvDb.last_update())
                except TypeError:
                    qDebug('Get last update failed.')
                    continue
                else:
                    if not localTime or localTime < remoteTime:
                        self.updateRequired.emit(localeID)
            self.updateLastVerif()

    def getLastVerification(self):
        try:
            with open(LAST_VERIF_PATH, 'r') as f:
                return int(''.join(f.readlines()).strip())
        except IOError:
            return 0
        except ValueError:
            return 0

    def updateLastVerif(self):
        with open(LAST_VERIF_PATH, 'w+') as f:
            f.write("%d" % time.time())
