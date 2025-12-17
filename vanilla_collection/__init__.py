"""
VANILLA Collection - A collection of classic arcade games.

This package provides a Flask-based web server hosting classic arcade games
like Snake, Pong, Tetris, and more, with both frontend gameplay and backend
APIs for leaderboards and procedural content generation.
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "VANILLA Collection Contributors"

# Re-export main components for convenient access
from .server import GameServer, ScoreStore, create_app
from .app import run
from .cli import main as cli_main

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Main classes
    "GameServer",
    "ScoreStore",
    # Factory functions
    "create_app",
    "run",
    "cli_main",
]
