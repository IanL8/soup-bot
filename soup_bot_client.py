#
# imports
import discord

#
# project imports
import commands
from handlers import database_handler as db
import soupbot_utilities as util

#
# context
class Context:
    # init
    def __init__(self, message, channel, author, guild, voice_client, bot, args):
        self.message = message
        self.channel = channel
        self.author = author
        self.guild = guild
        self.voice_client = voice_client
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
        # self.cmdHandler.set_bot(self)

    # on connection to discord
    async def on_ready(self):
        for g in self.guilds:
            if not db.add_guild(g):
                util.soup_log(f"[ERROR] {g.name} could not be added to the db")
        util.soup_log(f"[BOT] {self.user.name} has connected to Discord")

    # on close
    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=False)
        commands.cleanup()
        util.soup_log(f"[BOT] {self.user.name} has disconnected from Discord")

    # on guild join
    async def on_guild_join(self, guild):
        if not db.add_guild(guild):
            util.soup_log(f"[ERROR] {guild.name} could not be added to the db")

    # on member join
    async def on_member_join(self, member):
        if not db.add_member(member.id, member.guild.id):
            util.soup_log(f"[ERROR] {member.name}:{member.id} could not be added to the db")

    # on message
    async def on_message(self, message):
        if message.author == self.user or len(message.content) == 0:
            return

        flag = message.content[0]

        if db.get_flag(message.guild.id) == flag:
            args = message.content.split(" ")
            cmd = args.pop(0)[1:]
            if self.cmdHandler.is_command(cmd):
                try:
                    await self.cmdHandler.pass_command(cmd, Context(message,
                                                                    message.channel,
                                                                    message.author,
                                                                    message.guild,
                                                                    message.guild.voice_client,
                                                                    self,
                                                                    args))
                except discord.errors.HTTPException:
                    await message.channel.send("content too large")
