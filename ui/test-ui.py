from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys


class WorkflowBlocks:
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
        self.listWidget.model().rowsRemoved.connect(self.removed_item)
        self.listWidget.itemDoubleClicked.connect(self.current_item)
        self.listWidget.model().rowsInserted.connect(self.inserted_item)
        self.listWidget.model().rowsMoved.connect(self.moved_item)
        self.setAcceptDrops(True)
        self.workflow_list = []

    def add_to_workflow(self, block):
        block_class = getattr(WorkflowBlocks, block)
        instance = block_class()
        self.workflow_list.append(instance)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent):
        a0.accept()

    def dropEvent(self, a0: QtGui.QDropEvent):
        a0.accept()

    def current_item(self):
        i = self.listWidget.currentItem()
        ind = self.listWidget.indexFromItem(i)
        print(i.text())
        print(ind.row())

    def removed_item(self, i, first):
        print('Item Removed')
        print(first)

    def inserted_item(self, i, first):
        print('Item Inserted')
        print(first)
        print(self.listWidget.item(first))

    def moved_item(self, index, start, end, what, row):
        print('Item Moved')
        print(start, row)


app = QtWidgets.QApplication(sys.argv)
#QtWidgets.QApplication.setStyle('fusion')
main = MainWindow()
main.show()
sys.exit(app.exec_())
