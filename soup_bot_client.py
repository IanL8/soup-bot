import discord

from command_management import CommandHandler, Context
from command_blocks import *
import database_handler as db
import soupbot_utilities as util


class SoupBotClient(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)

        self.cmd_handler = CommandHandler()
        for cmd_module in [general, music, timer]:
            self.cmd_handler.add_block(cmd_module.Block())

    async def on_ready(self):
        for g in self.guilds:
            db.add_guild(g.id, g.text_channels[0].id, g.owner_id, [m.id for m in g.members if not m.bot])

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
        db.add_guild(guild.id, guild.text_channels[0].id, guild.owner_id, [m.id for m in guild.members if not m.bot])

    async def on_member_join(self, member):
        db.add_member(member.id, member.guild.id)

    async def on_message(self, message):
        if not (message.author == self.user or len(message.content) == 0) \
                and db.get_prefix(message.guild.id) == message.content[0]:

            args = message.content.split(" ")
            cmd = args.pop(0)[1:]
            block_index = self.cmd_handler.find_block(cmd)

            if block_index != -1:
                try:
                    await self.cmd_handler.pass_command(block_index, cmd, Context(args, message=message, bot=self))
                except discord.errors.HTTPException:
                    await message.channel.send("content too large")
