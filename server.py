#!/usr/bin/env python3
"""
Compatibility shim for the VANILLA Collection server.

The packaged implementation lives in `vanilla_collection.server`.
"""

from __future__ import annotations

from vanilla_collection.server import (  # noqa: F401
    API_VERSION,
    ASCENDING_GAMES,
    DEFAULT_SCORES,
    MAX_ENTRIES,
    MAX_PLAYER_NAME_LENGTH,
    MAX_SCORE_VALUE,
    MIN_PLAYER_NAME_LENGTH,
    MIN_SCORE_VALUE,
    RATE_LIMIT_MAX_REQUESTS,
    RATE_LIMIT_MAX_REQUESTS_READ,
    RATE_LIMIT_WINDOW,
    VALID_DIFFICULTIES,
    VALID_GAMES,
    GameServer,
    RateLimiter,
    ScoreStore,
    rate_limit,
    sanitize_string,
    validate_difficulty,
    validate_game,
    validate_player_name,
    validate_score,
)

__all__ = [
    "API_VERSION",
    "ASCENDING_GAMES",
    "DEFAULT_SCORES",
    "GameServer",
    "MAX_ENTRIES",
    "MAX_PLAYER_NAME_LENGTH",
    "MAX_SCORE_VALUE",
    "MIN_PLAYER_NAME_LENGTH",
    "MIN_SCORE_VALUE",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_MAX_REQUESTS_READ",
    "RATE_LIMIT_WINDOW",
    "RateLimiter",
    "ScoreStore",
    "VALID_DIFFICULTIES",
    "VALID_GAMES",
    "rate_limit",
    "sanitize_string",
    "validate_difficulty",
    "validate_game",
    "validate_player_name",
    "validate_score",
]


if __name__ == "__main__":
    GameServer().run()

