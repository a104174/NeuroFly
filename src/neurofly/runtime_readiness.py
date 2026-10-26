"""Startup byte verification; probes do not replay scientific experiments."""

import os
from pathlib import Path

from neurofly.experiment_api import ExperimentApiError, ExperimentArtifactStore
from neurofly.recorded_experiments_runtime import COLLECTION_ROOT, REQUIRED_ARTIFACT_IDS
from neurofly.runtime_bundle import (
    INVENTORY_ID,
    RECORDED_INVENTORY_ID,
    verify_release,
)


def startup_readiness():
    mode = os.environ.get("NEUROFLY_RUNTIME_MODE", "local")
    state = {"mode": mode, "ready": False, "status": "LOCAL_UNVERIFIED"}
    if mode == "local":
        return state
    state["status"] = "RUNTIME_NOT_VERIFIED"
    try:
        if mode != "provisioned":
            raise ValueError("invalid runtime mode")
        root = Path(os.environ["NEUROFLY_RUNTIME_RELEASE_ROOT"]).resolve()
        inventory_id = os.environ["NEUROFLY_RUNTIME_INVENTORY_ID"]
        if inventory_id not in {INVENTORY_ID, RECORDED_INVENTORY_ID}:
            raise ValueError("inventory authority mismatch")
        if Path.cwd().resolve() != root:
            raise ValueError("frozen relative paths require release working directory")
        recorded = inventory_id == RECORDED_INVENTORY_ID
        version = 3 if recorded else 2
        inventory_path = root / f"docs/deployment_runtime_inventory_v{version}.json"
        wrapper = verify_release(
            root, os.environ["NEUROFLY_RUNTIME_MANIFEST_ID"], inventory_path
        )
        expected_roots = {
            "NEUROFLY_EXPERIMENT_ARTIFACT_ROOT": root
            / (COLLECTION_ROOT if recorded else "data/derived/experiments"),
            "NEUROFLY_CIRCUIT_CONTRACT_ROOT": root
            / "data/derived/malecns/looming_giant_fiber_v1",
        }
        for variable, expected in expected_roots.items():
            if (
                Path(os.environ[variable]).resolve() != expected
                or not expected.is_dir()
            ):
                raise ValueError("configured artifact root mismatch")
        if recorded:
            ExperimentArtifactStore(
                root / COLLECTION_ROOT, required_artifact_ids=REQUIRED_ARTIFACT_IDS
            ).discover_artifact_ids()
        if "NEUROFLY_SCENARIO_ARTIFACT_PATH" in os.environ:
            expected_scenarios = {
                (root / row["repository_relative_path"]).parent
                for row in wrapper["manifest"]["files"]
                if "/closed_loop_scenario_artifact_v1/"
                in row["repository_relative_path"]
            }
            configured_scenario = Path(
                os.environ["NEUROFLY_SCENARIO_ARTIFACT_PATH"]
            ).resolve()
            if expected_scenarios != {configured_scenario}:
                raise ValueError("canonical scenario root mismatch")
        for variable in (
            "NEUROFLY_SCENARIO_ARTIFACT_PATH",
            "NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT",
            "NEUROFLY_MOTOR_EXPERIMENT_ARTIFACT_ROOT",
        ):
            if variable in os.environ:
                path = Path(os.environ[variable]).resolve()
                if not path.is_relative_to(root) or not path.exists():
                    raise ValueError("configured artifact path outside release")
        state.update(
            ready=True,
            status="VERIFIED",
            inventory_id=inventory_id,
            manifest_id=wrapper["manifest_id"],
            file_count=wrapper["manifest"]["file_count"],
        )
    except (OSError, ValueError, KeyError, TypeError, ExperimentApiError):
        # No paths, environment values, storage URLs or secrets in public state.
        pass
    return state
