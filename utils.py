import urllib.request

def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

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
