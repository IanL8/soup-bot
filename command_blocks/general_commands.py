#
# imports
import random

#
# project imports
from command_management.commands import Commands, CommandBlock
import database_handler as db
import soupbot_utilities as util


class GeneralCommands(CommandBlock):

    name = "general commands"
    commands = Commands()

    @commands.command("hello")
    async def hello(self, context):
        await context.send_message(f"hi {context.author.display_name}")

    @commands.command("true")
    async def truer(self, context):
        msg = ("TRUE" if random.random() > .49 else "NOT FALSE") + " <:LULW:1010200083314257960>"
        await context.send_message(msg)

    @commands.command("roll", info="roll a dice with the given amount of sides [default 100]", enable_input=True)
    async def roll(self, context):
        k = 100
        if len(context.args) > 0 and context.args[0].isdigit() and int(context.args[0]) != 0:
            k = int(context.args[0])
        try:
            num = int(random.random() * k) + 1
        except OverflowError:
            num = int(random.random() * 100) + 1

        await context.send_message(num)

    @commands.command("word", "random word")
    async def word(self, context):
        await context.send_message(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])

    @commands.command("phrase", "random string of words of a given size [default 2 | max 100]")
    async def phrase(self, context):
        k = 2
        if len(context.args) > 0 and context.args[0].isdigit() and 0 != int(context.args[0]) < 101:
            k = int(context.args[0])
        temp = []
        for i in range(k):
            temp.append(util.WORD_LIST[int(random.random() * len(util.WORD_LIST))])

        await context.send_message(util.list_to_string(temp, " "))

    @commands.command("8ball", enable_input=True)
    async def magic_8Ball(self, context):
        msg = ""
        if not context.basic:
            msg += f"{util.list_to_string(context.args)}\n\n"

        if context.author.id == 295323286244687872:
            msg += f"*{util.MAGIC_8BALL_LIST[int(random.random() * 10)]}*"
        else:
            msg += f"*{random.choice(util.MAGIC_8BALL_LIST)}*"

        await context.send_message(msg)

    @commands.command("lookup", "look up a given league player on op.gg", enable_input=True)
    async def lookup(self, context):
        if len(context.args) == 0:
            msg = "no name specified"
        else:
            msg = "https://na.op.gg/summoner/userName=" + util.list_to_string(context.args, "")

        await context.send_message(msg)

    @commands.command("which", "pick between a given set of options (separated by commas)", enable_input=True)
    async def which(self, context):
        tempList = [s.strip() for s in util.list_to_string(context.args).split(",")]
        while "" in tempList:
            tempList.remove("")
        if len(tempList) == 0:
            msg =  "no options specified"
        else:
            msg = tempList[int(random.random() * len(tempList))]

        await context.send_message(msg)

    @commands.command("git")
    async def git(self, context):
        await context.send_message("https://github.com/IanL8/soup-bot")

    @commands.command("avatar", "fetch a user's profile picture", enable_input=True)
    async def get_avatar(self, context):
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
    # database commands

    @commands.command("fortune", "get a random fortune once per day")
    async def fortune(self, context):
        uid = context.author.id

        await context.send_message(db.get_fortune(uid))


    @commands.command("add", "add a movie to the list", enable_input=True)
    async def add_movie(self, context):
        gid = context.guild.id

        if len(context.args) == 0:
            return await context.send_message("no movie given")

        movie = util.list_to_string(context.args)
        result = db.add_movie(gid, movie)
        if not result[0]:
            return await context.send_message(result[1])

        await context.confirm()

    @commands.command("remove", "remove a movie from the list", enable_input=True)
    async def remove_movie(self, context):
        gid = context.guild.id

        if len(context.args) == 0:
            return await context.send_message("no movie given")

        movie = util.list_to_string(context.args)
        result = db.remove_movie(gid, movie)
        if not result[0]:
            return await context.send_message(result[1])

        await context.confirm()

    @commands.command("movies", "list all movies")
    async def movie_list(self, context):
        li = db.get_movie_list(context.guild.id)
        if not li:
            return await context.send_message("no movies")

        temp = "```\n"
        for i in li:
            temp += i[0] + "\n"
        temp += "\n```"

        await context.send_message(temp)

    #
    # admin commands

    @commands.command("changeprefix", "change the prefix that the bot is accessed with", enable_input=True)
    async def set_flag(self, context):
        if len(context.args) == 0 or len(context.args[0]) < 0 or len(context.args[0]) > 2:
            return await context.send_message("bad prefix")

        newFlag = context.args[0]

        result = db.set_flag(context.author.id, context.guild.id, newFlag)
        if not result[0]:
            return await context.send_message(result[1])

        await context.confirm()
