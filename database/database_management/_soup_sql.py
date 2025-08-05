import sqlite3 as _sql
from functools import reduce as _reduce
from collections import namedtuple as _namedtuple

from soup_util.soup_logging import logger as _logger


_DATABASE_NAME = "database/database.db"
_QueryResult = _namedtuple("_QueryResult", ["is_success", "values"])


def connect():
    return _sql.connect(_DATABASE_NAME)

def query(conn, query_str, values=tuple(), flatten_results=True) -> _QueryResult:
    try:
        if not values:
            ret = conn.execute(query_str).fetchall()
        else:
            ret = conn.execute(query_str, values).fetchall()

    except _sql.OperationalError as e1:
        _logger.warning(str(e1), exc_info=True)
        return _QueryResult(False, ())

    except _sql.IntegrityError as e2:
        _logger.warning(str(e2), exc_info=True)
        return _QueryResult(False, ())

    except _sql.Error as e3:
        _logger.warning(str(e3), exc_info=True)
        return _QueryResult(False, ())

    return _QueryResult(True, _flatten_query_results(ret) if flatten_results else ret)

def _flatten_query_results(selection):
    if not selection:
        return tuple()
    else:
        return tuple([x for x in _reduce(lambda x, y: x + y, selection) if x is not None])

def add_member(conn, uid, gid):
    query(conn, "INSERT INTO Users (uid, gid) VALUES (?, ?);", (uid, gid,))
