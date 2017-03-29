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

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("NewSHaRK.ui", self)
        self.treeWidget.expandAll()
#        self.listWidget.currentItemChanged.connect(self.list_current_item)
        self.listWidget.itemDoubleClicked.connect(self.list_current_item)

    def list_current_item(self):
        i = self.listWidget.currentItem()
        print(i.text())
        if i.text() == 'Single':
            align.show()


app = QtWidgets.QApplication(sys.argv)
# QtWidgets.QApplication.setStyle('fusion')
align = Alignment()
main = MainWindow()
main.show()
sys.exit(app.exec_())
