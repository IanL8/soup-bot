from discord import app_commands, Interaction
from abc import ABC, abstractmethod

from .context import Context
from soupbot_util.logger import soup_log


class _CommandInfo:
    def __init__(self, name:str, desc:str, enable_input:bool):
        self.name = name
        self.desc = desc
        self.enable_input = enable_input


_all_commands: {callable:_CommandInfo} = dict()


def command(name:str, desc:str="...", enable_input:bool=False):
    """Decorator for methods defining a discord bot command. Commands must take one arg 'context', be asynchronous, and
    be an instance method to a subclass of 'CommandList' in order to work correctly."""

    def decorator(f:callable):

        async def wrapper(*args):
            soup_log(f"{name} {args[1].content}", "cmd")
            return await f(*args)

        _all_commands[wrapper] = _CommandInfo(name, desc, enable_input)
        return wrapper

    return decorator


class CommandList(ABC):

    name: str = "default"

    def __init__(self):
        self._basic_commands: {str:callable} = dict()
        self.app_commands: [callable] = []
        for value in self.__class__.__dict__.values():
            if value in _all_commands.keys():
                cmd = _all_commands.pop(value)
                self._basic_commands[cmd.name] = value
                self.app_commands.append(self._app_command(cmd.name, cmd.desc, cmd.enable_input, value))

    def _app_command(self, name, desc, enable_input, f):
        if enable_input:
            async def app_wrapper(interaction: Interaction, enter: str = None):
                return await f(self, Context(enter, interaction=interaction))
        else:
            async def app_wrapper(interaction: Interaction):
                return await f(self, Context("", interaction=interaction))
        return app_commands.command(name=name, description=desc)(app_wrapper)

    async def __call__(self, command_name, context):
        if command_name not in self._basic_commands.keys():
            return None
        return await self._basic_commands[command_name](self, context)

    def __contains__(self, item):
        return item in self._basic_commands.keys()

    @abstractmethod
    def on_close(self):
        pass
