from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException,WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from pathlib import Path
import time
import PySimpleGUI as sg
sg.theme('SystemDefault1')





def AutomateMSGSender(numbers,message):
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        total_number=len(numbers)
        
        print("##########################################################")
        print('\nWe found ' + str(total_number) + ' numbers in the file')
        print("##########################################################")
        delay = 30

        driver.get("https://web.whatsapp.com/")
        driver.maximize_window()
        # wait = WebDriverWait(driver, delay)

        confirm = sg.PopupOKCancel('Click "Ok" after scanning QR code (Do not close the window without confirming)\n',title='Confirm Logging',keep_on_top=True,icon='./icons/confirm.ico')
        driver.get("https://google.com/")
        time.sleep(5)
        if confirm == 'OK':
            try:
                searchBoxSelector = '//*[@id="side"]/div[1]/div/label/div/div[2]'
                contactNameSelector = '//*[@id="main"]/header/div[2]/div[1]/div/span'
                messageBoxSelector = '//*[@id="main"]/footer/div[1]/div/div/div[2]/div[1]/div/div[2]'
                # time.sleep(5)
                searchBox = driver.find_element_by_xpath(searchBoxSelector)
                time.sleep(2)

                for number in numbers:
                    try:
                        searchBox.clear()
                        searchBox.send_keys(number)
                        searchBox.send_keys(Keys.ENTER)
                        time.sleep(2)
                        try:
                            element = driver.find_element_by_xpath('//*[@id="pane-side"]/div[1]/div/span')
                            if element.text == "No chats, contacts or messages found":
                                print('Phone Number Invalid !!!')
                            else:
                                print("Nothing Found with this contact")
                            continue
                        except NoSuchElementException:
                            print('Phone Number Valid !!!')

                        time.sleep(2)
                        contactName = driver.find_element_by_xpath(contactNameSelector).text
                        messageInpField = driver.find_element_by_xpath(messageBoxSelector)
                        messageInpField.send_keys(f'Hello {contactName}, {message}')
                        messageInpField.send_keys(Keys.ENTER)
                        print("Message Sent Successfully !!!")
                    except NoSuchElementException:
                        print("An error occured when sending message !!!")
            
                menuSelector = '//*[@id="side"]/header/div[2]/div/span/div[3]/div'
                logoutSelector = '//*[@id="side"]/header/div[2]/div/span/div[3]/span/div[1]/ul/li[4]'
                driver.find_element_by_xpath(menuSelector).click()
                time.sleep(1)
                driver.find_element_by_xpath(logoutSelector).click()
                driver.quit()
            except NoSuchElementException:
                driver.quit()
        else:
            driver.quit()
        numbers = []

    except WebDriverException:
        print("Exit") 



def sqlInsertTemplate(conn,entities):
    cursorObj = conn.cursor()
    cursorObj.execute('INSERT INTO TEMPLATES(NAME,MESSAGE) VALUES(?, ?)', entities)
    conn.commit()

def sqlUpdateTemplate(conn,id,name,message):
    cursorObj = conn.cursor()
    cursorObj.execute(f'UPDATE TEMPLATES SET name="{name}",message="{message}" where id={id}')
    conn.commit()

def sqlInsertTContact(conn,entities):
    cursorObj = conn.cursor()
    cursorObj.execute('INSERT INTO CONTACTS(NAME,GROUPNAME,NUMBER) VALUES(?, ?, ?)', entities)
    conn.commit()

def sqlUpdateContact(conn,id,name,group,number):
    cursorObj = conn.cursor()
    cursorObj.execute(f'UPDATE CONTACTS SET name="{name}",groupname="{group}",number="{number}" where id={id}')
    conn.commit()



AutomateMSGSender([543653465],"dfgdfg")