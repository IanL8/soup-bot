from functools import reduce
from random import shuffle

import threading
from time import sleep
import asyncio
from math import ceil
from async_timeout import timeout

from command_management import Commands, CommandBlock
from .music_support import track_downloader, gather_tracks, Session, Track

sessions: {str:Session} = dict()

threading.Thread(target=track_downloader, args=(lambda: sessions,), daemon=True).start()


class Block(CommandBlock):

    name = "music commands"
    commands = Commands()

    def close(self):
        sessions.clear()

    @commands.command("join", "join vc")
    async def join(self, context):
        if not context.author.voice:
            return await context.send_message("user is not in a voice channel")

        await context.author.voice.channel.connect()
        await context.confirm()

    @commands.command("leave", "leave vc")
    async def leave(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        if context.guild.id in sessions.keys():
            sessions.pop(context.guild.id)

        await context.guild.voice_client.disconnect(force=False)
        await context.confirm()

    @staticmethod
    async def play_next_coro(gid, channel, vc, loop):
        track = sessions[gid].queue.pop(0)
        sessions[gid].all_tracks.append(track)
        asyncio.run_coroutine_threadsafe(channel.send(f"now playing...\n```{track.name}```"), loop)
        vc.play(track.audio_source(), after=lambda _: Block.play_next(gid, channel, vc, loop))

    @staticmethod
    def play_next(gid, channel, vc, loop):
        if not gid in sessions.keys():
            return
        elif not sessions[gid].queue:
            if sessions[gid].streaming_queue:
                while not sessions[gid].queue: sleep(0.1) # wait for tracks to populate queue from streaming_queue
            elif sessions[gid].loop_all:
                sessions[gid].queue = [t for t in sessions[gid].all_tracks]
                if sessions[gid].always_shuffle: shuffle(sessions[gid].queue)
            else:
                sessions[gid].playing = False
                return

        asyncio.run(Block.play_next_coro(gid, channel, vc, loop))

    @commands.command("play", "play audio in vc", enable_input=True)
    async def play(self, context):

        if not context.guild.voice_client in context.bot.voice_clients:
            if context.author.voice:
                await context.author.voice.channel.connect()
            else:
                return await context.send_message("user is not in a voice channel")

        await context.defer_message()

        if context.guild.id not in sessions.keys(): sessions[context.guild.id] = Session()

        tracks = gather_tracks(reduce(lambda x, y: f"{x} {y}", context.args))
        if not tracks:
            return await context.send_message("no tracks could be found from url")

        if not sessions[context.guild.id].playing:
            sessions[context.guild.id].playing = True
            track = tracks.pop(0)
            if not track.stream(): return await context.send_message("bad url/search")
            sessions[context.guild.id].all_tracks.append(track)
            await context.send_message(f"now playing...\n```{track.name}```")
            context.guild.voice_client.play(
                track.audio_source(),
                after=lambda _: self.play_next(context.guild.id, context.channel, context.guild.voice_client, context.bot.loop)
            )
        else:
            await context.confirm()

        if len(tracks) > 0: sessions[context.guild.id].add_tracks(tracks)

    @commands.command("shuffle", "shuffles the queue")
    async def shuffle(self, context):
        if not context.guild.id in sessions.keys():
            return await context.send_message("no session - play a track before using this command")

        shuffle(sessions[context.guild.id].queue)
        shuffle(sessions[context.guild.id].streaming_queue)
        await context.confirm()

    @commands.command("always_shuffle", "reshuffles the queue on every loop")
    async def always_shuffle(self, context):
        if not context.guild.id in sessions.keys():
            return await context.send_message("no session - play a track before using this command")

        if sessions[context.guild.id].always_shuffle:
            sessions[context.guild.id].always_shuffle = False
            return await context.send_message("always shuffle disabled")
        else:
            sessions[context.guild.id].always_shuffle = True
            return await context.send_message("always shuffle enabled")

    @commands.command("loop", "toggles the looping of queue")
    async def loop_queue(self, context):
        if not context.guild.id in sessions.keys():
            return await context.send_message("no session - play a track before using this command")

        if sessions[context.guild.id].loop_all:
            sessions[context.guild.id].loop_all = False
            return await context.send_message("looping disabled")
        else:
            sessions[context.guild.id].loop_all = True
            return await context.send_message("looping enabled")

    @commands.command("pause", "pause the current track")
    async def pause(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        if not context.guild.voice_client.is_playing():
            return await context.send_message("there is no track playing")

        context.guild.voice_client.pause()
        await context.confirm()

    @commands.command("resume", "resume the current track")
    async def resume(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        if context.guild.voice_client.is_playing():
            return await context.send_message("the track is already playing")

        context.guild.voice_client.resume()
        await context.confirm()

    @commands.command("skip", "skip the current track")
    async def skip(self, context):
        if not context.guild.voice_client in context.bot.voice_clients:
            return await context.send_message("bot is not in a voice channel")

        context.guild.voice_client.stop()
        await context.confirm()

    @commands.command("queue", "display the queue")
    async def get_queue(self, context):
        if not context.guild.id in sessions.keys() or len(sessions[context.guild.id].queue) == 0:
            return await context.send_message("empty queue")

        limit = 20
        queue = [track for track in sessions[context.guild.id].queue + sessions[context.guild.id].streaming_queue]

        def page(q, page_number):
            header = f"queue - page ({page_number}/{ceil(len(queue) / limit)})```\n"
            body = ""
            for track in q: body += f"{track.name}\n"
            return f"{header}{body}```"

        message = await context.send_message(page(queue[:limit], 1))
        if len(queue) < limit + 1: return

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        async with timeout(60):
            floor = 0   # floor
            ceiling = limit  # ceiling
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
                except asyncio.exceptions.CancelledError: return
                if not done: continue

                reaction, user = done.pop().result()
                if user == context.bot.user or reaction.message != message: continue

                if reaction.emoji == "▶️":
                    if len(queue) > ceiling:
                        floor += limit
                        ceiling += limit if len(queue) > limit else len(queue)
                    else: # len(queue) == ceiling:
                        floor = 0
                        ceiling = limit
                    await message.edit(content=page(queue[floor:ceiling], ceil(ceiling / limit)))
                elif reaction.emoji == "◀️":
                    if floor != 0:
                        ceiling -= ceiling-floor
                        floor -= limit
                    else: # floor == 0
                        ceiling = len(queue)
                        floor = ceiling - (limit if (ceiling % limit) == 0 else (ceiling % limit))
                    await message.edit(content=page(queue[floor:ceiling], ceil(ceiling / limit)))
