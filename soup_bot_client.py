import discord

from command_management.context import Context
from command_management.command_handler import CommandHandler
from command_lists import general, music, timer
import database_handler as database
from soupbot_util.logger import soup_log


class SoupBotClient(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)
        self.command_handler = CommandHandler()
        command_lists = [general.GeneralCommandList(), music.MusicCommandList(), timer.TimerCommandList()]
        for command_list in command_lists:
            self.command_handler.add_command_list(command_list)

    async def on_ready(self):
        for guild in self.guilds:
            database.add_guild(
                guild.id,
                guild.text_channels[0].id,
                guild.owner_id,
                [member.id for member in guild.members if not member.bot]
            )
        try:
            await self.command_handler.make_command_tree(self).sync()
        except discord.errors.ClientException:
            soup_log("failed to create command tree", "bot")
        soup_log(f"{self.user.name} has connected to Discord", "bot")

    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=True)
        self.command_handler.on_close()
        soup_log(f"{self.user.name} has disconnected from Discord", "bot")

    async def on_guild_join(self, guild):
        database.add_guild(
            guild.id,
            guild.text_channels[0].id,
            guild.owner_id,
            [m.id for m in guild.members if not m.bot]
        )

    async def on_member_join(self, member):
        database.add_member(member.id, member.guild.id)

    async def on_message(self, message):
        prefix = database.get_prefix(message.guild.id)
        if len(message.content) == 0 or prefix != message.content[0] or message.author == self.user:
            return
        command_name = message.content.split(" ").pop(0)[1:]
        index = self.command_handler.find_command_list_index(command_name)
        if index == -1:
            return
        try:
            await self.command_handler.pass_command(
                index,
                command_name,
                Context(message.content[len(prefix)+len(command_name):].strip(), message=message, bot=self)
            )
        except discord.errors.HTTPException:
            await message.channel.send("content too large")
