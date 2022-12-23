#
# imports
import discord

#
# project imports
from command_management.context import Context
from command_management.command_handler import CommandHandler
from command_blocks import *
import database_handler as db
import soupbot_utilities as util

#
# soupbot
class SoupBotClient(discord.Client):
    # init
    def __init__(self, **options):
        super().__init__(**options)
        # init tables
        db.init()

        # init cmds
        self.cmd_handler = CommandHandler()

        cmd_blocks = [general_commands.GeneralCommands(), time_commands.TimeCommands(), vc_commands.MusicCommands()]
        for b in cmd_blocks:
            self.cmd_handler.add_block(b)

    # on connection to discord
    async def on_ready(self):
        for g in self.guilds:
            if not db.add_guild(g):
                util.soup_log(f"[ERROR] {g.name} could not be added to the db")
        util.soup_log(f"[BOT] {self.user.name} has connected to Discord")
        try:
            await self.cmd_handler.make_command_tree(self).sync()
        except discord.errors.ClientException:
            util.soup_log("[BOT] failed to create command tree")

    # on close
    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=False)

        self.cmd_handler.close()
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

        if db.get_flag(message.guild.id) == message.content[0]:
            args = message.content.split(" ")
            cmd = args.pop(0)[1:]
            if self.cmd_handler.is_command(cmd):
                c = Context(message, message.channel, message.author, message.guild, message.guild.voice_client, self, args)
                try:
                    await self.cmd_handler.pass_command(cmd, c)
                except discord.errors.HTTPException:
                    await message.channel.send("content too large")
