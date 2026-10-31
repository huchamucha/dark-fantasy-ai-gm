import os
from flask import Flask, jsonify, request

from game_engine import GameEngine
from game_state import GameState

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

engine = GameEngine(
    base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
    api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
    model=os.getenv("LMSTUDIO_MODEL", "Qwen2.5-7B-Instruct-GGUF"),
)

sessions: dict[str, GameState] = {}


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "status": "ready",
        "llm": {
            "base_url": engine.client.base_url,
            "model": engine.client.model,
        },
    })


@app.post("/api/session/new")
def create_session():
    payload = request.get_json(silent=True) or {}
    player_name = payload.get("player_name") or "Warden"
    title = payload.get("title") or "The Ashen Dominion"
    location = payload.get("location") or "Blackglass Keep"
    trait = payload.get("trait") or "merciless curiosity"

    state = GameState.create(player_name=player_name, title=title, location=location, trait=trait)
    sessions[state.session_id] = state

    return jsonify({
        "ok": True,
        "session_id": state.session_id,
        "state": state.to_dict(),
    })


@app.post("/api/story/next")
def next_story_step():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id")
    if not session_id or session_id not in sessions:
        return jsonify({"ok": False, "error": "invalid or missing session_id"}), 400

    state = sessions[session_id]
    player_input = payload.get("player_input") or ""
    choice = payload.get("choice")

    try:
        result = engine.advance(state, player_input=player_input, choice=choice)
        sessions[session_id] = state
        return jsonify({"ok": True, "session_id": session_id, "result": result})
    except Exception as exc:  # pragma: no cover - local debugging only
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
