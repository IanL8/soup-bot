from os import getenv
from dotenv import load_dotenv
import json


def _read_file_to_list(file_name):
    with open(file_name) as file:
        return [x.strip() for x in file.read().split("\n") if len(x.strip()) > 0]


def _read_json_file_to_dict(file_name):
    with open(file_name) as file:
        return json.load(file)


# env
load_dotenv("resources/values.env")
TOKEN = getenv("DISCORD_TOKEN")
FFMPEG_EXE = getenv("FFMPEG_EXE")
SPOTIPY_CLIENT_SECRET = getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_CLIENT_ID = getenv("SPOTIPY_CLIENT_ID")
AZURE_TRANSLATOR_SECRET_KEY = getenv("AZURE_TRANSLATOR_KEY")
AZURE_TRANSLATOR_REGION = getenv("AZURE_TRANSLATOR_REGION")
DEEPL_API_KEY = getenv("DEEPL_API_KEY")


WORD_LIST = _read_file_to_list("resources/word_list.txt")
FORTUNES = _read_file_to_list("resources/fortunes.txt")

AZURE_TRANSLATION_KEY = _read_json_file_to_dict("resources/azure_translation_key.json")
DEEPL_TRANSLATION_KEY = _read_json_file_to_dict("resources/deepl_translation_key.json")

YDL_OPTIONS = {
    'quiet': True,
    'usenetrc': True,
    'cookiefile': './resources/cookies.txt',
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

MAGIC_8BALL_LIST = [
    "It is certain.",
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
    "Very doubtful."
]
