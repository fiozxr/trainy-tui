import sys
from api import TrainyAPI

def test_api():
    print("--- TESTING TRAINY API ---")
    api = TrainyAPI()
    
    query = "Never Gonna Give You Up"
    print(f"1. Searching tracks for '{query}'...")
    tracks = api.search_tracks(query, limit=3)
    if not tracks:
        print("❌ Search failed!")
        return False
    print(f"✅ Found {len(tracks)} tracks:")
    for t in tracks:
        print(f"   - {t['title']} by {t['artist']} [{t['duration']}] (ID: {t['videoId']})")
    
    first_track = tracks[0]
    print(f"\n2. Extracting stream URL for '{first_track['title']}'...")
    stream_url = api.get_stream_url(first_track['videoId'])
    if not stream_url:
        print("❌ Stream extraction failed!")
        return False
    print(f"✅ Stream URL extracted successfully (length: {len(stream_url)} chars)")

    print(f"\n3. Fetching synced lyrics for '{first_track['title']}'...")
    lyrics = api.get_synced_lyrics(first_track['title'], first_track['artist'])
    if lyrics:
        print(f"✅ Found {len(lyrics)} synced lyric lines!")
    else:
        print("ℹ️ No synced lyrics found for this track, but API call succeeded.")

    print("\n🎉 ALL TRAINY BACKEND TESTS PASSED!")
    return True

if __name__ == "__main__":
    test_api()
