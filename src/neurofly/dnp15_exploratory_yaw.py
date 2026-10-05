"""Frozen, open-loop model-space orientation; no biomechanics or v1 changes."""

import json
import math
from pathlib import Path

from neurofly.hs_dnp15_neural_validation import (
    PREREGISTRATION_ID as SOURCE_PREREGISTRATION_ID,
)
from neurofly.hs_dnp15_neural_validation import SCIENCE_ROOT
from neurofly.hs_dnp15_neural_validation_artifacts import (
    DEFAULT_ARTIFACT_ROOT as SOURCE_ROOT,
)
from neurofly.hs_dnp15_neural_validation_artifacts import replay_neural_artifact
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

GATE_ID = "42d46ef3e5deed0c36da518cc1523cfe3d0978e5cbed2aac85a9738fcdeadf2f"
PREREGISTRATION_ID = "1be0f6364070a5a5536f4c772bd47abb3be2f08357b439a51e03f034f8b2a654"
SOURCE_ID = "2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113"
MODEL_SCHEMA = "exploratory_yaw_orientation_plant_v1"
CONFIG_SCHEMA = "dnp15_exploratory_yaw_config_v1"
RESULT_SCHEMA = "dnp15_exploratory_yaw_result_v1"
ARTIFACT_SCHEMA = "dnp15_exploratory_yaw_artifact_v1"
GATE_PATH = SCIENCE_ROOT / "dnp15_yaw_mapping_evidence_gate.json"
PREREGISTRATION_PATH = SCIENCE_ROOT / "dnp15_exploratory_yaw_preregistration.json"


def load_evidence_gate(path=GATE_PATH):
    wrapper = json.loads(Path(path).read_bytes())
    gate = wrapper["gate"]
    if (
        set(wrapper) != {"schema", "gate_id", "gate"}
        or wrapper["schema"] != "dnp15_yaw_mapping_evidence_gate_v1"
        or wrapper["gate_id"] != GATE_ID
        or canonical_sha256(gate) != GATE_ID
        or gate["stage_a"]["decision"] != "EXPLORATORY_YAW_MAPPING_IDENTIFIABLE"
        or gate["stage_a"]["stage_b_permitted"] is not True
        or gate["authorities"]["phase25_artifact_id"] != SOURCE_ID
    ):
        raise ValueError("frozen qualitative yaw evidence gate mismatch")
    return gate


def load_preregistration(path=PREREGISTRATION_PATH):
    contract = json.loads(Path(path).read_bytes())
    gate = load_evidence_gate()
    if (
        canonical_sha256(contract) != PREREGISTRATION_ID
        or contract["evidence_gate_id"] != GATE_ID
        or contract["source_artifact_id"] != SOURCE_ID
        or contract["source_preregistration_id"] != SOURCE_PREREGISTRATION_ID
        or contract["target_identities"]
        != [
            {"body_id": 11215, "type": "DNp15", "side": "R"},
            {"body_id": 12069, "type": "DNp15", "side": "L"},
        ]
        or gate["body_mapping_readiness"] != "QUALITATIVE_YAW_MAPPING_JUSTIFIED"
    ):
        raise ValueError("frozen exploratory orientation preregistration mismatch")
    return contract


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def integrate_orientation(times, target_states, contract):
    """Pure bounded interval integration; accepts no structural contact inputs.

    Numerical validation uses synthetic inputs only in focused tests. Production
    consumes replay-validated canonical Phase25 trajectories with frozen config.
    """
    if (
        not isinstance(times, list)
        or len(times) < 2
        or any(not _finite(t) for t in times)
        or times[0] != 0
        or any(b <= a for a, b in zip(times[:-1], times[1:], strict=True))
        or not isinstance(target_states, list)
        or len(target_states) != len(times)
        or any(
            not isinstance(row, list)
            or len(row) != 2
            or any(not _finite(v) or abs(v) > 1 for v in row)
            for row in target_states
        )
    ):
        raise ValueError("require bounded bilateral states on a finite increasing grid")
    mapping, plant = contract["yaw_mapping"], contract["orientation_model"]
    gain, sign = mapping["dnp15_to_yaw_proxy_scale"], mapping["directional_sign"]
    horizon, initial = (
        plant["normalization_horizon_ms"],
        plant["initial_orientation_eq"],
    )
    if (
        not _finite(gain)
        or not 0 <= gain <= 1
        or type(sign) is not int
        or sign not in (-1, 1)
        or not _finite(horizon)
        or horizon <= 0
        or not _finite(initial)
        or times[-1] > horizon
    ):
        raise ValueError("invalid finite-horizon orientation normalization")
    differential = [right - left for right, left in target_states]
    drive = [sign * gain * delta for delta in differential]
    orientation = [initial]
    for n, dt in enumerate(b - a for a, b in zip(times[:-1], times[1:], strict=True)):
        orientation.append(orientation[-1] + (dt / horizon) * drive[n])
    # No saturation/clamping. A violated declared bound fails explicitly.
    if any(not _finite(v) or abs(v - initial) > 2 * gain + 1e-12 for v in orientation):
        raise ValueError("orientation violates finite-horizon analytic bound")
    return differential, drive, orientation


def build_yaw_artifact():
    """Only frozen production assumptions, no parameter/condition overrides."""
    contract = load_preregistration()
    gate = load_evidence_gate()
    source = replay_neural_artifact(SOURCE_ROOT / SOURCE_ID)
    if (
        source["artifact_id"] != SOURCE_ID
        or source["config_sha256"] != contract["source_config_sha256"]
        or source["result_sha256"] != contract["source_result_sha256"]
        or source["config"]["preregistration_id"] != SOURCE_PREREGISTRATION_ID
    ):
        raise ValueError("canonical Phase25 source identity mismatch")
    neural = source["result"]
    times = neural["time_ms"]
    if times != [n * contract["dt_ms"] for n in range(contract["interval_count"] + 1)]:
        raise ValueError("source grid differs from frozen orientation contract")
    if times[-1] != contract["duration_ms"]:
        raise ValueError("source duration differs from preregistration")
    if [
        {k: node[k] for k in ("body_id", "type", "side")}
        for node in neural["target_order"]
    ] != contract["target_identities"]:
        raise ValueError("source bilateral identity/order mismatch")
    by_condition = {run["condition_id"]: run for run in neural["runs"]}
    if (
        len(by_condition) != len(neural["runs"])
        or list(by_condition) != contract["conditions"]
    ):
        raise ValueError("source condition set/order differs from preregistration")
    runs = []
    for condition in contract["conditions"]:
        run = by_condition[condition]
        differential, drive, orientation = integrate_orientation(
            times, run["target_states"], contract
        )
        if differential != run["right_minus_left_diagnostic"]:
            raise ValueError("persisted source differential inconsistent with targets")
        peak = max(range(len(times)), key=lambda n: abs(orientation[n]))
        peak_drive = max(range(len(times)), key=lambda n: abs(drive[n]))
        runs.append(
            {
                "condition_id": condition,
                "dnp15_states": [row.copy() for row in run["target_states"]],
                "bilateral_differential": run["right_minus_left_diagnostic"].copy(),
                "yaw_drive_eq": drive,
                "yaw_orientation_eq": orientation,
                "summary": {
                    "final_orientation_eq": orientation[-1],
                    "orientation_at_absolute_peak_eq": orientation[peak],
                    "peak_orientation_time_ms": times[peak],
                    "drive_at_absolute_peak_eq": drive[peak_drive],
                    "peak_drive_time_ms": times[peak_drive],
                },
            }
        )
    config = {
        "schema": CONFIG_SCHEMA,
        "evidence_gate_id": GATE_ID,
        "preregistration_id": PREREGISTRATION_ID,
        "preregistration": contract,
        "model_sha256": canonical_sha256(
            {
                key: contract[key]
                for key in (
                    "model_identity",
                    "yaw_mapping",
                    "orientation_model",
                    "update_semantics",
                    "body_policy",
                )
            }
        ),
        "source_artifact_id": SOURCE_ID,
        "source_config_sha256": source["config_sha256"],
        "source_result_sha256": source["result_sha256"],
        "source_authorities": gate["authorities"],
    }
    result = {
        "schema": RESULT_SCHEMA,
        "time_ms": times.copy(),
        "target_order": contract["target_identities"],
        "units": {
            "neural": contract["source_units"],
            "yaw_drive": "yaw_drive_eq",
            "orientation": "yaw_orientation_eq",
        },
        "model_role": contract["model_role"],
        "translation": "NOT_MODELLED",
        "sensory_feedback": "NONE",
        "event_semantics": "NOT_DEFINED",
        "final_boundary_semantics": "NO_OUTGOING_INTERVAL",
        "runs": runs,
        "limitations": contract["claim_limits"],
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


def validate_yaw_artifact(response):
    expected = build_yaw_artifact()
    if canonical_json_bytes(response) != canonical_json_bytes(expected):
        raise ValueError("orientation artifact differs from frozen offline replay")
    return expected
