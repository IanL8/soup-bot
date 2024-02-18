from time import sleep
from discord import FFmpegOpusAudio
import yt_dlp
import asyncio

import soupbot_utilities as util


class Track:
    def __init__(self, name="", artists="", url=None):
        self.name = name
        self.artists = artists
        self.url = url
        self.stream_url = ""
        self.audio_source: FFmpegOpusAudio = None

    def stream(self):
        with yt_dlp.YoutubeDL(util.YDL_OPTIONS) as ydl:
            if not self.url:
                info = ydl.extract_info(f"ytsearch:{self.name} {self.artists}", download=False)["entries"][0]
            else:
                info = ydl.extract_info(self.url, download=False)
            self.name = info["title"]
            self.stream_url = info["url"]

    async def make_audio_source(self):
        self.audio_source = await FFmpegOpusAudio.from_probe(
            self.stream_url,
            method="fallback",
            executable=util.FFMPEG_EXE,
            **util.FFMPEG_OPTIONS
        )

class Session:
    def __init__(self):
        self.playing = False
        self.always_shuffle = False
        self.loop_all = False

        self.queue = []
        self.download_queue = []
        self.all_tracks = []

    def add_tracks(self, tracks):
        self.download_queue.extend(tracks)

def downloader(get_sessions):
    while True:
        sleep(0.5)
        for session in get_sessions().values():
            if session.download_queue:
                l = len(session.download_queue)
                for _ in range(l):
                    track = session.download_queue.pop(0)
                    track.stream()
                    asyncio.run(track.make_audio_source())
                    session.queue.append(track)
