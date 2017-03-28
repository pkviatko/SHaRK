from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys


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


app = QtWidgets.QApplication(sys.argv)
# QtWidgets.QApplication.setStyle('fusion')
main = MainWindow()
main.show()
sys.exit(app.exec_())
