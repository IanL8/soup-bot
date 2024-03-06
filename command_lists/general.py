from random import random, choice
from functools import reduce

from command_management.commands import CommandList, Commands
import database_handler as database
from soupbot_util.constants import WORD_LIST, MAGIC_8BALL_LIST


class GeneralCommandList(CommandList):

    name = "general commands"
    commands = Commands()

    def on_close(self):
        pass

    @commands.command("hello")
    async def hello(self, context):
        await context.send_message(f"hi {context.author.display_name}")

    @commands.command("true")
    async def truer(self, context):
        await context.send_message("TRUE" if random() > .49 else "NOT FALSE")

    @commands.command("roll", info="roll a dice with the given amount of sides [default 100]", enable_input=True)
    async def roll(self, context):
        if len(context.args) > 0 and context.args[0].isdigit() and 1000000000 > int(context.args[0]) > 0:
            sides = int(context.args[0])
        else:
            sides = 100
        await context.send_message(int(random() * sides) + 1)

    @commands.command("coinflip", info="flip a coin", enable_input=False)
    async def coinflip(self, context):
        await context.send_message("Heads" if int(random()*2) == 1 else "Tails")

    @commands.command("word", "random word")
    async def word(self, context):
        await context.send_message(choice(WORD_LIST))

    @commands.command("phrase", "random string of words of a given size [default 2 | max 100]")
    async def phrase(self, context):
        if len(context.args) > 0 and context.args[0].isdigit() and 0 < int(context.args[0]) < 101:
            length = int(context.args[0])
        else:
            length = 2
        await context.send_message(reduce(lambda x, y: f"{x} {y}", [choice(WORD_LIST) for _ in range(length)]))

    @commands.command("8ball", enable_input=True)
    async def magic_8Ball(self, context):
        if not context.is_basic_command and context.content:
            prompt = context.content + "\n\n"
        else:
            prompt = ""
        await context.send_message(prompt + choice(MAGIC_8BALL_LIST))

    @commands.command("lookup", "look up a given league player on op.gg", enable_input=True)
    async def lookup(self, context):
        if len(context.content) == 0:
            await context.send_message("no name given")
        else:
            await context.send_message(
                "https://na.op.gg/summoners/na/" + context.content.replace(" ", "%20").replace("#", "-")
            )

    @commands.command("which", "random selection between options [separate by commas]", enable_input=True)
    async def which(self, context):
        if len(context.content) == 0:
            await context.send_message("no options provided")
        else:
            options = tuple(filter(lambda x: x.strip() != "", context.content.split(",")))
            await context.send_message(choice(options))

    @commands.command("git")
    async def git(self, context):
        await context.send_message("https://github.com/IanL8/soup-bot")

    @commands.command("avatar", "fetch a user's profile picture", enable_input=True)
    async def get_avatar(self, context):
        if len(context.content) == 0:
            await context.send_message(str(context.author.avatar))
        elif len(context.mentions) > 0:
            await context.send_message(str(context.mentions[0].avatar))
        else:
            member = context.guild.get_member_named(context.content)
            await context.send_message(str(member.avatar) if member else "no such user exists")

    @commands.command("fortune", "get a random fortune once per day")
    async def fortune(self, context):
        await context.send_message(database.fortune(context.author.id))

    @commands.command("add", "add a movie to the list", enable_input=True)
    async def add_movie(self, context):
        if len(context.content) == 0:
            await context.send_message("no movie given")
        elif database.movies_table_contains(context.guild.id, context.content):
            await context.send_message("movie already in list")
        elif not database.add_movie(context.guild.id, context.content):
            await context.send_message("database error while adding movie")
        else:
            await context.confirm()

    @commands.command("remove", "remove a movie from the list", enable_input=True)
    async def remove_movie(self, context):
        if len(context.content) == 0:
            await context.send_message("no movie given")
        elif not database.movies_table_contains(context.guild.id, context.content):
            await context.send_message("movie not in list")
        elif not database.remove_movie(context.guild.id, context.content):
            await context.send_message("database error while removing movie")
        else:
            await context.confirm()

    @commands.command("movies", "list all movies")
    async def movie_list(self, context):
        movies = database.get_movie_list(context.guild.id)
        if not movies:
            await context.send_message("no movies")
        else:
            await context.send_message("```\n" + reduce(lambda x, y: f"{x}\n{y}", movies) + "\n```")

    @commands.command("change_prefix", "change the prefix that the bot is accessed with", enable_input=True)
    async def set_prefix(self, context):
        if not database.is_guild_owner(context.author.id, context.guild.id):
            await context.send_message("only the server owner has access to this command")
        elif len(context.content) == 0 or len(context.content) > 2:
            await context.send_message("bad prefix")
        elif not database.set_prefix(context.guild.id, context.content):
            await context.send_message("database error while setting new prefix")
        else:
            await context.confirm()
