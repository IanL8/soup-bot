from . import _soup_sql


def init_database():
    """Set up db."""

    conn = _soup_sql.connect()

    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS Guilds("
        "gid INTEGER NOT NULL, "
        "flag VARCHAR(10) DEFAULT '!', "
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
        "CREATE TABLE IF NOT EXISTS UserCooldowns("
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
        "last_update_time INTEGER UNSIGNED, "
        "PRIMARY KEY (app_id) "
        ");"
    )
    _soup_sql.query(
        conn,
        "CREATE TABLE IF NOT EXISTS UserTimers("
        "timer_id INTEGER PRIMARY KEY ASC, "
        "uid INTEGER NOT NULL, "
        "name VARCHAR(200), "
        "channel_id INTEGER NOT NULL, "
        "end_time INTEGER, "
        "FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE CASCADE"
        ");"
    )

    conn.commit()
    conn.close()
