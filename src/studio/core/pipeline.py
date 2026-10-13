"""Render pipeline: landmarks -> segmentation -> GAN blend -> compose.

Stages are pure functions over numpy arrays. The GAN stage is the only
one that hits torch; everything else is CPU numpy so preview stays
interactive even without CUDA.
"""
from __future__ import annotations

import numpy as np

from studio.models.face_landmarker import FaceLandmarker
from studio.models.hair_segmenter import HairSegmenter
from studio.models.makeup_gan import MakeupGan
from studio.config.settings import StudioSettings
from studio.utils.image_ops import resize_keep_ratio, bgr_to_rgb, rgb_to_bgr


class TryOnPipeline:
    def __init__(
        self,
        settings: StudioSettings,
        landmarker: FaceLandmarker,
        segmenter: HairSegmenter,
        gan: MakeupGan,
    ) -> None:
        self._settings = settings
        self._landmarker = landmarker
        self._segmenter = segmenter
        self._gan = gan

    def warmup(self) -> None:
        dummy = np.zeros((512, 512, 3), dtype=np.uint8)
        self._landmarker.detect(dummy)
        self._segmenter.mask(dummy)
        self._gan.transfer(dummy, dummy, strength=0.0)

    def apply(self, frame_bgr: np.ndarray, landmarks: np.ndarray, recipe) -> np.ndarray:
        work = resize_keep_ratio(frame_bgr, self._settings.render.working_size)
        rgb = bgr_to_rgb(work)
        hair_mask = self._segmenter.mask(rgb)
        styled = self._gan.transfer(
            rgb,
            recipe.reference_rgb,
            strength=recipe.intensity,
            hair_mask=hair_mask,
            region=recipe.region,
        )
        composed = rgb_to_bgr(styled)
        return resize_keep_ratio(composed, frame_bgr.shape[:2][::-1])