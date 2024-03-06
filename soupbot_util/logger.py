import time


_DATE_STRING = "{month:02}/{day:02}: {hour:02}:{minute:02}:{sec:02}"


def _get_date():
    t = time.localtime()
    return _DATE_STRING.format(month=t[1], day=t[2], hour=t[3], minute=t[4], sec=t[5])


def soup_log(text:str, category_name:str=""):
    """Prints a message with a timestamp. Can optionally provide a 3 letter name to describe the category of the thing
    being logged"""

    category = f"[{category_name}] ".upper() if len(category_name) == 3 else ""
    print(f"{_get_date()} : {category}{text}")