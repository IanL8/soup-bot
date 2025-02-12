from random import random, choice
from functools import reduce

from command_management import commands
from database import database_handler as database
from soupbot_util.constants import WORD_LIST, MAGIC_8BALL_LIST


class CommandList(commands.CommandList):

    name = "general commands"

    def on_close(self):
        pass

    @commands.command("hello", desc="Says hi to the user")
    async def hello(self, context):
        await context.send_message(f"hiii :3 {context.author.display_name}")

    @commands.command("true")
    async def truer(self, context):
        await context.send_message("TRUE" if random() > .49 else "NOT FALSE")

    @commands.command("roll", desc="Get a random number [default 100]")
    async def roll(self, context, max_number:int=100):
        if not (1000000000 > max_number > 0):
            max_number = 100

        await context.send_message(int(random() * max_number) + 1)

    @commands.command("coinflip", desc="Flip a coin")
    async def coinflip(self, context):
        await context.send_message("Heads" if int(random()*2) == 1 else "Tails")

    @commands.command("word", desc="Get a random word")
    async def word(self, context):
        await context.send_message(choice(WORD_LIST))

    @commands.command("phrase", desc="Random string of words of a given size [default 2 | max 100]")
    async def phrase(self, context, size:int=2):
        if not (0 < size < 101):
            size = 2

        await context.send_message(reduce(lambda x, y: f"{x} {y}", [choice(WORD_LIST) for _ in range(size)]))

    @commands.command("8ball", desc="Receive an answer from a magic 8 ball. Optionally can provide a question")
    async def magic_8Ball(self, context, question:str=""):
        if len(question) > 0:
            message = f"{question}\n\n{choice(MAGIC_8BALL_LIST)}"
        else:
            message = choice(MAGIC_8BALL_LIST)

        await context.send_message(message)

    @commands.command("opgg-lookup", desc="Look up a given league player on op.gg")
    async def lookup(self, context, username:str):
        await context.send_message(f"https://na.op.gg/summoners/na/{username.replace(' ', '%20').replace('#', '-')}")

    @commands.command("which", desc="Makes a random selection between options separated by commas")
    async def which(self, context, options:str):
        await context.send_message(f"picking out of the options {options}...\n\n"
                                   f"{choice([x for x in options.split(',') if x.strip() != ''])}")

    @commands.command("avatar", desc="Fetch a user's pfp by @ing them or writing their name. By default will return your avatar")
    async def get_avatar(self, context, username:str=""):
        if len(username) == 0:
            message = str(context.author.avatar)

        elif len(context.mentions) > 0:
            message = str(context.mentions[0].avatar)

        else:
            member = context.guild.get_member_named(username)
            message = str(member.avatar) if member else "no such user exists"

        await context.send_message(message)

    @commands.command("fortune", desc="Get a random fortune once per day")
    async def fortune(self, context):
        await context.send_message(database.fortune(context.author))

    @commands.command("movie-add", desc="Add a movie to the movie list")
    async def add_movie(self, context, name:str):
        if database.movies_table_contains(context.guild, name):
            await context.send_message("movie already in list")

        elif not database.add_movie(context.guild, name):
            await context.send_message("database error while adding movie")

        else:
            await context.confirm()

    @commands.command("movie-remove", desc="Remove a movie from the movie list")
    async def remove_movie(self, context, name:str):
        if not database.movies_table_contains(context.guild, name):
            await context.send_message("movie not in list")

        elif not database.remove_movie(context.guild, name):
            await context.send_message("database error while removing movie")

        else:
            await context.confirm()

    @commands.command("movies", desc="List all movies")
    async def movie_list(self, context):
        movies = database.get_movie_list(context.guild)

        if not movies:
            await context.send_message("no movies")
        else:
            await context.send_message("```\n" + reduce(lambda x, y: f"{x}\n{y}", movies) + "\n```")
