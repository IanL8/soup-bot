from discord import Interaction as _Interaction
from discord import app_commands as _app_commands
from functools import reduce as _reduce
import inspect as _inspect

from soup_util.soup_logging import logger as _logger


class CommandError(Exception):

    def __init__(self, message):
        super().__init__(message)

        self.message = message

    def __str__(self):
        return self.message


class Context:
    """Mainly a wrapper for data a command is passed, but has some methods."""

    def __init__(self, interaction: _Interaction = None):
        self._interaction = interaction
        self._deferred = False
        self.bot = interaction.client
        self.channel = interaction.channel
        self.author = interaction.user
        self.guild = interaction.guild
        self.mentions = []

        if "resolved" in interaction.data.keys():
            self.mentions = [self.guild.get_member(int(i)) for i in interaction.data["resolved"]["users"].keys()]

    async def defer_message(self):
        """Use near the start of the method if the time required to produce a message is longer than 3 seconds."""

        await self._interaction.response.defer()
        self._deferred = True

    async def send_message(self, text: str, **args):
        """Sends the user a message. Returns the message object. Can only call once per command."""

        if self._deferred:
            await self._interaction.followup.send(text, **args)
        else:
            await self._interaction.response.send_message(text, **args)

        return await self._interaction.original_response()

    async def confirm(self):
        """Gives the user a confirmation that the command was a success."""

        if self._deferred:
            await self._interaction.followup.send("✅")
        else:
            await self._interaction.response.send_message("✅")


class _CommandDataWrapper:
    def __init__(self, name: str, desc: str, autocomplete_fields: {str: list[str]},
                 dynamic_autocomplete: {str: callable}, partial_signature: str, parameters: str):

        self.name = name
        self.desc = desc
        self.autocomplete_fields = autocomplete_fields
        self.dynamic_autocomplete = dynamic_autocomplete
        self.partial_signature = partial_signature
        self.parameters = parameters

_all_commands: {callable: _CommandDataWrapper} = dict()


def command(name:str, desc: str="...", autocomplete_fields: {str: list[str]} = None, dynamic_autocomplete: {str: callable} = None):
    """Decorator for methods defining a discord bot command. Command must have the parameter 'context', be asynchronous, and
    be an instance method to a subclass of 'CommandList' in order to work correctly. Any parameters after context will be
    given as fields for the command and must be given a type."""

    def decorator(f: callable):
        partial_signature = _reduce(lambda x, y: f"{x}, {y}", str(_inspect.signature(f))[1:-1].split(",")[2:] + [""])
        parameters = _reduce(lambda x, y: f"{x}, {y}", _inspect.getfullargspec(f).args[2:] + [""])

        _all_commands[f] = _CommandDataWrapper(name, desc, autocomplete_fields, dynamic_autocomplete, partial_signature, parameters)
        return f

    return decorator


class CommandList:
    """Subclass this to create groups of similar discord commands."""

    name: str = "default"

    def __init__(self, client):
        self.app_commands: [callable] = []
        self.client = client

        for value in self.__class__.__dict__.values():
            if value in _all_commands.keys():
                self.app_commands.append(self._generate_app_command(_all_commands.pop(value), value))

    def _generate_app_command(self, command_data, function):
        scope = dict(locals().copy(), **globals().copy())

        exec(
            f"@_app_commands.command(name=command_data.name, description=command_data.desc[:100])\n"
            f"async def app_wrapper(interaction: _Interaction, {command_data.partial_signature}):\n"
            f"    args = [{command_data.parameters}]\n"
            f"    context = Context(interaction=interaction)\n"
            f"    _logger.info('%s %s',command_data.name, '' if len(args) == 0 else str(args))\n"
            f"    try:\n"
            f"        await function(self, context, {command_data.parameters})\n"
            f"    except CommandError as err:\n"
            f"        await self.error_handler(context, err)\n"
            f"    except Exception as e:\n"
            f"        _logger.warning(str(e), exc_info=True)\n"
            f"        await context.send_message('Oh no! **' + self.client.user.name + '** has ran into an error :(')\n",
            scope
        )

        if command_data.autocomplete_fields is not None:
            for field_name, choices in command_data.autocomplete_fields.items():
                scope["field_name"] = field_name
                scope["choices"] = choices
                exec(
                    f"@app_wrapper.autocomplete(field_name)\n"
                    f"async def field_name_autocomplete(interaction: _Interaction, current: str) -> list[_app_commands.Choice[str]]:\n"
                    f"    return [_app_commands.Choice(name=c, value=c) for c in choices if current.lower() in c.lower()][:25]\n",
                    scope
                )
        if command_data.dynamic_autocomplete is not None:
            for field_name, autocomplete_function in command_data.dynamic_autocomplete.items():
                scope["field_name"] = field_name
                scope["autocomplete_function"] = autocomplete_function
                exec(
                    f"@app_wrapper.autocomplete(field_name)\n"
                    f"async def field_name_autocomplete(interaction: _Interaction, current: str) -> list[_app_commands.Choice[str]]:\n"
                    f"    return [_app_commands.Choice(name=c, value=c) for c in await autocomplete_function(current)][:25]\n",
                    scope
                )

        return scope["app_wrapper"]

    async def on_start(self):
        pass

    async def on_close(self):
        pass

    async def error_handler(self, context: Context, error: CommandError):
        await context.send_message(str(error))
