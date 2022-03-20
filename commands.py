#
# imports
import random
import time

#
# project imports
import soupbot_utilities as util


#
# helper functions


#
# basic cmds

# help
def cmd_help(args):
    return "Commands: {s}".format(s=util.list_to_string(ALL_CMDS, ", "))


# true
def true_lulw(args):
    return ("TRUE" if random.random() > .49 else "NOT FALSE") + " <:LULW:801145828923408453>"


# roll <#>
def roll(args):
    k = 100
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    return str(int(random.random() * k) + 1)


# word
def word(args=""):
    return util.WORD_LIST[int(random.random() * len(util.WORD_LIST))]


# phrase <#>
def phrase(args):
    k = 2
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    temp = ""
    for i in range(k):
        temp += word() + " "
    return temp


# 8ball
def magic_8Ball(args):
    return util.MAGIC_8BALL_LIST[int(random.random() * len(util.MAGIC_8BALL_LIST))]


# lookup <name>
def lookup(args):
    if len(args) == 0:
        return "No name specified."
    return "https://na.op.gg/summoner/userName=" + args[0]


# which <options>
def which(args):
    tempList = [s.strip() for s in util.list_to_string(args).split(",")]
    while "" in tempList:
        tempList.remove("")
    if len(tempList) == 0:
        return "No options specified."
    return tempList[int(random.random() * len(tempList))]


def git(args):
    return "https://github.com/IanL8/soup-bot"


#
# database cmds

# fortune
def fortune(args, dbHandler, uid, gid):
    #
    # local vars
    k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
    output = list()             # holds the output of the query in make_query()
    lastUsage = 0               # holds the time of the last usage of the cmd

    # check if userId is already in the table
    k, output = dbHandler.make_query("SELECT tid FROM UserTimers WHERE uid=%s;", (uid,))
    if k == 0:
        return "[Error] Bad query"

    # if not, add them to the table
    if not util.find_in_list("fortune", output):
        k, output = dbHandler.make_query("INSERT INTO UserTimers (tid, uid) VALUES (%s, %s);",
                                         ("fortune", uid))
        if k == 0:
            return "[Error] Bad query"
    # if they are, fetch the last time fortune was used
    else:
        k, output = dbHandler.make_query("SELECT start_time FROM UserTimers WHERE uid=%s;", (uid,))
        if k == 0:
            return "[Error] Bad query"
        lastUsage = output[0][0]

    # if it has not been 20 hrs, return the time remaining to the next use
    t = time.time() - lastUsage
    if t < 72000:
        return util.time_remaining_to_string(72000 - t) + " until next fortune redeem."

    # update the table with the current time and return the fortune
    k, output = dbHandler.make_query("UPDATE UserTimers SET start_time=%s WHERE uid=%s;",
                                     (int(time.time()), uid))
    if k == 0:
        return "[Error] Bad query"
    return util.FORTUNES[int(random.random() * len(util.FORTUNES))]


# add movie
def add_movie(args, dbHandler, uid, gid):
    if len(args) == 0:
        return "No movie given"
    t = util.list_to_string(args)
    out = dbHandler.add_movie(gid, t)
    if out == 0:
        return "Bad query"
    return "done"


# remove movie
def remove_movie(args, dbHandler, uid, gid):
    if len(args) == 0:
        return "No movie given"
    out = dbHandler.remove_movie(gid, args[0])
    if out == 0:
        return "Bad query"
    return "done"


# list out the movies
def movie_list(args, dbHandler, uid, gid):
    out = dbHandler.get_movie_list(gid)
    if out == 0:
        return "No list"
    temp = "```\n"
    for k in out:
        temp += k[0] + "\n"
    temp += "\n```"
    return temp


#
# admin commands

# change prefix
def change_prefix(args, dbHandler, cmdHandler, uid, gid):
    if len(args) == 0 or len(args[0]) < 0 or len(args[0]) > 2:
        return "Bad prefix"
    #
    # local vars
    k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
    output = list()             # holds the output of the query in make_query()
    newPrefix = args[0]

    k, output = dbHandler.make_query("SELECT gid FROM Guilds WHERE owner_id=%s;", (uid, ))
    if k == 0:
        return "[Error] Bad query"

    if util.find_in_list(gid, output):
        k, output = dbHandler.make_query("UPDATE Guilds SET flag=%s WHERE gid=%s;", (newPrefix, gid))
        if k == 0:
            return "[Error] Bad query"
        cmdHandler.set_flag(newPrefix)
        return "Change successful"

    return "You do not have the permissions for this command"


#
# dictionaries

# dict of basic cmds
BASIC_COMMANDS = {"help": cmd_help, "true": true_lulw, "roll": roll, "word": word,
                  "phrase": phrase, "8ball": magic_8Ball, "lookup": lookup, "which": which, "git": git}

# dict of cmds that require DB access
DB_ACCESS_COMMANDS = {"fortune": fortune, "addMovie": add_movie, "removeMovie": remove_movie, "movieList": movie_list}

# dict of admin cmds
ADMIN_COMMANDS = {"changeprefix": change_prefix}


# list of all cmds
def make_cmd_list():
    temp = list(BASIC_COMMANDS.keys())
    temp += list(DB_ACCESS_COMMANDS.keys())
    temp += list(ADMIN_COMMANDS.keys())
    return temp


ALL_CMDS = make_cmd_list()
