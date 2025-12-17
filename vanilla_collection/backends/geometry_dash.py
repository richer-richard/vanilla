"""
Geometry Dash - Procedural Pattern Generator (VANILLA)

This backend generates lightweight obstacle chunks for the frontend runner.
The goal is to provide:
- Reproducible patterns (seeded by distance + difficulty)
- Clear difficulty scaling (density/complexity/beat)
- Visual theming hints (palette + theme name)
- Balanced level design with platforms, orbs, portals, and finish lines

The Flask route in server.py calls:
    pattern(distance, difficulty, ground_y, width)
and returns the dict as JSON.
"""

from __future__ import annotations

import hashlib
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
        "density": 0.65,
        "complexity": 0.60,
        "portal_rate": 0.08,
        "orb_rate": 0.35,
        "saw_rate": 0.08,
        "platform_rate": 0.45,
        "spike_max": 2,
        "bpm": 110,
    },
    "medium": {
        "density": 0.78,
        "complexity": 0.85,
        "portal_rate": 0.12,
        "orb_rate": 0.32,
        "saw_rate": 0.14,
        "platform_rate": 0.38,
        "spike_max": 3,
        "bpm": 124,
    },
    "hard": {
        "density": 0.92,
        "complexity": 1.05,
        "portal_rate": 0.16,
        "orb_rate": 0.28,
        "saw_rate": 0.20,
        "platform_rate": 0.32,
        "spike_max": 3,
        "bpm": 138,
    },
    "insane": {
        "density": 1.05,
        "complexity": 1.20,
        "portal_rate": 0.20,
        "orb_rate": 0.25,
        "saw_rate": 0.26,
        "platform_rate": 0.28,
        "spike_max": 4,
        "bpm": 152,
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
        return rng.choice([k for k, _ in items]) if items else "platform_run"
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
        self.distance = float(distance)

        # Calculate usable ceiling - leave more room for player
        height_est = self.ground_y + 72.0
        self.ceiling_y = _clamp(height_est * 0.12, 50.0, 80.0)
        
        # Safe zone bounds - player should have room to maneuver
        self.safe_top = self.ceiling_y + 100  # Don't put obstacles too high
        self.safe_bottom = self.ground_y - 60  # Ground level obstacles

        self.base_x = self.width + 100.0
        self._local_id = 0
        chunk = int(distance // 150)
        self._id_base = chunk * 1000

    def _id(self) -> int:
        self._local_id += 1
        return self._id_base + self._local_id

    def spike(self, x: float, variant: str = "up") -> Obstacle:
        w, h = 32.0, 48.0
        if variant == "down":
            y = self.ceiling_y + 30.0
        else:
            y = self.ground_y - h
        return Obstacle("spike", x, y, w, h, kind=variant, id=self._id())

    def block(self, x: float, w: float = 72.0, h: float = 60.0) -> Obstacle:
        return Obstacle("block", x, self.ground_y - h, w, h, id=self._id())

    def platform(self, x: float, w: float = 140.0, y: Optional[float] = None) -> Obstacle:
        # Platforms should be reachable with a single jump
        y_val = float(y) if y is not None else (self.ground_y - 140.0)
        y_val = _clamp(y_val, self.safe_top, self.ground_y - 100.0)
        return Obstacle("platform", x, y_val, w, 18.0, id=self._id())

    def saw(self, x: float, y: Optional[float] = None, size: float = 48.0) -> Obstacle:
        y_val = float(y) if y is not None else (self.ground_y - 120.0)
        y_val = _clamp(y_val, self.safe_top + 20, self.ground_y - size - 40.0)
        return Obstacle("sawblade", x, y_val, size, size, speed=3.5 + self.rng.random() * 1.0, id=self._id())

    def orb(self, x: float, y: Optional[float] = None) -> Obstacle:
        # Orbs help player navigate - place them where jumps are needed
        y_val = float(y) if y is not None else (self.ground_y - 180.0)
        y_val = _clamp(y_val, self.safe_top + 30, self.ground_y - 100.0)
        return Obstacle("orb", x, y_val, 28.0, 28.0, kind="jump", id=self._id())

    def portal(self, x: float, kind: str = "gravity") -> Obstacle:
        # Portals are tall to be easy to hit
        y = self.ceiling_y + 60.0
        h = max(100.0, (self.ground_y - self.ceiling_y) - 120.0)
        return Obstacle("portal", x, y, 48.0, h, kind=kind, color=kind, id=self._id())

    def pad(self, x: float) -> Obstacle:
        # Jump pads on ground for auto-bounce
        return Obstacle("pad", x, self.ground_y - 20.0, 60.0, 20.0, kind="jump", id=self._id())

    def finish_line(self, x: float) -> Obstacle:
        # Finish line marker at end of level sections
        return Obstacle("finish", x, self.ceiling_y, 20.0, self.ground_y - self.ceiling_y, kind="finish", id=self._id())

    # ===================
    # PATTERN GENERATORS
    # ===================

    def pattern_platform_run(self) -> Tuple[List[Obstacle], float]:
        """Easy pattern: platforms with gaps, orbs to help"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        # Platform chain with orbs
        for i in range(3):
            y_offset = self.ground_y - 130.0 - (i * 30)
            obs.append(self.platform(cursor, 130.0, y_offset))
            if self.rng.random() < 0.6:
                obs.append(self.orb(cursor + 50, y_offset - 60))
            cursor += 180.0 + self.rng.random() * 40
        
        return obs, cursor - self.width

    def pattern_single_spike(self) -> Tuple[List[Obstacle], float]:
        """Simple: single spikes with gaps"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        spike_count = self.rng.randint(1, int(self.config.get("spike_max", 2)))
        for _ in range(spike_count):
            obs.append(self.spike(cursor))
            cursor += 120.0 + self.rng.random() * 60  # Good gap between spikes
        
        return obs, cursor - self.width

    def pattern_spike_gap(self) -> Tuple[List[Obstacle], float]:
        """Two spikes with a platform/orb to help"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        obs.append(self.spike(cursor))
        cursor += 80
        
        # Add orb to help with jump
        obs.append(self.orb(cursor + 30, self.ground_y - 170))
        cursor += 100
        
        obs.append(self.spike(cursor))
        cursor += 140
        
        return obs, cursor - self.width

    def pattern_block_hop(self) -> Tuple[List[Obstacle], float]:
        """Blocks to jump over with safe landings"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        obs.append(self.block(cursor, 70.0, 55.0))
        cursor += 160
        
        # Safe gap
        cursor += 80
        
        obs.append(self.block(cursor, 65.0, 50.0))
        cursor += 180
        
        return obs, cursor - self.width

    def pattern_orb_chain(self) -> Tuple[List[Obstacle], float]:
        """Orbs guide the player through a section"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        # Gap with orbs to navigate
        obs.append(self.spike(cursor))
        obs.append(self.orb(cursor + 60, self.ground_y - 180))
        cursor += 130
        
        obs.append(self.platform(cursor, 120, self.ground_y - 160))
        obs.append(self.orb(cursor + 50, self.ground_y - 220))
        cursor += 180
        
        obs.append(self.spike(cursor))
        cursor += 150
        
        return obs, cursor - self.width

    def pattern_platform_jump(self) -> Tuple[List[Obstacle], float]:
        """Platform sequence - player must jump between platforms"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        y1 = self.ground_y - 140.0
        y2 = self.ground_y - 180.0
        
        obs.append(self.platform(cursor, 140.0, y1))
        cursor += 170
        
        obs.append(self.platform(cursor, 120.0, y2))
        obs.append(self.orb(cursor + 50, y2 - 55))
        cursor += 160
        
        obs.append(self.platform(cursor, 130.0, y1))
        cursor += 200
        
        return obs, cursor - self.width

    def pattern_saw_dodge(self) -> Tuple[List[Obstacle], float]:
        """Sawblades with safe paths"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        # Saw with orb to help pass
        obs.append(self.saw(cursor, self.ground_y - 130.0, 44.0))
        obs.append(self.orb(cursor - 30, self.ground_y - 200))
        cursor += 180
        
        # Safe gap
        cursor += 100
        
        obs.append(self.saw(cursor, self.ground_y - 160.0, 44.0))
        cursor += 180
        
        return obs, cursor - self.width

    def pattern_gravity_portal(self) -> Tuple[List[Obstacle], float]:
        """Gravity flip section - designed to be passable"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        # Gravity portal
        obs.append(self.portal(cursor, "gravity"))
        cursor += 200
        
        # After flip, player is on ceiling - add platform to land on
        obs.append(self.platform(cursor, 150.0, self.ceiling_y + 100))
        cursor += 180
        
        # Orb to help navigate back
        obs.append(self.orb(cursor, self.ceiling_y + 160))
        cursor += 120
        
        # Another gravity flip to return to normal
        obs.append(self.portal(cursor, "gravity"))
        cursor += 220
        
        return obs, cursor - self.width

    def pattern_speed_portal(self) -> Tuple[List[Obstacle], float]:
        """Speed boost section with simple obstacles"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        obs.append(self.portal(cursor, "speed"))
        cursor += 180
        
        # Simple spike - player has more speed so needs reaction time
        obs.append(self.spike(cursor))
        cursor += 150
        
        # Orb for next jump
        obs.append(self.orb(cursor, self.ground_y - 180))
        cursor += 120
        
        obs.append(self.spike(cursor))
        cursor += 200
        
        return obs, cursor - self.width

    def pattern_checkpoint(self) -> Tuple[List[Obstacle], float]:
        """Rest/checkpoint area with finish line marker"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        # Easy platform run
        obs.append(self.platform(cursor, 200.0, self.ground_y - 120))
        cursor += 240
        
        # Coins/orbs as reward
        obs.append(self.orb(cursor, self.ground_y - 160))
        cursor += 80
        obs.append(self.orb(cursor, self.ground_y - 160))
        cursor += 120
        
        # Finish line marker every ~1000m
        if self.distance > 0 and int(self.distance) % 800 < 150:
            obs.append(self.finish_line(cursor))
            cursor += 60
        
        return obs, cursor - self.width

    def pattern_pad_bounce(self) -> Tuple[List[Obstacle], float]:
        """Jump pad auto-bounces player over obstacles"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        obs.append(self.pad(cursor))
        cursor += 100
        
        # Block that pad helps jump over
        obs.append(self.block(cursor, 80, 70))
        cursor += 160
        
        # Landing platform
        obs.append(self.platform(cursor, 130, self.ground_y - 140))
        cursor += 200
        
        return obs, cursor - self.width

    def pattern_mixed_easy(self) -> Tuple[List[Obstacle], float]:
        """Mixed elements, easy difficulty"""
        obs: List[Obstacle] = []
        cursor = self.base_x
        
        # Block
        obs.append(self.block(cursor, 60, 50))
        cursor += 140
        
        # Orb mid-air
        obs.append(self.orb(cursor, self.ground_y - 170))
        cursor += 80
        
        # Platform
        obs.append(self.platform(cursor, 120, self.ground_y - 150))
        cursor += 180
        
        # Single spike at end
        obs.append(self.spike(cursor))
        cursor += 160
        
        return obs, cursor - self.width


def pattern(distance: float, difficulty: str, ground_y: float, width: float) -> Dict:
    difficulty_key = (difficulty or "medium").strip().lower()
    config = DIFFICULTY_CONFIG.get(difficulty_key, DIFFICULTY_CONFIG["medium"])

    # Stage buckets determine pattern selection
    dist = float(distance or 0)
    if dist < 200:
        stage = "intro"
    elif dist < 500:
        stage = "early"
    elif dist < 900:
        stage = "mid"
    elif dist < 1400:
        stage = "late"
    else:
        stage = "endgame"

    chunk = int(dist // 150)
    seed = f"vanilla-dash-{difficulty_key}-{chunk}"
    gen = DashGenerator(seed, difficulty_key, float(ground_y), float(width), dist)

    # Theme rotates every few chunks
    theme_names = list(THEMES.keys())
    theme = theme_names[(chunk // 3) % len(theme_names)] if theme_names else "neon"
    palette = THEMES.get(theme, THEMES["neon"])

    # Pattern pools by stage - emphasize playability
    platform_rate = float(config.get("platform_rate", 0.40))
    orb_rate = float(config.get("orb_rate", 0.30))
    portal_rate = float(config.get("portal_rate", 0.10))
    
    pools: Dict[str, Dict[str, float]] = {
        "intro": {
            "platform_run": 1.2,
            "single_spike": 0.8,
            "checkpoint": 0.5,
            "mixed_easy": 0.6,
        },
        "early": {
            "platform_run": 1.0 + platform_rate,
            "single_spike": 0.7,
            "spike_gap": 0.6,
            "block_hop": 0.5,
            "orb_chain": 0.6 + orb_rate,
            "checkpoint": 0.3,
        },
        "mid": {
            "platform_jump": 0.9 + platform_rate,
            "orb_chain": 0.8 + orb_rate,
            "spike_gap": 0.6,
            "saw_dodge": 0.5,
            "block_hop": 0.5,
            "gravity_portal": 0.3 + portal_rate,
            "checkpoint": 0.25,
        },
        "late": {
            "platform_jump": 0.8 + platform_rate,
            "saw_dodge": 0.7,
            "orb_chain": 0.75 + orb_rate,
            "gravity_portal": 0.4 + portal_rate,
            "speed_portal": 0.35 + portal_rate,
            "pad_bounce": 0.4,
            "checkpoint": 0.2,
        },
        "endgame": {
            "saw_dodge": 0.8,
            "gravity_portal": 0.5 + portal_rate,
            "speed_portal": 0.45 + portal_rate,
            "platform_jump": 0.7 + platform_rate,
            "orb_chain": 0.65 + orb_rate,
            "pad_bounce": 0.5,
            "checkpoint": 0.15,
        },
    }

    choice = _weighted_choice(gen.rng, pools.get(stage, pools["mid"]))
    
    methods = {
        "platform_run": gen.pattern_platform_run,
        "single_spike": gen.pattern_single_spike,
        "spike_gap": gen.pattern_spike_gap,
        "block_hop": gen.pattern_block_hop,
        "orb_chain": gen.pattern_orb_chain,
        "platform_jump": gen.pattern_platform_jump,
        "saw_dodge": gen.pattern_saw_dodge,
        "gravity_portal": gen.pattern_gravity_portal,
        "speed_portal": gen.pattern_speed_portal,
        "checkpoint": gen.pattern_checkpoint,
        "pad_bounce": gen.pattern_pad_bounce,
        "mixed_easy": gen.pattern_mixed_easy,
    }
    
    obstacles, pattern_width = methods.get(choice, gen.pattern_platform_run)()

    # Spawn spacing - ensure player has breathing room
    density = float(config.get("density", 0.75))
    breathing = 120.0 + gen.rng.random() * 100.0
    next_spawn = max(220.0, pattern_width + breathing) / max(0.45, density)

    bpm = float(config.get("bpm", 120))
    beat_interval = 60000.0 / max(40.0, bpm)

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
