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
        except pymysql.err.IntegrityError as inst3:
            util.soup_log("[Error] IntegrityError on {s} query".format(s=queryType))
            util.soup_log(str(inst3.args))
            util.soup_log("[SQL] {s} query unsuccessful".format(s=queryType))
            return 0, list()

        util.soup_log("[SQL] {s} query successful".format(s=queryType))
        return 1, [c for c in self.cursor]

    def add_guild(self, guild):
        #
        # local vars
        k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
        output = list()             # holds the output of the query in make_query()
        gid = str(guild.id)         # holds the guild's ID

        k, output = self.make_query("SELECT gid FROM Guilds;")
        if k == 0:
            return 0

        if not util.find_in_list(gid, output):
            k, output = self.make_query("INSERT INTO Guilds (gid, general_chat, owner_id) VALUES (%s, %s, %s);",
                                        (gid, str(guild.text_channels[0].id), str(guild.owner_id)))
            if k == 0:
                return 0
            for m in guild.members:
                if not m.bot:
                    k, output = self.make_query("INSERT INTO Users (uid, gid) VALUES (%s, %s);", (str(m.id), gid))
                    if k == 0:
                        return 0
        return 1

    def add_member(self, uid, gid):
        #
        # local vars
        k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
        output = list()             # holds the output of the query in make_query()

        k, output = self.make_query("SELECT uid FROM Users WHERE gid=%s", (gid, ))
        if k == 0:
            return 0
        if not util.find_in_list(uid, output):
            k, output = self.make_query("INSERT INTO Users (uid, gid) VALUES (%s, %s);", (uid, gid))
            if k == 0:
                return 0
        return 1

    def get_flag(self, gid):
        #
        # local vars
        k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
        output = list()             # holds the output of the query in make_query()

        k, output = self.make_query("SELECT flag FROM Guilds WHERE gid=%s;", (gid, ))
        return output[0][0]

    def add_movie(self, gid, movieName):
        #
        # local vars
        k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
        output = list()             # holds the output of the query in make_query()
        k, output = self.make_query("SELECT gid FROM MovieLists;")
        if k == 0:
            return 0
        if not util.find_in_list(gid, output):
            k, output = self.make_query("INSERT INTO MovieLists (gid) VALUES (%s);", (gid, ))
            if k == 0:
                return 0
        k, output = self.make_query("INSERT INTO Movies (name, gid) VALUES (%s, %s);", (movieName, gid))
        if k == 0:
            return 0
        return 1

    def remove_movie(self, gid, movieName):
        #
        # local vars
        k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
        output = list()             # holds the output of the query in make_query()
        k, output = self.make_query("SELECT gid FROM MovieLists;")
        if k == 0:
            return 0
        if not util.find_in_list(gid, output):
            return "No movie list"
        k, output = self.make_query("SELECT name FROM Movies;")
        if k == 0:
            return 0
        if not util.find_in_list(movieName, output):
            return 0
        k, output = self.make_query("DELETE FROM Movies WHERE name=%s AND gid=%s;", (movieName, gid))
        if k == 0:
            return 0
        return 1

    def get_movie_list(self, gid):
        #
        # local vars
        k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
        output = list()             # holds the output of the query in make_query()
        k, output = self.make_query("SELECT gid FROM MovieLists;")
        if k == 0:
            return 0
        if util.find_in_list(gid, output):
            k, output = self.make_query("SELECT name FROM Movies WHERE gid=%s;", (gid, ))
            if k == 0:
                return 0
        return output
