from __future__ import annotations

import os
from typing import Any, Dict, List
import urllib.parse
import requests

def search_music(keyword: str, limit: int = 4) -> List[Dict[str, Any]]:
    """
    app.py와의 인터페이스 호환 함수.
    키워드로 iTunes API를 호출하여 곡 정보 리스트를 반환합니다.
    """
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": keyword,
        "media": "music",
        "entity": "song",
        "limit": limit,
        "country": "KR",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        results: List[Dict[str, Any]] = []
        for item in data.get("results", []):
            track_name = item.get("trackName", "Unknown Title")
            artist_name = item.get("artistName", "Unknown Artist")
            preview_url = item.get("previewUrl", "")
            raw_artwork = item.get("artworkUrl100", "")
            artwork = raw_artwork.replace("100x100bb.jpg", "600x600bb.jpg") if raw_artwork else ""

            query_enc = urllib.parse.quote(f"{artist_name} {track_name}")
            yt_link = f"https://music.youtube.com/search?q={query_enc}"
            sp_link = f"https://open.spotify.com/search/{query_enc}"

            results.append({
                "title": track_name,
                "artist": artist_name,
                "preview_url": preview_url,
                "artwork": artwork,
                "yt_music_url": yt_link,
                "spotify_url": sp_link,
            })
        return results
    except Exception as e:
        print(f"[Music API Error] {e}")
        return []

def search_music_previews(keyword: str, limit: int = 4) -> List[Dict[str, Any]]:
    return search_music(keyword=keyword, limit=limit)
