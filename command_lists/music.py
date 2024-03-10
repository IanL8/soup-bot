from math import ceil
import threading
import asyncio
from async_timeout import timeout

from command_management.commands import CommandList, command
from ._music_support import background_streaming, gather_tracks, Session


_sessions: {str:Session} = dict()
_DISPLAY_LIMIT = 20

threading.Thread(target=background_streaming, args=(lambda: _sessions,), daemon=True).start()


class MusicCommandList(CommandList):

    name = "music commands"

    def on_close(self):
        _sessions.clear()

    @command("join", desc="join vc")
    async def join(self, context):
        if not context.author.voice:
            await context.send_message("user is not in a voice channel")
        else:
            await context.author.voice.channel.connect()
            await context.confirm()

    @command("leave", desc="leave vc")
    async def leave(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")
        else:
            if context.guild.id in _sessions.keys():
                _sessions[context.guild.id].end()
                _sessions.pop(context.guild.id)
            await context.guild.voice_client.disconnect(force=False)
            await context.confirm()

    @command("play", desc="play audio in vc", enable_input=True)
    async def play(self, context):
        in_vc = True
        if not context.guild.voice_client in context.bot.voice_clients:
            in_vc = False
            if not context.author.voice:
                await context.send_message("user is not in a voice channel")
                return
        await context.defer_message()

        if context.guild.id not in _sessions.keys():
            _sessions[context.guild.id] = Session()

        tracks = gather_tracks(context.content)
        if not tracks:
            await context.send_message("no tracks could be found from url")
            return
        elif not _sessions[context.guild.id].playing:
            track = tracks.pop(0)
            if not track.stream():
                await context.send_message("bad url or search")
                return
            if not in_vc:
                await context.author.voice.channel.connect()

            _sessions[context.guild.id].all_tracks.append(track)
            _sessions[context.guild.id].playing = True
            await context.send_message(f"now playing...\n```{track.name}```")
            context.guild.voice_client.play(
                track.audio_source,
                after=lambda _: _sessions[context.guild.id].play_next(
                    context.channel,
                    context.guild.voice_client,
                    context.bot.loop
                )
            )
        else:
            await context.confirm()
        if tracks and len(tracks) > 0:
            _sessions[context.guild.id].add_tracks(tracks)

    @command("shuffle", desc="shuffles the queue")
    async def shuffle(self, context):
        if not context.guild.id in _sessions.keys():
            await context.send_message("no session - play a track before using this command")
        else:
            _sessions[context.guild.id].shuffle()
            await context.confirm()

    @command("always-shuffle", desc="reshuffles the queue after every loop")
    async def always_shuffle(self, context):
        if not context.guild.id in _sessions.keys():
            await context.send_message("no session - play a track before using this command")
        elif _sessions[context.guild.id].always_shuffle:
            _sessions[context.guild.id].always_shuffle = False
            await context.send_message("always shuffle disabled")
        else:
            _sessions[context.guild.id].always_shuffle = True
            await context.send_message("always shuffle enabled")

    @command("loop", desc="toggles the looping of queue")
    async def loop_queue(self, context):
        if not context.guild.id in _sessions.keys():
            await context.send_message("no session - play a track before using this command")
        elif _sessions[context.guild.id].loop_all:
            _sessions[context.guild.id].loop_all = False
            await context.send_message("looping disabled")
        else:
            _sessions[context.guild.id].loop_all = True
            await context.send_message("looping enabled")

    @command("pause", desc="pause the current track")
    async def pause(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")
        elif not context.guild.voice_client.is_playing():
            await context.send_message("there is no track playing")
        else:
            context.guild.voice_client.pause()
            await context.confirm()

    @command("resume", desc="resume the current track")
    async def resume(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")
        elif context.guild.voice_client.is_playing():
            await context.send_message("the track is already playing")
        else:
            context.guild.voice_client.resume()
            await context.confirm()

    @command("skip", desc="skip the current track")
    async def skip(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            await context.send_message("bot is not in a voice channel")
            return

        context.guild.voice_client.stop()
        await context.confirm()

    @staticmethod
    def _page(queue, page_number):
        header = f"queue - page ({page_number}/{ceil(len(queue) / _DISPLAY_LIMIT)}```\n"
        body = ""
        for track in queue:
            body += f"{track.name}\n"
        return f"{header}{body}```"

    @command("queue", desc="display the queue")
    async def get_queue(self, context):
        if not context.guild.id in _sessions.keys() or len(_sessions[context.guild.id].queue) == 0:
            await context.send_message("empty queue")
            return

        queue = [track for track in _sessions[context.guild.id].queue + _sessions[context.guild.id].streaming_queue]
        message = await context.send_message(self._page(queue[:_DISPLAY_LIMIT], 1))
        if len(queue) < _DISPLAY_LIMIT + 1:
            return

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        async with timeout(60):
            floor = 0
            ceiling = _DISPLAY_LIMIT
            while True:
                try:
                    # credit: https://stackoverflow.com/a/70661168
                    tasks = [
                        context.bot.loop.create_task(context.bot.wait_for('reaction_remove')),
                        context.bot.loop.create_task(context.bot.wait_for('reaction_add'))
                    ]
                    done, pending = await asyncio.wait(
                        tasks,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                except asyncio.exceptions.CancelledError:
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
                    await message.edit(content=self._page(queue[floor:ceiling], ceil(ceiling / _DISPLAY_LIMIT)))
                elif reaction.emoji == "◀️":
                    if floor != 0:
                        ceiling -= ceiling-floor
                        floor -= _DISPLAY_LIMIT
                    else: # floor == 0
                        ceiling = len(queue)
                        floor = ceiling - (_DISPLAY_LIMIT if (ceiling % _DISPLAY_LIMIT) == 0 else (ceiling % _DISPLAY_LIMIT))
                    await message.edit(content=self._page(queue[floor:ceiling], ceil(ceiling / _DISPLAY_LIMIT)))
