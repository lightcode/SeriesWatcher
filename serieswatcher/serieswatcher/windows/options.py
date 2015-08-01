# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from serieswatcher.config import Config
from serieswatcher.widgets.selectfile import SelectFile


RANDOM_TIMES = ((u'Désactiver', 0),
                ('15 jours', 1296000),
                ('1 mois', 2592000),
                ('3 mois', 7776000))


class Options(QtGui.QDialog):
    """Class to handle the option window."""

    def __init__(self, parent=None):
        """Initialize the option window."""
        super(Options, self).__init__(parent)
        self.setWindowTitle('Options')
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)

        # SeriesWatcher options
        self.randomDuration = QtGui.QComboBox()
        self.randomDuration.addItems([t for t, v in RANDOM_TIMES])
        self.setRandomDuration(Config.config['random_duration'])
        form = QtGui.QFormLayout()
        form.addRow(u"Ne pas rediffuser d'épisodes vus il y a moins de",
                    self.randomDuration)
        groupSW = QtGui.QGroupBox(u'SeriesWatcher')
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
        form.addRow(self.player2)
        form.addRow(self.player1)
        form.addRow(self.player3)
        form.addRow(self.cmdOpen)

        groupPlayer = QtGui.QGroupBox(u'Configuration du lecteur vidéo')
        groupPlayer.setLayout(form)

        layout1 = QtGui.QVBoxLayout()
        layout1.addWidget(groupSW)
        layout1.addWidget(groupPlayer)

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Sauvegarder', QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.save)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.close)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.playerChanged)
        self.timer.start()

    def playerChanged(self):
        """Triggered when the user select another player."""
        if self.player() == 3:
            self.cmdOpen.setDisabled(False)
        else:
            self.cmdOpen.setDisabled(True)

    def setPlayer(self, value):
        """Select the player in the interface."""
        if 4 > value > 0:
            self.__dict__['player%s' % value].setChecked(True)

    def player(self):
        """Return the player number selected."""
        for n in range(1, 4):
            if self.__dict__['player%s' % n].isChecked():
                return n

    def getRandomValue(self):
        """Return the random value selected."""
        return RANDOM_TIMES[self.randomDuration.currentIndex()][1]

    def setRandomDuration(self, value):
        """Set the random duration in the interface."""
        for pos, v in enumerate(RANDOM_TIMES):
            t, d = v
            if d == int(value):
                self.randomDuration.setCurrentIndex(pos)
                return

    def save(self):
        """Save the configuration."""
        cmdOpen = str(self.cmdOpen.path())
        Config.setOption('command_open', cmdOpen)
        Config.setOption('player', self.player())
        Config.setOption('random_duration', self.getRandomValue())
        Config.save()
        self.close()
