#
# project imports
import soupbot_utilities as util

#
# command handler
class CommandHandler:

    def __init__(self):
        self.cmds: dict = dict()

    def is_command(self, c):
        return c in self.cmds.keys()

    def list_commands(self):
        return self.cmds.keys()

    def pass_command(self, c, context):
        return self.cmds[c](context)

    def command(self, name: str):

        def decorator(f: callable):

            def wrapper(context):
                util.soup_log("[CMD] {} on {}".format(name, context.args))
                return f(context)

            self.cmds[name] = wrapper

            return wrapper

        return decorator
