#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

class About(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle('A propos')
        
        ABOUT = [u"Series Watcher 1.1 Mars 2012<br/>",
                 u'Créé par <a href="http://lightcode.fr">LightCode.fr</a> ',
                 'sous licence Creative Commons BY-NC-SA.',
                 "<hr/>",
                 u'Base de donnée : '
                 '<a href="http://thetvdb.com">TheTVDB.com</a><br/>'
                 u"Librairie Python externe : desktop, PyQt4, ",
                 "ConfigParser3.2<br/>",
                 u'Icônes : Glyphicons']
                
        text = QtGui.QLabel(''.join(ABOUT))
        text.setOpenExternalLinks(True)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text)
        
        self.setLayout(layout)