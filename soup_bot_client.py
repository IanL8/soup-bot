import discord

from command_management import CommandHandler, Context
from command_blocks import *
import database_handler as db
import soupbot_utilities as util


class SoupBotClient(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)

        if not db.make_tables():
            util.soup_log("[DBS] failed to create tables")

        # initialize command handler and add blocks
        self.cmd_handler = CommandHandler()
        for b in [general_commands.Block, time_commands.Block, vc_commands.Block]:
            self.cmd_handler.add_block(b())

    async def on_ready(self):
        # add guilds to database
        for g in self.guilds:
            if not db.add_guild(g):
                util.soup_log(f"[ERROR] {g.name} could not be added to the db")

        # sync command tree
        try:
            await self.cmd_handler.make_command_tree(self).sync()
        except discord.errors.ClientException:
            util.soup_log("[BOT] failed to create command tree")

        util.soup_log(f"[BOT] {self.user.name} has connected to Discord")

    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=True)

        self.cmd_handler.close()
        util.soup_log(f"[BOT] {self.user.name} has disconnected from Discord")

    async def on_guild_join(self, guild):
        if not db.add_guild(guild):
            util.soup_log(f"[ERROR] {guild.name} could not be added to the db")

    async def on_member_join(self, member):
        if not db.add_member(member.id, member.guild.id):
            util.soup_log(f"[ERROR] {member.name}:{member.id} could not be added to the db")

    async def on_message(self, message):
        if message.author == self.user or len(message.content) == 0:
            return

        if db.get_flag(message.guild.id) == message.content[0]:
            args = message.content.split(" ")
            cmd = args.pop(0)[1:]

            index = self.cmd_handler.find_block(cmd)

            if index != -1:
                try:
                    await self.cmd_handler.pass_command(index, cmd, Context(args, message=message, bot=self))
                except discord.errors.HTTPException:
                    await message.channel.send("content too large")
