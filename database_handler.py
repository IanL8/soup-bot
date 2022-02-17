import pymysql

conn = None
cursor = None

activeConnection = False


def isConnected():
    return activeConnection


def connect(username, password, host, db):
    global conn, cursor, activeConnection
    if not activeConnection:
        conn = pymysql.connect(user=username, password=password, host=host, database=db)
        conn.autocommit(True)
        cursor = conn.cursor()
        activeConnection = True
        print("Connection to mysql successful")
    else:
        print("Error: Connection to mysql rejected")


def disconnect():
    global conn, cursor, activeConnection
    if activeConnection:
        cursor.close()
        conn.close()
        activeConnection = False
        print("Disconnection from mysql successful")
    else:
        print("Error: Disconnection from mysql rejected")


def make_query(query, values=tuple()):
    global cursor
    if len(values) > 0:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    return cursor
