import re as _re
import asyncio as _asyncio
import discord as _discord
import lavalink as _lavalink
from lavalink import events as _events
from math import ceil as _ceil

import command_management.commands as _commands
from soup_util import constants as _constants
from . import _lavalink_voice_protocol
from . import _ui_views


_url_rx = _re.compile(r"https?://(?:www\.)?.+")

_WAITING_TIME = 30

_FORCE_DISCONNECT = 4014
_RATE_LIMITED = 4021
_CALL_DELETED = 4022

_FIELD_LIMIT = 10


class CommandList(_commands.CommandList):

    name = "music commands"

    def __init__(self, *args):
        super().__init__(*args)

        self.lavalink = None

    async def on_start(self):
        if not hasattr(self.client, 'lavalink'):
            self.client.lavalink = _lavalink.Client(self.client.user.id)

            self.client.lavalink.add_node(
                host=_constants.NODE1_HOST,
                port=_constants.NODE1_PORT,
                password=_constants.NODE1_PASSWORD,
                region=_constants.NODE1_REGION,
                name=_constants.NODE1_NAME
            )
            self.client.lavalink.add_node(
                host=_constants.NODE2_HOST,
                port=_constants.NODE2_PORT,
                password=_constants.NODE2_PASSWORD,
                region=_constants.NODE2_REGION,
                name=_constants.NODE2_NAME
            )

        self.lavalink = self.client.lavalink
        self.lavalink.add_event_hook(self._on_track_start, event=_events.TrackStartEvent)
        self.lavalink.add_event_hook(self._on_queue_end, event=_events.QueueEndEvent)

    @_lavalink.listener(_events.TrackStartEvent)
    async def _on_track_start(self, event: _events.TrackStartEvent):
        guild = self.client.get_guild(event.player.guild_id)

        if not guild:
            await self.lavalink.player_manager.destroy(event.player.guild_id)
            return

        channel = guild.get_channel(event.player.fetch("text-channel"))

        if channel:
            embed = _discord.Embed(
                colour=_discord.Colour.dark_gold(),
                title=event.track.title[:_ui_views.TITLE_CHAR_LIMIT],
                description=event.track.author[:_ui_views.VALUE_CHAR_LIMIT]
            )
            embed.set_thumbnail(url=event.track.artwork_url)

            await channel.send(f"Now playing...", embed=embed)

    @_lavalink.listener(_events.QueueEndEvent)
    async def _on_queue_end(self, event: _events.QueueEndEvent):
        guild = self.client.get_guild(event.player.guild_id)

        await _asyncio.sleep(_WAITING_TIME)

        if not event.player.is_playing and guild is not None:
            await guild.voice_client.disconnect(force=True)

    @staticmethod
    def _reset_player(player):
        player.set_shuffle(False)
        player.set_loop(0)

    @staticmethod
    async def _create_player(context):
        if context.guild is None:
            raise _commands.CommandError("This command must be used in a server.")

        return context.bot.lavalink.player_manager.create(context.guild.id)

    @staticmethod
    async def _connect_to_voice(player, context):
        if not context.author.voice or not context.author.voice.channel:
            raise _commands.CommandError("You must join a voice channel to use this command.")

        if context.guild.voice_client is None:
            CommandList._reset_player(player)

            permissions = context.author.voice.channel.permissions_for(context.guild.me)

            if not permissions.connect or not permissions.speak:
                raise _commands.CommandError("The bot needs `CONNECT` and `SPEAK` permissions.")

            player.store("text-channel", context.channel.id)
            await context.author.voice.channel.connect(cls=_lavalink_voice_protocol.LavalinkVoiceClient)

    @_commands.command("join", desc="Makes the bot join your voice channel")
    async def join(self, context):
        player = await self._create_player(context)
        await self._connect_to_voice(player, context)

        await context.confirm()

    @_commands.command("leave", desc="Makes the bot leave its voice channel")
    async def leave(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            raise _commands.CommandError("Bot is not in a voice channel.")

        player = await self._create_player(context)

        player.queue.clear()
        await player.stop()

        await context.guild.voice_client.disconnect(force=False)
        await context.confirm()

    @_commands.command("play", desc="Plays music. Supports youtube/spotify/apple/soundcloud links or keyword searches")
    async def play(self, context, media: str):
        player = await self._create_player(context)
        await self._connect_to_voice(player, context)
        await context.defer_message()

        if not _url_rx.match(media):
            media = f"ytsearch:{media}"

        result = await player.node.get_tracks(media)

        if result.load_type == _lavalink.LoadType.EMPTY:
            raise _commands.CommandError("No tracks found.")
        elif result.load_type == _lavalink.LoadType.PLAYLIST:
            for track in result.tracks:
                track.extra["requester"] = context.author.id
                player.add(track=track)
        else:
            result.tracks[0].extra["requester"] = context.author.id
            player.add(track=result.tracks[0])

        if not player.is_playing:
            await player.play()

        await context.confirm()

    @_commands.command("shuffle", desc="Toggles on/off queue shuffle")
    async def shuffle(self, context):
        player = await self._create_player(context)

        if not player.is_playing:
            raise _commands.CommandError("No track is currently playing.")

        shuffle = not player.shuffle

        player.set_shuffle(shuffle)
        await context.send_message(f"Shuffle {'on' if shuffle else 'off'}.")

    @_commands.command("loop-queue", desc="Toggles on/off queue loop")
    async def loop_queue(self, context):
        player = await self._create_player(context)

        if not player.is_playing:
            raise _commands.CommandError("No track is currently playing.")

        # 0 - off
        # 1 - single track
        # 2 - queue
        loop = 2 if not player.loop == 2 else 0

        player.set_loop(loop)
        await context.send_message(f"Queue looping {'on' if loop == 2 else 'off'}.")

    @_commands.command("loop-track", desc="Toggles on/off single track loop")
    async def loop_track(self, context):
        player = await self._create_player(context)

        if not player.is_playing:
            raise _commands.CommandError("No track is currently playing.")

        loop = 1 if not player.loop == 1 else 0

        player.set_loop(loop)
        await context.send_message(f"Track looping {'on' if loop == 1 else 'off'}.")

    @_commands.command("pause", desc="Pause the current track")
    async def pause(self, context):
        player = await self._create_player(context)

        if not player.is_playing:
            raise _commands.CommandError("No track is currently playing.")
        elif player.paused:
            raise _commands.CommandError("The track is already paused.")

        await player.set_pause(True)
        await context.confirm()

    @_commands.command("resume", desc="Resume the current track")
    async def resume(self, context):
        player = await self._create_player(context)

        if not player.is_playing:
            raise _commands.CommandError("No track is currently playing.")
        elif not player.paused:
            raise _commands.CommandError("The track is already playing.")

        await player.set_pause(False)
        await context.confirm()

    @_commands.command("skip", desc="Skip the current track")
    async def skip(self, context):
        player = await self._create_player(context)

        if not player.is_playing:
            raise _commands.CommandError("No track is currently playing.")

        await player.skip()
        await context.confirm()

    @_commands.command("queue", desc="Displays the queue")
    async def queue(self, context):
        player = await self._create_player(context)

        if not player.is_playing:
            raise _commands.CommandError("No track is currently playing.")
        elif len(player.queue) == 0:
            raise _commands.CommandError("The queue is empty.")

        tracks = [track for track in player.queue]
        embeds = []
        total_pages = _ceil(len(tracks) / _FIELD_LIMIT)

        for i in range(total_pages):
            embeds.append(_discord.Embed(colour=_discord.Colour.dark_gold(), title=f"Queue [{i+1}/{total_pages}]"))
            embeds[i].set_image(url=_constants.EMBED_TRANSPARENT_IMAGE_URL)

            for _ in range(len(tracks) if len(tracks) < _FIELD_LIMIT else _FIELD_LIMIT):
                track = tracks.pop(0)

                embeds[i].add_field(
                    name=track.title[:_ui_views.TITLE_CHAR_LIMIT],
                    value=f"-# {track.author}"[:_ui_views.VALUE_CHAR_LIMIT],
                    inline=False
                )

        if total_pages > 1:
            await context.send_message("", embed=embeds[0], view=_ui_views.PagedEmbedView(embeds))
        else:
            await context.send_message("", embed=embeds[0])
