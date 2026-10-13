"""Desktop entry point for the AI Makeup / Hairstyle Try-On Studio.

Boots the Qt application, wires the DI container, and hands control to
the main window. Keeps process-level concerns (single-instance lock,
DPI awareness, crash logger install) out of the UI layer.
"""
from __future__ import annotations

import sys
import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from studio.core.di_container import Container
from studio.core.engine import TryOnEngine
from studio.handlers.window_handler import MainWindow
from studio.utils.crash_logger import install_crash_handler
from studio.config.settings import StudioSettings

LOG = logging.getLogger("studio.bootstrap")


def _configure_logging(settings: StudioSettings) -> None:
    log_dir = settings.paths.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "studio.log", encoding="utf-8"),
            logging.StreamHandler(sys.stderr),
        ],
    )


def main() -> int:
    settings = StudioSettings.load()
    _configure_logging(settings)
    install_crash_handler(settings.paths.crash_dir)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("AI Makeup / Hairstyle Try-On Studio")
    app.setOrganizationName("tryon-studio")

    container = Container(settings)
    container.register_singleton(TryOnEngine, TryOnEngine(settings))
    engine: TryOnEngine = container.resolve(TryOnEngine)
    engine.warmup()

    window = MainWindow(container)
    window.show()
    LOG.info("studio ready, models warmed, fps budget=%s", settings.render.target_fps)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())