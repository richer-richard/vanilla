#!/usr/bin/env python3
"""
VANILLA Arcade Hub - Lightweight JSON API

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
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, request

DEFAULT_SCORES = {
    "snake": [],
    "tetris": [],
    "pong": [],
    "breakout": [],
    "geometry_dash": [],
    "minesweeper": [],
    "space_shooters": [],
}

MAX_ENTRIES = 15


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
            data[game] = sorted(data[game], key=lambda item: item["score"], reverse=True)[:MAX_ENTRIES]
            self._write(data)

        return entry

    def games(self) -> Dict[str, List[dict]]:
        with self._lock:
            return self._read()


class GameServer:
    """Flask wrapper exposing the JSON API."""

    def __init__(self, scores_path: str | Path | None = None):
        self.store = ScoreStore(scores_path)
        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self) -> None:
        app = self.app
        store = self.store

        @app.after_request
        def add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            return response

        @app.route("/health", methods=["GET"])
        def health():
            return jsonify(
                {
                    "status": "ok",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

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
