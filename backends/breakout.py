from __future__ import annotations

import random
from typing import Dict, List

PALETTE = [
    "#9de8c7",
    "#a5b4fc",
    "#fcd34d",
    "#fb7185",
    "#6ee7ff",
]


def level_layout(level: int, width: float, difficulty: str) -> Dict[str, object]:
    rng = random.Random(f"breakout-{difficulty}-{level}-{width}")
    cols = 10
    rows = 4 + min(4, level)
    brick_width = width / cols
    brick_height = 24
    bricks: List[Dict[str, object]] = []
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

    return {"cols": cols, "rows": rows, "bricks": bricks}

