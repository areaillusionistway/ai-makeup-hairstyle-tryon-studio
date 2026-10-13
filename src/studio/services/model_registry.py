"""Discovers and verifies model weight files on disk.

Weights are not shipped in the repo (too big). On first run the studio
checks ~/.tryon-studio/models and offers a download from the configured
mirror. This module is the single source of truth for what's installed.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

LOG = logging.getLogger("studio.registry")


@dataclass(frozen=True, slots=True)
class ModelSpec:
    key: str
    filename: str
    sha256: str
    size_mb: int


KNOWN_MODELS: tuple[ModelSpec, ...] = (
    ModelSpec("landmark", "face_landmark_v3.onnx", "a1b2c3", 46),
    ModelSpec("hair", "hair_seg_unet.onnx", "d4e5f6", 88),
    ModelSpec("makeup", "makeup_gan_v2.pt", "0f1e2d", 210),
)


class ModelRegistry:
    def __init__(self, model_dir: Path) -> None:
        self._dir = model_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def installed(self) -> dict[str, Path]:
        found: dict[str, Path] = {}
        for spec in KNOWN_MODELS:
            p = self._dir / spec.filename
            if p.exists():
                found[spec.key] = p
        return found

    def missing(self) -> list[ModelSpec]:
        return [s for s in KNOWN_MODELS if not (self._dir / s.filename).exists()]

    def verify(self, spec: ModelSpec) -> bool:
        p = self._dir / spec.filename
        if not p.exists():
            return False
        h = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        ok = h.hexdigest().startswith(spec.sha256)
        if not ok:
            LOG.warning("hash mismatch for %s", spec.filename)
        return ok