"""Main window: webcam preview, recipe sidebar, live controls.

Thin — it wires widgets to engine calls and never does image math
itself. If you're tempted to put numpy in here, put it in pipeline.
"""
from __future__ import annotations

import logging

import cv2
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider, QListWidget, QStatusBar,
)

from studio.core.di_container import Container
from studio.core.engine import TryOnEngine
from studio.core.recipe import MakeupRecipe
from studio.handlers.capture_handler import CaptureHandler

LOG = logging.getLogger("studio.window")


class MainWindow(QMainWindow):
    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._engine: TryOnEngine = container.resolve(TryOnEngine)
        self._capture = CaptureHandler(container.settings.capture.device_index)
        self._recipe = MakeupRecipe(name="default", region="full_face")

        self.setWindowTitle("AI Makeup / Hairstyle Try-On Studio")
        self.resize(1280, 800)
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_frame)
        self._timer.start(int(1000 / container.settings.capture.target_fps))

    def _build_ui(self) -> None:
        central = QWidget()
        root = QHBoxLayout(central)
        self._preview = QLabel("camera offline")
        self._preview.setMinimumSize(960, 720)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._preview, stretch=3)

        side = QVBoxLayout()
        side.addWidget(QLabel("Recipes"))
        self._recipes = QListWidget()
        self._recipes.addItems(["natural", "glam", "k-pop", "balayage", "bob-cut"])
        side.addWidget(self._recipes)

        side.addWidget(QLabel("Intensity"))
        self._intensity = QSlider(Qt.Orientation.Horizontal)
        self._intensity.setRange(0, 100)
        self._intensity.setValue(75)
        side.addWidget(self._intensity)

        snap = QPushButton("Snapshot")
        snap.clicked.connect(self._on_snapshot)
        side.addWidget(snap)
        root.addLayout(side, stretch=1)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())

    def _on_frame(self) -> None:
        ok, frame = self._capture.read()
        if not ok:
            return
        result = self._engine.process(frame, self._recipe)
        self._show(result.composed)
        self.statusBar().showMessage(f"{result.latency_ms:.0f} ms")

    def _show(self, bgr) -> None:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        img = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
        self._preview.setPixmap(QPixmap.fromImage(img))

    def _on_snapshot(self) -> None:
        ok, frame = self._capture.read()
        if ok:
            self._capture.save_snapshot(frame, self._container.settings.paths.snapshot_dir)