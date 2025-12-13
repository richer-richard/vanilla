"""
Geometry Dash - Procedural Pattern Generator (VANILLA)

This backend generates lightweight obstacle chunks for the frontend runner.
The goal is to provide:
- Reproducible patterns (seeded by distance + difficulty)
- Clear difficulty scaling (density/complexity/beat)
- Visual theming hints (palette + theme name)

The Flask route in server.py calls:
    pattern(distance, difficulty, ground_y, width)
and returns the dict as JSON.
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Obstacle:
    type: str
    x: float
    y: float
    w: float
    h: float
    rotation: float = 0.0
    speed: float = 0.0
    kind: Optional[str] = None
    color: Optional[str] = None
    id: Optional[int] = None


DIFFICULTY_CONFIG: Dict[str, Dict[str, float]] = {
    "easy": {
        "density": 0.72,
        "complexity": 0.70,
        "portal_rate": 0.10,
        "orb_rate": 0.22,
        "saw_rate": 0.12,
        "bpm": 115,
    },
    "medium": {
        "density": 0.86,
        "complexity": 1.00,
        "portal_rate": 0.14,
        "orb_rate": 0.28,
        "saw_rate": 0.18,
        "bpm": 126,
    },
    "hard": {
        "density": 1.00,
        "complexity": 1.18,
        "portal_rate": 0.18,
        "orb_rate": 0.32,
        "saw_rate": 0.24,
        "bpm": 140,
    },
    "insane": {
        "density": 1.15,
        "complexity": 1.30,
        "portal_rate": 0.22,
        "orb_rate": 0.36,
        "saw_rate": 0.30,
        "bpm": 156,
    },
}


THEMES: Dict[str, Dict[str, str]] = {
    "neon": {
        "bg0": "#070a18",
        "bg1": "#0b1230",
        "accent": "#6ee7ff",
        "accent2": "#c084fc",
        "good": "#9de8c7",
        "danger": "#fb7185",
        "gold": "#fcd34d",
    },
    "cosmic": {
        "bg0": "#030615",
        "bg1": "#0b1d4d",
        "accent": "#93c5fd",
        "accent2": "#a78bfa",
        "good": "#67e8f9",
        "danger": "#f472b6",
        "gold": "#fde047",
    },
    "retro": {
        "bg0": "#0a0f27",
        "bg1": "#221043",
        "accent": "#34d399",
        "accent2": "#f59e0b",
        "good": "#22c55e",
        "danger": "#ef4444",
        "gold": "#eab308",
    },
    "ice": {
        "bg0": "#06121d",
        "bg1": "#04334f",
        "accent": "#7dd3fc",
        "accent2": "#a5b4fc",
        "good": "#99f6e4",
        "danger": "#fb7185",
        "gold": "#fcd34d",
    },
    "fire": {
        "bg0": "#160a0a",
        "bg1": "#3a0a0a",
        "accent": "#f97316",
        "accent2": "#fb7185",
        "good": "#fcd34d",
        "danger": "#ef4444",
        "gold": "#fbbf24",
    },
}


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _weighted_choice(rng: random.Random, weights: Dict[str, float]) -> str:
    items = [(k, max(0.0, float(w))) for k, w in weights.items()]
    total = sum(w for _, w in items)
    if total <= 0:
        return rng.choice([k for k, _ in items]) if items else "singles"
    pick = rng.random() * total
    for key, weight in items:
        pick -= weight
        if pick <= 0:
            return key
    return items[-1][0]


class DashGenerator:
    def __init__(self, seed: str, difficulty: str, ground_y: float, width: float, distance: float):
        self.rng = random.Random(seed)
        self.difficulty = difficulty
        self.config = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["medium"])
        self.ground_y = float(ground_y)
        self.width = float(width)

        height_est = self.ground_y + 72.0
        self.ceiling_y = _clamp(height_est * 0.105, 44.0, 72.0)

        self.base_x = self.width + 84.0
        self._local_id = 0
        chunk = int(distance // 110)
        self._id_base = chunk * 1000

    def _id(self) -> int:
        self._local_id += 1
        return self._id_base + self._local_id

    def spike(self, x: float, variant: str = "up") -> Obstacle:
        w, h = 34.0, 52.0
        if variant == "down":
            y = self.ceiling_y + 24.0
        else:
            y = self.ground_y - h
        return Obstacle("spike", x, y, w, h, kind=variant, id=self._id())

    def block(self, x: float, w: float = 76.0, h: float = 66.0) -> Obstacle:
        return Obstacle("block", x, self.ground_y - h, w, h, id=self._id())

    def platform(self, x: float, w: float = 150.0, y: Optional[float] = None) -> Obstacle:
        y_val = float(y) if y is not None else (self.ground_y - 170.0)
        y_val = _clamp(y_val, self.ceiling_y + 90.0, self.ground_y - 70.0)
        return Obstacle("platform", x, y_val, w, 16.0, id=self._id())

    def saw(self, x: float, y: Optional[float] = None, size: float = 52.0) -> Obstacle:
        y_val = float(y) if y is not None else (self.ground_y - 140.0)
        y_val = _clamp(y_val, self.ceiling_y + 64.0, self.ground_y - size - 32.0)
        return Obstacle("sawblade", x, y_val, size, size, speed=3.8 + self.rng.random() * 1.2, id=self._id())

    def orb(self, x: float, y: Optional[float] = None) -> Obstacle:
        y_val = float(y) if y is not None else (self.ground_y - 210.0)
        y_val = _clamp(y_val, self.ceiling_y + 70.0, self.ground_y - 120.0)
        return Obstacle("orb", x, y_val, 26.0, 26.0, kind="jump", id=self._id())

    def portal(self, x: float, kind: str = "gravity") -> Obstacle:
        # Tall, intentional hitbox so the portal is hard to miss.
        y = self.ceiling_y + 40.0
        h = max(120.0, (self.ground_y - self.ceiling_y) - 80.0)
        return Obstacle("portal", x, y, 44.0, h, kind=kind, color=kind, id=self._id())

    def pattern_singles(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        for _ in range(self.rng.randint(2, 4)):
            obs.append(self.spike(cursor))
            cursor += 98.0 + self.rng.random() * 42.0
        return obs, cursor - self.width

    def pattern_block_hop(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        obs.append(self.block(cursor, 84.0, 72.0))
        cursor += 140.0
        obs.append(self.spike(cursor))
        cursor += 115.0
        obs.append(self.block(cursor, 76.0, 64.0))
        cursor += 160.0
        return obs, cursor - self.width

    def pattern_orb_intro(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        obs.append(self.spike(cursor))
        obs.append(self.orb(cursor + 54.0, self.ground_y - 210.0))
        cursor += 170.0
        obs.append(self.platform(cursor, 150.0, self.ground_y - 180.0))
        obs.append(self.orb(cursor + 60.0, self.ground_y - 250.0))
        cursor += 220.0
        obs.append(self.spike(cursor))
        cursor += 160.0
        return obs, cursor - self.width

    def pattern_platform_chain(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        y1 = self.ground_y - 160.0
        y2 = self.ground_y - 205.0
        obs.append(self.platform(cursor, 150.0, y1))
        cursor += 190.0
        obs.append(self.platform(cursor, 130.0, y2))
        obs.append(self.spike(cursor + 140.0))
        cursor += 240.0
        obs.append(self.platform(cursor, 140.0, y1))
        if self.rng.random() < 0.5:
            obs.append(self.orb(cursor + 56.0, self.ground_y - 240.0))
        cursor += 210.0
        return obs, cursor - self.width

    def pattern_saw_line(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        obs.append(self.saw(cursor, self.ground_y - 150.0))
        cursor += 140.0
        obs.append(self.saw(cursor, self.ground_y - 200.0))
        cursor += 170.0
        obs.append(self.spike(cursor))
        cursor += 130.0
        if self.rng.random() < 0.55:
            obs.append(self.orb(cursor - 44.0, self.ground_y - 230.0))
        return obs, cursor - self.width

    def pattern_gravity_gate(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        obs.append(self.portal(cursor, "gravity"))
        cursor += 170.0
        # Ceiling section after gravity flip.
        obs.append(self.spike(cursor, "down"))
        cursor += 120.0
        obs.append(self.platform(cursor, 150.0, self.ceiling_y + 140.0))
        cursor += 210.0
        obs.append(self.spike(cursor, "down"))
        cursor += 160.0
        return obs, cursor - self.width

    def pattern_speed_gate(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        obs.append(self.portal(cursor, "speed"))
        cursor += 170.0
        obs.append(self.spike(cursor))
        cursor += 96.0
        obs.append(self.spike(cursor))
        cursor += 132.0
        obs.append(self.saw(cursor, self.ground_y - 160.0))
        cursor += 170.0
        return obs, cursor - self.width

    def pattern_gauntlet(self) -> Tuple[List[Obstacle], float]:
        obs: List[Obstacle] = []
        cursor = self.base_x
        obs.append(self.spike(cursor))
        cursor += 82.0
        obs.append(self.saw(cursor, self.ground_y - 165.0, 50.0))
        cursor += 150.0
        obs.append(self.block(cursor, 86.0, 72.0))
        cursor += 160.0
        obs.append(self.spike(cursor))
        obs.append(self.spike(cursor + 42.0))
        cursor += 200.0
        if self.rng.random() < self.config["orb_rate"]:
            obs.append(self.orb(cursor - 46.0, self.ground_y - 220.0))
        return obs, cursor - self.width


def pattern(distance: float, difficulty: str, ground_y: float, width: float) -> Dict:
    difficulty_key = (difficulty or "medium").strip().lower()
    config = DIFFICULTY_CONFIG.get(difficulty_key, DIFFICULTY_CONFIG["medium"])

    # Stage buckets in "meters" (frontend distance).
    dist = float(distance or 0)
    if dist < 120:
        stage = "intro"
    elif dist < 320:
        stage = "early"
    elif dist < 650:
        stage = "mid"
    elif dist < 1000:
        stage = "late"
    else:
        stage = "endgame"

    chunk = int(dist // 110)
    seed = f"vanilla-dash-{difficulty_key}-{chunk}"
    gen = DashGenerator(seed, difficulty_key, float(ground_y), float(width), dist)

    # Theme rotates every few chunks.
    theme_names = list(THEMES.keys())
    theme = theme_names[(chunk // 2) % len(theme_names)] if theme_names else "neon"
    palette = THEMES.get(theme, THEMES["neon"])

    # Pattern selection: stage-based with a difficulty "spice" factor.
    portal_bias = float(config["portal_rate"])
    saw_bias = float(config["saw_rate"])
    spice = float(config["complexity"])

    pools: Dict[str, Dict[str, float]] = {
        "intro": {
            "singles": 1.0,
            "block_hop": 0.7,
            "orb_intro": 0.5 * spice,
        },
        "early": {
            "singles": 0.8,
            "block_hop": 0.8,
            "orb_intro": 0.7 * spice,
            "platform_chain": 0.6 * spice,
        },
        "mid": {
            "platform_chain": 0.9,
            "saw_line": 0.55 + saw_bias,
            "orb_intro": 0.65 * spice,
            "gravity_gate": 0.35 + portal_bias,
        },
        "late": {
            "platform_chain": 0.85,
            "saw_line": 0.75 + saw_bias,
            "gauntlet": 0.70 * spice,
            "gravity_gate": 0.45 + portal_bias,
            "speed_gate": 0.40 + portal_bias,
        },
        "endgame": {
            "gauntlet": 1.05 * spice,
            "saw_line": 0.95 + saw_bias,
            "gravity_gate": 0.55 + portal_bias,
            "speed_gate": 0.55 + portal_bias,
            "platform_chain": 0.70,
        },
    }

    choice = _weighted_choice(gen.rng, pools.get(stage, pools["mid"]))
    methods = {
        "singles": gen.pattern_singles,
        "block_hop": gen.pattern_block_hop,
        "orb_intro": gen.pattern_orb_intro,
        "platform_chain": gen.pattern_platform_chain,
        "saw_line": gen.pattern_saw_line,
        "gravity_gate": gen.pattern_gravity_gate,
        "speed_gate": gen.pattern_speed_gate,
        "gauntlet": gen.pattern_gauntlet,
    }
    obstacles, pattern_width = methods.get(choice, gen.pattern_singles)()

    # Spawn spacing: pattern width + small randomized breathing room, scaled by density.
    density = float(config["density"])
    breathing = 90.0 + gen.rng.random() * 110.0
    next_spawn = max(170.0, pattern_width + breathing) / max(0.35, density)

    bpm = float(config["bpm"])
    beat_interval = 60000.0 / max(30.0, bpm)

    return {
        "obstacles": [asdict(ob) for ob in obstacles],
        "next_spawn": next_spawn,
        "theme": theme,
        "palette": palette,
        "beat_interval": beat_interval,
        "pattern_name": choice,
        "stage": stage,
    }


def get_difficulty_config(difficulty: str) -> Dict[str, float]:
    """Optional helper for clients that want difficulty metadata."""
    return dict(DIFFICULTY_CONFIG.get((difficulty or "medium").lower(), DIFFICULTY_CONFIG["medium"]))
