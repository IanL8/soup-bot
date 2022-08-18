#
# project imports
import soupbot_utilities as util

#
# command handler
class CommandHandler:

    def __init__(self):
        self.cmds = dict()          # cmd name -> function pointer
        self.info = dict()          # cmd name -> info
        self.categories = dict()    # category -> list of cmd names

    def is_command(self, c):
        return c in self.cmds.keys()

    def list_commands(self):
        return self.cmds.keys()

    def pass_command(self, c, context):
        return self.cmds[c](context)

    def command(self, name: str, info: str = "", category: str = "general"):

        def decorator(f: callable):

            def wrapper(context):
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return f(context)

            if not self.categories.get(category):
                self.categories[category] = list()

            self.cmds[name] = wrapper
            self.info[name] = info
            self.categories[category].append(name)

            return wrapper

        return decorator
