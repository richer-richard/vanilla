#!/usr/bin/env python3
"""
VANILLA Collection - Lightweight JSON API

This module runs a minimal Flask server for storing and retrieving
per-game leaderboards. It keeps data in a local JSON file and protects
reads/writes with a simple thread lock.

Endpoints:
- GET  /health                       -> simple health check
- GET  /leaderboard/<game>           -> scores for a game
- GET  /scores                       -> all scores grouped by game
- POST /score {game, player, score}  -> add a score entry
"""

from __future__ import annotations

import json
import os
import random
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from backends import breakout, geometry_dash, minesweeper, pong as pong_backend, snake as snake_backend, space_shooters, tetris as tetris_backend

from flask import Flask, jsonify, request, send_from_directory

DEFAULT_SCORES = {
    "snake": [],
    "pong": [],
    "breakout": [],
    "geometry_dash": [],
    "minesweeper": [],
    "space_shooters": [],
    "tetris": [],
}

MAX_ENTRIES = 15
ASCENDING_GAMES = {"minesweeper"}


class ScoreStore:
    """Handle reading and writing leaderboard data on disk."""

    def __init__(self, scores_path: str | Path | None = None):
        self.path = Path(scores_path or Path(__file__).with_name("scores.json")).resolve()
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(DEFAULT_SCORES)

    def _write(self, data: Dict[str, List[dict]]) -> None:
        temp_path = self.path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        temp_path.replace(self.path)

    def _read(self) -> Dict[str, List[dict]]:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                raise ValueError("Score file is malformed")
            return payload
        except Exception:
            # Reset to a known-good state if the file is missing or corrupted.
            self._write(DEFAULT_SCORES)
            return dict(DEFAULT_SCORES)

    def leaderboard(self, game: str) -> List[dict]:
        with self._lock:
            return list(self._read().get(game, []))

    def add_score(self, game: str, player: str, score: int | float, difficulty: str) -> dict:
        if not player or not str(player).strip():
            raise ValueError("Player name is required")
        if not isinstance(score, (int, float)):
            raise ValueError("Score must be numeric")

        entry = {
            "player": str(player).strip(),
            "score": int(score),
            "difficulty": difficulty or "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            data = self._read()
            data.setdefault(game, [])
            data[game].append(entry)
            reverse = game not in ASCENDING_GAMES
            data[game] = sorted(data[game], key=lambda item: item["score"], reverse=reverse)[:MAX_ENTRIES]
            self._write(data)

        return entry

    def games(self) -> Dict[str, List[dict]]:
        with self._lock:
            return self._read()


class GameServer:
    """Flask wrapper exposing the JSON API."""

    def __init__(self, scores_path: str | Path | None = None):
        self.store = ScoreStore(scores_path)
        self.root_dir = Path(__file__).parent.resolve()
        self.app = Flask(__name__, static_folder=str(self.root_dir), static_url_path='')
        self._register_routes()

    def _register_routes(self) -> None:
        app = self.app
        store = self.store

        def clamp(value: float, low: float, high: float) -> float:
            return max(low, min(high, value))

        @app.after_request
        def add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            return response

        @app.route("/", methods=["GET"])
        def root():
            return send_from_directory(self.root_dir, "index.html")

        @app.route("/health", methods=["GET"])
        def health():
            return jsonify(
                {
                    "status": "ok",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        @app.route("/api/health", methods=["GET"])
        def api_health():
            return health()

        @app.route("/scores", methods=["GET"])
        def scores():
            return jsonify(store.games())

        @app.route("/leaderboard/<game>", methods=["GET"])
        def leaderboard(game: str):
            return jsonify({"game": game, "scores": store.leaderboard(game)})

        @app.route("/score", methods=["POST", "OPTIONS"])
        def score():
            if request.method == "OPTIONS":
                return ("", 204)

            payload = request.get_json(silent=True) or {}
            game = str(payload.get("game") or payload.get("game_name") or "").strip().lower()
            player = str(payload.get("player") or payload.get("name") or "").strip()
            difficulty = str(payload.get("difficulty") or "unknown").strip()
            raw_score = payload.get("score")

            if not game:
                return jsonify({"error": "game is required"}), 400
            if not player:
                return jsonify({"error": "player is required"}), 400
            try:
                score_value = int(raw_score)
            except Exception:
                return jsonify({"error": "score must be a number"}), 400

            try:
                entry = store.add_score(game, player, score_value, difficulty)
            except ValueError as exc:
                return jsonify({"error": str(exc)}), 400

            return jsonify({"ok": True, "entry": entry, "leaderboard": store.leaderboard(game)}), 201

        @app.route("/api/score", methods=["POST", "OPTIONS"])
        def api_score():
            return score()

        @app.route("/api/scores", methods=["GET"])
        def api_scores():
            return scores()

        @app.route("/api/leaderboard/<game>", methods=["GET"])
        def api_leaderboard(game: str):
            return leaderboard(game)

        @app.route("/api/pong/ai-target", methods=["POST", "OPTIONS"])
        def pong_ai_target():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            return jsonify(pong_backend.ai_target(payload))

        @app.route("/api/space/wave", methods=["POST", "OPTIONS"])
        def space_wave():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            wave_num = int(payload.get("wave") or 1)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            width_val = float(payload.get("width") or 900)
            height_val = float(payload.get("height") or 600)
            plan = space_shooters.wave_plan(wave_num, difficulty, width_val, height_val)
            # clamp x to canvas width
            for enemy in plan.get("enemies", []):
                enemy["x"] = clamp(float(enemy.get("x", 0)), 24, width_val - 24)
            for power in plan.get("powerups", []):
                power["x"] = clamp(float(power.get("x", 0)), 24, width_val - 24)
            return jsonify(plan)

        @app.route("/api/snake/food", methods=["POST", "OPTIONS"])
        def snake_food():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            grid = int(payload.get("grid") or 16)
            snake_body = payload.get("snake") or []
            return jsonify(snake_backend.next_food(grid, snake_body))

        @app.route("/api/breakout/level", methods=["POST", "OPTIONS"])
        def breakout_level():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            level = int(payload.get("level") or 1)
            width_val = float(payload.get("width") or 900)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            return jsonify(breakout.level_layout(level, width_val, difficulty))

        @app.route("/api/geometry/pattern", methods=["POST", "OPTIONS"])
        def geometry_pattern():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            distance = float(payload.get("distance") or 0)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            ground_y = float(payload.get("ground_y") or 540)
            width_val = float(payload.get("width") or 960)
            return jsonify(geometry_dash.pattern(distance, difficulty, ground_y, width_val))

        @app.route("/api/minesweeper/board", methods=["POST", "OPTIONS"])
        def minesweeper_board():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            rows = int(payload.get("rows") or 9)
            cols = int(payload.get("cols") or 9)
            mines = int(payload.get("mines") or 10)
            safe_row = int(payload.get("safe_row") or 0)
            safe_col = int(payload.get("safe_col") or 0)
            layout = minesweeper.generate_board(rows, cols, mines, (safe_row, safe_col))
            return jsonify(layout)

        @app.route("/api/tetris/config", methods=["POST", "OPTIONS"])
        def tetris_config():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            difficulty = str(payload.get("difficulty") or "medium").lower()
            return jsonify({"difficulty": difficulty, "config": tetris_backend.config(difficulty)})

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
        self.app.run(host=host, port=port, debug=debug)


def create_app(scores_path: str | Path | None = None) -> Flask:
    """Flask entry point for WSGI servers."""
    return GameServer(scores_path).app


if __name__ == "__main__":
    server = GameServer()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "").lower() in {"1", "true", "yes"}
    print(f"Starting VANILLA backend on {host}:{port} (debug={debug})")
    print(f"Scores file: {server.store.path}")
    server.run(host=host, port=port, debug=debug)
