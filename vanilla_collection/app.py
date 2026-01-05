"""
VANILLA Collection bootstrapper.

Launches the unified Flask backend (static files + game helper APIs) and
optionally opens the collection landing page in the browser.
"""

from __future__ import annotations

import contextlib
import os
import sys
import threading
import webbrowser
from pathlib import Path

# Allow running this file directly
if __name__ == "__main__" and __package__ is None:
    _parent = str(Path(__file__).resolve().parent.parent)
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    __package__ = "vanilla_collection"

from .server import GameServer


def _open_browser(url: str, delay: float = 1.0) -> None:
    """Open the given URL after a short delay to let the server start."""

    def _launch() -> None:
        with contextlib.suppress(Exception):
            webbrowser.open(url)

    timer = threading.Timer(delay, _launch)
    timer.daemon = True
    timer.start()


def run(
    host: str | None = None,
    port: int | None = None,
    debug: bool | None = None,
    scores_path: Path | None = None,
    auto_open: bool | None = None,
) -> None:
    server = GameServer(scores_path=scores_path)
    resolved_host: str = host or os.environ.get("HOST", "127.0.0.1") or "127.0.0.1"
    resolved_port = port if port is not None else int(os.environ.get("PORT", "8000"))
    resolved_debug = bool(
        debug if debug is not None else os.environ.get("DEBUG", "").lower() in {"1", "true", "yes"}
    )

    resolved_auto_open = (
        auto_open
        if auto_open is not None
        else os.environ.get("AUTO_OPEN", "1") not in {"0", "false", "no"}
    )
    if resolved_auto_open:
        target_host = "127.0.0.1" if resolved_host == "0.0.0.0" else resolved_host
        _open_browser(f"http://{target_host}:{resolved_port}/")

    print(f"Starting VANILLA app on {resolved_host}:{resolved_port} (debug={resolved_debug})")
    print(f"Static root: {server.root_dir}")
    print(f"Scores file: {server.store.path}")
    server.run(host=resolved_host, port=resolved_port, debug=resolved_debug)


if __name__ == "__main__":
    run()
