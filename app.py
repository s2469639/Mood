# app.py 상단
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

# 실행과 동시에 .env 파일의 키들을 OS 환경변수로 주입


from flask import Flask, jsonify, render_template, request

from analyzer import analyze_mood
from database import get_latest_history, init_db, save_history
from music import search_music
load_dotenv()

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
