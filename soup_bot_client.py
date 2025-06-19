import discord

from command_management.command_handler import CommandHandler
from command_lists import general, music, timer, translator, steam

from database.database_management import db_setup, db_guilds

from soup_util import soup_logging


_logger = soup_logging.get_logger()


class SoupBotClient(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)

        self.command_handler = CommandHandler()
        self.command_handler.add_command_list(general.CommandList(self))
        self.command_handler.add_command_list(music.CommandList(self))
        self.command_handler.add_command_list(timer.CommandList(self))
        self.command_handler.add_command_list(translator.CommandList(self))
        self.command_handler.add_command_list(steam.CommandList(self))

        db_setup.init_database()

    async def setup_hook(self):
        for guild in self.guilds:
            db_guilds.add(guild)

        try:
            await self.command_handler.make_command_tree(self).sync()

        except discord.errors.ClientException:
            _logger.warning("failed to create command tree", exc_info=True)

        await self.command_handler.start()

        _logger.info("%s has connected to Discord", self.user.name)

    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=True)

        await self.command_handler.close()

        _logger.info("%s has disconnected from Discord", self.user.name)

    async def on_guild_join(self, guild):
        db_guilds.add(guild)
