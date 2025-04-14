from . import _soup_sql


def init_database():
    """Set up db."""

    conn = _soup_sql.connect()

    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS Guilds("
        "gid INTEGER NOT NULL, "
        "flag VARCHAR(10) DEFAULT '!', "
        "general_chat INTEGER, "
        "PRIMARY KEY (gid) "
        ");"
    )
    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS Users("
        "uid INTEGER NOT NULL, "
        "gid INTEGER NOT NULL, "
        "FOREIGN KEY(gid) REFERENCES Guilds(gid) ON DELETE CASCADE, "
        "PRIMARY KEY (uid, gid) "
        ");"
    )
    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS UserTimers("
        "tid VARCHAR(100) NOT NULL, "
        "uid INTEGER NOT NULL, "
        "start_time INT DEFAULT 0, "
        "FOREIGN KEY(uid) REFERENCES Users(uid) ON DELETE CASCADE, "
        "PRIMARY KEY (tid, uid) "
        ");"
    )
    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS Movies( "
        "name VARCHAR(150), "
        "gid INTEGER, "
        "priority INTEGER DEFAULT 0, "
        "PRIMARY KEY (name, gid), "
        "FOREIGN KEY (gid) REFERENCES Guilds(gid) ON DELETE CASCADE "
        ");"
    )
    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS SteamApps("
        "app_id INTEGER NOT NULL, "
        "name VARCHAR(40), "
        "searchable_name VARCHAR(40), "
        "search_priority DOUBLE, "
        "PRIMARY KEY (app_id) "
        ");"
    )
    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS SteamAppTableRefreshes("
        "start_time INTEGER UNSIGNED NOT NULL, "
        "last_app_id INTEGER, "
        "complete BOOL DEFAULT 0, "
        "PRIMARY KEY (start_time) "
        ");"
    )
    conn.commit()
    conn.close()
