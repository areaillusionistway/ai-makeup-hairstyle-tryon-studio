"""Export composed frames to PNG/JPG and recipe metadata sidecars."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


class ExportService:
    def __init__(self, export_dir: Path) -> None:
        self._dir = export_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def export(self, frame_bgr: np.ndarray, recipe, fmt: str = "png") -> Path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = self._dir / f"tryon_{stamp}"
        img_path = base.with_suffix(f".{fmt}")
        cv2.imwrite(str(img_path), frame_bgr)
        meta = {
            "recipe": recipe.name,
            "region": recipe.region,
            "intensity": recipe.intensity,
            "exported_at": stamp,
        }
        base.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return img_path