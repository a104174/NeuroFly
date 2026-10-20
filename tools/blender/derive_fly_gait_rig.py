"""Derive presentation-only leg rig metadata from the immutable V2-F GLB.

blender -b --factory-startup --python tools/blender/derive_fly_gait_rig.py
No source .blend or GLB is overwritten. Coordinates below are artist-selected
engineering pivots in glTF (+Y up, +Z forward), not measured biological joints.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "web/public/assets/fly/fly_visual_v2f.glb"
OUTPUT = ROOT / "web/src/assets/fly_gait_v6.json"
PIVOTS = {
    "Front": [
        [-0.035, -0.023, 0.163],
        [-0.075, 0.055, 0.215],
        [-0.184, -0.218, 0.303],
        [-0.210, -0.245, 0.361],
    ],
    "Middle": [
        [-0.071, 0.018, 0.128],
        [-0.169, 0.055, 0.113],
        [-0.238, -0.158, 0.090],
        [-0.310, -0.237, 0.067],
    ],
    "Rear": [
        [-0.029, -0.012, 0.060],
        [-0.158, 0.060, -0.055],
        [-0.256, -0.222, -0.238],
        [-0.313, -0.281, -0.287],
    ],
}


def runtime(point):
    return Vector((point.x, point.z, -point.y))


def tree(points):
    result = KDTree(len(points))
    for index, point in enumerate(points):
        result.insert(point, index)
    result.balance()
    return result


def main():
    assert (
        hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        == "0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238"
    )
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))
    objects = {obj.name: obj for obj in bpy.data.objects}
    bodies = tree(
        [
            runtime(obj.matrix_world @ v.co)
            for obj in objects.values()
            if obj.name.startswith(("Torso", "Head", "Wing", "Eye"))
            and obj.type == "MESH"
            for v in obj.data.vertices
        ]
    )
    legs = []
    for side in ["L", "R"]:
        for segment, points in PIVOTS.items():
            name = f"Leg.{side}.{segment}"
            obj = objects[name]
            vertices = [runtime(obj.matrix_world @ v.co) for v in obj.data.vertices]
            pivots = [[p[0] * (1 if side == "L" else -1), p[1], p[2]] for p in points]
            assert all(
                min((Vector(p) - v).length for v in vertices) < 0.025 for p in pivots
            )
            legs.append(
                {
                    "id": name,
                    "tripod": int((side == "L") != (segment == "Middle")),
                    "pivots": pivots,
                    "vertices": len(vertices),
                    "details": [],
                    "tree": tree(vertices),
                }
            )
    for obj in objects.values():
        if obj.type != "MESH" or not obj.name.startswith("Detail"):
            continue
        vertices = [runtime(obj.matrix_world @ v.co) for v in obj.data.vertices]
        center = sum(vertices, Vector()) / len(vertices)
        distances = [
            (leg["tree"].find(center)[2], index) for index, leg in enumerate(legs)
        ]
        distance, index = min(distances)
        if distance < 0.02 and distance < bodies.find(center)[2] * 0.9:
            legs[index]["details"].append(obj.name)
    for leg in legs:
        del leg["tree"]
        leg["details"].sort()
    record = {
        "schema": "engineering_fly_gait_rig_v6",
        "source_glb_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_url": "/assets/fly/fly_visual_v2f.glb",
        "generator": "tools/blender/derive_fly_gait_rig.py",
        "axes": "Y_UP_Z_FORWARD",
        "anchor": [0, 0.06168119236826897, 0.12187743186950684],
        "legs": legs,
        "animation": {
            "stride": 0.055,
            "swing_height": 0.012,
            "stance_fraction": 0.62,
            "turn_radius": 0.065,
            "motion_threshold": 0.0000001,
            "settle_s": 0.18,
            "floor_y": 0.006,
            "joint_blend_asset": 0.018,
            "reach_fraction": 0.998,
            "max_hip_deviation_rad": 1.8,
            "max_knee_bend_rad": 2.65,
        },
        "classification": (
            "ENGINEERING_KINEMATIC_GAIT_NOT_CONNECTOME_DERIVED_LEG_CONTROL"
        ),
        "attribution": (
            "Wildtype Male Drosophila Melanogaster by mlykouretzos, CC BY 4.0. "
            "V2-F surfaces/materials preserved; NeuroFly adds artist-selected "
            "pivots and procedural skinning."
        ),
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
    }
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                "rig": str(OUTPUT),
                "legs": len(legs),
                "bones": 18,
                "attached_detail_meshes": sum(len(leg["details"]) for leg in legs),
                "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
            }
        )
    )


if __name__ == "__main__":
    main()
