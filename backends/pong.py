from __future__ import annotations

import random
from typing import Dict


def ai_target(payload: Dict[str, object]) -> Dict[str, object]:
    difficulty = str(payload.get("difficulty") or "medium").lower()
    ball = payload.get("ball") or {}
    court = payload.get("court") or {}
    ai_state = payload.get("ai") or {}

    height = float(court.get("height") or 600)
    width = float(court.get("width") or 800)
    bx = float(ball.get("x") or width / 2)
    by = float(ball.get("y") or height / 2)
    dx = float(ball.get("dx") or 1)
    dy = float(ball.get("dy") or 0)
    ai_height = float(ai_state.get("height") or 96)

    target_x = width - 30
    travel_time = (target_x - bx) / max(1.0, abs(dx))
    predicted = by + dy * travel_time
    while predicted < 0 or predicted > height:
        predicted = -predicted if predicted < 0 else height - (predicted - height)

    noise = {"easy": 140, "medium": 110, "hard": 80}.get(difficulty, 110)
    miss_chance = {"easy": 0.5, "medium": 0.32, "hard": 0.22}.get(difficulty, 0.32)
    rng = random.Random(f"pong-{difficulty}-{bx:.1f}-{by:.1f}-{dx:.2f}-{dy:.2f}")
    wobble = rng.uniform(-noise, noise) * 0.5
    miss = rng.random() < miss_chance
    if miss:
        wobble += rng.choice([-1, 1]) * noise
    target_y = max(ai_height / 2 + 12, min(height - ai_height / 2 - 12, predicted + wobble))
    idle_frames = rng.randint(6, 14)
    return {"targetY": target_y, "miss": miss, "idle": idle_frames}

