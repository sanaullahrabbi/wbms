# import sqlite3

# from PyQt5 import QtCore, QtGui, QtWidgets




# class LoginDialog(QtWidgets.QDialog):
#     def __init__(self, *args, **kwargs):
#         QtWidgets.QDialog.__init__(self, *args, **kwargs)
#         self.setupUi(self)
#         self.login_button.clicked.connect(self.login_check)

#     def login_check(self):
#         uname = self.U_name_text.text()
#         passw = self.pass_text.text()
#         connection = sqlite3.connect("login.db")
#         result = connection.execute("SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD = ?", (uname, passw))
#         if result.fetchall():
#             self.accept()
#         else:
#             print("invalid login")

# class WelcomeWindow(QtWidgets.QMainWindow):
#     def __init__(self, *args, **kwargs):
#         QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
#         self.setupUi(self)


# if __name__ == "__main__":
#     import sys

#     app = QtWidgets.QApplication(sys.argv)
#     login = LoginDialog()
#     w = WelcomeWindow()
#     if login.exec_() == QtWidgets.QDialog.Accepted:
#         username = login.U_name_text.text()
#         w.lineEdit.setText(username)
#         w.show()
#     sys.exit(app.exec_())



# import sys
# from PyQt5 import QtCore, QtWidgets
# from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
# from PyQt5.QtWidgets import QPushButton
# from PyQt5.QtWidgets import QMessageBox
# from PyQt5.QtCore import QSize    

# class MainWindow(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         self.clickMethod()     

#     def clickMethod(self):
#         QMessageBox.about(self, "Title", "Message")

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     mainWin = MainWindow()
#     mainWin.show()
#     sys.exit( app.exec_() )




# import sys

# from PyQt5.QtWidgets import *


# class CustomDialog(QMessageBox):
#     def __init__(self):
#         self.window = None
#         super().__init__()
#         # 
#         # if close == QMessageBox.Ok:
#         #     print("Ok Clicked")
#     # def closeEvent(self, event):
#     #     if self.close == QMessageBox.Yes:
#     #         event.accept()
#     #     else:
#     #         event.ignore()

# app = QApplication(sys.argv)

# window = CustomDialog()

# sys.exit(app.exec_())


# import sys
# from PyQt5.QtCore import *
# from PyQt5.uic import loadUi
# from PyQt5 import QtWidgets
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import QDialog, QApplication, QWidget,QMainWindow

# class DashboardView(QDialog):
#     IconSize = QSize(16, 16)
#     def __init__(self):
#         super(DashboardView, self).__init__()
#         loadUi("./ui/dialog.ui",self)
#         self.setWindowFlags(Qt.WindowStaysOnTopHint)
#         self.label_2.setPixmap(QPixmap("./icons/confirm.png"))

#         self.buttonBox.accepted.connect(self.lol)
#         self.buttonBox.rejected.connect(self.reject)

#     def lol(self):
#         print("sdfsdf")


# app = QApplication(sys.argv)
# w = DashboardView()
# w.show()
# sys.exit(app.exec_())


import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import pandas as pd

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

# class MainWindow(QtWidgets.QMainWindow):

#     def __init__(self):
#         super().__init__()

#         self.table = QtWidgets.QTableView()

#         data = pd.DataFrame([
#           [1, 9, 2],
#           [1, 0, -1],
#           [3, 5, 2],
#           [3, 3, 2],
#           [5, 8, 9],
#         ], columns = ['A', 'B', 'C'], index=['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'])

#         self.model = TableModel(data)
#         self.table.setModel(self.model)

#         self.setCentralWidget(self.table)


# app=QtWidgets.QApplication(sys.argv)
# window=MainWindow()
# window.show()
# app.exec_()