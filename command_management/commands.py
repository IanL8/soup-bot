from discord import Interaction as _Interaction
from discord import app_commands as _app_commands
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
import inspect as _inspect

from .context import Context as _Context
from soup_util import soup_logging as _soup_logging


_logger = _soup_logging.get_logger()


class _CommandDataWrapper:
    def __init__(self, name:str, desc:str, autocomplete_fields:{str:list[str]}, parameters:str, args:str):
        self.name = name
        self.desc = desc
        self.autocomplete_fields = autocomplete_fields
        self.parameters = parameters
        self.args = args


_all_commands: {callable:_CommandDataWrapper} = dict()


def command(name:str, desc:str="...", autocomplete_fields:{str:list[str]}= None):
    """Decorator for methods defining a discord bot command. Command must have the parameter 'context', be asynchronous, and
    be an instance method to a subclass of 'CommandList' in order to work correctly. Any parameters after context will be
    given as fields for the command and must be given a type."""

    def decorator(f:callable):

        parameters = str(_inspect.signature(f))
        parameters = parameters[parameters.index("context") + 8:-1].strip()

        args = str(_inspect.getfullargspec(f).args)
        args = args[args.index("'context'") + 10:-1].replace("'", "").strip()

        _all_commands[f] = _CommandDataWrapper(name, desc, autocomplete_fields, parameters, args)
        return f

    return decorator


class CommandList(_ABC):

    name: str = "default"

    def __init__(self, client):
        self.app_commands: [callable] = []
        self.client = client

        for value in self.__class__.__dict__.values():
            if value in _all_commands.keys():
                command_data = _all_commands.pop(value)

                self.app_commands.append(self._generate_app_command(command_data, value))

    def _generate_app_command(self, command_data, function):
        scope = dict(locals().copy(), **globals().copy())

        exec(
            f"@_app_commands.command(name=command_data.name, description=command_data.desc[:100])\n"
            f"async def app_wrapper(interaction:_Interaction, {command_data.parameters}): "
            f"args = [{command_data.args}];"
            f"_logger.info('%s %s',command_data.name, '' if len(args) == 0 else str(args));"
            f"return await function(self, _Context(interaction=interaction), {command_data.args});",
            scope
        )

        if command_data.autocomplete_fields is not None:
            for field_name, choices in command_data.autocomplete_fields.items():
                scope["field_name"] = field_name
                scope["choices"] = choices
                exec(
                    f"@app_wrapper.autocomplete(field_name)\n"
                    f"async def field_name_autocomplete(interaction:_Interaction, current:str) -> list[_app_commands.Choice[str]]: "
                    f"return [_app_commands.Choice(name=c, value=c) for c in choices if current.lower() in c.lower()][:25]",
                    scope
                )

        return scope["app_wrapper"]

    @_abstractmethod
    async def on_start(self):
        pass

    @_abstractmethod
    async def on_close(self):
        pass
