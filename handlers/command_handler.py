#
# imports
from discord import app_commands
from discord import Interaction

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
        self.bot = None

    def set_bot(self, bot):
        self.bot = bot

    def is_command(self, c):
        return c in self.cmds.keys()

    def list_commands(self):
        return self.cmds.keys()

    def pass_command(self, c, context):
        return self.cmds[c](context)

    def command(self, name: str, info: str = "...", category: str = "general"):

        def decorator(f: callable):

            async def basic_wrapper(context):
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return await f(context)


            #
            # created to be added to app command tree
            @app_commands.command(name=name, description=info)
            async def app_wrapper(interaction: Interaction, *kwargs):
                context = Context.copy_from_interaction(interaction)
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return await f(context, kwargs)

            if not self.categories.get(category):
                self.categories[category] = list()

            self.cmds[name] = basic_wrapper
            self.appCMDs[name] = app_wrapper
            self.info[name] = info
            self.categories[category].append(name)

            return basic_wrapper

        return decorator
