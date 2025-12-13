from __future__ import annotations

import random
from typing import Dict, List


def wave_plan(wave: int, difficulty: str, width: float, height: float) -> Dict[str, object]:
    rng = random.Random(f"{difficulty}-wave-{wave}")
    base_count = max(4, min(8, 3 + wave))
    enemies: List[Dict[str, object]] = []
    for _ in range(base_count):
        roll = rng.random()
        if roll > 0.8:
            kind = "bomber"
            pattern = "sway"
            hp = 2
        elif roll > 0.58:
            kind = "zig"
            pattern = "zigzag"
            hp = 2
        elif roll > 0.38:
            kind = "slicer"
            pattern = "strafe"
            hp = 1
        else:
            kind = "drone"
            pattern = "straight"
            hp = 1
        enemies.append(
            {
                "kind": kind,
                "pattern": pattern,
                "hp": hp,
                "x": rng.uniform(40, width - 40),
                "y": -rng.uniform(40, 160),
                "w": 34,
                "h": 24,
                "speed": rng.uniform(140, 220) + wave * 4,
                "phase": rng.random() * 6.28,
            }
        )

    powerups: List[Dict[str, object]] = []
    if rng.random() < 0.55:
        drop_type = "shield" if wave % 4 == 0 else rng.choice(["rapid", "double"])
        powerups.append(
            {
                "type": drop_type,
                "delay": rng.uniform(0.5, 1.6),
                "x": width * rng.uniform(0.25, 0.75),
            }
        )

    return {"wave": wave, "enemies": enemies, "powerups": powerups}

