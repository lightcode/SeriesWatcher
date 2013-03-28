#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hashlib import sha512
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from config import Config
from widgets.selectfile import SelectFile


RANDOM_TIMES = [(u'Désactiver', 0),
                ('15 jours', 1296000),
                ('1 mois', 2592000),
                ('3 mois', 7776000)]


class Options(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Options, self).__init__(parent)
        self.setWindowTitle('Options')
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)
        
        # Series Watcher options
        self.randomDuration = QtGui.QComboBox()
        self.randomDuration.addItems([t for t, v in RANDOM_TIMES])
        self.setRandomDuration(Config.config['random_duration'])
        form = QtGui.QFormLayout()
        form.addRow(u"Ne pas rediffuser d'épisode vu il y a moins de", \
                    self.randomDuration)
        groupSW = QtGui.QGroupBox(u'Series Watcher')
        groupSW.setLayout(form)
        
        
        # Player Choice
        self.cmdOpen = SelectFile(Config.config['command_open'])
        
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
        form.addRow(self.cmdOpen)
        
        groupPlayer = QtGui.QGroupBox(u'Configuration du lecteur vidéo')
        groupPlayer.setLayout(form)
        
        
        # Debug option
        self.enablePlayer = QtGui.QCheckBox(u'Activer le debug')
        if int(Config.config['debug']):
            self.enablePlayer.setChecked(True)
        else:
            self.enablePlayer.setChecked(False)
        
        form = QtGui.QFormLayout()
        form.addRow(self.enablePlayer)
        
        groupDebug = QtGui.QGroupBox(u'Debug')
        groupDebug.setLayout(form)
        
        layout1 = QtGui.QVBoxLayout()
        layout1.addWidget(groupSW)
        layout1.addWidget(groupPlayer)
        layout1.addWidget(groupDebug)
        
        tab1 = QtGui.QWidget()
        tab1.setLayout(layout1)
        
        # Synchronisation
        self.syncServer = QtGui.QLineEdit(Config.config['sync_server'])
        self.syncUser = QtGui.QLineEdit(Config.config['sync_user'])
        self.syncPassword = QtGui.QLineEdit()
        self.syncPassword.setEchoMode(QtGui.QLineEdit.Password)
        
        layout2 = QtGui.QFormLayout()
        layout2.addRow('Serveur', self.syncServer)
        layout2.addRow("Nom d'utilisateur", self.syncUser)
        layout2.addRow('Mot de passe', self.syncPassword)
        
        tab2 = QtGui.QWidget()
        tab2.setLayout(layout2)
        
        tab = QtGui.QTabWidget()
        tab.addTab(tab1, u'Général')
        tab.addTab(tab2, 'Synchronisation')
        
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Sauvegarder', QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.save)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.close)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tab)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.playerChanged)
        self.timer.start()
    
    
    def openSubscribeWindow(self):
        sw = SubscribeWindow(self)
        sw.show()
    
    
    def setPlayer(self, value):
        if 4 > value > 0:
            self.__dict__['player%s' % value].setChecked(True)
    
    
    def playerChanged(self):
        if self.player() == 3:
            self.cmdOpen.setDisabled(False)
        else:
            self.cmdOpen.setDisabled(True)
    
    
    def player(self):
        for n in range(1, 4):
            if self.__dict__['player%s' % n].isChecked():
                return n
    
    
    def getRandomValue(self):
        return RANDOM_TIMES[self.randomDuration.currentIndex()][1]
    
    
    def setRandomDuration(self, value):
        for pos, v in enumerate(RANDOM_TIMES):
            t, d = v
            if d == int(value):
                self.randomDuration.setCurrentIndex(pos)
                return
    
    
    def save(self):
        cmdOpen = str(self.cmdOpen.path())
        Config.setOption('command_open', cmdOpen)
        Config.setOption('player', self.player())
        if self.enablePlayer.isChecked():
            Config.setOption('debug', 1)
        else:    
            Config.setOption('debug', 0)
        Config.setOption('random_duration', self.getRandomValue())
        
        Config.setOption('sync_server', self.syncServer.text())
        Config.setOption('sync_user', self.syncUser.text())
        if self.syncPassword.text():
            Config.setOption('sync_password', sha512(self.syncPassword.text()).hexdigest())
        
        Config.save()
        self.close()