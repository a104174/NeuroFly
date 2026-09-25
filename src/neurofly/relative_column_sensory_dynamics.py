"""Four-body exploratory sensory states driven only by Phase 7D assignments."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from neurofly.relative_column_assignment import (
    BODY_IDENTITIES,
    BODY_IDS,
    RELATIVE_ASSIGNMENT_RESULT_SCHEMA,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.relative_column_assignment_artifacts import (
    ARTIFACT_SCHEMA_VERSION as ASSIGNMENT_ARTIFACT_SCHEMA_VERSION,
)
from neurofly.relative_column_assignment_artifacts import (
    LoadedRelativeColumnArtifact,
)

SENSORY_STATE_CONFIG_SCHEMA = "relative_column_sensory_state_config_v1"
SENSORY_STATE_RESULT_SCHEMA = "relative_column_sensory_state_result_v1"
SENSORY_STATE_ARTIFACT_EXPERIMENT_ID = "phase7e_four_body_sensory_state_v1"
SENSORY_STATE_MODEL_ID = "relative_column_exploratory_sensory_state_v1"
SENSORY_STATE_MODEL_VERSION = 1
SENSORY_STATE_UNIT = "dimensionless"
SENSORY_STATE_INTEGRATION_SCHEME = "exact_exponential_zero_order_hold_v1"
SENSORY_STATE_CLASSIFICATION = "MODEL_ASSUMPTION"
REFERENCE_ASSUMPTION_SET_ID = "phase7e_reference_assumptions_v1"

INPUT_METRIC_COLUMN_OVERLAP = "column_overlap_fraction"
INPUT_METRIC_STRUCTURAL_SITE_OVERLAP = "structural_input_site_overlap_fraction"
INPUT_METRICS = (
    INPUT_METRIC_COLUMN_OVERLAP,
    INPUT_METRIC_STRUCTURAL_SITE_OVERLAP,
)
REFERENCE_TAU_SENS_MS = 1.0
REFERENCE_GAIN = 1.0
INITIAL_STATE = 0.0
RECOVERY_TAIL_STEPS = 10
SENSITIVITY_TAU_VALUES_MS = (0.5, 1.0, 2.0)
SENSITIVITY_GAIN_VALUES = (0.5, 1.0, 2.0)

EXPECTED_ASSIGNMENT_ARTIFACT_ID = (
    "404473c66c36b9f0332a203928200552c6c2e5490af446caae6c3d7475daafbe"
)
EXPECTED_SOURCE_CONTRACT_SHA256 = (
    "874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21"
)
EXPECTED_COLUMN_GRID_SHA256 = (
    "d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3"
)

_EXPECTED_IDENTITIES = tuple(dict(item) for item in BODY_IDENTITIES)
_EXPECTED_STIMULI = (
    "left_expand_33_29",
    "left_lplc2_11498_18_04",
    "right_expand_23_09",
    "right_translate_23_11",
)


class RelativeColumnSensoryDynamicsError(ValueError):
    """Invalid Phase 7D assignment input or exploratory sensory model state."""


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RelativeColumnSensoryDynamicsError(f"{name} must be finite numeric data.")
    result = float(value)
    if not math.isfinite(result):
        raise RelativeColumnSensoryDynamicsError(f"{name} must be finite numeric data.")
    return result


def _bounded_exposure(value: Any, name: str = "exposure") -> float:
    result = _finite_number(value, name)
    if not 0.0 <= result <= 1.0:
        raise RelativeColumnSensoryDynamicsError(f"{name} must be within [0,1].")
    return result


def _validate_assignment_artifact(
    artifact: LoadedRelativeColumnArtifact,
) -> dict[str, list[dict[str, Any]]]:
    """Validate Phase 7D identity and return each ordered stimulus timeline."""

    if artifact.artifact_id != EXPECTED_ASSIGNMENT_ARTIFACT_ID:
        raise RelativeColumnSensoryDynamicsError(
            "input must be the pinned Phase 7D four-body assignment artifact."
        )
    if artifact.manifest.get("artifact_id") != artifact.artifact_id:
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D manifest and loaded artifact identities disagree."
        )
    if artifact.manifest.get("artifact_schema_version") != (
        ASSIGNMENT_ARTIFACT_SCHEMA_VERSION
    ):
        raise RelativeColumnSensoryDynamicsError(
            "input artifact is not relative_column_sensory_assignment_artifact_v1."
        )
    config = artifact.config
    result = artifact.result
    file_hashes = artifact.manifest.get("files")
    if not isinstance(file_hashes, Mapping):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D payload hashes are unavailable."
        )
    try:
        expected_config_hash = file_hashes["config.json"]["sha256"]
        expected_result_hash = file_hashes["assignment_result.json"]["sha256"]
        actual_config_hash = sha256_bytes(canonical_json_bytes(dict(config)) + b"\n")
        actual_result_hash = sha256_bytes(canonical_json_bytes(dict(result)) + b"\n")
    except (KeyError, TypeError, ValueError):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D payload hashes are malformed."
        ) from None
    if (actual_config_hash, actual_result_hash) != (
        expected_config_hash,
        expected_result_hash,
    ):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D payload does not match its pinned hashes."
        )
    if (
        config.get("schema") != "relative_column_assignment_config_v1"
        or result.get("schema") != RELATIVE_ASSIGNMENT_RESULT_SCHEMA
        or result.get("experiment_id")
        != "phase7d_four_body_relative_column_assignment_v1"
        or tuple(result.get("body_ids", ())) != BODY_IDS
        or config.get("body_identities") != list(_EXPECTED_IDENTITIES)
    ):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D input schema or fixed body identities do not match."
        )
    source_identity = config.get("source_identity")
    column_grid_identity = config.get("column_grid_identity")
    if (
        not isinstance(source_identity, Mapping)
        or source_identity.get("schema") != "body_column_input_v1"
        or source_identity.get("dataset") != "male-cns:v1.0"
        or source_identity.get("candidate_id") != "looming_giant_fiber_v1"
        or source_identity.get("contract_identity_sha256")
        != EXPECTED_SOURCE_CONTRACT_SHA256
        or not isinstance(column_grid_identity, Mapping)
        or column_grid_identity.get("sha256") != EXPECTED_COLUMN_GRID_SHA256
    ):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D source contract or column grid identity mismatch."
        )
    stimulus_entries = config.get("stimuli")
    if (
        not isinstance(stimulus_entries, list)
        or any(not isinstance(entry, Mapping) for entry in stimulus_entries)
        or any(
            not isinstance(entry.get("config"), Mapping) for entry in stimulus_entries
        )
        or tuple(
            entry.get("config", {}).get("stimulus_id") for entry in stimulus_entries
        )
        != _EXPECTED_STIMULI
    ):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D stimulus identities do not match the fixed experiment."
        )

    timelines: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, int]] = set()
    for sample in result.get("samples", ()):
        if not isinstance(sample, Mapping):
            raise RelativeColumnSensoryDynamicsError(
                "Phase 7D timeline contains a malformed sample."
            )
        stimulus_id = sample.get("stimulus_id")
        side = sample.get("side")
        step = sample.get("step")
        dt_ms = _finite_number(sample.get("dt_ms"), "assignment dt_ms")
        time_ms = _finite_number(sample.get("time_ms"), "assignment time_ms")
        radius = sample.get("radius_lattice_steps")
        if (
            stimulus_id not in _EXPECTED_STIMULI
            or side not in {"L", "R"}
            or not _is_int(step)
            or step < 0
            or dt_ms <= 0.0
            or time_ms != step * dt_ms
            or not _is_int(radius)
            or radius < 0
            or (stimulus_id, step) in seen
        ):
            raise RelativeColumnSensoryDynamicsError(
                "Phase 7D sample has invalid identity, timing, or radius."
            )
        seen.add((stimulus_id, step))
        assignments = sample.get("assignments")
        if not isinstance(assignments, list) or len(assignments) != len(BODY_IDS):
            raise RelativeColumnSensoryDynamicsError(
                "Phase 7D sample does not contain the exact four body assignments."
            )
        if any(not isinstance(item, Mapping) for item in assignments) or [
            item.get("body_id") for item in assignments
        ] != list(BODY_IDS):
            raise RelativeColumnSensoryDynamicsError(
                "Phase 7D sample body set or order is invalid."
            )
        for identity, assignment in zip(_EXPECTED_IDENTITIES, assignments, strict=True):
            if (
                assignment.get("neuron_type") != identity["neuron_type"]
                or assignment.get("side") != identity["side"]
                or assignment.get("semantic_classification") != "ANATOMICAL_EXPOSURE"
                or assignment.get("neural_response_present") is not False
            ):
                raise RelativeColumnSensoryDynamicsError(
                    "Phase 7D identity/semantics mismatch for body "
                    f"{identity['body_id']}."
                )
            for metric in INPUT_METRICS:
                value = _bounded_exposure(assignment.get(metric), metric)
                if identity["side"] != side and value != 0.0:
                    raise RelativeColumnSensoryDynamicsError(
                        "Phase 7D unilateral input crosses sides."
                    )
        timelines[stimulus_id].append(dict(sample))

    if set(timelines) != set(_EXPECTED_STIMULI) or len(seen) != result.get(
        "sample_count"
    ):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D assignment timeline is incomplete."
        )
    for stimulus_id, samples in timelines.items():
        samples.sort(key=lambda item: item["step"])
        if [item["step"] for item in samples] != list(range(len(samples))):
            raise RelativeColumnSensoryDynamicsError(
                f"Phase 7D steps for {stimulus_id} are not contiguous from zero."
            )
        dts = {_finite_number(item["dt_ms"], "assignment dt_ms") for item in samples}
        sides = {item["side"] for item in samples}
        if len(dts) != 1 or len(sides) != 1:
            raise RelativeColumnSensoryDynamicsError(
                f"Phase 7D grid/side changes within stimulus {stimulus_id}."
            )
    return dict(timelines)


def sensory_model_config(artifact: LoadedRelativeColumnArtifact) -> dict[str, Any]:
    """Build the immutable reference config tied to a replayable Phase 7D run."""

    _validate_assignment_artifact(artifact)
    manifest_files = artifact.manifest.get("files")
    if not isinstance(manifest_files, Mapping):
        raise RelativeColumnSensoryDynamicsError(
            "Phase 7D payload hashes are unavailable."
        )
    assignment_identity = {
        "artifact_id": artifact.artifact_id,
        "artifact_schema_version": ASSIGNMENT_ARTIFACT_SCHEMA_VERSION,
        "experiment_id": artifact.result["experiment_id"],
        "config_sha256": manifest_files["config.json"]["sha256"],
        "result_sha256": manifest_files["assignment_result.json"]["sha256"],
        "source_contract_sha256": EXPECTED_SOURCE_CONTRACT_SHA256,
        "column_grid_sha256": EXPECTED_COLUMN_GRID_SHA256,
    }
    return {
        "schema": SENSORY_STATE_CONFIG_SCHEMA,
        "experiment_id": SENSORY_STATE_ARTIFACT_EXPERIMENT_ID,
        "model": {
            "model_id": SENSORY_STATE_MODEL_ID,
            "model_version": SENSORY_STATE_MODEL_VERSION,
            "state_unit": SENSORY_STATE_UNIT,
            "state_semantics": "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE",
            "integration_scheme": SENSORY_STATE_INTEGRATION_SCHEME,
            "input_hold_semantics": (
                "assignment sample at step n is held over [n*dt,(n+1)*dt]"
            ),
            "stochastic_policy": "deterministic",
        },
        "assignment_input": assignment_identity,
        "body_identities": [dict(item) for item in _EXPECTED_IDENTITIES],
        "reference_assumption_set_id": REFERENCE_ASSUMPTION_SET_ID,
        "reference_parameters": {
            "tau_sens_ms": {
                "value": REFERENCE_TAU_SENS_MS,
                "units": "ms",
                "classification": SENSORY_STATE_CLASSIFICATION,
            },
            "gain": {
                "value": REFERENCE_GAIN,
                "units": "dimensionless",
                "classification": SENSORY_STATE_CLASSIFICATION,
            },
            "input_metric_id": INPUT_METRIC_COLUMN_OVERLAP,
            "initial_state": {
                "value": INITIAL_STATE,
                "units": SENSORY_STATE_UNIT,
                "classification": SENSORY_STATE_CLASSIFICATION,
            },
            "recovery_tail_steps": RECOVERY_TAIL_STEPS,
        },
        "sensitivity_grid": {
            "tau_sens_ms": list(SENSITIVITY_TAU_VALUES_MS),
            "gain": list(SENSITIVITY_GAIN_VALUES),
            "input_metric_id": list(INPUT_METRICS),
            "parameter_classification": SENSORY_STATE_CLASSIFICATION,
        },
        "zero_exposure_control": {
            "control_id": "zero_exposure_model_input_control_v1",
            "schedule_source_stimulus_id": "left_expand_33_29",
            "semantics": (
                "all-zero model-input control on the source assignment time grid; "
                "not an additional biological or optical stimulus"
            ),
        },
        "scientific_boundary": {
            "input_is_phase7d_anatomical_exposure_only": True,
            "body_specific_parameters": False,
            "physiological_interpretation": False,
            "membrane_voltage_present": False,
            "spikes_present": False,
            "dn_p01_integration_present": False,
            "structural_weights_used_as_gain": False,
            "absolute_visual_angle_present": False,
            "functional_receptive_field_claim": False,
        },
    }


def _validate_model_parameters(
    *, tau_sens_ms: Any, gain: Any, input_metric_id: Any
) -> tuple[float, float, str]:
    tau = _finite_number(tau_sens_ms, "tau_sens_ms")
    scale = _finite_number(gain, "gain")
    if tau <= 0.0:
        raise RelativeColumnSensoryDynamicsError("tau_sens_ms must be positive.")
    if scale < 0.0:
        raise RelativeColumnSensoryDynamicsError("gain cannot be negative.")
    if input_metric_id not in INPUT_METRICS:
        raise RelativeColumnSensoryDynamicsError("unsupported anatomical input metric.")
    return tau, scale, input_metric_id


def integrate_exposure_values(
    exposures: Sequence[float],
    *,
    dt_ms: float,
    tau_sens_ms: float,
    gain: float,
    recovery_tail_steps: int = 0,
    assignment_steps: Sequence[int | None] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Integrate held exposure and return boundary-indexed dimensionless state."""

    dt = _finite_number(dt_ms, "dt_ms")
    tau, scale, _ = _validate_model_parameters(
        tau_sens_ms=tau_sens_ms,
        gain=gain,
        input_metric_id=INPUT_METRIC_COLUMN_OVERLAP,
    )
    if dt <= 0.0:
        raise RelativeColumnSensoryDynamicsError("dt_ms must be positive.")
    if not isinstance(exposures, Sequence) or not exposures:
        raise RelativeColumnSensoryDynamicsError(
            "exposure timeline must contain at least one sample."
        )
    values = tuple(_bounded_exposure(value) for value in exposures)
    if not _is_int(recovery_tail_steps) or recovery_tail_steps < 0:
        raise RelativeColumnSensoryDynamicsError(
            "recovery_tail_steps must be a non-negative integer."
        )
    if assignment_steps is None:
        assignment_steps = tuple(range(len(values)))
    if len(assignment_steps) != len(values) or any(
        value is not None and (not _is_int(value) or value < 0)
        for value in assignment_steps
    ):
        raise RelativeColumnSensoryDynamicsError("assignment step identity is invalid.")

    decay = math.exp(-dt / tau)
    state = INITIAL_STATE
    timeline: list[dict[str, Any]] = [
        {
            "state_step": 0,
            "time_ms": 0.0,
            "source_assignment_step": None,
            "input_exposure": None,
            "sample_kind": "INITIAL_CONDITION",
            "state_value": state,
        }
    ]
    for input_offset, exposure in enumerate(values):
        input_step = assignment_steps[input_offset]
        if input_step is not None and input_step != input_offset:
            raise RelativeColumnSensoryDynamicsError(
                "assignment steps must be contiguous and start at zero."
            )
        state_step = input_offset + 1
        state = state * decay + scale * exposure * (1.0 - decay)
        if not math.isfinite(state) or state < 0.0:
            raise RelativeColumnSensoryDynamicsError(
                "sensory model state became non-finite or negative."
            )
        timeline.append(
            {
                "state_step": state_step,
                "time_ms": state_step * dt,
                "source_assignment_step": input_step,
                "input_exposure": exposure,
                "sample_kind": (
                    "ZERO_EXPOSURE_CONTROL"
                    if input_step is None
                    else "ASSIGNMENT_INTERVAL_INPUT"
                ),
                "state_value": state,
            }
        )
    for tail_offset in range(recovery_tail_steps):
        state_step = len(values) + tail_offset + 1
        state *= decay
        if not math.isfinite(state) or state < 0.0:
            raise RelativeColumnSensoryDynamicsError(
                "sensory recovery state became non-finite or negative."
            )
        timeline.append(
            {
                "state_step": state_step,
                "time_ms": state_step * dt,
                "source_assignment_step": None,
                "input_exposure": 0.0,
                "sample_kind": "RECOVERY_ZERO_INPUT",
                "state_value": state,
            }
        )
    return tuple(timeline)


def _trajectory(
    *,
    stimulus_id: str,
    body_identity: Mapping[str, Any],
    samples: Sequence[Mapping[str, Any]],
    input_metric_id: str,
    tau_sens_ms: float,
    gain: float,
    recovery_tail_steps: int,
) -> dict[str, Any]:
    exposures = tuple(
        _bounded_exposure(
            next(
                item
                for item in sample["assignments"]
                if item["body_id"] == body_identity["body_id"]
            )[input_metric_id],
            input_metric_id,
        )
        for sample in samples
    )
    dt = _finite_number(samples[0]["dt_ms"], "assignment dt_ms")
    timeline = integrate_exposure_values(
        exposures,
        dt_ms=dt,
        tau_sens_ms=tau_sens_ms,
        gain=gain,
        recovery_tail_steps=recovery_tail_steps,
    )
    peak_index = max(
        range(len(timeline)), key=lambda index: timeline[index]["state_value"]
    )
    peak_exposure_index = max(range(len(exposures)), key=exposures.__getitem__)
    input_end = timeline[len(exposures)]
    return {
        "body_id": body_identity["body_id"],
        "neuron_type": body_identity["neuron_type"],
        "side": body_identity["side"],
        "input_metric_id": input_metric_id,
        "shared_parameter_set_id": REFERENCE_ASSUMPTION_SET_ID,
        "parameter_classification": SENSORY_STATE_CLASSIFICATION,
        "peak_exposure": exposures[peak_exposure_index],
        "peak_exposure_assignment_step": samples[peak_exposure_index]["step"],
        "peak_exploratory_state": timeline[peak_index]["state_value"],
        "peak_state_step": timeline[peak_index]["state_step"],
        "peak_state_time_ms": timeline[peak_index]["time_ms"],
        "state_after_last_assignment_interval": input_end["state_value"],
        "state_at_recovery_end": timeline[-1]["state_value"],
        "zero_exposure_assignment_sample_count": sum(
            value == 0.0 for value in exposures
        ),
        "state_timeline": list(timeline),
        "state_semantics": "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE",
    }


def _summarize_trajectory(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "body_id": value["body_id"],
        "neuron_type": value["neuron_type"],
        "side": value["side"],
        "peak_exposure": value["peak_exposure"],
        "peak_exposure_assignment_step": value["peak_exposure_assignment_step"],
        "peak_exploratory_state": value["peak_exploratory_state"],
        "peak_state_step": value["peak_state_step"],
        "peak_state_time_ms": value["peak_state_time_ms"],
        "state_at_recovery_end": value["state_at_recovery_end"],
    }


def _sensitivity_summary(
    timelines: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for metric in INPUT_METRICS:
        for tau in SENSITIVITY_TAU_VALUES_MS:
            for gain in SENSITIVITY_GAIN_VALUES:
                conditions = []
                for stimulus_id in _EXPECTED_STIMULI:
                    samples = timelines[stimulus_id]
                    conditions.append(
                        {
                            "stimulus_id": stimulus_id,
                            "bodies": [
                                _summarize_trajectory(
                                    _trajectory(
                                        stimulus_id=stimulus_id,
                                        body_identity=identity,
                                        samples=samples,
                                        input_metric_id=metric,
                                        tau_sens_ms=tau,
                                        gain=gain,
                                        recovery_tail_steps=RECOVERY_TAIL_STEPS,
                                    )
                                )
                                for identity in _EXPECTED_IDENTITIES
                            ],
                        }
                    )
                summaries.append(
                    {
                        "input_metric_id": metric,
                        "tau_sens_ms": tau,
                        "gain": gain,
                        "parameter_classification": SENSORY_STATE_CLASSIFICATION,
                        "conditions": conditions,
                    }
                )
    return summaries


def compute_sensory_state_result(
    assignment_artifact: LoadedRelativeColumnArtifact,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Derive reference states and a fixed sensitivity grid from Phase 7D only."""

    timelines = _validate_assignment_artifact(assignment_artifact)
    config = sensory_model_config(assignment_artifact)
    reference = config["reference_parameters"]
    metric = reference["input_metric_id"]
    tau = reference["tau_sens_ms"]["value"]
    gain = reference["gain"]["value"]
    recovery_steps = reference["recovery_tail_steps"]
    conditions: list[dict[str, Any]] = []
    for stimulus_id in _EXPECTED_STIMULI:
        samples = timelines[stimulus_id]
        conditions.append(
            {
                "stimulus_id": stimulus_id,
                "side": samples[0]["side"],
                "dt_ms": samples[0]["dt_ms"],
                "assignment_sample_count": len(samples),
                "radius_schedule_lattice_steps": [
                    item["radius_lattice_steps"] for item in samples
                ],
                "body_trajectories": [
                    _trajectory(
                        stimulus_id=stimulus_id,
                        body_identity=identity,
                        samples=samples,
                        input_metric_id=metric,
                        tau_sens_ms=tau,
                        gain=gain,
                        recovery_tail_steps=recovery_steps,
                    )
                    for identity in _EXPECTED_IDENTITIES
                ],
            }
        )

    zero_schedule = timelines["left_expand_33_29"]
    zero_dt = _finite_number(zero_schedule[0]["dt_ms"], "assignment dt_ms")
    zero_exposures = tuple(0.0 for _ in zero_schedule)
    zero_control = {
        "control_id": "zero_exposure_model_input_control_v1",
        "schedule_source_stimulus_id": "left_expand_33_29",
        "dt_ms": zero_dt,
        "assignment_sample_count": len(zero_schedule),
        "body_trajectories": [],
        "semantics": (
            "all-zero model input on the Phase 7D sample grid; not a new stimulus"
        ),
    }
    for identity in _EXPECTED_IDENTITIES:
        trace = integrate_exposure_values(
            zero_exposures,
            dt_ms=zero_dt,
            tau_sens_ms=tau,
            gain=gain,
            recovery_tail_steps=recovery_steps,
            assignment_steps=(None,) * len(zero_exposures),
        )
        zero_control["body_trajectories"].append(
            {
                "body_id": identity["body_id"],
                "neuron_type": identity["neuron_type"],
                "side": identity["side"],
                "input_metric_id": metric,
                "peak_exploratory_state": max(item["state_value"] for item in trace),
                "peak_state_step": 0,
                "peak_state_time_ms": 0.0,
                "state_at_recovery_end": trace[-1]["state_value"],
                "state_timeline": list(trace),
            }
        )

    result = {
        "schema": SENSORY_STATE_RESULT_SCHEMA,
        "experiment_id": SENSORY_STATE_ARTIFACT_EXPERIMENT_ID,
        "model_id": SENSORY_STATE_MODEL_ID,
        "model_version": SENSORY_STATE_MODEL_VERSION,
        "assignment_artifact_id": assignment_artifact.artifact_id,
        "state_unit": SENSORY_STATE_UNIT,
        "state_semantics": "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE",
        "body_ids": list(BODY_IDS),
        "conditions": conditions,
        "zero_exposure_control": zero_control,
        "sensitivity": _sensitivity_summary(timelines),
        "limitations": {
            "physiological_interpretation": False,
            "membrane_voltage_present": False,
            "spikes_present": False,
            "functional_receptive_field_claim": False,
            "dn_p01_integration_present": False,
            "type_level_encoder_drive_mixed": False,
            "structural_weight_used_as_gain": False,
            "absolute_visual_angle_present": False,
        },
    }
    return config, result


def sensitivity_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    """Return compact sensitivity extrema without ranking model assumptions."""

    points = result.get("sensitivity")
    if not isinstance(points, list):
        raise RelativeColumnSensoryDynamicsError("sensitivity result is malformed.")
    rows: list[dict[str, Any]] = []
    for point in points:
        body_points = [
            body for condition in point["conditions"] for body in condition["bodies"]
        ]
        values = [float(item["peak_exploratory_state"]) for item in body_points]
        rows.append(
            {
                "input_metric_id": point["input_metric_id"],
                "tau_sens_ms": point["tau_sens_ms"],
                "gain": point["gain"],
                "minimum_peak_state": min(values),
                "maximum_peak_state": max(values),
            }
        )
    return {
        "scenario_count": len(rows),
        "parameter_classification": SENSORY_STATE_CLASSIFICATION,
        "scenarios": rows,
    }
