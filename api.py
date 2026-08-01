import httpx
from ytmusicapi import YTMusic
import yt_dlp
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrainyAPI")

class TrainyAPI:
    def __init__(self):
        self.yt = YTMusic()
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

    def is_playlist_url(self, query: str) -> bool:
        """Check if query is a YouTube/YouTube Music playlist link or ID."""
        query = query.strip()
        if "list=" in query or "playlist" in query:
            return True
        if re.match(r'^(PL|VL|RD|OLAK5uy_)[a-zA-Z0-9_-]+$', query):
            return True
        return False

    def extract_playlist_id(self, query: str) -> str:
        """Extract playlist ID from URL or return raw ID."""
        query = query.strip()
        if "list=" in query:
            match = re.search(r'list=([a-zA-Z0-9_-]+)', query)
            if match:
                return match.group(1)
        return query

    def get_playlist_tracks(self, query: str, limit: int = 100):
        """Fetch all tracks from a YouTube Music or YouTube playlist."""
        playlist_id = self.extract_playlist_id(query)
        tracks = []

        # 1. Try ytmusicapi get_playlist
        try:
            res = self.yt.get_playlist(playlist_id, limit=limit)
            if res and 'tracks' in res:
                for item in res['tracks']:
                    if not item.get('videoId'):
                        continue
                    artists = ", ".join([a['name'] for a in item.get('artists', [])]) if item.get('artists') else ''
                    album = item.get('album', {}).get('name', '') if item.get('album') else ''
                    tracks.append({
                        'videoId': item.get('videoId'),
                        'title': item.get('title', 'Unknown Track'),
                        'artist': artists or 'Various Artists',
                        'album': album or res.get('title', 'Playlist'),
                        'duration': item.get('duration', '0:00'),
                        'thumbnails': item.get('thumbnails', [])
                    })
                if tracks:
                    return tracks
        except Exception as e:
            logger.warning(f"ytmusicapi playlist fetch failed: {e}. Trying yt-dlp fallback...")

        # 2. Fallback to yt-dlp flat extraction for any YouTube playlist URL
        try:
            ydl_flat_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
            }
            url = query if query.startswith('http') else f"https://www.youtube.com/playlist?list={playlist_id}"
            with yt_dlp.YoutubeDL(ydl_flat_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = info.get('entries', [])
                for entry in entries:
                    if not entry or not entry.get('id'):
                        continue
                    dur_sec = entry.get('duration')
                    dur_str = f"{int(dur_sec // 60)}:{int(dur_sec % 60):02d}" if dur_sec else "0:00"
                    tracks.append({
                        'videoId': entry.get('id'),
                        'title': entry.get('title', 'Unknown Track'),
                        'artist': entry.get('uploader') or entry.get('artist') or 'YouTube Playlist',
                        'album': info.get('title', 'Playlist'),
                        'duration': dur_str,
                        'thumbnails': []
                    })
            return tracks
        except Exception as e:
            logger.error(f"yt-dlp playlist extraction failed: {e}")
            return []

    def search_tracks(self, query: str, limit: int = 15):
        """Search tracks on YouTube Music."""
        try:
            results = self.yt.search(query=query, filter="songs", limit=limit)
            tracks = []
            for item in results:
                artists = ", ".join([a['name'] for a in item.get('artists', [])])
                album = item.get('album', {}).get('name', '') if item.get('album') else ''
                tracks.append({
                    'videoId': item.get('videoId'),
                    'title': item.get('title'),
                    'artist': artists,
                    'album': album,
                    'duration': item.get('duration', '0:00'),
                    'thumbnails': item.get('thumbnails', [])
                })
            return tracks
        except Exception as e:
            logger.error(f"Error searching tracks: {e}")
            return []

    def get_related_tracks(self, video_id: str, limit: int = 15):
        """Fetch related/recommended tracks (YouTube Music Radio / Smart Shuffle)."""
        try:
            results = self.yt.get_watch_playlist(videoId=video_id, limit=limit)
            tracks = []
            for item in results.get('tracks', []):
                if item.get('videoId') == video_id:
                    continue
                artists = ", ".join([a['name'] for a in item.get('artists', [])]) if item.get('artists') else ''
                album = item.get('album', {}).get('name', '') if item.get('album') else ''
                tracks.append({
                    'videoId': item.get('videoId'),
                    'title': item.get('title', ''),
                    'artist': artists,
                    'album': album,
                    'duration': item.get('length', '0:00'),
                    'thumbnails': item.get('thumbnails', [])
                })
            return tracks
        except Exception as e:
            logger.error(f"Error fetching related tracks: {e}")
            return []

    def get_stream_url(self, video_id: str) -> str | None:
        """Extract direct audio stream URL using yt-dlp."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url')
        except Exception as e:
            logger.error(f"Error getting stream URL for {video_id}: {e}")
            return None

    def get_synced_lyrics(self, title: str, artist: str, duration_sec: int | None = None):
        """Fetch synchronized lyrics from LRCLIB API."""
        try:
            params = {
                'track_name': title,
                'artist_name': artist,
            }
            if duration_sec:
                params['duration'] = duration_sec

            resp = httpx.get("https://lrclib.net/api/get", params=params, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                synced_lyrics = data.get('syncedLyrics')
                if synced_lyrics:
                    return self._parse_lrc(synced_lyrics)
                plain_lyrics = data.get('plainLyrics')
                if plain_lyrics:
                    return [{'time': 0, 'text': line} for line in plain_lyrics.splitlines() if line]
            return []
        except Exception as e:
            logger.error(f"Error fetching lyrics: {e}")
            return []

    def _parse_lrc(self, lrc_text: str):
        """Parse LRC formatted text into structured [{time: seconds, text: string}]."""
        lines = []
        for line in lrc_text.splitlines():
            line = line.strip()
            if not line or not line.startswith('['):
                continue
            try:
                parts = line.split(']', 1)
                if len(parts) == 2:
                    timestamp_str = parts[0][1:]
                    text = parts[1].strip()
                    ts_parts = timestamp_str.split(':')
                    minutes = float(ts_parts[0])
                    seconds = float(ts_parts[1])
                    total_sec = minutes * 60 + seconds
                    lines.append({'time': total_sec, 'text': text})
            except Exception:
                continue
        return lines

MetrolistAPI = TrainyAPI
