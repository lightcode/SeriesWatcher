# -*-coding: utf8-*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from config import Config


class Options(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle('Options')
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)
        
        self.cmdOpen = QtGui.QLineEdit(Config.config['command_open'])
        
        form = QtGui.QFormLayout()
        form.addRow(u"Commande d'ouverture de vidéo", self.cmdOpen)
        
        okBtn = QtGui.QPushButton('Sauvegarder')
        okBtn.clicked.connect(self.save)
        #okBtn.setFixedWidth(100)
        
        layout = QtGui.QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(okBtn)
        
        self.setLayout(layout)
    
    
    def save(self):
        cmdOpen = str(self.cmdOpen.text())
        Config.setOption('command_open', cmdOpen)
        
        self.close()