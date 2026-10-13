"""Tests for pure-numpy image helpers."""
from __future__ import annotations

import numpy as np

from studio.utils.image_ops import blend_masks, resize_keep_ratio


def test_resize_keep_ratio_preserves_aspect():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    out = resize_keep_ratio(img, (50, 50))
    assert out.shape[0] == 25
    assert out.shape[1] == 50


def test_blend_masks_full_overlay():
    base = np.zeros((4, 4, 3), dtype=np.uint8)
    overlay = np.full((4, 4, 3), 255, dtype=np.uint8)
    mask = np.ones((4, 4), dtype=np.float32)
    out = blend_masks(base, overlay, mask)
    assert out.min() == 255


def test_blend_masks_zero_overlay():
    base = np.full((4, 4, 3), 128, dtype=np.uint8)
    overlay = np.zeros((4, 4, 3), dtype=np.uint8)
    mask = np.zeros((4, 4), dtype=np.float32)
    out = blend_masks(base, overlay, mask)
    assert out.max() == 128