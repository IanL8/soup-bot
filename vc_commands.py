#
# imports
import discord
import asyncio
import threading
import yt_dlp
from pytube import Playlist as YTPlaylist
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
USERNAME = os.getenv("YT_USERNAME")
PASSWORD = os.getenv("YT_PASSWORD")

FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}

YDL_OPTIONS = {  # taken from https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
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
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

playlists = dict()

#
# objects

# playlist
class Playlist:
    def __init__(self):
        self.queue = list()

# song
class Song:
    def __init__(self, url, title):
        self.url = url
        self.title = title

#
# helper functions

#play next
def play_next(loop, guild, channel, vc):
    if len(playlists[guild].queue) == 0:
        del playlists[guild]
        return

    song = playlists[guild].queue.pop(0)
    asyncio.run(play_next_helper(song, loop, guild, channel, vc))

async def play_next_helper(song, loop, guild, channel, vc):
    await asyncio.sleep(1)
    source = await discord.FFmpegOpusAudio.from_probe(song.url, executable=FFMPEG_EXE, **FFMPEG_OPTIONS)
    asyncio.run_coroutine_threadsafe(channel.send(f"now playing...\n```{song.title}```"), loop)
    vc.play(source, after=lambda err: play_next(loop, guild, channel, vc))

#
# download queue
# idea: https://stackoverflow.com/a/26270790

downloadQueue = list()

stopThread = False

def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download_queue_processor())
    return

async def download_queue_processor():
    while True:
        await asyncio.sleep(10)
        if stopThread:
            return
        if downloadQueue:
            queue, loop, guild, channel = downloadQueue.pop(0)
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                while queue:
                    url = queue.pop(0)
                    try:
                        info = ydl.extract_info(url, download=False)
                        playlists[guild].queue.append(Song(info["url"], info["title"]))
                    except yt_dlp.DownloadError as derr:
                        util.soup_log("[ERROR] {}".format(derr.args))
                        asyncio.run_coroutine_threadsafe(channel.send(f"error: invalid link on {url}"), loop)

downloadLoop = asyncio.new_event_loop()
t = threading.Thread(target=loop_in_thread, args=(downloadLoop,))
t.start()

def close():
    global stopThread
    stopThread = True


#
# bot commands

# join vc
@commandHandler.command("join", "join vc")
async def join(context):

    if not context.author.voice:
        return await context.channel.send("user is not in a voice channel")
    elif context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is already in a voice channel")

    await context.author.voice.channel.connect()


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
    # if not a youtube link
    url = util.list_to_string(context.args, "")
    if not "https://www.youtube.com/" in url:
        return await context.channel.send("not a youtube link")

    # if bot not in voice
    if not context.guild.voice_client in context.bot.voice_clients:

        # if user is in voice
        if context.author.voice:
            await context.author.voice.channel.connect()
        else:
            return await context.channel.send("user is not in a voice channel")

    vc = context.guild.voice_client # can't use shortcut

    # create a playlist for context.guild if one does not exist already
    if not playlists.get(context.guild):
        playlists[context.guild] = Playlist()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:

        if "https://www.youtube.com/playlist?list=PL" in url:
            queue = list()
            for u in YTPlaylist(url).video_urls:
                queue.append(u)
            url = queue.pop(0)
            downloadQueue.append((queue, context.bot.loop, context.guild, context.channel))

        try:
            info = ydl.extract_info(url, download=False)
            playlists[context.guild].queue.append(Song(info["url"], info["title"]))
        except yt_dlp.DownloadError as derr:
            util.soup_log("[ERROR] {}".format(derr.args))
            return await context.channel.send("invalid link")

        if not vc.is_playing():

            song = playlists[context.guild].queue.pop(0)

            try:
                source = await discord.FFmpegOpusAudio.from_probe(song.url, executable=FFMPEG_EXE, **FFMPEG_OPTIONS)
                await context.channel.send(f"now playing...\n```{song.title}```")
                vc.play(source, after=(lambda err: play_next(context.bot.loop, context.guild, context.channel, vc)))
            except discord.errors.ClientException:
                playlists[context.guild].queue.insert(0, song)

# pause vid
@commandHandler.command("pause", "pause the current video")
async def pause(context):
    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if not context.voice_client.is_playing():
        return await context.channel.send("there is no video playing")

    context.voice_client.pause()


# resume vid
@commandHandler.command("resume", "resume the current video")
async def resume(context):
    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if context.voice_client.is_playing():
        return await context.channel.send("the video is already playing")

    context.voice_client.resume()


# skip vid
@commandHandler.command("skip", "skip the current video")
async def skip(context):
    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if not context.voice_client.is_playing():
        return await context.channel.send("there is no video playing")

    context.voice_client.stop()


# queue
@commandHandler.command("queue", "get the video queue")
async def get_queue(context):
    if not playlists.get(context.guild) or len(playlists[context.guild].queue) == 0:
        return await context.channel.send("there is no queue")

    limit = 20 if len(playlists[context.guild].queue) > 20 else len(playlists[context.guild].queue)
    msg = f"the next {limit} videos...```\n"
    for i in range(0, limit):
        msg += f"{playlists[context.guild].queue[i].title} \n"
    msg += "```"

    await context.channel.send(msg)


# clear queue
@commandHandler.command("clear_queue", "clears out the video queue")
async def clear_queue(context):
    if not playlists.get(context.guild) or len(playlists[context.guild].queue) == 0:
        return await context.channel.send("there is no queue")

    playlists[context.guild].queue = list()

    context.voice_client.stop()
