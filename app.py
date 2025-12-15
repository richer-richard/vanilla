"""
VANILLA Collection bootstrapper.

Launches the unified Flask backend (static files + game helper APIs) and
optionally opens the collection landing page in the browser.
"""

from __future__ import annotations

import os
import threading
import webbrowser
from typing import Optional
from server import GameServer

def _open_browser(url: str, delay: float = 1.0) -> None:
    """Open the given URL after a short delay to let the server start."""

    def _launch() -> None:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    timer = threading.Timer(delay, _launch)
    timer.daemon = True
    timer.start()

def run(host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None) -> None:
    server = GameServer()
    resolved_host = host or os.environ.get("HOST", "127.0.0.1")
    resolved_port = int(port or os.environ.get("PORT", 5000))
    resolved_debug = bool(debug if debug is not None else os.environ.get("DEBUG", "").lower() in {"1", "true", "yes"})

    if os.environ.get("AUTO_OPEN", "1") not in {"0", "false", "no"}:
        target_host = "127.0.0.1" if resolved_host == "0.0.0.0" else resolved_host
        _open_browser(f"http://{target_host}:{resolved_port}/index.html")

    print(f"Starting VANILLA app on {resolved_host}:{resolved_port} (debug={resolved_debug})")
    print(f"Static root: {server.root_dir}")
    print(f"Scores file: {server.store.path}")
    server.run(host=resolved_host, port=resolved_port, debug=resolved_debug)

if __name__ == "__main__":
    run()
