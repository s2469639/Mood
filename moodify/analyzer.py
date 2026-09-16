from __future__ import annotations

import json
import os
from typing import Any, Dict
from openai import OpenAI

SYSTEM_PROMPT = '''
당신은 감성 음악 큐레이터이자 DJ입니다.
사용자의 문장을 분석하여 어울리는 음악 추천 파라미터를 JSON으로 응답하세요.
반드시 마크다운 백틱 없이 유효한 JSON 형식으로만 출력하세요:
{
  "mood": "감정 요약 (예: 차분함, 신남, 위로)",
  "genre": "장르 (예: Indie, Acoustic, R&B, Pop)",
  "search_keyword": "음악 검색에 최적화된 키워드"
}
'''

def analyze_mood(user_text: str) -> Dict[str, Any]:
    """사용자 문장 분석 및 검색 키워드 추출"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "mood": "감성",
            "genre": "K-Pop",
            "search_keyword": user_text if user_text else "인기곡"
        }

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
            max_tokens=200,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        return json.loads(content)
    except Exception as e:
        print(f"[Analyzer Fallback] {e}")
        return {
            "mood": "위로",
            "genre": "Acoustic",
            "search_keyword": user_text if user_text else "힐링"
        }
