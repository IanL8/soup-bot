#
# imports
import random
import sqlite3 as sql
import time

#
# project imports
import soupbot_utilities as util

#
# globals
flags = dict()

#
# init database

# create tables
def init() -> bool:
    conn = sql.connect("../database.db")

    k = query(conn, "CREATE TABLE IF NOT EXISTS Guilds("
                    "gid INTEGER NOT NULL, "
                    "flag VARCHAR(10) DEFAULT '!', "
                    "general_chat INTEGER, "
                    "owner_id INTEGER NOT NULL, "
                    "PRIMARY KEY (gid) "
                    ");")
    if k == -1:
        return False

    k = query(conn, "CREATE TABLE IF NOT EXISTS Users("
                    "uid INTEGER NOT NULL, "
                    "gid INTEGER NOT NULL, "
                    "FOREIGN KEY(gid) REFERENCES Guilds(gid) ON DELETE CASCADE, "
                    "PRIMARY KEY (uid, gid) "
                    ");")
    if k == -1:
        return False

    k = query(conn, "CREATE TABLE IF NOT EXISTS UserTimers("
                    "tid VARCHAR(100) NOT NULL, "
                    "uid INTEGER NOT NULL, "
                    "start_time INT DEFAULT 0, "
                    "FOREIGN KEY(uid) REFERENCES Users(uid) ON DELETE CASCADE, "
                    "PRIMARY KEY (tid, uid) "
                    ");")
    if k == -1:
        return False

    k = query(conn, "CREATE TABLE IF NOT EXISTS Movies( "
                    "name VARCHAR(150), "
                    "gid INTEGER, "
                    "priority INTEGER DEFAULT 0, "
                    "PRIMARY KEY (name, gid), "
                    "FOREIGN KEY (gid) REFERENCES Guilds(gid) ON DELETE CASCADE "
                    ");")
    if k == -1:
        return False

    conn.commit()
    return True

#
# queries

# for db queries outside the scope of database_handler
# creates a connection and commits the transaction
def request(q, values=tuple()):
    conn = sql.connect("../database.db")

    k = query(conn, q, values)
    if k == -1:
        return k

    conn.commit()
    return k


# makes a query using the connection, SQL query, and its corresponding values
def query(conn, q, values=tuple()):
    k = -1
    queryType = q.split(" ")[0]
    try:
        if not values:
            k = conn.execute(q).fetchall()
        else:
            k = conn.execute(q, values).fetchall()
        util.soup_log(f"[SQL] {queryType} query {values if values else str()}")
    except sql.OperationalError as e1:
        util.soup_log(f"[Error] OperationError on {queryType} query")
        util.soup_log(f"Query values: {values}")
        util.soup_log(str(e1.args))
    except sql.IntegrityError as e2:
        util.soup_log(f"[Error] IntegrityError on {queryType} query")
        util.soup_log(f"Query values: {values}")
        util.soup_log(str(e2.args))
    except sql.Error as e3:
        util.soup_log(f"[Error] Unknown SQL error on {queryType} query")
        util.soup_log(f"Query values: {values}")
        util.soup_log(str(e3.args))

    finally:
        return k

#
# guilds

# returns true if a guild is added or if the guild is already in the db
def add_guild(guild) -> bool:
    conn = sql.connect("../database.db")
    gid = guild.id

    # if not already in Guilds
    k = query(conn, "SELECT gid FROM Guilds;")
    if k == -1:
        return False
    if not util.find_in_list(gid, k):
        # insert guild
        k = query(conn, "INSERT INTO Guilds (gid, general_chat, owner_id) VALUES (?, ?, ?);",
                  (gid, guild.text_channels[0].id, guild.owner_id))
        if k == -1:
            return False
        # insert guild members
        for m in guild.members:
            if not m.bot:
                query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (m.id, gid))

    conn.commit()
    return True


# returns true if a member is added or if the member is already in the db
def add_member(uid, gid) -> bool:
    conn = sql.connect("../database.db")

    # if member is not in guild
    k = query(conn, "SELECT uid FROM Users WHERE gid=?", (gid,))
    if k == -1:
        return False
    if not util.find_in_list(uid, k):
        # insert member
        k = query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid))
        if k == -1:
            return False

    conn.commit()
    return True

#
# flags

def get_flag(gid) -> str:
    conn = sql.connect("../database.db")

    # fetch flag from cache if possible
    if gid in flags.keys():
        return flags[gid]

    # fetch from db
    k = query(conn, "SELECT flag FROM Guilds WHERE gid=?;", (gid,))
    if k == -1:
        return "!"  # default

    # add to cache
    flags[gid] = k[0][0]

    return k[0][0]


def set_flag(uid, gid, newFlag):
    conn = sql.connect("../database.db")

    # if member is not the guild owner
    k = query(conn, "SELECT gid FROM Guilds WHERE owner_id=?;", (uid,))
    if k == -1:
        return False, "db error"
    if not util.find_in_list(gid, k):
        return False, "you do not have permission to use this command"

    # update flag
    k = query(conn, "UPDATE Guilds SET flag=? WHERE gid=?;", (newFlag, gid))
    if k == -1:
        return False, "db error"

    # commit transaction and update cache
    conn.commit()
    flags[gid] = newFlag
    return True, ""

#
# commands

def get_fortune(uid) -> str:
    conn = sql.connect("../database.db")
    lastUsage = 0

    # if member is not already in UserTimers
    k = query(conn, "SELECT tid FROM UserTimers WHERE uid=?;", (uid,))
    if k == -1:
        return "db error"
    if not util.find_in_list("fortune", k):
        # insert member
        k = query(conn, "INSERT INTO UserTimers (tid, uid) VALUES (?, ?);", ("fortune", uid))
        if k == -1:
            return "db error"
    # else, fetch the last usage of fortune
    else:
        k = query(conn, "SELECT start_time FROM UserTimers WHERE uid=?;", (uid,))
        if k == -1:
            return "db error"
        lastUsage = k[0][0]

    # if it has not been 20 hrs since the last use
    t = time.time() - lastUsage
    if t < 72000:
        return f"{util.time_to_string(72000 - t)} until next fortune redeem."

    # else, update the table with the current time and return the fortune
    k = query(conn, "UPDATE UserTimers SET start_time=? WHERE uid=?;", (int(time.time()), uid))
    if k == -1:
        return "db error"

    conn.commit()
    return util.FORTUNES[int(random.random() * len(util.FORTUNES))]


def add_movie(gid, movieName):
    conn = sql.connect("../database.db")

    # if movie is already in Movies
    k = query(conn, "SELECT name FROM Movies WHERE gid=?;", (gid, ))
    if k == -1:
        return False, "db error"
    if util.find_in_list(movieName, k):
        return False, "movie already in list"

    # get next highest priority
    k = query(conn, "SELECT MAX(priority) FROM Movies WHERE gid=?;", (gid, ))
    if k == -1:
        return False, "db error"
    p = 0 if (None, ) in k else k[0][0] + 1  # need to improve the readability of this

    # insert new movie into Movies
    k = query(conn, "INSERT INTO Movies (name, gid, priority) VALUES (?, ?, ?);", (movieName, gid, p))
    if k == -1:
        return False, "db error"

    conn.commit()
    return True, ""


def remove_movie(gid, movieName):
    conn = sql.connect("../database.db")

    # if movie not in Movies
    k = query(conn, "SELECT name FROM Movies WHERE gid=?;", (gid, ))  # should improve this
    if k == -1:
        return False, "db error"
    if not util.find_in_list(movieName, k):
        return False, "movie not in list"

    # remove movie from Movies
    k = query(conn, "DELETE FROM Movies WHERE name=? AND gid=?;", (movieName, gid))
    if k == -1:
        return False, "db error"

    conn.commit()
    return True, ""


def get_movie_list(gid) -> list:
    conn = sql.connect("../database.db")

    # get the movies for guild gid
    k = query(conn, "SELECT name FROM Movies WHERE gid=? ORDER BY priority;", (gid,))
    if k == -1:
        return []

    conn.commit()
    return k
