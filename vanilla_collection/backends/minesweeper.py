from __future__ import annotations

import random


def generate_board(rows: int, cols: int, mines: int, safe: tuple[int, int]) -> dict[str, object]:
    rng = random.Random(f"mines-{rows}-{cols}-{mines}-{safe}")
    safe_r, safe_c = safe
    safe_zone = {(safe_r + dr, safe_c + dc) for dr in range(-1, 2) for dc in range(-1, 2)}
    positions = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in safe_zone]
    rng.shuffle(positions)
    chosen = positions[:min(len(positions), mines)]

    counts = [[0 for _ in range(cols)] for _ in range(rows)]
    for r, c in chosen:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    counts[nr][nc] += 1

    return {"mines": chosen, "counts": counts}

