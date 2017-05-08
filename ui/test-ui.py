from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys


class Alignment(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        uic.loadUi("Alignment.ui", self)


class Filtering(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        uic.loadUi("Filtering.ui", self)


class Input(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        uic.loadUi("Input.ui", self)


class Output(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        uic.loadUi("Output.ui", self)


class Sampling(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        uic.loadUi("Sampling.ui", self)


class Statistics(QtWidgets.QDialog):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        uic.loadUi("Statistics.ui", self)


class MainWindow(QtWidgets.QMainWindow):

    workflow_list = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("NewSHaRK.ui", self)
        self.treeWidget.expandAll()
#        self.listWidget.currentItemChanged.connect(self.list_current_item)
        self.listWidget.itemDoubleClicked.connect(self.list_current_item)
        self.listWidget.model().rowsInserted.connect(self.inserted_item)
        self.listWidget.model().rowsMoved.connect(self.moved_item)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent):
        a0.accept()

    def dropEvent(self, a0: QtGui.QDropEvent):
        a0.accept()

    def list_current_item(self):
        i = self.listWidget.currentItem()
        ind = self.listWidget.indexFromItem(i)
        print(i.text())
        print(ind.row())

    def inserted_item(self, i, first):
        print('Item Inserted')
        print(first)

    def moved_item(self, index, start, end, what, row):
        print('Moved item')
        print(start, row)



app = QtWidgets.QApplication(sys.argv)
# QtWidgets.QApplication.setStyle('fusion')
main = MainWindow()
main.show()
sys.exit(app.exec_())
