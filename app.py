# app.py (팀원 1이 작성하는 메인 통합 코드)
from flask import Flask, jsonify, render_template, request

# 팀원들이 작성한 모듈을 그대로 임포트
from analyzer import analyze_mood
from database import init_db, save_history
from music import search_music

app = Flask(__name__)
init_db()  # DB 초기화


@app.route("/")
def index():
    return render_template("index.html")  # 팀원 4의 화면 제공


@app.route("/api/recommend", methods=["POST"])
def recommend():
    user_text = request.json.get("text", "")

    # 1. 팀원 2의 모듈 실행 (감정 분석)
    analysis_result = analyze_mood(user_text)

    # 2. 팀원 3의 모듈 실행 (음악 검색)
    songs = search_music(analysis_result["search_keyword"])

    # 3. 팀원 5의 모듈 실행 (기록 저장)
    save_history(user_text, songs)

    # 4. 프론트엔드로 결과 전달
    return jsonify({"success": True, "songs": songs})


if __name__ == "__main__":
    app.run(debug=True)