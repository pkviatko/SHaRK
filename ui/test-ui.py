import sys

from PyQt5 import QtGui, QtWidgets, uic


class WorkflowBlocks:

    class Input(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Input.ui", self)

    class Output(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Output.ui", self)

    class Filtering(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Filtering.ui", self)

    class Reduction(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Reduction.ui", self)

    class Sampling(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Sampling.ui", self)

    class Splitting(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Splitting.ui", self)

    class Integration(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Integration.ui", self)

    class Alignment(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)
            uic.loadUi("Alignment.ui", self)

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

    def current_item(self, item):
        # print('Item Edit')
        ind = self.listWidget.indexFromItem(item)
        # print(ind.row())
        self.workflow_list[ind.row()].show()

    def removed_item(self, i, position):
        print('Item Removed')
        print(position)
        print(self.workflow_list.pop(position))

    def inserted_item(self, i, position):
        global current_tree_item
        block_class = getattr(WorkflowBlocks, current_tree_item)
        instance = block_class()
        if position > len(self.workflow_list)-1:
            self.workflow_list.append(instance)
        else:
            self.workflow_list.insert(position, instance)
        # print('Item Inserted')
        # print(first)
        # print(current_tree_item)
        print(self.workflow_list)

    def moved_item(self, index, start, end, what, row):
        print('Item Moved')
        print(start, row)
        n_blocks = len(self.workflow_list)
        block_moved = self.workflow_list.pop(start)
        if row == n_blocks:
            self.workflow_list.append(block_moved)
        elif row < start:
            self.workflow_list.insert(row, block_moved)
        elif row > start:
            self.workflow_list.insert(row-1, block_moved)
        print(self.workflow_list)


app = QtWidgets.QApplication(sys.argv)
# QtWidgets.QApplication.setStyle('fusion')
main = MainWindow()
main.show()
sys.exit(app.exec_())
