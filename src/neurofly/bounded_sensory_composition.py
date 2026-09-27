"""Phase 7K disjoint Sample A/B union and simultaneous 32-body replay.

This composes already-persisted samples. It performs no new body selection and
reuses the Phase 7D exposure, Phase 7E state, Phase 7F transfer, and DNp01
readout primitives without changing their scientific semantics.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from neurofly.bounded_sensory_population import (
    INPUT_METRIC_COLUMN_OVERLAP,
    K_SENSITIVITY,
    SAMPLE_ARTIFACT_SCHEMA,
    STRATA,
    _assignment_result,
    _body_index,
    _route_set,
    _sensory_trajectories,
    _simulate_condition,
)
from neurofly.bounded_sensory_population_artifacts import (
    DEFAULT_SAMPLE_ARTIFACT_ROOT,
)
from neurofly.bounded_sensory_robustness import (
    CANONICAL_PHASE7H_ID,
    CANONICAL_PHASE7I_EXPERIMENT_ID,
    CANONICAL_PHASE7I_PLAN_ID,
    CANONICAL_SAMPLE_A_ID,
    DEFAULT_EXPERIMENT_B_ROOT,
    DEFAULT_PHASE7H_PATH,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_PHASE7I_PLAN_PATH,
    DEFAULT_PLAN_B_ROOT,
    DEFAULT_SAMPLE_A_PATH,
    DEFAULT_SAMPLE_B_ROOT,
    REFERENCE_K,
    _assert_contribution_accounting,
    _sample_reference_states,
    _stimulus_identity,
    compute_sample_b_coverage_plan,
    compute_sample_b_experiment,
    replay_canonical_baselines,
    select_independent_sample,
)
from neurofly.bounded_sensory_robustness_artifacts import (
    load_sample_b_artifact,
    load_sample_b_experiment_artifact,
    load_sample_b_plan_artifact,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    RelativeColumnAssignmentSource,
    RelativeColumnGrid,
    canonical_json_bytes,
    sha256_bytes,
)

COMPOSITION_CONFIG_SCHEMA = "bounded_sensory_composed_sample_config_v1"
COMPOSITION_RESULT_SCHEMA = "bounded_sensory_composed_sample_result_v1"
COMPOSITION_ARTIFACT_SCHEMA = "bounded_sensory_composed_sample_artifact_v1"
POPULATION32_CONFIG_SCHEMA = "bounded_sensory_population_32_config_v1"
POPULATION32_RESULT_SCHEMA = "bounded_sensory_population_32_result_v1"
POPULATION32_ARTIFACT_SCHEMA = "bounded_sensory_population_32_artifact_v1"
COMPOSITION_METHOD_ID = "disjoint_persisted_sample_union_v1"
EXPERIMENT_ID = "phase7k_simultaneous_32_body_composition_v1"
CANONICAL_SAMPLE_B_ID = (
    "873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33"
)
CANONICAL_PHASE7J_EXPERIMENT_ID = (
    "f5fd68c1ea8b248f206af9be58fd9adeef604cd2e770289d8f32711ccbba6026"
)
SAMPLE_SIZE = 32
STIMULUS_COUNT = 14
TARGET_IDS = (10001, 10010)
REFERENCE_STIMULUS_IDS = ("left_expand_33_29", "right_expand_23_09")
CANONICAL_BATTERY_IDS = (
    "left_expand_33_29",
    "left_lplc2_11498_18_04",
    "right_expand_23_09",
    "right_translate_23_11",
    "sample_l_centroid_expand",
    "sample_r_centroid_expand",
    "coverage_l_03_10_r1",
    "coverage_l_12_31_r1",
    "coverage_r_01_07_r1",
    "coverage_r_12_27_r1",
    "coverage_b_l_03_05_r1",
    "coverage_b_l_22_21_r1",
    "coverage_b_r_03_14_r1",
    "coverage_b_r_21_32_r1",
)
DEFAULT_COMPOSITION_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_composed_sample_v1"
DEFAULT_POPULATION32_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_population_32_v1"
DEFAULT_PHASE7H_ARTIFACT = DEFAULT_PHASE7H_PATH
DEFAULT_SAMPLE_A_ARTIFACT = DEFAULT_SAMPLE_ARTIFACT_ROOT / CANONICAL_SAMPLE_A_ID
DEFAULT_SAMPLE_B_ARTIFACT = DEFAULT_SAMPLE_B_ROOT / CANONICAL_SAMPLE_B_ID
DEFAULT_COVERAGE_B_ARTIFACT = DEFAULT_PLAN_B_ROOT / (
    "b718607e0cf671cc06454a6422ea7c3b48107516c59291b2fe01f9a244a9079f"
)
DEFAULT_PHASE7J_ARTIFACT = DEFAULT_EXPERIMENT_B_ROOT / CANONICAL_PHASE7J_EXPERIMENT_ID


class BoundedSensoryCompositionError(ValueError):
    """Invalid source artifacts or composition/experiment invariants."""


def _source_circuit_identity(circuit: Any) -> dict[str, Any]:
    return {
        "dataset": circuit.provenance.dataset,
        "candidate_id": circuit.candidate.identifier,
        "candidate_version": circuit.candidate.version,
        "file_sha256": dict(circuit.integrity.sha256_by_file),
    }


def _reference(artifact: Any, schema: str) -> dict[str, Any]:
    manifest = artifact.manifest
    return {
        "artifact_schema": schema,
        "artifact_id": artifact.artifact_id,
        "manifest_sha256": sha256_bytes(canonical_json_bytes(manifest) + b"\n"),
        "config_sha256": manifest["config_sha256"],
        "result_sha256": manifest["result_sha256"],
    }


def _artifact_payload_identity(
    schema: str, config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_schema": schema,
                "config_sha256": sha256_bytes(canonical_json_bytes(config) + b"\n"),
                "result_sha256": sha256_bytes(canonical_json_bytes(result) + b"\n"),
            }
        )
    )


def composition_artifact_id(
    config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    return _artifact_payload_identity(COMPOSITION_ARTIFACT_SCHEMA, config, result)


def population32_artifact_id(
    config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    return _artifact_payload_identity(POPULATION32_ARTIFACT_SCHEMA, config, result)


def _load_canonical_phase7j_inputs(
    *,
    sample_a_path: str = str(DEFAULT_SAMPLE_A_PATH),
    phase7h_path: str = str(DEFAULT_PHASE7H_PATH),
    phase7i_plan_path: str = str(DEFAULT_PHASE7I_PLAN_PATH),
    phase7i_experiment_path: str = str(DEFAULT_PHASE7I_EXPERIMENT_PATH),
    sample_b_path: str = str(DEFAULT_SAMPLE_B_ARTIFACT),
    coverage_b_path: str = str(DEFAULT_COVERAGE_B_ARTIFACT),
    experiment_b_path: str = str(DEFAULT_PHASE7J_ARTIFACT),
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> dict[str, Any]:
    """Replay and validate every canonical A/B source artifact exactly once."""
    sample_a, phase7h, phase7i_plan, phase7i_experiment, source, grid, circuit = (
        replay_canonical_baselines(
            sample_a_path=sample_a_path,
            phase7h_path=phase7h_path,
            phase7i_plan_path=phase7i_plan_path,
            phase7i_experiment_path=phase7i_experiment_path,
            source_root=source_root,
            workbook_path=workbook_path,
        )
    )
    sample_b = load_sample_b_artifact(sample_b_path)
    coverage_b = load_sample_b_plan_artifact(coverage_b_path)
    experiment_b = load_sample_b_experiment_artifact(experiment_b_path)

    if sample_a.artifact_id != CANONICAL_SAMPLE_A_ID:
        raise BoundedSensoryCompositionError("canonical Sample A identity changed.")
    if (
        sample_b.artifact_id != CANONICAL_SAMPLE_B_ID
        or coverage_b.artifact_id
        != "b718607e0cf671cc06454a6422ea7c3b48107516c59291b2fe01f9a244a9079f"
        or experiment_b.artifact_id != CANONICAL_PHASE7J_EXPERIMENT_ID
    ):
        raise BoundedSensoryCompositionError("canonical Phase 7J artifact changed.")
    if (
        phase7h.artifact_id != CANONICAL_PHASE7H_ID
        or phase7i_plan.artifact_id != CANONICAL_PHASE7I_PLAN_ID
        or phase7i_experiment.artifact_id != CANONICAL_PHASE7I_EXPERIMENT_ID
    ):
        raise BoundedSensoryCompositionError("canonical Phase 7H/7I identity changed.")

    # Recompute the persisted B lineage only as an integrity/replay check. The
    # union below uses the selected identities from those immutable artifacts.
    selected_b_config, selected_b_result = select_independent_sample(
        source, circuit, sample_a.as_input()
    )
    if selected_b_config != sample_b.config or selected_b_result != sample_b.result:
        raise BoundedSensoryCompositionError("Sample B failed source replay.")
    expected_plan_config, expected_plan_result = compute_sample_b_coverage_plan(
        sample_b.as_input(),
        sample_a,
        phase7h,
        phase7i_plan,
        phase7i_experiment,
        source,
        grid,
        circuit,
    )
    if (
        expected_plan_config != coverage_b.config
        or expected_plan_result != coverage_b.result
    ):
        raise BoundedSensoryCompositionError("Sample B coverage plan failed replay.")
    expected_experiment_config, expected_experiment_result = (
        compute_sample_b_experiment(
            sample_b.as_input(),
            coverage_b.as_input(),
            sample_a,
            phase7h,
            phase7i_plan,
            phase7i_experiment,
            source,
            grid,
            circuit,
        )
    )
    if (
        expected_experiment_config != experiment_b.config
        or expected_experiment_result != experiment_b.result
    ):
        raise BoundedSensoryCompositionError("Phase 7J Sample B failed full replay.")

    return {
        "sample_a": sample_a,
        "phase7h": phase7h,
        "phase7i_plan": phase7i_plan,
        "phase7i_experiment": phase7i_experiment,
        "sample_b": sample_b,
        "coverage_b": coverage_b,
        "experiment_b": experiment_b,
        "source": source,
        "grid": grid,
        "circuit": circuit,
    }


def compose_samples(
    sample_a: Any,
    sample_b: Any,
    source: RelativeColumnAssignmentSource,
    circuit: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create Sample C from the two persisted disjoint sample identities."""
    if sample_a.artifact_id != CANONICAL_SAMPLE_A_ID:
        raise BoundedSensoryCompositionError("wrong canonical Sample A artifact.")
    if sample_b.artifact_id != CANONICAL_SAMPLE_B_ID:
        raise BoundedSensoryCompositionError("wrong canonical Sample B artifact.")
    if (
        sample_a.config.get("source_contract_identity") != source.source_identity
        or sample_b.config.get("source_contract_identity") != source.source_identity
        or sample_a.config.get("circuit_contract_identity")
        != _source_circuit_identity(circuit)
        or sample_b.config.get("circuit_contract_identity")
        != _source_circuit_identity(circuit)
    ):
        raise BoundedSensoryCompositionError("Sample A/B source identities differ.")
    a_ids = list(sample_a.result.get("body_ids", ()))
    b_ids = list(sample_b.result.get("body_ids", ()))
    if (
        len(a_ids) != 16
        or len(set(a_ids)) != 16
        or len(b_ids) != 16
        or len(set(b_ids)) != 16
    ):
        raise BoundedSensoryCompositionError(
            "Sample A/B must each contain 16 unique bodies."
        )
    overlap = set(a_ids) & set(b_ids)
    if overlap:
        raise BoundedSensoryCompositionError("Sample A/B are not disjoint.")

    body_source, _ = _body_index(source, circuit)
    a_rows = {row["body_id"]: row for row in sample_a.result["selected_bodies"]}
    b_rows = {row["body_id"]: row for row in sample_b.result["selected_bodies"]}
    if set(a_rows) != set(a_ids) or set(b_rows) != set(b_ids):
        raise BoundedSensoryCompositionError("sample body records do not match IDs.")
    routes_a = _route_set(sample_a.result, circuit)
    routes_b = _route_set(sample_b.result, circuit)
    route_by_source = {route.source_body_id: route for route in (*routes_a, *routes_b)}
    rows = []
    for body_id in sorted((*a_ids, *b_ids)):
        origin = "A" if body_id in a_rows else "B"
        source_row = a_rows.get(body_id, b_rows.get(body_id))
        current = body_source.get(body_id)
        route = route_by_source.get(body_id)
        if current is None or route is None or source_row is None:
            raise BoundedSensoryCompositionError(
                f"missing union source/route: {body_id}."
            )
        for key in ("neuron_type", "side", "target_body_id", "structural_weight"):
            if source_row.get(key) != current[key]:
                raise BoundedSensoryCompositionError(
                    f"union identity/route differs from CircuitContract: {body_id}."
                )
        row = dict(source_row)
        row["sample_origin"] = origin
        row["route_provenance"] = "MALECNS_CIRCUITCONTRACT"
        rows.append(row)

    counts = Counter((row["neuron_type"], row["side"]) for row in rows)
    expected_strata = {(neuron_type, side): 8 for neuron_type, side in STRATA}
    if len(rows) != SAMPLE_SIZE or dict(counts) != expected_strata:
        raise BoundedSensoryCompositionError("union is not exactly 8×4 balanced.")
    routes = [route_by_source[body_id].to_dict() for body_id in sorted(route_by_source)]
    targets = Counter(route.target_body_id for route in route_by_source.values())
    if targets != Counter({10001: 16, 10010: 16}):
        raise BoundedSensoryCompositionError("union route target composition changed.")

    config = {
        "schema": COMPOSITION_CONFIG_SCHEMA,
        "artifact_schema": COMPOSITION_ARTIFACT_SCHEMA,
        "composition_id": "phase7k_sample_c_union_a_b_v1",
        "composition_method_id": COMPOSITION_METHOD_ID,
        "sample_a_artifact": _reference(sample_a, SAMPLE_ARTIFACT_SCHEMA),
        "sample_b_artifact": _reference(
            sample_b, "bounded_independent_sensory_sample_artifact_v1"
        ),
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _source_circuit_identity(circuit),
        "body_column_identity": {
            "schema": source.contract.schema_version,
            "dataset": source.contract.dataset,
            "candidate_identifier": source.contract.candidate_identifier,
            "candidate_version": source.contract.candidate_version,
            "source_file_sha256": dict(
                source.source_identity.get("source_file_sha256", {})
            ),
        },
        "body_ids": sorted((*a_ids, *b_ids)),
        "sample_size": SAMPLE_SIZE,
        "strata": [
            {"neuron_type": neuron_type, "side": side, "count": 8}
            for neuron_type, side in STRATA
        ],
        "composition_method": "DISJOINT_ARTIFACT_UNION",
        "selection_or_filtering_used_outcomes": False,
        "sample_a_and_b_disjoint": True,
        "route_contract": routes,
        "structural_weight_semantics": "SOURCE_STRUCTURAL_COUNT_METADATA_ONLY",
    }
    result = {
        "schema": COMPOSITION_RESULT_SCHEMA,
        "composition_id": config["composition_id"],
        "body_ids": config["body_ids"],
        "sample_size": SAMPLE_SIZE,
        "sample_a_body_ids": a_ids,
        "sample_b_body_ids": b_ids,
        "sample_a_sample_b_overlap_count": len(overlap),
        "sample_a_sample_b_disjoint": not overlap,
        "selected_bodies": rows,
        "stratum_counts": [
            {
                "neuron_type": neuron_type,
                "side": side,
                "count": counts[(neuron_type, side)],
            }
            for neuron_type, side in STRATA
        ],
        "target_counts": [
            {"target_body_id": target, "source_count": targets[target]}
            for target in TARGET_IDS
        ],
        "model_outcomes_used": False,
        "result_semantics": "PERSISTED_SAMPLE_UNION_ONLY_NO_RESELECTION",
    }
    return config, result


def make_composition_payload(
    *,
    sample_a_path: str = str(DEFAULT_SAMPLE_A_PATH),
    phase7h_path: str = str(DEFAULT_PHASE7H_PATH),
    phase7i_plan_path: str = str(DEFAULT_PHASE7I_PLAN_PATH),
    phase7i_experiment_path: str = str(DEFAULT_PHASE7I_EXPERIMENT_PATH),
    sample_b_path: str = str(DEFAULT_SAMPLE_B_ARTIFACT),
    coverage_b_path: str = str(DEFAULT_COVERAGE_B_ARTIFACT),
    experiment_b_path: str = str(DEFAULT_PHASE7J_ARTIFACT),
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[dict[str, Any], dict[str, Any]]:
    context = _load_canonical_phase7j_inputs(
        sample_a_path=sample_a_path,
        phase7h_path=phase7h_path,
        phase7i_plan_path=phase7i_plan_path,
        phase7i_experiment_path=phase7i_experiment_path,
        sample_b_path=sample_b_path,
        coverage_b_path=coverage_b_path,
        experiment_b_path=experiment_b_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    return compose_samples(
        context["sample_a"], context["sample_b"], context["source"], context["circuit"]
    )


def _stimulus_entries(plan: Any) -> list[dict[str, Any]]:
    entries = plan.config.get("stimuli")
    if not isinstance(entries, list) or len(entries) != STIMULUS_COUNT:
        raise BoundedSensoryCompositionError(
            "Sample B battery is not the canonical 14."
        )
    parsed = [_stimulus_identity(entry) for entry in entries]
    ids = tuple(stimulus.stimulus_id for stimulus in parsed)
    if ids != CANONICAL_BATTERY_IDS or len(set(ids)) != STIMULUS_COUNT:
        raise BoundedSensoryCompositionError(
            "Sample B stimulus identity/config changed."
        )
    return entries


def _assignment_coverage(
    composition_result: Mapping[str, Any], assignment: Mapping[str, Any]
) -> list[dict[str, Any]]:
    body_ids = tuple(composition_result["body_ids"])
    identities = {row["body_id"]: row for row in composition_result["selected_bodies"]}
    maxima = dict.fromkeys(body_ids, 0.0)
    positive_stimuli: dict[int, list[str]] = {body_id: [] for body_id in body_ids}
    for sample in assignment["samples"]:
        for exposure in sample["assignments"]:
            body_id = exposure["body_id"]
            value = exposure[INPUT_METRIC_COLUMN_OVERLAP]
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise BoundedSensoryCompositionError("invalid anatomical exposure.")
            maxima[body_id] = max(maxima[body_id], value)
            if value > 0.0:
                positive_stimuli[body_id].append(sample["stimulus_id"])
            if sample["side"] != identities[body_id]["side"] and value != 0.0:
                raise BoundedSensoryCompositionError(
                    "relative-column side isolation failed."
                )
    return [
        {
            "body_id": body_id,
            "neuron_type": identities[body_id]["neuron_type"],
            "side": identities[body_id]["side"],
            "target_body_id": identities[body_id]["target_body_id"],
            "max_column_overlap_fraction": maxima[body_id],
            "positive_stimulus_ids": list(dict.fromkeys(positive_stimuli[body_id])),
            "body_stimulus_covered": maxima[body_id] > 0.0,
            "coverage_semantics": "SOFTWARE_EXPERIMENT_COVERAGE_ONLY",
        }
        for body_id in body_ids
    ]


def _assignment_rows_by_key(
    assignment: Mapping[str, Any],
) -> dict[tuple[str, int], Mapping[str, Any]]:
    return {
        (sample["stimulus_id"], sample["step"]): sample
        for sample in assignment["samples"]
    }


def _assert_nested_assignment(
    union_assignment: Mapping[str, Any],
    prior_assignment: Mapping[str, Any],
    body_ids: Sequence[int],
    *,
    label: str,
) -> int:
    union_samples = _assignment_rows_by_key(union_assignment)
    prior_samples = _assignment_rows_by_key(prior_assignment)
    comparisons = 0
    fields = (
        "active_column_set_sha256",
        "active_columns",
        "active_column_count",
        "radius_lattice_steps",
    )
    for key, prior in prior_samples.items():
        current = union_samples.get(key)
        if current is None:
            raise BoundedSensoryCompositionError(f"{label} stimulus sample is missing.")
        for field in fields:
            if prior[field] != current[field]:
                raise BoundedSensoryCompositionError(f"{label} active columns changed.")
        previous = {item["body_id"]: item for item in prior["assignments"]}
        current_rows = {item["body_id"]: item for item in current["assignments"]}
        for body_id in body_ids:
            for metric in (
                "column_overlap_fraction",
                "structural_input_site_overlap_fraction",
            ):
                if previous[body_id][metric] != current_rows[body_id][metric]:
                    raise BoundedSensoryCompositionError(
                        f"{label} anatomical assignment changed for {body_id}."
                    )
            comparisons += 1
    return comparisons


def _assert_nested_trajectories(
    current: Mapping[str, Sequence[Mapping[str, Any]]],
    previous: Mapping[str, Sequence[Mapping[str, Any]]],
    body_ids: Sequence[int],
    *,
    label: str,
) -> int:
    comparisons = 0
    for stimulus_id, old_rows in previous.items():
        if stimulus_id not in current:
            raise BoundedSensoryCompositionError(f"{label} state stimulus missing.")
        current_rows = {row["body_id"]: row for row in current[stimulus_id]}
        old_by_id = {row["body_id"]: row for row in old_rows}
        for body_id in body_ids:
            if (
                old_by_id[body_id]["state_timeline"]
                != current_rows[body_id]["state_timeline"]
            ):
                raise BoundedSensoryCompositionError(
                    f"{label} state timeline changed for {body_id}/{stimulus_id}."
                )
            comparisons += 1
    return comparisons


def _condition_for_stimulus(
    conditions: Sequence[Mapping[str, Any]], stimulus_id: str, prefix: str
) -> Mapping[str, Any]:
    condition_id = f"{prefix}{stimulus_id}"
    matches = [row for row in conditions if row["condition_id"] == condition_id]
    if len(matches) != 1:
        raise BoundedSensoryCompositionError(
            f"missing unique condition {condition_id}."
        )
    return matches[0]


def _assert_nested_transfers(
    union_conditions: Sequence[Mapping[str, Any]],
    previous_conditions: Sequence[Mapping[str, Any]],
    body_ids: Sequence[int],
    stimulus_ids: Sequence[str],
    *,
    previous_prefix: str,
    label: str,
) -> int:
    comparisons = 0
    for stimulus_id in stimulus_ids:
        current = _condition_for_stimulus(union_conditions, stimulus_id, "stimulus::")
        previous = _condition_for_stimulus(
            previous_conditions, stimulus_id, previous_prefix
        )
        for current_step, previous_step in zip(
            current["source_contributions_by_interval"],
            previous["source_contributions_by_interval"],
            strict=True,
        ):
            old = {row["source_body_id"]: row for row in previous_step["contributions"]}
            new = {row["source_body_id"]: row for row in current_step["contributions"]}
            for body_id in body_ids:
                if (
                    old[body_id]["target_body_id"] != new[body_id]["target_body_id"]
                    or old[body_id]["model_drive_mveq"]
                    != new[body_id]["model_drive_mveq"]
                ):
                    raise BoundedSensoryCompositionError(
                        f"{label} transfer changed for {body_id}/{stimulus_id}."
                    )
                comparisons += 1
    return comparisons


def _assert_target_additivity(
    union_conditions: Sequence[Mapping[str, Any]],
    a_conditions: Sequence[Mapping[str, Any]],
    b_conditions: Sequence[Mapping[str, Any]],
    stimulus_ids: Sequence[str],
) -> int:
    comparisons = 0
    for stimulus_id in stimulus_ids:
        union = _condition_for_stimulus(union_conditions, stimulus_id, "stimulus::")
        a = _condition_for_stimulus(a_conditions, stimulus_id, "phase7i_")
        b = _condition_for_stimulus(b_conditions, stimulus_id, "sample_b_stimulus_")
        for interval_c, interval_a, interval_b in zip(
            union["source_contributions_by_interval"],
            a["source_contributions_by_interval"],
            b["source_contributions_by_interval"],
            strict=True,
        ):
            drives = {
                int(target["body_id"]): target["drive_mveq_by_interval"]
                for target in union["targets"]
            }
            drives_a = {
                int(target["body_id"]): target["drive_mveq_by_interval"]
                for target in a["targets"]
            }
            drives_b = {
                int(target["body_id"]): target["drive_mveq_by_interval"]
                for target in b["targets"]
            }
            step = interval_c["step"]
            for target_id in TARGET_IDS:
                expected = drives_a[target_id][step] + drives_b[target_id][step]
                if not math.isclose(
                    drives[target_id][step], expected, rel_tol=0.0, abs_tol=1e-15
                ):
                    raise BoundedSensoryCompositionError(
                        "union target drive is not the per-step A+B sum."
                    )
                comparisons += 1
    return comparisons


def _add_source_annotations(
    condition: dict[str, Any],
    states: Mapping[int, Sequence[float]],
    body_rows: Mapping[int, Mapping[str, Any]],
) -> None:
    for interval in condition["source_contributions_by_interval"]:
        step = interval["step"]
        for contribution in interval["contributions"]:
            identity = body_rows[contribution["source_body_id"]]
            contribution["source_type"] = identity["neuron_type"]
            contribution["source_side"] = identity["side"]
            contribution["sensory_state"] = states[contribution["source_body_id"]][step]
            contribution["state_semantics"] = (
                "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE"
            )
            contribution["transfer_semantics"] = "EXPLORATORY_EDGE_ROUTED_MODEL_DRIVE"


def _mask_body_ids(
    body_rows: Sequence[Mapping[str, Any]], a_ids: set[int], b_ids: set[int], mask: str
) -> set[int]:
    if mask == "all32":
        return {row["body_id"] for row in body_rows}
    if mask == "none":
        return set()
    if mask == "LC4" or mask == "LPLC2":
        return {row["body_id"] for row in body_rows if row["neuron_type"] == mask}
    if mask == "left" or mask == "right":
        side = "L" if mask == "left" else "R"
        return {row["body_id"] for row in body_rows if row["side"] == side}
    if mask == "sample_a":
        return set(a_ids)
    if mask == "sample_b":
        return set(b_ids)
    raise BoundedSensoryCompositionError(f"unsupported 32-body mask: {mask}.")


def _coverage_state_transfer_rows(
    composition_result: Mapping[str, Any],
    assignment: Mapping[str, Any],
    trajectories: Mapping[str, Sequence[Mapping[str, Any]]],
    stimulus_conditions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows = _assignment_coverage(composition_result, assignment)
    by_id = {row["body_id"]: row for row in rows}
    for row in rows:
        row["max_exploratory_state"] = 0.0
        row["max_transfer_contribution_mveq"] = 0.0
        row["body_state_exercised"] = False
        row["body_transfer_exercised"] = False
        row["first_positive_transfer_stimulus_id"] = None
    for stimulus_id, body_trajectories in trajectories.items():
        for trajectory in body_trajectories:
            body_id = trajectory["body_id"]
            maximum = max(
                (sample["state_value"] for sample in trajectory["state_timeline"]),
                default=0.0,
            )
            by_id[body_id]["max_exploratory_state"] = max(
                by_id[body_id]["max_exploratory_state"], maximum
            )
    for condition in stimulus_conditions:
        stimulus_id = condition["condition_id"].removeprefix("stimulus::")
        for interval in condition["source_contributions_by_interval"]:
            for contribution in interval["contributions"]:
                row = by_id[contribution["source_body_id"]]
                value = contribution["model_drive_mveq"]
                row["max_transfer_contribution_mveq"] = max(
                    row["max_transfer_contribution_mveq"], value
                )
                if value > 0.0 and row["first_positive_transfer_stimulus_id"] is None:
                    row["first_positive_transfer_stimulus_id"] = stimulus_id
    for row in rows:
        row["body_state_exercised"] = row["max_exploratory_state"] > 0.0
        row["body_transfer_exercised"] = row["max_transfer_contribution_mveq"] > 0.0
        row["coverage_semantics"] = "SOFTWARE_EXPERIMENT_COVERAGE_ONLY"
    return rows


def compute_population32_experiment(
    composition_artifact: Mapping[str, Any],
    sample_a: Any,
    phase7h: Any,
    phase7i_plan: Any,
    phase7i_experiment: Any,
    sample_b: Any,
    coverage_b: Any,
    experiment_b: Any,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    circuit: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the fixed A∪B union after its source-only coverage audit passes."""
    composition = composition_artifact
    if composition.get("artifact_schema") != COMPOSITION_ARTIFACT_SCHEMA:
        raise BoundedSensoryCompositionError("wrong Sample C artifact schema.")
    config_c = composition.get("config", {})
    result_c = composition.get("result", {})
    expected_composition_config, expected_composition_result = compose_samples(
        sample_a, sample_b, source, circuit
    )
    if (
        config_c != expected_composition_config
        or result_c != expected_composition_result
    ):
        raise BoundedSensoryCompositionError("Sample C composition failed replay.")

    entries = _stimulus_entries(coverage_b)
    stimuli = tuple(_stimulus_identity(entry) for entry in entries)
    if [stimulus.stimulus_id for stimulus in stimuli] != list(CANONICAL_BATTERY_IDS):
        raise BoundedSensoryCompositionError("canonical 14-stimulus battery changed.")
    assignment = _assignment_result(result_c, source, grid, stimuli)
    anatomical_coverage = _assignment_coverage(result_c, assignment)
    if not all(row["body_stimulus_covered"] for row in anatomical_coverage):
        missing = [
            row["body_id"]
            for row in anatomical_coverage
            if not row["body_stimulus_covered"]
        ]
        raise BoundedSensoryCompositionError(
            f"32-body battery regressed source coverage for {missing}."
        )

    trajectories = _sensory_trajectories(assignment, result_c)
    a_ids = set(sample_a.result["body_ids"])
    b_ids = set(sample_b.result["body_ids"])
    union_ids = set(result_c["body_ids"])
    if a_ids & b_ids or a_ids | b_ids != union_ids or len(union_ids) != SAMPLE_SIZE:
        raise BoundedSensoryCompositionError(
            "Sample C is not the exact disjoint union."
        )

    # First assert nested anatomy/state reuse on the common canonical stimulus
    # subset. B was computed on all fourteen; A's Phase 7I baseline has ten.
    a_assignment_comparisons = _assert_nested_assignment(
        assignment,
        phase7i_experiment.result["assignment"],
        sorted(a_ids),
        label="Sample A",
    )
    b_assignment_comparisons = _assert_nested_assignment(
        assignment,
        experiment_b.result["assignment"],
        sorted(b_ids),
        label="Sample B",
    )
    a_trajectory_comparisons = _assert_nested_trajectories(
        trajectories,
        phase7i_experiment.result["sensory_trajectories_by_stimulus"],
        sorted(a_ids),
        label="Sample A",
    )
    b_trajectory_comparisons = _assert_nested_trajectories(
        trajectories,
        experiment_b.result["sensory_trajectories_by_stimulus"],
        sorted(b_ids),
        label="Sample B",
    )

    # Reuse the validated Phase 7H/J route builder for each immutable 16-body
    # source, then concatenate exact CircuitContract-derived routes.
    routes = tuple(
        sorted(
            (
                *_route_set(sample_a.result, circuit),
                *_route_set(sample_b.result, circuit),
            ),
            key=lambda route: route.source_body_id,
        )
    )
    if (
        len(routes) != SAMPLE_SIZE
        or len({route.source_body_id for route in routes}) != SAMPLE_SIZE
    ):
        raise BoundedSensoryCompositionError(
            "union route set is not exactly 32 unique routes."
        )
    route_counts = Counter(route.target_body_id for route in routes)
    if route_counts != Counter({10001: 16, 10010: 16}):
        raise BoundedSensoryCompositionError("union route target counts changed.")
    body_rows = {row["body_id"]: row for row in result_c["selected_bodies"]}

    conditions: list[dict[str, Any]] = []
    for stimulus in stimuli:
        stimulus_states = {
            row["body_id"]: [sample["state_value"] for sample in row["state_timeline"]]
            for row in trajectories[stimulus.stimulus_id]
        }
        intervals = len(next(iter(stimulus_states.values()))) - 1
        condition = _simulate_condition(
            condition_id=f"stimulus::{stimulus.stimulus_id}",
            pathway_mask="all32",
            active_body_ids=union_ids,
            k=REFERENCE_K,
            states=stimulus_states,
            dt_ms=stimulus.dt_ms,
            steps=intervals,
            routes=routes,
            circuit=circuit,
        )
        _add_source_annotations(condition, stimulus_states, body_rows)
        conditions.append(condition)

    reference_states, reference_dt, reference_steps = _sample_reference_states(
        trajectories, result_c
    )
    mask_specs = (
        ("all32_reference", "all32", REFERENCE_K),
        ("k_zero", "all32", 0.0),
        ("no_sources", "none", REFERENCE_K),
        ("lc4_only", "LC4", REFERENCE_K),
        ("lplc2_only", "LPLC2", REFERENCE_K),
        ("left_only", "left", REFERENCE_K),
        ("right_only", "right", REFERENCE_K),
        ("sample_a_only", "sample_a", REFERENCE_K),
        ("sample_b_only", "sample_b", REFERENCE_K),
        ("sensitivity_k_0_5", "all32", 0.5),
        ("sensitivity_k_2", "all32", 2.0),
    )
    for condition_id, mask, k in mask_specs:
        active_ids = _mask_body_ids(result_c["selected_bodies"], a_ids, b_ids, mask)
        condition = _simulate_condition(
            condition_id=condition_id,
            pathway_mask=mask,
            active_body_ids=active_ids,
            k=k,
            states=reference_states,
            dt_ms=reference_dt,
            steps=reference_steps,
            routes=routes,
            circuit=circuit,
        )
        _add_source_annotations(condition, reference_states, body_rows)
        conditions.append(condition)

    _assert_contribution_accounting(conditions)
    stimulus_conditions = [
        condition
        for condition in conditions
        if condition["condition_id"].startswith("stimulus::")
    ]
    coverage_rows = _coverage_state_transfer_rows(
        result_c, assignment, trajectories, stimulus_conditions
    )
    if len(coverage_rows) != SAMPLE_SIZE or any(
        not row["body_stimulus_covered"]
        or not row["body_state_exercised"]
        or not row["body_transfer_exercised"]
        for row in coverage_rows
    ):
        raise BoundedSensoryCompositionError("32/32 non-zero path coverage failed.")

    # Per-stimulus source-side isolation: the opposite eye is anatomically
    # inactive and its zero state must remain a zero routed contribution.
    side_isolation_checks = 0
    for stimulus in stimuli:
        assignments = {
            (sample["stimulus_id"], item["body_id"]): item
            for sample in assignment["samples"]
            for item in sample["assignments"]
        }
        condition = _condition_for_stimulus(
            stimulus_conditions, stimulus.stimulus_id, "stimulus::"
        )
        for row in result_c["selected_bodies"]:
            if row["side"] == stimulus.side:
                continue
            for step, interval in enumerate(
                condition["source_contributions_by_interval"]
            ):
                if (
                    assignments[(stimulus.stimulus_id, row["body_id"])][
                        "column_overlap_fraction"
                    ]
                    != 0.0
                ):
                    raise BoundedSensoryCompositionError(
                        "unilateral source exposure leaked sides."
                    )
                contribution = next(
                    item
                    for item in interval["contributions"]
                    if item["source_body_id"] == row["body_id"]
                )
                if (
                    contribution["sensory_state"] != 0.0
                    or contribution["model_drive_mveq"] != 0.0
                ):
                    raise BoundedSensoryCompositionError(
                        "unilateral state/transfer leaked sides."
                    )
                side_isolation_checks += 1

    stimulus_ids_a = tuple(
        item["config"]["stimulus_id"] for item in phase7i_plan.config["stimuli"]
    )
    if (
        stimulus_ids_a != CANONICAL_BATTERY_IDS[: len(stimulus_ids_a)]
        or len(stimulus_ids_a) != 10
    ):
        raise BoundedSensoryCompositionError(
            "Phase 7I subset of the 14-stimulus battery changed."
        )
    a_transfer_comparisons = _assert_nested_transfers(
        conditions,
        phase7i_experiment.result["conditions"],
        sorted(a_ids),
        stimulus_ids_a,
        previous_prefix="phase7i_",
        label="Sample A",
    )
    b_transfer_comparisons = _assert_nested_transfers(
        conditions,
        experiment_b.result["conditions"],
        sorted(b_ids),
        tuple(CANONICAL_BATTERY_IDS),
        previous_prefix="sample_b_stimulus_",
        label="Sample B",
    )
    additive_comparisons = _assert_target_additivity(
        conditions,
        phase7i_experiment.result["conditions"],
        experiment_b.result["conditions"],
        stimulus_ids_a,
    )

    # The A-only/B-only reference masks must exactly reproduce the canonical
    # 16-body reference conditions, including the unchanged LIF readout.
    nested_mask_regressions = []
    for current_id, prior_conditions, prior_id, label in (
        ("sample_a_only", phase7h.result["conditions"], "all16_reference", "A"),
        ("sample_b_only", experiment_b.result["conditions"], "reference_all16", "B"),
    ):
        current = next(row for row in conditions if row["condition_id"] == current_id)
        prior = next(row for row in prior_conditions if row["condition_id"] == prior_id)
        for target_id in TARGET_IDS:
            now_target = next(
                row for row in current["targets"] if row["body_id"] == target_id
            )
            old_target = next(
                row for row in prior["targets"] if row["body_id"] == target_id
            )
            for field in (
                "drive_mveq_by_interval",
                "membrane_mv_by_boundary",
                "filtered_synaptic_mveq_by_boundary",
                "simulated_spikes",
            ):
                if now_target[field] != old_target[field]:
                    raise BoundedSensoryCompositionError(
                        f"Sample {label}-only reference changed {field} "
                        f"for {target_id}."
                    )
        nested_mask_regressions.append(
            {"sample": label, "identical_to_canonical_reference": True}
        )

    body_contributions = {}
    for neuron_type, side in STRATA:
        source_ids = [
            row["body_id"]
            for row in result_c["selected_bodies"]
            if row["neuron_type"] == neuron_type and row["side"] == side
        ]
        body_contributions[f"{neuron_type}_{side}"] = source_ids

    coverage_totals = {
        "body_stimulus_covered": sum(
            row["body_stimulus_covered"] for row in coverage_rows
        ),
        "body_state_exercised": sum(
            row["body_state_exercised"] for row in coverage_rows
        ),
        "body_transfer_exercised": sum(
            row["body_transfer_exercised"] for row in coverage_rows
        ),
        "denominator": SAMPLE_SIZE,
    }
    baseline_sensory_config = experiment_b.config["sensory_model"]
    baseline_transfer_config = experiment_b.config["transfer_model"]
    baseline_dnp01_config = experiment_b.config["dnp01_model"]
    if (
        baseline_sensory_config.get("model_id")
        != "relative_column_exploratory_sensory_state_v1"
        or baseline_sensory_config.get("tau_sens_ms") != 1.0
        or baseline_sensory_config.get("gain") != 1.0
        or baseline_sensory_config.get("initial_state") != 0.0
        or baseline_sensory_config.get("input_metric_id") != "column_overlap_fraction"
        or baseline_transfer_config.get("k_transfer_mveq_per_state") != 1.0
        or baseline_transfer_config.get("structural_weight_used_as_gain") is not False
        or baseline_dnp01_config != phase7h.config["dnp01_model"]
    ):
        raise BoundedSensoryCompositionError("Phase 7E/F/DNp01 invariant changed.")

    config = {
        "schema": POPULATION32_CONFIG_SCHEMA,
        "artifact_schema": POPULATION32_ARTIFACT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "composition_artifact_id": composition["artifact_id"],
        "sample_a_artifact": _reference(sample_a, SAMPLE_ARTIFACT_SCHEMA),
        "sample_b_artifact": _reference(
            sample_b, "bounded_independent_sensory_sample_artifact_v1"
        ),
        "sample_b_coverage_artifact": _reference(
            coverage_b, "bounded_independent_sensory_coverage_plan_artifact_v1"
        ),
        "sample_b_experiment_artifact": _reference(
            experiment_b, "bounded_independent_sensory_population_artifact_v1"
        ),
        "phase7h_experiment_artifact_id": phase7h.artifact_id,
        "phase7i_plan_artifact_id": phase7i_plan.artifact_id,
        "phase7i_experiment_artifact_id": phase7i_experiment.artifact_id,
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _source_circuit_identity(circuit),
        "column_grid_identity": grid.to_identity_dict(),
        "body_ids": list(result_c["body_ids"]),
        "body_count": SAMPLE_SIZE,
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimulus_battery_source": "CANONICAL_SAMPLE_B_COVERAGE_PLAN_V1",
        "stimuli": entries,
        "sensory_model": baseline_sensory_config,
        "transfer_model": baseline_transfer_config,
        "dnp01_model": baseline_dnp01_config,
        "route_contract": [route.to_dict() for route in routes],
        "pathway_controls": [item[0] for item in mask_specs],
        "sensitivity_k_transfer_mveq_per_state": list(K_SENSITIVITY),
        "population_normalization": "none",
        "model_outcomes_used_for_composition_or_battery": False,
        "time_alignment": "sensory_state_boundary_n_drives_interval_n_to_n_plus_1",
        "scientific_boundary": {
            "absolute_visual_angle_present": False,
            "functional_receptive_field_claim": False,
            "physiological_calibration": False,
            "structural_count_is_efficacy": False,
            "body_specific_gain": False,
            "behavior_or_body_mechanics": False,
            "dn_p01_is_existing_model_output": True,
        },
    }
    result = {
        "schema": POPULATION32_RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "composition_artifact_id": composition["artifact_id"],
        "body_ids": list(result_c["body_ids"]),
        "assignment": assignment,
        "sensory_trajectories_by_stimulus": trajectories,
        "anatomical_coverage": anatomical_coverage,
        "body_coverage": coverage_rows,
        "coverage_totals": coverage_totals,
        "conditions": conditions,
        "source_contribution_accounting_validated": True,
        "per_step_A_B_target_additivity": {
            "stimulus_ids": list(stimulus_ids_a),
            "target_step_comparisons": additive_comparisons,
            "passed": True,
        },
        "nested_regression": {
            "sample_a_assignment_body_sample_comparisons": a_assignment_comparisons,
            "sample_b_assignment_body_sample_comparisons": b_assignment_comparisons,
            "sample_a_state_trace_comparisons": a_trajectory_comparisons,
            "sample_b_state_trace_comparisons": b_trajectory_comparisons,
            "sample_a_transfer_source_step_comparisons": a_transfer_comparisons,
            "sample_b_transfer_source_step_comparisons": b_transfer_comparisons,
            "sample_a_only_and_sample_b_only_reference": nested_mask_regressions,
        },
        "side_isolation_checks": side_isolation_checks,
        "source_bodies_by_stratum": body_contributions,
        "comparison_semantics": (
            "COMPOSITIONAL_ARCHITECTURE_ONLY_NOT_BIOLOGICAL_REPLICATION"
        ),
        "result_semantics": (
            "SIMULTANEOUS_32_BODY_EXPLORATORY_SENSORY_TO_DNP01_EXPERIMENT"
        ),
    }
    result["config_stimulus_ids"] = [stimulus.stimulus_id for stimulus in stimuli]
    result["sample_a_b_sample_c_comparison"] = {
        "sample_a_body_count": 16,
        "sample_b_body_count": 16,
        "sample_c_body_count": 32,
        "sample_a_sample_b_overlap_count": 0,
        "sample_c_stimulus_count": len(stimuli),
        "sample_a_stimulus_count": len(phase7i_plan.config["stimuli"]),
        "sample_b_stimulus_count": len(coverage_b.config["stimuli"]),
        "sample_a_assignment_samples": phase7i_experiment.result["assignment"][
            "sample_count"
        ],
        "sample_b_assignment_samples": experiment_b.result["assignment"][
            "sample_count"
        ],
        "sample_c_assignment_samples": assignment["sample_count"],
        "sample_a_coverage_totals": phase7i_experiment.result["coverage_totals"],
        "sample_b_coverage_totals": experiment_b.result["coverage_totals"],
        "sample_c_coverage_totals": coverage_totals,
        "sample_a_max_target_peak_drive": {
            str(target): max(
                row["peak_drive_mveq"]
                for condition in phase7i_experiment.result["conditions"]
                for row in condition["targets"]
                if row["body_id"] == target
            )
            for target in (10001, 10010)
        },
        "sample_b_max_target_peak_drive": {
            str(target): max(
                row["peak_drive_mveq"]
                for condition in experiment_b.result["conditions"]
                for row in condition["targets"]
                if row["body_id"] == target
            )
            for target in (10001, 10010)
        },
        "sample_c_max_target_peak_drive": {
            str(target): max(
                row["peak_drive_mveq"]
                for condition in stimulus_conditions
                for row in condition["targets"]
                if row["body_id"] == target
            )
            for target in (10001, 10010)
        },
        "matched_stimulus_ids": list(stimulus_ids_a),
        "interpretation": "NOT_BIOLOGICAL_REPLICATION_OR_CALIBRATION",
    }
    return config, result


def make_population32_payload(
    composition_path: str,
    *,
    sample_a_path: str = str(DEFAULT_SAMPLE_A_PATH),
    phase7h_path: str = str(DEFAULT_PHASE7H_PATH),
    phase7i_plan_path: str = str(DEFAULT_PHASE7I_PLAN_PATH),
    phase7i_experiment_path: str = str(DEFAULT_PHASE7I_EXPERIMENT_PATH),
    sample_b_path: str = str(DEFAULT_SAMPLE_B_ARTIFACT),
    coverage_b_path: str = str(DEFAULT_COVERAGE_B_ARTIFACT),
    experiment_b_path: str = str(DEFAULT_PHASE7J_ARTIFACT),
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay sources and Sample C, then execute the already-fixed 14-stimulus union."""
    from neurofly.bounded_sensory_composition_artifacts import load_composition_artifact

    context = _load_canonical_phase7j_inputs(
        sample_a_path=sample_a_path,
        phase7h_path=phase7h_path,
        phase7i_plan_path=phase7i_plan_path,
        phase7i_experiment_path=phase7i_experiment_path,
        sample_b_path=sample_b_path,
        coverage_b_path=coverage_b_path,
        experiment_b_path=experiment_b_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    composition = load_composition_artifact(composition_path)
    expected_config, expected_result = compose_samples(
        context["sample_a"], context["sample_b"], context["source"], context["circuit"]
    )
    if composition.config != expected_config or composition.result != expected_result:
        raise BoundedSensoryCompositionError("persisted Sample C failed source replay.")
    return compute_population32_experiment(
        composition.as_input(),
        context["sample_a"],
        context["phase7h"],
        context["phase7i_plan"],
        context["phase7i_experiment"],
        context["sample_b"],
        context["coverage_b"],
        context["experiment_b"],
        context["source"],
        context["grid"],
        context["circuit"],
    )
