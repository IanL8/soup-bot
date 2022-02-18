import pymysql

import soupbot_utilities as util

conn = None
cursor = None

activeConnection = False

user, password, host, db = None, None, None, None


def initialize(u, p, h, d):
    global user, password, host, db
    user, password, host, db = u, p, h, d
    connect()


def connect():
    global conn, cursor, activeConnection
    global user, password, host, db
    util.timed_message("Trying to connect to mysql...")
    if not activeConnection:
        conn = pymysql.connect(user=user, password=password, host=host, database=db)
        conn.autocommit(True)
        cursor = conn.cursor()
        activeConnection = True
        util.timed_message("Connection successful")
    else:
        util.timed_message("Error: Already connected")


def disconnect():
    global conn, cursor, activeConnection
    util.timed_message("Trying to disconnect from mysql...")
    if activeConnection:
        cursor.close()
        conn.close()
        activeConnection = False
        util.timed_message("Disconnection successful")
    else:
        util.timed_message("Error: Not connected")


def make_query(query, values=tuple()):
    global cursor, activeConnection
    try:
        if len(values) > 0:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
    except BrokenPipeError:
        util.timed_message(str(BrokenPipeError))
        disconnect()
        connect()
    return [c for c in cursor]
