#
# imports
import discord
import asyncio
from async_timeout import timeout
import threading
import yt_dlp
from pytube import Playlist as YTPlaylist
import os
from dotenv import load_dotenv
from math import ceil

#
# project imports
from command_categories import commandHandler
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
                        util.soup_log(f"[ERROR] {derr.args}")
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
@commandHandler.command("join", "join vc", "vc")
async def join(context):

    if not context.author.voice:
        return await context.channel.send("user is not in a voice channel")
    elif context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is already in a voice channel")

    await context.author.voice.channel.connect()
    await context.message.add_reaction("✅")

# leave vc
@commandHandler.command("leave", "leave vc", "vc")
async def leave(context):

    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if playlists.get(context.guild):
        playlists.get(context.guild).queue = list()
    await context.voice_client.disconnect()
    await context.message.add_reaction("✅")


# play audio from a yt vid
#credit: https://www.youtube.com/watch?v=jHZlvRr9KxM
@commandHandler.command("play", "play a given youtube video (link) in vc", "vc")
async def play(context):
    # if not a youtube link
    url = util.list_to_string(context.args, "")
    if not ("https://www.youtube.com/" in url or "https://youtu.be/" in url):
        return await context.channel.send("not a youtube link")

    # if bot not in voice
    if not context.guild.voice_client in context.bot.voice_clients:
        # if user is in voice
        if context.author.voice:
            await context.author.voice.channel.connect()
        else:
            return await context.channel.send("user is not in a voice channel", "vc")

    # create a playlist for context.guild if one does not exist already
    if not playlists.get(context.guild):
        playlists[context.guild] = Playlist()

    # if yt link is a playlist
    queue = None
    if "playlist?list=PL" in url:
        queue = list(YTPlaylist(url).video_urls)
        # if playing
        if playlists[context.guild].playing:
            downloadQueue.append((queue, context.bot.loop, context.guild, context.channel))
            await context.message.add_reaction("✅")
            return
        else:
            url = queue.pop(0)
    else:
        # if playing
        if playlists[context.guild].playing:
            downloadQueue.append(([url,], context.bot.loop, context.guild, context.channel))
            await context.message.add_reaction("✅")
            return

    # play song
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        playlists[context.guild].playing = True
        vc = context.guild.voice_client # can't use shortcut

        try:
            info = ydl.extract_info(url, download=False)
            song = Song(info["url"], info["title"])
        except yt_dlp.DownloadError as derr:
            util.soup_log(f"[ERROR] {derr.args}")
            playlists[context.guild].playing = False
            return await context.channel.send("invalid link")

        try:
            if queue:
                downloadQueue.append((queue, context.bot.loop, context.guild, context.channel))
            source = await discord.FFmpegOpusAudio.from_probe(song.url, executable=FFMPEG_EXE, **FFMPEG_OPTIONS)
            await context.channel.send(f"now playing...\n```{song.title}```")
            vc.play(source, after=(lambda err: play_next(context.bot.loop, context.guild, context.channel, vc)))
            await context.message.add_reaction("✅")
        except discord.errors.ClientException:
            playlists[context.guild].playing = False
            playlists[context.guild].queue.append(song)


# pause vid
@commandHandler.command("pause", "pause the current video", "vc")
async def pause(context):
    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if not context.voice_client.is_playing():
        return await context.channel.send("there is no video playing")

    context.voice_client.pause()
    await context.message.add_reaction("✅")


# resume vid
@commandHandler.command("resume", "resume the current video", "vc")
async def resume(context):
    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if context.voice_client.is_playing():
        return await context.channel.send("the video is already playing")

    context.voice_client.resume()
    await context.message.add_reaction("✅")


# skip vid
@commandHandler.command("skip", "skip the current video", "vc")
async def skip(context):
    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if not context.voice_client.is_playing():
        return await context.channel.send("there is no video playing")

    context.voice_client.stop()
    await context.message.add_reaction("✅")


# queue
@commandHandler.command("queue", "get the video queue", "vc")
async def get_queue(context):
    if not playlists.get(context.guild) or len(playlists[context.guild].queue) == 0:
        return await context.channel.send("there is no queue")

    limit = 20
    queue = [s for s in playlists[context.guild].queue]
    maxPages = ceil(len(queue) / limit)

    def make_queue_msg(q, pos: int):
        temp = f"queue - page ({pos}/{maxPages})```\n"
        for i in q:
            temp += f"{i.title} \n"
        temp += "```"
        return temp

    msg = await context.channel.send(make_queue_msg(queue[:limit], 1))

    if len(queue) < 21:
        return

    await msg.add_reaction("◀️")
    await msg.add_reaction("▶️")

    async with timeout(60):
        x = 0   # floor
        y = limit  # ceiling
        while True:
            try:
                # credit: https://stackoverflow.com/a/70661168
                done, pending = await asyncio.wait([
                    context.bot.loop.create_task(context.bot.wait_for('reaction_remove')),
                    context.bot.loop.create_task(context.bot.wait_for('reaction_add'))
                ], return_when=asyncio.FIRST_COMPLETED)
            except asyncio.exceptions.CancelledError:
                return
            if not done:
                continue
            reaction, user = done.pop().result()
            if user == context.bot.user or reaction.message != msg:
                continue

            if reaction.emoji == "▶️":
                if len(queue) > y:
                    x += limit
                    y += limit if len(queue) > limit else len(queue)
                else: # len(queue) == y:
                    x = 0
                    y = limit
                await msg.edit(content=make_queue_msg(queue[x:y], ceil(y / limit)))
            elif reaction.emoji == "◀️":
                if x != 0:
                    y -= y-x
                    x -= limit
                else: # x == 0
                    y = len(queue)
                    x = y - (limit if (y % limit) == 0 else (y % limit))
                await msg.edit(content=make_queue_msg(queue[x:y], ceil(y / limit)))


# clear queue
@commandHandler.command("clear_queue", "clears out the video queue", "vc")
async def clear_queue(context):
    if not playlists.get(context.guild) or len(playlists[context.guild].queue) == 0:
        return await context.channel.send("there is no queue")

    playlists[context.guild].queue = list()

    context.voice_client.stop()
    await context.message.add_reaction("✅")
