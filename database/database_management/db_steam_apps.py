from . import _soup_sql


def is_empty() -> bool:
    """Returns True if the table is empty. If not, returns False"""

    conn = _soup_sql.connect()

    _is_empty = len(_soup_sql.query(conn, "SELECT app_id FROM SteamApps;").values) == 0

    conn.close()
    return _is_empty


def add_or_update(app_id, name, searchable_name, search_priority) -> bool:
    """Adds a steam app to SteamApps, or updates its data if its already in the table."""

    conn = _soup_sql.connect()

    if app_id in _soup_sql.query(conn, "SELECT app_id FROM SteamApps;").values:

        if not _soup_sql.query(conn, "UPDATE SteamApps SET name=?, searchable_name=?, search_priority=? WHERE app_id=?;",
                     (name, searchable_name, search_priority, app_id)).is_success:
            conn.close()
            return False

    elif not _soup_sql.query(conn, "INSERT INTO SteamApps (app_id, name, searchable_name, search_priority) VALUES (?, ?, ?, ?);",
                   (app_id, name, searchable_name, search_priority)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def get_all_app_ids() -> [int]:
    """Returns a list of all app ids in the table."""

    conn = _soup_sql.connect()

    values = _soup_sql.query(conn, "SELECT app_id FROM SteamApps;")

    conn.close()
    return values


def search(app_name, searchable_name) -> [dict]:
    """Search the list of steam games by app name. Returns the best match by name and search priority,
    or None if nothing is found for the entered name."""

    conn = _soup_sql.connect()

    # check for perfect match
    apps = _soup_sql.query(
        conn,
        "SELECT app_id, name FROM SteamApps WHERE LOWER(name)=? ORDER BY search_priority DESC;",
        (app_name.lower(),),
        False
    ).values

    # if none, find best option
    if len(apps) == 0:
        apps = _soup_sql.query(
            conn,
            "SELECT app_id, name FROM SteamApps WHERE searchable_name LIKE ? ORDER BY search_priority DESC;",
            (f"%{searchable_name}%",),
            False
        ).values

    conn.close()
    if len(apps) == 0:
        return None

    app = apps[0]

    return {"appid": app[0], "name": app[1]}
