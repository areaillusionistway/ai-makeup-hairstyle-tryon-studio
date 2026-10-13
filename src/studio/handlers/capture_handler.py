"""Webcam capture wrapper. Owns the cv2.VideoCapture lifecycle."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import cv2

LOG = logging.getLogger("studio.capture")


class CaptureHandler:
    def __init__(self, device_index: int = 0) -> None:
        self._cap = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)
        if not self._cap.isOpened():
            LOG.warning("camera %s failed to open; preview will be blank", device_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def read(self):
        return self._cap.read()

    def save_snapshot(self, frame, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        name = datetime.now().strftime("tryon_%Y%m%d_%H%M%S.png")
        path = out_dir / name
        cv2.imwrite(str(path), frame)
        LOG.info("snapshot saved -> %s", path)
        return path

    def release(self) -> None:
        self._cap.release()