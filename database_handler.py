import random
import sqlite3 as sql
import time
from functools import reduce

import soupbot_utilities as util


#
# helper functions
def _one_col_selection_to_tuple(selection):
    if not selection:
        return tuple()
    else:
        return reduce(lambda x, y: x + y, selection)

#
# core database operations
def _make_tables():

    conn = sql.connect(DATABASE_NAME)

    _query(
        conn,
        "CREATE TABLE IF NOT EXISTS Guilds("
        "gid INTEGER NOT NULL, "
        "flag VARCHAR(10) DEFAULT '!', "
        "general_chat INTEGER, "
        "owner_id INTEGER NOT NULL, "
        "PRIMARY KEY (gid) "
        ");"
    )
    _query(
        conn,
        "CREATE TABLE IF NOT EXISTS Users("
        "uid INTEGER NOT NULL, "
        "gid INTEGER NOT NULL, "
        "FOREIGN KEY(gid) REFERENCES Guilds(gid) ON DELETE CASCADE, "
        "PRIMARY KEY (uid, gid) "
        ");"
    )
    _query(
        conn,
        "CREATE TABLE IF NOT EXISTS UserTimers("
        "tid VARCHAR(100) NOT NULL, "
        "uid INTEGER NOT NULL, "
        "start_time INT DEFAULT 0, "
        "FOREIGN KEY(uid) REFERENCES Users(uid) ON DELETE CASCADE, "
        "PRIMARY KEY (tid, uid) "
        ");"
    )
    _query(
        conn,
        "CREATE TABLE IF NOT EXISTS Movies( "
        "name VARCHAR(150), "
        "gid INTEGER, "
        "priority INTEGER DEFAULT 0, "
        "PRIMARY KEY (name, gid), "
        "FOREIGN KEY (gid) REFERENCES Guilds(gid) ON DELETE CASCADE "
        ");"
    )
    conn.commit()

def _query(conn, query, values=tuple()):
    """Returns the results of the query or 0 if an exception occurred"""

    queryType = query.split(" ")[0]
    ret = []

    try:
        if not values:
            ret = conn.execute(query).fetchall()
        else:
            ret = conn.execute(query, values).fetchall()
        util.soup_log(f"[SQL] {queryType} query {values if values else str()}")
    except sql.OperationalError as e1:
        ret = 0
        util.soup_log(f"[Error] OperationError on {queryType} query")
        util.soup_log(f"Query values: {values}")
        util.soup_log(str(e1.args))
    except sql.IntegrityError as e2:
        ret = 0
        util.soup_log(f"[Error] IntegrityError on {queryType} query")
        util.soup_log(f"Query values: {values}")
        util.soup_log(str(e2.args))
    except sql.Error as e3:
        ret = 0
        util.soup_log(f"[Error] Unknown SQL error on {queryType} query")
        util.soup_log(f"Query values: {values}")
        util.soup_log(str(e3.args))
    finally:
        return ret


#
# init database
DATABASE_NAME = "database.db"
_make_tables()

# small cache - incorporate a more efficient cache if bot scales past more than a few servers
_prefix_cache = dict()


#
# functions for use by other modules

# guilds, users, and prefixes
def add_guild(gid, main_chat_id, owner_id, member_ids) -> bool:
    """Add a guild and its members to db. Returns True if successful, False otherwise"""

    conn = sql.connect(DATABASE_NAME)

    # check if already in table
    ret = _query(conn, "SELECT gid FROM Guilds;")
    if ret == 0 or gid in _one_col_selection_to_tuple(ret):
        return False

    ret = _query(
        conn,
        "INSERT INTO Guilds (gid, general_chat, owner_id) VALUES (?, ?, ?);",
        (gid, main_chat_id, owner_id)
    )
    if ret == 0:
        return False

    for uid in member_ids:
        _query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid))

    conn.commit()
    return True

def add_member(uid, gid) -> bool:
    """Add a user to the db. Returns True if successful, False otherwise"""

    conn = sql.connect(DATABASE_NAME)

    # check if already in table
    ret = _query(conn, "SELECT uid FROM Users WHERE gid=?;", (gid, ))
    if not ret or uid in _one_col_selection_to_tuple(ret):
        return False

    ret = _query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid,))
    if ret == 0: return False

    conn.commit()
    return True

def is_guild_owner(uid, gid) -> bool:
    """Returns True if the user is the guild owner, False otherwise"""

    conn = sql.connect(DATABASE_NAME)

    ret = _query(conn, "SELECT owner_id FROM Guilds WHERE gid=?;", (gid,))
    if not ret:
        return False

    return uid == ret[0][0]

def get_prefix(gid) -> str:
    """Fetches the command signifier, or prefix, from the db or cache"""

    if gid in _prefix_cache.keys():
        return _prefix_cache[gid]

    conn = sql.connect(DATABASE_NAME)

    prefix = "!" # default
    ret = _query(conn, "SELECT flag FROM Guilds WHERE gid=?;", (gid,))
    if ret:
        prefix = ret[0][0]

    _prefix_cache[gid] = prefix
    return prefix

def set_prefix(gid, new_prefix):
    """Sets the prefix for the guild to new_prefix. Returns True if successful, False otherwise"""

    conn = sql.connect(DATABASE_NAME)

    ret = _query(conn, "UPDATE Guilds SET flag=? WHERE gid=?;", (new_prefix, gid))
    if ret == 0:
        return False

    conn.commit()
    _prefix_cache[gid] = new_prefix
    return True

# command support
def get_fortune(uid) -> str:
    """Returns a random fortune, time until next usage, or database error if an exception occurs"""
    conn = sql.connect(DATABASE_NAME)
    last_usage_time = 0

    ret = _query(conn, "SELECT uid FROM UserTimers WHERE tid=?;", ("fortune",))

    # => if list is empty or uid not in list
    if not (ret and uid in _one_col_selection_to_tuple(ret)):
        ret = _query(conn, "INSERT INTO UserTimers (tid, uid) VALUES (?, ?);", ("fortune", uid))
        if ret == 0:
            return "database error"
    else:
        ret = _query(conn, "SELECT start_time FROM UserTimers WHERE uid=?;", (uid,))
        if ret == 0:
            return "database error"
        last_usage_time = ret[0][0]

    time_since_last_use = time.time() - last_usage_time
    if time_since_last_use < 72000:
        return f"{util.time_to_string(72000 - time_since_last_use)} until next fortune redeem."

    ret = _query(conn, "UPDATE UserTimers SET start_time=? WHERE uid=?;", (int(time.time()), uid))
    if ret == 0:
        return "database error"

    conn.commit()
    return util.FORTUNES[int(random.random() * len(util.FORTUNES))]

def movies_table_contains(gid, movie):
    """Returns True if the movie+guild id combination is in the table, False otherwise"""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "SELECT name FROM Movies WHERE gid=?;", (gid, ))
    if not ret:
        return False

    return movie in _one_col_selection_to_tuple(ret)

def add_movie(gid, movie):
    """Adds a movie+guild id to the db. Returns True if successful, False otherwise"""

    conn = sql.connect(DATABASE_NAME)
    priority = 0

    ret = _query(conn, "SELECT MAX(priority) FROM Movies WHERE gid=?;", (gid, ))
    if ret == 0:
        return False
    elif ret[0][0]:
        priority = ret[0][0] + 1

    ret = _query(
        conn,
        "INSERT INTO Movies (name, gid, priority) VALUES (?, ?, ?);",
        (movie, gid, priority)
    )
    if ret == 0:
        return False

    conn.commit()
    return True

def remove_movie(gid, movie):
    """Removes the movie from the db. Returns True if successful, False otherwise"""

    conn = sql.connect(DATABASE_NAME)

    ret = _query(conn, "DELETE FROM Movies WHERE name=? AND gid=?;", (movie, gid))
    if ret == 0:
        return False

    conn.commit()
    return True

def get_movie_list(gid) -> list:
    """Return all movies for the guild"""

    conn = sql.connect(DATABASE_NAME)

    ret = _query(conn, "SELECT name FROM Movies WHERE gid=? ORDER BY priority;", (gid,))
    if not ret:
        return []

    conn.commit()
    return list(_one_col_selection_to_tuple(ret))
