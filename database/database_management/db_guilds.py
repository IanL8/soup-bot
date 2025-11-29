from . import _soup_sql


_prefix_cache = dict()


def add(guild):
    """Add a guild to the db."""

    conn = _soup_sql.connect()

    if not guild.id in _soup_sql.query(conn, "SELECT gid FROM Guilds;").values:
        _soup_sql.query(conn, "INSERT INTO Guilds (gid) VALUES (?);", (guild.id,))

    conn.commit()
    conn.close()
    return True

def get_prefix(guild):
    """Fetches the basic command prefix for this guild."""

    if guild.id in _prefix_cache.keys():
        return _prefix_cache[guild.id]

    conn = _soup_sql.connect()

    prefix = _soup_sql.query(conn, "SELECT flag FROM Guilds WHERE gid=?;", (guild.id,)).values[0]

    _prefix_cache[guild.id] = prefix
    return prefix

def set_prefix(guild, new_prefix):
    """Sets the prefix for the guild to new_prefix."""

    conn = _soup_sql.connect()

    _soup_sql.query(conn, "UPDATE Guilds SET flag=? WHERE gid=?;", (new_prefix, guild.id))

    conn.commit()
    _prefix_cache[guild.id] = new_prefix
