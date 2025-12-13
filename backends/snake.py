from __future__ import annotations

import random
from typing import Dict, Iterable, Set, Tuple


def _occupied(snake: Iterable[Dict[str, int]]) -> Set[Tuple[int, int]]:
    return {(int(seg.get("x", 0)), int(seg.get("y", 0))) for seg in snake}


def next_food(grid: int, snake: Iterable[Dict[str, int]]) -> Dict[str, int]:
    taken = _occupied(snake)
    rng = random.Random(f"snake-{grid}-{len(taken)}")
    open_spaces = [(x, y) for x in range(grid) for y in range(grid) if (x, y) not in taken]
    if not open_spaces:
        return {"x": 0, "y": 0}
    x, y = rng.choice(open_spaces)
    return {"x": x, "y": y}

