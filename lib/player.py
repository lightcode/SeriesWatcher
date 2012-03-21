#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import user
import sys
import time
import vlc
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor, QIcon, QPalette, QShortcut

class VLCWidget(QtGui.QFrame):
    mouseMoved = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setMouseTracking(True)
        # the UI player
        self._palette = self.palette()
        self._palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(self._palette)
        self.setAutoFillBackground(True)    
    
    
    def mouseMoveEvent(self, e):
        self.mouseMoved.emit()



class Episode(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.img = QtGui.QLabel()
        self.img.setFixedWidth(120)
        
        self.title = QtGui.QLabel("Titre de l'episode")
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.img)
        layout.addWidget(self.title)
        self.setLayout(layout)
    
    
    def setImage(self, path):
        pixmap = QtGui.QPixmap(path)
        pixmap = pixmap.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img.setPixmap(pixmap)
    
    
    def setTitle(self, title):
        self.title.setText(title)



class Player(QtGui.QMainWindow):
    _playList = []
    TIME_HIDE_BAR = 2000
    currentEpisode = 0
    VLC_PARAM = "-I dummy --ignore-config --verbose=0 \
                --no-video-title-show --no-plugins-cache"
    
    PLAY, PAUSE, STOP, USER_STOP = 0, 1, 2, 3
    _playerState = STOP
    
    def __init__(self, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Series Player")
        self.resize(640, 480)
        
        self.instance = vlc.Instance(self.VLC_PARAM)
        self.mediaPlayer = self.instance.media_player_new()
        self.mediaPlayer.video_set_mouse_input(False)
        self.mediaPlayer.video_set_key_input(False) 
        self.createUI()
    
    
    def showBar(self):
        self.bar.show()
        self.currentEpisodeWidget.show()
        QtCore.QTimer.singleShot(self.TIME_HIDE_BAR, self.tryHide)
        self._timeShow = time.clock()
        self.videoFrame.setCursor(Qt.ArrowCursor)
    
    
    def tryHide(self):
        totalTime = int(time.clock() - self._timeShow) * 1000
        if totalTime >= self.TIME_HIDE_BAR:
            self.bar.hide()
            self.currentEpisodeWidget.hide()
            self.videoFrame.setCursor(Qt.BlankCursor)
    
    
    def nextEpisode(self):
        self.currentEpisode += 1
        return self.playFile()
    
    
    def previousEpisode(self):
        self.currentEpisode -= 1
        return self.playFile()
    
    
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
    
    
    def showCurrentEpisode(self):
        self.currentEpisodeWidget.show()
        QtCore.QTimer.singleShot(self.TIME_HIDE_BAR,
                                 self.currentEpisodeWidget.hide)
    
    
    def closeEvent(self, e):
        self.timer.stop()
        self.currentEpisode = 0
        self._playList = []
        self.stop()
        self.playList.clear()
        self._playerState = self.STOP
        QtGui.QMainWindow.closeEvent(self, e)
    
    
    def changeEpisode(self):
        newItem = self.playList.currentRow()
        self.currentEpisode = newItem
        self.playFile()
    
    
    def drawBar(self):
        totalWidth = self.videoFrame.width()
        w = totalWidth - 60 if totalWidth < 750 else 750
        self.bar.resize(w, 100)
        y = self.videoFrame.y() + self.videoFrame.height()
        y = y - self.bar.height()
        x = (totalWidth - w) / 2
        self.bar.move(x, y)
        
        # Playlist
        x = totalWidth - 240 - 30
        self.playList.move(x, 30)
        self.playList.resize(240, 200)
        
        # Current Episode
        self.currentEpisodeWidget.resize(300, 100)
        x = totalWidth - 300 - 30
        self.currentEpisodeWidget.move(x, 50)
    
    
    def volumeUp(self):
        volume = self.volumeSlider.value() + 5
        if volume > 100:
            volume = 100
        self.volumeSlider.setValue(volume)
    
    
    def volumeDown(self):
        volume = self.volumeSlider.value() - 5
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
            self._playerState = self.PAUSE
        else:
            if self.mediaPlayer.play() == -1:
                self.playFile()
                return
            self.mediaPlayer.play()
            self.playButton.setText("Pause")
            self.playButton.setIcon(QIcon("art/pause.png"))
            self.timer.start()
            self._playerState = self.PLAY
    
    
    def stop(self, state=USER_STOP):
        self._playerState = state
        self.mediaPlayer.stop()
        self.playButton.setText("Play")
        self.playButton.setIcon(QIcon("art/play.png"))
    
    
    def playFile(self):
        try:
            title, path, imgPath = self._playList[self.currentEpisode]
            self.showCurrentEpisode()
            self.currentEpisodeWidget.setImage(imgPath)
            self.currentEpisodeWidget.setTitle(title)
            self.openFile(path)
            self.playPause()
            self.playList.setCurrentRow(self.currentEpisode)
            return True
        except IndexError:
            return False
    
    
    def openFile(self, fileName):
        self.showCurrentEpisode()
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
    
    
    def addToPlayList(self, title, path, imgPath):
        self._playList.append([title, path, imgPath])
        item = QtGui.QListWidgetItem(title)
        self.playList.addItem(item)
    
    
    def tryToPlay(self):
        if self._playerState == self.STOP:
            self.playFile()
    
    
    def setBtnVolume(self, volume):
        if volume == 0:
            self.volumeBtn.setIcon(QIcon('art/mute.png'))
        elif volume < 50:
            self.volumeBtn.setIcon(QIcon('art/volume_down.png'))
        else:
            self.volumeBtn.setIcon(QIcon('art/volume_up.png'))
    
    
    def toggleVolume(self):
        volume = self.volumeSlider.value()
        if volume == 0:
            volume = 100
        else:
            volume = 0
        self.volumeSlider.setValue(volume)
    
    
    def setVolume(self, volume):
        self.mediaPlayer.audio_set_volume(volume)
        self.setBtnVolume(volume)
    
    
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
        
        time = int(self.mediaPlayer.get_time())
        if time > 0:
            time //= 1000
            textTime = self._timeToText(time)
            self.currentTime.setText(textTime)
        else:
            self.currentTime.setText('--:--')
        
        if not self.mediaPlayer.is_playing():
            self.timer.stop()
            if self._playerState != self.PAUSE:
                if self._playerState != self.USER_STOP:
                    self.stop(self.STOP)
                if self._playerState == self.STOP:
                    if not self.nextEpisode():
                        self.close()
    
    
    def createUI(self):        
        self.videoFrame = VLCWidget()
        self.videoFrame.mouseMoved.connect(self.showBar)
        
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
        
        self.setStyleSheet('QToolBar { border:none; }')
        tool = QtGui.QToolBar()
        self.playButton = tool.addAction(QIcon('art/play.png'), 'Play',
                                         self.playPause)
        tool.addAction(QIcon('art/previous.png'), u'Précédent',
                       self.previousEpisode)
        tool.addAction(QIcon('art/stop.png'), 'Stop', self.stop)
        tool.addAction(QIcon('art/next.png'), 'Suivant', self.nextEpisode)
        self.screenBtn = tool.addAction(QIcon('art/fullscreen.png'),
                                        u"Plein écran", self.fullScreen)
        self.playListBtn = tool.addAction(QIcon('art/playlist.png'),
                                          "Afficher la playlist",
                                          self.showPlayList)
        self.playListBtn.setCheckable(True)
        
        
        toolRight = QtGui.QToolBar()
        self.volumeBtn = toolRight.addAction(QIcon('art/mute.png'), 'Volume',
                                             self.toggleVolume)
        
        volume = self.mediaPlayer.audio_get_volume()
        self.volumeSlider = QtGui.QSlider(Qt.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(volume)
        self.volumeSlider.setToolTip("Volume")
        self.volumeSlider.valueChanged.connect(self.setVolume)
        self.setBtnVolume(volume)
        
        hButtonBox = QtGui.QHBoxLayout()
        hButtonBox.addWidget(tool)
        hButtonBox.addStretch(1)
        hButtonBox.addWidget(toolRight)
        hButtonBox.addWidget(self.volumeSlider)
        
        vBoxLayout = QtGui.QVBoxLayout()
        vBoxLayout.addLayout(timeLayout)
        vBoxLayout.addLayout(hButtonBox)
        
        self.playList = QtGui.QListWidget()
        #self.playList.setStyleSheet('''
        #    QListWidget::item:selected {
        #        background-color:#1979FF; color:white;
        #    }
        #''')
        self.playList.currentRowChanged.connect(self.changeEpisode)
        self.playList.hide()
        
        
        self.currentEpisodeWidget = Episode()
        self.currentEpisodeWidget.hide()
        palette = QPalette()
        palette.setColor(QPalette.Window, palette.color(QPalette.Window))
        self.currentEpisodeWidget.setPalette(palette)
        self.currentEpisodeWidget.setAutoFillBackground(True)
        #self.currentEpisode.hide()
        
        
        
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
        self.currentEpisodeWidget.setParent(widget)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)
        
        QShortcut(Qt.Key_Escape, self).activated.connect(self.fullScreen)
        QShortcut(Qt.Key_Space, self).activated.connect(self.playPause)
        QShortcut(Qt.Key_MediaPlay, self).activated.connect(self.playPause)
        QShortcut(Qt.Key_MediaStop, self).activated.connect(self.stop)
        
        if sys.platform == "linux2":   # For Linux
            self.mediaPlayer.set_xwindow(self.videoFrame.winId())
        elif sys.platform == "win32":  # For Windows
            self.mediaPlayer.set_hwnd(self.videoFrame.winId())
        elif sys.platform == "darwin": # For Mac OS
            self.mediaPlayer.set_agl(self.videoFrame.windId())



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mediaPlayer = Player()
    mediaPlayer.show()
    sys.exit(app.exec_())