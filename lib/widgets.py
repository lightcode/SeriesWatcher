# -*-coding: utf8-*-
import os.path
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

class SelectFolder(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.label = QtGui.QLineEdit()
        btn = QtGui.QPushButton('Parcourir')
        btn.clicked.connect(self.selectFolder)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(btn)
        self.setLayout(layout)
    
    
    def selectFolder(self):
        path = QtGui.QFileDialog.getExistingDirectory()
        path = '%s/*' % path
        self.label.setText(path)
    
    
    def path(self):
        return self.label.text()
    
    
    def setPath(self, path):
        self.label.setText(path)


class EpisodesViewer(QtGui.QTableWidget):
    # Signals :
    pressEnter = QtCore.pyqtSignal('QModelIndex')
    refreshEpisodes = QtCore.pyqtSignal()
    markedAsView = QtCore.pyqtSignal()
    markedAsNotView = QtCore.pyqtSignal()
    
    nbColumn = 3
    columnWidth = 260
    rowHeight = 100
    
    
    def __init__(self, parent = None):
        super(EpisodesViewer, self).__init__(parent)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        #self.setAcceptDrops(True)
    
    
    def contextMenu(self, pos):
        globalPos = self.mapToGlobal(pos)
        
        nbNone = 0
        for item in self.selectedIndexes():
            (r, c) = (item.row(), item.column())
            if not self.cellWidget(r, c):
                nbNone += 1
        if nbNone == len(self.selectedIndexes()):
            return
        
        menu = QtGui.QMenu()
        markAsView = menu.addAction('Marquer comme vu')
        markAsView.setIcon(QtGui.QIcon('art/check.png'))
        markAsView.triggered.connect(self.markAsView)
        
        markAsNotView = menu.addAction('Marquer comme non vu')
        markAsNotView.setIcon(QtGui.QIcon('art/uncheck.png'))
        markAsNotView.triggered.connect(self.markAsNotView)
        menu.exec_(globalPos)
    
    
    def markAsView(self):
        self.markedAsView.emit()
    
    
    def markAsNotView(self):
        self.markedAsNotView.emit()
    
    
    def setRowCount(self, nbRows):
        QtGui.QTableWidget.setRowCount(self, nbRows)
        [self.setRowHeight(i, self.rowHeight) for i in xrange(nbRows)]
    
    
    def setColumnCount(self, nbColumn):
        QtGui.QTableWidget.setColumnCount(self, nbColumn)
        [self.setColumnWidth(i, self.columnWidth) for i in xrange(nbColumn)]
    
    
    def keyPressEvent(self, e):
        QtGui.QTableWidget.keyPressEvent(self, e)
        key = e.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.pressEnter.emit(self.currentIndex())
    
    
    def resizeEvent(self, size):
        QtGui.QTableWidget.resizeEvent(self, size)
        oldNbColumn = size.oldSize().width() // 260
        self.nbColumn = size.size().width() // 260
        self.columnWidth = size.size().width() // self.nbColumn
        self.setColumnCount(self.nbColumn)
        if oldNbColumn != self.nbColumn:
            self.setColumnCount(self.nbColumn)
            self.refreshEpisodes.emit()
    
    """
    def dragEnterEvent(self, event):
        QtGui.QTableWidget.dragEnterEvent(self, event)
        authorizedExt = ('mp4', 'avi', 'wmv', 'flv', 'mkv')
        for url in event.mimeData().urls():
            path = unicode(url.toLocalFile())
            ext = path.split('.')[-1].lower()
            if ext not in authorizedExt:
                return
        event.acceptProposedAction()
    
    
    def dragMoveEvent(self, event):
        event.acceptProposedAction()
    
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = unicode(url.toLocalFile())
            print path
    """



class VideoItem(QtGui.QWidget):
    def __init__(self, titleStr):
        QtGui.QWidget.__init__(self)
        
        self.img = QtGui.QLabel()
        self.img.setMaximumWidth(120)
        
        self.title = QtGui.QLabel(titleStr)
        self.title.setAlignment(Qt.AlignTop)
        self.title.setStyleSheet('padding-top:10px')
        self.title.setWordWrap(True)
        
        self.infos = QtGui.QLabel()
        self.infos.setAlignment(Qt.AlignBottom)
        
        text = QtGui.QVBoxLayout()
        text.addWidget(self.title)
        text.addWidget(self.infos)
        
        cell = QtGui.QHBoxLayout()
        cell.addWidget(self.img)
        cell.addLayout(text)
        
        self.setLayout(cell)
    
    
    def setImage(self, image):
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.img.setPixmap(pixmap)
    
    
    def setTitle(self, titleStr):
        self.title.setText(titleStr)
    
    
    def setInfos(self, infos):
        text = ''
        commonStyle = 'padding-left:1px;padding-bottom:5px'
        if infos == 1:
            self.infos.setStyleSheet('color:#777;' + commonStyle)
            text = u'Téléchargé'
        elif infos == 2:
            self.infos.setStyleSheet('color:red;' + commonStyle)
            text = u'Téléchargé <sup>Nouveau</sup>'
        self.infos.setText(text)