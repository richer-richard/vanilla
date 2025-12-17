"""
Pac-Man backend module.

This module provides server-side support for the Pac-Man game,
including maze generation and ghost AI configuration.
"""

from __future__ import annotations

import random
from typing import Any

# Standard Pac-Man maze layout
# 0=wall, 1=pellet, 2=empty, 3=power pellet, 4=ghost house
STANDARD_MAZE = [
    "0000000000000000000000000000",
    "0111111111111001111111111110",
    "0100001000010010100010000010",
    "0300001000010010100010000030",
    "0100001000010010100010000010",
    "0111111111111111111111111110",
    "0100001001000000010010000010",
    "0100001001000000010010000010",
    "0111111001111001111001111110",
    "0000001000010010100010000000",
    "0000001000010010100010000000",
    "0000001002222222220010000000",
    "0000001000044440000010000000",
    "0000001002040440200010000000",
    "2222221222040440222122222222",
    "0000001000044440000010000000",
    "0000001002222222220010000000",
    "0000001000000000000010000000",
    "0000001001111111110010000000",
    "0111111111110010111111111110",
    "0100001000010010100010000010",
    "0100001000010010100010000010",
    "0311001111112222111111001130",
    "0001001001000000010010010000",
    "0001001001000000010010010000",
    "0111111001111001111001111110",
    "0100000000010010100000000010",
    "0100000000010010100000000010",
    "0111111111111111111111111110",
    "0000000000000000000000000000",
    "0000000000000000000000000000",
]


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
            "ghost_speed": 1.5,
            "pacman_speed": 2.5,
            "frightened_time": 10000,
            "scatter_time": 7000,
            "chase_time": 20000,
            "ghost_release_interval": 5000,
        },
        "medium": {
            "ghost_speed": 2.0,
            "pacman_speed": 2.5,
            "frightened_time": 7000,
            "scatter_time": 5000,
            "chase_time": 20000,
            "ghost_release_interval": 3000,
        },
        "hard": {
            "ghost_speed": 2.5,
            "pacman_speed": 2.5,
            "frightened_time": 5000,
            "scatter_time": 3000,
            "chase_time": 25000,
            "ghost_release_interval": 2000,
        },
    }

    return configs.get(difficulty, configs["medium"])


def get_maze() -> list[str]:
    """
    Return the standard Pac-Man maze layout.

    Returns:
        List of strings representing the maze
    """
    return STANDARD_MAZE.copy()


def get_maze_as_grid() -> list[list[int]]:
    """
    Return the maze as a 2D grid of integers.

    Returns:
        2D list of integers representing the maze
    """
    return [[int(cell) for cell in row] for row in STANDARD_MAZE]


def count_pellets() -> int:
    """
    Count the total number of pellets in the maze.

    Returns:
        Total pellet count (including power pellets)
    """
    count = 0
    for row in STANDARD_MAZE:
        for cell in row:
            if cell in ("1", "3"):
                count += 1
    return count


def get_ghost_config() -> list[dict[str, Any]]:
    """
    Return configuration for all four ghosts.

    Returns:
        List of ghost configurations
    """
    return [
        {
            "name": "blinky",
            "color": "#ff0000",
            "start_x": 13.5,
            "start_y": 11,
            "scatter_target": {"x": 25, "y": -3},
            "personality": "chaser",  # Directly targets Pac-Man
        },
        {
            "name": "pinky",
            "color": "#ffb8ff",
            "start_x": 13.5,
            "start_y": 14,
            "scatter_target": {"x": 2, "y": -3},
            "personality": "ambusher",  # Targets ahead of Pac-Man
        },
        {
            "name": "inky",
            "color": "#00ffff",
            "start_x": 11.5,
            "start_y": 14,
            "scatter_target": {"x": 27, "y": 31},
            "personality": "fickle",  # Complex targeting
        },
        {
            "name": "clyde",
            "color": "#ffb852",
            "start_x": 15.5,
            "start_y": 14,
            "scatter_target": {"x": 0, "y": 31},
            "personality": "random",  # Random/shy behavior
        },
    ]


def calculate_ghost_target(
    ghost_name: str,
    ghost_x: float,
    ghost_y: float,
    pacman_x: float,
    pacman_y: float,
    pacman_direction: tuple[int, int],
    blinky_x: float = 0,
    blinky_y: float = 0,
    mode: str = "chase",
) -> dict[str, float]:
    """
    Calculate the target position for a ghost based on its AI personality.

    Args:
        ghost_name: Name of the ghost
        ghost_x: Ghost's current X position
        ghost_y: Ghost's current Y position
        pacman_x: Pac-Man's current X position
        pacman_y: Pac-Man's current Y position
        pacman_direction: Pac-Man's current direction (dx, dy)
        blinky_x: Blinky's X position (needed for Inky's AI)
        blinky_y: Blinky's Y position (needed for Inky's AI)
        mode: Current ghost mode ("chase", "scatter", "frightened")

    Returns:
        Target position dict with x and y
    """
    from typing import Dict, cast

    ghosts = {g["name"]: g for g in get_ghost_config()}
    ghost = ghosts.get(ghost_name, ghosts["blinky"])

    if mode == "scatter":
        return cast(Dict[str, float], ghost["scatter_target"])

    if mode == "frightened":
        # Random movement when frightened
        return {"x": random.randint(0, 27), "y": random.randint(0, 30)}

    # Chase mode - each ghost has different targeting
    dx, dy = pacman_direction

    if ghost_name == "blinky":
        # Directly targets Pac-Man
        return {"x": pacman_x, "y": pacman_y}

    elif ghost_name == "pinky":
        # Targets 4 tiles ahead of Pac-Man
        return {"x": pacman_x + dx * 4, "y": pacman_y + dy * 4}

    elif ghost_name == "inky":
        # Complex targeting: double the vector from Blinky to 2 tiles ahead of Pac-Man
        ahead_x = pacman_x + dx * 2
        ahead_y = pacman_y + dy * 2
        return {"x": ahead_x + (ahead_x - blinky_x), "y": ahead_y + (ahead_y - blinky_y)}

    elif ghost_name == "clyde":
        # Targets Pac-Man if far, scatter if close
        dist = ((pacman_x - ghost_x) ** 2 + (pacman_y - ghost_y) ** 2) ** 0.5
        if dist > 8:
            return {"x": pacman_x, "y": pacman_y}
        return cast(Dict[str, float], ghost["scatter_target"])

    # Default: chase Pac-Man directly
    return {"x": pacman_x, "y": pacman_y}
