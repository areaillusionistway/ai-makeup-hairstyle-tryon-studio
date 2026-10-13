"""Makeup/hair transfer GAN wrapper (torch). Handles device placement
and mixed-precision inference on Windows.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import torch

LOG = logging.getLogger("studio.gan")


class MakeupGan:
    def __init__(self, model_path: Path, device: str | None = None) -> None:
        self._device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self._net = torch.jit.load(str(model_path), map_location=self._device)
        self._net.eval()
        LOG.info("makeup GAN loaded on %s", self._device)

    @torch.inference_mode()
    def transfer(
        self,
        rgb: np.ndarray,
        reference_rgb: np.ndarray,
        strength: float,
        hair_mask: np.ndarray | None = None,
        region: str = "full_face",
    ) -> np.ndarray:
        src = self._to_tensor(rgb)
        ref = self._to_tensor(reference_rgb)
        out = self._net(src, ref, strength=float(strength), region=region)
        blended = out.clamp(0, 1).squeeze(0).permute(1, 2, 0).cpu().numpy()
        blended = (blended * 255.0).astype(np.uint8)
        if hair_mask is not None and region == "hair":
            m = hair_mask[..., None]
            blended = (blended * m + rgb * (1 - m)).astype(np.uint8)
        return blended

    def _to_tensor(self, rgb: np.ndarray) -> torch.Tensor:
        t = torch.from_numpy(rgb.astype(np.float32) / 255.0)
        return t.permute(2, 0, 1).unsqueeze(0).to(self._device)