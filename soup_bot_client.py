import discord as _discord

import command_lists as _clists
import database.database_management.db_setup as _db_setup
import database.database_management.db_guilds as _db_guilds
from command_management.command_handler import CommandHandler as _CommandHandler
from soup_util.soup_logging import logger as _logger


class SoupBotClient(_discord.Client):

    def __init__(self, **options):
        super().__init__(**options)

        self.command_handler = _CommandHandler()

        self.command_handler.add_command_list(_clists.general.CommandList(self))
        self.command_handler.add_command_list(_clists.music.CommandList(self))
        self.command_handler.add_command_list(_clists.timer.CommandList(self))
        self.command_handler.add_command_list(_clists.translator.CommandList(self))
        self.command_handler.add_command_list(_clists.steam.CommandList(self))

        _db_setup.init_database()

    async def setup_hook(self):
        for guild in self.guilds:
            _db_guilds.add(guild)

        try:
            await self.command_handler.make_command_tree(self).sync()

        except _discord.errors.ClientException:
            _logger.error("Failed to create command tree", exc_info=True)

        await self.command_handler.start()

        _logger.info("%s has connected to Discord", self.user.name)

    async def close(self):
        for vc in self.voice_clients:
            await vc.disconnect(force=True)

        await self.command_handler.close()

        _logger.info("%s has disconnected from Discord", self.user.name)

    async def on_guild_join(self, guild):
        _db_guilds.add(guild)

    async def on_message(self, message):
        prefix = "!" if message.guild is None else _db_guilds.get_prefix(message.guild)

        if self._has_permissions(message.channel) and not (message.author == self.user or len(message.content) == 0) \
                and message.content.startswith(prefix):

            command_name = message.content.split(" ").pop(0)[len(prefix):]

            if command_name in self.command_handler.basic_command_names:
                await self.command_handler.pass_command(command_name, message, self)

    @staticmethod
    def _has_permissions(channel):
        if channel.guild is None:
            return True

        permissions = channel.permissions_for(channel.guild.me)

        return (type(channel) != _discord.Thread and permissions.send_messages and permissions.add_reactions) \
                or (type(channel) == _discord.Thread and permissions.send_messages_in_threads)
