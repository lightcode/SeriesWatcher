# -*-coding: utf8-*-
from PyQt4 import QtCore, QtGui
from config import Config


class Options(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle('Options')
        
        cmdOpen = QtGui.QLineEdit(Config.config['command_open'])
        
        form = QtGui.QFormLayout()
        form.addRow(u"Commande d'ouverture de vidéo", cmdOpen)
        
        self.setLayout(form)