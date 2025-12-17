from __future__ import annotations

import random

PALETTE = [
    "#9de8c7",
    "#a5b4fc",
    "#fcd34d",
    "#fb7185",
    "#6ee7ff",
]


def _physics_for_level(level: int, difficulty: str, rng: random.Random) -> dict[str, float]:
    difficulty_key = (difficulty or "medium").lower()
    base = {
        "easy": {
            "maxBounceDeg": 60.0,
            "paddleInfluence": 0.20,
            "spinFromPaddle": 0.016,
            "spinFromEdge": 0.14,
            "spinMagnus": 0.060,
            "spinDecay": 0.992,
            "maxSpin": 0.50,
            "speedUpBrick": 0.050,
            "speedUpLevel": 0.22,
            "maxSpeed": 8.2,
            "minSpeed": 3.0,
            "paddleSpeed": 8.3,
        },
        "medium": {
            "maxBounceDeg": 62.0,
            "paddleInfluence": 0.24,
            "spinFromPaddle": 0.020,
            "spinFromEdge": 0.18,
            "spinMagnus": 0.075,
            "spinDecay": 0.991,
            "maxSpin": 0.55,
            "speedUpBrick": 0.060,
            "speedUpLevel": 0.26,
            "maxSpeed": 8.7,
            "minSpeed": 3.2,
            "paddleSpeed": 8.6,
        },
        "hard": {
            "maxBounceDeg": 64.0,
            "paddleInfluence": 0.27,
            "spinFromPaddle": 0.023,
            "spinFromEdge": 0.20,
            "spinMagnus": 0.085,
            "spinDecay": 0.990,
            "maxSpin": 0.60,
            "speedUpBrick": 0.070,
            "speedUpLevel": 0.30,
            "maxSpeed": 9.2,
            "minSpeed": 3.4,
            "paddleSpeed": 9.0,
        },
    }.get(difficulty_key, {})

    lvl = max(1, int(level))
    progress = min(1.0, max(0.0, (lvl - 1) / 6))

    # Gentle per-level tuning (deterministic via seed).
    max_speed = base.get("maxSpeed", 8.7) + progress * 0.55 + rng.uniform(-0.05, 0.05)
    speed_up_brick = base.get("speedUpBrick", 0.06) + progress * 0.015 + rng.uniform(-0.004, 0.004)
    paddle_influence = (
        base.get("paddleInfluence", 0.24) + progress * 0.02 + rng.uniform(-0.01, 0.01)
    )

    return {
        "maxBounceDeg": base.get("maxBounceDeg", 62.0) + rng.uniform(-2.0, 2.0) * 0.35,
        "paddleInfluence": max(0.0, paddle_influence),
        "spinFromPaddle": max(0.0, base.get("spinFromPaddle", 0.02) + rng.uniform(-0.002, 0.002)),
        "spinFromEdge": max(0.0, base.get("spinFromEdge", 0.18) + rng.uniform(-0.02, 0.02)),
        "spinMagnus": max(0.0, base.get("spinMagnus", 0.075) + rng.uniform(-0.01, 0.01)),
        "spinDecay": min(
            0.999, max(0.95, base.get("spinDecay", 0.991) + rng.uniform(-0.002, 0.002))
        ),
        "maxSpin": max(0.0, base.get("maxSpin", 0.55) + rng.uniform(-0.04, 0.04)),
        "speedUpBrick": max(0.0, speed_up_brick),
        "speedUpLevel": max(0.0, base.get("speedUpLevel", 0.26) + rng.uniform(-0.03, 0.03) * 0.35),
        "maxSpeed": max(1.0, max_speed),
        "minSpeed": max(0.5, base.get("minSpeed", 3.2) + rng.uniform(-0.1, 0.1) * 0.2),
        "paddleSpeed": max(
            1.0, base.get("paddleSpeed", 8.6) + progress * 0.25 + rng.uniform(-0.1, 0.1)
        ),
    }


def level_layout(level: int, width: float, difficulty: str) -> dict[str, object]:
    rng = random.Random(f"breakout-{difficulty}-{level}-{width}")
    cols = 10
    rows = 4 + min(4, level)
    brick_width = width / cols
    brick_height = 24
    bricks: list[dict[str, object]] = []
    gap_col = rng.randint(0, cols - 1) if level > 1 else -1

    for row in range(rows):
        for col in range(cols):
            if col == gap_col and row % 2 == 1:
                continue
            hp = 1 + ((row + level) % 2)
            if level >= 3 and rng.random() < 0.2:
                hp += 1
            bricks.append(
                {
                    "x": col * brick_width + 4,
                    "y": row * (brick_height + 6) + 40,
                    "w": brick_width - 8,
                    "h": brick_height,
                    "hp": hp,
                    "color": PALETTE[(row + col) % len(PALETTE)],
                }
            )

    physics = _physics_for_level(level, difficulty, rng)
    return {"cols": cols, "rows": rows, "bricks": bricks, "physics": physics}
