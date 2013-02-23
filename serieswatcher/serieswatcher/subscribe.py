from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

class SubscribeWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SubscribeWindow, self).__init__(parent)
        self.setWindowTitle('Inscription')
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)
        
        
        self.syncUser = QtGui.QLineEdit()
        self.syncPassword1 = QtGui.QLineEdit()
        self.syncPassword1.setEchoMode(QtGui.QLineEdit.Password)
        self.syncPassword2 = QtGui.QLineEdit()
        self.syncPassword2.setEchoMode(QtGui.QLineEdit.Password)
        
        layout = QtGui.QFormLayout()
        layout.addRow("Nom d'utilisateur", self.syncUser)
        layout.addRow('Mot de passe', self.syncPassword1)
        layout.addRow('Retaper le mot de passe', self.syncPassword2)
        
        formWidget = QtGui.QWidget()
        formWidget.setLayout(layout)
        
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton('Envoyer', QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.subscribe)
        buttonBox.addButton('Annuler', QtGui.QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.close)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(formWidget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
    
    
    def subscribe(self):
        pass



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    sw = SubscribeWindow()
    sw.show()
    sys.exit(app.exec_())