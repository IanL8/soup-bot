#
# imports
import pymysql

#
# project imports
import soupbot_utilities as util


#
# database handler
class DatabaseHandler(object):

    # init
    def __init__(self, u, p, h, d):
        self.user, self.password, self.host, self.db = u, p, h, d
        self.cursor, self.conn = None, None
        self.connected = False

    # makes the connection to the mysql database
    def connect(self):
        util.soup_log("Trying to connect to mysql...")
        if not self.connected:
            self.conn = pymysql.connect(user=self.user, password=self.password, host=self.host, database=self.db)
            self.conn.autocommit(True)
            self.cursor = self.conn.cursor()
            self.connected = True
            util.soup_log("Connection successful")
        else:
            util.soup_log("[Error] Already connected")

    # disconnects from the mysql database
    def disconnect(self):
        util.soup_log("Trying to disconnect from mysql...")
        if self.connected:
            self.cursor.close()
            self.conn.close()
            self.connected = False
            util.soup_log("Disconnection successful")
        else:
            util.soup_log("[Error] Not connected")

    # makes a query using the SQL query and its corresponding values
    # returns either (1, query result) if successful, or (0, empty list) if unsuccessful
    def make_query(self, query, values=tuple()):
        queryType = query.split(" ")[0]
        #
        # attempt query
        try:
            if len(values) > 0:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
        except pymysql.err.OperationalError as inst1:
            util.soup_log("[Error] OperationError on {s} query".format(s=queryType))
            util.soup_log(str(inst1.args))
            util.soup_log("Restarting connection...")
            self.disconnect()
            self.connect()
            util.soup_log("Restart successful")
            #
            # attempt query again
            util.soup_log("[SQL] Reattempting {s} query...".format(s=queryType))
            try:
                if len(values) > 0:
                    self.cursor.execute(query, values)
                else:
                    self.cursor.execute(query)
            except pymysql.err.OperationalError as inst2:
                util.soup_log("[Error] OperationError on {s} query".format(s=queryType))
                util.soup_log(str(inst2.args))
                util.soup_log("[SQL] {s} query unsuccessful".format(s=queryType))
                return 0, list()

        util.soup_log("[SQL] {s} query successful".format(s=queryType))
        return 1, [c for c in self.cursor]
