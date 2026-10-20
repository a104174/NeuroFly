"""Derive engineering wing hinges from the immutable deployed V2-F glTF geometry.

No Blender/source asset is modified. Run:
.venv/bin/python tools/exports/build_wing_rig.py
Root candidates are the anterior wing cap (Z > .115); the ten vertices closest
to the torso define each visual hinge. These are artistic, not anatomical data.
"""

import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "web/public/assets/fly/fly_visual_v2f.glb"
OUTPUT = ROOT / "web/src/assets/fly_wings_v7_1.json"
SOURCE_HASH = "0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238"


def derive():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_HASH
    length = struct.unpack_from("<I", raw, 12)[0]
    gltf = json.loads(raw[20 : 20 + length])
    binary = raw[28 + length :]
    nodes = {n["name"]: n for n in gltf["nodes"] if "mesh" in n}

    def points(node):
        assert not any(
            k in node for k in ["matrix", "rotation", "scale", "translation"]
        )
        primitives = gltf["meshes"][node["mesh"]]["primitives"]
        assert len(primitives) == 1
        accessor = gltf["accessors"][primitives[0]["attributes"]["POSITION"]]
        assert accessor["type"] == "VEC3" and accessor["componentType"] == 5126
        view = gltf["bufferViews"][accessor["bufferView"]]
        start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        return [
            struct.unpack_from("<fff", binary, start + i * view.get("byteStride", 12))
            for i in range(accessor["count"])
        ]

    torso = points(nodes["Torso.Unseparated"])
    wings = []
    for side, sign in [("L", -1), ("R", 1)]:
        name = f"Wing.{side}"
        vertices = points(nodes[name])
        cap = [v for v in vertices if v[2] > 0.115]
        closest = sorted(cap, key=lambda v: min(math.dist(v, p) for p in torso))[:10]
        pivot = [sum(v[k] for v in closest) / len(closest) for k in range(3)]
        assert min(math.dist(pivot, p) for p in vertices) < 0.01
        assert min(math.dist(pivot, p) for p in torso) < 0.01
        wings.append(
            {
                "id": name,
                "sign": sign,
                "pivot": pivot,
                "vertices": len(vertices),
                "rest_matrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            }
        )
    return {
        "schema": "articulated_wing_motion_v7_1",
        "source_glb_sha256": SOURCE_HASH,
        "generator": "tools/exports/build_wing_rig.py",
        "classification": "ENGINEERING_FLIGHT_VISUAL_DEMO",
        "axes": "Y_UP_Z_FORWARD",
        "wings": wings,
        "animation": {
            "frequency_hz": 2,
            "stroke_rad": 0.45,
            "spread_rad": 0.95,
            "duration_s": 8,
            "takeoff_s": 1,
            "hover_s": 2.25,
            "landing_s": 5.75,
            "grounded_s": 7,
            "height": 0.18,
        },
        "attribution": (
            "Wildtype Male Drosophila Melanogaster by mlykouretzos, "
            "CC BY 4.0; original V2-F surfaces and materials preserved. "
            "Engineering hinges only."
        ),
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(derive(), indent=2) + "\n")
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
