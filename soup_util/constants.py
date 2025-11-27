from os import getenv as _getenv
from dotenv import load_dotenv as _load_dotenv
import json as _json


def _read_file_to_list(file_name):
    with open(file_name) as file:
        return [x.strip() for x in file.read().split("\n") if len(x.strip()) > 0]

def _read_json_file_to_dict(file_name):
    with open(file_name) as file:
        return _json.load(file)


# env file
_load_dotenv("resources/.env")

TOKEN = _getenv("DISCORD_TOKEN")

FFMPEG_EXE = _getenv("FFMPEG_EXE")

SPOTIPY_CLIENT_SECRET = _getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_CLIENT_ID = _getenv("SPOTIPY_CLIENT_ID")

AZURE_TRANSLATOR_SECRET_KEY = _getenv("AZURE_TRANSLATOR_KEY")
AZURE_TRANSLATOR_REGION = _getenv("AZURE_TRANSLATOR_REGION")

DEEPL_API_KEY = _getenv("DEEPL_API_KEY")

STEAM_API_KEY = _getenv("STEAM_API_KEY")

YOUTUBE_API_KEY = _getenv("YOUTUBE_API_KEY")

EMBED_TRANSPARENT_IMAGE_URL = _getenv("EMBED_TRANSPARENT_IMAGE_URL")

NODE1_HOST = _getenv("NODE1_HOST")
NODE1_PORT = _getenv("NODE1_PORT")
NODE1_PASSWORD = _getenv("NODE1_PASSWORD")
NODE1_REGION = _getenv("NODE1_REGION")
NODE1_NAME = _getenv("NODE1_NAME")

NODE2_HOST = _getenv("NODE2_HOST")
NODE2_PORT = _getenv("NODE2_PORT")
NODE2_PASSWORD = _getenv("NODE2_PASSWORD")
NODE2_REGION = _getenv("NODE2_REGION")
NODE2_NAME = _getenv("NODE2_NAME")

# txt files
WORD_LIST = _read_file_to_list("resources/word_list.txt")
WORDLE_LIST = _read_file_to_list("resources/wordle_list.txt")
FORTUNES = _read_file_to_list("resources/fortunes.txt")

# json files
AZURE_TRANSLATION_KEY = _read_json_file_to_dict("resources/azure_translation_key.json")
DEEPL_TRANSLATION_KEY = _read_json_file_to_dict("resources/deepl_translation_key.json")

# literals
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
