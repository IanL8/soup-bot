#
# context
class Context:
    # init
    def __init__(self, message=None, channel=None, author=None, guild=None, voice_client=None, bot=None, args=None):
        self.basic          = True # basic cmd: True, app cmd: False
        self.interaction    = None
        self.message        = message
        self.channel        = channel
        self.author         = author
        self.guild          = guild
        self.voice_client   = voice_client
        self.bot            = bot
        self.args           = args

    @staticmethod
    def copy_from_interaction(interaction):
        self = Context()
        self.basic          = False
        self.interaction    = interaction
        self.message        = interaction.message
        self.channel        = interaction.channel
        self.author         = interaction.user
        self.guild          = interaction.guild
        self.voice_client   = interaction.guild.voice_client
        self.bot            = interaction.client
        self.args           = None

        return self

    async def send_message(self, s):
        if self.basic:
            msg = await self.channel.send(s)
        else:
            await self.interaction.response.send_message(s)
            msg = await self.interaction.original_response()

        return msg

    async def confirm(self):
        if self.basic:
            await self.message.add_reaction("✅")
        else:
            await self.interaction.response.send_message("done ✅")
