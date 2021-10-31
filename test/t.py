import sqlite3

conn = sqlite3.connect('../wbms.db')
print("Opened database successfully")

# conn.execute('''CREATE TABLE IF NOT EXISTS TEMPLATES
#          (ID INTEGER PRIMARY KEY AUTOINCREMENT,
#          NAME           TEXT    NOT NULL,
#          MESSAGE        CHAR(500));''')

conn.execute('''CREATE TABLE IF NOT EXISTS CONTACTS
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
         NAME TEXT NOT NULL,
         GROUPNAME TEXT,
         NUMBER BLOB);''')

# def sqlInsert(conn,entities):
#     cursorObj = conn.cursor()
#     cursorObj.execute('INSERT INTO TEMPLATES(NAME,MESSAGE) VALUES(?, ?)', entities)
#     conn.commit()

# conn.execute("INSERT INTO CONTACTS (NAME,GROUPNAME,NUMBER) \
#       VALUES ('Mark2','Family','0010911111111')")
# conn.execute("INSERT INTO CONTACTS (NAME,GROUPNAME,NUMBER) \
#       VALUES ('Mark3','Family4','00109111111fdgd11')")
# conn.commit()
# entities = ('DEMO1',"uytgyu")
# sqlInsert(conn,entities)
# cursor = conn.execute("SELECT id, name, message from TEMPLATES")
# cursor = conn.execute("SELECT * from CONTACTS")
# # print(cursor.fetchall())
# # templatesname = [row for row in cursor.fetchall()]

# print(cursor.fetchall())
# # for row in cursor:
# #     print(row)
# #    print("ID = ", row[0])
# #    print("NAME = ", row[1])
# #    print("SALARY = ", row[2], "\n")
# print("Table created successfully")
# # conn.execute("DROP table IF EXISTS CONTACTS")
# conn.close()


