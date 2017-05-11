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

    class Sample(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Sampling.ui", self)

    class Statistics(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Statistics.ui", self)


class MainWindow(QtWidgets.QMainWindow):

    current_tree_item = 0

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("NewSHaRK.ui", self)
        self.treeWidget.expandAll()
        self.treeWidget.itemPressed.connect(self.tree_item)
        self.listWidget.model().rowsRemoved.connect(self.removed_item)
        self.listWidget.itemDoubleClicked.connect(self.current_item)
        self.listWidget.model().rowsInserted.connect(self.inserted_item)
        self.listWidget.model().rowsMoved.connect(self.moved_item)
        self.setAcceptDrops(True)
        self.workflow_list = []

    def tree_item(self, i):
        global current_tree_item
        current_tree_item = i.text(0)

    def add_to_workflow(self, block):
        block_class = getattr(WorkflowBlocks, block)
        instance = block_class()
        self.workflow_list.append(instance)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent):
        a0.accept()

    def dropEvent(self, a0: QtGui.QDropEvent):
        a0.accept()

    def current_item(self, i):
        print('Item Edit')
        ind = self.listWidget.indexFromItem(i)
        print(ind.row())
#        print(i.text())

    def removed_item(self, i, first):
        print('Item Removed')
        print(first)
        print(self.workflow_list.pop(first))

    def inserted_item(self, i, first):
        global current_tree_item
        block_class = getattr(WorkflowBlocks, current_tree_item)
        instance = block_class()
        if first > len(self.workflow_list)-1:
            self.workflow_list.append(instance)
        else:
            self.workflow_list.insert(first, instance)
        print('Item Inserted')
        print(first)
        print(current_tree_item)
        print(self.workflow_list)

    def moved_item(self, index, start, end, what, row):
        print('Item Moved')
        print(start, row)


app = QtWidgets.QApplication(sys.argv)
# QtWidgets.QApplication.setStyle('fusion')
main = MainWindow()
main.show()
sys.exit(app.exec_())
