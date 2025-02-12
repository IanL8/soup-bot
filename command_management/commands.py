from discord import app_commands, Interaction
from abc import ABC, abstractmethod
import inspect

from soupbot_util.logger import soup_log
from .context import Context


class _CommandDataWrapper:
    def __init__(self, name:str, desc:str, parameters:str, args:str):
        self.name = name
        self.desc = desc
        self.parameters = parameters
        self.args = args


_all_commands: {callable:_CommandDataWrapper} = dict()


def command(name:str, desc:str="..."):
    """Decorator for methods defining a discord bot command. Command must have the parameter 'context', be asynchronous, and
    be an instance method to a subclass of 'CommandList' in order to work correctly. Any parameters after context will be
    given as fields for the command and must be given a type."""

    def decorator(f:callable):

        parameters = str(inspect.signature(f))
        parameters = parameters[parameters.index("context") + 8:-1].strip()

        args = str(inspect.getfullargspec(f).args)
        args = args[args.index("'context'") + 10:-1].replace("'", "").strip()

        _all_commands[f] = _CommandDataWrapper(name, desc, parameters, args)
        return f

    return decorator


class CommandList(ABC):

    name: str = "default"

    def __init__(self):
        self.app_commands: [callable] = []

        for value in self.__class__.__dict__.values():
            if value in _all_commands.keys():
                cmd = _all_commands.pop(value)

                self.app_commands.append(self._generate_app_command(cmd.name, cmd.desc, cmd.parameters, cmd.args, value))

    def _generate_app_command(self, name, desc, parameters, args, function):
        cmd_name_llll = name # avoid variable name overlap with variables in parameter/args strings
        scope = dict(locals().copy(), **globals().copy())

        exec(
            f"async def app_wrapper(interaction:Interaction, {parameters}): "
                f"soup_log(cmd_name_llll + ' ' + str(({args})), 'cmd');"
                f"return await function(self, Context(interaction=interaction), {args});",
            scope
        )

        return app_commands.command(name=name, description=desc[:100])(scope["app_wrapper"])

    @abstractmethod
    def on_close(self):
        pass
