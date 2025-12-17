"""
Flappy Bird backend module.

This module provides server-side support for the Flappy Bird game,
including configuration and pipe generation patterns.
"""

from __future__ import annotations

import random
from typing import Any


def config(difficulty: str = "medium") -> dict[str, Any]:
    """
    Return game configuration based on difficulty level.

    Args:
        difficulty: One of "easy", "medium", or "hard"

    Returns:
        Configuration dict with game parameters
    """
    configs = {
        "easy": {
            "gravity": 0.35,
            "flap_strength": -7,
            "pipe_speed": 2.5,
            "pipe_gap": 180,
            "pipe_spacing": 280,
            "pipe_width": 70
        },
        "medium": {
            "gravity": 0.45,
            "flap_strength": -8,
            "pipe_speed": 3.5,
            "pipe_gap": 150,
            "pipe_spacing": 250,
            "pipe_width": 65
        },
        "hard": {
            "gravity": 0.55,
            "flap_strength": -9,
            "pipe_speed": 4.5,
            "pipe_gap": 120,
            "pipe_spacing": 220,
            "pipe_width": 60
        }
    }

    return configs.get(difficulty, configs["medium"])


def generate_pipes(
    count: int = 5,
    difficulty: str = "medium",
    canvas_height: float = 600,
    canvas_width: float = 400
) -> list[dict[str, Any]]:
    """
    Generate a sequence of pipe positions.

    Args:
        count: Number of pipes to generate
        difficulty: Difficulty level
        canvas_height: Height of the game canvas
        canvas_width: Width of the game canvas

    Returns:
        List of pipe configurations with gap positions
    """
    cfg = config(difficulty)
    gap_size = cfg["pipe_gap"]
    spacing = cfg["pipe_spacing"]

    pipes = []
    min_gap_y = 100
    max_gap_y = canvas_height - gap_size - 100

    for i in range(count):
        gap_y = random.randint(int(min_gap_y), int(max_gap_y))
        pipes.append({
            "x": canvas_width + (i * spacing),
            "gap_y": gap_y,
            "gap_size": gap_size
        })

    return pipes


def next_pipe(
    current_distance: float,
    difficulty: str = "medium",
    canvas_height: float = 600
) -> dict[str, Any]:
    """
    Generate the next pipe based on current game state.

    Args:
        current_distance: Current distance traveled
        difficulty: Difficulty level
        canvas_height: Height of the game canvas

    Returns:
        Next pipe configuration
    """
    cfg = config(difficulty)
    gap_size = cfg["pipe_gap"]

    min_gap_y = 100
    max_gap_y = canvas_height - gap_size - 100

    # Add some variation based on distance for increasing difficulty
    variation = min(50, current_distance / 1000)
    min_gap_y = min(150, min_gap_y + variation)
    max_gap_y = max(canvas_height - gap_size - 150, max_gap_y - variation)

    gap_y = random.randint(int(min_gap_y), int(max_gap_y))

    return {
        "gap_y": gap_y,
        "gap_size": gap_size
    }
