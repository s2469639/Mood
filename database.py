import sqlite3
from contextlib import contextmanager

DB_NAME = "moodify.db"

@contextmanager
def get_db_connection():
    """데이터베이스 연결을 안전하게 관리하기 위한 컨텍스트 매니저 (PEP 8 준수)"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 컬럼명을 딕셔너리처럼 키로 접근할 수 있게 설정
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """1. 테이블 생성 함수: 음악 기록 저장을 위한 history 테이블 생성"""
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
        # 날짜별 조회가 잦으므로 날짜 기준 인덱스 생성 (성능 최적화)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_date ON history(date)
        """)
        conn.commit()

def save_music_history(date: str, mood: str, title: str, artist: str, preview_url: str, artwork: str):
    """2. 추천받은 음악 정보를 오늘 날짜와 함께 저장하는 함수"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO history (date, mood, title, artist, preview_url, artwork)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, mood, title, artist, preview_url, artwork))
        conn.commit()

def get_latest_history(limit: int = 20):
    """3. 저장된 기록을 최신순(시간 역순)으로 가져오는 함수"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, mood, title, artist, preview_url, artwork
            FROM history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        # Row 객체를 딕셔너리로 변환하여 반환
        return [dict(row) for row in rows]