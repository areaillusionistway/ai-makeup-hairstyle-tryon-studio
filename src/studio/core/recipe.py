"""Makeup / hairstyle recipe model.

A recipe is the user-facing unit of work: a named style preset with a
reference image, a region mask spec, an intensity, and optional hair
dye color. Serialized to JSON in the user's presets folder.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Literal

import numpy as np

Region = Literal["lips", "eyes", "cheeks", "brows", "full_face", "hair"]


@dataclass(slots=True)
class MakeupRecipe:
    name: str
    region: Region
    intensity: float = 0.75
    reference_path: str = ""
    hair_tint_rgb: tuple[int, int, int] | None = None
    tags: list[str] = field(default_factory=list)

    _ref_cache: np.ndarray | None = field(default=None, repr=False, compare=False)

    @property
    def reference_rgb(self) -> np.ndarray:
        if self._ref_cache is None:
            from studio.utils.image_ops import load_image_rgb
            if not self.reference_path:
                raise ValueError(f"recipe {self.name!r} has no reference image")
            self._ref_cache = load_image_rgb(Path(self.reference_path))
        return self._ref_cache

    def to_json(self, path: Path) -> None:
        payload = asdict(self)
        payload.pop("_ref_cache", None)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: Path) -> "MakeupRecipe":
        data = json.loads(path.read_text(encoding="utf-8"))
        data.pop("_ref_cache", None)
        return cls(**data)