from __future__ import annotations

import random
from typing import Dict


def _physics(difficulty: str, rng: random.Random) -> Dict[str, float]:
    diff = (difficulty or "medium").lower()
    base = {
        "easy": {
            "maxBounceDeg": 52.0,
            "paddleInfluence": 0.10,
            "spinFromPaddle": 0.010,
            "spinFromEdge": 0.08,
            "spinCurvature": 0.040,
            "spinDecay": 0.992,
            "maxSpin": 0.65,
            "speedUpHit": 0.16,
            "maxSpeed": 7.2,
        },
        "medium": {
            "maxBounceDeg": 56.0,
            "paddleInfluence": 0.12,
            "spinFromPaddle": 0.012,
            "spinFromEdge": 0.10,
            "spinCurvature": 0.050,
            "spinDecay": 0.991,
            "maxSpin": 0.75,
            "speedUpHit": 0.18,
            "maxSpeed": 8.4,
        },
        "hard": {
            "maxBounceDeg": 60.0,
            "paddleInfluence": 0.14,
            "spinFromPaddle": 0.014,
            "spinFromEdge": 0.12,
            "spinCurvature": 0.060,
            "spinDecay": 0.990,
            "maxSpin": 0.85,
            "speedUpHit": 0.20,
            "maxSpeed": 9.4,
        },
    }.get(diff, {})

    return {
        "maxBounceDeg": base.get("maxBounceDeg", 56.0) + rng.uniform(-1.2, 1.2) * 0.4,
        "paddleInfluence": max(0.0, base.get("paddleInfluence", 0.12) + rng.uniform(-0.02, 0.02) * 0.4),
        "spinFromPaddle": max(0.0, base.get("spinFromPaddle", 0.012) + rng.uniform(-0.003, 0.003) * 0.35),
        "spinFromEdge": max(0.0, base.get("spinFromEdge", 0.10) + rng.uniform(-0.03, 0.03) * 0.35),
        "spinCurvature": max(0.0, base.get("spinCurvature", 0.05) + rng.uniform(-0.01, 0.01) * 0.35),
        "spinDecay": min(0.999, max(0.95, base.get("spinDecay", 0.991) + rng.uniform(-0.002, 0.002))),
        "maxSpin": max(0.0, base.get("maxSpin", 0.75) + rng.uniform(-0.08, 0.08) * 0.35),
        "speedUpHit": max(0.0, base.get("speedUpHit", 0.18) + rng.uniform(-0.04, 0.04) * 0.3),
        "maxSpeed": max(3.0, base.get("maxSpeed", 8.4) + rng.uniform(-0.4, 0.4) * 0.2),
    }


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
    physics = _physics(difficulty, rng)
    return {"targetY": target_y, "miss": miss, "idle": idle_frames, "physics": physics}
