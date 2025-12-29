from typing import final as _final
from functools import reduce as _reduce
import discord as _discord
import inspect as _inspect

from soup_util.soup_logging import logger as _logger


_AUTOCOMPLETE_NAME_CHAR_LIMIT = 100
_AUTOCOMPLETE_LIMIT = 25

_DEFAULT_COMMAND_LIST_NAME = "default"

command_display_data = {}


class CommandError(Exception):

    def __init__(self, message):
        super().__init__(message)

        self.message = message

    def __str__(self):
        return self.message

class _CommandGenerationError(Exception):

    def __init__(self, message):
        super().__init__(message)

        self.message = message

    def __str__(self):
        return self.message


class Context:
    """Mainly a wrapper for data a command is passed, but has some methods."""

    def __init__(self, message: _discord.Message = None, interaction: _discord.Interaction = None,
                 client: _discord.Client = None):
        if message is None:
            self._interaction = interaction
            self._message = None
            self._deferred = False
            self._is_basic_command = False
            self.bot = interaction.client
            self.channel = interaction.channel
            self.author = interaction.user
            self.guild = interaction.guild
            self.mentions = []

            if "resolved" in interaction.data:
                if "members" in interaction.data["resolved"]:
                    self.mentions = [self.guild.get_member(int(i)) for i in interaction.data["resolved"]["members"].keys()]
                elif "users" in interaction.data["resolved"]:
                    self.mentions = [self.bot.get_user(int(i)) for i in interaction.data["resolved"]["users"].keys()]
        else:
            self._interaction = None
            self._message = message
            self._deferred = False
            self._is_basic_command = True
            self.bot = client
            self.channel = message.channel
            self.author = message.author
            self.guild = message.guild
            self.mentions = []

        self._sent_message = None

    async def defer_message(self):
        """Use near the start of the method if the time required to produce a message is longer than 3 seconds. Does
        nothing if the command sent was basic."""

        if not self._is_basic_command:
            await self._interaction.response.defer()
            self._deferred = True

    async def send_message(self, text: str, **args):
        """Sends the user a message. Returns the message object. Only call once per command."""

        if self._is_basic_command:
            self._sent_message = await self.channel.send(text, **args)
            return self._sent_message
        elif self._deferred:
            await self._interaction.followup.send(text, **args)
        else:
            await self._interaction.response.send_message(text, **args)

        self._sent_message = await self._interaction.original_response()
        return self._sent_message

    async def edit_message(self, **args):
        """Edits the message sent to the user, with keyword arguments supported by discord.Message.edit(). If used
        before sending a message, does nothing."""

        if not self._sent_message:
            return

        if self._is_basic_command:
            await self._sent_message.edit(**args)
        else:
            raw_message = await self._sent_message.fetch()
            await raw_message.edit(**args)

    async def confirm(self):
        """Gives the user a confirmation that the command was a success. Sends a message if the user sent an app
        command, otherwise just reacts to the message."""

        if self._is_basic_command:
            await self._message.add_reaction("✅")
        elif self._deferred:
            await self._interaction.followup.send("✅")
        else:
            await self._interaction.response.send_message("✅")


class _CommandTempDataWrapper:

    def __init__(self, name: str, desc: str, autocomplete_fields: {str: list[str]},
                 dynamic_autocomplete: {str: callable}, partial_signature: str, parameters: str):
        self.name = name
        self.desc = desc
        self.autocomplete_fields = autocomplete_fields
        self.dynamic_autocomplete = dynamic_autocomplete
        self.partial_signature = partial_signature
        self.parameters = parameters

        self.basic_compatible = len(parameters) == 0 or len(partial_signature.split(",")) - 1 == partial_signature.count("=")


_all_commands: {callable: _CommandTempDataWrapper} = dict()


def command(name: str, desc: str="...", autocomplete_fields: {str: list[str]} = None, dynamic_autocomplete: {str: callable} = None):
    """Decorator for methods defining a discord bot command. Command must have the parameter 'context', be asynchronous, and
    be an instance method to a subclass of 'CommandList' in order to work correctly. Any parameters after context will be
    given as fields for the command and must be given a type."""

    def decorator(f: callable):
        partial_signature = _reduce(lambda x, y: f"{x}, {y}", str(_inspect.signature(f))[1:-1].split(",")[2:] + [""])
        parameters = _reduce(lambda x, y: f"{x}, {y}", _inspect.getfullargspec(f).args[2:] + [""])

        if any(value.name == name for value in _all_commands.values()):
            raise _CommandGenerationError(f"Multiple commands exist with the same name, '{name}'.")

        _all_commands[f] = _CommandTempDataWrapper(name, desc, autocomplete_fields, dynamic_autocomplete, partial_signature, parameters)
        return f

    return decorator


class _Command:

    def __init__(self, name, desc, basic_compatible, app_command, basic_command):
        self.name = name
        self.desc = desc
        self.basic_compatible = basic_compatible
        self.app_command = app_command
        self.basic_command = basic_command


class CommandList:
    """Subclass this to create groups of similar discord commands."""

    name: str = _DEFAULT_COMMAND_LIST_NAME

    def __init__(self, client):
        self.client = client
        self.commands: list[_Command] = []

        if any(key == self.name for key in command_display_data.keys()):
            raise _CommandGenerationError(f"Multiple commands lists exist with the same name, '{self.name}'.")

        if self.name == _DEFAULT_COMMAND_LIST_NAME:
            _logger.warn(f"A command list with the default name exists. Consider giving it a descriptive name.")

        command_display_data[self.name] = []

        for value in self.__class__.__dict__.values():
            if value in _all_commands.keys():
                cmd = _all_commands.pop(value)

                command_display_data[self.name].append(
                    {"name": cmd.name, "description": cmd.desc, "basic_compatible": cmd.basic_compatible}
                )

                self.commands.append(_Command(
                    cmd.name,
                    cmd.desc,
                    cmd.basic_compatible,
                    self._generate_app_command(cmd, value),
                    None if not cmd.basic_compatible else self._generate_basic_command(cmd.name, value)
                ))

    @_final
    def _generate_basic_command(self, name, function):
        async def basic_command(context):
            _logger.info("%s", name)
            try:
                await function(self, context)
            except CommandError as err:
                await self.error_handler(context, err)
            except Exception as e:
                _logger.error(str(e), exc_info=True)
                await context.send_message('Oh no! **' + self.client.user.name + '** has ran into an error :(')

        return basic_command

    @_final
    def _generate_app_command(self, cmd, function):
        scope = dict(locals().copy(), **globals().copy())

        exec(
            f"@_discord.app_commands.command(name=cmd.name, description=cmd.desc[:100])\n"
            f"async def app_wrapper(interaction: _discord.Interaction, {cmd.partial_signature}):\n"
            f"    args = [{cmd.parameters}]\n"
            f"    context = Context(interaction=interaction)\n"
            f"    _logger.info('%s %s',cmd.name, '' if len(args) == 0 else str(args))\n"
            f"    try:\n"
            f"        await function(self, context, {cmd.parameters})\n"
            f"    except CommandError as err:\n"
            f"        await self.error_handler(context, err)\n"
            f"    except Exception as e:\n"
            f"        _logger.error(str(e), exc_info=True)\n"
            f"        await context.send_message('Oh no! **' + self.client.user.name + '** has ran into an error :(')\n",
            scope
        )

        if cmd.autocomplete_fields is not None:
            for field_name, choices in cmd.autocomplete_fields.items():
                scope["field_name"] = field_name
                scope["choices"] = choices
                exec(
                    f"@app_wrapper.autocomplete(field_name)\n"
                    f"async def field_name_autocomplete(interaction: _discord.Interaction, current: str) -> list[_discord.app_commands.Choice[str]]:\n"
                    f"    choices_temp = [c[:_AUTOCOMPLETE_NAME_CHAR_LIMIT] for c in choices if current.lower() in c.lower()]\n"
                    f"    return [_discord.app_commands.Choice(name=c, value=c) for c in choices_temp[:_AUTOCOMPLETE_LIMIT]]\n",
                    scope
                )
        if cmd.dynamic_autocomplete is not None:
            for field_name, autocomplete_function in cmd.dynamic_autocomplete.items():
                scope["field_name"] = field_name
                scope["autocomplete_function"] = autocomplete_function
                exec(
                    f"@app_wrapper.autocomplete(field_name)\n"
                    f"async def field_name_autocomplete(interaction: _discord.Interaction, current: str) -> list[_discord.app_commands.Choice[str]]:\n"
                    f"    choices = [c[:_AUTOCOMPLETE_NAME_CHAR_LIMIT] for c in await autocomplete_function(current)]\n"
                    f"    return [_discord.app_commands.Choice(name=c, value=c) for c in choices[:_AUTOCOMPLETE_LIMIT]]\n",
                    scope
                )

        return scope["app_wrapper"]

    @_final
    @property
    def app_commands(self) -> list[_discord.app_commands.AppCommand]:
        return [cmd.app_command for cmd in self.commands]

    @_final
    @property
    def basic_commands(self) -> {str: callable}:
        return {cmd.name: cmd.basic_command for cmd in self.commands if cmd.basic_compatible}

    async def on_start(self):
        pass

    async def on_close(self):
        pass

    async def error_handler(self, context: Context, error: CommandError):
        await context.send_message(str(error))
