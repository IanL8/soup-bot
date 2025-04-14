from . import _soup_sql


def add(guild) -> bool:
    """Add a guild to the db. Returns True if successful, False otherwise."""

    conn = _soup_sql.connect()

    if guild.id in _soup_sql.query(conn, "SELECT gid FROM Guilds;").values:
        conn.close()
        return True

    if not _soup_sql.query(conn, "INSERT INTO Guilds (gid, general_chat) VALUES (?, ?);", (guild.id, guild.text_channels[0].id)).is_success:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True
