import sqlite3 as sql
from functools import reduce
from collections import namedtuple

from soup_util import soup_logging


_logger = soup_logging.get_logger()


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

    try:
        if not values:
            ret = conn.execute(query_str).fetchall()
        else:
            ret = conn.execute(query_str, values).fetchall()

    except sql.OperationalError as e1:
        _logger.warning(str(e1), exc_info=True)
        return _QueryResult(False, ())

    except sql.IntegrityError as e2:
        _logger.warning(str(e2), exc_info=True)
        return _QueryResult(False, ())

    except sql.Error as e3:
        _logger.warning(str(e3), exc_info=True)
        return _QueryResult(False, ())

    return _QueryResult(True, _flatten_query_results(ret) if flatten_results else ret)


def add_member(conn, uid, gid) -> bool:
    """Add a user to the db. Returns True if successful, False otherwise."""

    results = query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid,))

    return results.is_success
