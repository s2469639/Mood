from contextlib import contextmanager
from datetime import datetime
import sqlite3
from typing import Any, Dict, List

DB_NAME = "moodify.db"

@contextmanager
def get_db_connection():
    """데이터베이스 연결을 안전하게 관리하기 위한 컨텍스트 매니저 (PEP 8 준수)"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """1. 테이블 생성 함수"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mood TEXT NOT NULL,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                preview_url TEXT,
                artwork TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_date ON history(date)
        ''')
        conn.commit()

def save_history(user_text: str, songs: List[Dict[str, Any]]) -> None:
    """app.py 연동용 일괄 저장 함수 (단일 트랜잭션 최적화)"""
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
            song.get("artwork", ""),
        )
        for song in songs
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO history (date, mood, title, artist, preview_url, artwork)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', records)
        conn.commit()

def save_music_history(date: str, mood: str, title: str, artist: str, preview_url: str, artwork: str):
    """단일 곡 저장 함수 (레거시 및 개별 저장 지원)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (date, mood, title, artist, preview_url, artwork)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, mood, title, artist, preview_url, artwork))
        conn.commit()

def get_latest_history(limit: int = 20) -> List[Dict[str, Any]]:
    """최근 청취 기록을 최신순으로 반환"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, date, mood, title, artist, preview_url, artwork
            FROM history
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
