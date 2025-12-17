from __future__ import annotations

import os
import sys
from pathlib import Path


def web_root() -> Path:
    override = os.environ.get("VANILLA_WEB_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return (Path(__file__).resolve().parent / "web").resolve()


def default_data_dir() -> Path:
    override = os.environ.get("VANILLA_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))

    return (base / "vanilla-collection").resolve()


def default_scores_path() -> Path:
    override = os.environ.get("VANILLA_SCORES_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return default_data_dir() / "scores.json"
