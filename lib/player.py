#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import user
import sys
import time
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor, QIcon, QPalette, QShortcut
from debug import Debug

# Import VLC
path = os.getcwd()
try:
    import vlc
except:
    vlc = None
os.chdir(path)


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
        
        self.title = QtGui.QLabel()
        self.title.setWordWrap(True)
        self.title.setStyleSheet('font-size:14pt;')
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.img)
        layout.addWidget(self.title)
        self.setLayout(layout)
    
    
    def setImage(self, path):
        pix = QtGui.QPixmap(path)
        pix = pix.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img.setPixmap(pix)
    
    
    def setTitle(self, title):
        self.title.setText(title)



class Options(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
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



class Player(QtGui.QMainWindow):
    VLCLoaded = False
    _playList = []
    TIME_HIDE_BAR = 2000
    currentEpisode = -1
    PLAY, PAUSE, STOP, USER_STOP = 0, 1, 2, 3
    _playerState = STOP
    VLC_PARAM = ' '.join(['-I dummy', '--ignore-config', '--verbose=0',
                          '--no-video-title-show', '--no-plugins-cache'])
    
    
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("Series Player")
        self.resize(640, 480)
        if vlc:
            self.VLCLoaded = True
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
        else:
            QtCore.QTimer.singleShot(self.TIME_HIDE_BAR, self.tryHide)
    
    
    def nextEpisode(self):
        if self.currentEpisode < len(self._playList) - 1:
            Debug.add(Debug.INFO, 'nextEpisode(1)')
            self.currentEpisode += 1
            self.playFile()
        elif self.autoPlay.isChecked():
            Debug.add(Debug.INFO, 'nextEpisode(2)')
            if self.parent().playFirstEpisode():
                self.currentEpisode += 1
                self.playFile()
            else:
                return False
        elif self.btnRandom.isChecked():
            Debug.add(Debug.INFO, 'nextEpisode(3)')
            if self.parent().playRandomEpisode():
                Debug.add(Debug.INFO, 'nextEpisode(3) : play action')
                self.currentEpisode += 1
                self.playFile()
            else:
                return False
        else:
            Debug.add(Debug.INFO, 'nextEpisode(4)')
            Debug.add(Debug.INFO, 'nextEpisode : self._playList = %s' % self._playList)
            Debug.add(Debug.INFO, 'nextEpisode : self.currentEpisode = %s' % self.currentEpisode)
            return False
        return True
    
    
    def previousEpisode(self):
        if self.currentEpisode > 0:
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
        totalWidth = self.videoFrame.width()
        w = totalWidth - 60 if totalWidth < 750 else 750
        self.bar.resize(w, 100)
        y = self.videoFrame.y() + self.videoFrame.height() - self.bar.height()
        x = (totalWidth - w) / 2
        self.bar.move(x, y)
        
        # Playlist
        self.playList.move(30, 30)
        self.playList.resize(240, 200)
        
        # Current Episode
        self.currentEpisodeWidget.resize(320, 100)
        x = totalWidth - 320 - 25
        self.currentEpisodeWidget.move(x, 25)
    
    
    def volumeUp(self):
        volume = self.volumeSlider.value() + 5
        volume = 100 if volume > 100 else volume
        self.volumeSlider.setValue(volume)
    
    
    def volumeDown(self):
        volume = self.volumeSlider.value() - 5
        volume = 0 if volume < 0 else volume
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
            self.play()
    
    
    def play(self):
        if self.mediaPlayer.play() == -1:
            self.playFile()
            return
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
        except IndexError:
            Debug.add(Debug.ERROR, 'playFile : self._playList = %s' % self._playList)
            Debug.add(Debug.ERROR, 'playFile : self.currentEpisode = %s' % self.currentEpisode)
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
    
    
    def addToPlayList(self, number, title, path, imgPath):
        fullTitle = '<b>%s</b> %s' % (number, title)
        self._playList.append([fullTitle, path, imgPath])
        item = QtGui.QListWidgetItem(title)
        self.playList.addItem(item)
        Debug.add(Debug.INFO, 'addToPlayList : self._playList =', self._playList)
        Debug.add(Debug.INFO, 'addToPlayList : self.currentEpisode =', self.currentEpisode)

    
    def tryToPlay(self):
        if self._playerState == self.STOP:
            Debug.add(Debug.INFO, 'tryToPlay')
            self.nextEpisode()
    
    
    def setBtnVolume(self, volume):
        if volume < 50:
            self.volumeBtn.setIcon(QIcon('art/volume_down.png'))
        else:
            self.volumeBtn.setIcon(QIcon('art/volume_up.png'))
    
    
    def toggleVolume(self):
        self.mediaPlayer.audio_toggle_mute()
        if self.mediaPlayer.audio_get_mute():
            self.volumeBtn.setIcon(QIcon('art/mute.png'))
            self.volumeSlider.setDisabled(True)
        else:
            self.setBtnVolume(self.mediaPlayer.audio_get_volume())
            self.volumeSlider.setDisabled(False)
    
    
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
        
        if self.mediaPlayer.is_playing() == 0:
            self.timer.stop()
            # FIX : when videos don't play
            if percent <= 1 and self._playerState == self.PLAY:
                self.play()
            elif self._playerState != self.PAUSE:
                if self._playerState != self.USER_STOP:
                    self.stop(self.STOP)
                if self._playerState == self.STOP:
                    Debug.add(Debug.INFO, 'updateUI : nextEpisode()')
                    if percent >= 99: # video is at the end
                        self.videoFinished()
    
    
    def videoFinished(self):
        if not self.nextEpisode():
            self.close()
    
    
    def changeEpisode(self):
        newItem = self.playList.currentRow()
        self.currentEpisode = newItem
        self.playFile()
    
    
    def showOptions(self):
        self.options = Options(self)
        self.options.show()
    
    
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
        tool.addSeparator()
        
        self.playListBtn = tool.addAction(QIcon('art/playlist.png'),
                                          "Playlist", self.showPlayList)
        self.playListBtn.setCheckable(True)
        self.autoPlay = tool.addAction(QIcon('art/refresh.png'),
                                       "Activer la lecture automatique")
        self.autoPlay.setCheckable(True)
        
        self.btnRandom = tool.addAction(QIcon('art/random.png'),
                                       u"Jouer aléatoirement un autre épisode")
        self.btnRandom.setCheckable(True)
        
        toolRight = QtGui.QToolBar()
        self.volumeBtn = toolRight.addAction(QIcon('art/mute.png'), 'Volume',
                                             self.toggleVolume)
        tool.addSeparator()
        
        self.screenBtn = tool.addAction(QIcon('art/fullscreen.png'),
                                        u"Plein écran", self.fullScreen)
        tool.addAction(QIcon('art/options.png'), "Options", self.showOptions)
        
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
        self.currentEpisodeWidget.hide()
        palette = QPalette()
        palette.setColor(QPalette.Window, palette.color(QPalette.Window))
        self.currentEpisodeWidget.setPalette(palette)
        self.currentEpisodeWidget.setAutoFillBackground(True)
        self.currentEpisodeWidget.hide()
        
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