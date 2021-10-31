import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QWidget,QMainWindow

from methodWork import AutomateMSGSender




class LoginView(QDialog):
    def __init__(self):
        super(LoginView, self).__init__()
        loadUi("login.ui",self)
        self.login.clicked.connect(self.gotodashboard)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)

    
    def gotodashboard(self):
        username = self.usernamefield.text()
        password = self.passwordfield.text()

        if len(username)==0 or len(password)==0:
            self.error.setText("Please input all fields.")

        else:
            res_username = 'admin'
            res_password = 'admin'
            if username == res_username and password == res_password:
                dashboard = DashboardView()
                widget.setWindowTitle('Dashboard')
                widget.setFixedHeight(510)
                widget.setFixedWidth(800)
                widget.addWidget(dashboard)
                widget.setCurrentIndex(widget.currentIndex()+1)
                self.error.setText("")
            else:
                self.error.setText("Invalid username or password")




class DashboardView(QMainWindow):
    def __init__(self):
        super(DashboardView, self).__init__()
        loadUi("dashboard.ui",self)

        qpixmap = QPixmap('../Design File/icons/logo.png')
        self.bgimg.setPixmap(qpixmap)

        self.pushButton_send.clicked.connect(self.sendsinglesms)

        self.w = []

    def sendsinglesms(self):
        sendSingleSMS = SendSingleSMSView()
        sendSingleSMS.setWindowTitle('Single SMS')
        sendSingleSMS.setFixedHeight(400)
        sendSingleSMS.setFixedWidth(800)
        # widget.addWidget(sendSingleSMS)
        # widget.setCurrentIndex(widget.currentIndex()+1)
        self.w.append(sendSingleSMS) 
        self.w[-1].show()


class SendSingleSMSView(QDialog):
    def __init__(self):
        super(SendSingleSMSView, self).__init__()
        loadUi("sendsinglesms.ui",self)
        combo_list = ['Select Templates', 'Teamplate1', 'Teamplate2']
        self.comboBox.addItems(combo_list)

        self.pushButton_send.clicked.connect(self.sendMessage)

    def sendMessage(self):
        number_value = self.singlenumber.text()
        AutomateMSGSender(number_value)

# main
app = QApplication(sys.argv)
login = LoginView()
widget = QtWidgets.QStackedWidget()
widget.addWidget(login)
widget.setWindowTitle('Login')
widget.setFixedHeight(400)
widget.setFixedWidth(600)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")



# Importent code line
# self.w = []
# self.w.append(PopupWindow(self)) 
# self.w[-1].show()









