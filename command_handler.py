#
# project imports
import soupbot_utilities as util

#
# command handler
class CommandHandler:

    def __init__(self):
        self.cmds = dict()
        self.cmdInfo = dict()

    def is_command(self, c):
        return c in self.cmds.keys()

    def list_commands(self):
        return self.cmds.keys()

    def pass_command(self, c, context):
        return self.cmds[c](context)

    def command(self, name: str, info: str = ""):

        def decorator(f: callable):

            def wrapper(context):
                util.soup_log(f"[CMD] {name} {context.args if context.args else str()}")
                return f(context)

            self.cmds[name] = wrapper
            self.cmdInfo[name] = info

            return wrapper

        return decorator


commandHandler = CommandHandler()