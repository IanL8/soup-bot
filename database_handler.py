#
# imports
import random
import sqlite3 as sql
import time

#
# project imports
import soupbot_utilities as util


# create tables
def init() -> bool:
    conn = sql.connect("database.db")

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

def request(q, values=tuple()):
    conn = sql.connect("database.db")

    k = query(conn, q, values)
    if k == -1:
        return k

    conn.commit()
    return k


# makes a query using the SQL query and its corresponding values
# returns either (1, query result) if successful, or (0, empty list) if unsuccessful
def query(conn, q, values=tuple()):
    k = -1
    queryType = q.split(" ")[0]
    try:
        if not values:
            k = conn.execute(q).fetchall()
        else:
            k = conn.execute(q, values).fetchall()
    except sql.OperationalError as e1:
        util.soup_log("[Error] OperationError on {s} query".format(s=queryType))
        util.soup_log(str(e1.args))
    except sql.IntegrityError as e2:
        util.soup_log("[Error] IntegrityError on {s} query".format(s=queryType))
        util.soup_log(str(e2.args))
    except sql.Error as e3:
        util.soup_log("[Error] Unknown SQL error on {s} query".format(s=queryType))
        util.soup_log(str(e3.args))
    finally:
        return k


def add_guild(guild) -> bool:
    gid = guild.id
    conn = sql.connect("database.db")

    k = query(conn, "SELECT gid FROM Guilds;")
    if k == -1:
        return False
    if not util.find_in_list(gid, k):
        k = query(conn, "INSERT INTO Guilds (gid, general_chat, owner_id) VALUES (?, ?, ?);",
                  (gid, guild.text_channels[0].id, guild.owner_id))
        if k == -1:
            return False
        for m in guild.members:
            if not m.bot:
                query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (m.id, gid))

    conn.commit()
    return True


def add_member(uid, gid) -> bool:
    conn = sql.connect("database.db")

    k = query(conn, "SELECT uid FROM Users WHERE gid=?", (gid,))
    if k == -1:
        return False
    if not util.find_in_list(uid, k):
        k = query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid))
        if k == -1:
            return False

    conn.commit()
    return True


def get_flag(gid) -> str:
    conn = sql.connect("database.db")

    k = query(conn, "SELECT flag FROM Guilds WHERE gid=?;", (gid,))
    if k == -1:
        return "!"  # default

    return k[0][0]


def get_fortune(uid) -> str:
    conn = sql.connect("database.db")
    lastUsage = 0

    # check if userId is already in the table
    k = query(conn, "SELECT tid FROM UserTimers WHERE uid=?;", (uid,))
    if k == -1:
        return "[Error] Bad query"

    # if not, add them to the table
    if not util.find_in_list("fortune", k):
        k = query(conn, "INSERT INTO UserTimers (tid, uid) VALUES (?, ?);", ("fortune", uid))
        if k == -1:
            return "[Error] Bad query"
    # if they are, fetch the last time fortune was used
    else:
        k = query(conn, "SELECT start_time FROM UserTimers WHERE uid=?;", (uid,))
        if k == -1:
            return "[Error] Bad query"
        lastUsage = k[0][0]

    # if it has not been 20 hrs, return the time remaining to the next use
    t = time.time() - lastUsage
    if t < 72000:
        return util.time_remaining_to_string(72000 - t) + " until next fortune redeem."

    # update the table with the current time and return the fortune
    k = query(conn, "UPDATE UserTimers SET start_time=? WHERE uid=?;", (int(time.time()), uid))
    if k == -1:
        return "[Error] Bad query"

    conn.commit()
    return util.FORTUNES[int(random.random() * len(util.FORTUNES))]


def add_movie(gid, movieName) -> bool:
    conn = sql.connect("database.db")

    k = query(conn, "SELECT name FROM Movies WHERE gid=?;", (gid, ))
    if k == -1 or util.find_in_list(movieName, k):
        return False
    k = query(conn, "SELECT MAX(priority) FROM Movies WHERE gid=?;", (gid, ))
    if k == -1:
        return False
    p = 0 if (None, ) in k else k[0][0] + 1  # need to improve the readability of this
    k = query(conn, "INSERT INTO Movies (name, gid, priority) VALUES (?, ?, ?);", (movieName, gid, p))
    if k == -1:
        return False

    conn.commit()
    return True


def remove_movie(gid, movieName) -> bool:
    conn = sql.connect("database.db")

    k = query(conn, "SELECT name FROM Movies WHERE gid=?;", (gid, ))  # should improve this
    if k == -1 or not util.find_in_list(movieName, k):
        return False
    k = query(conn, "DELETE FROM Movies WHERE name=? AND gid=?;", (movieName, gid))
    if k == -1:
        return False

    conn.commit()
    return True


def get_movie_list(gid) -> list:
    conn = sql.connect("database.db")

    k = query(conn, "SELECT gid FROM Movies;")
    if k == -1:
        return []
    if not util.find_in_list(gid, k):
        return []
    k = query(conn, "SELECT name FROM Movies WHERE gid=? ORDER BY priority;", (gid,))
    if k == -1:
        return []

    conn.commit()
    return k
