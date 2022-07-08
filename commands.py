#
# imports
import random
import time
import discord

#
# project imports
from command_handler import CommandHandler
import database_handler as db
import soupbot_utilities as util
import youtube_dl
import os
from dotenv import load_dotenv


#
# globals
commandHandler = CommandHandler()
load_dotenv("values.env")
FFMPEG_EXE = os.getenv("FFMPEG_EXE")

#
# basic cmds

#
# hello
@commandHandler.command("hello")
async def hello(context):
    await  context.channel.send("hi {}".format(context.author.display_name))


# help
@commandHandler.command("help")
async def cmd_help(context):
    msg = "Commands: {}".format(util.list_to_string(commandHandler.list_commands(), ", "))
    await context.channel.send(msg)


# true
@commandHandler.command("true")
async def true_lulw(context):
    msg = ("TRUE" if random.random() > .49 else "NOT FALSE") + " <:LULW:801145828923408453>"
    await context.channel.send(msg)


# roll <#>
@commandHandler.command("roll")
async def roll(context):
    k = 100
    if len(context.args) > 0 and context.args[0].isdigit() and int(context.args[0]) != 0:
        k = int(context.args[0])
    await context.channel.send(str(int(random.random() * k) + 1))


# word
@commandHandler.command("word")
async def word(context):
    await context.channel.send(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])


# phrase <#>
@commandHandler.command("phrase")
async def phrase(context):
    k = 2
    if len(context.args) > 0 and context.args[0].isdigit() and int(context.args[0]) != 0:
        k = int(context.args[0])
    temp = []
    for i in range(k):
        temp.append(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])
    await context.channel.send(util.list_to_string(temp, " "))


# 8ball
@commandHandler.command("8ball")
async def magic_8Ball(context):
    if context.author.id == 295323286244687872:
        return await context.channel.send(util.MAGIC_8BALL_LIST[int(random.random() * 10)])
    await context.channel.send(random.choice(util.MAGIC_8BALL_LIST))


# lookup <name>
@commandHandler.command("lookup")
async def lookup(context):
    if len(context.args) == 0:
        msg = "No name specified."
    else:
        msg = "https://na.op.gg/summoner/userName=" + util.list_to_string(context.args, "")

    await context.channel.send(msg)


# which <options>
@commandHandler.command("which")
async def which(context):
    tempList = [s.strip() for s in util.list_to_string(context.args).split(",")]
    while "" in tempList:
        tempList.remove("")
    if len(tempList) == 0:
        msg =  "No options specified."
    else:
        msg = tempList[int(random.random() * len(tempList))]

    await context.channel.send(msg)


# git
@commandHandler.command("git")
async def git(context):
    await context.channel.send("https://github.com/IanL8/soup-bot")


# avatar
@commandHandler.command("avatar")
async def get_avatar(context):
    name = util.list_to_string(context.args, " ")
    i = None

    for member in context.guild.members:
        if str(member.nick).lower() == name.lower() or str(member.name).lower() == name.lower():
            i = member.id

    if i:
        msg = str(context.guild.get_member(i).avatar_url)
    else:
        msg = "invalid nickname"

    await context.channel.send(msg)

#
# stopwatch

stopwatches = dict()
class Stopwatch:
    def __init__(self, uid, startTime):
        self.uid = uid
        self.startTime = startTime


# start stopwatch
@commandHandler.command("start")
async def start_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no name specified")

    name = util.list_to_string(context.args, " ")
    if name in stopwatches.keys():
        msg = "the name *{}* is already in use".format(name)
    else:
        stopwatches[name] = Stopwatch(context.author.id, time.time())
        msg = "stopwatch *{}* started".format(name)

    await context.channel.send(msg)


# check stopwatch
@commandHandler.command("check")
async def check_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no stopwatch specified")

    name = util.list_to_string(context.args, " ")
    if name not in stopwatches.keys():
        msg = "no stopwatch named *{}*".format(name)
    else:
        msg = util.time_to_string(time.time() - stopwatches[name].startTime)

    await context.channel.send(msg)


# stop stopwatch
@commandHandler.command("stop")
async def stop_stopwatch(context):
    if len(context.args) == 0:
        return await context.channel.send("no stopwatch specified")

    name = util.list_to_string(context.args, " ")
    if name not in stopwatches.keys():
        msg = "no stopwatch named *{}*".format(name)
    elif stopwatches[name].uid != context.author.id:
        msg = "this is not your stopwatch"
    else:
        current = time.time() - stopwatches[name].startTime
        stopwatches.pop(name)
        msg = "*{}* stopped at {}".format(name, util.time_to_string(current))

    await context.channel.send(msg)


# get stopwatches
@commandHandler.command("stopwatches")
async def get_stopwatches(context):
    if len(stopwatches) == 0:
        msg = "no stopwatches"
    else:
        msg = util.list_to_string(stopwatches.keys(), ", ")

    await context.channel.send(msg)

#
# music
queue = list()


# join vc
@commandHandler.command("join")
async def join(context):

    if not context.author.voice:
        return await context.channel.send("user is not in a voice channel")
    elif context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is already in a voice channel")

    channel = context.author.voice.channel
    await channel.connect()


# leave vc
@commandHandler.command("leave")
async def leave(context):

    if not context.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    await context.voice_client.disconnect()


# play audio from a yt vid
#credit: https://www.youtube.com/watch?v=jHZlvRr9KxM
@commandHandler.command("play")
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

        url2 = info["formats"][0]["url"]
        source = await discord.FFmpegOpusAudio.from_probe(url2, executable=FFMPEG_EXE, **FFMPEG_OPTIONS)

        vc.play(source)


# pause vid
@commandHandler.command("pause")
async def pause(context):
    if not context.guild.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if not context.guild.voice_client.is_playing():
        return await context.channel.send("there is no song playing")

    context.voice_client.pause()


# resume vid
@commandHandler.command("resume")
async def resume(context):
    if not context.guild.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    if context.guild.voice_client.is_playing():
        return await context.channel.send("the song is already playing")

    context.voice_client.resume()

# skip vid
@commandHandler.command("skip")
async def skip(context):
    if not context.guild.voice_client in context.bot.voice_clients:
        return await context.channel.send("bot is not in a voice channel")

    context.voice_client.stop()


#
# database cmds

# fortune
@commandHandler.command("fortune")
async def fortune(context):
    uid = context.author.id

    await context.channel.send(db.get_fortune(uid))


# add movie
@commandHandler.command("add")
async def add_movie(context):
    gid = context.guild.id

    if len(context.args) == 0:
        return await context.channel.send("no movie given")

    t = util.list_to_string(context.args)
    if not db.add_movie(gid, t):
        msg = "error"
    else:
        msg = "done"

    await context.channel.send(msg)


# remove movie
@commandHandler.command("remove")
async def remove_movie(context):
    gid = context.guild.id

    if len(context.args) == 0:
        return await context.channel.send("no movie given")

    t = util.list_to_string(context.args)
    if not db.remove_movie(gid, t):
        msg = "error"
    else:
        msg = "done"

    await context.channel.send(msg)

# list out the movies
@commandHandler.command("movies")
async def movie_list(context):
    gid = context.guild.id

    li = db.get_movie_list(gid)
    temp = "```\n"
    for i in li:
        temp += i[0] + "\n"
    temp += "\n```"
    await context.channel.send(temp)

#
# admin commands

# change prefix
@commandHandler.command("changeprefix")
async def set_flag(context):
    if len(context.args) == 0 or len(context.args[0]) < 0 or len(context.args[0]) > 2:
        return await context.channel.send("bad prefix")

    uid = context.author.id
    gid = context.guild.id

    newFlag = context.args[0]
    await context.channel.send(db.set_flag(uid, gid, newFlag))

#
# get commandHandler object
def get_command_handler():
    return commandHandler
