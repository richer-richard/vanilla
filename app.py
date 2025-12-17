"""
Compatibility shim for running the VANILLA Collection from source.

The packaged implementation lives in `vanilla_collection.app`.
"""

from __future__ import annotations

from vanilla_collection.app import run

if __name__ == "__main__":
    run()

