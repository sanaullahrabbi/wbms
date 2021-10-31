from faulthandler import disable
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from pathlib import Path
from sys import path
import PySimpleGUI as sg
import pandas
import time
import os


# Global Variables
numbers = []

def getNumbers(file):
    global numbers
    if file.lower().endswith(('.txt','.csv')):
        f = open(file, "r")
        for line in f.read().splitlines():
            if line != "":
                numbers.append(line)
        f.close()

    elif file.lower().endswith(('.xlsx','.xlsm','.xls','.xml')):
        excel_data = pandas.read_excel(file, sheet_name='Customers')
        numbers = excel_data['Contact'].to_list()
    else:
        numbers =[]
    return numbers


def AutomateMSGSender(numbers):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    total_number=len(numbers)

    print("##########################################################")
    print('\nWe found ' + str(total_number) + ' numbers in the file')
    print("##########################################################")
    print()
    delay = 30

    driver.get("https://web.whatsapp.com/")
    driver.maximize_window()
    wait = WebDriverWait(driver, delay)

    # input_name = input("Press Enter After Scanning . . . . .")
    confirm = sg.PopupOK('Click "Ok" after scanning QR code (Do not close the confirmation)',title='Confirm Logging',keep_on_top=True)
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
                    messageInpField = wait.until(lambda driver:driver.find_element_by_xpath(messageBoxSelector))
                    messageInpField.send_keys(f'Hello {contactName}, This is a test message from whatsapp automation. No need to replay !!!')
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


sg.theme('SystemDefault')
button_list = [
    [
        sg.Text('MENU', size=(20,1),font=("Arial, 12")),
    ],
    [
        sg.Button('Send Manualy',key='b1',size=(20,1),pad=(5,5),border_width=2,)
    ],
    [
        sg.Button('Send From File',key='b2',size=(20,1),pad=(5,5),focus=False)
    ],
    [
        sg.Button('Contact Book',key='b3',size=(20,1),pad=(5,5))
    ],
    [
        sg.Button('Demo Button',key='b4',size=(20,1),pad=(5,5))
    ],
    [
        sg.Button('Demo Button',key='b5',size=(20,1),pad=(5,5))
    ],
    [
        sg.Button('Demo Button',key='b6',size=(20,1),pad=(5,5))
    ],
]
file_list_column = [
    [
        sg.Text('Number List', size=(25,1),font=("Arial, 12")),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40,23),
            key='-FILE LIST-'
        )
    ],
]
log_column = [
    [
        sg.Text('logs ( all  operation will be shown here )',font=("Arial, 12")),
    ],
    [
        sg.Multiline(size=(80,28), auto_refresh=True, reroute_stdout=True,disabled=True, reroute_cprint=True, write_only=True, key='-OUT-')
    ]
    ,
]

msg_viwer_column = [
    [
        sg.Text('Enter Message Formate:',size=(25,1),font=("Arial, 11")),
    ],
    [
        sg.Multiline(size=(50,8),key='-MSG-')
    ],
    [ sg.Text('')],
    [
        sg.Text('Enter Single or Multiple Contact:', size=(25,1),font=("Arial, 11")),
    ],
    [
        sg.Multiline(size=(50,12),key='-CONTACT-',focus=True)
    ],
    [sg.Text('The second window')],
              
              [sg.Text(size=(25,1), k='-OUTPUT-')],
              [sg.Button('Erase'), sg.Button('Popup'), sg.Button('Exit')]
]

layout = [
    [
        sg.Column(button_list,vertical_alignment='top',pad=(20,0)),
        # sg.VSeparator(),
        # sg.Column(msg_viwer_column),
        # sg.VSeparator(),
        # sg.Column(file_list_column,vertical_alignment='top',pad=(20,0)),
        sg.VSeparator(),
        sg.Column(log_column,vertical_alignment='top',pad=(28,0)),
    ]
]

def make_win2():
    layout2 = [ [
        sg.Text('Enter Message Formate:',size=(25,1),font=("Arial, 11")),
    ],
    [
        sg.Multiline(size=(50,8),key='-MSG-')
    ],
    [ sg.Text('')],
    [
        sg.Text('Enter Single or Multiple Contact:', size=(25,1),font=("Arial, 11")),
    ],
    [
        sg.Multiline(size=(50,12),key='-CONTACT-',focus=True)
    ],
        [sg.Text('The second window')],
              [sg.Text(size=(25,1), k='-OUTPUT-')],
              [sg.Button('Exit')]]
    return sg.Window('Second Window', layout2,keep_on_top=True,use_default_focus=False)

window = sg.Window('WhatsApp Bulk Messsage Sender', layout,margins=(10,30))

while True:
    event, values = window.read()

    if event == 'EXIT' or event == sg.WIN_CLOSED:
        break

    elif event == 'b1':
        print('Hello 1')
        # input_number = values['-CONTACT-']
        # number_list = input_number.split('\n')
        # numbers = [number.replace(' ','')  for number in number_list if number]
        # AutomateMSGSender(numbers)

    elif event == 'b2':
        print('Hello 2')
        file = sg.popup_get_file('Select .txt , .xlsx file witch contains the list of numbers',title='Select From File')
        if file:
            numbers = getNumbers(file)
            print(numbers)
            AutomateMSGSender(numbers)
    elif event == 'b3':
        window2 = make_win2()
        while True:
            event2, values2 = window2.read()
            print(event2,values2)
            if event2 == 'Exit' or event2 == sg.WIN_CLOSED:
                break
            elif event == '-IN-':
                window2['-OUTPUT-'].update(f'You enetered {values["-IN-"]}')
            elif event == 'Erase':
                window2['-OUTPUT-'].update('')
                window2['-IN-'].update('')
        # AutomateMSGSender(numbers)
        window2.close()
        
        

window.close()
