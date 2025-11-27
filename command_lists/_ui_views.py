import discord as _discord


FIELD_LIMIT = 25
TITLE_CHAR_LIMIT = 256
VALUE_CHAR_LIMIT = 1024


class PagedEmbedView(_discord.ui.View):
    def __init__(self, embeds, timeout=600):
        super().__init__(timeout=timeout)

        self.embeds = embeds
        self.embed_index = 0

    @_discord.ui.button(label="<", style=_discord.ButtonStyle.grey)
    async def left_arrow_button(self, interaction: _discord.Interaction, button: _discord.ui.Button):
        self.embed_index = len(self.embeds) - 1 if self.embed_index == 0 else self.embed_index - 1
        await interaction.response.edit_message(embed=self.embeds[self.embed_index], view=self)

    @_discord.ui.button(label=">", style=_discord.ButtonStyle.grey)
    async def right_arrow_button(self, interaction: _discord.Interaction, button: _discord.ui.Button):
        self.embed_index = (self.embed_index + 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.embed_index], view=self)
