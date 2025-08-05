from . import _soup_sql


def add(uid, gid, name, channel_id, end_time) -> int:
    """Adds a new timer. Returns the corresponding timer_id."""

    conn = _soup_sql.connect()

    if not uid in _soup_sql.query(conn, "SELECT uid FROM Users WHERE gid=?;", (gid,)).values:
        _soup_sql.add_member(conn, uid, gid)

    timer_id = _soup_sql.query(
        conn,
        "INSERT INTO UserTimers (uid, name, channel_id, end_time) VALUES (?, ?, ?, ?) RETURNING timer_id;",
        (uid, name, channel_id, end_time)
    ).values[0]

    conn.commit()
    conn.close()

    return timer_id

def remove(timer_id):
    """Remove a timer based on the timer_id."""

    conn = _soup_sql.connect()

    _soup_sql.query(conn, "DELETE FROM UserTimers WHERE timer_id=?;", (timer_id, ))

    conn.commit()
    conn.close()

def get_all() -> [dict]:
    """Returns a list of all active timers. Each element is a dictionary with the keys 'uid', 'name', 'channel_id',
    'end_time', and 'timer_id'."""

    conn = _soup_sql.connect()

    values = _soup_sql.query(conn, "SELECT uid, name, channel_id, end_time, timer_id FROM UserTimers;", flatten_results=False).values

    conn.close()
    return [{"uid": v[0], "name": v[1], "channel_id": v[2], "end_time": v[3], "timer_id": v[4]} for v in values]
