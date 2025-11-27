import random as _random
from functools import reduce as _reduce

import command_management.commands as _commands
import database.database_management.db_movies as _db_movies
import database.database_management.db_cooldowns as _db_cooldowns
import soup_util.constants as _constants


class CommandList(_commands.CommandList):

    name = "general commands"

    @_commands.command("hello", desc="Says hi to the user")
    async def hello(self, context):
        await context.send_message(f"hiii :3 {context.author.display_name}")

    @_commands.command("true")
    async def truer(self, context):
        await context.send_message("TRUE" if _random.random() > .49 else "NOT FALSE")

    @_commands.command("roll", desc="Get a random number [default 100]")
    async def roll(self, context, max_number: int = 100):
        if not (1000000000 > max_number > 0):
            max_number = 100

        await context.send_message(int(_random.random() * max_number) + 1)

    @_commands.command("coinflip", desc="Flip a coin")
    async def coinflip(self, context):
        await context.send_message("Heads" if int(_random.random()*2) == 1 else "Tails")

    @_commands.command("wordle-guess", desc="Gives a random word from the pool of possible Wordle answers")
    async def wordle_guess(self, context):
        await context.send_message(f"Good luck! ||{_random.choice(_constants.WORDLE_LIST)}||")

    @_commands.command("word", desc="Get a random word")
    async def word(self, context):
        await context.send_message(_random.choice(_constants.WORD_LIST))

    @_commands.command("phrase", desc="Random string of words of a given size [default 2 | max 100]")
    async def phrase(self, context, size: int = 2):
        if not (0 < size < 101):
            size = 2

        await context.send_message(_reduce(lambda x, y: f"{x} {y}", [_random.choice(_constants.WORD_LIST) for _ in range(size)]))

    @_commands.command("8ball", desc="Receive an answer from a magic 8 ball. Optionally can provide a question")
    async def magic_8ball(self, context, question: str = ""):
        if len(question) > 0:
            message = f"{question}\n\n{_random.choice(_constants.MAGIC_8BALL_LIST)}"
        else:
            message = _random.choice(_constants.MAGIC_8BALL_LIST)

        await context.send_message(message)

    @_commands.command("opgg-lookup", desc="Look up a given league player on op.gg")
    async def lookup(self, context, username: str):
        await context.send_message(f"https://na.op.gg/summoners/na/{username.replace(' ', '%20').replace('#', '-')}")

    @_commands.command("which", desc="Makes a random selection between options separated by commas")
    async def which(self, context, options: str):
        await context.send_message(
            f"Picking out of the options {options}...\n\n{_random.choice([x for x in options.split(',') if x.strip() != ''])}"
        )

    @_commands.command("avatar", desc="Fetch a user's pfp by @ing them or writing their name. By default will return your avatar")
    async def get_avatar(self, context, username: str=""):
        if len(username) == 0:
            message = str(context.author.avatar)

        elif len(context.mentions) > 0:
            message = str(context.mentions[0].avatar)

        else:
            member = context.guild.get_member_named(username)
            message = str(member.avatar) if member else "No such user exists."

        await context.send_message(message)

    @_commands.command("fortune", desc="Get a random fortune once per day")
    async def fortune(self, context):
        await context.send_message(_db_cooldowns.fortune(context.author))

    @_commands.command("movie-add", desc="Add a movie to the movie list")
    async def add_movie(self, context, name: str):
        if _db_movies.contains(context.guild, name):
            raise _commands.CommandError("Movie already in list.")

        _db_movies.add(context.guild, name)
        await context.confirm()

    @_commands.command("movie-remove", desc="Remove a movie from the movie list")
    async def remove_movie(self, context, name: str):
        if not _db_movies.contains(context.guild, name):
            raise _commands.CommandError("Movie not in list.")

        _db_movies.remove(context.guild, name)
        await context.confirm()

    @_commands.command("movies", desc="List all movies")
    async def movie_list(self, context):
        movies = _db_movies.get_all(context.guild)

        if not movies:
            await _commands.CommandError("No movies in the list.")

        await context.send_message("```\n" + _reduce(lambda x, y: f"{x}\n{y}", movies[:100]) + "\n```")
