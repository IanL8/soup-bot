from discord import app_commands, Client

from .commands import CommandList
from soupbot_util.logger import soup_log


class CommandHandler:
    """Defines how the discord client adds commands."""

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

    def close(self):
        for command_list in self.command_lists:
            command_list.on_close()
