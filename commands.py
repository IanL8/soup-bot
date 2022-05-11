#
# imports
import random
import time

#
# project imports
from dec_cmd_handler import CmdHandler
import database_handler as db
import soupbot_utilities as util

#
# globals
cmdHandler = CmdHandler()

#
# basic cmds


# help
@cmdHandler.name("help")
def cmd_help(context, args):
    return "Commands: {s}".format(s=util.list_to_string(cmdHandler.list_all_cmds(), ", "))


# true
@cmdHandler.name("true")
def true_lulw(context, args):
    return ("TRUE" if random.random() > .49 else "NOT FALSE") + " <:LULW:801145828923408453>"


# roll <#>
@cmdHandler.name("roll")
def roll(context, args):
    k = 100
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    return str(int(random.random() * k) + 1)


# word
@cmdHandler.name("word")
def word(context=None, args=""):
    return util.WORD_LIST[int(random.random() * len(util.WORD_LIST))]


# phrase <#>
@cmdHandler.name("phrase")
def phrase(context, args):
    k = 2
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    temp = ""
    for i in range(k):
        temp += word() + " "
    return temp


# 8ball
@cmdHandler.name("8ball")
def magic_8Ball(context, args):
    if context.author.id == 295323286244687872:
        return util.MAGIC_8BALL_LIST[int(random.random() * 10)]
    return util.MAGIC_8BALL_LIST[int(random.random() * len(util.MAGIC_8BALL_LIST))]


# lookup <name>
@cmdHandler.name("lookup")
def lookup(context, args):
    if len(args) == 0:
        return "No name specified."
    return "https://na.op.gg/summoner/userName=" + args[0]


# which <options>
@cmdHandler.name("which")
def which(context, args):
    tempList = [s.strip() for s in util.list_to_string(args).split(",")]
    while "" in tempList:
        tempList.remove("")
    if len(tempList) == 0:
        return "No options specified."
    return tempList[int(random.random() * len(tempList))]


@cmdHandler.name("git")
def git(context, args):
    return "https://github.com/IanL8/soup-bot"


#
# database cmds

# fortune
@cmdHandler.name("fortune")
def fortune(context, args):
    uid = context.author.id
    gid = context.guild.id
    lastUsage = 0

    # check if userId is already in the table
    k = db.request("SELECT tid FROM UserTimers WHERE uid=?;", (uid,))
    if k == -1:
        return "[Error] Bad query"

    # if not, add them to the table
    if not util.find_in_list("fortune", k):
        k = db.request("INSERT INTO UserTimers (tid, uid) VALUES (?, ?);", ("fortune", uid))
        if k == -1:
            return "[Error] Bad query"
    # if they are, fetch the last time fortune was used
    else:
        k = db.request("SELECT start_time FROM UserTimers WHERE uid=?;", (uid,))
        if k == -1:
            return "[Error] Bad query"
        lastUsage = k[0][0]

    # if it has not been 20 hrs, return the time remaining to the next use
    t = time.time() - lastUsage
    if t < 72000:
        return util.time_remaining_to_string(72000 - t) + " until next fortune redeem."

    # update the table with the current time and return the fortune
    k = db.request("UPDATE UserTimers SET start_time=? WHERE uid=?;", (int(time.time()), uid))
    if k == -1:
        return "[Error] Bad query"
    return util.FORTUNES[int(random.random() * len(util.FORTUNES))]


# add movie
@cmdHandler.name("addmovie")
def add_movie(context, args):
    gid = context.guild.id

    if len(args) == 0:
        return "No movie given"
    t = util.list_to_string(args)
    if not db.add_movie(gid, t):
        return "Bad query"
    return "done"


# remove movie
@cmdHandler.name("removemovie")
def remove_movie(context, args):
    gid = context.guild.id

    if len(args) == 0:
        return "No movie given"
    t = util.list_to_string(args)
    if not db.remove_movie(gid, t):
        return "Bad query"
    return "done"


# list out the movies
@cmdHandler.name("listmovies")
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
@cmdHandler.name("changeprefix")
def change_prefix(context, args):
    if len(args) == 0 or len(args[0]) < 0 or len(args[0]) > 2:
        return "Bad prefix"

    uid = context.author.id
    gid = context.guild.id

    newPrefix = args[0]

    k = db.request("SELECT gid FROM Guilds WHERE owner_id=?;", (uid,))
    if k == -1:
        return "[Error] Bad query"

    if util.find_in_list(gid, k):
        k = db.request("UPDATE Guilds SET flag=? WHERE gid=?;", (newPrefix, gid))
        if k == -1:
            return "[Error] Bad query"
        return "Change successful"

    return "You do not have the permissions for this command"


#
# get cmdHandler object
def get_cmd_handler():
    return cmdHandler

