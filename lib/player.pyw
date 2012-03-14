#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import user
import sys
import time
import vlc
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor, QIcon, QPalette

class VLCWidget(QtGui.QFrame):
    mouseMoveHover = QtCore.pyqtSignal()
    _oldMousePos = QtCore.QPoint()
    
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        # the UI player
        self._palette = self.palette()
        self._palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(self._palette)
        self.setAutoFillBackground(True)
        
        self.timerInput = QtCore.QTimer(self)
        self.timerInput.setInterval(200)
        self.timerInput.timeout.connect(self.checkMouse)
        self.timerInput.start()
    
    
    def checkMouse(self):
        newCursor = QtGui.QCursor()
        newMousePos = newCursor.pos()
        point = self.mapFromGlobal(newMousePos)
        x, y = point.x(), point.y()
        if x < 0 or y < 0 or y > self.height() or x > self.width():
            return
        if newMousePos != self._oldMousePos:
            self.mouseMoveHover.emit()
            self._oldMousePos = newMousePos



class PlayList(QtGui.QListWidget):
    pass

    
class Player(QtGui.QMainWindow):
    _playList = []
    TIME_HIDE_BAR = 2000
    currentEpisode = 0
    isPaused = False
    VLC_PARAM = "-I dummy --ignore-config --verbose=0 \
                --no-video-title-show --no-plugins-cache"
    
    def __init__(self, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")
        self.resize(640, 480)
        
        self.instance = vlc.Instance(self.VLC_PARAM)
        self.mediaPlayer = self.instance.media_player_new()
        self.mediaPlayer.video_set_mouse_input(False)
        self.mediaPlayer.video_set_key_input(False) 
        self.createUI()
    
    
    def showBar(self):
        self.bar.show()
        QtCore.QTimer.singleShot(self.TIME_HIDE_BAR, self.tryHide)
        self._timeShow = time.clock()
        self.videoFrame.setCursor(Qt.ArrowCursor)
    
    
    def tryHide(self):
        totalTime = int(time.clock() - self._timeShow) * 1000
        if totalTime >= self.TIME_HIDE_BAR:
            self.bar.hide()
            self.videoFrame.setCursor(Qt.BlankCursor)
    
    
    def createUI(self):        
        self.videoFrame = VLCWidget()
        self.videoFrame.mouseMoveHover.connect(self.showBar)
        
        self.currentTime = QtGui.QLabel('--:--')
        
        self.positionSlider = QtGui.QSlider(Qt.Horizontal)
        self.positionSlider.setToolTip("Position")
        self.positionSlider.setMaximum(1000)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        
        self.totalTime = QtGui.QLabel('--:--')
        
        timeLayout = QtGui.QHBoxLayout()
        timeLayout.addWidget(self.currentTime)
        timeLayout.addWidget(self.positionSlider)
        timeLayout.addWidget(self.totalTime)
        
        tool = QtGui.QToolBar()
        tool.setStyleSheet('QToolBar { border:none; }')
        self.playButton = tool.addAction(QIcon('art/play.png'),
                                         'Play', self.playPause)
        tool.addAction(QIcon('art/previous.png'), u'Précédent',
                       self.previousEpisode)
        tool.addAction(QIcon('art/stop.png'), 'Stop', self.stop)
        tool.addAction(QIcon('art/next.png'), u'Suivant', self.nextEpisode)
        self.screenBtn = tool.addAction(QIcon('art/fullscreen.png'),
                                        u"Plein écran", self.fullScreen)
        self.playListBtn = tool.addAction(QIcon('art/playlist.png'),
                                          u"Afficher la playlist",
                                          self.showPlayList)
        self.playListBtn.setCheckable(True)
        
        self.volumeSlider = QtGui.QSlider(Qt.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(self.mediaPlayer.audio_get_volume())
        self.volumeSlider.setToolTip("Volume")
        self.volumeSlider.valueChanged.connect(self.setVolume)
        
        hButtonBox = QtGui.QHBoxLayout()
        hButtonBox.addWidget(tool)
        hButtonBox.addStretch(1)
        hButtonBox.addWidget(self.volumeSlider)
        
        vBoxLayout = QtGui.QVBoxLayout()
        vBoxLayout.addLayout(timeLayout)
        vBoxLayout.addLayout(hButtonBox)
        
        self.playList = PlayList()
        self.playList.itemClicked.connect(self.changeEpisode)
        self.playList.resize(240, 200)
        self.playList.hide()
        
        self.bar = QtGui.QWidget()
        palette = QPalette()
        palette.setColor(QPalette.Window, palette.color(QPalette.Window))
        self.bar.setPalette(palette)
        self.bar.setAutoFillBackground(True)
        self.bar.hide()
        self.drawBar()
        self.bar.setLayout(vBoxLayout)
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.videoFrame)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        
        widget = QtGui.QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)
        self.bar.setParent(widget)
        self.playList.setParent(widget)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)
        
        s1 = QtGui.QShortcut(Qt.Key_Escape, self)
        s1.activated.connect(self.fullScreen)
        s2 = QtGui.QShortcut(Qt.Key_Space, self)
        s2.activated.connect(self.playPause)
        s3 = QtGui.QShortcut(Qt.Key_MediaPlay, self)
        s3.activated.connect(self.playPause)
        s4 = QtGui.QShortcut(Qt.Key_MediaStop, self)
        s4.activated.connect(self.stop)
        
        if sys.platform == "linux2":   # For Linux
            self.mediaPlayer.set_xwindow(self.videoFrame.winId())
        elif sys.platform == "win32":  # For Windows
            self.mediaPlayer.set_hwnd(self.videoFrame.winId())
        elif sys.platform == "darwin": # For Mac OS
            self.mediaPlayer.set_agl(self.videoFrame.windId())
    
    
    def nextEpisode(self):
        self.playFile()
    
    
    def previousEpisode(self):
        self.currentEpisode -= 2
        self.playFile()
    
    
    def resizeEvent(self, e):
        QtGui.QMainWindow.resizeEvent(self, e)
        self.drawBar()
    
    
    def mouseDoubleClickEvent(self, e):
        self.fullScreen()
    
    
    def wheelEvent(self, e):
        if e.delta() > 0:
            self.volumeUp()
        elif e.delta() < 0:
            self.volumeDown()
    
    
    def showPlayList(self):
        if self.playListBtn.isChecked():
            self.playList.show()
        else:
            self.playList.hide()
    
    
    def showPlayListTimed(self):
        self.playList.show()
        QtCore.QTimer.singleShot(self.TIME_HIDE_BAR, self.showPlayList)
    
    
    def closeEvent(self, e):
        self.timer.stop()
        self.currentEpisode = 0
        self._playList = []
        self.stop()
        self.playList.clear()
        QtGui.QMainWindow.closeEvent(self, e)
    
    
    def changeEpisode(self):
        newItem = self.playList.currentRow()
        self.currentEpisode = newItem
        self.playFile()
    
    
    def drawBar(self):
        w = self.videoFrame.width() - 60
        self.bar.resize(w, 100)
        y = self.videoFrame.y() + self.videoFrame.height()
        y = y - self.bar.height() - 40
        self.bar.move(30, y)
    
    
    def volumeUp(self):
        volume = self.volumeSlider.value() + 10
        if volume > 100:
            volume = 100
        self.volumeSlider.setValue(volume)
    
    
    def volumeDown(self):
        volume = self.volumeSlider.value() - 10
        if volume < 0:
            volume = 0
        self.volumeSlider.setValue(volume)
    
    
    def fullScreen(self):
        if self.windowState() == Qt.WindowFullScreen:
            self.screenBtn.setIcon(QIcon('art/fullscreen.png'))
            self.setWindowState(self._afterFullScreen)
        else:
            self._afterFullScreen = self.windowState()
            self.screenBtn.setIcon(QIcon('art/minimise.png'))
            self.setWindowState(Qt.WindowFullScreen)
    
    
    def playPause(self):
        if self.mediaPlayer.is_playing():
            self.mediaPlayer.pause()
            self.playButton.setText("Play")
            self.playButton.setIcon(QIcon("art/play.png"))
            self.isPaused = True
        else:
            if self.mediaPlayer.play() == -1:
                self.playFile()
                return
            self.mediaPlayer.play()
            self.playButton.setText("Pause")
            self.playButton.setIcon(QIcon("art/pause.png"))
            self.timer.start()
            self.isPaused = False
    
    
    def stop(self):
        self.mediaPlayer.stop()
        self.playButton.setText("Play")
    
    
    def playFile(self):
        if len(self._playList) > self.currentEpisode:
            path = self._playList[self.currentEpisode]
            self.showPlayListTimed()
            self.openFile(path)
            self.playPause()
            self.playList.setCurrentRow(self.currentEpisode)
            self.currentEpisode += 1
            return True
        return False
    
    
    def openFile(self, fileName):
        fileName = 'file:///' + fileName
        media = self.instance.media_new(unicode(fileName))
        self.mediaPlayer.set_media(media)
        media.parse()
        time = media.get_duration()
        if time < 0:
            self.currentTime.setText('--:--')
        else:
            textTime = self._timeToText(time // 1000)
            self.totalTime.setText(textTime)
    
    
    def addToPlayList(self, title, path):
        self._playList.append(path)
        item = QtGui.QListWidgetItem(title)
        self.playList.addItem(item)
    
    
    def tryToPlay(self):
        if not self.mediaPlayer.is_playing() and not self.isPaused:
            self.playFile()
    
    
    def setVolume(self, volume):
        self.mediaPlayer.audio_set_volume(volume)
    
    
    def setPosition(self, position):
        self.mediaPlayer.set_position(position / 1000.0)
    
    
    def _timeToText(self, time):
        time = int(time)
        s = time % 60
        m = (time // 60) % 60
        h = time // 3600
        if h < 1:
            return '%02d:%02d' % (m, s)
        else:
            return '%02d:%02d:%02d' % (h, m, s)
    
    
    def updateUI(self):
        percent = self.mediaPlayer.get_position() * 1000
        self.positionSlider.setValue(percent)
        
        time = int(self.mediaPlayer.get_time()) // 1000
        textTime = self._timeToText(time)
        self.currentTime.setText(textTime)
        
        if not self.mediaPlayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self.stop()
                if not self.playFile():
                    self.close()



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mediaPlayer = Player()
    mediaPlayer.show()
    sys.exit(app.exec_())