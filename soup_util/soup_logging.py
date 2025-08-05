from os import path as _path
from os import mkdir as _mkdir
from os import listdir as _listdir
from time import localtime as _localtime
import logging as _logging


_directory_name = "logs"


def _make_filename():
    t = _localtime()
    return f"{t.tm_year:04}-{t.tm_mon:02}-{t.tm_mday:02}_{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}_{t.tm_zone}"

if _directory_name not in filter(_path.isdir, _listdir()):
    _mkdir(_directory_name)


_console_handler = _logging.StreamHandler()
_console_handler.setLevel(level=_logging.INFO)

_file_handler = _logging.FileHandler(f"{_directory_name}/{_make_filename()}.log", mode="a", encoding="utf-8")
_file_handler.setLevel(level=_logging.INFO)

_logging.basicConfig(
    level=_logging.NOTSET,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    handlers=[_console_handler, _file_handler]
)

logger = _logging.getLogger(__name__)
