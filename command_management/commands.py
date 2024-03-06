import types
from discord import app_commands, Interaction
from abc import ABC, abstractmethod

from .context import Context
from soupbot_util.logger import soup_log


class Commands:

    def __init__(self):
        self.basic : {str:types.FunctionType} = dict()
        self.app : [types.FunctionType] = []
        self.command_list_instance : CommandList = None

    def set_command_list_instance(self, instance):
        self.command_list_instance = instance

    def command(self, name:str, info:str="...", enable_input:bool=False):
        """Decorator for methods defining a discord bot command."""

        def decorator(f: callable):
            # basic command wrapper
            async def basic_wrapper(context):
                soup_log(f"{name} {context.content}", "cmd")
                return await f(self=self.command_list_instance, context=context)
            # app command wrapper
            if enable_input:
                async def app_wrapper(interaction:Interaction, enter:str=None):
                    soup_log(f"{name} {enter}", "cmd")
                    return await f(self=self.command_list_instance, context=Context(enter, interaction=interaction))
            else:
                async def app_wrapper(interaction:Interaction):
                    soup_log(f"[CMD] {name}", "cmd")
                    return await f(
                        self=self.command_list_instance,
                        context=Context("", interaction=interaction)
                    )
            self.basic[name] = basic_wrapper
            self.app.append(app_commands.command(name=name, description=info)(app_wrapper))

            return basic_wrapper
        return decorator

class CommandList(ABC):
    """All commands created for the discord bot must be within a subclass of CommandList and use the command
    decorator from Commands."""

    name: str = "default"
    commands : Commands # each list subclass needs to make its own instance of Commands

    def __init__(self):
        self.commands.set_command_list_instance(self)

    # enforce that commands is overwritten by each  subclass
    def __init_subclass__(cls, **kwargs):
        if not any("commands" in subclass.__dict__ for subclass in cls.__mro__ if subclass is not CommandList):
            raise NotImplementedError("Need to overwrite class attribute 'commands' in order to subclass CommandList.")

    @abstractmethod
    def on_close(self):
        pass
