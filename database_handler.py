import mysql.connector

cnx = None
cursor = None


def connect(password):
    global cnx, cursor
    cnx = mysql.connector.connect(user="root", password=password, host="localhost", database="soupbot")
    cnx.autocommit = True
    cursor = cnx.cursor()


def disconnect():
    cursor.close()
    cnx.close()


def make_query(query):
    cursor.execute(query)
    return cursor
