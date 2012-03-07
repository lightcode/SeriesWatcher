# -*-coding: utf8-*-
from PyQt4 import QtCore, QtGui
from config import Config
from widgets import SelectFolder
from addSerie import AddSerie

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
        
        tool = QtGui.QToolBar()
        tool.setStyleSheet('border:none')
        tool.addAction(QtGui.QIcon('art/add.png'), u'Ajouter une série', self.add)
        tool.addSeparator()
        tool.addAction(QtGui.QIcon('art/up.png'), 'Monter', self.upItem)
        tool.addAction(QtGui.QIcon('art/down.png'), 'Descendre', self.downItem)
        tool.addAction(QtGui.QIcon('art/delete.png'), u'Supprimer cette série', self.delete)
        
        layoutButton = QtGui.QHBoxLayout()
        layoutButton.addWidget(tool)
        
        layoutList = QtGui.QVBoxLayout()
        layoutList.addWidget(self.listWidget)
        layoutList.addLayout(layoutButton)
        
        self.setLayout(layoutList)
    
    
    def add(self):
        addSerie = AddSerie(self)
        addSerie.serieAdded.connect(self.serieAdded)
        addSerie.open()
    
    
    def delete(self):
        currentIndex = self.listWidget.currentIndex().row()
        item = self.listWidget.takeItem(currentIndex)
        del item
    
    
    def serieAdded(self, name, title, tvDbId, lang, path):
        item = QtGui.QListWidgetItem(title)
        setattr(item, 'name', name)
        setattr(item, 'path', path)
        setattr(item, 'lang', lang)
        setattr(item, 'tvDbId', tvDbId)
        self.listWidget.addItem(item)
    
    
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
            title = unicode(self.listWidget.item(i).text())
            name = self.listWidget.item(i).name
            path = self.listWidget.item(i).path
            lang = self.listWidget.item(i).lang
            tvDbId = self.listWidget.item(i).tvDbId
            items.append([name, title, path, tvDbId, lang])
        return items



class EditSeries(QtGui.QDialog):
    # Signals :
    edited = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Editer les séries')
        
        # Select serie pannel
        self.listSeries = ListSeries()
        self.listSeries.itemSelectionChanged.connect(self.itemSelectionChanged)
        
        # Edit serie pannel
        self.title = QtGui.QLineEdit()
        self.title.textChanged.connect(self.listSeries.setTitle)
        self.path = SelectFolder()
        
        form = QtGui.QFormLayout()
        form.addRow('Titre', self.title)
        form.addRow(self.path)
        
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Sauvegarder', QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.save)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.close)
        
        # Make a layout and go...
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.listSeries)
        layout.addLayout(form)
        
        bigLayout = QtGui.QVBoxLayout()
        bigLayout.addLayout(layout)
        bigLayout.addWidget(buttonBox)
        
        self.setLayout(bigLayout)
    
    
    def itemSelectionChanged(self, title, path, lang):
        self.title.setText(title)
        self.path.setPath(path)
    
    
    def save(self):
        Config.series = self.listSeries.getItems()
        Config.save()
        self.edited.emit()
        self.close()