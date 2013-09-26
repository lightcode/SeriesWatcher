#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Matthieu GAIGNIÈRE
#
# This file is part of SeriesWatcher.
#
# SeriesWatcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# SeriesWatcher is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# SeriesWatcher. If not, see <http://www.gnu.org/licenses/>.


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