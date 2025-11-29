import discord as _discord

from . import commands as _commands
from soup_util.soup_logging import logger as _logger


class CommandHandler:

    def __init__(self):
        self.command_lists: list[_commands.CommandList] = []
        self.basic_commands: {str: callable} = {}

    @property
    def basic_command_names(self):
        return [name for name in self.basic_commands.keys()]

    def add_command_list(self, command_list: _commands.CommandList):
        self.command_lists.append(command_list)
        for k, v in command_list.basic_commands.items():
            self.basic_commands[k] = v

        _logger.info("%s added", command_list.name)

    def make_command_tree(self, client: _discord.Client):
        tree = _discord.app_commands.CommandTree(client)

        for command_list in self.command_lists:
            for app_command in command_list.app_commands:
                tree.add_command(app_command)

        return tree

    async def start(self):
        for command_list in self.command_lists:
            await command_list.on_start()

    async def close(self):
        for command_list in self.command_lists:
            await command_list.on_close()

    async def pass_command(self, command_name, message, client):
        await self.basic_commands[command_name](_commands.Context(message=message, client=client))
