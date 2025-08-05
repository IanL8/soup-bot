import threading as _threading
import asyncio as _asyncio
from math import ceil as _ceil
from async_timeout import timeout as _timeout

import command_management.commands as _commands
from . import _music_support


_sessions: {str: _music_support.Session} = dict()
_DISPLAY_LIMIT = 20


class CommandList(_commands.CommandList):

    name = "music commands"

    async def on_start(self):
        _threading.Thread(target=_music_support.background_streaming, args=(lambda: _sessions,), daemon=True).start()

    async def on_close(self):
        _sessions.clear()

    @_commands.command("join", desc="Makes the bot join your voice channel")
    async def join(self, context):
        if not context.author.voice:
            await context.send_message("user is not in a voice channel")
        else:
            await context.author.voice.channel.connect()
            await context.confirm()

    @_commands.command("leave", desc="Makes the bot leave its voice channel")
    async def leave(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")

        else:
            if context.guild.id in _sessions.keys():
                _sessions[context.guild.id].end()
                _sessions.pop(context.guild.id)

            await context.guild.voice_client.disconnect(force=False)
            await context.confirm()

    @_commands.command("play", desc="Plays audio from a yt/spotify url, or from a given song name in the voice channel")
    async def play(self, context, media: str):
        in_vc = True

        if not context.guild.voice_client in context.bot.voice_clients:
            in_vc = False

            if not context.author.voice:
                await context.send_message("user is not in a voice channel")
                return

        await context.defer_message()

        if context.guild.id not in _sessions.keys():
            _sessions[context.guild.id] = _music_support.Session()

        tracks = _music_support.gather_tracks(media)
        if not tracks:
            await context.send_message("no tracks could be found from url")
            return

        elif not _sessions[context.guild.id].playing:
            track = tracks.pop(0)

            if not await _asyncio.to_thread(track.stream):
                await context.send_message("bad url or search")
                return
            if not in_vc:
                await context.author.voice.channel.connect()

            _sessions[context.guild.id].all_tracks.append(track)
            _sessions[context.guild.id].playing = True

            await context.send_message(f"now playing...\n```{track.name}```")

            context.guild.voice_client.play(
                track.audio_source,
                after=lambda _: _ if not _sessions.get(context.guild.id) else _sessions[context.guild.id].play_next(
                    context.channel,
                    context.guild.voice_client,
                    context.bot.loop
                )
            )

        else:
            await context.confirm()

        if tracks and len(tracks) > 0:
            _sessions[context.guild.id].add_tracks(tracks)

    @_commands.command("shuffle", desc="Shuffles the current queue")
    async def shuffle(self, context):
        if not context.guild.id in _sessions.keys():
            await context.send_message("no session - play a track before using this command")

        else:
            _sessions[context.guild.id].shuffle()
            await context.confirm()

    @_commands.command("always-shuffle", desc="Reshuffles the queue after every loop, if looping is enabled")
    async def always_shuffle(self, context):
        if not context.guild.id in _sessions.keys():
            await context.send_message("no session - play a track before using this command")

        elif _sessions[context.guild.id].always_shuffle:
            _sessions[context.guild.id].always_shuffle = False
            await context.send_message("always shuffle disabled")

        else:
            _sessions[context.guild.id].always_shuffle = True
            await context.send_message("always shuffle enabled")

    @_commands.command("loop", desc="Toggles looping the queue")
    async def loop_queue(self, context):
        if not context.guild.id in _sessions.keys():
            await context.send_message("no session - play a track before using this command")

        elif _sessions[context.guild.id].loop_all:
            _sessions[context.guild.id].loop_all = False
            await context.send_message("looping disabled")

        else:
            _sessions[context.guild.id].loop_all = True
            await context.send_message("looping enabled")

    @_commands.command("pause", desc="Pause the current track")
    async def pause(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")

        elif not context.guild.voice_client.is_playing():
            await context.send_message("there is no track playing")

        else:
            context.guild.voice_client.pause()
            await context.confirm()

    @_commands.command("resume", desc="Resume the current track")
    async def resume(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")

        elif context.guild.voice_client.is_playing():
            await context.send_message("the track is already playing")

        else:
            context.guild.voice_client.resume()
            await context.confirm()

    @_commands.command("skip", desc="Skip the current track")
    async def skip(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")
            return

        context.guild.voice_client.stop()
        await context.confirm()

    @_commands.command("queue", desc="Display the queue")
    async def get_queue(self, context):
        if not context.guild.id in _sessions.keys() or len(_sessions[context.guild.id].queue) == 0:
            await context.send_message("empty queue")
            return

        queue = [track for track in _sessions[context.guild.id].queue]
        message = await context.send_message(self._page(queue[:_DISPLAY_LIMIT], 1))

        if len(queue) < _DISPLAY_LIMIT + 1:
            return

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        async with _timeout(60):

            floor = 0
            ceiling = _DISPLAY_LIMIT

            while True:
                try:
                    # credit: https://stackoverflow.com/a/70661168
                    tasks = [
                        context.bot.loop.create_task(context.bot.wait_for('reaction_remove')),
                        context.bot.loop.create_task(context.bot.wait_for('reaction_add'))
                    ]
                    done, pending = await _asyncio.wait(tasks,return_when=_asyncio.FIRST_COMPLETED)

                except _asyncio.exceptions.CancelledError:
                    return

                if not done:
                    continue

                reaction, user = done.pop().result()

                if user == context.bot.user or reaction.message != message:
                    continue
                elif reaction.emoji == "▶️":

                    if len(queue) > ceiling:
                        floor += _DISPLAY_LIMIT
                        ceiling += _DISPLAY_LIMIT if len(queue) > _DISPLAY_LIMIT else len(queue)
                    else: # len(queue) == ceiling:
                        floor = 0
                        ceiling = _DISPLAY_LIMIT

                    await message.edit(content=self._page(queue[floor:ceiling], _ceil(ceiling / _DISPLAY_LIMIT)))

                elif reaction.emoji == "◀️":

                    if floor != 0:
                        ceiling -= ceiling-floor
                        floor -= _DISPLAY_LIMIT
                    else: # floor == 0
                        ceiling = len(queue)
                        floor = ceiling - (_DISPLAY_LIMIT if (ceiling % _DISPLAY_LIMIT) == 0 else (ceiling % _DISPLAY_LIMIT))

                    await message.edit(content=self._page(queue[floor:ceiling], _ceil(ceiling / _DISPLAY_LIMIT)))

    @staticmethod
    def _page(queue, page_number):
        header = f"queue - page ({page_number}/{_ceil(len(queue) / _DISPLAY_LIMIT)})```\n" # TODO make pages easier to make for other commands
        body = ""

        for track in queue:
            body += f"{track.name}\n"
        return f"{header}{body}```"
