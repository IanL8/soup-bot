from random import choice as _choice
import time as _time

from . import _soup_sql
from soup_util.constants import FORTUNES as _FORTUNES


def _duration_to_string(duration) -> str:
    time_readout = ""

    for seconds, unit in [(86400, "days"), (3600, "hours"), (60, "minutes"), (1, "seconds")]:
        unit_amount = int(duration / seconds)
        duration = duration % seconds
        time_readout += f"{unit_amount} {unit}, " if unit_amount > 0 else ""

    return time_readout[:-2]


def fortune(user) -> str:
    """Returns a random fortune, or time until next usage is available."""

    conn = _soup_sql.connect()

    # don't report db errors to user - better to let the cooldown portion fail and still give them their fortune redeem

    if not user.id in _soup_sql.query(conn, "SELECT uid FROM Users WHERE gid=?;", (user.guild.id,)).values:
        _soup_sql.add_member(conn, user.id, user.guild.id)

    user_ids = _soup_sql.query(conn, "SELECT uid FROM UserTimers WHERE tid='fortune';").values
    if user.id in user_ids:
        last_usage_time = _soup_sql.query(conn, "SELECT start_time FROM UserTimers WHERE uid=?;", (user.id,)).values[0]
    else:
        _soup_sql.query(conn, "INSERT INTO UserTimers (tid, uid) VALUES ('fortune', ?);", (user.id,))
        last_usage_time = 0

    time_since_last_use = _time.time() - last_usage_time
    if time_since_last_use < 72000:
        conn.close()
        return f"{_duration_to_string(72000 - time_since_last_use)} until next fortune redeem."

    _soup_sql.query(conn, "UPDATE UserTimers SET start_time=? WHERE tid='fortune' AND uid=?;", (int(_time.time()), user.id))

    conn.commit()
    conn.close()
    return _choice(_FORTUNES)
