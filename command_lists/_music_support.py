from collections.abc import Iterable as _Iterable
from time import sleep as _sleep
import asyncio as _asyncio
from random import shuffle as _shuffle
from functools import reduce as _reduce
import spotipy as _spotipy
import yt_dlp as _yt_dlp
from pytube import Playlist as _YoutubePlaylist
from googleapiclient.discovery import build as _google_build
from discord import FFmpegOpusAudio as _FFmpegOpusAudio

import soup_util.constants as _constants
from soup_util.soup_logging import logger as _logger


_youtube = _google_build('youtube', 'v3', developerKey=_constants.YOUTUBE_API_KEY)
_spotify = _spotipy.Spotify(
    auth_manager=_spotipy.oauth2.SpotifyClientCredentials(client_id=_constants.SPOTIPY_CLIENT_ID, client_secret=_constants.SPOTIPY_CLIENT_SECRET)
)


class Track:

    _AVOIDED_TERMS = ["react", "cover", "live"]

    def __init__(self, name="", album="", artists="", search_query=None, url=None):
        self.name = name
        self.album = album
        self.artists = artists
        self.search_query = search_query
        self.url = url

        self.stream_url = ""

    def stream(self):
        if not self.url:
            q = self.search_query if self.search_query else f"{self.name} {self.artists}"

            result = _youtube.search().list(
                part="snippet", q=q, type="video", safeSearch="none", maxResults=5, order="relevance" # TODO look into the best order to use
            ).execute()

            if not isinstance(result.get("items"), _Iterable):
                return False

            entries = [item["snippet"]["title"] for item in result["items"]]

            if len(entries) == 0:
                return False

            best_match_index = self._find_best_result(entries)
            self.url = f"https://www.youtube.com/watch?v={result['items'][best_match_index]['id']['videoId']}"

        with (_yt_dlp.YoutubeDL(_constants.YDL_OPTIONS) as ydl):
            try:
                info = ydl.extract_info(self.url, download=False)

            except _yt_dlp.utils.YoutubeDLError as e:
                _logger.warning(str(e), exc_info=True)
                return False

        if info:
            self.name = info["title"]
            self.stream_url = info["url"]
            return True
        else:
            return False

    def _find_best_result(self, entries) -> int:
        for i in range(len(entries)):
            if not any(term in entries[i].lower() for term in self._AVOIDED_TERMS if term not in self.name.lower()):
                return i

        return 0

    @property
    def audio_source(self):
        return _FFmpegOpusAudio(
            self.stream_url,
            bitrate=192,
            codec="copy",
            executable=_constants.FFMPEG_EXE,
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
        _shuffle(self.queue)
        _shuffle(self.streaming_queue)

    def play_next(self, channel, vc, loop):
        if not self.queue:
            if self.streaming_queue:
                while not self.queue:
                    _sleep(0.1) # wait for tracks to populate queue from streaming_queue

            elif self.loop_all:
                self.queue = [t for t in self.all_tracks]
                if self.always_shuffle:
                    self.shuffle()

            else:
                self.playing = False

        if self.playing:
            _asyncio.run(self._play_next_coro(channel, vc, loop))

    async def _play_next_coro(self, channel, vc, loop):
        track = self.queue.pop(0)
        _asyncio.run_coroutine_threadsafe(channel.send(f"now playing...\n```{track.name}```"), loop)
        vc.play(track.audio_source, after=lambda _: self.play_next(channel, vc, loop))


def gather_tracks(text):
    tracks = []

    if "spotify.com" in text:
        try:
            if "playlist" in text:
                playlist = _spotify.playlist(text)
                items = [(item["track"], item["track"]["album"]["name"]) for item in playlist["tracks"]["items"]]
            elif "album" in text:
                album = _spotify.album(text)
                items = [(item, album["name"]) for item in album["tracks"]["items"]]
            elif "track" in text:
                track = _spotify.track(text)
                items = [(track, track["album"]["name"]),]
            else:
                return None

        except _spotipy.SpotifyException as e:
            _logger.warning(str(e), exc_info=True)
            return None

        for track, album_name in items:
            artists = _reduce(lambda x, y: f"{x} {y}", (artist["name"] for artist in track["artists"]))
            tracks.append(Track(track["name"], album=album_name, artists=artists))

    elif "youtube.com" in text or "youtu.be" in text:
        if "playlist" in text:
            tracks.extend([Track(url=url) for url in _YoutubePlaylist(text).video_urls])
        else:
            tracks.append(Track(url=text))

    else:
        tracks.append(Track(search_query=text))

    return tracks


def background_streaming(get_sessions):
    while True:
        _sleep(0.5)

        for session in get_sessions().values():
            if session.streaming_queue:
                l = len(session.streaming_queue)

                for _ in range(l):
                    track = session.streaming_queue.pop(0)
                    if track.stream():
                        session.queue.append(track)
                        session.all_tracks.append(track)
