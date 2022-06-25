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
def cmd_help(context, args):
    return "Commands: {s}".format(s=util.list_to_string(commandHandler.list_commands(), ", "))


# true
@commandHandler.command("true")
def true_lulw(context, args):
    return ("TRUE" if random.random() > .49 else "NOT FALSE") + " <:LULW:801145828923408453>"


# roll <#>
@commandHandler.command("roll")
def roll(context, args):
    k = 100
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    return str(int(random.random() * k) + 1)


# word
@commandHandler.command("word")
def word(context, args):
    return util.WORD_LIST[int(random.random() * len(util.WORD_LIST))]


# phrase <#>
@commandHandler.command("phrase")
def phrase(context, args):
    k = 2
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    temp = []
    for i in range(k):
        temp.append(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])
    return util.list_to_string(temp, " ")


# 8ball
@commandHandler.command("8ball")
def magic_8Ball(context, args):
    if context.author.id == 295323286244687872:
        return util.MAGIC_8BALL_LIST[int(random.random() * 10)]
    return util.MAGIC_8BALL_LIST[int(random.random() * len(util.MAGIC_8BALL_LIST))]


# lookup <name>
@commandHandler.command("lookup")
def lookup(context, args):
    if len(args) == 0:
        return "No name specified."
    return "https://na.op.gg/summoner/userName=" + util.list_to_string(args, "")


# which <options>
@commandHandler.command("which")
def which(context, args):
    tempList = [s.strip() for s in util.list_to_string(args).split(",")]
    while "" in tempList:
        tempList.remove("")
    if len(tempList) == 0:
        return "No options specified."
    return tempList[int(random.random() * len(tempList))]


# git
@commandHandler.command("git")
def git(context, args):
    return "https://github.com/IanL8/soup-bot"


# avatar
@commandHandler.command("avatar")
def get_avatar(context, args):
    name = util.list_to_string(args, " ")
    i = None

    for member in context.guild.members:
        if str(member.nick).lower() == name.lower() or str(member.name).lower() == name.lower():
            i = member.id

    if i:
        return str(context.guild.get_member(i).avatar_url)
    else:
        return "invalid nickname"

#
# stopwatch

stopwatches = dict()
class Stopwatch:
    def __init__(self, uid, startTime):
        self.uid = uid
        self.startTime = startTime


# start stopwatch
@commandHandler.command("start")
def start_stopwatch(context, args):
    if len(args) == 0:
        return "no name specified"

    name = util.list_to_string(args, " ")
    if name in stopwatches.keys():
        return "the name *{}* is already in use".format(name)

    stopwatches[name] = Stopwatch(context.author.id, time.time())
    return "stopwatch *{}* started".format(name)


# check stopwatch
@commandHandler.command("check")
def check_stopwatch(context, args):
    if len(args) == 0:
        return "no stopwatch specified"

    name = util.list_to_string(args, " ")
    if name not in stopwatches.keys():
        return "no stopwatch named *{}*".format(name)

    return util.time_to_string(time.time() - stopwatches[name].startTime)


# stop stopwatch
@commandHandler.command("stop")
def stop_stopwatch(context, args):
    if len(args) == 0:
        return "no stopwatch specified"

    name = util.list_to_string(args, " ")
    if name not in stopwatches.keys():
        return "no stopwatch named *{}*".format(name)

    if stopwatches[name].uid != context.author.id:
        return "this is not your stopwatch"

    current = time.time() - stopwatches[name].startTime
    stopwatches.pop(name)
    return "*{}* stopped at {}".format(name, util.time_to_string(current))


# get stopwatches
@commandHandler.command("stopwatches")
def get_stopwatches(context, args):
    if len(stopwatches) == 0:
        return "no stopwatches"

    return util.list_to_string(stopwatches.keys(), ", ")

#
# database cmds

# fortune
@commandHandler.command("fortune")
def fortune(context, args):
    uid = context.author.id

    return db.get_fortune(uid)


# add movie
@commandHandler.command("add")
def add_movie(context, args):
    gid = context.guild.id

    if len(args) == 0:
        return "No movie given"
    t = util.list_to_string(args)
    if not db.add_movie(gid, t):
        return "error"
    return "done"


# remove movie
@commandHandler.command("remove")
def remove_movie(context, args):
    gid = context.guild.id

    if len(args) == 0:
        return "No movie given"
    t = util.list_to_string(args)
    if not db.remove_movie(gid, t):
        return "error"
    return "done"


# list out the movies
@commandHandler.command("movies")
def movie_list(context, args):
    gid = context.guild.id

    li = db.get_movie_list(gid)
    temp = "```\n"
    for i in li:
        temp += i[0] + "\n"
    temp += "\n```"
    return temp

#
# admin commands

# change prefix
@commandHandler.command("changeprefix")
def set_flag(context, args):
    if len(args) == 0 or len(args[0]) < 0 or len(args[0]) > 2:
        return "Bad prefix"

    uid = context.author.id
    gid = context.guild.id

    newFlag = args[0]
    return db.set_flag(uid, gid, newFlag)


#
# get commandHandler object
def get_command_handler():
    return commandHandler
