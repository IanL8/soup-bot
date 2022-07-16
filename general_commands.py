#
# imports
import random

#
# project imports
from command_handler import commandHandler
import database_handler as db
import soupbot_utilities as util

#
# basic cmds

# help
@commandHandler.command("help")
async def cmd_help(context):
    msg = "Commands```\n"
    for k, v in commandHandler.cmdInfo.items():
        msg += k + " " * (20 - len(k)) + v + "\n"
    msg += "```"
    await context.channel.send(msg)


# hello
@commandHandler.command("hello")
async def hello(context):
    await context.channel.send("hi {}".format(context.author.display_name))


# true
@commandHandler.command("true")
async def true_lulw(context):
    msg = ("TRUE" if random.random() > .49 else "NOT FALSE") + " <:LULW:801145828923408453>"
    await context.channel.send(msg)


# roll <#>
@commandHandler.command("roll", "roll a dice with the given amount of sides [default 100]")
async def roll(context):
    k = 100
    if len(context.args) > 0 and context.args[0].isdigit() and int(context.args[0]) != 0:
        k = int(context.args[0])
    await context.channel.send(str(int(random.random() * k) + 1))


# word
@commandHandler.command("word", "random word")
async def word(context):
    await context.channel.send(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])


# phrase <#>
@commandHandler.command("phrase", "random string of words of a given size [default 2]")
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
@commandHandler.command("lookup", "look up a given league player on op.gg")
async def lookup(context):
    if len(context.args) == 0:
        msg = "No name specified."
    else:
        msg = "https://na.op.gg/summoner/userName=" + util.list_to_string(context.args, "")

    await context.channel.send(msg)


# which <options>
@commandHandler.command("which", "pick between a given set of options (separated by commas)")
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
@commandHandler.command("avatar", "fetch a user's profile picture")
async def get_avatar(context):
    name = util.list_to_string(context.args, " ")
    i = None

    if len(context.args) == 0:
        return await context.channel.send(context.author.avatar_url)

    for member in context.guild.members:
        if str(member.nick).lower() == name.lower() or str(member.name).lower() == name.lower():
            i = member.id

    if i:
        msg = str(context.guild.get_member(i).avatar_url)
    else:
        msg = "invalid nickname"

    await context.channel.send(msg)

#
# database cmds

# fortune
@commandHandler.command("fortune", "get a random fortune once per day")
async def fortune(context):
    uid = context.author.id

    await context.channel.send(db.get_fortune(uid))


# add movie
@commandHandler.command("add", "add a movie to the list")
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
@commandHandler.command("remove", "remove a movie from the list")
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
@commandHandler.command("movies", "list all movies")
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
@commandHandler.command("changeprefix", "change the prefix that the bot is accessed with")
async def set_flag(context):
    if len(context.args) == 0 or len(context.args[0]) < 0 or len(context.args[0]) > 2:
        return await context.channel.send("bad prefix")

    uid = context.author.id
    gid = context.guild.id

    newFlag = context.args[0]
    await context.channel.send(db.set_flag(uid, gid, newFlag))
