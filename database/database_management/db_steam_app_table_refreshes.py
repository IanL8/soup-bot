from . import _soup_sql


def add(start_time: int) -> bool:
    """Adds a new column to SteamAppTableRefreshes to track the progress of the current full apps table refresh."""

    conn = _soup_sql.connect()

    if not _soup_sql.query(conn, "INSERT INTO SteamAppTableRefreshes (start_time) VALUES (?);", (start_time,)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def update_last_app_id(start_time, last_app_id) -> bool:
    """Updates the last app_id updated for this refresh in SteamAppTableRefreshes."""

    conn = _soup_sql.connect()

    if not _soup_sql.query(conn, "UPDATE SteamAppTableRefreshes SET last_app_id=? WHERE start_time=?;", (last_app_id, start_time)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def get_last_app_id(start_time):
    """Gets the last app id of the refresh with the given start time. Returns None if the start time is not in the table."""

    conn = _soup_sql.connect()

    app_ids = _soup_sql.query(conn, "SELECT last_app_id FROM SteamAppTableRefreshes WHERE start_time=?;", (start_time,)).values

    conn.close()
    return None if len(app_ids) == 0 else app_ids[0]


def mark_refresh_complete(start_time) -> bool:
    """Marks the latest refresh as complete by setting the complete value to 1."""

    conn = _soup_sql.connect()

    if not _soup_sql.query(conn, "UPDATE SteamAppTableRefreshes SET complete=1 WHERE start_time=?;", (start_time,)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def get_incomplete_refresh_start_time():
    """Gets the start time of an incomplete table refresh if there is one. If not, returns None. There can only be one
    incomplete refresh at one time, and it must be the latest one."""

    conn = _soup_sql.connect()

    times = _soup_sql.query(conn, "SELECT start_time FROM SteamAppTableRefreshes WHERE complete=0;").values

    conn.close()
    return None if len(times) == 0 else times[0]


def get_latest_refresh_start_time():
    """Gets the start time of the most recent completed refresh. If the table is empty, returns -1."""

    conn = _soup_sql.connect()

    times = _soup_sql.query(conn, "SELECT MAX(start_time) FROM SteamAppTableRefreshes WHERE complete=1;").values

    conn.close()
    return -1 if len(times) == 0 else times[0]
