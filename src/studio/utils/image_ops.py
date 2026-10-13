"""Image helpers shared by pipeline and handlers. Pure numpy/cv2."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_image_rgb(path: Path) -> np.ndarray:
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(f"cannot read image: {path}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def bgr_to_rgb(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def rgb_to_bgr(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


def resize_keep_ratio(img: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    tw, th = size
    h, w = img.shape[:2]
    scale = min(tw / w, th / h)
    nw, nh = int(w * scale), int(h * scale)
    return cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)


def blend_masks(base: np.ndarray, overlay: np.ndarray, mask: np.ndarray) -> np.ndarray:
    m = mask[..., None].astype(np.float32)
    return (overlay.astype(np.float32) * m + base.astype(np.float32) * (1 - m)).astype(np.uint8)