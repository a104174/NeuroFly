"""Build and export NeuroFly's project-owned presentation fly asset.

Run with Blender, not the system Python interpreter:

    blender --background --factory-startup \
        --python tools/blender/export_fly_visual.py

Pass ``-- --output-root PATH`` to reproduce the complete source/export output
under a temporary root without modifying the repository artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ASSET_ID = "neurofly_fly_visual_v1"
ASSET_VERSION = 1
MANIFEST_SCHEMA = "neurofly_visual_asset_manifest_v1"
BLEND_RELATIVE_PATH = Path("assets/blender/fly_visual_v1.blend")
GLB_RELATIVE_PATH = Path("web/public/assets/fly/fly_visual_v1.glb")
MANIFEST_RELATIVE_PATH = Path("web/src/assets/fly_visual_v1.json")
PUBLIC_URL = "/assets/fly/fly_visual_v1.glb"
TRIANGLE_LIMIT = 20_000
MATERIAL_LIMIT = 6


def _arguments() -> argparse.Namespace:
    script_arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Root receiving the repository-relative source, GLB, and manifest paths.",
    )
    return parser.parse_args(script_arguments)


def _clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.actions,
        bpy.data.images,
    ):
        for datablock in list(datablocks):
            datablocks.remove(datablock)


def _material(name: str, color: tuple[float, float, float, float], roughness: float):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    material.diffuse_color = color
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Alpha"].default_value = color[3]
    if color[3] < 1 and hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    return material


def _apply_transform(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def _smooth(obj: bpy.types.Object) -> None:
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def _add_ellipsoid(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    *,
    rotation_z: float = 0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=12,
        location=location,
        rotation=(0, 0, rotation_z),
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    _apply_transform(obj)
    _smooth(obj)
    obj.data.materials.append(material)
    return obj


def _add_leg(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    material: bpy.types.Material,
) -> bpy.types.Object:
    start_vector = Vector(start)
    end_vector = Vector(end)
    direction = end_vector - start_vector
    midpoint = (start_vector + end_vector) / 2
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=0.012,
        depth=direction.length,
        location=midpoint,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction)
    _apply_transform(obj)
    _smooth(obj)
    obj.data.materials.append(material)
    return obj


def _build_asset() -> tuple[bpy.types.Object, list[bpy.types.Object]]:
    body_material = _material("Body", (0.055, 0.11, 0.12, 1.0), 0.64)
    eye_material = _material("Eyes", (0.34, 0.075, 0.045, 1.0), 0.42)
    wing_material = _material("Wings", (0.33, 0.52, 0.55, 0.38), 0.3)

    objects = [
        _add_ellipsoid("Thorax", (0, 0, 0), (0.19, 0.25, 0.17), body_material),
        _add_ellipsoid("Head", (0, -0.31, 0.015), (0.17, 0.16, 0.145), body_material),
        _add_ellipsoid(
            "Abdomen", (0, 0.29, -0.01), (0.145, 0.30, 0.125), body_material
        ),
        _add_ellipsoid(
            "Eye.L", (-0.115, -0.415, 0.035), (0.065, 0.055, 0.078), eye_material
        ),
        _add_ellipsoid(
            "Eye.R", (0.115, -0.415, 0.035), (0.065, 0.055, 0.078), eye_material
        ),
        _add_ellipsoid(
            "Wing.L",
            (-0.31, 0.015, 0.075),
            (0.31, 0.19, 0.022),
            wing_material,
            rotation_z=-0.2,
        ),
        _add_ellipsoid(
            "Wing.R",
            (0.31, 0.015, 0.075),
            (0.31, 0.19, 0.022),
            wing_material,
            rotation_z=0.2,
        ),
    ]

    leg_specs = (
        ("Leg.L.Front", (-0.13, -0.15, -0.08), (-0.40, -0.31, -0.18)),
        ("Leg.L.Middle", (-0.16, 0.0, -0.09), (-0.43, 0.0, -0.19)),
        ("Leg.L.Rear", (-0.13, 0.15, -0.08), (-0.39, 0.34, -0.18)),
        ("Leg.R.Front", (0.13, -0.15, -0.08), (0.40, -0.31, -0.18)),
        ("Leg.R.Middle", (0.16, 0.0, -0.09), (0.43, 0.0, -0.19)),
        ("Leg.R.Rear", (0.13, 0.15, -0.08), (0.39, 0.34, -0.18)),
    )
    objects.extend(
        _add_leg(name, start, end, body_material) for name, start, end in leg_specs
    )

    long_axis_min = min(
        obj.location.y + min(corner[1] for corner in obj.bound_box) for obj in objects
    )
    long_axis_max = max(
        obj.location.y + max(corner[1] for corner in obj.bound_box) for obj in objects
    )
    normalization = 1.0 / (long_axis_max - long_axis_min)
    for obj in objects:
        obj.location *= normalization
        obj.scale = (normalization, normalization, normalization)
        _apply_transform(obj)

    root = bpy.data.objects.new("NeuroFlyFlyVisualV1", None)
    bpy.context.scene.collection.objects.link(root)
    root["asset_id"] = ASSET_ID
    root["asset_version"] = ASSET_VERSION
    root["role"] = "NEUROFLY_VISUAL_ASSET"
    root["presentation_only"] = True
    for obj in objects:
        obj.parent = root

    return root, objects


def _runtime_bounds(objects: list[bpy.types.Object]) -> tuple[list[float], list[float]]:
    # Blender (X, Y, Z) converts to runtime glTF (X, Z, -Y) with export_yup.
    points = []
    for obj in objects:
        points.extend(
            (world.x, world.z, -world.y)
            for world in (obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
        )
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return minimum, maximum


def _triangle_count(objects: list[bpy.types.Object]) -> int:
    return sum(
        max(0, len(polygon.vertices) - 2)
        for obj in objects
        for polygon in obj.data.polygons
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _export(output_root: Path) -> None:
    output_root = output_root.resolve()
    blend_path = output_root / BLEND_RELATIVE_PATH
    glb_path = output_root / GLB_RELATIVE_PATH
    manifest_path = output_root / MANIFEST_RELATIVE_PATH
    for path in (blend_path, glb_path, manifest_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    _clear_scene()
    root, objects = _build_asset()
    triangle_count = _triangle_count(objects)
    used_materials = {
        material.name for obj in objects for material in obj.data.materials
    }
    bounds_min, bounds_max = _runtime_bounds(objects)
    if triangle_count > TRIANGLE_LIMIT:
        raise RuntimeError(
            f"Triangle budget exceeded: {triangle_count} > {TRIANGLE_LIMIT}"
        )
    if len(used_materials) > MATERIAL_LIMIT:
        raise RuntimeError(
            f"Material budget exceeded: {len(used_materials)} > {MATERIAL_LIMIT}"
        )

    scene = bpy.context.scene
    scene.name = "NeuroFlyFlyVisualV1"
    scene.unit_settings.system = "NONE"
    scene["scientific_status"] = "presentation_only"
    scene["canonical_origin"] = "thorax_center"
    scene["runtime_axes"] = "+Y up, +Z forward, -X left"

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)

    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        check_existing=False,
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_draco_mesh_compression_enable=False,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_yup=True,
        export_materials="EXPORT",
        export_texcoords=False,
        export_normals=True,
        export_tangents=False,
        export_colors=False,
    )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "asset_id": ASSET_ID,
        "asset_version": ASSET_VERSION,
        "role": "NEUROFLY_VISUAL_ASSET",
        "source": {
            "type": "BLENDER",
            "path": BLEND_RELATIVE_PATH.as_posix(),
            "provenance": (
                "Created in-project by the deterministic Phase 5C Blender script; "
                "no third-party model or texture was used."
            ),
        },
        "runtime": {
            "glb_path": GLB_RELATIVE_PATH.as_posix(),
            "public_url": PUBLIC_URL,
            "sha256": _sha256(glb_path),
        },
        "reuse": {
            "status": "PROJECT_CREATED_TERMS_UNSPECIFIED",
            "note": (
                "Project-created asset; the repository does not currently declare "
                "broader license terms."
            ),
        },
        "canonical_transform": {
            "source_up_axis": "+Z",
            "source_forward_axis": "-Y",
            "runtime_up_axis": "+Y",
            "runtime_forward_axis": "+Z",
            "runtime_left_axis": "-X",
            "origin": "thorax center",
            "normalized_scale": "runtime long-axis (+Z) extent is 1.0 asset unit",
            "scene_position": [0.0, 0.78, 0.0],
            "scene_rotation_euler_rad": [0.0, 0.0, 0.0],
            "scene_uniform_scale": 2.0,
        },
        "budget": {
            "triangle_limit": TRIANGLE_LIMIT,
            "material_limit": MATERIAL_LIMIT,
            "texture_image_limit": 0,
        },
        "measured": {
            "triangle_count": triangle_count,
            "material_count": len(used_materials),
            "animation_count": 0,
            "camera_count": 0,
            "light_count": 0,
            "texture_image_count": 0,
            "bounds_min": bounds_min,
            "bounds_max": bounds_max,
        },
        "export": {
            "tool": "Blender",
            "tool_version": bpy.app.version_string,
            "script": "tools/blender/export_fly_visual.py",
            "format": "GLB",
            "settings": {
                "selection_only": True,
                "object_transforms_applied_before_export": True,
                "export_apply": False,
                "draco_compression": False,
                "animations": False,
                "cameras": False,
                "lights": False,
                "textures": False,
                "runtime_y_up": True,
            },
        },
        "scientific_status": {
            "presentation_only": True,
            "disclaimer": (
                "Stylized project visual asset; not MaleCNS morphology, measured "
                "anatomy, an individual reconstruction, or a connectome-derived "
                "body model."
            ),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "blend": str(blend_path),
                "glb": str(glb_path),
                "manifest": str(manifest_path),
                "sha256": manifest["runtime"]["sha256"],
                "triangles": triangle_count,
                "materials": len(used_materials),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    _export(_arguments().output_root)
