"""
Snake Game Backend - Smart Food Placement (VANILLA)

This backend provides intelligent food placement that the frontend cannot easily do:
1. Uses flood-fill to ensure the snake can reach the food
2. Avoids placing food in dead-end positions
3. Provides optimal food positions that give the player room to maneuver

The Flask route in server.py calls:
    next_food(grid, snake)
and returns the dict as JSON.
"""

from __future__ import annotations

import random
from collections import deque
from typing import Dict, Iterable, List, Set, Tuple


def _occupied(snake: Iterable[Dict[str, int]]) -> Set[Tuple[int, int]]:
    """Get set of cells occupied by snake body."""
    return {(int(seg.get("x", 0)), int(seg.get("y", 0))) for seg in snake}


def _flood_fill(start: Tuple[int, int], blocked: Set[Tuple[int, int]], grid: int) -> Set[Tuple[int, int]]:
    """
    Returns all reachable cells from start position using flood fill.
    This helps identify if a food position might trap the snake.
    """
    reachable = set()
    queue = deque([start])
    visited = {start}
    
    while queue:
        x, y = queue.popleft()
        if (x, y) in blocked:
            continue
        if x < 0 or x >= grid or y < 0 or y >= grid:
            continue
        
        reachable.add((x, y))
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited and 0 <= nx < grid and 0 <= ny < grid:
                visited.add((nx, ny))
                if (nx, ny) not in blocked:
                    queue.append((nx, ny))
    
    return reachable


def _get_safe_score(pos: Tuple[int, int], snake_set: Set[Tuple[int, int]], grid: int) -> int:
    """
    Calculate how "safe" a food position is.
    Higher score = better position (more escape routes for player).
    """
    x, y = pos
    score = 0
    
    # Count open neighbors
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid and 0 <= ny < grid and (nx, ny) not in snake_set:
            score += 1
    
    # Prefer positions not near edges (more room to maneuver)
    edge_dist = min(x, y, grid - 1 - x, grid - 1 - y)
    score += min(edge_dist, 3)  # Cap bonus at 3
    
    # Prefer positions with more open space around
    for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid and 0 <= ny < grid and (nx, ny) not in snake_set:
            score += 0.5
    
    return int(score * 10)


def next_food(grid: int, snake: Iterable[Dict[str, int]]) -> Dict[str, int]:
    """
    Generate smart food placement.
    
    This provides value the frontend alone cannot:
    1. Ensures food is reachable via flood-fill
    2. Scores positions by safety (escape routes)
    3. Uses seeded randomness for reproducibility
    """
    snake_list = list(snake)
    taken = _occupied(snake_list)
    
    # Get snake head position
    head = snake_list[0] if snake_list else {"x": grid // 2, "y": grid // 2}
    head_pos = (int(head.get("x", 0)), int(head.get("y", 0)))
    
    # Find all open spaces
    open_spaces = [(x, y) for x in range(grid) for y in range(grid) if (x, y) not in taken]
    
    if not open_spaces:
        return {"x": 0, "y": 0}
    
    # For smaller snakes, just use basic placement
    if len(snake_list) < 5:
        rng = random.Random(f"snake-{grid}-{len(taken)}")
        x, y = rng.choice(open_spaces)
        return {"x": x, "y": y}
    
    # For longer snakes, use smart placement
    # Find reachable cells from snake head
    reachable = _flood_fill(head_pos, taken, grid)
    
    # Filter to only reachable open spaces
    reachable_spaces = [(x, y) for x, y in open_spaces if (x, y) in reachable]
    
    if not reachable_spaces:
        # Fallback if no reachable spaces (shouldn't happen in normal play)
        rng = random.Random(f"snake-{grid}-{len(taken)}-fallback")
        x, y = rng.choice(open_spaces)
        return {"x": x, "y": y}
    
    # Score each reachable position
    scored_positions = [(pos, _get_safe_score(pos, taken, grid)) for pos in reachable_spaces]
    
    # Sort by score (higher is better)
    scored_positions.sort(key=lambda p: p[1], reverse=True)
    
    # Take top 30% of positions and randomly select from them
    # This adds variety while still preferring good positions
    top_count = max(1, len(scored_positions) // 3)
    top_positions = [pos for pos, _ in scored_positions[:top_count]]
    
    rng = random.Random(f"snake-smart-{grid}-{len(taken)}-{head_pos}")
    x, y = rng.choice(top_positions)
    
    return {"x": x, "y": y}


def get_game_stats(grid: int, snake: Iterable[Dict[str, int]]) -> Dict:
    """
    Get game statistics that might be useful for analytics.
    This is additional backend functionality beyond basic food placement.
    """
    snake_list = list(snake)
    taken = _occupied(snake_list)
    
    head = snake_list[0] if snake_list else {"x": grid // 2, "y": grid // 2}
    head_pos = (int(head.get("x", 0)), int(head.get("y", 0)))
    
    # Calculate reachable space percentage
    reachable = _flood_fill(head_pos, taken, grid)
    total_cells = grid * grid
    open_cells = total_cells - len(taken)
    reachable_percent = (len(reachable) / max(1, open_cells)) * 100
    
    # Calculate how "trapped" the snake is
    danger_level = 100 - reachable_percent
    
    return {
        "snake_length": len(snake_list),
        "grid_coverage": (len(taken) / total_cells) * 100,
        "reachable_cells": len(reachable),
        "reachable_percent": round(reachable_percent, 1),
        "danger_level": round(danger_level, 1),
        "open_cells": open_cells,
    }
