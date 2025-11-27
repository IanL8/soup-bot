from time import time as _time
import asyncio as _asyncio
import discord as _discord

import command_management.commands as _commands
import database.database_management.db_timers as _db_timers


class CommandList(_commands.CommandList):

    name = "time commands"

    async def on_start(self):
        timers = _db_timers.get_all()

        for timer in timers:
            channel = self.client.get_channel(timer["channel_id"])
            _asyncio.run_coroutine_threadsafe(
                _timer(timer["uid"], timer["name"], channel, timer["end_time"] - _time(), timer["timer_id"]),
                self.client.loop
            )

    @_commands.command("timer", desc="Start a timer with a duration in [seconds, minutes, hours, days]")
    async def timer(self, context, duration: str, name: str = ""):

        duration_seconds = _duration_str_to_seconds(duration.lower())

        if duration_seconds <= 0:
            raise _commands.CommandError("Timer duration must be greater than 0.")
        elif len(name) > 200:
            raise _commands.CommandError(f"Timer name is {len(name) - 200} characters too long.")

        can_use_channel = context.channel.permissions_for(context.guild.get_member(context.bot.user.id)).send_messages

        if not can_use_channel:
            channels = _gather_usable_channels(
                context.guild.get_member(context.bot.user.id),
                context.guild.get_member(context.author.id),
                context.guild.text_channels
            )

            if len(channels) == 0:
                raise _commands.CommandError("No available channels allow the bot to send messages.")

            await context.send_message(
                "The bot cannot send messages in this channel. Please select a channel to be notified in.",
                view=_ChannelSelectorView(channels, duration_seconds, name),
                ephemeral=True
            )

        else:
            timer_id = _db_timers.add(context.author.id, context.guild.id, name, context.channel.id, int(_time()) + duration_seconds)
            _asyncio.run_coroutine_threadsafe(
                _timer(context.author.id, name, context.channel, duration_seconds, timer_id),
                context.bot.loop
            )

            await context.send_message(f"Timer {f'**{name}** started.' if len(name) != 0 else 'started.'}")

class _ChannelSelectorView(_discord.ui.View):
    def __init__(self, channels, duration, name, timeout=180):
        super().__init__(timeout=timeout)

        self.add_item(_ChannelSelector(channels, duration, name))

class _ChannelSelector(_discord.ui.Select):
    def __init__(self, channels, duration, name):

        self.channels = {f"{i+1}. {c.name}" : c for i, c in enumerate(channels)}
        self.duration = duration
        self.name = name

        options = [_discord.SelectOption(label=label) for label in self.channels.keys()]

        super().__init__(placeholder="Select a channel", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: _discord.Interaction):
        channel = self.channels[self.values[0]]

        await interaction.response.edit_message(content=f"**{channel.name}** selected", view=None)

        timer_id = _db_timers.add(interaction.user.id, interaction.guild.id, self.name, channel.id, int(_time()) + self.duration)
        _asyncio.run_coroutine_threadsafe(
            _timer(interaction.user.id, self.name, channel, self.duration, timer_id),
            interaction.client.loop
        )

        await interaction.followup.send(f"Timer {f'**{self.name}** started.' if len(self.name) != 0 else 'started.'}")


def _duration_str_to_seconds(text):
    current_number = ""
    total_seconds = 0

    if not any(c.isalpha() for c in text):
        text += "m"

    for character in text:
        if character.isdigit():
            current_number += character
            continue
        elif not character.isalpha() or current_number == "":
            continue

        match character:
            case "s":
                total_seconds += int(current_number)
                current_number = ""
            case "m":
                total_seconds += 60 * int(current_number)
                current_number = ""
            case "h":
                total_seconds += 3600 * int(current_number)
                current_number = ""
            case "d":
                total_seconds += 86400 * int(current_number)
                current_number = ""

    return total_seconds

def _gather_usable_channels(mem1, mem2, text_channels):
    channels = []

    for channel in text_channels:
        if channel.permissions_for(mem1).send_messages and channel.permissions_for(mem1).view_channel \
                and channel.permissions_for(mem2).send_messages and channel.permissions_for(mem2).view_channel:
            channels.append(channel)

    return channels

async def _timer(uid, name, channel, duration, timer_id):
    if duration > 0:
        await _asyncio.sleep(duration)

    await channel.send(f"{name} <@{uid}>")
    _db_timers.remove(timer_id)
