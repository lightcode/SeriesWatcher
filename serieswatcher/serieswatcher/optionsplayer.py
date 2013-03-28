#!/usr/bin/env python
from PyQt4 import QtGui


class OptionsPlayer(QtGui.QDialog):
    def __init__(self, parent=None):
        super(OptionsPlayer, self).__init__(parent)
        self.setWindowTitle('Options')
        self.parent = parent
        
        audioList = parent.mediaPlayer.audio_get_track_description()
        stList = parent.mediaPlayer.video_get_spu_description()
        
        self.st = QtGui.QComboBox()
        for id, text in stList:
            self.st.addItem(text.decode('utf8'))
        if stList:
            self.st.setDisabled(False)
        else:
            self.st.setDisabled(True)
        self.st.setCurrentIndex(self.parent.mediaPlayer.video_get_spu())
        self.st.currentIndexChanged.connect(self.changeST)
        
        self.audio = QtGui.QComboBox()
        for id, text in audioList:
            self.audio.addItem(text.decode('utf8'))
        if audioList:
            self.audio.setDisabled(False)
        else:
            self.audio.setDisabled(True)
        self.audio.setCurrentIndex(self.parent.mediaPlayer.audio_get_track())
        self.audio.currentIndexChanged.connect(self.changeAudio)
        
        layout = QtGui.QFormLayout()
        layout.addRow('Sous-titres', self.st)
        layout.addRow('Audio', self.audio)    
        self.setLayout(layout)
    
    
    def changeST(self, new):
        self.parent.mediaPlayer.video_set_spu(new)
    
    
    def changeAudio(self, new):
        self.parent.mediaPlayer.audio_set_track(new)