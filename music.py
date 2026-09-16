# music.py
from __future__ import annotations

import json
import os
from typing import Any, Dict, List
import urllib.parse
import requests

# iTunes 검색이 0건일 때 화면을 채워줄 보증된 기본 트랙 4곡
FALLBACK_TRACKS = [
    {
        "title": "밤편지",
        "artist": "아이유",
        "artwork": (
            "https://is1-ssl.mzstatic.com/image/thumb/Music118/v4/b8/b5/0b/b8b50b73-030a-3ecb-665e-bc8e20235940/cover_IU_ThroughTheNight.jpg/600x600bb.jpg"
        ),
        "preview_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview115/v4/b7/c1/9d/b7c19d4e-1282-1cbe-41bf-3df08e9a2be9/mzaf_10526084092497793448.plus.aac.p.m4a",
        "yt_music_url": "https://music.youtube.com/search?q=%EC%95%84%EC%9D%B4%EC%9C%A0+%EB%B0%A4%ED%8E%B8%EC%A7%80",
    },
    {
        "title": "Ditto",
        "artist": "NewJeans",
        "artwork": (
            "https://is1-ssl.mzstatic.com/image/thumb/Music113/v4/4c/76/85/4c768571-0847-f32f-b48a-a3a8309df507/cover_NewJeans_OMG.jpg/600x600bb.jpg"
        ),
        "preview_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview122/v4/e5/22/07/e52207a7-5431-1e96-a836-8cb9622d100a/mzaf_3990812977823908953.plus.aac.p.m4a",
        "yt_music_url": "https://music.youtube.com/search?q=NewJeans+Ditto",
    },
    {
        "title": "봄 사랑 벚꽃 말고",
        "artist": "HIGH4 & 아이유",
        "artwork": (
            "https://is1-ssl.mzstatic.com/image/thumb/Music/v4/4a/ec/4a/4aec4a64-4e7a-c711-2e62-c840f135b026/cover.jpg/600x600bb.jpg"
        ),
        "preview_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/e8/e4/df/e8e4df73-a5f1-3310-7467-bc13bcda1978/mzaf_12480392348398110900.plus.aac.p.m4a",
        "yt_music_url": "https://music.youtube.com/search?q=%EB%B4%84+%EC%82%AC%EB%9E%91+%EB%82%97%EA%BD%83+%EB%A7%90%EA%B3%A0",
    },
    {
        "title": "Square (2017)",
        "artist": "백예린",
        "artwork": (
            "https://is1-ssl.mzstatic.com/image/thumb/Music113/v4/48/80/4f/48804f58-6934-8c70-6644-33827ec32f5d/cover_YerinBaek_Square.jpg/600x600bb.jpg"
        ),
        "preview_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/71/bf/20/71bf2092-be29-d055-6b58-e4905d41a7d6/mzaf_4840898517227447814.plus.aac.p.m4a",
        "yt_music_url": "https://music.youtube.com/search?q=%EB%B0%B1%EC%98%88%EB%A6%B0+Square",
    },
]


def query_itunes(term: str, limit: int = 4) -> List[Dict[str, Any]]:
  """iTunes Search API 순수 호출 함수"""
  base_url = "https://itunes.apple.com/search"
  params = {
      "term": term,
      "media": "music",
      "entity": "song",
      "limit": limit,
      "country": "KR",
  }
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  try:
    resp = requests.get(base_url, params=params, headers=headers, timeout=5)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("results", []):
      title = item.get("trackName", "Unknown Title")
      artist = item.get("artistName", "Unknown Artist")
      raw_art = item.get("artworkUrl100", "")
      art = (
          raw_art.replace("100x100bb.jpg", "600x600bb.jpg") if raw_art else ""
      )
      preview = item.get("previewUrl", "")

      query_enc = urllib.parse.quote(f"{artist} {title}")
      yt_link = f"https://music.youtube.com/search?q={query_enc}"

      results.append({
          "title": title,
          "artist": artist,
          "artwork": art,
          "album_art": art,
          "preview_url": preview,
          "yt_music_url": yt_link,
      })
    return results
  except Exception as e:
    print(f"[iTunes API Fail]: {e}")
    return []


def search_music(keyword: str, limit: int = 4) -> List[Dict[str, Any]]:
  """1차 검색 실패 시 단어 분해 및 Fallback을 단계적으로 수행하는 안정형 함수"""
  clean_kw = keyword.replace("#", "").strip()

  # 1. 원본 키워드로 1차 검색
  songs = query_itunes(clean_kw, limit=limit)
  if songs:
    return songs

  # 2. 공백 분리 후 첫 번째 핵심 단어(가수/장르)로 2차 검색
  tokens = clean_kw.split()
  for token in tokens:
    if len(token) >= 2:
      songs = query_itunes(token, limit=limit)
      if songs:
        return songs

  # 3. 인기 K-Pop 검색 시도
  songs = query_itunes("K-Pop", limit=limit)
  if songs:
    return songs

  # 4. 네트워크 단절 등 최악의 경우 내장 트랙 4곡 반환
  return FALLBACK_TRACKS[:limit]