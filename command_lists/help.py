import discord as _discord
from math import ceil as _ceil

import command_management.commands as _commands
import soup_util.constants as _constants
from . import _ui_views


_FIELD_ROW_LIMIT = 10


class CommandList(_commands.CommandList):

    name = "Help"

    def __init__(self, *args):
        super().__init__(*args)

        self.embeds: {str: list[_discord.Embed]} = {}
        self.categories = []

    async def on_start(self):
        self.categories = [category for category in _commands.command_display_data.keys() if self.name != category]

        for category in self.categories:
            self.embeds[category] = list()

            cmds = _commands.command_display_data[category].copy()
            total_pages = _ceil(len(cmds) / _FIELD_ROW_LIMIT)

            for i in range(total_pages):
                self.embeds[category].append(
                    _discord.Embed(colour=_discord.Colour.green(), title=f"{category} [{i + 1}/{total_pages}]")
                )
                self.embeds[category][i].set_image(url=_constants.EMBED_TRANSPARENT_IMAGE_URL)

                for _ in range(len(cmds) if len(cmds) < _FIELD_ROW_LIMIT else _FIELD_ROW_LIMIT):
                    cmd = cmds.pop(0)

                    self.embeds[category][i].add_field(
                        name=cmd["name"][:_ui_views.VALUE_CHAR_LIMIT],
                        value=f"{cmd['description']}\n{'-# > / Command Only' if not cmd['basic_compatible'] else ''}",
                        inline=False
                    )

    @staticmethod
    async def _autocomplete(current):
        choices = [category for category in _commands.command_display_data.keys() if CommandList.name != category]
        return [c for c in choices if current.lower() in c.lower()]

    @_commands.command("help",
                       desc="Menu with descriptions for each command. Can optionally provide a starting category.",
                       dynamic_autocomplete={"category": _autocomplete})
    async def help(self, context, category: str = "General"):
        if category not in self.categories:
            raise _commands.CommandError("Invalid category.")

        view = _HelpMenuView(self.embeds, category, 1200)
        message = await context.send_message("", embed=self.embeds[category][0], view=view)

        await view.wait()
        view.disable_items()
        await message.edit(view=view)


class _HelpMenuView(_ui_views.PagedEmbedView):

    def __init__(self, commands_by_category, starting_category, timeout):
        super().__init__(commands_by_category[starting_category], timeout=timeout, row=1)

        self.commands_by_category = commands_by_category

        self.add_item(_CategorySelectView(commands_by_category.keys(), 0))

    def switch_category(self, category):
        self.embed_index = 0
        self.embeds = self.commands_by_category[category]

class _CategorySelectView(_discord.ui.Select):

    def __init__(self, categories, row):
        self.all_options = [_discord.SelectOption(label=label) for label in categories]

        super().__init__(placeholder="Select a Category", min_values=1, max_values=1, options=self.all_options, row=row)

    async def callback(self, interaction: _discord.Interaction):
        self.view.switch_category(self.values[0])

        await interaction.message.edit(embed=self.view.embeds[0])
        await interaction.response.defer()
