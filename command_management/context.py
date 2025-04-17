from discord import Interaction
import functools
import typing


class Context:
    """A class defining the data a method containing a bot command is passed."""

    def __init__(self, interaction:Interaction=None):
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

    async def run_blocking_func(self, func: typing.Callable, *args, **kwargs):
        """Use on all long blocking functions to avoid locking up the main thread the bot runs on. Returns the result."""

        return await self.bot.loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

    async def send_message(self, text:str):
        """Send the user a message. Returns the message object. Can only call once per command."""

        if self._deferred:
            await self._interaction.followup.send(text)
        else:
            await self._interaction.response.send_message(text)

        return await self._interaction.original_response()

    async def confirm(self):
        """Give the user a confirmation that the command was a success."""

        if self._deferred:
            await self._interaction.followup.send("✅")
        else:
            await self._interaction.response.send_message("✅")
