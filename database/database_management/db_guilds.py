from . import _soup_sql


def add(guild):
    """Add a guild to the db."""

    conn = _soup_sql.connect()

    if not guild.id in _soup_sql.query(conn, "SELECT gid FROM Guilds;").values:
        _soup_sql.query(conn, "INSERT INTO Guilds (gid) VALUES (?);", (guild.id,))

    conn.commit()
    conn.close()
    return True
