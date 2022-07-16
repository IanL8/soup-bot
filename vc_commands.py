#
# imports
import discord
import youtube_dl
import os
from dotenv import load_dotenv

#
# project imports
from command_handler import commandHandler
import soupbot_utilities as util

#
# globals
load_dotenv("values.env")
FFMPEG_EXE = os.getenv("FFMPEG_EXE")

#
# playlist
playlists = dict()
class Playlist:
    def __init__(self):
        self.playing = False
        self.queue = list()


# join vc
@commandHandler.command("join", "join vc")
async def join(context):

    if not context.author.voice:
        return await context.channel.send("user is not in a voice channel")
    elif context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is already in a voice channel")

    channel = context.author.voice.channel
    await channel.connect()


# leave vc
@commandHandler.command("leave", "leave vc")
async def leave(context):

    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    await context.voice_client.disconnect()


# play audio from a yt vid
#credit: https://www.youtube.com/watch?v=jHZlvRr9KxM
@commandHandler.command("play", "play a given youtube video (link) in vc")
async def play(context):
    if not context.guild.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if context.guild.voice_client.is_playing():
        await context.channel.send("bot is currently playing another song")
        return await context.channel.send("skip this song in order to play another")

    context.voice_client.stop()

    url = util.list_to_string(context.args, "")
    FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
    YDL_OPTIONS = {  # taken from https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    }
    vc = context.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except youtube_dl.DownloadError as e1:
            util.soup_log("[ERROR] {}".format(str(e1.args)))
            return await context.channel.send("invalid link")

        if info["_type"] == "playlist":
            for e in info["entries"]:
                url2 = e["formats"][0]["url"]
                source = await discord.FFmpegOpusAudio.from_probe(url2, executable=FFMPEG_EXE, **FFMPEG_OPTIONS)
                vc.play(source)
        else:
            url2 = info["formats"][0]["url"]
            source = await discord.FFmpegOpusAudio.from_probe(url2, executable=FFMPEG_EXE, **FFMPEG_OPTIONS)

        vc.play(source)


# pause vid
@commandHandler.command("pause", "pause the current video")
async def pause(context):
    if not context.guild.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if not context.guild.voice_client.is_playing():
        return await context.channel.send("there is no song playing")

    context.voice_client.pause()


# resume vid
@commandHandler.command("resume", "resume the current video")
async def resume(context):
    if not context.guild.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if context.guild.voice_client.is_playing():
        return await context.channel.send("the song is already playing")

    context.voice_client.resume()

# skip vid
@commandHandler.command("skip", "skip the current video")
async def skip(context):
    if not context.guild.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    context.voice_client.stop()

