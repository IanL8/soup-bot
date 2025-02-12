"""Abstracts database operations from the rest of the application. Can interact with the database by calling this
module's public functions."""

import sqlite3 as sql
import time
from random import choice
from functools import reduce
from collections import namedtuple

from soupbot_util.logger import soup_log
from soupbot_util.constants import FORTUNES


_DATABASE_NAME = "database/database.db"
_QueryResult = namedtuple("_QueryResult", ["is_success", "values"])


def _flatten_query_results(selection):
    if not selection:
        return tuple()
    else:
        return tuple([x for x in reduce(lambda x, y: x + y, selection) if x is not None])


def _query(conn, query, values=tuple()) -> _QueryResult:
    """Returns the results of the query or None if an exception occurred."""

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
        return _QueryResult(False, ())

    except sql.IntegrityError as e2:
        soup_log(f"IntegrityError on {queryType} query", "err")
        soup_log(f"Query values: {values}", "err")
        soup_log(str(e2.args), "err")
        return _QueryResult(False, ())

    except sql.Error as e3:
        soup_log(f"Unknown SQL error on {queryType} query", "err")
        soup_log(f"Query values: {values}", "err")
        soup_log(str(e3.args), "err")
        return _QueryResult(False, ())

    return _QueryResult(True, _flatten_query_results(ret))


def _duration_to_string(duration) -> str:
    time_readout = ""

    for seconds, unit in [(86400, "days"), (3600, "hours"), (60, "minutes"), (1, "seconds")]:
        unit_amount = int(duration / seconds)
        duration = duration % seconds
        time_readout += f"{unit_amount} {unit}, " if unit_amount > 0 else ""

    return time_readout[:-2]


def _add_member(conn, uid, gid) -> bool:
    """Add a user to the db. Returns True if successful, False otherwise."""

    results = _query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid,))

    return results.is_success


#
# db interface


def init_database():
    """Set up db."""

    conn = sql.connect(_DATABASE_NAME)

    _query(
        conn,
        "CREATE TABLE IF NOT EXISTS Guilds("
        "gid INTEGER NOT NULL, "
        "flag VARCHAR(10) DEFAULT '!', "
        "general_chat INTEGER, "
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
    conn.close()


def add_guild(guild) -> bool:
    """Add a guild to the db. Returns True if successful, False otherwise."""

    conn = sql.connect(_DATABASE_NAME)

    if guild.id in _query(conn, "SELECT gid FROM Guilds;").values:
        conn.close()
        return True

    if not _query(conn, "INSERT INTO Guilds (gid, general_chat) VALUES (?, ?);", (guild.id, guild.text_channels[0].id)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def fortune(user) -> str:
    """Returns a random fortune, or time until next usage is available."""

    conn = sql.connect(_DATABASE_NAME)

    # don't report db errors to user - better to let the cooldown portion fail and still give them their fortune redeem

    if not user.id in _query(conn, "SELECT uid FROM Users WHERE gid=?;", (user.guild.id,)).values:
        _add_member(conn, user.id, user.guild.id)

    user_ids = _query(conn, "SELECT uid FROM UserTimers WHERE tid='fortune';").values
    if user.id in user_ids:
        last_usage_time = _query(conn, "SELECT start_time FROM UserTimers WHERE uid=?;", (user.id,)).values[0]
    else:
        _query(conn, "INSERT INTO UserTimers (tid, uid) VALUES ('fortune', ?);", (user.id,))
        last_usage_time = 0

    time_since_last_use = time.time() - last_usage_time
    if time_since_last_use < 72000:
        conn.close()
        return f"{_duration_to_string(72000 - time_since_last_use)} until next fortune redeem."

    _query(conn, "UPDATE UserTimers SET start_time=? WHERE tid='fortune' AND uid=?;", (int(time.time()), user.id))

    conn.commit()
    conn.close()
    return choice(FORTUNES)


def movies_table_contains(guild, movie) -> bool:
    """Returns True if the movie is in the db for this guild, False otherwise."""

    conn = sql.connect(_DATABASE_NAME)

    movies = _query(conn, "SELECT name FROM Movies WHERE gid=?;", (guild.id, )).values

    conn.close()
    return movie in movies


def add_movie(guild, movie) -> bool:
    """Adds a movie to the db for this guild. Returns True if successful, False otherwise."""

    conn = sql.connect(_DATABASE_NAME)

    results = _query(conn, "SELECT MAX(priority) FROM Movies WHERE gid=?;", (guild.id, ))

    if not results.is_success:
        conn.close()
        return False

    priority = 0 if len(results.values) == 0 else results.values[0] + 1

    if not _query(conn, "INSERT INTO Movies (name, gid, priority) VALUES (?, ?, ?);", (movie, guild.id, priority)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def remove_movie(guild, movie) -> bool:
    """Removes the movie from the db for this guild. Returns True if successful, False otherwise."""

    conn = sql.connect(_DATABASE_NAME)

    if not _query(conn, "DELETE FROM Movies WHERE name=? AND gid=?;", (movie, guild.id)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def get_movie_list(guild) -> list:
    """Return all movies for the given guild."""

    conn = sql.connect(_DATABASE_NAME)

    movies = _query(conn, "SELECT name FROM Movies WHERE gid=? ORDER BY priority;", (guild.id,)).values

    conn.close()
    return list(movies)
