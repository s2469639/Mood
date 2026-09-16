from __future__ import annotations

import json
import os
from typing import Any, Dict
from openai import OpenAI

SYSTEM_PROMPT = """
당신은 사람들의 감정과 일상의 순간을 음악으로 연결해 주는 '감성 음악 큐레이터이자 DJ'입니다.
사용자의 기분 문장을 분석하여 음악 추천에 필요한 파라미터를 JSON 형식으로 추출하세요.
반드시 마크다운 백틱 없이 순수 JSON 형식으로만 응답하세요:
{
  "tempo": "느림 | 보통 | 빠름",
  "mood": "감정 요약 (예: 러닝, 새벽 감성, 카페, 봄 산책, 힐링)",
  "genre": "추천 장르 (예: 어쿠스틱, K-Pop, 팝, R&B)",
  "search_keyword": "iTunes 음악 검색용 키워드"
}
"""

def analyze_mood(user_text: str) -> Dict[str, Any]:
    """사용자 문장 분석 및 음악 검색 키워드 추출 (API 키 미등록 시 자동 Fallback)"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "tempo": "보통",
            "mood": "일상",
            "genre": "K-Pop",
            "search_keyword": user_text if user_text else "인기곡"
        }

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        if "search_keyword" not in data:
            data["search_keyword"] = f"{data.get('genre', '')} {data.get('mood', '')}".strip() or user_text
        return data
    except Exception as e:
        print(f"[Analyzer Fallback] {e}")
        return {
            "tempo": "보통",
            "mood": "위로",
            "genre": "Acoustic",
            "search_keyword": user_text if user_text else "힐링 음악"
        }
