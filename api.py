import httpx
from ytmusicapi import YTMusic
import yt_dlp
import logging

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
