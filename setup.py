from contextlib import contextmanager
from datetime import datetime
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional
import urllib.parse
from openai import OpenAI
import requests

PROJECT_DIR = "moodify"
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "templates")

# 1. 폴더 자동 생성
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(os.path.join(PROJECT_DIR, "static"), exist_ok=True)

print("📁 [1/5] 프로젝트 폴더 구조 생성 완료...")

# -------------------------------------------------------------
# 2. database.py 생성 (변수명 호환 및 단일 트랜잭션 최적화)
# -------------------------------------------------------------
database_py_code = '''from contextlib import contextmanager
from datetime import datetime
import sqlite3
from typing import Any, Dict, List

DB_NAME = "moodify.db"

@contextmanager
def get_db_connection():
    """데이터베이스 연결 컨텍스트 매니저 (PEP 8 준수)"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """1. 테이블 생성 및 인덱스 초기화"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mood TEXT NOT NULL,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                preview_url TEXT,
                artwork TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_date ON history(date)
        """)
        conn.commit()

def save_history(user_text: str, songs: List[Dict[str, Any]]) -> None:
    """[app.py 인터페이스 호환] 추천받은 곡 목록 전체를 단일 트랜잭션으로 일괄 저장"""
    if not songs:
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = [
        (
            now_str,
            user_text,
            song.get("title", "Unknown Title"),
            song.get("artist", "Unknown Artist"),
            song.get("preview_url", ""),
            # artwork와 album_art 두 변수명 모두 완벽 호환
            song.get("artwork") or song.get("album_art", "")
        )
        for song in songs
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO history (date, mood, title, artist, preview_url, artwork)
            VALUES (?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()

def save_music_history(date: str, mood: str, title: str, artist: str, preview_url: str, artwork: str):
    """단일 곡 개별 저장 함수 (레거시 지원)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO history (date, mood, title, artist, preview_url, artwork)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, mood, title, artist, preview_url, artwork))
        conn.commit()

def get_latest_history(limit: int = 50) -> List[Dict[str, Any]]:
    """저장된 기록을 최신순으로 반환"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, mood, title, artist, preview_url, artwork
            FROM history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
'''

with open(
    os.path.join(PROJECT_DIR, "database.py"), "w", encoding="utf-8"
) as f:
  f.write(database_py_code.strip() + "\n")

# -------------------------------------------------------------
# 3. music.py 생성 (변수명 양방향 호환 및 600x600 앨범아트)
# -------------------------------------------------------------
music_py_code = '''from __future__ import annotations

import os
from typing import Any, Dict, List
import urllib.parse
import requests

def search_music(keyword: str, limit: int = 4) -> List[Dict[str, Any]]:
    """
    app.py 및 프론트엔드 연동용 함수.
    iTunes Search API에서 곡 정보와 30초 미리듣기를 추출합니다.
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
            # 600x600 고화질 커버 아트
            artwork = raw_artwork.replace("100x100bb.jpg", "600x600bb.jpg") if raw_artwork else ""

            # 스트리밍 서비스 검색 딥링크
            search_query = urllib.parse.quote(f"{artist_name} {track_name}")
            yt_music_url = f"https://music.youtube.com/search?q={search_query}"
            spotify_url = f"https://open.spotify.com/search/{search_query}"

            # 모든 팀원의 변수명(artwork, album_art, yt_link 등)을 100% 수용
            results.append({
                "track_id": item.get("trackId"),
                "title": track_name,
                "artist": artist_name,
                "artwork": artwork,
                "album_art": artwork,
                "preview_url": preview_url,
                "youtube_music_link": yt_music_url,
                "yt_music_url": yt_music_url,
                "spotify_link": spotify_url,
                "spotify_url": spotify_url,
            })
        return results
    except Exception as e:
        print(f"[Music API Error] {e}")
        return []

def search_music_previews(keyword: str, limit: int = 4) -> List[Dict[str, Any]]:
    """기존 코드 호환용 Alias"""
    return search_music(keyword=keyword, limit=limit)
'''

with open(os.path.join(PROJECT_DIR, "music.py"), "w", encoding="utf-8") as f:
  f.write(music_py_code.strip() + "\n")

# -------------------------------------------------------------
# 4. analyzer.py 생성 (MoodAnalyzer.tsx 기반 파이썬 이식)
# -------------------------------------------------------------
analyzer_py_code = '''from __future__ import annotations

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
'''

with open(
    os.path.join(PROJECT_DIR, "analyzer.py"), "w", encoding="utf-8"
) as f:
  f.write(analyzer_py_code.strip() + "\n")

# -------------------------------------------------------------
# 5. app.py 생성 (E2E 파이프라인 및 design.html 파라미터 대응)
# -------------------------------------------------------------
app_py_code = '''from flask import Flask, jsonify, render_template, request

from analyzer import analyze_mood
from database import get_latest_history, init_db, save_history
from music import search_music

app = Flask(__name__)
init_db()  # DB 및 테이블 자동 초기화

@app.route("/")
def index():
    """디자인팀이 작성한 메인 화면 제공"""
    return render_template("index.html")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json(silent=True) or {}
        user_text = data.get("text", "").strip()
        pref_artist = data.get("artist", "").strip()
        pref_genre = data.get("genre", "").strip()

        if not user_text and not pref_artist and not pref_genre:
            return jsonify({"success": False, "message": "문장을 입력해주세요."}), 400

        # 1. 감정 분석
        combined_query = f"{user_text} {pref_artist} {pref_genre}".strip()
        analysis_result = analyze_mood(combined_query)

        # 2. 음악 검색
        search_keyword = analysis_result.get("search_keyword") or combined_query
        songs = search_music(search_keyword, limit=4)

        # 3. 데이터베이스 기록 저장
        save_history(user_text or search_keyword, songs)

        # 4. 결과 전달
        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "songs": songs
        })
    except Exception as e:
        app.logger.error(f"추천 처리 오류: {e}")
        return jsonify({"success": False, "message": "서버 처리 중 오류가 발생했습니다."}), 500

@app.route("/api/history", methods=["GET"])
def history():
    """캘린더 조회를 위한 히스토리 API"""
    logs = get_latest_history(limit=50)
    return jsonify({"success": True, "history": logs})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''

with open(os.path.join(PROJECT_DIR, "app.py"), "w", encoding="utf-8") as f:
  f.write(app_py_code.strip() + "\n")

print(
    "✅ [Moodify Auto Setup] 모든 파이썬 모듈과 디렉토리 구축이 완료되었습니다!"
)
print("👉 실행 방법: cd moodify && python app.py")