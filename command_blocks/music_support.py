from time import sleep

from discord import FFmpegOpusAudio
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Playlist as YoutubePlaylist

import soupbot_utilities as util


auth_manager = SpotifyClientCredentials(client_id=util.SPOTIPY_CLIENT_ID, client_secret=util.SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


class Track:

    def __init__(self, name=None, album="", artists="", url=None):
        self.name = name
        self.album = album
        self.artists = artists
        self.url = url
        self.stream_url = ""

    def stream(self):
        with yt_dlp.YoutubeDL(util.YDL_OPTIONS) as ydl:
            if not self.url:
                entries = ydl.extract_info(
                    f"ytsearch3:intitle:'{self.name}' {self.album} {self.artists}",
                    download=False
                )["entries"]
                if len(entries) == 0: return False
                info = None
                first = entries[0] # preserve first result
                while not info and len(entries) > 0:
                    has_term = False
                    e = entries.pop(0)
                    for t in ["react", "cover", "live"]: # avoid results with these terms in title unless in track name
                        has_term = has_term or (t in e["title"].lower() and not t in self.name.lower())
                    if not has_term:
                        info = e
                if not info: info = first # default if no quality results are found
            else:
                try:
                    info = ydl.extract_info(self.url, download=False)
                except yt_dlp.utils.DownloadError as _:
                    return False
            self.name = info["title"]
            self.stream_url = info["url"]
            return True

    def audio_source(self):
        return FFmpegOpusAudio(
            self.stream_url,
            bitrate=192,
            codec="copy",
            executable=util.FFMPEG_EXE,
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


def gather_tracks(arg):
    tracks = []
    if "spotify.com" in arg:
        if "playlist" in arg:
            try:
                items = sp.playlist(arg)["tracks"]["items"]
            except spotipy.SpotifyException as _:
                return None
            for i in items:
                artists = ""
                for a in i["track"]["artists"]: artists += f"{a['name']} "
                tracks.append(Track(i['track']['name'], album=i["track"]["album"]["name"],artists=artists))
        elif "album" in arg:
            try:
                am = sp.album(arg)
                album_name = am["name"]
                items = am["tracks"]["items"]
            except spotipy.SpotifyException as _:
                return None
            for i in items:
                artists = ""
                for a in i["artists"]: artists += f"{a['name']} "
                tracks.append(Track(i['name'], album=album_name, artists=artists))
        elif "track" in arg:
            try:
                track = sp.track(arg)
            except spotipy.SpotifyException as _:
                return None
            artists = ""
            for a in track["artists"]: artists += f"{a['name']} "
            tracks.append(Track(track['name'], album=track["album"]["name"], artists=artists))
        else:
            tracks = None
    elif "youtube.com" in arg or "youtu.be" in arg:
        if "playlist" in arg:
            tracks.extend([Track(url=url) for url in YoutubePlaylist(arg).video_urls])
        else:
            tracks.append(Track(url=arg))
    else:
        tracks.append(Track(name=arg))

    return tracks


def track_downloader(get_sessions):
    while True:
        sleep(0.5)
        for session in get_sessions().values():
            if session.streaming_queue:
                l = len(session.streaming_queue)
                for _ in range(l):
                    track = session.streaming_queue.pop(0)
                    if track.stream():
                        session.queue.append(track)
