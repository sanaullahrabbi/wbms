import sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtWidgets import QDialog,QMainWindow,QTableView,QMessageBox,QCompleter,QApplication,QLineEdit,QFileDialog
from PyQt5.QtCore import Qt,QAbstractTableModel,QThread,pyqtSignal
from utils import sqlInsertTContact,sqlInsertTemplate, sqlUpdateContact, sqlUpdateTemplate, connect
import pandas as pd
import sqlite3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException,WebDriverException
from webdriver_manager import chrome,microsoft,opera
import PySimpleGUI as sg
import time
import shutil
from pathlib import Path
import os

def page_is_loading(driver):
    while True:
        x = driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        else:
            yield False


sg.theme('SystemDefault1')

messageBoxSelector = '//*[@id="main"]/footer/div[1]/div/div/div[2]/div[1]/div/div[2]'
invalidMsgSelector = '//*[@id="app"]/div[1]/span[2]/div[1]/span/div[1]/div/div/div/div/div[1]'
menuSelector = '//*[@id="side"]/header/div[2]/div/span/div[3]/div'
logoutSelector = '//*[@id="side"]/header/div[2]/div/span/div[3]/span/div[1]/ul/li[4]/div[1]'


def logoutFunc(driver,wait):
    driver.get("https://web.whatsapp.com/")
    wait.until(EC.element_to_be_clickable((By.XPATH , menuSelector))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH , logoutSelector))).click()
    driver.quit()


conn = sqlite3.connect('wbms.db')

conn.execute('''CREATE TABLE IF NOT EXISTS CONTACTS
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
         NAME BLOB NOT NULL,
         GROUPNAME BLOB,
         NUMBER BLOB);''')
conn.execute('''CREATE TABLE IF NOT EXISTS TEMPLATES
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
         NAME  BLOB NOT NULL,
         MESSAGE  BLOB);''')

cursorobj = conn.cursor()
print("Opened database successfully")


class threadingClass(QThread):
    progress = pyqtSignal(float,str)

    def __init__(self,numbers,message):
        super(threadingClass, self).__init__()
        self.numbers = numbers
        self.message = message

    def run(self):
        if connect() == True:
            value = 0
            progress_value = 100 / len(self.numbers)
            delay = 30
            try:
                driver = webdriver.Chrome(chrome.ChromeDriverManager().install())
            except:
                driver = webdriver.Edge(microsoft.EdgeChromiumDriverManager().install())

            driver.get("https://web.whatsapp.com/")
            driver.maximize_window()
            wait = WebDriverWait(driver, delay)

            confirm = sg.PopupOKCancel('Click "Ok" after scanning QR code (Do not close the window without confirming)\n',title='Confirm Logging',keep_on_top=True,icon='./icons/confirm.ico',location=(100,100))
            if confirm == 'OK':
                time.sleep(5)
                for number in self.numbers:
                    url = 'https://web.whatsapp.com/send?phone=88' + str(number) + '&text=' + self.message
                    time.sleep(1)
                    driver.get(url)
                    while not page_is_loading(driver):
                        continue
                    print('page loaded')
                    # time.sleep(4)
                    try:
                        invalidEl = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, invalidMsgSelector)))
                        if invalidEl.text == "Phone number shared via url is invalid.":
                            print('Phone Number Invalid !!!')
                        else:
                            print("Nothing Found with this contact")
                        value = value + progress_value
                        self.progress.emit(value,number)
                        continue
                    except:
                        try:
                            msgField = wait.until(EC.presence_of_element_located((By.XPATH, messageBoxSelector)))
                            msgField.send_keys(Keys.ENTER)
                            # messageInpField = wait.until(driver.find_element(By.XPATH , messageBoxSelector))
                            # messageInpField.send_keys(Keys.ENTER)
                            print('Phone Number Valid !!!')
                            print("Message Sent Successfully !!!")
                            value = value + progress_value
                            self.progress.emit(value,number)
                        except:
                            print("Message cannot be sent !!!")
                            value = value + progress_value
                            self.progress.emit(value,number)
                            continue
                logoutFunc(driver,wait)   
            else:
                driver.quit()
        else:
             QMessageBox.warning(self,"Warning","You have no internet connection!\nPlease connect your internet.",QMessageBox.Ok)


class TableModel(QAbstractTableModel):
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


class LoginView(QDialog):
    def __init__(self):
        super(LoginView, self).__init__()
        self.w = None
        loadUi("./ui/login.ui",self)
        self.login.clicked.connect(self.gotodashboard)
        self.passwordfield.setEchoMode(QLineEdit.Password)
    
    def gotodashboard(self):
        username = self.usernamefield.text()
        password = self.passwordfield.text()

        if len(username)==0 or len(password)==0:
            self.error.setText("Please input all fields.")

        else:
            res_username = 'admin'
            res_password = 'admin'
            if username == res_username and password == res_password:
                w.close()
                # if self.w is None:
                self.w = DashboardView()
                self.w.show()
                self.error.setText("")
            else:
                self.error.setText("Invalid username or password")


class DashboardView(QMainWindow):
    def __init__(self):
        self.w = None
        super(DashboardView, self).__init__()
        loadUi("./ui/dashboard.ui",self)

        qpixmap = QPixmap('./icons/logo.png')
        self.bgimg.setPixmap(qpixmap)

        icon_message1 = QIcon("./icons/comment.png")
        icon_message2 = QIcon("./icons/chatting.png")
        icon_message3 = QIcon("./icons/group.png")
        icon_message4 = QIcon("./icons/folder.png")
        icon_message5 = QIcon("./icons/book.png")
        icon_message6 = QIcon("./icons/notes.png")
        icon_message7 = QIcon("./icons/settings.png")
        icon_message8 = QIcon("./icons/backup.png")
        icon_message9 = QIcon("./icons/import.png")
        icon_message10 = QIcon("./icons/excel.png")
        icon_message11 = QIcon("./icons/cancel.png")
        icon_message12 = QIcon("./icons/aboutus.png")

        self.pushButton_1.setIcon(icon_message1)
        self.pushButton_2.setIcon(icon_message2)
        self.pushButton_3.setIcon(icon_message3)
        self.pushButton_4.setIcon(icon_message4)
        self.pushButton_5.setIcon(icon_message5)
        self.pushButton_6.setIcon(icon_message6)
        self.pushButton_12.setIcon(icon_message7)
        self.pushButton_8.setIcon(icon_message8)
        self.pushButton_9.setIcon(icon_message9)
        self.pushButton_10.setIcon(icon_message10)
        self.pushButton_11.setIcon(icon_message11)
        self.pushButton_7.setIcon(icon_message12)

        self.pushButton_1.clicked.connect(self.sendSingleSmsWindowFunc)
        self.pushButton_2.clicked.connect(self.sendMultipleSmsWindowFunc)
        self.pushButton_3.clicked.connect(self.sendGroupSmsWindowFunc)
        self.pushButton_4.clicked.connect(self.sendFileToSmsWindowFunc)
        self.pushButton_11.clicked.connect(self.closeByButtonFunc)
        self.pushButton_6.clicked.connect(self.createTemplateWindowFunc)
        self.pushButton_5.clicked.connect(self.contactWindowFunc)
        self.pushButton_10.clicked.connect(self.samplesWindowFunc)
        self.pushButton_8.clicked.connect(self.backupDatabaseFunc)
        self.pushButton_9.clicked.connect(self.restoreDatabaseFunc)
        self.setWindowTitle("Dashboard")

    def closeByButtonFunc(self):
        close = QMessageBox.question(self,"Quit","Are you sure want to quit?",QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            sys.exit(0)

    def sendSingleSmsWindowFunc(self):
        smw = SendSingleMessage()
        smw.setWindowTitle('Single SMS')
        smw.exec_()

    def sendMultipleSmsWindowFunc(self):
        smw = SendMultipleMessageClass()
        smw.setWindowTitle('Multiple SMS')
        smw.setFixedHeight(400)
        smw.setFixedWidth(800)
        smw.exec_()

    def sendGroupSmsWindowFunc(self):
        smw = SendGroupMessageClass()
        smw.setWindowTitle('Group SMS')
        smw.setFixedHeight(400)
        smw.setFixedWidth(800)
        smw.exec_()

    def sendFileToSmsWindowFunc(self):
        smw = SendFileToMessageClass()
        smw.setWindowTitle('File To SMS')
        smw.setFixedHeight(400)
        smw.setFixedWidth(800)
        smw.exec_()

    def contactWindowFunc(self):
        smw = ContactClass()
        smw.setWindowTitle('Contacts')
        smw.exec_()

    def createTemplateWindowFunc(self):
        smw = CreateTemplateClass()
        smw.setWindowTitle('Create Templates')
        smw.exec_()

    def samplesWindowFunc(self):
        os.startfile(Path.cwd()/'samples')

    def backupDatabaseFunc(self):
        folderPath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folderPath:
            fullPath = Path(folderPath)/'wbms.db'
            dbFilePath = Path.cwd()/'wbms.db'
            shutil.copy2(dbFilePath, fullPath)
            QMessageBox.information(self,'Done','Database backup successfully')

    def restoreDatabaseFunc(self):
        filePath = QFileDialog.getOpenFileName(self, 'Select File','c:\\','db(*.db)')
        if filePath[0]:
            close = QMessageBox.question(self,"Quit","Are you sure you want to restore databse?\nIt will remove all previous data.",QMessageBox.Yes | QMessageBox.No)
            if close == QMessageBox.Yes:
                fullPath = filePath[0]
                dbFilePath = Path.cwd()/'wbms.db'
                shutil.copy2(fullPath, dbFilePath)
                QMessageBox.information(self,'Done','Database restore successfully')

    def closeEvent(self, event):
        close = QMessageBox.question(self,"Quit","Are you sure want to quit?",QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class SendSingleMessage(QDialog):
    def __init__(self):
        super(SendSingleMessage, self).__init__()
        loadUi("./ui/sendsinglemessage.ui",self)
        cursorobj.execute("SELECT id,name from TEMPLATES")
        rows = cursorobj.fetchall()

        self.comboBox.addItem("SELECT TEMPATE",None)
        for row in rows:
            self.comboBox.addItem(row[1],row[0])

        self.comboBox.activated.connect(self.selectOptionFunc)
        self.pushButton_1.clicked.connect(self.sendMessageFunc)
        # self.comboBox.model().item(0).setEnabled(False)
        icon_message1 = QIcon("./icons/send.png")
        icon_message2 = QIcon("./icons/cancel.png")
        self.pushButton_1.setIcon(icon_message1)
        self.pushButton_2.setIcon(icon_message2)
        self.pushButton_2.clicked.connect(self.close)

    def selectOptionFunc(self):
        selected_template_id = self.comboBox.currentData()
        if selected_template_id:
            cursorobj.execute(f'SELECT message from TEMPLATES where id="{selected_template_id}"')
            templates_message = cursorobj.fetchall()[0][0]
            self.smsbody.setPlainText(templates_message)

    def sendMessageFunc(self):
        number = self.singlenumber.text()
        message = self.smsbody.toPlainText()
        if len(number)==0 or len(message)==0:
            QMessageBox.warning(self,"Warning","Fill both number and message field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            self.thread = threadingClass([number],message)
            self.thread.start()
            self.thread.finished.connect(self.finishedProgressFunc)

    def finishedProgressFunc(self):
        QMessageBox.information(self,'Done','Operation Completed !!!')
        template_saver = QMessageBox.question(self,'Save Template','Do you want to save this template?', QMessageBox.Yes | QMessageBox.No)
        template_message = self.smsbody.toPlainText()
        if template_saver == QMessageBox.Yes and template_message:
            wobj = CreateTemplateClass()
            wobj.textEdit.setPlainText(template_message)
            wobj.exec_()

        self.singlenumber.setText('')
        self.smsbody.setText('')
        self.campaing.setText('')


class SendMultipleMessageClass(QDialog):
    def __init__(self):
        super(SendMultipleMessageClass, self).__init__()
        loadUi("./ui/sendmultiplemessage.ui",self)
        cursorobj.execute("SELECT id,name from TEMPLATES")
        rows = cursorobj.fetchall()

        self.comboBox.addItem("SELECT TEMPATE",None)
        for row in rows:
            self.comboBox.addItem(row[1],row[0])

        self.comboBox.activated.connect(self.selectOptionFunc)
        self.pushButton_1.clicked.connect(self.sendMessageFunc)

        icon_message1 = QIcon("./icons/send.png")
        icon_message2 = QIcon("./icons/cancel.png")
        self.pushButton_1.setIcon(icon_message1)
        self.pushButton_2.setIcon(icon_message2)
        self.pushButton_2.clicked.connect(self.close)

    def selectOptionFunc(self):
        selected_campain_id = self.comboBox.currentData()
        if selected_campain_id:
            cursorobj.execute(f'SELECT message from TEMPLATES where id="{selected_campain_id}"')
            templates_message = cursorobj.fetchall()[0][0]
            self.smsbody.setPlainText(templates_message)

    def sendMessageFunc(self):
        message = self.smsbody.toPlainText()
        input_number = self.recipient.toPlainText()
        number_list = input_number.split('\n')
        numbers = [number.replace(' ','')  for number in number_list if number]
        self.count.setText(str(len(numbers)))
        
        if len(numbers)==0 or len(message)==0:
            QMessageBox.warning(self,"Warning","Fill both number and message field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            self.thread = threadingClass(numbers,message)
            self.thread.start()
            self.thread.progress.connect(self.evtUpdateProgressFunc)
            self.thread.finished.connect(self.finishedProgressFunc)

    def evtUpdateProgressFunc(self,value,number):
        self.status.append(f'Sending: {number}')
        self.progressBar.setValue(value)
        
    def finishedProgressFunc(self):
        QMessageBox.information(self,'Done','Operation Completed !!!')
        template_saver = QMessageBox.question(self,'Save Template','Do you want to save this template?', QMessageBox.Yes | QMessageBox.No)
        template_message = self.smsbody.toPlainText()
        if template_saver == QMessageBox.Yes and template_message:
            wobj = CreateTemplateClass()
            wobj.textEdit.setPlainText(template_message)
            wobj.exec_()

        self.smsbody.setText('')
        self.campaing.setText('')
        self.listWidget.clear()


class SendGroupMessageClass(QDialog):
    def __init__(self):
        super(SendGroupMessageClass, self).__init__()
        loadUi("./ui/sendgroupmessage.ui",self)

        cursorobj.execute("SELECT id,name from TEMPLATES")
        rows = cursorobj.fetchall()


        self.comboBox_2.addItem("SELECT TEMPATE",None)
        for row in rows:
            self.comboBox_2.addItem(row[1],row[0])

        cursorobj.execute("SELECT DISTINCT groupname from CONTACTS ORDER BY groupname")
        grouprows = cursorobj.fetchall()

        self.comboBox_3.addItem("SELECT GROUP",None)
        for row in grouprows:
            self.comboBox_3.addItem(row[0])

        self.comboBox_2.activated.connect(self.selectOptionFunc)
        self.comboBox_3.activated.connect(self.selectGroupOptionFunc)
        self.pushButton_1.clicked.connect(self.sendMessageFunc)

        icon_message1 = QIcon("./icons/send.png")
        icon_message2 = QIcon("./icons/cancel.png")
        self.pushButton_1.setIcon(icon_message1)
        self.pushButton_2.setIcon(icon_message2)
        self.pushButton_2.clicked.connect(self.close)

    def selectOptionFunc(self):
        selected_campain_id = self.comboBox_2.currentData()
        if selected_campain_id:
            cursorobj.execute(f'SELECT message from TEMPLATES where id="{selected_campain_id}"')
            templates_message = cursorobj.fetchall()[0][0]
            self.smsbody.setPlainText(templates_message)

    def selectGroupOptionFunc(self):
        selected_groupname = self.comboBox_3.currentText()
        if selected_groupname:
            cursorobj.execute(f'SELECT number from CONTACTS where groupname="{selected_groupname}"')
            select_numbers = cursorobj.fetchall()
            for number in select_numbers:
                    if number[0] != '':
                        self.listWidget.addItem(str(number[0]))

    def sendMessageFunc(self):
        lw = self.listWidget
        numbers = [lw.item(x).text() for x in range(lw.count())]
        message = self.smsbody.toPlainText()
        self.count_2.setText(str(len(numbers)))
        if len(numbers)==0 or len(message)==0:
            QMessageBox.warning(self,"Warning","Fill both number and message field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            self.thread = threadingClass(numbers,message)
            self.thread.start()
            self.thread.progress.connect(self.evtUpdateProgressFunc)
            self.thread.finished.connect(self.finishedProgressFunc)

    def evtUpdateProgressFunc(self,value,number):
        self.status.append(f'Sending: {number}')
        self.progressBar.setValue(value)
        
    def finishedProgressFunc(self):
        QMessageBox.information(self,'Done','Operation Completed !!!')
        QMessageBox.information(self,'Done','Operation Completed !!!')
        template_saver = QMessageBox.question(self,'Save Template','Do you want to save this template?', QMessageBox.Yes | QMessageBox.No)
        template_message = self.smsbody.toPlainText()
        if template_saver == QMessageBox.Yes and template_message:
            wobj = CreateTemplateClass()
            wobj.textEdit.setPlainText(template_message)
            wobj.exec_()

        self.smsbody.setText('')
        self.campaing.setText('')
        self.listWidget.clear()


class SendFileToMessageClass(QDialog):
    def __init__(self):
        super(SendFileToMessageClass, self).__init__()
        loadUi("./ui/sendfiletomessage.ui",self)
        cursorobj.execute("SELECT id,name from TEMPLATES")
        rows = cursorobj.fetchall()

        self.comboBox_2.addItem("SELECT TEMPATE",None)
        for row in rows:
            self.comboBox_2.addItem(row[1],row[0])

        self.comboBox_2.activated.connect(self.selectOptionFunc)
        self.pushButton_1.clicked.connect(self.sendMessageFunc)
        self.pushButton_3.clicked.connect(self.browseFile)

        icon_message1 = QIcon("./icons/send.png")
        icon_message2 = QIcon("./icons/cancel.png")
        icon_message3 = QIcon("./icons/excel.png")
        self.pushButton_1.setIcon(icon_message1)
        self.pushButton_2.setIcon(icon_message2)
        self.pushButton_3.setIcon(icon_message3)
        self.pushButton_2.clicked.connect(self.close)

    def selectOptionFunc(self):
        selected_campain_id = self.comboBox_2.currentData()
        if selected_campain_id:
            cursorobj.execute(f'SELECT message from TEMPLATES where id="{selected_campain_id}"')
            templates_message = cursorobj.fetchall()[0][0]
            self.smsbody.setPlainText(templates_message)
    
    def browseFile(self):
        # , 'Text files (*.txt);;XML files (*.xml,*.xlsx,*.xlsm,*.xls)'
        filename = QFileDialog.getOpenFileName(self, 'open file')
        file_name = Path(filename[0]).name
        if file_name.lower().endswith(('.txt','.csv')):
            with open(filename[0], "r") as f:
                for number in f.read().splitlines():
                    if number != '':
                        self.listWidget.addItem(str(number))
            f.close()

        elif file_name.lower().endswith(('.xlsx','.xlsm','.xls','.xml')):
            excel_data = pd.read_excel(filename[0], sheet_name='Customers')
            numbers = excel_data['Contact'].to_list()
            for number in numbers:
                self.listWidget.addItem(str(number))

    def sendMessageFunc(self):
        lw = self.listWidget
        numbers = [lw.item(x).text() for x in range(lw.count())]
        message = self.smsbody.toPlainText()
        self.count_2.setText(str(len(numbers)))
        if len(numbers)==0 or len(message)==0:
            QMessageBox.warning(self,"Warning","Fill both number and message field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            self.thread = threadingClass(numbers,message)
            self.thread.start()
            self.thread.progress.connect(self.evtUpdateProgressFunc)
            self.thread.finished.connect(self.finishedProgressFunc)

    def evtUpdateProgressFunc(self,value,number):
        self.status.append(f'Sending: {number}')
        self.progressBar.setValue(value)
        
    def finishedProgressFunc(self):
        QMessageBox.information(self,'Done','Operation Completed !!!')
        QMessageBox.information(self,'Done','Operation Completed !!!')
        template_saver = QMessageBox.question(self,'Save Template','Do you want to save this template?', QMessageBox.Yes | QMessageBox.No)
        template_message = self.smsbody.toPlainText()
        if template_saver == QMessageBox.Yes and template_message:
            wobj = CreateTemplateClass()
            wobj.textEdit.setPlainText(template_message)
            wobj.exec_()

        self.smsbody.setText('')
        self.campaing.setText('')
        self.listWidget.clear()


class CreateTemplateClass(QDialog):
    def __init__(self):
        super(CreateTemplateClass, self).__init__()
        loadUi("./ui/templatecreate.ui",self)
        icon_message6 = QIcon("./icons/cancel.png")
        icon_message4 = QIcon("./icons/magnifying-glass.png")
        icon_message5 = QIcon("./icons/excel.png")
        icon_message3 = QIcon("./icons/error.png")
        icon_message7 = QIcon("./icons/eraser.png")
        icon_message = QIcon("./icons/design-tool.png")
        icon_message_2 = QIcon("./icons/edit.png")
        self.pushButton_6.setIcon(icon_message6)
        self.pushButton_4.setIcon(icon_message4)
        self.pushButton_5.setIcon(icon_message5)
        self.pushButton_3.setIcon(icon_message3)
        self.pushButton_7.setIcon(icon_message7)
        self.pushButton.setIcon(icon_message)
        self.pushButton_2.setIcon(icon_message_2)

        self.pushButton_6.clicked.connect(self.close) 
        self.pushButton.clicked.connect(self.createTemplateFunc) 
        self.pushButton_2.clicked.connect(self.updateTemplateFunc) 
        self.pushButton_3.clicked.connect(self.deleteTemplateFunc) 
        self.pushButton_7.clicked.connect(self.clearFieldFunc) 
        self.pushButton_4.clicked.connect(self.searchTemplateFunc) 
        self.pushButton_5.clicked.connect(self.exportTemplateFunc) 

        self.tableCreate()
        self.tableView.doubleClicked.connect(self.rowDoubleClick)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
    
    def clearFieldFunc(self):
        self.lineEdit.setText("")
        self.textEdit.setPlainText("")

    def rowDoubleClick(self):
        index=(self.tableView.selectionModel().currentIndex())
        # value=index.sibling(index.row(),index.column()).data()
        selected_id=index.sibling(index.row(),0).data()
        cursorobj.execute(f'SELECT name , message from TEMPLATES where id="{selected_id}"')
        obj = cursorobj.fetchall()
        self.lineEdit.setText(obj[0][0])
        self.textEdit.setPlainText(obj[0][1])

    def createTemplateFunc(self):
        name = self.lineEdit.text()
        message = self.textEdit.toPlainText()
        if len(name)==0 or len(message)==0:
            QMessageBox.warning(self,"Warning","Fill both title and message field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            try:
                sqlInsertTemplate(conn,(name,message))
                self.tableCreate()
                self.lineEdit.setText("")
                self.textEdit.setPlainText("")
                QMessageBox.information(self,"Success","Template Create Successfully",QMessageBox.Ok)
            except sqlite3.Error:
                QMessageBox.critical(self,"Error","An error occured",QMessageBox.Ok)

    def updateTemplateFunc(self):
        index=(self.tableView.selectionModel().currentIndex())
        selected_id = index.sibling(index.row(),0).data()
        name = self.lineEdit.text()
        message = self.textEdit.toPlainText()
        if len(name)==0 or len(message)==0:
            QMessageBox.warning(self,"Warning","Fill both title and message field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            try:
                sqlUpdateTemplate(conn,selected_id,name,message)
                self.tableCreate()
                self.lineEdit.setText("")
                self.textEdit.setPlainText("")
                QMessageBox.information(self,"Success","Template Updated Successfully",QMessageBox.Ok)
            except sqlite3.Error:
                QMessageBox.critical(self,"Error","An error occured",QMessageBox.Ok)

    def deleteTemplateFunc(self):
        index=(self.tableView.selectionModel().currentIndex())
        selected_id = index.sibling(index.row(),0).data()
        if selected_id:
            delete = QMessageBox.question(self,"Quit",f"Are you sure want to delete Template id{selected_id}?",QMessageBox.Yes | QMessageBox.No)
            if delete == QMessageBox.Yes:
                sql = 'DELETE FROM TEMPLATES WHERE id=?'
                try:
                    cursorobj.execute(sql, (selected_id,))
                    conn.commit()
                    self.tableCreate()
                except sqlite3.Error:
                    QMessageBox.critical(self,"Error","An error occured",QMessageBox.Ok)

        else:
            QMessageBox.warning(self,"Warning","Select a row First",QMessageBox.Ok)

    def searchTemplateFunc(self):
        name = self.lineEdit_2.text()
        if name:
            cursorobj.execute(f'SELECT id,name,message from TEMPLATES WHERE name LIKE "%{name}%" OR message LIKE "%{name}%"')
            rows = cursorobj.fetchall()
            print(rows)
            if rows:
                df = pd.DataFrame(rows)
                df.rename(columns={0: 'ID', 1: 'NAME', 2: 'MESSAGE'}, inplace=True)
                self.model = TableModel(df)
                self.tableView.setModel(self.model)     
                self.tableView.resizeColumnToContents(0)
                self.tableView.resizeColumnToContents(1)
                self.tableView.resizeColumnToContents(2)
            else:
                df = pd.DataFrame({})
                self.model = TableModel(df)
                self.tableView.setModel(self.model)     

        else:
            self.tableCreate()

    def exportTemplateFunc(self):
        cursorobj.execute("SELECT id,name,message from TEMPLATES")
        rows = cursorobj.fetchall()
        df = pd.DataFrame(rows)
        df.rename(columns={0: 'ID', 1: 'NAME', 2: 'MESSAGE'}, inplace=True)
        folderPath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folderPath:
            fullPath = Path(folderPath)/'templates.xlsx'
            df.to_excel(fullPath,index=False)
            QMessageBox.information(self,'Done','Templates Export Successfully')

    def tableCreate(self):
        cursorobj.execute("SELECT id,name,message from TEMPLATES")
        rows = cursorobj.fetchall()
        df = pd.DataFrame(rows)
        df.rename(columns={0: 'ID', 1: 'NAME', 2: 'MESSAGE'}, inplace=True)
        self.model = TableModel(df)
        self.tableView.setModel(self.model)     
        self.tableView.resizeColumnToContents(0)
        self.tableView.resizeColumnToContents(1)
        self.tableView.resizeColumnToContents(2)


class ContactClass(QDialog):
    def __init__(self):
        super(ContactClass, self).__init__()
        loadUi("./ui/contact.ui",self)
        icon_message6 = QIcon("./icons/cancel.png")
        icon_message4 = QIcon("./icons/magnifying-glass.png")
        icon_message5 = QIcon("./icons/excel.png")
        icon_message3 = QIcon("./icons/error.png")
        icon_message7 = QIcon("./icons/eraser.png")
        icon_message = QIcon("./icons/design-tool.png")
        icon_message_2 = QIcon("./icons/edit.png")
        icon_message_8 = QIcon("./icons/printer.png")
        icon_message_9 = QIcon("./icons/excel.png")
        self.pushButton_6.setIcon(icon_message6)
        self.pushButton_4.setIcon(icon_message4)
        self.pushButton_5.setIcon(icon_message5)
        self.pushButton_3.setIcon(icon_message3)
        self.pushButton_7.setIcon(icon_message7)
        self.pushButton.setIcon(icon_message)
        self.pushButton_2.setIcon(icon_message_2)
        self.pushButton_8.setIcon(icon_message_8)
        self.pushButton_9.setIcon(icon_message_9)

        self.pushButton_2.clicked.connect(self.updateContactFunc) 
        self.pushButton_3.clicked.connect(self.deleteContactFunc) 
        self.pushButton_7.clicked.connect(self.clearFieldFunc) 
        self.pushButton_6.clicked.connect(self.close) 
        self.pushButton.clicked.connect(self.createContactFunc) 
        self.pushButton_4.clicked.connect(self.searchContactFunc) 
        self.pushButton_5.clicked.connect(self.exportContactFunc) 
        self.pushButton_9.clicked.connect(self.importContactFunc)

        self.autoCompleteFunc()
        self.tableCreate()

        self.tableView.doubleClicked.connect(self.rowDoubleClick)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)

        self.comboBox.addItem('All','*')
        self.comboBox.addItem('Name','name')
        self.comboBox.addItem('Group Name','groupname')
        self.comboBox.addItem('Number','number')
    
    def clearFieldFunc(self):
        self.lineEdit.setText("")
        self.lineEdit_3.setText("")
        self.lineEdit_4.setText("")

    def rowDoubleClick(self):
        index=(self.tableView.selectionModel().currentIndex())
        # value=index.sibling(index.row(),index.column()).data()
        selected_id=index.sibling(index.row(),0).data()
        cursorobj.execute(f'SELECT name , groupname ,number from CONTACTS where id="{selected_id}"')
        obj = cursorobj.fetchall()
        self.lineEdit.setText(str(obj[0][0]))
        self.lineEdit_3.setText(str(obj[0][2]))
        self.lineEdit_4.setText(str(obj[0][1]))

    def createContactFunc(self):
        name = self.lineEdit.text()
        group = self.lineEdit_4.text()
        number = self.lineEdit_3.text()
        if len(name)==0 or len(number)==0:
            QMessageBox.warning(self,"Warning","Fill all field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            try:
                sqlInsertTContact(conn,(name,group,number))
                self.tableCreate()
                self.lineEdit.setText("")
                self.lineEdit_3.setText("")
                self.lineEdit_4.setText("")
                self.autoCompleteFunc()
                QMessageBox.information(self,"Success","Contact Create Successfully",QMessageBox.Ok)
            except sqlite3.Error:
                QMessageBox.critical(self,"Error","An error occured",QMessageBox.Ok)

    def updateContactFunc(self):
        index=(self.tableView.selectionModel().currentIndex())
        selected_id = index.sibling(index.row(),0).data()
        name = self.lineEdit.text()
        group = self.lineEdit_4.text()
        number = self.lineEdit_3.text()
        if len(name)==0 or len(number)==0:
            QMessageBox.warning(self,"Warning","Fill all field to proceed\n(Don't leave empty)",QMessageBox.Ok)
        else:
            try:
                sqlUpdateContact(conn,selected_id,name,group,number)
                self.tableCreate()
                self.lineEdit.setText("")
                self.lineEdit_3.setText("")
                self.lineEdit_4.setText("")
                self.autoCompleteFunc()
                QMessageBox.information(self,"Success","Contact Updated Successfully",QMessageBox.Ok)
            except sqlite3.Error:
                QMessageBox.critical(self,"Error","An error occured",QMessageBox.Ok)

    def deleteContactFunc(self):
        index=(self.tableView.selectionModel().currentIndex())
        selected_id = index.sibling(index.row(),0).data()
        if selected_id:
            delete = QMessageBox.question(self,"Quit",f"Are you sure want to delete Contact id{selected_id}?",QMessageBox.Yes | QMessageBox.No)
            if delete == QMessageBox.Yes:
                sql = 'DELETE FROM CONTACTS WHERE id=?'
                try:
                    cursorobj.execute(sql, (selected_id,))
                    conn.commit()
                    self.tableCreate()
                    self.autoCompleteFunc()
                except sqlite3.Error:
                    QMessageBox.critical(self,"Error","An error occured",QMessageBox.Ok)

        else:
            QMessageBox.warning(self,"Warning","Select a row First",QMessageBox.Ok)

    def searchContactFunc(self):
        selected_filter = str(self.comboBox.currentData())
        name = str(self.lineEdit_2.text())
        if name:
            if selected_filter == 'number':
                cursorobj.execute(f'SELECT * from CONTACTS WHERE {selected_filter} LIKE "%{name}%"')
            elif selected_filter == 'name':
                cursorobj.execute(f'SELECT * from CONTACTS WHERE {selected_filter} LIKE "%{name}%"')
            elif selected_filter == 'groupname':
                cursorobj.execute(f'SELECT * from CONTACTS WHERE {selected_filter} LIKE "%{name}%"')
            elif selected_filter == '*':
                cursorobj.execute(f'SELECT * from CONTACTS WHERE name LIKE "%{name}%" OR groupname LIKE "%{name}%" OR number LIKE "%{name}%"')
            else:
                cursorobj.execute(f'SELECT * from CONTACTS')

        rows = cursorobj.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            df.rename(columns={0: 'ID', 1: 'NAME', 2: 'GROUPNAME', 3: 'NUMBER'}, inplace=True)
            self.model = TableModel(df)
            self.tableView.setModel(self.model)     
            self.tableView.resizeColumnToContents(0)
            self.tableView.resizeColumnToContents(1)
            self.tableView.resizeColumnToContents(2)
        elif not rows and not name:
            self.tableCreate()
        else:
            df = pd.DataFrame({})
            self.model = TableModel(df)
            self.tableView.setModel(self.model)     
            self.tableView.resizeColumnToContents(0)
            self.tableView.resizeColumnToContents(1)
            self.tableView.resizeColumnToContents(2)

    def exportContactFunc(self):
        cursorobj.execute("SELECT * from CONTACTS")
        rows = cursorobj.fetchall()
        df = pd.DataFrame(rows)
        df.rename(columns={0: 'ID', 1: 'NAME', 2: 'GROUPNAME',3:"NUMBER"}, inplace=True)
        folderPath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folderPath:
            fullPath = Path(folderPath)/'contacts.xlsx'
            df.to_excel(fullPath,index=False)
            QMessageBox.information(self,'Done','Contacts Export Successfully')

    def importContactFunc(self):
        filePath = QFileDialog.getOpenFileName(self, 'Select File','./','Excel Files (*.xls *.xlsx)')

        if filePath[0]:
            df = pd.read_excel(filePath[0],dtype=str)
            df.to_sql('CONTACTS', conn, if_exists='replace', index = False)
            self.tableCreate()
            QMessageBox.information(self,'Done','Contacts import successfully')

    def tableCreate(self):
        cursorobj.execute("SELECT * from CONTACTS")
        rows = cursorobj.fetchall()
        df = pd.DataFrame(rows)
        df.rename(columns={0: 'ID', 1: 'NAME', 2: 'GROUPNAME',3:"NUMBER"}, inplace=True)
        self.model = TableModel(df)
        self.tableView.setModel(self.model)     
        self.tableView.resizeColumnToContents(0)
        self.tableView.resizeColumnToContents(1)
        self.tableView.resizeColumnToContents(2)

    def autoCompleteFunc(self):
        cursorobj.execute("SELECT groupname from CONTACTS")
        rows = cursorobj.fetchall()
        groups = [row[0] for row in rows]
        completer = QCompleter(groups)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.lineEdit_4.setCompleter(completer)
        

# main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DashboardView()
    w.show()
    sys.exit(app.exec_())

# obj = threadingClass(['01930380487','5634636434'],"demo")
# obj.run()