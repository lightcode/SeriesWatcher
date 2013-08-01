#!/usr/bin/env python

from PyQt4 import QtGui


class OptionsPlayer(QtGui.QDialog):
    """Class to handle the window option for the player."""
    
    def __init__(self, parent=None):
        """Initialize the window option for the player."""
        super(OptionsPlayer, self).__init__(parent)
        self.setWindowTitle('Options')
        
        # Subtitles
        self.idSubtitlesList = []
        self.st = QtGui.QComboBox()
        stList = self.parent().mediaPlayer.video_get_spu_description()

        if stList:
            for id_, text in stList:
                self.idSubtitlesList.append(id_)
                self.st.addItem(text.decode('utf8'))

            current = self.parent().mediaPlayer.video_get_spu()
            pos = self.idSubtitlesList.index(current)
            self.st.setCurrentIndex(pos)
            self.st.currentIndexChanged.connect(self.changeST)
        else:
            self.st.setDisabled(True)

        # Audio tracks
        self.idAudioTracksList = []
        self.audio = QtGui.QComboBox()
        audioList = self.parent().mediaPlayer.audio_get_track_description()

        if audioList:
            for id_, text in audioList:
                self.idAudioTracksList.append(id_)
                self.audio.addItem(text.decode('utf8'))

            current = self.parent().mediaPlayer.audio_get_track()
            pos = self.idAudioTracksList.index(current)
            self.audio.setCurrentIndex(pos)
            self.audio.currentIndexChanged.connect(self.changeAudio)
        else:
            self.audio.setDisabled(True)

        # Design of the window
        layout = QtGui.QFormLayout()
        layout.addRow('Sous-titres', self.st)
        layout.addRow('Audio', self.audio)    
        self.setLayout(layout)
    
    def changeST(self, pos):
        """Triggered when the user select the subtitle."""
        id_ = self.idSubtitlesList[pos]
        self.parent().mediaPlayer.video_set_spu(id_)
    
    def changeAudio(self, pos):
        """Triggered when the user select the audio track."""
        id_ = self.idAudioTracksList[pos]
        self.parent().mediaPlayer.audio_set_track(id_)