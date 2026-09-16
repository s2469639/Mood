import urllib.parse
import requests


def search_music_previews(keyword: str, limit: int = 4) -> list[dict]:
  """키워드(곡명, 아티스트, 분위기 등)를 입력받아

  iTunes에서 30초 미리듣기 음원 및 YouTube Music/Spotify 딥링크 데이터를 반환합니다.
  """
  base_url = "https://itunes.apple.com/search"
  params = {
      "term": keyword,
      "media": "music",
      "entity": "song",
      "limit": limit,
      "country": "KR",  # 한국 음원 매칭 우선
  }

  try:
    response = requests.get(base_url, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("results", []):
      track_name = item.get("trackName", "")
      artist_name = item.get("artistName", "")

      # 고화질 앨범 아트 추출 (100x100 -> 600x600 변환)
      artwork_url = item.get("artworkUrl100", "").replace(
          "100x100bb", "600x600bb"
      )
      preview_url = item.get("previewUrl", "")

      # 검색 쿼리 인코딩 (스트리밍 서비스 검색 바로가기 URL 생성)
      search_query = urllib.parse.quote(f"{artist_name} {track_name}")
      yt_music_url = (
          f"https://music.youtube.com/search?q={search_query}"
      )
      spotify_url = f"https://open.spotify.com/search/{search_query}"

      results.append({
          "track_id": item.get("trackId"),
          "title": track_name,
          "artist": artist_name,
          "album_art": artwork_url,
          "preview_url": preview_url,  # 30초 m4a/aac 스트리밍 링크
          "youtube_music_link": yt_music_url,
          "spotify_link": spotify_url,
      })

    return results

  except Exception as e:
    print(f"음악 검색 중 오류 발생: {e}")
    return []


# 로컬 테스트용
if __name__ == "__main__":
  test_keyword = "NewJeans Hype Boy"
  songs = search_music_previews(test_keyword, limit=4)
  for idx, s in enumerate(songs, 1):
    print(f"[{idx}] {s['title']} - {s['artist']}")
    print(f"    미리듣기: {s['preview_url']}")
    print(f"    YouTube Music: {s['youtube_music_link']}")
    print(f"    Spotify: {s['spotify_link']}")