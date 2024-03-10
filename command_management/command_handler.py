from discord import app_commands, Client

from .commands import CommandList
from .context import Context
from soupbot_util.logger import soup_log


class CommandHandler:
    """Defines how the discord client adds and calls commands."""

    def __init__(self):
        self.command_lists : [CommandList] = []

    def add_command_list(self, command_list: CommandList):
        self.command_lists.append(command_list)
        soup_log(f"{command_list.name} added", "lst")

    def make_command_tree(self, client: Client):
        tree = app_commands.CommandTree(client)
        for command_list in self.command_lists:
            for app_command in command_list.app_commands:
                tree.add_command(app_command)
        return tree

    def on_close(self):
        for command_list in self.command_lists:
            command_list.on_close()

    def command_list_index(self, command_name:str):
        for index, command_list in enumerate(self.command_lists):
            if command_name in command_list:
                return index
        return -1

    async def pass_command(self, index: int, command_name: str, context: Context):
        return await self.command_lists[index](command_name, context)
