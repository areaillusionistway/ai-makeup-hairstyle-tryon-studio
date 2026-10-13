"""Installs a global exception hook that dumps a traceback to disk.

Windows users close the console; without this a crash is invisible.
"""
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path


def install_crash_handler(crash_dir: Path) -> None:
    crash_dir.mkdir(parents=True, exist_ok=True)

    def _hook(exc_type, exc, tb):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = crash_dir / f"crash_{stamp}.log"
        with path.open("w", encoding="utf-8") as fh:
            fh.write(f"crash at {stamp}\n\n")
            traceback.print_exception(exc_type, exc, tb, file=fh)
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _hook