"""Round-trip and validation tests for MakeupRecipe serialization."""
from __future__ import annotations

import json

import pytest

from studio.core.recipe import MakeupRecipe


def test_recipe_roundtrip(tmp_path):
    r = MakeupRecipe(
        name="glam",
        region="lips",
        intensity=0.9,
        reference_path="C:/refs/glam.png",
        hair_tint_rgb=(180, 40, 90),
        tags=["evening", "bold"],
    )
    path = tmp_path / "glam.json"
    r.to_json(path)
    loaded = MakeupRecipe.from_json(path)

    assert loaded.name == "glam"
    assert loaded.region == "lips"
    assert abs(loaded.intensity - 0.9) < 1e-6
    assert loaded.hair_tint_rgb == (180, 40, 90)


def test_json_has_no_cache_field(tmp_path):
    r = MakeupRecipe(name="x", region="eyes")
    path = tmp_path / "x.json"
    r.to_json(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "_ref_cache" not in payload


def test_missing_reference_raises(tmp_path):
    r = MakeupRecipe(name="y", region="cheeks", reference_path="")
    with pytest.raises(ValueError):
        _ = r.reference_rgb