#
# imports
from discord import app_commands, Interaction
from abc import ABC

#
# project imports
import soupbot_utilities as util
from command_management.context import Context

class Commands:

    def __init__(self):
        self.cmds       = dict()    # cmd name -> function pointer
        self.app_cmds   = dict()    # cmd name -> function pointer
        self.block      = None

    def add_instance(self, block):
        self.block = block

    def command(self, name: str, info: str = "...", enable_input: bool = False):

        def decorator(f: callable):

            # basic wrapper
            def basic_wrapper(context):
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return f(self.block, context)

            # app wrapper
            if enable_input:
                async def app_wrapper(interaction: Interaction, enter: str):
                    util.soup_log(f"[CMD] {name} {enter if not enter else enter.split()}")
                    return await f(self.block, Context.copy_from_interaction(interaction, enter))
            else:
                async def app_wrapper(interaction: Interaction):
                    util.soup_log(f"[CMD] {name}")
                    return await f(self.block, Context.copy_from_interaction(interaction, ""))

            self.cmds[name] = basic_wrapper
            self.app_cmds[name] = app_commands.command(name=name, description=info)(app_wrapper)

            return basic_wrapper

        return decorator

class CommandBlock(ABC):

    name: str = "default"
    commands: Commands

    def __init__(self):
        self.commands.add_instance(self)

    def close(self):
        pass
