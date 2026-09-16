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
1. 사용자가 입력한 현재 기분, 일상 상황(예: "한강 공원에서 러닝 중", "부장님께 깨졌어", "햇빛 좋은 날 피크닉"), 선호 장르/가수를 면밀히 분석합니다.
2. 그 순간에 가장 완벽하게 어울리는 음악을 큐레이션하고, 감성적이면서도 공감 가는 추천 사유를 제공합니다.
3. 사용자가 마음에 든 곡과 유사한 바이브의 곡을 추가 탐색할 수 있도록 꼬리물기 추천을 유도합니다.

[출력 형식 - 반드시 순수 JSON 포맷으로만 응답할 것]
반드시 마크다운 백틱(```json) 없이 아래 JSON 스키마를 만족하는 유효한 JSON 문자열만 출력하세요:
{
  "empathy": "사용자의 상황이나 기분에 다정하고 센스 있게 공감하는 1~2문장",
  "tags": ["#태그1", "#태그2", "#태그3"],
  "main_tracks": [
    {
      "title": "정확한 곡명",
      "artist": "정확한 아티스트명",
      "curation_reason": "이 순간에 이 노래가 왜 어울리는지 1~2줄 감성적 설명",
      "musical_features": "템포(BPM), 장르, 보컬 톤 등 음악적 특징 요약",
      "search_query": "YouTube Music/Spotify 검색에 최적화된 검색 키워드 (예: NewJeans Hype Boy)"
    }
  ],
  "tail_tracks": [
    {
      "title": "곡명",
      "artist": "아티스트명",
      "recommendation_point": "추천 포인트 한 줄"
    },
    {
      "title": "곡명",
      "artist": "아티스트명",
      "recommendation_point": "추천 포인트 한 줄"
    }
  ],
  "archiving_tip": "연인이나 친구와 이 순간을 기록한다면 이런 멘트와 함께 남겨보세요: '[추천 한 줄 멘트]'"
}
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
      "country": "KR",  # 한국 음원 라이브러리 우선 매칭
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

      # 고화질 앨범 아트 추출 (100x100 -> 600x600 교체)
      artwork_url = item.get("artworkUrl100", "").replace(
          "