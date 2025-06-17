from . import _soup_sql


def contains(guild, movie) -> bool:
    """Returns True if the movie is in the db for this guild, False otherwise."""

    conn = _soup_sql.connect()

    movies = _soup_sql.query(conn, "SELECT name FROM Movies WHERE gid=?;", (guild.id,)).values

    conn.close()
    return movie in movies


def add(guild, movie):
    """Adds a movie to the db for this guild."""

    conn = _soup_sql.connect()

    results = _soup_sql.query(conn, "SELECT MAX(priority) FROM Movies WHERE gid=?;", (guild.id,))

    priority = 0 if len(results.values) == 0 else results.values[0] + 1

    _soup_sql.query(conn, "INSERT INTO Movies (name, gid, priority) VALUES (?, ?, ?);", (movie, guild.id, priority))

    conn.commit()
    conn.close()


def remove(guild, movie):
    """Removes the movie from the db for this guild. Returns True if successful, False otherwise."""

    conn = _soup_sql.connect()

    _soup_sql.query(conn, "DELETE FROM Movies WHERE name=? AND gid=?;", (movie, guild.id))

    conn.commit()
    conn.close()


def get_all(guild) -> list:
    """Return all movies for the given guild."""

    conn = _soup_sql.connect()

    movies = _soup_sql.query(conn, "SELECT name FROM Movies WHERE gid=? ORDER BY priority;", (guild.id,)).values

    conn.close()
    return list(movies)
