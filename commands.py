import random
import time

import soupbot_utilities as util
import database_handler as db_handler

#
# helper functions


# find id in cursor.execute() output
def find_user_id(user_id, li):
    for element in li:
        for e in element:
            if user_id == e:
                return True
    return False


def cmd_help(args, author):
    return "Commands {s}".format(s=COMMAND_LIST.keys())


def hello(args, author):
    return "hello {s}".format(s=author.name)


def bye(args, author):
    return "bye {s}".format(s=author.name)


def roll(args, author):
    k = 100
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    return str(int(random.random() * k) + 1)


def word(args="", author=""):
    return util.WORD_LIST[int(random.random() * len(util.WORD_LIST))]


def phrase(args, author):
    k = 2
    if len(args) > 0 and args[0].isdigit() and int(args[0]) != 0:
        k = int(args[0])
    temp = ""
    for i in range(k):
        temp += word() + " "
    return temp


def magic_8Ball(args, author):
    return util.MAGIC_8BALL_LIST[int(random.random() * len(util.MAGIC_8BALL_LIST))]


def lookup(args, author):
    if len(args) == 0:
        return "No name specified."
    return "https://na.op.gg/summoner/userName=" + args[0]


def which(args, author):
    if len(args) == 0:
        return "No options specified."
    tempString = ""
    for a in args:
        tempString += a
    tempList = tempString.split(",")
    return tempList[int(random.random() * len(tempList))]


def fortune(args, author):
    #
    # local vars
    k = 0                       # holds 1 or 0 depending on whether make_query() was a success or a failure
    output = list()             # holds the output of the query in make_query()
    userId = str(author.id)     # holds the user's ID
    lastUsage = 0               # holds the time of the last usage of the cmd

    # check if userId is already in the table
    k, output = db_handler.make_query("SELECT user_id FROM UserTimers")
    if k == 0:
        return "[Error] Bad query"

    # if not, add them to the table
    if not find_user_id(userId, output):
        k, output = db_handler.make_query("INSERT INTO UserTimers (timer_name, user_id) VALUES (%s, %s);",
                                          ("fortune", userId))
        if k == 0:
            return "[Error] Bad query"
    # if they are, fetch the last time fortune was used
    else:
        k, output = db_handler.make_query("SELECT start_time FROM UserTimers WHERE user_id=%s;", (userId,))
        if k == 0:
            return "[Error] Bad query"
        lastUsage = output[0][0]

    # if it has not been 20 hrs, return the time remaining to the next use
    t = time.time() - lastUsage
    if t < 72000:
        return util.time_to_string(72000 - t) + " until next fortune redeem."

    # update the table with the current time and return the fortune
    k, output = db_handler.make_query("UPDATE UserTimers SET start_time=%s WHERE user_id=%s;",
                                      (int(time.time()), userId))
    if k == 0:
        return "[Error] Bad query"
    return util.FORTUNES[int(random.random() * len(util.FORTUNES))]


def git(args, author):
    return "https://github.com/IanL8/soup-bot"


# list of basic cmds
COMMAND_LIST = {"help": cmd_help, "hello": hello, "bye": bye, "roll": roll, "word": word,  "phrase": phrase,
                "8ball": magic_8Ball, "lookup": lookup, "which": which, "fortune": fortune, "git": git}
