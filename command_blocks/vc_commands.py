import discord
import asyncio
from async_timeout import timeout
import threading
import yt_dlp
from pytube import Playlist as YTPlaylist
from math import ceil

from command_management import Commands, CommandBlock
import soupbot_utilities as util

#
# classes

class Song:
    def __init__(self, url, title):
        self.url = url
        self.title = title


class Playlist:
    def __init__(self):
        self.queue: [Song] = list()
        self.playing = False


playlists = dict() # guild -> playlist

#
# helper functions

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
    source = await discord.FFmpegOpusAudio.from_probe(
        song.url, method="fallback", executable=util.FFMPEG_EXE, **util.FFMPEG_OPTIONS)
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
            with yt_dlp.YoutubeDL(util.YDL_OPTIONS) as ydl:
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

#
# bot commands

class Block(CommandBlock):

    name = "music commands"
    cmds = Commands()

    def close(self):
        global stopThread
        stopThread = True

    @cmds.command("join", "join vc")
    async def join(self, context):

        if not context.author.voice:
            return await context.send_message("user is not in a voice channel")
        elif context.voice_client in context.bot.voice_clients: # look at later
            return await context.send_message("bot is already in a voice channel")

        await context.author.voice.channel.connect()
        await context.confirm()

    @cmds.command("leave", "leave vc")
    async def leave(self, context):

        if not context.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        if playlists.get(context.guild):
            playlists.get(context.guild).queue = list()
        await context.voice_client.disconnect(force=False)
        await context.confirm()

    #ref from: https://www.youtube.com/watch?v=jHZlvRr9KxM
    @cmds.command("play", "play a given youtube video (link) in vc", enable_input=True)
    async def play(self, context):
        # if not a youtube link
        url = util.list_to_string(context.args, "")
        if not ("https://www.youtube.com/" in url or "https://youtu.be/" in url):
            return await context.send_message("not a youtube link")

        # if bot not in voice
        if not context.guild.voice_client in context.bot.voice_clients:
            # if user is in voice
            if context.author.voice:
                await context.author.voice.channel.connect()
            else:
                return await context.send_message("user is not in a voice channel", "vc")

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
                return await context.send_message("added to queue")
            else:
                url = queue.pop(0)
        else:
            # if playing
            if playlists[context.guild].playing:
                downloadQueue.append(([url,], context.bot.loop, context.guild, context.channel))
                return await context.send_message("added to queue")

        # play song
        with yt_dlp.YoutubeDL(util.YDL_OPTIONS) as ydl:
            playlists[context.guild].playing = True
            vc = context.guild.voice_client # can't use shortcut

            # get song
            try:
                info = ydl.extract_info(url, download=False)
                song = Song(info["url"], info["title"])
            except yt_dlp.DownloadError as derr:
                util.soup_log(f"[ERROR] {derr.args}")
                playlists[context.guild].playing = False
                return await context.send_message("error: invalid link")

            # play
            try:
                if queue:
                    downloadQueue.append((queue, context.bot.loop, context.guild, context.channel))
                source = await discord.FFmpegOpusAudio.from_probe(song.url, method="fallback",
                                                                  executable=util.FFMPEG_EXE, **util.FFMPEG_OPTIONS)
                vc.play(source, after=(lambda err: play_next(context.bot.loop, context.guild, context.channel, vc)))
                await context.send_message(f"now playing...\n```{song.title}```")
            except discord.errors.ClientException:
                playlists[context.guild].playing = False
                playlists[context.guild].queue.append(song)

    @cmds.command("pause", "pause the current video")
    async def pause(self, context):
        if not context.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        if not context.voice_client.is_playing():
            return await context.send_message("there is no video playing")

        context.voice_client.pause()
        await context.confirm()

    @cmds.command("resume", "resume the current video")
    async def resume(self, context):
        if not context.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        if context.voice_client.is_playing():
            return await context.send_message("the video is already playing")

        context.voice_client.resume()
        await context.confirm()

    @cmds.command("skip", "skip the current video")
    async def skip(self, context):
        if not context.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        if not context.voice_client.is_playing():
            return await context.send_message("there is no video playing")

        context.voice_client.stop()
        await context.confirm()

    @cmds.command("queue", "get the video queue")
    async def get_queue(self, context):
        if not playlists.get(context.guild) or len(playlists[context.guild].queue) == 0:
            return await context.send_message("there is no queue")

        limit = 20
        queue = [s for s in playlists[context.guild].queue]
        maxPages = ceil(len(queue) / limit)

        def make_queue_msg(q, pos: int):
            temp = f"queue - page ({pos}/{maxPages})```\n"
            for i in q:
                temp += f"{i.title} \n"
            temp += "```"
            return temp

        msg = await context.send_message(make_queue_msg(queue[:limit], 1))

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

    @cmds.command("clear", "clears out the video queue")
    async def clear_queue(self, context):
        if not playlists.get(context.guild) or len(playlists[context.guild].queue) == 0:
            return await context.send_message("there is no queue")

        playlists[context.guild].queue = list()

        context.voice_client.stop()
        await context.confirm()