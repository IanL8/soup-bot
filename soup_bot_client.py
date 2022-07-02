#
# imports
import discord

#
# project imports
import commands
import database_handler as db
import soupbot_utilities as util


#
# context
class Context:
    # init
    def __init__(self, message, channel, author, guild, bot, args):
        self.message = message
        self.channel = channel
        self.author = author
        self.guild = guild
        self.bot = bot
        self.args = args


#
# soupbot
class SoupBotClient(discord.Client):
    # init
    def __init__(self, **options):
        super().__init__(**options)
        # init tables
        db.init()
        # get cmd_handler
        self.cmdHandler = commands.get_command_handler()

    # on connection to discord
    async def on_ready(self):
        for g in self.guilds:
            if not db.add_guild(g):
                util.soup_log("[ERROR] {s} could not be added to the db".format(s=g.name))
        util.soup_log("[BOT] {} has connected to Discord".format(self.user.name))

    # on close
    async def close(self):
        util.soup_log("[BOT] {} has disconnected from Discord".format(self.user.name))

    # on guild join
    async def on_guild_join(self, guild):
        if not db.add_guild(guild):
            util.soup_log("[ERROR] {s} could not be added to the db".format(s=guild.name))

    # on member join
    async def on_member_join(self, member):
        if not db.add_member(member.id, member.guild.id):
            util.soup_log("[ERROR] {m}:{i} could not be added to the db".format(m=member.name, i=member.id))

    # on message
    async def on_message(self, message):
        if message.author == self.user or len(message.content) == 0:
            return

        flag = message.content[0]

        if db.get_flag(message.guild.id) == flag:
            args = message.content.split(" ")
            cmd = args.pop(0)[1:]
            if self.cmdHandler.is_command(cmd):
                await self.cmdHandler.pass_command(cmd, Context(message,
                                                                message.channel,
                                                                message.author,
                                                                message.guild,
                                                                self,
                                                                args))
