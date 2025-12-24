import discord as _discord


FIELD_LIMIT = 25
TITLE_CHAR_LIMIT = 256
VALUE_CHAR_LIMIT = 1024


class PagedEmbedView(_discord.ui.View):

    def __init__(self, embeds, timeout=600, row = None):
        super().__init__(timeout=timeout)

        self.embeds = embeds
        self.embed_index = 0

        self.add_item(_ArrowButton(
            "<",
            _discord.ButtonStyle.grey,
            lambda interaction: self.left_arrow_action(interaction),
            row=row
        ))
        self.add_item(_ArrowButton(
            ">",
            _discord.ButtonStyle.grey,
            lambda interaction: self.right_arrow_action(interaction),
            row=row
        ))

    def disable_items(self) -> None:
        for c in self.children:
            c.disabled = True

    async def left_arrow_action(self, interaction):
        self.embed_index = (self.embed_index - 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.embed_index])

    async def right_arrow_action(self, interaction):
        self.embed_index = (self.embed_index + 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.embed_index])

class _ArrowButton(_discord.ui.Button):

    def __init__(self, label, style, button_action, row=None):
        super().__init__(style=style, label=label, row=row)

        self.button_action = button_action

    async def callback(self, interaction: _discord.Interaction):
        await self.button_action(interaction)
