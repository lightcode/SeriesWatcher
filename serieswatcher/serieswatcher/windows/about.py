#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Matthieu GAIGNIÈRE
#
# This file is part of SeriesWatcher.
#
# SeriesWatcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# SeriesWatcher is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# SeriesWatcher. If not, see <http://www.gnu.org/licenses/>.


from PyQt4 import QtGui
from serieswatcher.const import TEXT_VERSION, RELEASE_DATE


class About(QtGui.QDialog):
    """Class to create the window 'about'."""
    
    def __init__(self, parent=None):
        """Create the window 'about'."""
        super(About, self).__init__(parent)
        self.setWindowTitle('A propos')
        
        ABOUT = [u"Series Watcher %s %s<br/>" % (TEXT_VERSION, RELEASE_DATE),
                 u'Créé par <a href="http://lightcode.fr">LightCode.fr</a> ',
                 'sous licence Creative Commons BY-NC-SA.',
                 "<hr/>",
                 u'Base de donnée : '
                 '<a href="http://thetvdb.com">TheTVDB.com</a><br/>'
                 u"Librairie Python externe : desktop, PyQt4, ",
                 "ConfigParser3.2, LibVLC, SQLObject<br/>"]
                
        text = QtGui.QLabel(''.join(ABOUT))
        text.setOpenExternalLinks(True)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text)
        
        self.setLayout(layout)