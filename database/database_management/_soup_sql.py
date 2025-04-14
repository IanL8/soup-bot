import sqlite3 as sql
from functools import reduce
from collections import namedtuple

from soupbot_util.logger import soup_log


_DATABASE_NAME = "database/database.db"
_QueryResult = namedtuple("_QueryResult", ["is_success", "values"])


def _flatten_query_results(selection):
    if not selection:
        return tuple()
    else:
        return tuple([x for x in reduce(lambda x, y: x + y, selection) if x is not None])


def connect():
    return sql.connect(_DATABASE_NAME)


def query(conn, query_str, values=tuple(), flatten_results=True) -> _QueryResult:
    """Returns the results of the query or None if an exception occurred."""

    queryType = query_str.split()[0]

    try:
        if not values:
            ret = conn.execute(query_str).fetchall()
        else:
            ret = conn.execute(query_str, values).fetchall()

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

    return _QueryResult(True, _flatten_query_results(ret) if flatten_results else ret)


def add_member(conn, uid, gid) -> bool:
    """Add a user to the db. Returns True if successful, False otherwise."""

    results = query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid,))

    return results.is_success


# add/update app
# make a new refresh table entry
# update last app entered, update when complete
# return incomplete refresh; return start time of refresh or None if all completed
# search table; return top result sort by search prio
# get all app_ids
# remove app by id
