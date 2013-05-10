from PyQt4 import QtCore

class Runnable(QtCore.QRunnable):
    """Generic runnable to use with QThreadPool."""
    def __init__(self, task):
        QtCore.QRunnable.__init__(self)
        self.task = task

    def run(self):
        self.task.run()