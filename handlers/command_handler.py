#
# imports
from discord import app_commands
from discord import Interaction
# import inspect

#
# project imports
import soupbot_utilities as util
from soup_commands.context import Context

#
# command handler
class CommandHandler:

    def __init__(self):
        self.cmds = dict()          # cmd name -> function pointer
        self.appCMDs = dict()          # cmd name -> function pointer
        self.info = dict()          # cmd name -> info
        self.categories = dict()    # category -> list of cmd names

    def is_command(self, c):
        return c in self.cmds.keys()

    def list_commands(self):
        return self.cmds.keys()

    def pass_command(self, c, context):
        return self.cmds[c](context)

    def command(self, name: str, info: str = "...", category: str = "general", enableInput: bool= False):

        def decorator(f: callable):

            # basic wrapper
            def basic_wrapper(context):
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return f(context)

            # app wrapper
            if enableInput:
                async def app_wrapper(interaction: Interaction, enter: str):
                    util.soup_log(f"[CMD] {name} {enter if not enter else enter.split()}")
                    return await f(Context.copy_from_interaction(interaction, enter))
            else:
                async def app_wrapper(interaction: Interaction):
                    util.soup_log(f"[CMD] {name}")
                    return await f(Context.copy_from_interaction(interaction, ""))

            if not self.categories.get(category):
                self.categories[category] = list()

            self.cmds[name] = basic_wrapper
            self.appCMDs[name] = app_commands.command(name=name, description=info)(app_wrapper)
            self.info[name] = info
            self.categories[category].append(name)

            return basic_wrapper

        return decorator
