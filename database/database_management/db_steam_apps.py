from . import _soup_sql


def is_empty() -> bool:
    """Returns True if the table is empty. If not, returns False"""

    conn = _soup_sql.connect()

    _is_empty = len(_soup_sql.query(conn, "SELECT app_id FROM SteamApps;").values) == 0

    conn.close()
    return _is_empty

def add_or_update(app_id, name, searchable_name, search_priority, last_update_time):
    """Adds a steam app to SteamApps, or updates its data if its already in the table."""

    conn = _soup_sql.connect()

    if app_id in _soup_sql.query(conn, "SELECT app_id FROM SteamApps;").values:
        _soup_sql.query(
                conn,
                "UPDATE SteamApps SET name=?, searchable_name=?, search_priority=?, last_update_time=? WHERE app_id=?;",
                (name, searchable_name, search_priority, app_id, last_update_time)
        )
    else:
        _soup_sql.query(
            conn,
            "INSERT INTO SteamApps (app_id, name, searchable_name, search_priority, last_update_time) VALUES (?, ?, ?, ?, ?);",
            (app_id, name, searchable_name, search_priority, last_update_time)
        )

    conn.commit()
    conn.close()

def get_all_app_ids() -> [int]:
    """Returns a list of all app ids in the table."""

    conn = _soup_sql.connect()

    values = _soup_sql.query(conn, "SELECT app_id FROM SteamApps;").values

    conn.close()
    return values

def get_oldest_by_update_time(amount) -> [int]:
    """Returns a list of the oldest [amount] app ids."""

    if amount < 1:
        return []

    conn = _soup_sql.connect()

    values = _soup_sql.query(conn, "SELECT app_id FROM SteamApps ORDER BY last_update_time ASC LIMIT ?", (amount,)).values

    conn.close()
    return values

def remove_all(app_ids):
    """Removes all apps by app_id in the provided list."""

    conn = _soup_sql.connect()

    for app_id in app_ids:
        _soup_sql.query(conn, "DELETE FROM SteamApps WHERE app_id=?", (app_id,))

    conn.commit()
    conn.close()

def search(app_name = None, searchable_name = None) -> [dict]:
    """Search the table of steam games by searchable_name for potential matches, or by exact app name with app_name.
    Returns the best matches, or an empty list if nothing is found. Each element in the returned list is a
    dictionary with the keys 'appid', 'name' and 'search_priority'. The list is sorted descending by search_priority."""

    if app_name is None and searchable_name is None:
        return []

    conn = _soup_sql.connect()

    # check for perfect match
    if app_name is not None:
        apps = _soup_sql.query(
            conn,
            "SELECT app_id, name, search_priority FROM SteamApps WHERE LOWER(name)=?;",
            (app_name,),
            False
        ).values
    else:
        apps = _soup_sql.query(
            conn,
            "SELECT app_id, name, search_priority FROM SteamApps WHERE LOWER(name) LIKE ? ORDER BY search_priority DESC;",
            (f"%{searchable_name}%",),
            False
        ).values

    conn.close()
    return [{"appid": app[0], "name": app[1], "search_priority": app[2]} for app in apps]
