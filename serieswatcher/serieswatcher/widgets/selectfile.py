# -*- coding: utf-8 -*-

from PyQt4 import QtGui


class SelectFile(QtGui.QWidget):
    def __init__(self, path='', parent=None):
        super(SelectFile, self).__init__(parent)
        self.label = QtGui.QLineEdit()
        btn = QtGui.QPushButton('Parcourir')
        btn.clicked.connect(self.selectFile)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(btn)
        self.setLayout(layout)
        self.setPath(path)

    def selectFile(self):
        directory = os.path.basename(self.path())
        path = QtGui.QFileDialog.getOpenFileName(self, directory=directory)
        self.label.setText(path)

    def path(self):
        return str(self.label.text())

    def setPath(self, path):
        if not path:
            path = ""
        self.label.setText(path)
