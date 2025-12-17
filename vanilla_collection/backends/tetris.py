from __future__ import annotations


def config(difficulty: str) -> dict[str, int]:
    diff = (difficulty or "medium").lower().strip()

    presets = {
        "easy": {"level": 1, "gravityMs": 850, "lockDelayMs": 500, "dasMs": 140, "arrMs": 40},
        "medium": {"level": 5, "gravityMs": 650, "lockDelayMs": 450, "dasMs": 120, "arrMs": 35},
        "hard": {"level": 10, "gravityMs": 500, "lockDelayMs": 400, "dasMs": 105, "arrMs": 30},
    }

    preset = presets.get(diff) or presets["medium"]
    return dict(preset)
