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
        util.timed_message("[Error] Already connected")


def disconnect():
    global conn, cursor, activeConnection
    util.timed_message("Trying to disconnect from mysql...")
    if activeConnection:
        cursor.close()
        conn.close()
        activeConnection = False
        util.timed_message("Disconnection successful")
    else:
        util.timed_message("[Error] Not connected")


# returns either (1, query result) if successful, or (0, empty list) if unsuccessful
def make_query(query, values=tuple()):
    global conn, cursor, activeConnection
    queryType = query.split(" ")[0]
    #
    # attempt query
    try:
        if len(values) > 0:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
    except pymysql.err.OperationalError as inst1:
        util.timed_message("[Error] OperationError on {s} query".format(s=queryType))
        util.timed_message(str(inst1.args))
        util.timed_message("Restarting connection...")
        disconnect()
        connect()
        util.timed_message("Restart successful")
        #
        # attempt query again
        util.timed_message("Reattempting {s} query...".format(s=queryType))
        try:
            if len(values) > 0:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
        except pymysql.err.OperationalError as inst2:
            util.timed_message("[Error] OperationError on {s} query".format(s=queryType))
            util.timed_message(str(inst2.args))
            util.timed_message("{s} query unsuccessful".format(s=queryType))
            return 0, list()

    util.timed_message("{s} query successful".format(s=queryType))
    return 1, [c for c in cursor]
