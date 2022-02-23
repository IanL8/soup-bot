#
# imports
import pymysql

#
# project imports
import soupbot_utilities as util

#
# global vars
conn = None
cursor = None
activeConnection = False
user, password, host, db = None, None, None, None


#
# functions

# sets the globals: user, password, host, db
def initialize(u, p, h, d):
    global user, password, host, db
    user, password, host, db = u, p, h, d


# makes the connection to the mysql database
def connect():
    global conn, cursor, activeConnection
    global user, password, host, db
    util.soup_log("Trying to connect to mysql...")
    if not activeConnection:
        conn = pymysql.connect(user=user, password=password, host=host, database=db)
        conn.autocommit(True)
        cursor = conn.cursor()
        activeConnection = True
        util.soup_log("Connection successful")
    else:
        util.soup_log("[Error] Already connected")


# disconnects from the mysql database
def disconnect():
    global conn, cursor, activeConnection
    util.soup_log("Trying to disconnect from mysql...")
    if activeConnection:
        cursor.close()
        conn.close()
        activeConnection = False
        util.soup_log("Disconnection successful")
    else:
        util.soup_log("[Error] Not connected")


# makes a query using the SQL query and its corresponding values
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
        util.soup_log("[Error] OperationError on {s} query".format(s=queryType))
        util.soup_log(str(inst1.args))
        util.soup_log("Restarting connection...")
        disconnect()
        connect()
        util.soup_log("Restart successful")
        #
        # attempt query again
        util.soup_log("Reattempting {s} query...".format(s=queryType))
        try:
            if len(values) > 0:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
        except pymysql.err.OperationalError as inst2:
            util.soup_log("[Error] OperationError on {s} query".format(s=queryType))
            util.soup_log(str(inst2.args))
            util.soup_log("{s} query unsuccessful".format(s=queryType))
            return 0, list()

    util.soup_log("{s} query successful".format(s=queryType))
    return 1, [c for c in cursor]
