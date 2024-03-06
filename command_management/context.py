from discord import Interaction, Message, Client


class Context:
    """A wrapper for the data a method defining a bot command is passed when executing a command."""

    def __init__(self, message_content:str, message:Message=None, interaction:Interaction=None, bot:Client=None):
        if interaction is None:
            self._interaction = None
            self._message = message
            self._deferred = False
            self.is_basic_command = True
            self.bot = bot
            self.args = message_content.split()
            self.content = message_content
            self.channel = message.channel
            self.author = message.author
            self.guild = message.guild
            self.mentions = message.mentions
        else:
            self._interaction = interaction
            self._message = None
            self._deferred = False
            self.is_basic_command = False
            self.bot = interaction.client
            self.args = message_content.split()
            self.content = message_content
            self.channel = interaction.channel
            self.author = interaction.user
            self.guild = interaction.guild
            self.mentions = []
            if "resolved" in interaction.data.keys():
                self.mentions = [self.guild.get_member(int(i)) for i in interaction.data["resolved"]["users"].keys()]

    async def defer_message(self):
        """Use near the start of the method if the time required to produce a message is longer than 3 seconds. Does
        nothing if the command sent was basic."""

        if not self.is_basic_command:
            await self._interaction.response.defer()
            self._deferred = True

    async def send_message(self, text:str):
        """Send the user a message. Returns the message object. Can only call once per command."""

        if self.is_basic_command:
            return await self.channel.send(text)
        elif self._deferred:
            await self._interaction.followup.send(text)
        else:
            await self._interaction.response.send_message(text)
        return await self._interaction.original_response()

    async def confirm(self):
        """Give the user a confirmation that the command was a success. Sends a message if the user sent an app command,
        otherwise just reacts to the message."""

        if self.is_basic_command:
            await self._message.add_reaction("✅")
            return

        if self._deferred:
            await self._interaction.followup.send("✅")
        else:
            await self._interaction.response.send_message("✅")