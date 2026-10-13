"""Studio settings: paths, render budget, capture device, model paths.

Loaded from %APPDATA%/tryon-studio/settings.toml if present, else
defaults. Frozen dataclasses so nothing mutates config at runtime.
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Paths:
    root: Path
    model_dir: Path
    preset_dir: Path
    snapshot_dir: Path
    export_dir: Path
    log_dir: Path
    crash_dir: Path


@dataclass(frozen=True, slots=True)
class ModelPaths:
    landmark_model: Path
    hair_model: Path
    makeup_model: Path


@dataclass(frozen=True, slots=True)
class RenderConfig:
    working_size: tuple[int, int] = (512, 512)
    target_fps: int = 30


@dataclass(frozen=True, slots=True)
class CaptureConfig:
    device_index: int = 0
    target_fps: int = 30


@dataclass(frozen=True, slots=True)
class StudioSettings:
    paths: Paths
    models: ModelPaths
    render: RenderConfig = field(default_factory=RenderConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    log_level: str = "INFO"

    @classmethod
    def load(cls) -> "StudioSettings":
        root = Path(os.environ.get("APPDATA", Path.home())) / "tryon-studio"
        root.mkdir(parents=True, exist_ok=True)
        cfg = root / "settings.toml"
        if cfg.exists():
            data = tomllib.loads(cfg.read_text(encoding="utf-8"))
            log_level = data.get("log_level", "INFO")
            device = int(data.get("capture", {}).get("device_index", 0))
        else:
            log_level, device = "INFO", 0

        paths = Paths(
            root=root,
            model_dir=root / "models",
            preset_dir=root / "presets",
            snapshot_dir=root / "snapshots",
            export_dir=root / "exports",
            log_dir=root / "logs",
            crash_dir=root / "crashes",
        )
        models = ModelPaths(
            landmark_model=paths.model_dir / "face_landmark_v3.onnx",
            hair_model=paths.model_dir / "hair_seg_unet.onnx",
            makeup_model=paths.model_dir / "makeup_gan_v2.pt",
        )
        return cls(
            paths=paths,
            models=models,
            capture=CaptureConfig(device_index=device),
            log_level=log_level,
        )