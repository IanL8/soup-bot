#
# imports
import random
import asyncio
from async_timeout import timeout

#
# project imports
from soup_commands import commandHandler
from handlers import database_handler as db
import soupbot_utilities as util

#
# basic cmds

# help
@commandHandler.command("help")
async def cmd_help(context):
    categories = tuple(commandHandler.categories.keys())

    def make_help_page(category, pos: int):
        temp = f"{category} - page ({pos}/{len(commandHandler.categories)})```\n"
        for cmd in commandHandler.categories[category]:
            temp += cmd + " " * (20 - len(cmd)) + commandHandler.info[cmd] + "\n"
        temp += "```"
        return temp

    msg = await context.send_message(make_help_page(categories[0], 1))

    await msg.add_reaction("◀️")
    await msg.add_reaction("▶️")

    async with timeout(60):
        i = 0                               # current position
        k = len(categories) - 1             # last position
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
                if i < k:
                    i += 1
                else:
                    i = 0
                await msg.edit(content=make_help_page(categories[i], i+1))
            elif reaction.emoji == "◀️":
                if i > 0:
                    i -= 1
                else:
                    i = k
                await msg.edit(content=make_help_page(categories[i], i+1))


# hello
@commandHandler.command("hello")
async def hello(context):
    await context.send_message(f"hi {context.author.display_name}")


# true
@commandHandler.command("true")
async def true_lulw(context):
    msg = ("TRUE" if random.random() > .49 else "NOT FALSE") + " <:LULW:1010200083314257960>"

    await context.send_message(msg)


# roll <#>
@commandHandler.command("roll", "roll a dice with the given amount of sides [default 100]", enableInput=True)
async def roll(context):
    k = 100
    if len(context.args) > 0 and context.args[0].isdigit() and int(context.args[0]) != 0:
        k = int(context.args[0])
    try:
        num = int(random.random() * k) + 1
    except OverflowError:
        num = int(random.random() * 100) + 1

    await context.send_message(num)


# word
@commandHandler.command("word", "random word")
async def word(context):
    await context.send_message(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])


# phrase <#>
@commandHandler.command("phrase", "random string of words of a given size [default 2 | max 100]")
async def phrase(context):
    k = 2
    if len(context.args) > 0 and context.args[0].isdigit() and 0 != int(context.args[0]) < 101:
        k = int(context.args[0])
    temp = []
    for i in range(k):
        temp.append(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])

    await context.send_message(util.list_to_string(temp, " "))


# 8ball
@commandHandler.command("8ball", enableInput=True)
async def magic_8Ball(context):
    msg = ""
    if not context.basic:
        msg += f"{util.list_to_string(context.args)}\n\n"

    if context.author.id == 295323286244687872:
        msg += f"**{util.MAGIC_8BALL_LIST[int(random.random() * 10)]}**"
    else:
        msg += f"*{random.choice(util.MAGIC_8BALL_LIST)}*"

    await context.send_message(msg)


# lookup <name>
@commandHandler.command("lookup", "look up a given league player on op.gg", enableInput=True)
async def lookup(context):
    if len(context.args) == 0:
        msg = "no name specified"
    else:
        msg = "https://na.op.gg/summoner/userName=" + util.list_to_string(context.args, "")

    await context.send_message(msg)


# which <options>
@commandHandler.command("which", "pick between a given set of options (separated by commas)", enableInput=True)
async def which(context):
    tempList = [s.strip() for s in util.list_to_string(context.args).split(",")]
    while "" in tempList:
        tempList.remove("")
    if len(tempList) == 0:
        msg =  "no options specified"
    else:
        msg = tempList[int(random.random() * len(tempList))]

    await context.send_message(msg)


# git
@commandHandler.command("git")
async def git(context):
    await context.send_message("https://github.com/IanL8/soup-bot")


# avatar
@commandHandler.command("avatar", "fetch a user's profile picture", enableInput=True)
async def get_avatar(context):
    name = util.list_to_string(context.args, " ")
    i = None

    if len(context.args) == 0:
        return await context.send_message(context.author.avatar)

    for member in context.guild.members:
        if str(member.nick).lower() == name.lower() or str(member.name).lower() == name.lower():
            i = member.id

    if i:
        msg = str(context.guild.get_member(i).avatar)
    else:
        msg = "invalid nickname"

    await context.send_message(msg)

#
# database cmds

# fortune
@commandHandler.command("fortune", "get a random fortune once per day")
async def fortune(context):
    uid = context.author.id

    await context.send_message(db.get_fortune(uid))


# add movie
@commandHandler.command("add", "add a movie to the list", "movie", enableInput=True)
async def add_movie(context):
    gid = context.guild.id

    if len(context.args) == 0:
        return await context.send_message("no movie given")

    movie = util.list_to_string(context.args)
    result = db.add_movie(gid, movie)
    if not result[0]:
        return await context.send_message(result[1])

    await context.confirm()


# remove movie
@commandHandler.command("remove", "remove a movie from the list", "movie", enableInput=True)
async def remove_movie(context):
    gid = context.guild.id

    if len(context.args) == 0:
        return await context.send_message("no movie given")

    movie = util.list_to_string(context.args)
    result = db.remove_movie(gid, movie)
    if not result[0]:
        return await context.send_message(result[1])

    await context.confirm()

# list out the movies
@commandHandler.command("movies", "list all movies", "movie")
async def movie_list(context):
    li = db.get_movie_list(context.guild.id)
    if not li:
        return await context.send_message("no movies")

    temp = "```\n"
    for i in li:
        temp += i[0] + "\n"
    temp += "\n```"

    await context.send_message(temp)

#
# admin soup_commands

# change prefix
@commandHandler.command("change_prefix", "change the prefix that the bot is accessed with", "admin", enableInput=True)
async def set_flag(context):
    if len(context.args) == 0 or len(context.args[0]) < 0 or len(context.args[0]) > 2:
        return await context.send_message("bad prefix")

    newFlag = context.args[0]

    result = db.set_flag(context.author.id, context.guild.id, newFlag)
    if not result[0]:
        return await context.send_message(result[1])

    await context.confirm()
