import mysql.connector

cnx = None
cursor = None

activeConnection = False


def isConnected():
    return activeConnection


def connect(password):
    global cnx, cursor, activeConnection
    cnx = mysql.connector.connect(user="root", password=password, host="localhost", database="soupbot")
    cnx.autocommit = True
    cursor = cnx.cursor()
    activeConnection = True


def disconnect():
    global cnx, cursor, activeConnection
    cursor.close()
    cnx.close()
    activeConnection = False


def make_query(query):
    global cursor
    cursor.execute(query)
    return cursor
