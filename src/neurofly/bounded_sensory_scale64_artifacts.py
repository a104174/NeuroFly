"""Immutable Phase 7L 64-body artifacts and content-addressed integrity checks."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.bounded_sensory_scale64 import (
    COMPOSITION_ARTIFACT_SCHEMA,
    COMPOSITION_CONFIG_SCHEMA,
    COMPOSITION_RESULT_SCHEMA,
    DEFAULT_COMPOSITION64_ROOT,
    DEFAULT_EXPERIMENT64_ROOT,
    DEFAULT_PLAN64_ROOT,
    DEFAULT_SAMPLE_C_ROOT,
    DEFAULT_SAMPLE_D_ROOT,
    EXPERIMENT_ARTIFACT_SCHEMA,
    EXPERIMENT_CONFIG_SCHEMA,
    EXPERIMENT_RESULT_SCHEMA,
    PLAN_ARTIFACT_SCHEMA,
    PLAN_CONFIG_SCHEMA,
    PLAN_RESULT_SCHEMA,
    POPULATION64_SIZE,
    SAMPLE64_SIZE,
    SAMPLE_ARTIFACT_SCHEMA,
    SAMPLE_CONFIG_SCHEMA,
    SAMPLE_RESULT_SCHEMA,
    scale64_artifact_id,
)
from neurofly.relative_column_assignment import canonical_json_bytes, sha256_bytes

MANIFEST_FILENAME = "manifest.json"
_KIND_SPECS = {
    "sample": (
        SAMPLE_ARTIFACT_SCHEMA,
        SAMPLE_CONFIG_SCHEMA,
        SAMPLE_RESULT_SCHEMA,
        "sample_config.json",
        "sample_result.json",
    ),
    "composition": (
        COMPOSITION_ARTIFACT_SCHEMA,
        COMPOSITION_CONFIG_SCHEMA,
        COMPOSITION_RESULT_SCHEMA,
        "composition_config.json",
        "composition_result.json",
    ),
    "plan": (
        PLAN_ARTIFACT_SCHEMA,
        PLAN_CONFIG_SCHEMA,
        PLAN_RESULT_SCHEMA,
        "coverage_plan_config.json",
        "coverage_plan_result.json",
    ),
    "experiment": (
        EXPERIMENT_ARTIFACT_SCHEMA,
        EXPERIMENT_CONFIG_SCHEMA,
        EXPERIMENT_RESULT_SCHEMA,
        "experiment_config.json",
        "experiment_result.json",
    ),
}
_ROOTS = {
    "sample_c": DEFAULT_SAMPLE_C_ROOT,
    "sample_d": DEFAULT_SAMPLE_D_ROOT,
    "composition": DEFAULT_COMPOSITION64_ROOT,
    "plan": DEFAULT_PLAN64_ROOT,
    "experiment": DEFAULT_EXPERIMENT64_ROOT,
}


class BoundedSensoryScale64ArtifactError(ValueError):
    """A Phase 7L artifact is malformed, tampered, or incomplete."""


@dataclass(frozen=True, slots=True)
class LoadedScale64Artifact:
    path: Path
    kind: str
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def as_input(self) -> dict[str, Any]:
        return {
            "artifact_schema": self.manifest["artifact_schema"],
            "artifact_id": self.artifact_id,
            "manifest_sha256": sha256_bytes(
                canonical_json_bytes(self.manifest) + b"\n"
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "config": self.config,
            "result": self.result,
            "manifest": self.manifest,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "artifact_schema": self.manifest["artifact_schema"],
            "artifact_id": self.artifact_id,
            "path": str(self.path),
            "body_count": len(self.result.get("body_ids", ())),
            "body_ids": self.result.get("body_ids", []),
            "stratum_counts": self.result.get("stratum_counts", []),
            "parent_artifact_ids": self.result.get(
                "parent_artifact_ids", self.result.get("excluded_prior_sample_ids", [])
            ),
            "stimulus_count": len(self.config.get("stimuli", ())),
            "condition_count": self.result.get("condition_count"),
            "coverage_totals": self.result.get("coverage_totals"),
            "artifact_bytes_including_manifest": sum(
                item.stat().st_size for item in self.path.iterdir()
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
        }


def _read_canonical(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise BoundedSensoryScale64ArtifactError(
            f"malformed Phase 7L {label}."
        ) from None
    if not isinstance(value, dict) or raw != canonical_json_bytes(value) + b"\n":
        raise BoundedSensoryScale64ArtifactError(
            f"Phase 7L {label} is not canonical JSON."
        )
    return value, raw


def _validate_payload(
    kind: str, config: dict[str, Any], result: dict[str, Any]
) -> None:
    try:
        _, config_schema, result_schema, _, _ = _KIND_SPECS[kind]
    except KeyError:
        raise BoundedSensoryScale64ArtifactError(
            "unknown Phase 7L artifact kind."
        ) from None
    if config.get("schema") != config_schema or result.get("schema") != result_schema:
        raise BoundedSensoryScale64ArtifactError(
            "unsupported Phase 7L artifact schema."
        )
    if kind == "sample":
        ids = result.get("body_ids", ())
        if (
            len(ids) != SAMPLE64_SIZE
            or len(set(ids)) != SAMPLE64_SIZE
            or result.get("sample_size") != SAMPLE64_SIZE
            or result.get("model_outcomes_used") is not False
            or config.get("model_outcomes_used") is not False
            or [row.get("count") for row in result.get("stratum_counts", ())]
            != [4, 4, 4, 4]
            or result.get("prior_overlap_count") != 0
        ):
            raise BoundedSensoryScale64ArtifactError(
                "invalid Phase 7L sample artifact."
            )
    elif kind == "composition":
        ids = result.get("body_ids", ())
        if (
            len(ids) != POPULATION64_SIZE
            or len(set(ids)) != POPULATION64_SIZE
            or result.get("sample_size") != POPULATION64_SIZE
            or result.get("pairwise_disjoint") is not True
            or len(result.get("pairwise_disjointness", ())) != 6
            or any(
                row.get("overlap_count") != 0 for row in result["pairwise_disjointness"]
            )
            or [row.get("count") for row in result.get("stratum_counts", ())]
            != [16, 16, 16, 16]
            or config.get("model_outcomes_used_for_composition") is not False
        ):
            raise BoundedSensoryScale64ArtifactError(
                "invalid 64-body composition artifact."
            )
    elif kind == "plan":
        if (
            len(result.get("body_ids", ())) != POPULATION64_SIZE
            or len(result.get("final_coverage", ())) != POPULATION64_SIZE
            or not all(
                row.get("body_stimulus_covered") for row in result["final_coverage"]
            )
            or result.get("model_outcomes_used") is not False
            or result.get("neural_dynamics_computed") is not False
            or config.get("model_outcomes_used_for_battery_design") is not False
            or config.get("neural_dynamics_computed") is not False
        ):
            raise BoundedSensoryScale64ArtifactError(
                "invalid anatomy-only 64-body plan."
            )
    else:
        totals = result.get("coverage_totals", {})
        if (
            len(result.get("body_ids", ())) != POPULATION64_SIZE
            or totals
            != {
                "body_stimulus_covered": 64,
                "body_state_exercised": 64,
                "body_transfer_exercised": 64,
                "denominator": 64,
            }
            or result.get("source_contribution_accounting_validated") is not True
            or result.get("parent_additivity_validated") is not True
            or config.get("body_count") != POPULATION64_SIZE
            or len(config.get("route_contract", ())) != POPULATION64_SIZE
            or result.get("condition_count") != len(result.get("conditions", ()))
        ):
            raise BoundedSensoryScale64ArtifactError(
                "incomplete 64-body experiment artifact."
            )


def load_scale64_artifact(path: str | Path, kind: str) -> LoadedScale64Artifact:
    try:
        artifact_schema, config_schema, result_schema, config_name, result_name = (
            _KIND_SPECS[kind]
        )
    except KeyError:
        raise BoundedSensoryScale64ArtifactError(
            "unknown Phase 7L artifact kind."
        ) from None
    root = Path(path)
    if not root.is_dir() or {item.name for item in root.iterdir()} != {
        config_name,
        result_name,
        MANIFEST_FILENAME,
    }:
        raise BoundedSensoryScale64ArtifactError(
            "Phase 7L artifact file set is invalid."
        )
    config, config_bytes = _read_canonical(root / config_name, "config")
    result, result_bytes = _read_canonical(root / result_name, "result")
    manifest, _ = _read_canonical(root / MANIFEST_FILENAME, "manifest")
    _validate_payload(kind, config, result)
    expected_id = scale64_artifact_id(kind, config, result)
    if (
        manifest.get("artifact_schema") != artifact_schema
        or manifest.get("artifact_id") != expected_id
        or manifest.get("config_sha256") != sha256_bytes(config_bytes)
        or manifest.get("result_sha256") != sha256_bytes(result_bytes)
        or manifest.get("body_ids") != result.get("body_ids")
        or config.get("schema") != config_schema
        or result.get("schema") != result_schema
        or config.get("body_ids") != result.get("body_ids")
    ):
        raise BoundedSensoryScale64ArtifactError(
            "Phase 7L integrity/identity mismatch."
        )
    return LoadedScale64Artifact(root, kind, expected_id, config, result, manifest)


def export_scale64_artifact(
    kind: str,
    config: dict[str, Any],
    result: dict[str, Any],
    *,
    output_root: str | Path | None = None,
) -> LoadedScale64Artifact:
    try:
        artifact_schema, _, _, config_name, result_name = _KIND_SPECS[kind]
    except KeyError:
        raise BoundedSensoryScale64ArtifactError(
            "unknown Phase 7L artifact kind."
        ) from None
    _validate_payload(kind, config, result)
    artifact_id = scale64_artifact_id(kind, config, result)
    root = Path(output_root) if output_root is not None else _ROOTS[kind]
    destination = root / artifact_id
    if destination.exists():
        existing = load_scale64_artifact(destination, kind)
        if existing.config != config or existing.result != result:
            raise BoundedSensoryScale64ArtifactError(
                "existing content-addressed Phase 7L artifact differs from replay."
            )
        return existing
    config_bytes = canonical_json_bytes(config) + b"\n"
    result_bytes = canonical_json_bytes(result) + b"\n"
    manifest = {
        "artifact_schema": artifact_schema,
        "artifact_id": artifact_id,
        "config_sha256": sha256_bytes(config_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "body_ids": result.get("body_ids", []),
    }
    payloads = (
        (config_name, config_bytes),
        (result_name, result_bytes),
        (MANIFEST_FILENAME, canonical_json_bytes(manifest) + b"\n"),
    )
    staging: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=destination.parent)
        )
        for filename, payload in payloads:
            with (staging / filename).open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        if destination.exists():
            raise BoundedSensoryScale64ArtifactError(
                "immutable artifact destination appeared."
            )
        os.replace(staging, destination)
        staging = None
    except OSError as exc:
        raise BoundedSensoryScale64ArtifactError(
            "could not persist Phase 7L artifact."
        ) from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_scale64_artifact(destination, kind)


def scale64_artifact_path(
    kind: str, artifact_id: str, *, sample_label: str | None = None
) -> Path:
    if kind == "sample":
        if sample_label not in {"C", "D"}:
            raise BoundedSensoryScale64ArtifactError("sample path needs C or D label.")
        root = _ROOTS[f"sample_{sample_label.lower()}"]
    else:
        try:
            root = _ROOTS[kind]
        except KeyError:
            raise BoundedSensoryScale64ArtifactError(
                "unknown Phase 7L artifact kind."
            ) from None
    return root / artifact_id
