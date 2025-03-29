import discord

from command_management.command_handler import CommandHandler
from command_lists import general, music, timer, translator, steam

from database import database_handler as database

from soupbot_util.logger import soup_log


class SoupBotClient(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)

        self.command_handler = CommandHandler()
        self.command_handler.add_command_list(general.CommandList())
        self.command_handler.add_command_list(music.CommandList())
        self.command_handler.add_command_list(timer.CommandList())
        self.command_handler.add_command_list(translator.CommandList())
        self.command_handler.add_command_list(steam.CommandList())

        database.init_database()

    async def on_ready(self):
        for guild in self.guilds:
            database.add_guild(guild)

        try:
            await self.command_handler.make_command_tree(self).sync()

        except discord.errors.ClientException:
            soup_log("failed to create command tree", "bot")

        soup_log(f"{self.user.name} has connected to Discord", "bot")

    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=True)

        self.command_handler.close()

        soup_log(f"{self.user.name} has disconnected from Discord", "bot")

    async def on_guild_join(self, guild):
        database.add_guild(guild)
