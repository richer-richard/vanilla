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
import logging
import os
import re
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from flask import Flask, Response, jsonify, request, send_from_directory

from .backends import (
    breakout,
    geometry_dash,
    minesweeper,
    space_shooters,
)
from .backends import (
    pong as pong_backend,
)
from .backends import (
    snake as snake_backend,
)
from .backends import (
    tetris as tetris_backend,
)
from .paths import default_scores_path, web_root

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ============================================================================
# CONFIGURATION
# ============================================================================

API_VERSION = "v1"
MAX_PLAYER_NAME_LENGTH = 32
MIN_PLAYER_NAME_LENGTH = 1
MAX_SCORE_VALUE = 999_999_999
MIN_SCORE_VALUE = 0

VALID_GAMES: set[str] = {
    "snake",
    "pong",
    "breakout",
    "geometry_dash",
    "minesweeper",
    "space_shooters",
    "tetris",
    "flappy",
    "pacman",
    "asteroids",
}
VALID_DIFFICULTIES: set[str] = {"easy", "medium", "hard", "unknown"}

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 30  # max requests per window for score submission
RATE_LIMIT_MAX_REQUESTS_READ = 100  # max requests per window for read operations

DEFAULT_SCORES: dict[str, list[dict]] = {game: [] for game in VALID_GAMES}

MAX_ENTRIES = 15
ASCENDING_GAMES: set[str] = {"minesweeper"}

# CORS Configuration - can be overridden via environment variable
# Use comma-separated list for multiple origins: "http://localhost:3000,https://example.com"
# Use "*" for development only
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*")


# ============================================================================
# RATE LIMITER
# ============================================================================


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _get_client_id(self) -> str:
        """Get a unique identifier for the client."""
        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "")[:50]
        return f"{ip}:{hash(ua) % 10000}"

    def _cleanup_old_requests(self, client_id: str, window: int) -> None:
        """Remove requests outside the current window."""
        now = time.time()
        cutoff = now - window
        self._requests[client_id] = [ts for ts in self._requests[client_id] if ts > cutoff]

    def is_allowed(
        self, max_requests: int = RATE_LIMIT_MAX_REQUESTS, window: int = RATE_LIMIT_WINDOW
    ) -> tuple[bool, int]:
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
                logger.warning(f"Rate limit exceeded for client {client_id}")
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


def rate_limit(
    max_requests: int = RATE_LIMIT_MAX_REQUESTS, window: int = RATE_LIMIT_WINDOW
) -> Callable:
    """Decorator to apply rate limiting to a route."""

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            allowed, remaining = rate_limiter.is_allowed(max_requests, window)

            if not allowed:
                retry_after = rate_limiter.get_retry_after(window)
                response = jsonify(
                    {
                        "error": "rate_limit_exceeded",
                        "message": f"Too many requests. Try again in {retry_after} seconds.",
                        "retry_after": retry_after,
                    }
                )
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

            if hasattr(response, "headers"):
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
    s = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", s)
    # Truncate to max length
    return s[:max_length]


def validate_player_name(name: str) -> tuple[bool, str]:
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


def validate_game(game: str) -> tuple[bool, str]:
    """Validate game name."""
    if not game:
        return False, "Game name is required"
    if game not in VALID_GAMES:
        return False, f"Invalid game. Must be one of: {', '.join(sorted(VALID_GAMES))}"
    return True, ""


def validate_difficulty(difficulty: str) -> tuple[bool, str]:
    """Validate difficulty level."""
    if difficulty and difficulty not in VALID_DIFFICULTIES:
        return False, f"Invalid difficulty. Must be one of: {', '.join(sorted(VALID_DIFFICULTIES))}"
    return True, ""


def validate_score(score: Any) -> tuple[bool, str, int]:
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

    def __init__(self, scores_path: str | Path | None = None) -> None:
        default_path = default_scores_path()
        self.path = Path(scores_path or default_path).expanduser().resolve()
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(DEFAULT_SCORES)
        logger.info(f"ScoreStore initialized with path: {self.path}")

    def _write(self, data: dict[str, list[dict]]) -> None:
        temp_path = self.path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        temp_path.replace(self.path)

    def _read(self) -> dict[str, list[dict]]:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                raise ValueError("Score file is malformed")
            return payload
        except Exception as e:
            logger.error(f"Error reading scores file: {e}. Resetting to default.")
            self._write(DEFAULT_SCORES)
            return dict(DEFAULT_SCORES)

    def leaderboard(self, game: str) -> list[dict]:
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
            data[game] = sorted(data[game], key=lambda item: item["score"], reverse=reverse)[
                :MAX_ENTRIES
            ]
            self._write(data)

        logger.info(f"Score added: {player} scored {score} in {game} ({difficulty})")
        return entry

    def games(self) -> dict[str, list[dict]]:
        with self._lock:
            return self._read()


# ============================================================================
# GAME SERVER
# ============================================================================


class GameServer:
    """Flask wrapper exposing the JSON API."""

    def __init__(self, scores_path: str | Path | None = None) -> None:
        self.store = ScoreStore(scores_path)
        self.root_dir = web_root()
        self.app = Flask(__name__, static_folder=str(self.root_dir), static_url_path="")
        self._register_routes()

    def _register_routes(self) -> None:
        app = self.app
        store = self.store

        def clamp(value: float, low: float, high: float) -> float:
            return max(low, min(high, value))

        def get_cors_origin() -> str:
            """Get the appropriate CORS origin based on configuration."""
            if CORS_ALLOWED_ORIGINS == "*":
                return "*"
            allowed = [o.strip() for o in CORS_ALLOWED_ORIGINS.split(",")]
            origin = request.headers.get("Origin", "")
            if origin in allowed:
                return origin
            return allowed[0] if allowed else "*"

        @app.after_request
        def add_cors_headers(response: Response) -> Response:
            response.headers["Access-Control-Allow-Origin"] = get_cors_origin()
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            return response

        # ====================================================================
        # SHARED HANDLERS (reduce code duplication)
        # ====================================================================

        def handle_score_submission(
            payload: dict, include_api_version: bool = False
        ) -> tuple[Response, int]:
            """Common handler for score submission."""
            # Sanitize and validate inputs
            game = sanitize_string(payload.get("game") or payload.get("game_name"), 50).lower()
            player = sanitize_string(
                payload.get("player") or payload.get("name"), MAX_PLAYER_NAME_LENGTH
            )
            difficulty = sanitize_string(payload.get("difficulty") or "unknown", 20).lower()
            raw_score = payload.get("score")

            response_extra = {"api_version": API_VERSION} if include_api_version else {}

            # Validate game
            valid, error = validate_game(game)
            if not valid:
                return jsonify({"error": error, **response_extra}), 400

            # Validate player name
            valid, error = validate_player_name(player)
            if not valid:
                return jsonify({"error": error, **response_extra}), 400

            # Validate difficulty
            valid, error = validate_difficulty(difficulty)
            if not valid:
                return jsonify({"error": error, **response_extra}), 400

            # Validate score
            valid, error, score_value = validate_score(raw_score)
            if not valid:
                return jsonify({"error": error, **response_extra}), 400

            try:
                entry = store.add_score(game, player, score_value, difficulty)
            except ValueError as exc:
                return jsonify({"error": str(exc), **response_extra}), 400

            return (
                jsonify(
                    {
                        "ok": True,
                        **response_extra,
                        "entry": entry,
                        "leaderboard": store.leaderboard(game),
                    }
                ),
                201,
            )

        def handle_leaderboard(
            game: str, include_api_version: bool = False
        ) -> tuple[Response, int]:
            """Common handler for leaderboard retrieval."""
            game = sanitize_string(game, 50).lower()
            response_extra = {"api_version": API_VERSION} if include_api_version else {}

            valid, error = validate_game(game)
            if not valid:
                return jsonify({"error": error, **response_extra}), 400

            return jsonify({**response_extra, "game": game, "scores": store.leaderboard(game)}), 200

        # ====================================================================
        # STATIC FILES & HEALTH
        # ====================================================================

        @app.route("/", methods=["GET"])
        def root() -> Response:
            return send_from_directory(self.root_dir, "index.html")

        @app.route("/health", methods=["GET"])
        def health() -> Response:
            result: Response = jsonify(
                {
                    "status": "ok",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            return result

        @app.route("/api/health", methods=["GET"])
        def api_health() -> Response:
            return health()

        # ====================================================================
        # LEGACY ENDPOINTS (with rate limiting and validation)
        # ====================================================================

        @app.route("/scores", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def scores() -> Response:
            result: Response = jsonify(store.games())
            return result

        @app.route("/leaderboard/<game>", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def leaderboard(game: str) -> tuple[Response, int]:
            return handle_leaderboard(game, include_api_version=False)

        @app.route("/score", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS)
        def score() -> tuple[str, int] | tuple[Response, int]:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            return handle_score_submission(payload, include_api_version=False)

        @app.route("/api/score", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS)
        def api_score() -> tuple[str, int] | tuple[Response, int]:
            result: tuple[str, int] | tuple[Response, int] = score()
            return result

        @app.route("/api/scores", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def api_scores() -> Response:
            result: Response = scores()
            return result

        @app.route("/api/leaderboard/<game>", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def api_leaderboard(game: str) -> tuple[Response, int]:
            return handle_leaderboard(game, include_api_version=False)

        # ====================================================================
        # GAME-SPECIFIC ENDPOINTS (Legacy)
        # ====================================================================

        @app.route("/api/pong/ai-target", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def pong_ai_target() -> tuple[str, int] | Response:
            if request.method == "OPTIONS":
                return ("", 204)
            payload: dict[str, object] = request.get_json(silent=True) or {}
            result: Response = jsonify(pong_backend.ai_target(payload))
            return result

        @app.route("/api/space/wave", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def space_wave() -> tuple[str, int] | Response:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            wave_num = int(payload.get("wave") or 1)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            width_val = float(payload.get("width") or 900)
            height_val = float(payload.get("height") or 600)
            plan: dict[str, Any] = space_shooters.wave_plan(
                wave_num, difficulty, width_val, height_val
            )
            enemies: list[dict[str, Any]] = plan.get("enemies", [])
            for enemy in enemies:
                enemy["x"] = clamp(float(enemy.get("x", 0)), 24, width_val - 24)
            powerups: list[dict[str, Any]] = plan.get("powerups", [])
            for power in powerups:
                power["x"] = clamp(float(power.get("x", 0)), 24, width_val - 24)
            result: Response = jsonify(plan)
            return result

        @app.route("/api/snake/food", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def snake_food() -> tuple[str, int] | Response:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            grid = int(payload.get("grid") or 16)
            snake_body = payload.get("snake") or []
            result: Response = jsonify(snake_backend.next_food(grid, snake_body))
            return result

        @app.route("/api/breakout/level", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def breakout_level() -> tuple[str, int] | Response:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            level = int(payload.get("level") or 1)
            width_val = float(payload.get("width") or 900)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            result: Response = jsonify(breakout.level_layout(level, width_val, difficulty))
            return result

        @app.route("/api/geometry/pattern", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def geometry_pattern() -> tuple[str, int] | Response:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            distance = float(payload.get("distance") or 0)
            difficulty = str(payload.get("difficulty") or "medium").lower()
            ground_y = float(payload.get("ground_y") or 540)
            width_val = float(payload.get("width") or 960)
            result: Response = jsonify(
                geometry_dash.pattern(distance, difficulty, ground_y, width_val)
            )
            return result

        @app.route("/api/minesweeper/board", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def minesweeper_board() -> tuple[str, int] | Response:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            rows = int(payload.get("rows") or 9)
            cols = int(payload.get("cols") or 9)
            mines = int(payload.get("mines") or 10)
            safe_row = int(payload.get("safe_row") or 0)
            safe_col = int(payload.get("safe_col") or 0)
            layout = minesweeper.generate_board(rows, cols, mines, (safe_row, safe_col))
            result: Response = jsonify({"board": layout, **layout})
            return result

        @app.route("/api/tetris/config", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def tetris_config() -> tuple[str, int] | Response:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            difficulty = str(payload.get("difficulty") or "medium").lower()
            result: Response = jsonify(
                {"difficulty": difficulty, "config": tetris_backend.config(difficulty)}
            )
            return result

        # ====================================================================
        # V1 API ROUTES (with enhanced validation and rate limiting)
        # ====================================================================

        @app.route(f"/api/{API_VERSION}/health", methods=["GET"])
        def v1_health() -> Response:
            result: Response = jsonify(
                {
                    "status": "ok",
                    "api_version": API_VERSION,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            return result

        @app.route(f"/api/{API_VERSION}/scores", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_scores() -> Response:
            result: Response = jsonify({"api_version": API_VERSION, "games": store.games()})
            return result

        @app.route(f"/api/{API_VERSION}/leaderboard/<game>", methods=["GET"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_leaderboard(game: str) -> tuple[Response, int]:
            return handle_leaderboard(game, include_api_version=True)

        @app.route(f"/api/{API_VERSION}/score", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS)
        def v1_score() -> tuple[str, int] | tuple[Response, int]:
            if request.method == "OPTIONS":
                return ("", 204)
            payload = request.get_json(silent=True) or {}
            return handle_score_submission(payload, include_api_version=True)

        # V1 game-specific endpoints
        @app.route(f"/api/{API_VERSION}/pong/ai-target", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_pong_ai_target() -> tuple[str, int] | Response:
            result: tuple[str, int] | Response = pong_ai_target()
            return result

        @app.route(f"/api/{API_VERSION}/snake/food", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_snake_food() -> tuple[str, int] | Response:
            result: tuple[str, int] | Response = snake_food()
            return result

        @app.route(f"/api/{API_VERSION}/breakout/level", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_breakout_level() -> tuple[str, int] | Response:
            result: tuple[str, int] | Response = breakout_level()
            return result

        @app.route(f"/api/{API_VERSION}/geometry/pattern", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_geometry_pattern() -> tuple[str, int] | Response:
            result: tuple[str, int] | Response = geometry_pattern()
            return result

        @app.route(f"/api/{API_VERSION}/minesweeper/board", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_minesweeper_board() -> tuple[str, int] | Response:
            result: tuple[str, int] | Response = minesweeper_board()
            return result

        @app.route(f"/api/{API_VERSION}/space/wave", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_space_wave() -> tuple[str, int] | Response:
            result: tuple[str, int] | Response = space_wave()
            return result

        @app.route(f"/api/{API_VERSION}/tetris/config", methods=["POST", "OPTIONS"])
        @rate_limit(max_requests=RATE_LIMIT_MAX_REQUESTS_READ)
        def v1_tetris_config() -> tuple[str, int] | Response:
            result: tuple[str, int] | Response = tetris_config()
            return result

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
        logger.info(f"Starting server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app(scores_path: str | Path | None = None) -> Flask:
    """Flask entry point for WSGI servers."""
    setup_logging()
    return GameServer(scores_path).app


if __name__ == "__main__":
    setup_logging()
    server = GameServer()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "").lower() in {"1", "true", "yes"}
    logger.info(f"Starting VANILLA backend on {host}:{port} (debug={debug})")
    logger.info(f"Scores file: {server.store.path}")
    server.run(host=host, port=port, debug=debug)
