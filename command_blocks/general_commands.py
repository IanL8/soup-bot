from random import random, choice
from functools import reduce

from command_management import Commands, CommandBlock
import database_handler as db
import soupbot_utilities as util


class Block(CommandBlock):

    name = "general commands"
    commands = Commands()

    @commands.command("hello")
    async def hello(self, context):
        await context.send_message(f"hi {context.author.display_name}")

    @commands.command("true")
    async def truer(self, context):
        await context.send_message("TRUE" if random() > .49 else "NOT FALSE")

    @commands.command("roll", info="roll a dice with the given amount of sides [default 100]", enable_input=True)
    async def roll(self, context):
        sides = 100
        if len(context.args) > 0 and context.args[0].isdigit() and 1000000000 > int(context.args[0]) > 0:
            sides = int(context.args[0])

        await context.send_message(int(random() * sides) + 1)

    @commands.command("word", "random word")
    async def word(self, context):
        await context.send_message(choice(util.WORD_LIST))

    @commands.command("phrase", "random string of words of a given size [default 2 | max 100]")
    async def phrase(self, context):
        length = 2
        if len(context.args) > 0 and context.args[0].isdigit() and 0 < int(context.args[0]) < 101:
            length = int(context.args[0])

        await context.send_message(reduce(lambda x, y: f"{x} {y}", [choice(util.WORD_LIST) for _ in range(length)]))

    @commands.command("8ball", enable_input=True)
    async def magic_8Ball(self, context):
        prompt = reduce(lambda x, y: f"{x} {y}", context.args) + "\n\n" if not context.is_basic and context.args else ""
        await context.send_message(prompt + choice(util.MAGIC_8BALL_LIST))

    @commands.command("lookup", "look up a given league player on op.gg", enable_input=True)
    async def lookup(self, context):
        if len(context.args) == 0:
            return await context.send_message("no name given")
        else:
            return await context.send_message(
                "https://na.op.gg/summoners/na/" + reduce(lambda x, y: f"{x}%20{y}", context.args).replace("#", "-")
            )

    @commands.command("which", "random selection between options that are separated by commas", enable_input=True)
    async def which(self, context):
        str_args = reduce(lambda x, y: f"{x} {y}", context.args)
        options = tuple(filter(lambda x: x.strip() != "", str_args.split(",")))
        await context.send_message(choice(options))

    @commands.command("git")
    async def git(self, context):
        await context.send_message("https://github.com/IanL8/soup-bot")

    @commands.command("avatar", "fetch a user's profile picture", enable_input=True)
    async def get_avatar(self, context):
        if not context.args:
            msg = str(context.author.avatar)
        elif len(context.mentions) > 0:
            msg = str(context.mentions[0].avatar)
        else:
            msg = "no user found"

        await context.send_message(msg)

    @commands.command("fortune", "get a random fortune once per day")
    async def fortune(self, context):
        await context.send_message(db.get_fortune(context.author.id))

    @commands.command("add", "add a movie to the list", enable_input=True)
    async def add_movie(self, context):
        movie = reduce(lambda x, y: f"{x} {y}", context.args)

        if len(context.args) == 0:
            return await context.send_message("no movie given")
        elif db.movies_table_contains(context.guild.id, movie):
            return await context.send_message("movie already in list")

        if not db.add_movie(context.guild.id, movie):
            return await context.send_message("database error while adding movie")

        await context.confirm()

    @commands.command("remove", "remove a movie from the list", enable_input=True)
    async def remove_movie(self, context):
        movie = reduce(lambda x, y: f"{x} {y}", context.args)

        if len(context.args) == 0:
            return await context.send_message("no movie given")
        elif not db.movies_table_contains(context.guild.id, movie):
            return await context.send_message("movie not in list")

        if not db.remove_movie(context.guild.id, movie):
            return await context.send_message("database error while removing movie")

        await context.confirm()

    @commands.command("movies", "list all movies")
    async def movie_list(self, context):
        movies = db.get_movie_list(context.guild.id)
        if not movies:
            return await context.send_message("no movies")

        msg = "```\n"
        for m in movies:
            msg += m + "\n"
        msg += "\n```"

        await context.send_message(msg)

    @commands.command("change_prefix", "change the prefix that the bot is accessed with", enable_input=True)
    async def set_prefix(self, context):
        if len(context.args) == 0 or len(context.args[0]) < 0 or len(context.args[0]) > 2:
            return await context.send_message("bad prefix")
        elif not db.is_guild_owner(context.author.id, context.guild.id):
            return await context.send_message("only the server owner has access to this command")

        new_prefix = context.args[0]

        ret = db.set_prefix(context.guild.id, new_prefix)
        if not ret:
            return await context.send_message("database error")

        return await context.confirm()
