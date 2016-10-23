import csv
import ntpath
import os
import sys

from Bio import SeqIO
from PyQt4 import QtGui, QtCore, uic

import func

del_option = 'delete'
del_factor = 0.00
elapsed = 0
input_file_path = []
shark_dir = ntpath.dirname(__file__)
white_logo = ntpath.join(shark_dir, r".\pic\256x256_WhiteLogo.png")


class PrefDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi("pref.ui", self)

        self.connect(self.save_syn_toolButton, QtCore.SIGNAL('clicked()'), self.append_syn)
        self.connect(self.show_syn_toolButton_3, QtCore.SIGNAL('clicked()'), self.show_syn_widget)

    def append_syn(self):
        new_syn_list = self.synonyms_lineEdit.text().split(',')
        with open('syn.csv', 'a') as syn:
            writer = csv.writer(syn, delimiter='\t')
            writer.writerow(new_syn_list)
        syn.close()

    def show_syn_widget(self):
        synonyms.show()
        synonyms.center()


class AboutDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi("about.ui", self)


class ReportWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

    def populate_vbox(self, stats_dict):
        vbox = QtGui.QVBoxLayout()
        for v, k in stats_dict.items():
            l = QtGui.QLabel()
            if v == "runtime":
                l.setText('<b>Runtime</b> was <b>%s</b>' % str(k))
            else:
                l.setText('There was <b>%s</b> <b>%s</b>' % (func.full_stats_dict[k], str(v)))
            l.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            vbox.addWidget(l)
        self.setLayout(vbox)

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


class StatsWidget(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        uic.loadUi("stats.ui", self)

    def populate_stats(self, show_option, stats_list):
        if show_option == "full":
            for stat in stats_list:
                vbox = QtGui.QVBoxLayout()
                self.populate_vbox(vbox, stat)
                self.horizontalLayout_2.addLayout(vbox)

            self.LeftArrow.setEnabled(False)
            self.RightArrow.setEnabled(False)
#        big_vbox.setContentsMargins(5, 5, 5, 5)

        self.setWindowIcon(QtGui.QIcon(white_logo))
        self.setWindowTitle('Input stats')
        self.startPush.clicked.connect(main.analyse_that)

    def populate_vbox(self, vbox, stats_dict):
        for k, v in reversed(stats_dict.items()):
            l = QtGui.QLabel()
            l.setText('<b>%s</b> is <b>%s</b> ' % (func.full_stats_dict[k], str(v)))
            l.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            vbox.addWidget(l)

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


class SynWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        vbox = QtGui.QVBoxLayout()
        preface = QtGui.QLabel()
        preface.setText('<b>The current tag synonyms look like this:</b>')
        vbox.addWidget(preface)
        for k in func.gene_synonyms:
            l = QtGui.QLabel()
            l.setText('%s' % (', '.join(k)))
            l.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            vbox.addWidget(l)
#        vbox.setContentsMargins(5, 5, 5, 5)

        self.setLayout(vbox)
        self.setWindowIcon(QtGui.QIcon(white_logo))
        self.setWindowTitle('Tag synonyms')

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


class MainWindow(QtGui.QMainWindow):
    alert = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi("window.ui", self)

        self.progressBar.reset()

        set_output = QtGui.QAction(QtGui.QIcon('output.png'), 'Save', self)
        set_output.setShortcut('Ctrl+S')
        set_output.setStatusTip('Choose output directory')
        self.connect(set_output, QtCore.SIGNAL('triggered()'), self.showDialogOutput)

        self.connect(self.outputfilepathButton, QtCore.SIGNAL('clicked()'), self.showDialogOutput)

        set_input = QtGui.QAction(QtGui.QIcon('input.png'), 'Open file', self)
        set_input.setShortcut('Ctrl+O')
        set_input.setStatusTip('Choose input files')
        self.connect(set_input, QtCore.SIGNAL('triggered()'), self.showDialogInput)

        self.connect(self.inputfilepathButton, QtCore.SIGNAL('clicked()'), self.showDialogInput)

        set_reference = QtGui.QAction(QtGui.QIcon('reference.png'), 'Add reference', self)
        set_reference.setShortcut('Ctrl+R')
        set_reference.setStatusTip('Add reference')
        self.connect(set_reference, QtCore.SIGNAL('triggered()'), self.showDialogReference)

        self.connect(self.referencepathButton, QtCore.SIGNAL('clicked()'), self.showDialogReference)

        set_pref = QtGui.QAction(QtGui.QIcon('preferences.png'), 'Preferences', self)
        set_pref.setShortcut('Ctrl+P')
        set_pref.setStatusTip('Edit program preferences')
        self.connect(set_pref, QtCore.SIGNAL('triggered()'), self.show_pref)

        exit_form = QtGui.QAction('Exit', self)
        exit_form.setShortcut('Ctrl+Q')
        exit_form.setStatusTip('Exit application')
        self.connect(exit_form, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        view_help = QtGui.QAction('Help', self)
        view_help.setShortcut('Ctrl+H')
        view_help.setStatusTip('View help')

        about = QtGui.QAction('About', self)
#        about.setShortcut('Ctrl+H')
        about.setStatusTip('About SHaRK')
        self.connect(about, QtCore.SIGNAL('triggered()'), self.show_about)

        self.deletionoptionCombo.activated.connect(self.set_del_option)
        self.deletionpercentDoubleSpinBox.valueChanged.connect(self.set_del_percent)
        self.percentageRadio.toggled.connect(self.set_del_percent)
        self.deletionnumberSpinBox.valueChanged.connect(self.set_del_number)
        self.numberRadio.toggled.connect(self.set_del_number)

        self.goDialogButtonBox.accepted.connect(self.first_step)
        self.goDialogButtonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.reset_main)
        self.range_comboBox.currentIndexChanged.connect(self.activate_percentile)

        self.alert.connect(self.showError)

        menu_bar = self.menuBar()
        file = menu_bar.addMenu('&File')
        file.addAction(set_input)
        file.addAction(set_reference)
        file.addAction(set_output)
        file.addAction(exit_form)
#        edit = menu_bar.addMenu('&Edit')
        settings = menu_bar.addMenu('&Settings')
        settings.addAction(set_pref)
        help = menu_bar.addMenu('&Help')
        help.addAction(view_help)
        help.addAction(about)

        self.center()

    def show_pref(self):
        pref_dialog.show()

    def show_about(self):
        about_dialog.show()

    def reset_main(self):
        self.inputfilepathLine.clear()
        self.outputfilepathLine.clear()
        self.referencepathLine.clear()
        self.req_tags_Line.clear()
        self.un_tags_Line.clear()
        self.deleterepeatsBox.setChecked(False)
        self.uniteBox.setChecked(False)

        self.gap_spinBox.setValue(-200)
        self.iters_spinBox.setValue(1)
        self.diagonal_checkBox.setChecked(False)
        self.silent_checkBox.setChecked(True)
        self.alignstat_checkBox.setChecked(False)
        self.trunc_checkBox.setChecked(False)
        self.range_comboBox.setCurrentIndex(2)
        self.perc_doubleSpinBox.setValue(25)

        self.checksourceBox.setChecked(True)
        self.showresultsBox.setChecked(False)
        self.copiesnumberSpinBox.setValue(0)
        self.deletionoptionCombo.setCurrentIndex(0)
        self.deletionpercentDoubleSpinBox.setValue(0)
        self.deletionnumberSpinBox.setValue(0)
        self.percentageRadio.setChecked(True)



    def set_del_option(self):
        global del_option
        index = self.deletionoptionCombo.currentIndex()
        if index == 0:
            del_option = 'delete'
        elif index == 1:
            del_option = 'leave'
        print(del_option)
        return del_option

    def set_del_percent(self):
        global del_factor
        del_factor = round(self.deletionpercentDoubleSpinBox.value(), 5)
        print(del_factor)
        return del_factor

    def set_del_number(self):
        global del_factor
        del_factor = self.deletionnumberSpinBox.value()
        print(del_factor)
        return del_factor

    def activate_percentile(self, index):
        if index == 4:
            self.perc_doubleSpinBox.setEnabled(True)
        else:
            self.perc_doubleSpinBox.setEnabled(False)

    def showDialogOutput(self):
        global output_dir
        check = QtGui.QFileDialog.getExistingDirectory(self, 'Open file', '/home')
        if check != '':
            output_dir = check
        self.outputfilepathLine.setText(output_dir)
        print(output_dir)

    def showDialogInput(self):
        global input_file_path
        check = QtGui.QFileDialog.getOpenFileNames(self, 'Open file', '/home',
                                                   '''FASTA files (*.fas *.fasta);;
GenBank files (*.gbk *.gb);;
Any files (*.*)''')
        if check:
            input_file_path = check
            self.inputfilepathLine.setText(str(input_file_path))
        print(input_file_path[0])

    def check_unite_bool(self):
        global check_unite
        check_unite = self.uniteBox.isChecked()
        print(check_unite)
        return check_unite

    def showDialogReference(self):
        check = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home', 'Any files (*.*)')
        if check:
            reference_path = check
            self.referencepathLine.setText(reference_path)
            print(reference_path)

    def first_step(self):
        global param_dict
        global session_report
        session_report = func.SessionStats()

        param_dict = {"output_directory": self.outputfilepathLine.text(),
                      "reference_path": self.referencepathLine.text(),
                      "positive_tags": self.req_tags_Line.text(),
                      "negative_tags": self.un_tags_Line.text(),
                      "delete_repeats": self.deleterepeatsBox.isChecked(),
                      "unite_bool": self.uniteBox.isChecked(),
                      "copies_number": self.copiesnumberSpinBox.value(),
                      "deletion_factor": del_factor,
                      "deletion_option": del_option,
                      "source_bool": self.checksourceBox.isChecked(),
                      "percentage_toggled": self.percentageRadio.isChecked(),
                      "stats_option": "full",
                      "reference_target_range": [85, 674]}

        if param_dict["stats_option"] == "full":
            stats_list = []
            for path in input_file_path:
                stats = func.range_stats(func.read_check(path, False, False, '.fas'))
                stats["file"] = os.path.basename(path)
                stats_list.append(stats)
            stats_widget.populate_stats("full", stats_list)
            stats_widget.show()
            stats_widget.center()

    def analyse_that(self):
        global session_report

        output_dir = self.outputfilepathLine.text()
        output_dir += os.sep
        counter = 0
        if not self.inputfilepathLine.text():
            print('missing input file path')
            counter += 1
        elif not self.outputfilepathLine.text():
            print('output directory is missing')
            counter += 1
        for path in input_file_path:
            if os.path.isfile(path) is False:
                counter += 1
                print('input path is wrong')
            else:
                session_report.i_files += 1
        if self.referencepathLine.text() != '' and os.path.isfile(self.referencepathLine.text()) is False:
            counter += 1
            print('reference path is wrong')
        if counter == 0:

            self.statusBar.showMessage('Preparing to process %i files' % len(input_file_path))
            self.progressBar.setEnabled(True)
            file_sizes = []

            for path in input_file_path:
                p = open(path, 'r')
                seqs = SeqIO.parse(p, 'fasta')
                size = 0
                for s in seqs:
                    size += 1
                p.close()

                session_report.i_seqs += 1
                file_sizes.append(size)
            work_range = 0
            for s in file_sizes:
                work_range += s
            self.progressBar.setRange(0, work_range)
            progress_value = 0
            if self.referencepathLine.text() != '':
                r = open(self.referencepathLine.text(), 'r')
                ref = SeqIO.read(r, 'fasta')
                r.close()
            else:
                ref = ''
            united_name = ''
            if self.uniteBox.isChecked() is True:
                session_report.o_files += 1
                united_name += output_dir
                for path in input_file_path:
                    united_name += (ntpath.basename(path)[0: len(ntpath.basename(path)) - 4])
                    if input_file_path.index(path) != len(input_file_path) - 1:
                        united_name += '+'
                united_name += '.fas'
            for path in input_file_path:
                self.statusBar.showMessage('Last file processed in %f seconds' % func.file_analysis(param_dict, path,
                                                                                                    session_report))
                print(path)
                progress_value += file_sizes[input_file_path.index(path)]
                self.progressBar.setValue(progress_value)
            self.statusBar.showMessage('Processing finished')
            self.showReport()
        else:
            self.alert.emit()
        self.progressBar.reset()
        self.progressBar.setEnabled(False)

    def showReport(self):
        global report
        report = ReportWidget()
        report.populate_vbox(session_report.produce_dict())
        report.show()
        report.center()

    def showError(self):
        QtGui.QErrorMessage().qtHandler().showMessage('Invalid input data! Please, check again carefully.')

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Exit application', "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


app = QtGui.QApplication(sys.argv)
QtGui.QApplication.setStyle('plastique')
pref_dialog = PrefDialog()
about_dialog = AboutDialog()
stats_widget = StatsWidget()
synonyms = SynWidget()
main = MainWindow()
main.show()
sys.exit(app.exec_())

