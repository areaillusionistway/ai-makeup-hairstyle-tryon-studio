"""Top-level try-on engine.

Owns the loaded face/hair models, the render pipeline, and the frame
cache. The UI talks to this and only this — never to the models
directly.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import numpy as np

from studio.core.pipeline import TryOnPipeline
from studio.models.face_landmarker import FaceLandmarker
from studio.models.hair_segmenter import HairSegmenter
from studio.models.makeup_gan import MakeupGan
from studio.config.settings import StudioSettings

LOG = logging.getLogger("studio.engine")


@dataclass(slots=True)
class FrameResult:
    composed: np.ndarray
    landmarks: np.ndarray
    latency_ms: float


class TryOnEngine:
    """Stateful engine; not thread-safe. UI thread owns one instance."""

    def __init__(self, settings: StudioSettings) -> None:
        self._settings = settings
        self._landmarker = FaceLandmarker(settings.models.landmark_model)
        self._segmenter = HairSegmenter(settings.models.hair_model)
        self._gan = MakeupGan(settings.models.makeup_model)
        self._pipeline = TryOnPipeline(settings, self._landmarker, self._segmenter, self._gan)
        self._warmed = False

    def warmup(self) -> None:
        """Run one dummy frame so first real click isn't 900ms."""
        if self._warmed:
            return
        t0 = time.perf_counter()
        self._pipeline.warmup()
        self._warmed = True
        LOG.info("warmup done in %.0fms", (time.perf_counter() - t0) * 1000)

    def process(self, frame_bgr: np.ndarray, recipe: "MakeupRecipe") -> FrameResult:
        t0 = time.perf_counter()
        landmarks = self._landmarker.detect(frame_bgr)
        composed = self._pipeline.apply(frame_bgr, landmarks, recipe)
        dt = (time.perf_counter() - t0) * 1000
        return FrameResult(composed=composed, landmarks=landmarks, latency_ms=dt)