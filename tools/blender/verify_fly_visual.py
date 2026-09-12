"""Verify the tracked Phase 5C visual-asset manifest and GLB integrity."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA = "neurofly_visual_asset_manifest_v1"
EXPECTED_ASSET_ID = "neurofly_fly_visual_v1"
EXPECTED_ASSET_VERSION = 1
MANIFEST_RELATIVE_PATH = Path("web/src/assets/fly_visual_v1.json")


class AssetVerificationError(ValueError):
    """Raised when the tracked presentation asset is inconsistent."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_glb_json(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    if len(payload) < 20:
        raise AssetVerificationError("GLB is too short.")
    magic, version, declared_length = struct.unpack_from("<4sII", payload, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(payload):
        raise AssetVerificationError("GLB header is invalid.")
    json_length, chunk_type = struct.unpack_from("<I4s", payload, 12)
    if chunk_type != b"JSON" or 20 + json_length > len(payload):
        raise AssetVerificationError("GLB JSON chunk is invalid.")
    return json.loads(payload[20 : 20 + json_length].rstrip(b" \x00"))


def _triangle_count(glb: dict[str, Any]) -> int:
    accessors = glb.get("accessors", [])
    triangles = 0
    for mesh in glb.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            if primitive.get("mode", 4) != 4 or "indices" not in primitive:
                raise AssetVerificationError(
                    "Every primitive must be indexed triangles."
                )
            count = accessors[primitive["indices"]]["count"]
            if count % 3:
                raise AssetVerificationError(
                    "Triangle index count is not divisible by three."
                )
            triangles += count // 3
    return triangles


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssetVerificationError(message)


def verify_asset(root: Path) -> dict[str, Any]:
    root = root.resolve()
    manifest_path = root / MANIFEST_RELATIVE_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _require(manifest.get("schema") == EXPECTED_SCHEMA, "Unexpected manifest schema.")
    _require(manifest.get("asset_id") == EXPECTED_ASSET_ID, "Unexpected asset ID.")
    _require(
        manifest.get("asset_version") == EXPECTED_ASSET_VERSION,
        "Unexpected asset version.",
    )
    _require(manifest.get("role") == "NEUROFLY_VISUAL_ASSET", "Unexpected asset role.")
    _require(
        manifest.get("scientific_status", {}).get("presentation_only") is True,
        "Asset must be presentation-only.",
    )

    runtime = manifest["runtime"]
    glb_relative_path = Path(runtime["glb_path"])
    _require(
        not glb_relative_path.is_absolute(), "GLB path must be repository-relative."
    )
    _require(
        ".." not in glb_relative_path.parts,
        "GLB path cannot traverse outside the root.",
    )
    glb_path = root / glb_relative_path
    _require(glb_path.is_file(), "GLB file is missing.")
    _require(
        _sha256(glb_path) == runtime["sha256"],
        "GLB SHA-256 does not match the manifest.",
    )

    glb = _load_glb_json(glb_path)
    measured = manifest["measured"]
    budget = manifest["budget"]
    actual_triangles = _triangle_count(glb)
    _require(
        actual_triangles == measured["triangle_count"],
        "Triangle count does not match the GLB.",
    )
    _require(
        len(glb.get("materials", [])) == measured["material_count"],
        "Material count mismatch.",
    )
    _require(
        len(glb.get("animations", [])) == measured["animation_count"] == 0,
        "Asset must have no animations.",
    )
    _require(
        len(glb.get("cameras", [])) == measured["camera_count"] == 0,
        "Asset must have no cameras.",
    )
    lights = glb.get("extensions", {}).get("KHR_lights_punctual", {}).get("lights", [])
    _require(len(lights) == measured["light_count"] == 0, "Asset must have no lights.")
    _require(
        len(glb.get("images", [])) == measured["texture_image_count"] == 0,
        "Asset must have no images.",
    )
    _require(actual_triangles <= budget["triangle_limit"], "Triangle budget exceeded.")
    _require(
        measured["material_count"] <= budget["material_limit"],
        "Material budget exceeded.",
    )

    bounds_min = measured["bounds_min"]
    bounds_max = measured["bounds_max"]
    _require(len(bounds_min) == len(bounds_max) == 3, "Bounds must have three axes.")
    extents = [
        maximum - minimum
        for minimum, maximum in zip(bounds_min, bounds_max, strict=True)
    ]
    _require(
        all(math.isfinite(value) and value > 0 for value in extents),
        "Bounds must be finite and non-zero.",
    )
    _require(
        math.isclose(extents[2], 1.0, rel_tol=0, abs_tol=1e-6),
        "Runtime long axis must be one asset unit.",
    )

    return {
        "asset_id": manifest["asset_id"],
        "asset_version": manifest["asset_version"],
        "sha256": runtime["sha256"],
        "bytes": glb_path.stat().st_size,
        "triangles": actual_triangles,
        "materials": measured["material_count"],
        "animations": measured["animation_count"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    result = verify_asset(parser.parse_args().root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
