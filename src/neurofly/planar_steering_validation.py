"""Offline prescribed poses -> fixed HS/DNp15 kernels -> shadow-only readout.

Run with ``python -m neurofly.planar_steering_validation --output-root PATH``.
No API, autonomous plant, randomness or frontend integration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from neurofly import exploratory_course_control as course
from neurofly import planar_motion_observation as spatial
from neurofly.orientation_to_horizontal_motion import SideDescriptors
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ID = "HS_DNP15_PLANAR_STEERING_VALIDATION"
CONFIG_SCHEMA = "planar_steering_shadow_config_v1"
RESULT_SCHEMA = "planar_steering_shadow_result_v1"
ARTIFACT_SCHEMA = "planar_steering_shadow_artifact_v1"
RESULT_FILENAME = "shadow.json"


@dataclass(frozen=True, slots=True)
class PrescribedRun:
    condition_id: str
    geometry: spatial.VisualGeometry
    poses: tuple[spatial.PoseBoundary, ...]
    readout: Literal["ENABLED", "DISABLED"]
    control: str

    def __post_init__(self):
        if (
            type(self.geometry) is not spatial.VisualGeometry
            or type(self.poses) is not tuple
            or len(self.poses) != 501
            or any(type(p) is not spatial.PoseBoundary for p in self.poses)
            or any(
                p.index != n or p.time_ms != n * 0.1 for n, p in enumerate(self.poses)
            )
            or self.readout not in ("ENABLED", "DISABLED")
        ):
            raise ValueError("invalid or incomplete prescribed run/grid")


@dataclass(frozen=True, slots=True)
class ShadowReadout:
    computed_yaw_drive_eq: float
    proposed_increment_eq: float | None
    enabled_shadow_drive_eq: float
    classification: Literal["SHADOW_ONLY"] = "SHADOW_ONLY"
    applied_to_pose: Literal[False] = False


@dataclass(frozen=True, slots=True)
class ShadowBoundary:
    boundary_index: int
    time_ms: float
    pose: spatial.PoseBoundary
    observation: spatial.SpatialObservation | None
    sensory_descriptor: SideDescriptors
    hs_states: tuple[float, ...]
    dnp15_states: tuple[float, float]
    bilateral_differential: float
    route_contributions: tuple[float, ...] | None
    target_drives: tuple[float, float] | None
    readout: ShadowReadout
    validity: Literal["VALID"] = "VALID"


def prescribed_inputs(p: dict) -> tuple[PrescribedRun, ...]:
    if canonical_sha256(p) != spatial.PREREGISTRATION_ID:
        raise ValueError("modified prescribed condition/observation protocol")
    grid, recipe = p["grid"], p["pose_recipe"]
    runs = []
    for condition in p["conditions"]:
        geometry = spatial.VisualGeometry(
            tuple(spatial.Landmark(**v) for v in p["geometries"][condition["geometry"]])
        )
        dx, dz = condition["displacement_world_eq"]
        dh = condition["heading_change_eq"]
        poses = tuple(
            spatial.PoseBoundary(
                n,
                n * grid["dt_ms"],
                dx * min(n / recipe["motion_end_step"], 1),
                dz * min(n / recipe["motion_end_step"], 1),
                dh * min(n / recipe["motion_end_step"], 1),
            )
            for n in range(grid["boundary_count"])
        )
        runs.append(
            PrescribedRun(
                condition["id"],
                geometry,
                poses,
                condition["readout"],
                condition["control"],
            )
        )
    return tuple(runs)


def load_sources(p: dict) -> tuple[course.Components, dict]:
    """Verify full source authorities and numerical artifacts, never regenerate."""
    if canonical_sha256(p) != spatial.PREREGISTRATION_ID:
        raise ValueError("planar preregistration identity mismatch")
    for name, digest in p["frozen_kernel_files"].items():
        if (
            hashlib.sha256((REPO_ROOT / "src/neurofly" / name).read_bytes()).hexdigest()
            != digest
        ):
            raise ValueError("frozen neural/observation kernel source changed")
    cp = course.load_preregistration()
    components = course.load_components(cp)
    if (
        p["source_artifacts"] != cp["source_artifacts"]
        or p["authority_records"] != cp["authority_records"]
    ):
        raise ValueError("incompatible source model identities")
    authorities = {
        row["document"]: (course.SCIENCE_ROOT / row["document"]).read_text()
        for row in p["authority_records"]
    }
    artifacts = {}
    for key, root, replay in (
        ("phase25", course.NEURAL_ROOT, course.replay_neural_artifact),
        ("phase28", course.YAW_ROOT, course.replay_yaw_artifact),
    ):
        reference = p["source_artifacts"][key]
        path = root / reference["artifact_id"]
        source = replay(path)
        if any(
            source[k] != reference[k]
            for k in ("artifact_id", "config_sha256", "result_sha256", "schema")
        ):
            raise ValueError("numerical source authority mismatch")
        artifacts[key] = {
            **reference,
            "repository_relative_path": str(path),
            "config": source["config"],
        }
    definitions = {
        "authority_documents_utf8": authorities,
        "numerically_replayed_artifact_sources": artifacts,
        "neural_contract": components.neural_contract,
        "yaw_contract": components.embodiment_contract,
        "orientation_reference_contract": asdict(components.observation_contract),
    }
    return components, definitions


def _validate_components(components: course.Components) -> None:
    expected = course.load_components(course.load_preregistration())
    if type(components) is not course.Components or canonical_json_bytes(
        asdict(components)
    ) != canonical_json_bytes(asdict(expected)):
        raise ValueError("unsupported neural kernel, routes or parameter configuration")


def run_condition(
    inputs: PrescribedRun, p: dict, components: course.Components
) -> dict:
    """Immutable pose input; neural states cannot write to it at any boundary."""
    _validate_components(components)
    allowed = {r.condition_id: r for r in prescribed_inputs(p)}
    if type(inputs) is not PrescribedRun or inputs != allowed.get(inputs.condition_id):
        raise ValueError("unsupported intervention or prescribed input")
    sources, targets = [0.0] * 6, [0.0] * 2
    boundaries = []
    for n, pose in enumerate(inputs.poses):
        observed = (
            spatial.observe_interval(inputs.geometry, inputs.poses[n - 1], pose)
            if n
            else None
        )
        sides = observed.sides if observed else SideDescriptors(0.0, 0.0)
        last = n == len(inputs.poses) - 1
        dt = (
            inputs.poses[n + 1].time_ms - pose.time_ms
            if not last
            else p["grid"]["dt_ms"]
        )
        if not last:
            step = course.compose_neural_interval(
                sources, targets, sides, dt, components
            )
            drive = step["yaw_drive_eq"]
            proposal = step["proposed_orientation_increment_eq"]
        else:
            # Instantaneous readout only. No extra state update/outgoing interval.
            _, drives, _ = course.embodiment.integrate_orientation(
                [0, dt],
                [targets.copy(), targets.copy()],
                components.embodiment_contract,
            )
            drive, proposal = drives[0], None
        boundaries.append(
            asdict(
                ShadowBoundary(
                    n,
                    pose.time_ms,
                    pose,
                    observed,
                    sides,
                    tuple(sources),
                    tuple(targets),
                    targets[0] - targets[1],
                    None if last else tuple(step["route_contributions"]),
                    None if last else tuple(step["target_drives"]),
                    ShadowReadout(
                        drive, proposal, drive if inputs.readout == "ENABLED" else 0.0
                    ),
                )
            )
        )
        if not last:
            sources, targets = step["next_sources"], step["next_targets"]
    samples = [b["observation"] for b in boundaries[1:]]
    return {
        "condition_id": inputs.condition_id,
        "boundaries": boundaries,
        "termination": {
            "status": "COMPLETED_VALID_HORIZON",
            "step": 500,
            "time_ms": 50.0,
        },
        "diagnostics": {
            "peak_abs_hs": max(abs(v) for b in boundaries for v in b["hs_states"]),
            "peak_abs_dnp15": max(
                abs(v) for b in boundaries for v in b["dnp15_states"]
            ),
            "min_differential": min(b["bilateral_differential"] for b in boundaries),
            "max_differential": max(b["bilateral_differential"] for b in boundaries),
            "final_differential": boundaries[-1]["bilateral_differential"],
            "clipped_intervals": sum(
                any(s["clipped"] for s in o["samples"]) for o in samples
            ),
            "clipped_channel_samples": sum(
                s["clipped"] for o in samples for s in o["samples"]
            ),
            "observed_interval_count": len(samples),
            "body_updated_by_readout": False,
        },
    }


def evaluate_controls(runs: list[dict]) -> dict:
    """Preregistered expectations, not output-fitted effect-size thresholds."""
    by_id = {r["condition_id"]: r for r in runs}

    def rows(name):
        return by_id[name]["boundaries"]

    neutral = rows("STATIONARY_SYMMETRIC")
    positive = rows("TRANSLATION_Z_POSITIVE_ASYMMETRIC")
    negative = rows("TRANSLATION_Z_NEGATIVE_ASYMMETRIC")
    mirror = rows("MIRRORED_TRANSLATION_Z_POSITIVE_ASYMMETRIC")
    disabled = rows("READOUT_DISABLED_TRANSLATION_Z_POSITIVE_ASYMMETRIC")
    exact_zero = all(
        b["hs_states"] == (0.0,) * 6
        and b["dnp15_states"] == (0.0,) * 2
        and b["readout"]["computed_yaw_drive_eq"] == 0
        for b in neutral
    )
    mirrored = all(
        a["dnp15_states"] == tuple(reversed(b["dnp15_states"]))
        and a["bilateral_differential"] == -b["bilateral_differential"]
        for a, b in zip(positive, mirror, strict=True)
    )
    disconnected = all(
        all(a[k] == b[k] for k in a if k != "readout")
        and a["readout"]["computed_yaw_drive_eq"]
        == b["readout"]["computed_yaw_drive_eq"]
        and a["readout"]["proposed_increment_eq"]
        == b["readout"]["proposed_increment_eq"]
        and b["readout"]["enabled_shadow_drive_eq"] == 0
        for a, b in zip(positive, disabled, strict=True)
    )
    inputs = {
        r.condition_id: r for r in prescribed_inputs(spatial.load_preregistration())
    }
    gates = {
        "neutral_exact_zero": exact_zero,
        "symmetric_translation_common_mode_only": all(
            b["bilateral_differential"] == 0
            for name in (
                "TRANSLATION_Z_POSITIVE_SYMMETRIC",
                "TRANSLATION_Z_NEGATIVE_SYMMETRIC",
            )
            for b in rows(name)
        ),
        "asymmetric_signed_response": max(b["bilateral_differential"] for b in positive)
        > 0
        and min(b["bilateral_differential"] for b in negative) < 0,
        "mirror_target_swap": mirrored,
        "sham_identical": positive == rows("SHAM_TRANSLATION_Z_POSITIVE_ASYMMETRIC"),
        "readout_disconnection_only": disconnected,
        "rotation_sign": min(
            b["bilateral_differential"] for b in rows("ROTATION_POSITIVE")
        )
        < 0
        and max(b["bilateral_differential"] for b in rows("ROTATION_NEGATIVE")) > 0,
        "prescribed_poses_unchanged": all(
            b["pose"] == asdict(pose)
            for r in runs
            for b, pose in zip(
                r["boundaries"], inputs[r["condition_id"]].poses, strict=True
            )
        ),
        "no_pose_actuation": all(
            not b["readout"]["applied_to_pose"] for r in runs for b in r["boundaries"]
        ),
    }
    return {
        "gates": gates,
        "all_pass": all(gates.values()),
        "route_intervention": "UNAVAILABLE_IN_UNCHANGED_SIX_ROUTE_KERNEL",
    }


def build_shadow_artifact() -> dict:
    p = spatial.load_preregistration()
    components, definitions = load_sources(p)
    inputs = prescribed_inputs(p)
    software_files = {"src/neurofly/" + name for name in p["frozen_kernel_files"]}
    software_files |= {
        "src/neurofly/planar_motion_observation.py",
        "src/neurofly/planar_steering_validation.py",
    }
    config = {
        "schema": CONFIG_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "preregistration_id": spatial.PREREGISTRATION_ID,
        "preregistration": p,
        "source_definitions": definitions,
        "prescribed_inputs": [asdict(r) for r in inputs],
        "random_policy": "NONE",
        "seed": None,
        "software": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "implementation": platform.python_implementation(),
            "model_version": ARTIFACT_SCHEMA,
            "source_repository_head": p["source_repository_head"],
            "files_sha256": {
                name: hashlib.sha256((REPO_ROOT / name).read_bytes()).hexdigest()
                for name in sorted(software_files)
            },
        },
    }
    runs = [run_condition(r, p, components) for r in inputs]
    result = {
        "schema": RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "source_order": components.neural_contract["source_identities"],
        "target_order": components.neural_contract["target_identities"],
        "selected_routes": components.neural_contract["selected_routes"],
        "units": {
            "position": "world_eq",
            "heading": "heading_eq",
            "time": "ms",
            "sensory": "horizontal_motion_eq",
            "source": "dimensionless_signed_proxy",
            "target": "dnp15_state_eq",
            "drive": "yaw_drive_eq",
        },
        "runs": runs,
        "controls": evaluate_controls(runs),
        "readout_application": "SHADOW_ONLY",
        "propulsion": "NOT_DEFINED",
        "limitations": p["limitations"],
    }
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema": ARTIFACT_SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, ch, rh]),
    }


def validate_shadow_artifact(response: dict) -> dict:
    """Full deterministic replay also rejects semantically tampered/rehashed data."""
    expected = build_shadow_artifact()
    if canonical_json_bytes(response) != canonical_json_bytes(expected):
        raise ValueError("shadow artifact differs from complete validated replay")
    return expected


def _manifest(response: dict) -> dict:
    raw = canonical_json_bytes(response, newline=True)
    return {
        "schema": ARTIFACT_SCHEMA,
        **{k: response[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "files": {
            RESULT_FILENAME: {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        },
    }


def replay_shadow_artifact(path: Path) -> dict:
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("invalid shadow artifact file inventory")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        value = json.loads(raw)
        if raw != canonical_json_bytes(value, newline=True):
            raise ValueError("noncanonical shadow JSON")
        payloads.append(value)
    response, manifest = payloads
    if manifest != _manifest(response) or path.name != response["artifact_id"]:
        raise ValueError("shadow manifest/hash/directory mismatch")
    return validate_shadow_artifact(response)


def generate_shadow_artifact(output_root: Path) -> Path:
    root = Path(output_root).resolve()
    if root.is_relative_to(REPO_ROOT):
        raise ValueError(
            "new diagnostics must be stored outside the repository/runtime"
        )
    response = build_shadow_artifact()
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_shadow_artifact(destination)
        return destination
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".shadow-", dir=root))
    try:
        for name, content in (
            (RESULT_FILENAME, response),
            ("manifest.json", _manifest(response)),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(canonical_json_bytes(content, newline=True))
                stream.flush()
                os.fsync(stream.fileno())
        # No overwrite of a competing or previously approved artifact.
        os.rename(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--output-root", type=Path)
    operation.add_argument("--replay", type=Path)
    args = parser.parse_args(argv)
    try:
        path = args.replay or generate_shadow_artifact(args.output_root)
        response = replay_shadow_artifact(path)
        print(
            json.dumps(
                {
                    "path": str(path),
                    "artifact_id": response["artifact_id"],
                    "config_sha256": response["config_sha256"],
                    "result_sha256": response["result_sha256"],
                    "controls": response["result"]["controls"],
                },
                indent=2,
            )
        )
        return 0 if response["result"]["controls"]["all_pass"] else 1
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(1, f"Planar shadow validation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
