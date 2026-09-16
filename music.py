from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
import urllib.parse
from openai import OpenAI
import requests

# ==========================================
# 1. 감성 음악 큐레이터 및 DJ 시스템 프롬프트
# ==========================================
MOODIFY_SYSTEM_PROMPT = """
당신은 사람들의 감정과 일상의 순간을 음악으로 연결해 주는 '감성 음악 큐레이터이자 DJ'입니다.

[역할 및 목표]
1. 사용자가 입력한 현재 기분, 일상 상황(예: "한강 공원에서 러닝 중", "부장님께 깨졌어", "햇빛 좋은 날 피크닉"), 사진 묘사, 선호 장르/가수를 면밀히 분석합니다.
2. 그 순간에 가장 완벽하게 어울리는 음악을 큐레이션하고, 감성적이면서도 공감 가는 추천 사유를 제공합니다.
3. 사용자가 마음에 든 곡과 유사한 바이브의 곡을 추가 탐색할 수 있도록 꼬리물기 추천을 유도합니다.

[출력 형식 - 반드시 유효한 JSON 포맷으로만 응답할 것]
반드시 백틱(```json) 없이 아래 JSON 구조로만 출력하세요:
{
  "empathy": "사용자의 상황이나 기분에 다정하고 센스 있게 1~2문장으로 공감",
  "tags": ["#태그1", "#태그2", "#태그3"],
  "main_tracks": [
    {
      "title": "정확한 곡명",
      "artist": "정확한 아티스트명",
      "curation_reason": "이 순간에 이 노래가 왜 어울리는지 1~2줄 감성적 설명",
      "musical_features": "템포(BPM), 장르, 보컬 톤 등",
      "search_query": "가수명 곡명 (검색용 키워드)"
    }
  ],
  "tail_tracks": [
    {
      "title": "곡명",
      "artist": "아티스트",
      "point": "추천 포인트 한 줄"
    },
    {
      "title": "곡명",
      "artist": "아티스트",
      "point": "추천 포인트 한 줄"
    }
  ],
  "archiving_tip": "연인이나 친구와 이 순간을 기록한다면 이런 멘트와 함께 남겨보세요: '[추천 한 줄 멘트]'"
}

[어조]
따뜻하고 감각적이며, 음악에 조예가 깊은 친한 친구 같은 다정한 어조를 유지하세요.
"""


# ==========================================
# 2. iTunes Search API & 30초 미리듣기 연동
# ==========================================
def search_music_previews(keyword: str, limit: int = 1) -> List[Dict[str, Any]]:
  """키워드(곡명, 아티스트 등)를 입력받아 iTunes에서 30초 미리듣기 음원,

  고화질(600x600) 앨범 아트 및 YouTube Music/Spotify 검색 딥링크를 반환합니다.
  """
  base_url = "[https://itunes.apple.com/search](https://itunes.apple.com/search)"
  params = {
      "term": keyword,
      "media": "music",
      "entity": "song",
      "limit": limit,
      "country": "KR",  # 한국 음원 스토어 우선 매칭
  }

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  try:
    response = requests.get(
        base_url, params=params, headers=headers, timeout=10
    )
    response.raise_for_status()
    data = response.json()

    results: List[Dict[str, Any]] = []
    for item in data.get("results", []):
      track_name = item.get("trackName", "")
      artist_name = item.get("artistName", "")

      # 고화질 앨범 커버 (100x100 -> 600x600 변환)
      artwork_url = item.get("artworkUrl100", "").replace(
          "100x100bb", "600x600bb"
      )
      preview_url = item.get("previewUrl", "")

      # 스트리밍 서비스 검색 바로가기 URL 인코딩
      search_query = urllib.parse.quote(f"{artist_name} {track_name}")
      yt_music_url = f"[https://music.youtube.com/search?q=](https://music.youtube.com/search?q=){search_query}"
      spotify_url = f"[https://open.spotify.com/search/](https://open.spotify.com/search/){search_query}"

      results.append({
          "track_id": item.get("trackId"),
          "title": track_name,
          "artist": artist_name,
          "album_art": artwork_url,
          "preview_url": preview_url,
          "youtube_music_link": yt_music_url,
          "spotify_link": spotify_url,
      })

    return results

  except Exception as e:
    print(f"⚠️ iTunes 음원 검색 실패 ({keyword}): {e}")
    return []


# ==========================================
# 3. Moodify 감성 DJ 추천 엔진
# ==========================================
class MoodifyCurator:

  def __init__(self, api_key: Optional[str] = None):
    # 환경변수 OPENAI_API_KEY 또는 직접 전달받은 키 사용
    self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

  def get_recommendation(
      self,
      mood_text: str,
      preferred_artist: str = "",
      preferred_genre: str = "",
  ) -> str:
    """사용자 입력을 분석하여 지정된 포맷의 감성 DJ 텍스트로 최종 렌더링합니다."""
    user_input_payload = f"현재 상황 및 기분: {mood_text}\n"
    if preferred_artist:
      user_input_payload += f"선호 가수: {preferred_artist}\n"
    if preferred_genre:
      user_input_payload += f"선호 장르: {preferred_genre}\n"

    try:
      # 1. LLM 구조화 생성 요청
      response = self.client.chat.completions.create(
          model="gpt-4o-mini",
          response_format={"type": "json_object"},
          messages=[
              {"role": "system", "content": MOODIFY_SYSTEM_PROMPT},
              {"role": "user", "content": user_input_payload},
          ],
          temperature=0.75,
      )

      raw_json = response.choices[0].message.content
      data = json.loads(raw_json)

      # 2. 메인 추천 곡에 실시간 iTunes 음원 및 딥링크 결합
      for track in data.get("main_tracks", []):
        search_target = (
            track.get("search_query") or f"{track['artist']} {track['title']}"
        )
        itunes_info = search_music_previews(search_target, limit=1)

        if itunes_info:
          track_meta = itunes_info[0]
          track["preview_url"] = track_meta.get("preview_url")
          track["youtube_music_link"] = track_meta.get("youtube_music_link")
          track["spotify_link"] = track_meta.get("spotify_link")
        else:
          q = urllib.parse.quote(search_target)
          track["preview_url"] = None
          track["youtube_music_link"] = f"[https://music.youtube.com/search?q=](https://music.youtube.com/search?q=){q}"
          track["spotify_link"] = f"[https://open.spotify.com/search/](https://open.spotify.com/search/){q}"

      # 3. 요청하신 지정 포맷(1~5단계)으로 문자열 구성
      return self._format_response(data)

    except Exception as e:
      return f"❌ 추천 생성 중 오류가 발생했습니다: {e}"

  def _format_response(self, d: Dict[str, Any]) -> str:
    lines = []

    # 1. 공감 한마디
    empathy = d.get("empathy", "오늘 하루도 정말 고생 많으셨어요.")
    lines.append(f"1. 공감 한마디:\n   {empathy}\n")

    # 2. 무드 분석 태그
    tags = " ".join(d.get("tags", ["#오늘의기분", "#음악추천", "#휴식"]))
    lines.append(f"2. 무드 분석 태그:\n   {tags}\n")

    # 3. 대표 추천 곡
    lines.append("3. 대표 추천 곡:")
    for track in d.get("main_tracks", []):
      lines.append(f"   - {track.get('title')} - {track.get('artist')}")
      lines.append(f"     * 큐레이션 이유: {track.get('curation_reason')}")
      lines.append(f"     * 음악적 특징: {track.get('musical_features')}")
      lines.append(f"     * 검색 쿼리 힌트: {track.get('search_query')}")
      if track.get("preview_url"):
        lines.append(f"     * 30초 미리듣기: {track.get('preview_url')}")
      lines.append(f"     * YouTube Music: {track.get('youtube_music_link')}")
      lines.append(f"     * Spotify: {track.get('spotify_link')}")
    lines.append("")

    # 4. 꼬리물기 추천
    lines.append("4. 꼬리물기 추천 (이 곡과 결이 비슷한 노래 2곡):")
    for tail in d.get("tail_tracks", []):
      lines.append(
          f"   - {tail.get('title')} - {tail.get('artist')} :"
          f" {tail.get('point')}"
      )
    lines.append("")

    # 5. 데이트/아카이빙 팁
    archiving = d.get("archiving_tip", "")
    lines.append(f"5. 데이트/아카이빙 팁:\n   - {archiving}")

    return "\n".join(lines)


# ==========================================
# 4. 테스트 실행
# ==========================================
if __name__ == "__main__":
  # 터미널에서 export OPENAI_API_KEY="your-key" 설정 후 실행
  curator = MoodifyCurator()

  # 상황 예시 입력
  user_input = "한강 공원에서 바람 맞으면서 러닝 중이야! 시원하고 상쾌해"
  fav_artist = ""
  fav_genre = "시티팝 / 청량한 팝"

  print("=" * 60)
  print(f"🎧 Moodify DJ가 신청곡을 준비 중입니다...\n입력: {user_input}")
  print("=" * 60 + "\n")

  result_message = curator.get_recommendation(
      mood_text=user_input,
      preferred_artist=fav_artist,
      preferred_genre=fav_genre,
  )

  print(result_message)