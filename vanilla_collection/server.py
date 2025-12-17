#!/usr/bin/env python3
"""
VANILLA Collection - Lightweight JSON API

This module runs a minimal Flask server for storing and retrieving
per-game leaderboards. It keeps data in a local JSON file and protects
reads/writes with a simple thread lock.

Endpoints (v1 API):
- GET  /health                       -> simple health check
- GET  /api/v1/leaderboard/<game>    -> scores for a game
- GET  /api/v1/scores                -> all scores grouped by game
- POST /api/v1/score                 -> add a score entry

Legacy endpoints (without version) are still supported for backwards compatibility.
"""

from __future__ import annotations

import functools
import html
import json
import os
import re
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .backends import (
    asteroids as asteroids_backend,
    breakout,
    flappy as flappy_backend,
    geometry_dash,
    minesweeper,
    pacman as pacman_backend,
    pong as pong_backend,
    snake as snake_backend,
    space_shooters,
    tetris as tetris_backend,
)
from .paths import default_scores_path, web_root

from flask import Flask, jsonify, request, send_from_directory, Response

# ============================================================================
# CONFIGURATION
# ============================================================================

API_VERSION = "v1"
MAX_PLAYER_NAME_LENGTH = 32
MIN_PLAYER_NAME_LENGTH = 1
MAX_SCORE_VALUE = 999_999_999
MIN_SCORE_VALUE = 0
VALID_GAMES = {"snake", "pong", "breakout", "geometry_dash", "minesweeper", "space_shooters", "tetris", "flappy", "pacman", "asteroids"}
VALID_DIFFICULTIES = {"easy", "medium", "hard", "unknown"}

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 30  # max requests per window for score submission
RATE_LIMIT_MAX_REQUESTS_READ = 100  # max requests per window for read operations

DEFAULT_SCORES = {
    "snake": [],
    "pong": [],
    "breakout": [],
    "geometry_dash": [],
    "minesweeper": [],
    "space_shooters": [],
    "tetris": [],
    "flappy": [],
    "pacman": [],
    "asteroids": [],
}

MAX_ENTRIES = 15
ASCENDING_GAMES = {"minesweeper"}


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""
    
    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def _get_client_id(self) -> str:
        """Get a unique identifier for the client."""
        # Use IP address + user agent hash as identifier
        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "")[:50]
        return f"{ip}:{hash(ua) % 10000}"
    
    def _cleanup_old_requests(self, client_id: str, window: int) -> None:
        """Remove requests outside the current window."""
        now = time.time()
        cutoff = now - window
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] 
            if ts > cutoff
        ]
    
    def is_allowed(self, max_requests: int = RATE_LIMIT_MAX_REQUESTS, 
                   window: int = RATE_LIMIT_WINDOW) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        Returns (allowed, remaining_requests).
        """
        client_id = self._get_client_id()
        now = time.time()
        
        with self._lock:
            self._cleanup_old_requests(client_id, window)
            current_count = len(self._requests[client_id])
            
            if current_count >= max_requests:
                return False, 0
            
            self._requests[client_id].append(now)
            return True, max_requests - current_count - 1
    
    def get_retry_after(self, window: int = RATE_LIMIT_WINDOW) -> int:
        """Get seconds until next request is allowed."""
        client_id = self._get_client_id()
        
        with self._lock:
            if not self._requests[client_id]:
                return 0
            oldest = min(self._requests[client_id])
            return max(0, int(window - (time.time() - oldest)))


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = RATE_LIMIT_MAX_REQUESTS, 
               window: int = RATE_LIMIT_WINDOW) -> Callable:
    """Decorator to apply rate limiting to a route."""
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            allowed, remaining = rate_limiter.is_allowed(max_requests, window)
            
            if not allowed:
                retry_after = rate_limiter.get_retry_after(window)
                response = jsonify({
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Try again in {retry_after} seconds.",
                    "retry_after": retry_after
                })
                response.status_code = 429
                response.headers["Retry-After"] = str(retry_after)
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = "0"
                return response
            
            result = f(*args, **kwargs)
            
            # Add rate limit headers to response
            if isinstance(result, tuple):
                response = result[0] if isinstance(result[0], Response) else jsonify(result[0])
                status = result[1] if len(result) > 1 else 200
            elif isinstance(result, Response):
                response = result
                status = response.status_code
            else:
                response = result
                status = 200
            
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
            
            if isinstance(result, tuple):
                return response, status
            return response
        
        return wrapped
    return decorator


# ============================================================================
# INPUT VALIDATION
# ============================================================================

def sanitize_string(value: Any, max_length: int = 100) -> str:
    """Sanitize a string input."""
    if value is None:
        return ""
    s = str(value).strip()
    # Remove HTML/script tags
    s = html.escape(s)
    # Remove control characters
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)
    # Truncate to max length
    return s[:max_length]


def validate_player_name(name: str) -> Tuple[bool, str]:
    """Validate player name."""
    if not name:
        return False, "Player name is required"
    if len(name) < MIN_PLAYER_NAME_LENGTH:
        return False, f"Player name must be at least {MIN_PLAYER_NAME_LENGTH} character"
    if len(name) > MAX_PLAYER_NAME_LENGTH:
        return False, f"Player name must be at most {MAX_PLAYER_NAME_LENGTH} characters"
    # Check for only whitespace
    if not name.strip():
        return False, "Player name cannot be only whitespace"
    return True, ""


def validate_game(game: str) -> Tuple[bool, str]:
    """Validate game name."""
    if not game:
        return False, "Game name is required"
    if game not in VALID_GAMES:
        return False, f"Invalid game. Must be one of: {', '.join(sorted(VALID_GAMES))}"
    return True, ""


def validate_difficulty(difficulty: str) -> Tuple[bool, str]:
    """Validate difficulty level."""
    if difficulty and difficulty not in VALID_DIFFICULTIES:
        return False, f"Invalid difficulty. Must be one of: {', '.join(sorted(VALID_DIFFICULTIES))}"
    return True, ""


def validate_score(score: Any) -> Tuple[bool, str, int]:
    """Validate score value."""
    try:
        score_int = int(score)
    except (TypeError, ValueError):
        return False, "Score must be a number", 0
    
    if score_int < MIN_SCORE_VALUE:
        return False, f"Score must be at least {MIN_SCORE_VALUE}", 0
    if score_int > MAX_SCORE_VALUE:
        return False, f"Score must be at most {MAX_SCORE_VALUE}", 0
    
    return True, "", score_int


# ============================================================================
# SCORE STORE
# ============================================================================

class ScoreStore:
    """Handle reading and writing leaderboard data on disk."""

    def __init__(self, scores_path: str | Path | None = None):
        default_path = default_scores_path()
        self.path = Path(scores_path or default_path).expanduser().resolve()
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
        self.root_dir = web_root()
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
            return jsonify({"board": layout, **layout})

        @app.route("/api/tetris/config", methods=["POST", "OPTIONS"])
        def tetris_config():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            difficulty = str(payload.get("difficulty") or "medium").lower()
            return jsonify({"difficulty": difficulty, "config": tetris_backend.config(difficulty)})

        # ====================================================================
        # V1 API ROUTES (with enhanced validation and rate limiting)
        # ====================================================================
        
        @app.route(f"/api/{API_VERSION}/health", methods=["GET"])
        def v1_health():
            return jsonify({
                "status": "ok",
                "api_version": API_VERSION,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        
        @app.route(f"/api/{API_VERSION}/scores", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_scores():
            return jsonify({
                "api_version": API_VERSION,
                "games": store.games()
            })
        
        @app.route(f"/api/{API_VERSION}/leaderboard/<game>", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_leaderboard(game: str):
            # Validate game
            game = sanitize_string(game, 50).lower()
            valid, error = validate_game(game)
            if not valid:
                return jsonify({"error": error, "api_version": API_VERSION}), 400
            
            return jsonify({
                "api_version": API_VERSION,
                "game": game, 
                "scores": store.leaderboard(game)
            })
        
        @app.route(f"/api/{API_VERSION}/score", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS)
        def v1_score():
            if request.method == "OPTIONS":
                return ("", 204)

            payload = request.get_json(silent=True) or {}
            
            # Sanitize and validate inputs
            game = sanitize_string(
                payload.get("game") or payload.get("game_name"), 50
            ).lower()
            player = sanitize_string(
                payload.get("player") or payload.get("name"), 
                MAX_PLAYER_NAME_LENGTH
            )
            difficulty = sanitize_string(
                payload.get("difficulty") or "unknown", 20
            ).lower()
            raw_score = payload.get("score")

            # Validate game
            valid, error = validate_game(game)
            if not valid:
                return jsonify({"error": error, "api_version": API_VERSION}), 400
            
            # Validate player name
            valid, error = validate_player_name(player)
            if not valid:
                return jsonify({"error": error, "api_version": API_VERSION}), 400
            
            # Validate difficulty
            valid, error = validate_difficulty(difficulty)
            if not valid:
                return jsonify({"error": error, "api_version": API_VERSION}), 400
            
            # Validate score
            valid, error, score_value = validate_score(raw_score)
            if not valid:
                return jsonify({"error": error, "api_version": API_VERSION}), 400

            try:
                entry = store.add_score(game, player, score_value, difficulty)
            except ValueError as exc:
                return jsonify({"error": str(exc), "api_version": API_VERSION}), 400

            return jsonify({
                "ok": True, 
                "api_version": API_VERSION,
                "entry": entry, 
                "leaderboard": store.leaderboard(game)
            }), 201
        
        # V1 game-specific endpoints
        @app.route(f"/api/{API_VERSION}/pong/ai-target", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_pong_ai_target():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            return jsonify(pong_backend.ai_target(payload))

        @app.route(f"/api/{API_VERSION}/snake/food", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_snake_food():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            grid = int(payload.get("grid") or 16)
            snake_body = payload.get("snake") or []
            return jsonify(snake_backend.next_food(grid, snake_body))

        @app.route(f"/api/{API_VERSION}/breakout/level", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_breakout_level():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            level = int(payload.get("level") or 1)
            width_val = float(payload.get("width") or 900)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            return jsonify(breakout.level_layout(level, width_val, difficulty))

        @app.route(f"/api/{API_VERSION}/geometry/pattern", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_geometry_pattern():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            distance = float(payload.get("distance") or 0)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            ground_y = float(payload.get("ground_y") or 540)
            width_val = float(payload.get("width") or 960)
            return jsonify(geometry_dash.pattern(distance, difficulty, ground_y, width_val))

        @app.route(f"/api/{API_VERSION}/minesweeper/board", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_minesweeper_board():
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

        @app.route(f"/api/{API_VERSION}/space/wave", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_space_wave():
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            wave_num = int(payload.get("wave") or 1)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            width_val = float(payload.get("width") or 900)
            height_val = float(payload.get("height") or 600)
            plan = space_shooters.wave_plan(wave_num, difficulty, width_val, height_val)
            for enemy in plan.get("enemies", []):
                enemy["x"] = clamp(float(enemy.get("x", 0)), 24, width_val - 24)
            for power in plan.get("powerups", []):
                power["x"] = clamp(float(power.get("x", 0)), 24, width_val - 24)
            return jsonify(plan)

        @app.route(f"/api/{API_VERSION}/tetris/config", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_tetris_config():
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
