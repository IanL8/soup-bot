"""Abstracts database operations from the rest of the application. Can interact with the database by calling this
module's public functions."""

import sqlite3 as sql
import time
from random import choice
from functools import reduce

from soupbot_util.logger import soup_log
from soupbot_util.constants import FORTUNES


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


def _flatten_query_results(selection):
    if not selection:
        return tuple()
    else:
        return tuple(reduce(lambda x, y: x + y, selection))


def _query(conn, query, values=tuple()):
    """Returns the results of the query or 0 if an exception occurred."""

    queryType = query.split()[0]

    try:
        if not values:
            ret = conn.execute(query).fetchall()
        else:
            ret = conn.execute(query, values).fetchall()
        soup_log(f"{queryType} query {values if values else str()}", "sql")
    except sql.OperationalError as e1:
        soup_log(f"OperationError on {queryType} query", "err")
        soup_log(f"Query values: {values}", "err")
        soup_log(str(e1.args), "err")
        return 0
    except sql.IntegrityError as e2:
        soup_log(f"IntegrityError on {queryType} query", "err")
        soup_log(f"Query values: {values}", "err")
        soup_log(str(e2.args), "err")
        return 0
    except sql.Error as e3:
        soup_log(f"Unknown SQL error on {queryType} query", "err")
        soup_log(f"Query values: {values}", "err")
        soup_log(str(e3.args), "err")
        return 0

    return _flatten_query_results(ret)


#
# init database
DATABASE_NAME = "database.db"
_make_tables()

# incorporate a more efficient cache with an actual replacement policy if bot scales past more than a few servers
# until then this works ok
_prefix_cache = dict()


#
# db interface

# guilds, users, and prefixes
def add_guild(gid, main_chat_id, owner_id, member_ids) -> bool:
    """Add a guild and its members to db. Returns True if successful, False otherwise."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "SELECT gid FROM Guilds;")
    if ret == 0 or gid in ret:
        return False
    ret = _query(
        conn,
        "INSERT INTO Guilds (gid, general_chat, owner_id) VALUES (?, ?, ?);",
        (gid, main_chat_id, owner_id)
    )
    if ret == 0:
        return False
    for uid in member_ids:
        ret = _query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid))
        if ret == 0:
            return False

    conn.commit()
    return True


def add_member(uid, gid) -> bool:
    """Add a user to the db. Returns True if successful, False otherwise."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "SELECT uid FROM Users WHERE gid=?;", (gid, ))
    if ret == 0 or uid in ret:
        return False
    ret = _query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid,))
    if ret == 0:
        return False

    conn.commit()
    return True


def is_guild_owner(uid, gid) -> bool:
    """Returns True if the user is the guild owner, False otherwise."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "SELECT owner_id FROM Guilds WHERE gid=?;", (gid,))
    if ret == 0 or len(ret) == 0:
        return False

    return uid == ret[0]


def get_prefix(gid) -> str:
    """Fetches the command prefix for a guild."""

    if gid in _prefix_cache.keys():
        return _prefix_cache[gid]

    conn = sql.connect(DATABASE_NAME)
    prefix = "!" # default
    ret = _query(conn, "SELECT flag FROM Guilds WHERE gid=?;", (gid,))
    if ret != 0 and len(ret) == 1:
        prefix = ret[0]

    _prefix_cache[gid] = prefix
    return prefix


def set_prefix(gid, new_prefix) -> bool:
    """Sets the prefix for the guild to new_prefix. Returns True if successful, False otherwise."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "UPDATE Guilds SET flag=? WHERE gid=?;", (new_prefix, gid))
    if ret == 0:
        return False

    conn.commit()
    _prefix_cache[gid] = new_prefix
    return True


# command support
_TIME_UNITS = [(86400, "days"), (3600, "hours"), (60, "min"), (1, "sec")]

def _duration_to_string(duration) -> str:
    time_readout = ""
    for seconds, unit in _TIME_UNITS:
        unit_amount = int(duration / seconds)
        duration = duration % seconds
        if unit_amount > 0:
            time_readout += f"{unit_amount} {unit}, "

    return time_readout[:-2]


def fortune(uid) -> str:
    """Returns a random fortune, time until next usage, or database error if an exception occurs."""

    conn = sql.connect(DATABASE_NAME)
    last_usage_time = 0
    ret = _query(conn, "SELECT uid FROM UserTimers WHERE tid=?;", ("fortune",))

    if ret != 0 and uid in ret:
        ret = _query(conn, "SELECT start_time FROM UserTimers WHERE uid=?;", (uid,))
        if ret == 0 or len(ret) == 0:
            return "database error"
        last_usage_time = ret[0]
    else:
        ret = _query(conn, "INSERT INTO UserTimers (tid, uid) VALUES (?, ?);", ("fortune", uid))
        if ret == 0:
            return "database error"

    time_since_last_use = time.time() - last_usage_time
    if time_since_last_use < 72000:
        return f"{_duration_to_string(72000 - time_since_last_use)} until next fortune redeem."

    ret = _query(conn, "UPDATE UserTimers SET start_time=? WHERE uid=?;", (int(time.time()), uid))
    if ret == 0:
        return "database error"

    conn.commit()
    return choice(FORTUNES)


def movies_table_contains(gid, movie) -> bool:
    """Returns True if the movie+guild combination is in the db, False otherwise."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "SELECT name FROM Movies WHERE gid=?;", (gid, ))
    if ret == 0:
        return False

    return movie in ret


def add_movie(gid, movie) -> bool:
    """Adds a movie+guild id to the db. Returns True if successful, False otherwise."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "SELECT MAX(priority) FROM Movies WHERE gid=?;", (gid, ))
    if ret == 0:
        return False
    elif len(ret) != 0 and ret[0] is not None:
        priority = ret[0] + 1
    else:
        priority = 0
    ret = _query(
        conn,
        "INSERT INTO Movies (name, gid, priority) VALUES (?, ?, ?);",
        (movie, gid, priority)
    )
    if ret == 0:
        return False

    conn.commit()
    return True


def remove_movie(gid, movie) -> bool:
    """Removes the movie from the db. Returns True if successful, False otherwise."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "DELETE FROM Movies WHERE name=? AND gid=?;", (movie, gid))
    if ret == 0:
        return False

    conn.commit()
    return True


def get_movie_list(gid) -> list:
    """Return all movies for the given guild."""

    conn = sql.connect(DATABASE_NAME)
    ret = _query(conn, "SELECT name FROM Movies WHERE gid=? ORDER BY priority;", (gid,))
    if ret == 0:
        return []

    return list(ret)
