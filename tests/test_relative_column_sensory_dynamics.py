"""Phase 7E exact discrete state and immutable replay tests."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import pytest

from neurofly.relative_column_assignment import (
    DEFAULT_OUTPUT_ROOT as ASSIGNMENT_OUTPUT_ROOT,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    sha256_file,
)
from neurofly.relative_column_assignment_artifacts import (
    replay_relative_column_artifact,
)
from neurofly.relative_column_sensory_artifacts import (
    RelativeColumnSensoryArtifactExportError,
    RelativeColumnSensoryArtifactIntegrityError,
    export_relative_column_sensory_artifact,
    load_relative_column_sensory_artifact,
    relative_column_sensory_artifact_id,
    replay_relative_column_sensory_artifact,
)
from neurofly.relative_column_sensory_dynamics import (
    BODY_IDS,
    EXPECTED_ASSIGNMENT_ARTIFACT_ID,
    INPUT_METRIC_COLUMN_OVERLAP,
    INPUT_METRIC_STRUCTURAL_SITE_OVERLAP,
    REFERENCE_GAIN,
    REFERENCE_TAU_SENS_MS,
    SENSORY_STATE_MODEL_ID,
    RelativeColumnSensoryDynamicsError,
    compute_sensory_state_result,
    integrate_exposure_values,
    sensitivity_summary,
)

ASSIGNMENT_PATH = ASSIGNMENT_OUTPUT_ROOT / EXPECTED_ASSIGNMENT_ARTIFACT_ID
SOURCE_AVAILABLE = (
    ASSIGNMENT_PATH.exists()
    and DEFAULT_SOURCE_ROOT.exists()
    and DEFAULT_WORKBOOK.exists()
)


@pytest.fixture(scope="module")
def assignment_artifact():
    if not SOURCE_AVAILABLE:
        pytest.skip("replay-verified Phase 7D source artifact is unavailable")
    return replay_relative_column_artifact(
        ASSIGNMENT_PATH,
        source_root=DEFAULT_SOURCE_ROOT,
        workbook_path=DEFAULT_WORKBOOK,
    )


def _sensitivity_point(
    result: dict,
    *,
    metric: str,
    tau: float,
    gain: float,
    stimulus_id: str,
) -> dict:
    point = next(
        item
        for item in result["sensitivity"]
        if item["input_metric_id"] == metric
        and item["tau_sens_ms"] == tau
        and item["gain"] == gain
    )
    return next(
        item for item in point["conditions"] if item["stimulus_id"] == stimulus_id
    )


def _body_summary(condition: dict, body_id: int) -> dict:
    return next(item for item in condition["bodies"] if item["body_id"] == body_id)


def test_exact_discrete_update_zero_input_decay_accumulation_and_bounds() -> None:
    tau = 1.0
    gain = 1.0
    dt = 0.1
    decay = math.exp(-dt / tau)
    trace = integrate_exposure_values(
        (1.0, 1.0, 0.0),
        dt_ms=dt,
        tau_sens_ms=tau,
        gain=gain,
        recovery_tail_steps=1,
    )
    assert [item["state_step"] for item in trace] == [0, 1, 2, 3, 4]
    assert [item["time_ms"] for item in trace] == [
        0.0,
        0.1,
        0.2,
        0.30000000000000004,
        0.4,
    ]
    assert trace[0]["state_value"] == 0.0
    assert trace[1]["state_value"] == pytest.approx(1.0 - decay)
    assert trace[2]["state_value"] == pytest.approx(1.0 - decay**2)
    assert trace[3]["state_value"] == pytest.approx(trace[2]["state_value"] * decay)
    assert trace[4]["state_value"] == pytest.approx(trace[3]["state_value"] * decay)
    assert all(0.0 <= item["state_value"] <= gain for item in trace)
    assert all(math.isfinite(item["state_value"]) for item in trace)
    assert not any(
        forbidden in row
        for row in trace
        for forbidden in ("spike", "threshold", "membrane_mv", "firing_rate")
    )


def test_zero_exposure_remains_zero_and_assignment_interval_is_explicit() -> None:
    trace = integrate_exposure_values(
        (0.0, 0.0, 0.0, 0.0),
        dt_ms=0.1,
        tau_sens_ms=REFERENCE_TAU_SENS_MS,
        gain=REFERENCE_GAIN,
        recovery_tail_steps=4,
        assignment_steps=(None, None, None, None),
    )
    assert all(row["state_value"] == 0.0 for row in trace)
    assert all(row["state_step"] == index for index, row in enumerate(trace))
    assert [row["sample_kind"] for row in trace[1:5]] == ["ZERO_EXPOSURE_CONTROL"] * 4
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="contiguous"):
        integrate_exposure_values(
            (0.2, 0.3),
            dt_ms=0.1,
            tau_sens_ms=1.0,
            gain=1.0,
            assignment_steps=(0, 2),
        )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"tau_sens_ms": 0.0}, "tau_sens_ms"),
        ({"tau_sens_ms": math.inf}, "tau_sens_ms"),
        ({"gain": -0.1}, "gain"),
        ({"gain": math.nan}, "gain"),
        ({"dt_ms": 0.0}, "dt_ms"),
    ],
)
def test_invalid_model_parameters_fail_closed(kwargs, message) -> None:
    parameters = {
        "dt_ms": 0.1,
        "tau_sens_ms": 1.0,
        "gain": 1.0,
    }
    parameters.update(kwargs)
    with pytest.raises(RelativeColumnSensoryDynamicsError, match=message):
        integrate_exposure_values((0.5,), **parameters)


def test_exposure_range_and_metric_validation_fail_closed() -> None:
    with pytest.raises(RelativeColumnSensoryDynamicsError, match=r"\[0,1\]"):
        integrate_exposure_values((1.01,), dt_ms=0.1, tau_sens_ms=1.0, gain=1.0)
    assert INPUT_METRIC_COLUMN_OVERLAP != INPUT_METRIC_STRUCTURAL_SITE_OVERLAP


def test_shared_parameters_make_same_exposure_same_state_and_gain_scales_linearly() -> (
    None
):
    exposures = (0.2, 0.4, 0.8, 0.0)
    baseline = integrate_exposure_values(
        exposures, dt_ms=0.1, tau_sens_ms=1.0, gain=1.0, recovery_tail_steps=2
    )
    other_identity = integrate_exposure_values(
        exposures, dt_ms=0.1, tau_sens_ms=1.0, gain=1.0, recovery_tail_steps=2
    )
    half_gain = integrate_exposure_values(
        exposures, dt_ms=0.1, tau_sens_ms=1.0, gain=0.5, recovery_tail_steps=2
    )
    assert baseline == other_identity
    assert [row["state_value"] * 0.5 for row in baseline] == pytest.approx(
        [row["state_value"] for row in half_gain]
    )


def test_tau_changes_smoothing_and_decay_not_input_identity() -> None:
    fast = integrate_exposure_values(
        (0.5,), dt_ms=0.1, tau_sens_ms=0.5, gain=1.0, recovery_tail_steps=10
    )
    slow = integrate_exposure_values(
        (0.5,), dt_ms=0.1, tau_sens_ms=2.0, gain=1.0, recovery_tail_steps=10
    )
    assert fast[1]["state_value"] > slow[1]["state_value"]
    assert fast[-1]["state_value"] < slow[-1]["state_value"]


def test_real_phase7d_assignment_drives_only_four_exploratory_states(
    assignment_artifact,
):
    old_hashes = {
        path.name: sha256_file(path)
        for path in ASSIGNMENT_PATH.iterdir()
        if path.is_file()
    }
    config, result = compute_sensory_state_result(assignment_artifact)
    assert config["model"]["model_id"] == SENSORY_STATE_MODEL_ID
    assert config["body_identities"] == [
        {"body_id": 12032, "neuron_type": "LC4", "side": "L"},
        {"body_id": 16128, "neuron_type": "LC4", "side": "R"},
        {"body_id": 11498, "neuron_type": "LPLC2", "side": "L"},
        {"body_id": 14465, "neuron_type": "LPLC2", "side": "R"},
    ]
    assert config["reference_parameters"]["input_metric_id"] == (
        INPUT_METRIC_COLUMN_OVERLAP
    )
    assert config["reference_parameters"]["tau_sens_ms"] == {
        "value": REFERENCE_TAU_SENS_MS,
        "units": "ms",
        "classification": "MODEL_ASSUMPTION",
    }
    assert config["reference_parameters"]["gain"]["value"] == REFERENCE_GAIN
    assert config["scientific_boundary"]["dn_p01_integration_present"] is False
    assert result["body_ids"] == list(BODY_IDS)
    assert result["state_semantics"] == (
        "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE"
    )
    assert len(result["conditions"]) == 4
    assert len(result["sensitivity"]) == 18
    assert result["limitations"]["spikes_present"] is False
    assert result["limitations"]["dn_p01_integration_present"] is False
    assert old_hashes == {
        path.name: sha256_file(path)
        for path in ASSIGNMENT_PATH.iterdir()
        if path.is_file()
    }

    left_condition = next(
        item
        for item in result["conditions"]
        if item["stimulus_id"] == "left_expand_33_29"
    )
    right_condition = next(
        item
        for item in result["conditions"]
        if item["stimulus_id"] == "right_expand_23_09"
    )
    left_body = next(
        item for item in left_condition["body_trajectories"] if item["body_id"] == 12032
    )
    left_opposite = next(
        item for item in left_condition["body_trajectories"] if item["body_id"] == 16128
    )
    right_body = next(
        item
        for item in right_condition["body_trajectories"]
        if item["body_id"] == 16128
    )
    right_opposite = next(
        item
        for item in right_condition["body_trajectories"]
        if item["body_id"] == 12032
    )
    assert left_body["peak_exploratory_state"] > 0.0
    assert right_body["peak_exploratory_state"] > 0.0
    assert left_opposite["peak_exposure"] == 0.0
    assert left_opposite["peak_exploratory_state"] == 0.0
    assert right_opposite["peak_exposure"] == 0.0
    assert right_opposite["peak_exploratory_state"] == 0.0
    assert left_body["state_timeline"][1]["source_assignment_step"] == 0
    assert left_body["state_timeline"][1]["state_step"] == 1
    assert left_body["state_timeline"][1]["time_ms"] == 0.1
    assert left_body["state_timeline"][1]["sample_kind"] == (
        "ASSIGNMENT_INTERVAL_INPUT"
    )
    assert left_body["state_after_last_assignment_interval"] == pytest.approx(
        left_body["state_timeline"][4]["state_value"]
    )
    zero_control = result["zero_exposure_control"]
    assert all(
        all(row["state_value"] == 0.0 for row in body["state_timeline"])
        for body in zero_control["body_trajectories"]
    )
    for condition in result["conditions"]:
        for body in condition["body_trajectories"]:
            assert (
                not {
                    "spikes",
                    "membrane_mv",
                    "firing_rate",
                    "dnp01_trajectory",
                }
                & body.keys()
            )


def test_sensitivity_covers_tau_gain_and_anatomical_input_metric(
    assignment_artifact,
):
    _, result = compute_sensory_state_result(assignment_artifact)
    summary = sensitivity_summary(result)
    assert summary["scenario_count"] == 18
    assert {item["input_metric_id"] for item in summary["scenarios"]} == {
        INPUT_METRIC_COLUMN_OVERLAP,
        INPUT_METRIC_STRUCTURAL_SITE_OVERLAP,
    }
    assert {item["tau_sens_ms"] for item in summary["scenarios"]} == {0.5, 1.0, 2.0}
    assert {item["gain"] for item in summary["scenarios"]} == {0.5, 1.0, 2.0}

    small_gain = _sensitivity_point(
        result,
        metric=INPUT_METRIC_COLUMN_OVERLAP,
        tau=1.0,
        gain=0.5,
        stimulus_id="left_expand_33_29",
    )
    unit_gain = _sensitivity_point(
        result,
        metric=INPUT_METRIC_COLUMN_OVERLAP,
        tau=1.0,
        gain=1.0,
        stimulus_id="left_expand_33_29",
    )
    double_gain = _sensitivity_point(
        result,
        metric=INPUT_METRIC_COLUMN_OVERLAP,
        tau=1.0,
        gain=2.0,
        stimulus_id="left_expand_33_29",
    )
    half_state = _body_summary(small_gain, 12032)["peak_exploratory_state"]
    unit_state = _body_summary(unit_gain, 12032)["peak_exploratory_state"]
    double_state = _body_summary(double_gain, 12032)["peak_exploratory_state"]
    assert half_state == pytest.approx(unit_state * 0.5)
    assert double_state == pytest.approx(unit_state * 2.0)

    weighted_metric = _sensitivity_point(
        result,
        metric=INPUT_METRIC_STRUCTURAL_SITE_OVERLAP,
        tau=1.0,
        gain=1.0,
        stimulus_id="left_expand_33_29",
    )
    assert _body_summary(weighted_metric, 12032)["peak_exploratory_state"] != unit_state
    assert config_model_parameters_are_shared(result)


def config_model_parameters_are_shared(result: dict) -> bool:
    """No per-body parameter fields are serialized in any trajectory."""

    forbidden = {"tau_by_body", "gain_by_body", "body_gain", "body_tau"}
    for condition in result["conditions"]:
        for body in condition["body_trajectories"]:
            if forbidden & body.keys():
                return False
    return True


def test_real_artifact_hash_replay_tamper_and_phase7d_noninterference(
    assignment_artifact, tmp_path: Path
):
    config, result = compute_sensory_state_result(assignment_artifact)
    artifact_id = relative_column_sensory_artifact_id(config, result)
    assert artifact_id == relative_column_sensory_artifact_id(config, result)
    artifact_path = tmp_path / artifact_id
    artifact = export_relative_column_sensory_artifact(config, result, artifact_path)
    assert artifact.artifact_id == artifact_id
    assert artifact.config["assignment_input"]["artifact_id"] == (
        EXPECTED_ASSIGNMENT_ARTIFACT_ID
    )
    assert artifact.result["model_id"] == SENSORY_STATE_MODEL_ID
    replayed = replay_relative_column_sensory_artifact(
        artifact_path,
        assignment_artifact_path=ASSIGNMENT_PATH,
        source_root=DEFAULT_SOURCE_ROOT,
        workbook_path=DEFAULT_WORKBOOK,
    )
    assert replayed.artifact_id == artifact.artifact_id
    assert replayed.config == artifact.config
    assert replayed.result == artifact.result

    changed_config = json.loads(json.dumps(config))
    changed_config["reference_parameters"]["tau_sens_ms"]["value"] = 2.0
    changed_config_artifact_path = tmp_path / "changed-config"
    export_relative_column_sensory_artifact(
        changed_config, result, changed_config_artifact_path
    )
    with pytest.raises(
        RelativeColumnSensoryArtifactIntegrityError, match="config differs on replay"
    ):
        replay_relative_column_sensory_artifact(
            changed_config_artifact_path,
            assignment_artifact_path=ASSIGNMENT_PATH,
            source_root=DEFAULT_SOURCE_ROOT,
            workbook_path=DEFAULT_WORKBOOK,
        )

    assert all(
        Path(ASSIGNMENT_PATH, name).exists()
        for name in (
            "config.json",
            "assignment_result.json",
            "manifest.json",
        )
    )
    with pytest.raises(RelativeColumnSensoryArtifactExportError, match="immutable"):
        export_relative_column_sensory_artifact(config, result, artifact_path)

    result_path = artifact_path / "sensory_state_result.json"
    result_path.write_bytes(result_path.read_bytes() + b" ")
    with pytest.raises(RelativeColumnSensoryArtifactIntegrityError):
        load_relative_column_sensory_artifact(artifact_path)


def test_wrong_phase7d_artifact_identity_and_body_set_fail_closed(assignment_artifact):
    wrong_id = replace(assignment_artifact, artifact_id="0" * 64)
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="pinned Phase 7D"):
        compute_sensory_state_result(wrong_id)

    changed_result = json.loads(json.dumps(dict(assignment_artifact.result)))
    changed_result["body_ids"] = changed_result["body_ids"][:-1]
    wrong_body_set = replace(
        assignment_artifact, result=MappingProxyType(changed_result)
    )
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="pinned hashes"):
        compute_sensory_state_result(wrong_body_set)


def test_wrong_assignment_schema_fails_closed(assignment_artifact):
    changed_result = json.loads(json.dumps(dict(assignment_artifact.result)))
    changed_result["schema"] = "experiment_artifact_v1"
    wrong_schema = replace(assignment_artifact, result=MappingProxyType(changed_result))
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="pinned hashes"):
        compute_sensory_state_result(wrong_schema)


def test_wrong_assignment_side_and_exposure_range_fail_closed(assignment_artifact):
    changed_result = json.loads(json.dumps(dict(assignment_artifact.result)))
    changed_result["samples"][0]["assignments"][0]["side"] = "R"
    wrong_side = replace(assignment_artifact, result=MappingProxyType(changed_result))
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="pinned hashes"):
        compute_sensory_state_result(wrong_side)

    changed_result = json.loads(json.dumps(dict(assignment_artifact.result)))
    changed_result["samples"][0]["assignments"][0]["column_overlap_fraction"] = 2.0
    invalid_exposure = replace(
        assignment_artifact, result=MappingProxyType(changed_result)
    )
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="pinned hashes"):
        compute_sensory_state_result(invalid_exposure)

    changed_result = json.loads(json.dumps(dict(assignment_artifact.result)))
    changed_result["samples"][0]["assignments"][0]["column_overlap_fraction"] = 0.5
    valid_range_tamper = replace(
        assignment_artifact, result=MappingProxyType(changed_result)
    )
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="pinned hashes"):
        compute_sensory_state_result(valid_range_tamper)


def test_wrong_phase7d_source_identity_fails_closed(assignment_artifact):
    changed_config = json.loads(json.dumps(dict(assignment_artifact.config)))
    changed_config["source_identity"]["contract_identity_sha256"] = "0" * 64
    mismatched_source = replace(
        assignment_artifact, config=MappingProxyType(changed_config)
    )
    with pytest.raises(RelativeColumnSensoryDynamicsError, match="pinned hashes"):
        compute_sensory_state_result(mismatched_source)
