# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from serieswatcher.const import TEXT_VERSION, RELEASE_DATE


class About(QtGui.QDialog):
    """Class to create the window 'about'."""

    def __init__(self, parent=None):
        """Create the window 'about'."""
        super(About, self).__init__(parent)
        self.setWindowTitle('A propos')

        ABOUT = (
            u'SeriesWatcher %s - %s<br/>'
            u'Créé par Matthieu Gaignière publié sur '
            u'<a href="http://lightcode.fr">LightCode.fr</a> sous licence GPL.'
            u'<hr/>'
            u'Base de donnée : '
            u'<a href="http://thetvdb.com">TheTVDB.com</a><br/>'
            u'Librairies Python externes : desktop, PyQt4, ConfigParser3.2, '
            u'LibVLC, SQLObject.'
        ) % (TEXT_VERSION, RELEASE_DATE)

        text = QtGui.QLabel(ABOUT)
        text.setOpenExternalLinks(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(text)

        self.setLayout(layout)
