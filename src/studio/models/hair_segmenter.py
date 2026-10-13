"""Hair region segmentation (U-Net ONNX). Returns a soft alpha mask."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort


class HairSegmenter:
    def __init__(self, model_path: Path) -> None:
        self._sess = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        self._input = self._sess.get_inputs()[0].name

    def mask(self, rgb: np.ndarray) -> np.ndarray:
        """Return (H, W) float32 in [0,1] hair probability."""
        h, w = rgb.shape[:2]
        blob = rgb.astype(np.float32).transpose(2, 0, 1)[None, ...] / 255.0
        out = self._sess.run(None, {self._input: blob})[0]
        mask = out.squeeze()
        import cv2
        return cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)