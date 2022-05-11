
class CmdHandler:

    def __init__(self):
        self.cmds: dict = dict()

    def is_cmd(self, c):
        if c in self.cmds.keys():
            return True
        return False

    def list_all_cmds(self):
        return self.cmds.keys()

    def pass_cmd(self, c, context, args):
        return self.cmds[c](context, args)

    def name(self, name):

        def decorator(f):
            self.cmds[name] = f
            return f

        return decorator
