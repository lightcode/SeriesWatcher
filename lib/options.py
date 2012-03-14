#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        
        self.player1 = QtGui.QRadioButton(u'Utiliser le lecteur par défaut')
        self.player2 = QtGui.QRadioButton(u'Utiliser le lecteur intégré')
        self.player3 = QtGui.QRadioButton(u'Utiliser le lecteur suivant...')
        self.setPlayer(int(Config.config['player']))
        
        buttonGroup = QtGui.QButtonGroup()
        buttonGroup.addButton(self.player1)
        buttonGroup.addButton(self.player2)
        buttonGroup.addButton(self.player3)
        
        form = QtGui.QFormLayout()
        form.addRow(self.player1)
        form.addRow(self.player2)
        form.addRow(self.player3)
        form.addRow(u"Commande d'ouverture de vidéo", self.cmdOpen)
        
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Sauvegarder', QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.save)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.close)
        
        layout = QtGui.QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)
    
    
    def setPlayer(self, value):
        if 4 > value > 0:
            self.__dict__['player%s' % value].setChecked(True)
    
    
    def player(self):
        for n in range(1, 4):
            if self.__dict__['player%s' % n].isChecked():
                return n
    
    
    def save(self):
        cmdOpen = str(self.cmdOpen.text())
        Config.setOption('command_open', cmdOpen)
        Config.setOption('player', self.player())
        Config.save()
        self.close()


if __name__ == "__main__":
    import sys
    Config.loadConfig()
    app = QtGui.QApplication(sys.argv)
    options = Options()
    options.show()
    sys.exit(app.exec_())