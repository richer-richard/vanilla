"""
Asteroids backend module.

This module provides server-side support for the Asteroids game,
including asteroid generation, wave configuration, and UFO spawning.
"""

from __future__ import annotations

import math
import random
from typing import Dict, Any, List, Tuple


def config(difficulty: str = "medium") -> Dict[str, Any]:
    """
    Return game configuration based on difficulty level.
    
    Args:
        difficulty: One of "easy", "medium", or "hard"
    
    Returns:
        Configuration dict with game parameters
    """
    configs = {
        "easy": {
            "ship_speed": 0.15,
            "rotation_speed": 0.08,
            "asteroid_speed": 1.0,
            "bullet_speed": 8,
            "starting_asteroids": 3,
            "friction": 0.99,
            "invulnerability_time": 3000,
            "ufo_spawn_chance": 0.001,
            "max_bullets": 6
        },
        "medium": {
            "ship_speed": 0.12,
            "rotation_speed": 0.07,
            "asteroid_speed": 1.5,
            "bullet_speed": 10,
            "starting_asteroids": 4,
            "friction": 0.995,
            "invulnerability_time": 2000,
            "ufo_spawn_chance": 0.002,
            "max_bullets": 5
        },
        "hard": {
            "ship_speed": 0.1,
            "rotation_speed": 0.06,
            "asteroid_speed": 2.0,
            "bullet_speed": 12,
            "starting_asteroids": 5,
            "friction": 0.998,
            "invulnerability_time": 1500,
            "ufo_spawn_chance": 0.003,
            "max_bullets": 4
        }
    }
    
    return configs.get(difficulty, configs["medium"])


def generate_asteroid(
    canvas_width: float = 800,
    canvas_height: float = 600,
    size: str = "large",
    difficulty: str = "medium",
    avoid_x: float = None,
    avoid_y: float = None,
    avoid_radius: float = 150
) -> Dict[str, Any]:
    """
    Generate a single asteroid with random properties.
    
    Args:
        canvas_width: Width of the game canvas
        canvas_height: Height of the game canvas
        size: Size of asteroid ("large", "medium", "small")
        difficulty: Difficulty level
        avoid_x: X position to avoid (e.g., ship position)
        avoid_y: Y position to avoid
        avoid_radius: Minimum distance from avoid position
    
    Returns:
        Asteroid configuration dict
    """
    cfg = config(difficulty)
    
    # Determine radius based on size
    radii = {"large": 40, "medium": 25, "small": 12}
    points = {"large": 20, "medium": 50, "small": 100}
    radius = radii.get(size, 40)
    
    # Generate position (avoiding specified area)
    max_attempts = 50
    for _ in range(max_attempts):
        x = random.random() * canvas_width
        y = random.random() * canvas_height
        
        if avoid_x is None or avoid_y is None:
            break
            
        dist = math.hypot(x - avoid_x, y - avoid_y)
        if dist >= avoid_radius:
            break
    
    # Generate velocity
    speed_multiplier = {"large": 1.0, "medium": 1.5, "small": 2.0}
    speed = cfg["asteroid_speed"] * speed_multiplier.get(size, 1.0)
    angle = random.random() * math.pi * 2
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed
    
    # Generate shape (random polygon)
    num_vertices = random.randint(8, 12)
    vertices = []
    for i in range(num_vertices):
        vert_angle = (i / num_vertices) * math.pi * 2
        variation = 0.7 + random.random() * 0.4
        vertices.append({
            "x": math.cos(vert_angle) * radius * variation,
            "y": math.sin(vert_angle) * radius * variation
        })
    
    return {
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy,
        "radius": radius,
        "size": size,
        "points": points.get(size, 20),
        "rotation": random.random() * math.pi * 2,
        "rotation_speed": (random.random() - 0.5) * 0.05,
        "vertices": vertices
    }


def generate_wave(
    wave_number: int,
    difficulty: str = "medium",
    canvas_width: float = 800,
    canvas_height: float = 600,
    ship_x: float = 400,
    ship_y: float = 300
) -> List[Dict[str, Any]]:
    """
    Generate asteroids for a wave.
    
    Args:
        wave_number: Current wave number (1-based)
        difficulty: Difficulty level
        canvas_width: Width of the game canvas
        canvas_height: Height of the game canvas
        ship_x: Ship's X position to avoid
        ship_y: Ship's Y position to avoid
    
    Returns:
        List of asteroid configurations
    """
    cfg = config(difficulty)
    base_count = cfg["starting_asteroids"]
    
    # Increase asteroid count with each wave
    num_asteroids = base_count + (wave_number - 1)
    
    asteroids = []
    for _ in range(num_asteroids):
        asteroid = generate_asteroid(
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            size="large",
            difficulty=difficulty,
            avoid_x=ship_x,
            avoid_y=ship_y,
            avoid_radius=150
        )
        asteroids.append(asteroid)
    
    return asteroids


def split_asteroid(
    asteroid: Dict[str, Any],
    difficulty: str = "medium"
) -> List[Dict[str, Any]]:
    """
    Split an asteroid into smaller pieces.
    
    Args:
        asteroid: The asteroid being destroyed
        difficulty: Difficulty level
    
    Returns:
        List of new smaller asteroids (empty if asteroid was small)
    """
    size = asteroid.get("size", "large")
    x = asteroid.get("x", 0)
    y = asteroid.get("y", 0)
    
    if size == "large":
        return [
            generate_asteroid(size="medium", difficulty=difficulty, avoid_x=None, avoid_y=None),
            generate_asteroid(size="medium", difficulty=difficulty, avoid_x=None, avoid_y=None)
        ]
    elif size == "medium":
        return [
            generate_asteroid(size="small", difficulty=difficulty, avoid_x=None, avoid_y=None),
            generate_asteroid(size="small", difficulty=difficulty, avoid_x=None, avoid_y=None)
        ]
    
    # Small asteroids don't split
    return []


def generate_ufo(
    canvas_width: float = 800,
    canvas_height: float = 600,
    difficulty: str = "medium"
) -> Dict[str, Any]:
    """
    Generate a UFO enemy.
    
    Args:
        canvas_width: Width of the game canvas
        canvas_height: Height of the game canvas
        difficulty: Difficulty level
    
    Returns:
        UFO configuration dict
    """
    # UFO enters from left or right side
    from_left = random.random() < 0.5
    x = 0 if from_left else canvas_width
    y = random.random() * canvas_height * 0.6 + canvas_height * 0.2
    
    speed_multipliers = {"easy": 1.5, "medium": 2.0, "hard": 2.5}
    speed = speed_multipliers.get(difficulty, 2.0)
    
    vx = speed if from_left else -speed
    vy = (random.random() - 0.5) * speed * 0.5
    
    return {
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy,
        "radius": 20,
        "points": 200,
        "fire_rate": 2000 if difficulty == "easy" else 1500 if difficulty == "medium" else 1000
    }


def should_spawn_ufo(
    elapsed_time: float,
    score: int,
    difficulty: str = "medium"
) -> bool:
    """
    Determine if a UFO should spawn.
    
    Args:
        elapsed_time: Time since game start (ms)
        score: Current player score
        difficulty: Difficulty level
    
    Returns:
        True if UFO should spawn
    """
    cfg = config(difficulty)
    
    # Don't spawn too early
    if elapsed_time < 30000:
        return False
    
    # Higher scores increase UFO frequency
    score_multiplier = 1 + (score / 5000)
    spawn_chance = cfg["ufo_spawn_chance"] * score_multiplier
    
    return random.random() < spawn_chance
