#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QIcon, QPalette, QShortcut
from .const import THEME, ICONS
from .optionsplayer import OptionsPlayer
from .widgets.videoepisode import Episode
from .widgets.vlcwidget import VLCWidget

# Import VLC
path = os.getcwd()
try:
    import vlc
except:
    vlc = None
os.chdir(path)

def _timeToText(time):
    """Format the time."""
    time = int(time)
    s = time % 60
    m = (time // 60) % 60
    h = time // 3600
    if h < 1:
        return '%02d:%02d' % (m, s)
    else:
        return '%02d:%02d:%02d' % (h, m, s)

class Slider(QtGui.QSlider):
    def __init__(self, parent=None):
        super(Slider, self).__init__(parent)
        self.setMouseTracking(True)
        self._duration = 0
    
    def mouseMoveEvent(self, event):
        k = event.x() / float(self.width())
        self.setToolTip(_timeToText(self._duration * k))
        super(Slider, self).mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        k = event.x() / float(self.width())
        a = k * self.maximum()
        self.setValue(a)
        self.sliderMoved.emit(self.value())
        super(Slider, self).mousePressEvent(event)
    
    def setDuration(self, duration):
        self._duration = duration / 1000.


class Player(QtGui.QMainWindow):
    """Class to handle the window player."""
    VLCLoaded = False
    TIME_HIDE_BAR = 2000
    PLAY, PAUSE, STOP, USER_STOP = 0, 1, 2, 3
    VLC_PARAM = ' '.join(['-I dummy', '--ignore-config', '--verbose=0',
                          '--no-video-title-show', '--no-plugins-cache'])
    
    def __init__(self, parent=None):
        """Initialize the player video."""
        QtGui.QMainWindow.__init__(self, parent)
        self._playList = []
        self._playerState = self.STOP
        self.currentEpisode = -1
        self.setWindowTitle("Series Player")
        self.resize(640, 480)
        if vlc:
            self.VLCLoaded = True
            self.instance = vlc.Instance(self.VLC_PARAM)
            self.mediaPlayer = self.instance.media_player_new()
            self.mediaPlayer.video_set_mouse_input(False)
            self.mediaPlayer.video_set_key_input(False)
            self.createUI()
        
        with open(THEME + 'seriesplayer.css') as style:
            self.setStyleSheet(style.read())
    
    def showBar(self):
        """Show the player bar."""
        self.bar.show()
        self.currentEpisodeWidget.show()
        QtCore.QTimer.singleShot(self.TIME_HIDE_BAR, self.tryHide)
        self._timeShow = time.clock()
        self.videoFrame.setCursor(Qt.ArrowCursor)
    
    def tryHide(self):
        """Try to hide the player bar."""
        totalTime = int(time.clock() - self._timeShow) * 1000
        if totalTime >= self.TIME_HIDE_BAR:
            self.bar.hide()
            self.currentEpisodeWidget.hide()
            self.videoFrame.setCursor(Qt.BlankCursor)
        else:
            QtCore.QTimer.singleShot(self.TIME_HIDE_BAR, self.tryHide)
    
    def nextEpisode(self):
        """Try to play the next episode."""
        if self.currentEpisode < len(self._playList) - 1:
            self.currentEpisode += 1
            self.playFile()
        elif self.autoPlay.isChecked():
            if self.parent().playFirstEpisode():
                self.currentEpisode += 1
                self.playFile()
            else:
                return False
        elif self.btnRandom.isChecked():
            if self.parent().playRandomEpisode():
                self.currentEpisode += 1
                self.playFile()
            else:
                return False
        else:
            return False
        return True
    
    def previousEpisode(self):
        """Triggered when the user click on the previous
        episode button.
        """
        if self.currentEpisode > 0:
            self.currentEpisode -= 1
            return self.playFile()
    
    def resizeEvent(self, e):
        """Triggered when the user resize the window."""
        QtGui.QMainWindow.resizeEvent(self, e)
        self.drawBar()
    
    def mouseDoubleClickEvent(self, e):
        """Triggered when the user double click on the video."""
        self.fullScreen()
    
    def wheelEvent(self, e):
        """Triggered when the user turn his mouse wheel."""
        if e.delta() > 0:
            self.volumeUp()
        elif e.delta() < 0:
            self.volumeDown()
    
    def showPlayList(self):
        """Show the playlist."""
        if self.playListBtn.isChecked():
            self.playList.show()
            pos = self.playList.geometry()
            self.hideAnimation = QtCore.QPropertyAnimation(self.playList,
                                                           "geometry")
            self.hideAnimation.setDuration(60)
            self.playList.endGeometry = QtCore.QRect(pos)
            self.playList.startGeometry = QtCore.QRect(-60, pos.y(),
                                                       pos.width(),
                                                       pos.height())
            self.hideAnimation.setStartValue(self.playList.startGeometry)
            self.hideAnimation.setEndValue(self.playList.endGeometry)
            self.hideAnimation.start()
        else:
            self.playList.hide()
    
    def showCurrentEpisode(self):
        """Show the current episode bar."""
        self.currentEpisodeWidget.show()
        QtCore.QTimer.singleShot(self.TIME_HIDE_BAR,
                                 self.currentEpisodeWidget.hide)
    
    def closeEvent(self, e):
        """Triggered when the user close the window."""
        self.timer.stop()
        self.currentEpisode = -1
        self.stop()
        self._playList = []
        self.playList.blockSignals(True)
        self.playList.clear()
        self.playList.blockSignals(False)
        self._playerState = self.STOP
        self.autoPlay.setChecked(False)
        self.btnRandom.setChecked(False)
        QtGui.QMainWindow.closeEvent(self, e)
    
    def drawBar(self):
        """Draw the bar on the window."""
        totalWidth = self.videoFrame.width()
        w = totalWidth - 60 if totalWidth < 750 else 750
        self.bar.resize(w, 100)
        y = self.videoFrame.y() + self.videoFrame.height() - self.bar.height()
        x = (totalWidth - w) / 2
        self.bar.move(x, y)
        
        # Playlist
        self.playList.move(0, 30)
        self.playList.resize(240, 200)
        
        # Current Episode
        self.currentEpisodeWidget.resize(320, 100)
        x = totalWidth - 320 - 25
        self.currentEpisodeWidget.move(x, 25)
    
    def volumeUp(self):
        """Triggered when the user change the volume."""
        volume = self.volumeSlider.value() + 5
        volume = 100 if volume > 100 else volume
        self.volumeSlider.setValue(volume)
    
    def volumeDown(self):
        """Triggered when the user change the volume."""
        volume = self.volumeSlider.value() - 5
        volume = 0 if volume < 0 else volume
        self.volumeSlider.setValue(volume)
    
    def fullScreen(self):
        """Toggle the window in full screen."""
        if self.windowState() == Qt.WindowFullScreen:
            self.screenBtn.setIcon(QIcon(ICONS + 'fullscreen.png'))
            self.setWindowState(self._afterFullScreen)
        else:
            self._afterFullScreen = self.windowState()
            self.screenBtn.setIcon(QIcon(ICONS + 'fullscreen-exit.png'))
            self.setWindowState(Qt.WindowFullScreen)
    
    def playPause(self):
        """Toggle the video in pause or play."""
        if self.mediaPlayer.is_playing():
            self.mediaPlayer.pause()
            self.playButton.setText("Play")
            self.playButton.setIcon(QIcon(ICONS + "play.png"))
            self._playerState = self.PAUSE
        else:
            self.play()
    
    def play(self):
        """Play the video."""
        if self.mediaPlayer.play() == -1:
            self.playFile()
            return
        self.playButton.setText("Pause")
        self.playButton.setIcon(QIcon(ICONS + "pause.png"))
        self.timer.start()
        self._playerState = self.PLAY
    
    def stop(self, state=USER_STOP):
        """Stop the video."""
        self._playerState = state
        self.mediaPlayer.stop()
        self.playButton.setText("Play")
        self.playButton.setIcon(QIcon(ICONS + "play.png"))
    
    def playFile(self):
        """Open the file and play it."""
        try:
            title, path, imgPath = self._playList[self.currentEpisode]
        except IndexError:
            pass
        else:
            self.showCurrentEpisode()
            self.currentEpisodeWidget.setImage(imgPath)
            self.currentEpisodeWidget.setTitle(title)
            self.openFile(path)
            self.play()
            self.playList.blockSignals(True)
            self.playList.setCurrentRow(self.currentEpisode)
            self.playList.blockSignals(False)
    
    def openFile(self, fileName):
        """Open the file."""
        self.showCurrentEpisode()
        fileName = 'file:///' + fileName
        media = self.instance.media_new(unicode(fileName))
        self.mediaPlayer.set_media(media)
        media.parse()
        time = media.get_duration()
        if time < 0:
            self.currentTime.setText('--:--')
        else:
            textTime = _timeToText(time // 1000)
            self.totalTime.setText(textTime)
            self.positionSlider.setDuration(time)
    
    def addToPlayList(self, number, title, path, imgPath):
        """Add the episode in the playlist."""
        fullTitle = '<b>%s</b> %s' % (number, title)
        self._playList.append([fullTitle, path, imgPath])
        item = QtGui.QListWidgetItem(title)
        self.playList.addItem(item)
    
    def tryToPlay(self):
        """Try to play the episode."""
        if self._playerState == self.STOP:
            self.nextEpisode()
    
    def setBtnVolume(self, volume):
        """Change the image on the button."""
        if volume < 50:
            self.volumeBtn.setIcon(QIcon(ICONS + 'volume-medium.png'))
        else:
            self.volumeBtn.setIcon(QIcon(ICONS + 'volume-high.png'))
    
    def toggleVolume(self):
        """Toggle the volume on mute or not mute."""
        self.mediaPlayer.audio_toggle_mute()
        if self.mediaPlayer.audio_get_mute():
            self.volumeBtn.setIcon(QIcon(ICONS + 'volume-mute.png'))
            self.volumeSlider.setDisabled(True)
        else:
            self.setBtnVolume(self.mediaPlayer.audio_get_volume())
            self.volumeSlider.setDisabled(False)
    
    def setVolume(self, volume):
        """Set volume."""
        self.mediaPlayer.audio_set_volume(volume)
        self.setBtnVolume(volume)
    
    def setPosition(self, position):
        """Set the current position in the video."""
        self.mediaPlayer.set_position(position / 1000.0)
    
    def updateUI(self):
        """Refresh the user interface."""
        percent = self.mediaPlayer.get_position() * 1000
        self.positionSlider.setValue(percent)
        
        time = int(self.mediaPlayer.get_time())
        if time > 0:
            time //= 1000
            textTime = _timeToText(time)
            self.currentTime.setText(textTime)
        else:
            self.currentTime.setText('--:--')
        
        if self.mediaPlayer.is_playing() == 0:
            self.timer.stop()
            # Fix. When videos don't play
            if percent <= 1 and self._playerState == self.PLAY:
                self.play()
            elif self._playerState != self.PAUSE:
                if self._playerState != self.USER_STOP:
                    self.stop(self.STOP)
                if self._playerState == self.STOP:
                    # Video is at the end
                    if percent >= 99:
                        self.videoFinished()
    
    def videoFinished(self):
        """Triggered when the video finish."""
        if not self.nextEpisode():
            self.close()
    
    def changeEpisode(self):
        """Select the current in the playlist and play it."""
        newItem = self.playList.currentRow()
        self.currentEpisode = newItem
        self.playFile()
    
    def showOptions(self):
        """Open the video window."""
        self.options = OptionsPlayer(self)
        self.options.show()
    
    def speedUp(self):
        speed = self.mediaPlayer.get_rate()
        self.mediaPlayer.set_rate(speed + 0.5)
    
    def speedDown(self):
        speed = self.mediaPlayer.get_rate()
        self.mediaPlayer.set_rate(speed - 0.5)
    
    def createUI(self):
        """Make the window interface."""
        self.videoFrame = VLCWidget()
        self.videoFrame.mouseMoved.connect(self.showBar)
        
        self.currentTime = QtGui.QLabel('--:--')
        
        self.positionSlider = Slider(Qt.Horizontal)
        self.positionSlider.setToolTip("Position")
        self.positionSlider.setMaximum(1000)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        
        self.totalTime = QtGui.QLabel('--:--')
        
        timeLayout = QtGui.QHBoxLayout()
        timeLayout.addWidget(self.currentTime)
        timeLayout.addWidget(self.positionSlider)
        timeLayout.addWidget(self.totalTime)
        
        tool = QtGui.QToolBar()
        self.playButton = tool.addAction(QIcon(ICONS + 'play.png'), 'Play',
                                         self.playPause)
        tool.addAction(QIcon(ICONS + 'backward.png'), u'Précédent',
                       self.previousEpisode)
        tool.addAction(QIcon(ICONS + 'stop.png'), 'Stop', self.stop)
        tool.addAction(QIcon(ICONS + 'forward.png'), 'Suivant',
                       self.nextEpisode)
        tool.addSeparator()
        
        self.playListBtn = tool.addAction(QIcon(ICONS + 'playlist.png'),
                                          "Playlist", self.showPlayList)
        self.playListBtn.setCheckable(True)
        self.autoPlay = tool.addAction(QIcon(ICONS + 'reload.png'),
                                       "Activer la lecture automatique")
        self.autoPlay.setCheckable(True)
        
        self.btnRandom = tool.addAction(QIcon(ICONS + 'random.png'),
                                        u"Jouer aléatoirement un autre épisode")
        self.btnRandom.setCheckable(True)
        
        toolRight = QtGui.QToolBar()
        self.volumeBtn = toolRight.addAction(QIcon(ICONS + 'volume-mute.png'),
                                             'Volume', self.toggleVolume)
        tool.addSeparator()
        
        tool.addAction(u'Ralentir', self.speedDown)
        tool.addAction(u'Accélérer', self.speedUp)
        tool.addSeparator()
        
        self.screenBtn = tool.addAction(QIcon(ICONS + 'fullscreen.png'),
                                        u"Plein écran", self.fullScreen)
        # Fix me :
        #tool.addAction(QIcon(ICONS + 'options.png'), 'Options', self.showOptions)
        
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
        self.playList.currentRowChanged.connect(self.changeEpisode)
        self.playList.hide()
        
        self.currentEpisodeWidget = Episode()
        self.currentEpisodeWidget.setObjectName('currentEpisode')
        palette = QPalette()
        palette.setColor(QPalette.Window, palette.color(QPalette.Window))
        self.currentEpisodeWidget.setPalette(palette)
        self.currentEpisodeWidget.setAutoFillBackground(True)
        self.currentEpisodeWidget.hide()
        
        self.bar = QtGui.QWidget()
        self.bar.setObjectName('tool')
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