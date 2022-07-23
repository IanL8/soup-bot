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
        self.playing = False

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
        playlists[guild].playing = False
        return

    song = playlists[guild].queue.pop(0)
    asyncio.run(play_next_helper(song, loop, guild, channel, vc))

async def play_next_helper(song, loop, guild, channel, vc):
    await asyncio.sleep(1)
    if loop.is_closed():
        return
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
        await asyncio.sleep(5)
        if stopThread:
            return
        if downloadQueue:
            songQueue, loop, guild, channel = downloadQueue.pop(0)
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                while songQueue:
                    if not playlists[guild].playing:
                        playlists[guild].queue = list()
                        break
                    url = songQueue.pop(0)
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

    playlists[context.guild].queue = list()
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

    # create a playlist for context.guild if one does not exist already
    if not playlists.get(context.guild):
        playlists[context.guild] = Playlist()

    playlists[context.guild].playing = True

    # if yt link is a playlist
    if "https://www.youtube.com/playlist?list=PL" in url:
        queue = list(YTPlaylist(url).video_urls)
        if not playlists[context.guild].playing:
            url = queue.pop(0)
            downloadQueue.append((queue, context.bot.loop, context.guild, context.channel))
        else:
            downloadQueue.append((queue, context.bot.loop, context.guild, context.channel))
            return

    # if playing
    if playlists[context.guild].playing:
        downloadQueue.append(([url,], context.bot.loop, context.guild, context.channel))
        return

    vc = context.guild.voice_client # can't use shortcut

    # play song
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            song = Song(info["url"], info["title"])
        except yt_dlp.DownloadError as derr:
            util.soup_log("[ERROR] {}".format(derr.args))
            playlists[context.guild].playing = False
            return await context.channel.send("invalid link")

        try:
            source = await discord.FFmpegOpusAudio.from_probe(song.url, executable=FFMPEG_EXE, **FFMPEG_OPTIONS)
            await context.channel.send(f"now playing...\n```{song.title}```")
            vc.play(source, after=(lambda err: play_next(context.bot.loop, context.guild, context.channel, vc)))
        except discord.errors.ClientException:
            playlists[context.guild].playing = False
            playlists[context.guild].queue.append(song)


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

    queue = await context.channel.send(msg)

    # await queue.add_reaction("◀️")
    # await queue.add_reaction("▶️")
    #
    # def check_back_arrow(emoji, user):
    #     return emoji == "◀️"
    # def check_forward_arrow(emoji, user):
    #     return emoji == "▶️"
    #
    # # async with timeout(20):
    #     # while True:
    #     #     await asyncio.sleep(.25)
    #
    # # reaction, user = await context.bot.wait_for("reaction_add", msg=queue , check=check_back_arrow)
    # reaction =
    # print(reaction)


# clear queue
@commandHandler.command("clear_queue", "clears out the video queue")
async def clear_queue(context):
    if not playlists.get(context.guild) or len(playlists[context.guild].queue) == 0:
        return await context.channel.send("there is no queue")

    playlists[context.guild].queue = list()

    context.voice_client.stop()
