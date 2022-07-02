#
# imports
import random
import time

#
# project imports
from command_handler import CommandHandler
import database_handler as db
import soupbot_utilities as util

#
# globals
commandHandler = CommandHandler()

#
# basic cmds

# help
@commandHandler.command("help")
async def cmd_help(context):
    msg = "Commands: {s}".format(s=util.list_to_string(commandHandler.list_commands(), ", "))
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
        await context.channel.send(util.MAGIC_8BALL_LIST[int(random.random() * 10)])
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
        msg = "no name specified"

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
        return "no stopwatch specified"

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
        return "no stopwatch specified"

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

    # voice_client = context.guild.voice_client

    if not context.author.voice:
        return "user not in voice"

    channel = context.author.voice.channel
    await channel.connect()

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
        await context.channel.send("no movie given")

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
        await context.channel.send("no movie given")

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
        await context.channel.send("bad prefix")

    uid = context.author.id
    gid = context.guild.id

    newFlag = context.args[0]
    await context.channel.send(db.set_flag(uid, gid, newFlag))


#
# get commandHandler object
def get_command_handler():
    return commandHandler
