import time as _time
import logging as _logging
import os as _os


_directory_name = "logs"

def _make_filename():
    t = _time.localtime()
    return f"{t.tm_year:04}-{t.tm_mon:02}-{t.tm_mday:02}_{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}_{t.tm_zone}"


if _directory_name not in filter(_os.path.isdir, _os.listdir()):
    _os.mkdir(_directory_name)


_console_handler = _logging.StreamHandler()
_file_handler = _logging.FileHandler(f"{_directory_name}/{_make_filename()}.log", mode="a", encoding="utf-8")

_console_handler.setLevel(level=_logging.INFO)
_file_handler.setLevel(level=_logging.INFO)

_logging.basicConfig(
    level=_logging.NOTSET,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    handlers=[_console_handler, _file_handler]
)

_logger = _logging.getLogger(__name__)


def get_logger():
    return _logger
