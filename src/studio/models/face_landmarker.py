"""ONNX face landmark detection (68-point or 478-point depending on model)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort


class FaceLandmarker:
    def __init__(self, model_path: Path, providers: list[str] | None = None) -> None:
        providers = providers or ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self._sess = ort.InferenceSession(str(model_path), providers=providers)
        self._input = self._sess.get_inputs()[0].name

    def detect(self, frame_bgr: np.ndarray) -> np.ndarray:
        """Return (N, 2) landmark coordinates in original frame space."""
        h, w = frame_bgr.shape[:2]
        blob = self._preprocess(frame_bgr)
        out = self._sess.run(None, {self._input: blob})[0]
        pts = out.reshape(-1, 2)
        pts[:, 0] *= w
        pts[:, 1] *= h
        return pts

    @staticmethod
    def _preprocess(frame_bgr: np.ndarray) -> np.ndarray:
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (256, 256)).astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        rgb = (rgb - mean) / std
        return rgb.transpose(2, 0, 1)[None, ...]