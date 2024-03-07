from time import sleep
import asyncio
from random import shuffle
from functools import reduce
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from pytube import Playlist as YoutubePlaylist
from pytube import Search
from discord import FFmpegOpusAudio

from soupbot_util.constants import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, YDL_OPTIONS, FFMPEG_EXE
from soupbot_util.logger import soup_log


auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


class Track:

    def __init__(self, name=None, album="", artists="", url=None):
        self.name = name
        self.album = album
        self.artists = artists
        self.url = url
        self.stream_url = ""

    def _find_best_result(self, results) -> str:
        if len(results) == 0:
            return ""

        avoided_terms = ["react", "cover", "live"]
        best_result = None
        first_result = results[0]
        while not best_result and len(results) > 0:
            result = results.pop(0)
            # the best result is the first result without any avoided terms
            # normally avoided terms are permitted if they are in the name of the track
            if not any(term in result.title.lower() for term in avoided_terms if term not in self.name.lower()):
                best_result = result

        if not best_result:
            best_result = first_result  # default if no quality results are found

        return best_result.watch_url

    def stream(self):
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            if not self.url:
                self.url = self._find_best_result(Search(f"intitle:'{self.name}' {self.album} {self.artists}").results)
            try:
                info = ydl.extract_info(self.url, download=False)
            except yt_dlp.utils.YoutubeDLError as e:
                soup_log(f"{e}","err")
                return False

        if info:
            self.name = info["title"]
            self.stream_url = info["url"]
            return True
        else:
            return False

    @property
    def audio_source(self):
        return FFmpegOpusAudio(
            self.stream_url,
            bitrate=192,
            codec="copy",
            executable=FFMPEG_EXE,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        )


class Session:

    def __init__(self):
        self.playing = False
        self.always_shuffle = False
        self.loop_all = False
        self.queue = []
        self.streaming_queue = []
        self.all_tracks = []

    def add_tracks(self, tracks):
        self.streaming_queue.extend(tracks)

    def end(self):
        self.playing = False

    def shuffle(self):
        shuffle(self.queue)
        shuffle(self.streaming_queue)

    async def _play_next_coro(self, channel, vc, loop):
        track = self.queue.pop(0)
        asyncio.run_coroutine_threadsafe(channel.send(f"now playing...\n```{track.name}```"), loop)
        vc.play(track.audio_source, after=lambda _: self.play_next(channel, vc, loop))

    def play_next(self, channel, vc, loop):
        if not self.queue:
            if self.streaming_queue:
                while not self.queue:
                    sleep(0.1) # wait for tracks to populate queue from streaming_queue
            elif self.loop_all:
                self.queue = [t for t in self.all_tracks]
                if self.always_shuffle:
                    self.shuffle()
            else:
                self.playing = False
        if self.playing:
            asyncio.run(self._play_next_coro(channel, vc, loop))


def gather_tracks(text):
    tracks = []
    if "spotify.com" in text:
        try:
            if "playlist" in text:
                playlist = sp.playlist(text)
                items = [(item["track"], item["track"]["album"]["name"]) for item in playlist["tracks"]["items"]]
            elif "album" in text:
                album = sp.album(text)
                items = [(item, album["name"]) for item in album["tracks"]["items"]]
            elif "track" in text:
                track = sp.track(text)
                items = [(track, track["album"]["name"]),]
            else:
                return None
        except spotipy.SpotifyException as e:
            soup_log(f"{e}", "err")
            return None
        for track, album_name in items:
            artists = reduce(lambda x, y: f"{x} {y}", (artist["name"] for artist in track["artists"]))
            tracks.append(Track(track["name"], album=album_name, artists=artists))
    elif "youtube.com" in text or "youtu.be" in text:
        if "playlist" in text:
            tracks.extend([Track(url=url) for url in YoutubePlaylist(text).video_urls])
        else:
            tracks.append(Track(url=text))
    else:
        tracks.append(Track(name=text))
    return tracks


def background_streaming(get_sessions):
    while True:
        sleep(0.5)
        for session in get_sessions().values():
            if session.streaming_queue:
                l = len(session.streaming_queue)
                for _ in range(l):
                    track = session.streaming_queue.pop(0)
                    if track.stream():
                        session.queue.append(track)
                        session.all_tracks.append(track)
