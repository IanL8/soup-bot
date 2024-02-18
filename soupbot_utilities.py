import time
from os import getenv
from dotenv import load_dotenv

#
# functions

_TIME_UNITS = [(86400, "days"), (3600, "hours"), (60, "min"), (1, "sec")]
_DATE_STRING = "{month:02}/{day:02}: {hour:02}:{minute:02}:{sec:02}"

def read_file_to_list(src):
    temp = []
    f = open(src)
    s = f.readline()
    while len(s) > 0:
        temp.insert(0, s)
        s = f.readline().strip()
    f.close()
    return temp

def time_to_string(t):
    """Takes a time t in seconds and returns the time in days, hours, min, sec"""

    s = ""
    for i, j in _TIME_UNITS:
        temp = int(t / i)
        t = t % i
        if temp > 0:
            s += f"{temp} {j}, "

    return s[:-2]


def _get_date():
    t = time.localtime()
    return _DATE_STRING.format(month=t[1], day=t[2], hour=t[3], minute=t[4], sec=t[5])


def soup_log(s):
    """prints a message s with a timestamp"""
    print(f"{_get_date()}: {s}")

#
# constants

# env
load_dotenv("values.env")
TOKEN = getenv("DISCORD_TOKEN")
FFMPEG_EXE = getenv("FFMPEG_EXE")
SPOTIPY_CLIENT_SECRET = getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_CLIENT_ID = getenv("SPOTIPY_CLIENT_ID")

FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}

YDL_OPTIONS = {  # referenced from https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
    'format': 'bestaudio/best',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    # 'default_search': 'auto',
    # 'flat_playlist': True,
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

MAGIC_8BALL_LIST = ["It is certain.",
                    "It is decidedly so.",
                    "Without a doubt.",
                    "Yes – definitely.",
                    "You may rely on it.",
                    "As I see it, yes.",
                    "Most likely.",
                    "Outlook good.",
                    "Yes.",
                    "Signs point to yes.",
                    "Reply hazy, try again.",
                    "Ask again later.",
                    "Better not tell you now.",
                    "Cannot predict now.",
                    "Concentrate and ask again.",
                    "Don't count on it.",
                    "My reply is no.",
                    "My sources say no.",
                    "Outlook not so good.",
                    "Very doubtful."]

WORD_LIST = read_file_to_list("src/word_list.txt")  # list of words from https://www.mit.edu/~ecprice/wordlist.10000

FORTUNES = read_file_to_list("src/fort.txt")
