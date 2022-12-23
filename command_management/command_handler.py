#
# imports
from discord import app_commands

#
# project imports
import soupbot_utilities as util
from command_management.context import Context
from command_management.commands import CommandBlock

#
# command handler
class CommandHandler:

    def __init__(self):
        self.cmds       = dict()    # cmd name -> function pointer
        self.app_cmds   = dict()    # cmd name -> function pointer
        self.blocks     = set()

    def add_block(self, block: CommandBlock):
        for (k, v) in block.commands.cmds.items():
            self.cmds[k] = v
        for (k, v) in block.commands.app_cmds.items():
            self.app_cmds[k] = v

        self.blocks.add(block)

        util.soup_log(f"[BLK] block: {block.name} added")

    def make_command_tree(self, client):
        tree = app_commands.CommandTree(client)
        for v in self.app_cmds.values():
            tree.add_command(v)

        return tree

    def close(self):
        for b in self.blocks:
            b.close()

    def is_command(self, c):
        return c in self.cmds.keys()

    def list_commands(self):
        return self.cmds.keys()

    def pass_command(self, c, context: Context):
        return self.cmds[c](context)
