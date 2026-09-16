from flask import Flask, jsonify, render_template, request

from analyzer import analyze_mood
from database import get_latest_history, init_db, save_history
from music import search_music

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json(silent=True) or {}
        user_text = data.get("text", "").strip()

        if not user_text:
            return jsonify({"success": False, "message": "문장을 입력해주세요."}), 400

        analysis_result = analyze_mood(user_text)
        search_keyword = analysis_result.get("search_keyword", user_text)
        songs = search_music(search_keyword, limit=4)
        save_history(user_text, songs)

        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "songs": songs
        })
    except Exception as e:
        app.logger.error(f"추천 오류: {str(e)}")
        return jsonify({"success": False, "message": "서버 처리 중 오류가 발생했습니다."}), 500

@app.route("/api/history", methods=["GET"])
def history():
    logs = get_latest_history(limit=20)
    return jsonify({"success": True, "history": logs})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
