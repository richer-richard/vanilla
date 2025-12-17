from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .app import run


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="vanilla-collection", description="Run the VANILLA Collection server.")

    parser.add_argument("--host", default=None, help="Bind host (default: 127.0.0.1 or $HOST)")
    parser.add_argument("--port", type=int, default=None, help="Bind port (default: 5000 or $PORT)")

    debug_group = parser.add_mutually_exclusive_group()
    debug_group.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    debug_group.add_argument("--no-debug", action="store_true", help="Disable Flask debug mode")

    open_group = parser.add_mutually_exclusive_group()
    open_group.add_argument("--open", dest="auto_open", action="store_true", help="Open browser on start")
    open_group.add_argument("--no-open", dest="auto_open", action="store_false", help="Do not open browser on start")
    parser.set_defaults(auto_open=None)

    parser.add_argument(
        "--scores",
        default=None,
        help="Path to scores JSON (default: user data dir or $VANILLA_SCORES_PATH)",
    )

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

    debug: Optional[bool]
    if getattr(args, "debug", False):
        debug = True
    elif getattr(args, "no_debug", False):
        debug = False
    else:
        debug = None

    scores_path = Path(args.scores).expanduser() if args.scores else None

    run(
        host=args.host,
        port=args.port,
        debug=debug,
        scores_path=scores_path,
        auto_open=args.auto_open,
    )
    return 0

