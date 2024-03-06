from os import getenv
from dotenv import load_dotenv


def _read_file_to_list(file_name):
    temp = []
    file = open(file_name)
    line = file.readline()
    while len(line) > 0:
        temp.insert(0, line)
        line = file.readline().strip()
    file.close()
    return temp


# env
load_dotenv("values.env")
TOKEN = getenv("DISCORD_TOKEN")
FFMPEG_EXE = getenv("FFMPEG_EXE")
SPOTIPY_CLIENT_SECRET = getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_CLIENT_ID = getenv("SPOTIPY_CLIENT_ID")


YDL_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'outtmpl': '%(title)s.%(ext)s',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'libopus',
        'preferredquality': '192',
    }],
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


WORD_LIST = _read_file_to_list("rec/word_list.txt")  # list of words from https://www.mit.edu/~ecprice/wordlist.10000


FORTUNES = _read_file_to_list("rec/fort.txt")
