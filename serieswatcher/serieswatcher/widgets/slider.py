#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


from PyQt4 import QtGui


def timeToText(time):
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
        self.setToolTip(timeToText(self._duration * k))
        super(Slider, self).mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        k = event.x() / float(self.width())
        a = k * self.maximum()
        self.setValue(a)
        self.sliderMoved.emit(self.value())
        super(Slider, self).mousePressEvent(event)
    
    def setDuration(self, duration):
        self._duration = duration / 1000.