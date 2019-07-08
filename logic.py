import json
import threading
from time import sleep

from PyQt5 import QtWidgets, QtGui, QtCore

import courseparser as cp
from ui_design import Ui_MainWindow  # importing our generated file


class mywindow(QtWidgets.QMainWindow):

    def __init__(self):
        self.grades = []
        self.gotGrades = False
        self.lastCourse = ""
        self.lastSemester = ""
        self.lastYear = ""
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pass_in.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.getGradesButton.clicked.connect(self.updateGrades)
        self.ui.soundNotification.isChecked()
        self.gotGrades = False
        self.ui.stop_button.clicked.connect(self.stopTracking)
        self.ui.start_button.clicked.connect(self.trackGrades)
        self.threads = []
        self.stopPressed = []
        self.currentThread = -1

    def cacheUserName(self):
        self.ui.id_in.text()
        try:
            read_write_file = open("settings.json", "r+")
            if read_write_file:
                data = json.load(read_write_file)
                data['user_name'] = self.ui.id_in.text()
                data['dimensions'][0]['width'] = self.width()
                data['dimensions'][0]['height'] = self.height()
                read_write_file.seek(0)
                json.dump(data, read_write_file, indent=4)
                read_write_file.truncate()
        except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
            pass

    # Closing main windows override, check if there is unsaved data and prompts the user if so for save
    def closeEvent(self, event):
        self.cacheUserName()
        return super().closeEvent(event)

    def getDate(self):
        if self.ui.semester_in.currentText() == 'Winter':
            return self.ui.year_in.text() + '01'
        elif self.ui.semester_in.currentText() == 'Spring':
            return str(int(self.ui.year_in.text()) - 1) + '02'
        elif self.ui.semester_in.currentText() == 'Summer':
            return str(int(self.ui.year_in.text()) - 1) + '03'
        else:
            return 'WTF is wrong Technion?'

    def getGrades(self):
        doNotProceed = False
        self.lastYear = self.ui.year_in.text()
        self.lastSemester = self.ui.semester_in.currentText()
        self.lastCourse = self.ui.course_in.text()
        if self.ui.pass_in.text() == "" or self.ui.course_in.text() == "" or self.ui.id_in.text() == "":
            return
        package = cp.preparePackage(self.ui.course_in.text(), self.ui.id_in.text(), self.ui.pass_in.text(),
                                    self.getDate())
        self.grades = cp.getGrades(package)

    def showdialog(self, params):
        msg = QtWidgets.QMessageBox()
        string = ""
        counter = 0
        if len(params) > 1:
            if len(params) > 2:
                for a in range(0, len(params) - 2):
                    string += params[a] + ", "
                    counter = a
                string += params[counter + 1] + " and " + params[counter + 2]
            else:
                string = params[0] + " and " + params[1]
        else:
            string = params[0]
        msg.setText("Please enter valid " + string)
        msg.setWindowTitle("Input error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = msg.exec_()

    def errorMessage(self):
        if self.ui.pass_in.text() == "" or self.ui.course_in.text() == "" or self.ui.id_in.text() == "":
            a = []
            if self.ui.pass_in.text() == "":
                a.append("password")
            if self.ui.course_in.text() == "":
                a.append("Course number")
            if self.ui.id_in.text() == "":
                a.append("ID")
            self.showdialog(a)
            return
        else:
            self.showdialog(["Something went wrong, retry later!"])
            return

    def updateGrades(self):
        changedInput = (self.lastCourse != self.ui.course_in.text()) or \
                       (self.lastSemester != self.ui.semester_in.currentText()) or \
                       (self.lastYear != self.ui.year_in.text())
        notify = False
        self.getGrades()
        if self.grades == []:
            self.errorMessage()
            return
        for column in range(0, len(self.grades[0])):
            if not self.gotGrades:
                self.ui.grades_table.setColumnCount(len(self.grades[0]))
                self.ui.grades_table.setRowCount(len(self.grades))
                for col in range(0, len(self.grades[0])):
                    for row in range(0, len(self.grades)):
                        item = QtWidgets.QTableWidgetItem()
                        self.ui.grades_table.setItem(row, column, item)
                for row in range(0, len(self.grades)):
                    self.ui.grades_table.item(row, column).setText(self.grades[row][column])
            else:
                try:
                    self.ui.grades_table.setColumnCount(len(self.grades[0]))
                    self.ui.grades_table.setRowCount(len(self.grades))
                    newGrades = []
                    for row in range(0, len(self.grades)):
                        newGrades.append(QtWidgets.QTableWidgetItem(self.grades[row][column]))
                    if not changedInput and \
                            ((newGrades[0] and self.ui.grades_table.item(0, column).text() != newGrades[0].text()) or \
                             (newGrades[1] and self.ui.grades_table.item(1, column).text() != newGrades[1].text())):
                        notify = True
                        brush = QtGui.QBrush(QtGui.QColor(58, 213, 34))
                        brush.setStyle(QtCore.Qt.NoBrush)
                        for row in range(0, len(self.grades)):
                            newGrades[row].setForeground(brush)
                    for row in range(0, len(self.grades)):
                        self.ui.grades_table.setItem(row, column, newGrades[row])
                except ValueError or TypeError:
                    for row in range(0, len(self.grades)):
                        self.ui.grades_table.setItem(row, column, QtWidgets.QTableWidgetItem(newGrades[row]))
        if (len(self.grades[0]) > 0) and not self.ui.stop_button.isEnabled():
            self.ui.start_button.setEnabled(True)
            self.ui.start_button.setToolTip("")
        self.playSound(notify)
        self.gotGrades = True

    def playSound(self, notify):
        if notify and self.ui.soundNotification.isChecked():
            cp.makeSound(duration=0.5, frequency=800)

    def trackGrades(self):
        self.ui.start_button.setEnabled(False)
        self.ui.start_button.setToolTip("Tracker already running")
        self.ui.stop_button.setEnabled(True)
        self.ui.stop_button.setToolTip("")

        if len(self.threads) > 0 and self.threads[0] and self.threads[0].isAlive():
            self.threads.append(threading.Thread(target=lambda: self.trackGradesAux(self.currentThread)))
            self.stopPressed.append(False)
            self.threads[self.currentThread].start()
        else:
            self.currentThread = 0
            self.tryToShrink()
            if len(self.threads) == 0:
                self.threads.append(threading.Thread(target=lambda: self.trackGradesAux(self.currentThread)))
            else:
                self.threads[0] = threading.Thread(target=lambda: self.trackGradesAux(self.currentThread))
            if len(self.stopPressed) == 0:
                self.stopPressed.append(False)
            else:
                self.stopPressed[0] = False
            self.threads[0].start()

    def tryToShrink(self):
        counter = 0
        for i in range(len(self.threads) - 1, -1, -1):
            if not self.threads[i].isAlive():
                counter += 1
        if counter != 0:
            self.threads = self.threads[:-counter]
            self.stopPressed = self.stopPressed[:-counter]

    def trackGradesAux(self, threadNumber):
        while True:
            sleep(int(self.ui.frequency_spin.text()))
            if len(self.stopPressed) - 1 < threadNumber or self.stopPressed[threadNumber]:
                return
            self.updateGrades()

    def stopTracking(self):

        self.stopPressed[self.currentThread] = True
        self.currentThread += 1
        self.ui.start_button.setEnabled(True)
        self.ui.start_button.setToolTip("")
        self.ui.stop_button.setEnabled(False)
        self.ui.stop_button.setToolTip("Tracker isn't running")
