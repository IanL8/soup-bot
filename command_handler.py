
class CommandHandler:

    def __init__(self):
        self.cmds: dict = dict()

    def is_command(self, c):
        return c in self.cmds.keys()

    def list_commands(self):
        return self.cmds.keys()

    def pass_command(self, c, context, args):
        return self.cmds[c](context, args)

    def name(self, name: str):

        def decorator(f: callable):
            self.cmds[name] = f
            return f

        return decorator
