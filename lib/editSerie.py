# -*-coding: utf8-*-
from PyQt4 import QtCore, QtGui
from config import Config
from widgets import SelectFolder

class ListSeries(QtGui.QWidget):
    # Signals :
    itemSelectionChanged = QtCore.pyqtSignal('QString', 'QString', 'QString')
    
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        
        self.listWidget = QtGui.QListWidget()
        for serie in Config.series:
            name, title, path, tvDbId, lang = serie
            item = QtGui.QListWidgetItem(title)
            setattr(item, 'name', name)
            setattr(item, 'path', path)
            setattr(item, 'lang', lang)
            setattr(item, 'tvDbId', tvDbId)
            self.listWidget.addItem(item)
        self.listWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        
        btnUp = QtGui.QPushButton('Monter')
        btnUp.clicked.connect(self.upItem)
        btnDown = QtGui.QPushButton('Descendre')
        btnDown.clicked.connect(self.downItem)
        
        layoutButton = QtGui.QHBoxLayout()
        layoutButton.addWidget(btnUp)
        layoutButton.addWidget(btnDown)
        
        layoutList = QtGui.QVBoxLayout()
        layoutList.addWidget(self.listWidget)
        layoutList.addLayout(layoutButton)
        
        self.setLayout(layoutList)
    
    
    def _itemSelectionChanged(self):
        currentIndex = self.listWidget.currentIndex().row()
        title = self.listWidget.item(currentIndex).text()
        path = self.listWidget.item(currentIndex).path
        lang = self.listWidget.item(currentIndex).lang
        self.itemSelectionChanged.emit(title, path, lang)
    
    
    def upItem(self):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.takeItem(currentIndex)
        self.listWidget.insertItem(currentIndex - 1, currentItem)
        self.listWidget.setCurrentRow(currentIndex - 1)
    
    
    def downItem(self):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.takeItem(currentIndex)
        self.listWidget.insertItem(currentIndex + 1, currentItem)
        self.listWidget.setCurrentRow(currentIndex + 1)
    
    
    def setTitle(self, title):
        currentIndex = self.listWidget.currentIndex().row()
        currentItem = self.listWidget.item(currentIndex)
        currentItem.setText(title)
    
    
    def getItems(self):
        nb = self.listWidget.count()
        items = []
        for i in xrange(nb):
            title = str(self.listWidget.item(i).text())
            name = self.listWidget.item(i).name
            path = self.listWidget.item(i).path
            lang = self.listWidget.item(i).lang
            tvDbId = self.listWidget.item(i).tvDbId
            items.append([name, title, path, tvDbId, lang])
        return items



class EditSerie(QtGui.QDialog):
    # Signals :
    edited = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Editer la série')
        
        # Select serie pannel
        self.listSeries = ListSeries()
        self.listSeries.itemSelectionChanged.connect(self.itemSelectionChanged)
        
        # Edit serie pannel
        self.title = QtGui.QLineEdit()
        self.title.textChanged.connect(self.listSeries.setTitle)
        self.path = SelectFolder()
        btnSave = QtGui.QPushButton('Sauvegarder')
        btnSave.clicked.connect(self.save)
        
        form = QtGui.QFormLayout()
        form.addRow('Titre', self.title)
        form.addRow(self.path)
        form.addRow(btnSave)
        
        # Make a layout and go...
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.listSeries)
        layout.addLayout(form)
        
        self.setLayout(layout)
    
    
    def itemSelectionChanged(self, title, path, lang):
        self.title.setText(title)
        self.path.setPath(path)
    
    
    def save(self):
        Config.series = self.listSeries.getItems()
        Config.save()
        self.edited.emit()
        self.close()