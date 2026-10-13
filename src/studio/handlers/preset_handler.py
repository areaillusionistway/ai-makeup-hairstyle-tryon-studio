"""Loads and saves recipe presets from the user's presets folder."""
from __future__ import annotations

from pathlib import Path

from studio.core.recipe import MakeupRecipe


class PresetHandler:
    def __init__(self, preset_dir: Path) -> None:
        self._dir = preset_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def list_presets(self) -> list[str]:
        return sorted(p.stem for p in self._dir.glob("*.json"))

    def load(self, name: str) -> MakeupRecipe:
        return MakeupRecipe.from_json(self._dir / f"{name}.json")

    def save(self, recipe: MakeupRecipe) -> Path:
        path = self._dir / f"{recipe.name}.json"
        recipe.to_json(path)
        return path