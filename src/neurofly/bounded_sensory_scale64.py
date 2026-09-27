"""Phase 7L: deterministic disjoint-sample composition at 64 bodies.

All sample selection and stimulus planning use source anatomy only. Sensory
states and DNp01 readout are computed only after four immutable sample
artifacts and the anatomy-only coverage plan have been fixed.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from neurofly.bounded_sensory_composition import (
    CANONICAL_BATTERY_IDS,
    CANONICAL_PHASE7J_EXPERIMENT_ID,
    CANONICAL_SAMPLE_B_ID,
    DEFAULT_PHASE7J_ARTIFACT,
    DEFAULT_POPULATION32_ROOT,
    _add_source_annotations,
)
from neurofly.bounded_sensory_composition import (
    DEFAULT_COMPOSITION_ROOT as DEFAULT_COMPOSITION32_ROOT,
)
from neurofly.bounded_sensory_composition import (
    _reference as _phase7k_reference,
)
from neurofly.bounded_sensory_composition_artifacts import (
    load_composition_artifact as load_composition32_artifact,
)
from neurofly.bounded_sensory_composition_artifacts import (
    replay_population32_artifact,
)
from neurofly.bounded_sensory_coverage import (
    MAX_RADIUS_LATTICE_STEPS,
    _coverage_candidates_for_side,
)
from neurofly.bounded_sensory_coverage_artifacts import (
    DEFAULT_SAMPLE_ARTIFACT_PATH as DEFAULT_SAMPLE_A_PATH,
)
from neurofly.bounded_sensory_coverage_artifacts import (
    load_coverage_experiment,
)
from neurofly.bounded_sensory_population import (
    STRATA,
    _assignment_result,
    _body_index,
    _condition_states,
    _maximin_candidate,
    _sensory_trajectories,
    _simulate_condition,
    make_source_bundle,
)
from neurofly.bounded_sensory_population_artifacts import (
    load_population_artifact,
    load_sample_artifact,
)
from neurofly.bounded_sensory_robustness import (
    CANONICAL_PHASE7H_ID,
    CANONICAL_PHASE7I_EXPERIMENT_ID,
    CANONICAL_SAMPLE_A_ID,
    DEFAULT_PHASE7H_PATH,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_SAMPLE_B_ROOT,
)
from neurofly.bounded_sensory_robustness_artifacts import (
    load_sample_b_artifact,
    load_sample_b_experiment_artifact,
)
from neurofly.malecns.contract import CircuitContract
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    RelativeColumnAssignmentSource,
    RelativeColumnGrid,
    RelativeColumnStimulus,
    active_column_set,
    canonical_json_bytes,
    compute_body_exposure,
    sha256_bytes,
)
from neurofly.relative_column_dnp01_transfer import Route

SAMPLE64_SIZE = 16
POPULATION64_SIZE = 64
SAMPLE_C_ID = "phase7l_disjoint_16_body_sample_c_v1"
SAMPLE_D_ID = "phase7l_disjoint_16_body_sample_d_v1"
SELECTION_METHOD_ID = "rank_quartile_centroid_maximin_prior_samples_v1"
COMPOSITION_METHOD_ID = "four_persisted_pairwise_disjoint_sample_union_v1"
COVERAGE_METHOD_ID = "minimum_source_column_disk_set_cover_64_v1"
EXPERIMENT_ID = "phase7l_simultaneous_64_body_composition_v1"
REFERENCE_K = 1.0
K_SENSITIVITY = (0.0, 0.5, 1.0, 2.0)
TARGET_IDS = (10001, 10010)
SOURCE_MODEL_ID = "relative_column_exploratory_sensory_state_v1"
TRANSFER_MODEL_ID = "exploratory_edge_routed_model_drive_v1"

SAMPLE_CONFIG_SCHEMA = "bounded_sensory_scale64_sample_config_v1"
SAMPLE_RESULT_SCHEMA = "bounded_sensory_scale64_sample_result_v1"
SAMPLE_ARTIFACT_SCHEMA = "bounded_sensory_scale64_sample_artifact_v1"
COMPOSITION_CONFIG_SCHEMA = "bounded_sensory_composition64_config_v1"
COMPOSITION_RESULT_SCHEMA = "bounded_sensory_composition64_result_v1"
COMPOSITION_ARTIFACT_SCHEMA = "bounded_sensory_composition64_artifact_v1"
PLAN_CONFIG_SCHEMA = "bounded_sensory_coverage64_plan_config_v1"
PLAN_RESULT_SCHEMA = "bounded_sensory_coverage64_plan_result_v1"
PLAN_ARTIFACT_SCHEMA = "bounded_sensory_coverage64_plan_artifact_v1"
EXPERIMENT_CONFIG_SCHEMA = "bounded_sensory_population64_config_v1"
EXPERIMENT_RESULT_SCHEMA = "bounded_sensory_population64_result_v1"
EXPERIMENT_ARTIFACT_SCHEMA = "bounded_sensory_population64_artifact_v1"

CANONICAL_SAMPLE_C_ID = (
    "bd10225993d0101d9a2338e7d18dac772fa4ab9096938de14930ea14df47c301"
)
CANONICAL_SAMPLE_D_ID = (
    "3609c165476f524b8187aed5400421cdd1ca1862fd5b3ab0e5cba2d90a95abe2"
)
CANONICAL_COMPOSITION64_ID = (
    "db5df9b639f5ed834a4e2f408e39bec264552427260eadd8eb8789bcdf431436"
)
CANONICAL_PLAN64_ID = "d92627cb1787b2b566e37d333064d259e5347aae6781b8381558dda233561536"
CANONICAL_EXPERIMENT64_ID = (
    "5095eddbf35c363cf4ae47ef875420ecad725eb0c837767ec8789e65bd68ab02"
)

DEFAULT_SAMPLE_C_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_sample_c_64_v1"
DEFAULT_SAMPLE_D_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_sample_d_64_v1"
DEFAULT_COMPOSITION64_ROOT = (
    DEFAULT_SOURCE_ROOT / "bounded_sensory_composed_sample_64_v1"
)
DEFAULT_PLAN64_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_coverage_plan_64_v1"
DEFAULT_EXPERIMENT64_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_population_64_v1"
DEFAULT_COMPOSITION32_PATH = (
    DEFAULT_COMPOSITION32_ROOT
    / "82ebef1acef2415fd57b9922e815e87e2d60fd76070a93e67103e2f3924198bf"
)
DEFAULT_EXPERIMENT32_PATH = (
    DEFAULT_POPULATION32_ROOT
    / "b6be84a66d3cecde3e7bf05992515dc31521a8ebc5e8feebadf9b5f0560d9405"
)
DEFAULT_SAMPLE_B_PATH = DEFAULT_SAMPLE_B_ROOT / CANONICAL_SAMPLE_B_ID
DEFAULT_PHASE7J_PATH = DEFAULT_PHASE7J_ARTIFACT


class BoundedSensoryScale64Error(ValueError):
    """Invalid Phase 7L source, sample, coverage plan, or experiment."""


def _as_input(artifact: Any) -> dict[str, Any]:
    return artifact.as_input() if hasattr(artifact, "as_input") else dict(artifact)


def _artifact_reference(artifact: Any, schema: str | None = None) -> dict[str, Any]:
    item = _as_input(artifact)
    manifest = item.get("manifest", {})
    resolved_schema = schema or item.get("artifact_schema")
    if resolved_schema is None:
        resolved_schema = {
            CANONICAL_SAMPLE_A_ID: "bounded_sensory_sample_artifact_v1",
            CANONICAL_SAMPLE_B_ID: "bounded_independent_sensory_sample_artifact_v1",
        }.get(item.get("artifact_id"))
    return {
        "artifact_schema": resolved_schema,
        "artifact_id": item["artifact_id"],
        "manifest_sha256": item.get("manifest_sha256"),
        "config_sha256": item["config_sha256"],
        "result_sha256": item["result_sha256"],
        "manifest_body_ids": manifest.get("body_ids"),
    }


def _circuit_identity(circuit: CircuitContract) -> dict[str, Any]:
    return {
        "dataset": circuit.provenance.dataset,
        "candidate_id": circuit.candidate.identifier,
        "candidate_version": circuit.candidate.version,
        "file_sha256": dict(circuit.integrity.sha256_by_file),
    }


def _artifact_id(
    schema: str, config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    config_hash = sha256_bytes(canonical_json_bytes(dict(config)) + b"\n")
    result_hash = sha256_bytes(canonical_json_bytes(dict(result)) + b"\n")
    return sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_schema": schema,
                "config_sha256": config_hash,
                "result_sha256": result_hash,
            }
        )
    )


def scale64_artifact_id(
    kind: str, config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    schemas = {
        "sample": SAMPLE_ARTIFACT_SCHEMA,
        "composition": COMPOSITION_ARTIFACT_SCHEMA,
        "plan": PLAN_ARTIFACT_SCHEMA,
        "experiment": EXPERIMENT_ARTIFACT_SCHEMA,
    }
    try:
        schema = schemas[kind]
    except KeyError:
        raise BoundedSensoryScale64Error("unknown Phase 7L artifact kind.") from None
    return _artifact_id(schema, config, result)


def _balanced_quartile_ranks(
    candidates: Sequence[Mapping[str, Any]],
) -> dict[int, dict[str, int]]:
    ordered = sorted(
        candidates, key=lambda row: (row["structural_weight"], row["body_id"])
    )
    if len(ordered) < 4:
        raise BoundedSensoryScale64Error(
            "a selection stratum has fewer than four candidates."
        )
    result: dict[int, dict[str, int]] = {}
    within: Counter[int] = Counter()
    for rank, row in enumerate(ordered):
        group = min(3, (rank * 4) // len(ordered))
        result[int(row["body_id"])] = {
            "rank_zero_based": rank,
            "rank_group_zero_based": group,
            "rank_within_group_zero_based": within[group],
        }
        within[group] += 1
    if set(within) != {0, 1, 2, 3} or max(within.values()) - min(within.values()) > 1:
        raise BoundedSensoryScale64Error("rank-balanced quartile partition is invalid.")
    return result


def select_disjoint_sample(
    sample_id: str,
    prior_samples: Sequence[Mapping[str, Any]],
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Select one deterministic four-quartile sample using source descriptors only."""
    if sample_id not in {SAMPLE_C_ID, SAMPLE_D_ID}:
        raise BoundedSensoryScale64Error("only Phase 7L Sample C or D may be selected.")
    expected_prior_count = 2 if sample_id == SAMPLE_C_ID else 3
    if len(prior_samples) != expected_prior_count:
        raise BoundedSensoryScale64Error("wrong prior-sample count for this selection.")
    prior_inputs = [_as_input(item) for item in prior_samples]
    if [item["artifact_id"] for item in prior_inputs[:2]] != [
        CANONICAL_SAMPLE_A_ID,
        CANONICAL_SAMPLE_B_ID,
    ]:
        raise BoundedSensoryScale64Error(
            "canonical Sample A/B parent identity mismatch."
        )
    if (
        sample_id == SAMPLE_D_ID
        and prior_inputs[2].get("artifact_schema") != SAMPLE_ARTIFACT_SCHEMA
    ):
        raise BoundedSensoryScale64Error(
            "Sample D requires the persisted Sample C artifact."
        )

    body_rows, _ = _body_index(source, circuit)
    prior_ids: set[int] = set()
    prior_rows_by_stratum: dict[tuple[str, str], list[dict[str, Any]]] = {
        key: [] for key in STRATA
    }
    prior_sample_ids = []
    for sample in prior_inputs:
        ids = sample.get("result", {}).get("body_ids", [])
        if len(ids) != SAMPLE64_SIZE or len(ids) != len(set(ids)):
            raise BoundedSensoryScale64Error("prior sample identity set is malformed.")
        if prior_ids & set(ids):
            raise BoundedSensoryScale64Error("prior samples overlap.")
        prior_ids.update(ids)
        prior_sample_ids.append(sample["artifact_id"])
        for body_id in ids:
            row = body_rows.get(body_id)
            if row is None:
                raise BoundedSensoryScale64Error(
                    "prior body is absent from pinned sources."
                )
            prior_rows_by_stratum[(row["neuron_type"], row["side"])].append(row)

    selected: list[dict[str, Any]] = []
    group_summaries = []
    for neuron_type, side in STRATA:
        stratum_prior = prior_rows_by_stratum[(neuron_type, side)]
        candidates = [
            row
            for row in body_rows.values()
            if row["neuron_type"] == neuron_type
            and row["side"] == side
            and row["body_id"] not in prior_ids
        ]
        ranks = _balanced_quartile_ranks(candidates)
        selected_in_stratum = list(stratum_prior)
        for group in range(4):
            group_candidates = [
                row
                for row in candidates
                if ranks[row["body_id"]]["rank_group_zero_based"] == group
            ]
            chosen, minimum_distance = _maximin_candidate(
                group_candidates, selected_in_stratum
            )
            rank = ranks[chosen["body_id"]]
            chosen_row = dict(chosen)
            chosen_row.update(
                {
                    "selection_rank_group": group + 1,
                    "selection_rank_zero_based": rank["rank_zero_based"],
                    "rank_within_group_zero_based": rank[
                        "rank_within_group_zero_based"
                    ],
                    "rank_group_candidate_count": len(group_candidates),
                    "minimum_hex_centroid_distance_to_prior_samples_and_new_"
                    "sample": minimum_distance,
                    "tie_break": "smallest_body_id_among_exact_maximin_ties",
                    "selected_against_sample_artifact_ids": list(prior_sample_ids),
                    "sentinel": False,
                }
            )
            selected.append(chosen_row)
            selected_in_stratum.append(chosen_row)
            group_summaries.append(
                {
                    "neuron_type": neuron_type,
                    "side": side,
                    "rank_group": group + 1,
                    "candidate_count": len(group_candidates),
                    "selected_body_id": chosen["body_id"],
                    "structural_edge_count_descriptor": chosen["structural_weight"],
                    "minimum_hex_centroid_distance": minimum_distance,
                }
            )

    body_ids = [row["body_id"] for row in selected]
    if len(body_ids) != SAMPLE64_SIZE or len(set(body_ids)) != SAMPLE64_SIZE:
        raise BoundedSensoryScale64Error("new sample must contain 16 unique bodies.")
    if set(body_ids) & prior_ids:
        raise BoundedSensoryScale64Error("new sample overlaps an earlier sample.")
    stratum_counts = [
        {
            "neuron_type": neuron_type,
            "side": side,
            "count": sum(
                row["neuron_type"] == neuron_type and row["side"] == side
                for row in selected
            ),
        }
        for neuron_type, side in STRATA
    ]
    if [row["count"] for row in stratum_counts] != [4, 4, 4, 4]:
        raise BoundedSensoryScale64Error("new sample composition is not exactly 4×4.")

    config = {
        "schema": SAMPLE_CONFIG_SCHEMA,
        "artifact_schema": SAMPLE_ARTIFACT_SCHEMA,
        "sample_id": sample_id,
        "sample_size": SAMPLE64_SIZE,
        "body_ids": body_ids,
        "selection_method_id": SELECTION_METHOD_ID,
        "selection_inputs": [
            "body_id",
            "neuron_type",
            "side",
            "structural_DNp01_edge_count_descriptor",
            "unweighted_anatomical_column_centroid",
            "column_topology_and_occupancy",
            "source_assignment_fraction",
        ],
        "structural_edge_count_semantics": (
            "DESCRIPTIVE_RANK_PARTITION_ONLY_NOT_EFFICACY"
        ),
        "centroid_semantics": "UNWEIGHTED_RELATIVE_COLUMN_ANATOMY_ONLY",
        "exclusion_parent_artifacts": [
            _artifact_reference(item) for item in prior_inputs
        ],
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "strata": [
            {"neuron_type": neuron_type, "side": side, "count": 4}
            for neuron_type, side in STRATA
        ],
        "algorithm": {
            "candidate_sort": "structural_weight_then_body_id",
            "rank_partition": "balanced_floor_rank_times_4_over_candidate_count",
            "rank_group_order": [1, 2, 3, 4],
            "selection_within_group": (
                "maximize_minimum_hex_centroid_distance_to_all_prior_samples_"
                "and_already_selected_new_sample_bodies"
            ),
            "distance": "continuous_extension_of_validated_axial_hex_lattice_norm",
            "tie_break": "smallest_body_id",
        },
        "model_outcomes_used": False,
    }
    result = {
        "schema": SAMPLE_RESULT_SCHEMA,
        "sample_id": sample_id,
        "sample_size": SAMPLE64_SIZE,
        "body_ids": body_ids,
        "selected_bodies": selected,
        "stratum_counts": stratum_counts,
        "rank_group_summaries": group_summaries,
        "excluded_prior_sample_ids": [item["artifact_id"] for item in prior_inputs],
        "prior_overlap_count": 0,
        "selection_semantics": "OUTCOME_BLIND_STRUCTURAL_ANATOMICAL_SAMPLE",
        "model_outcomes_used": False,
        "selection_stage_has_neural_dynamics": False,
    }
    return config, result


def compose_four_samples(
    samples: Sequence[Mapping[str, Any]],
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compose immutable A/B/C/D parent artifacts without new selection."""
    if len(samples) != 4:
        raise BoundedSensoryScale64Error("64-body union requires exactly four parents.")
    inputs = [_as_input(item) for item in samples]
    expected_ids = [CANONICAL_SAMPLE_A_ID, CANONICAL_SAMPLE_B_ID]
    if [item["artifact_id"] for item in inputs[:2]] != expected_ids:
        raise BoundedSensoryScale64Error("A/B parent IDs are not canonical.")
    if (
        inputs[2]["config"].get("sample_id") != SAMPLE_C_ID
        or inputs[3]["config"].get("sample_id") != SAMPLE_D_ID
    ):
        raise BoundedSensoryScale64Error("C/D parents have incorrect sample identity.")
    if len({item["artifact_id"] for item in inputs}) != 4:
        raise BoundedSensoryScale64Error("sample parent artifacts are not distinct.")

    body_rows, _ = _body_index(source, circuit)
    parent_sets: list[set[int]] = []
    selected_by_id: dict[int, dict[str, Any]] = {}
    for item in inputs:
        result = item.get("result", {})
        ids = result.get("body_ids", [])
        selected = result.get("selected_bodies", [])
        if len(ids) != SAMPLE64_SIZE or len(set(ids)) != SAMPLE64_SIZE:
            raise BoundedSensoryScale64Error(
                "a parent sample is not exactly 16 bodies."
            )
        if {row.get("body_id") for row in selected} != set(ids):
            raise BoundedSensoryScale64Error("parent selected-body table is malformed.")
        current = set(ids)
        if any(current & prior for prior in parent_sets):
            raise BoundedSensoryScale64Error(
                "A/B/C/D parents are not pairwise disjoint."
            )
        parent_sets.append(current)
        for row in selected:
            body_id = row["body_id"]
            source_row = body_rows.get(body_id)
            if source_row is None or any(
                source_row[key] != row.get(key)
                for key in (
                    "neuron_type",
                    "side",
                    "target_body_id",
                    "structural_weight",
                    "anatomical_column_centroid",
                )
            ):
                raise BoundedSensoryScale64Error(
                    f"parent identity/route differs from source for {body_id}."
                )
            if body_id in selected_by_id:
                raise BoundedSensoryScale64Error("union contains a duplicate body.")
            selected_by_id[body_id] = dict(row)

    ids = sorted(selected_by_id)
    if len(ids) != POPULATION64_SIZE:
        raise BoundedSensoryScale64Error("four-sample union is not exactly 64 bodies.")
    counts = [
        {
            "neuron_type": neuron_type,
            "side": side,
            "count": sum(
                selected_by_id[body_id]["neuron_type"] == neuron_type
                and selected_by_id[body_id]["side"] == side
                for body_id in ids
            ),
        }
        for neuron_type, side in STRATA
    ]
    if [item["count"] for item in counts] != [16, 16, 16, 16]:
        raise BoundedSensoryScale64Error("union is not exactly 16×4 stratified.")
    target_counts = Counter(selected_by_id[body]["target_body_id"] for body in ids)
    if target_counts != Counter({10001: 32, 10010: 32}):
        raise BoundedSensoryScale64Error(
            "CircuitContract route target composition changed."
        )

    refs = [_artifact_reference(item) for item in inputs]
    config = {
        "schema": COMPOSITION_CONFIG_SCHEMA,
        "artifact_schema": COMPOSITION_ARTIFACT_SCHEMA,
        "composition_id": "phase7l_four_sample_64_body_union_v1",
        "composition_method": COMPOSITION_METHOD_ID,
        "parent_sample_artifacts": refs,
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "body_ids": ids,
        "sample_size": POPULATION64_SIZE,
        "expected_strata": [
            {"neuron_type": neuron_type, "side": side, "count": 16}
            for neuron_type, side in STRATA
        ],
        "model_outcomes_used_for_composition": False,
    }
    pairwise = []
    for left in range(4):
        for right in range(left + 1, 4):
            pairwise.append(
                {
                    "sample_a_artifact_id": inputs[left]["artifact_id"],
                    "sample_b_artifact_id": inputs[right]["artifact_id"],
                    "overlap_count": len(parent_sets[left] & parent_sets[right]),
                    "disjoint": not (parent_sets[left] & parent_sets[right]),
                }
            )
    result = {
        "schema": COMPOSITION_RESULT_SCHEMA,
        "body_ids": ids,
        "sample_size": POPULATION64_SIZE,
        "selected_bodies": [selected_by_id[body] for body in ids],
        "stratum_counts": counts,
        "target_route_counts": [
            {"target_body_id": target, "source_count": target_counts[target]}
            for target in TARGET_IDS
        ],
        "parent_artifact_ids": [item["artifact_id"] for item in inputs],
        "parent_sample_body_ids": {
            label: sorted(parent)
            for label, parent in zip("ABCD", parent_sets, strict=True)
        },
        "pairwise_disjointness": pairwise,
        "pairwise_disjoint": all(row["disjoint"] for row in pairwise),
        "model_outcomes_used": False,
    }
    return config, result


def _source_records(
    body_ids: Sequence[int], source: RelativeColumnAssignmentSource
) -> tuple[dict[int, tuple[Any, ...]], dict[int, Any]]:
    selected = set(body_ids)
    collected: dict[int, list[Any]] = defaultdict(list)
    for record in source.contract.records:
        if record.body_id in selected:
            collected[record.body_id].append(record)
    summaries = {
        row.body_id: row for row in source.contract.summaries if row.body_id in selected
    }
    if set(collected) != selected or set(summaries) != selected:
        raise BoundedSensoryScale64Error("selected bodies lack source column topology.")
    return (
        {body: tuple(sorted(rows)) for body, rows in collected.items()},
        summaries,
    )


def _coverage_rows(
    composition_result: Mapping[str, Any],
    records_by_body: Mapping[int, Sequence[Any]],
    summaries: Mapping[int, Any],
    grid: RelativeColumnGrid,
    stimuli: Sequence[RelativeColumnStimulus],
) -> list[dict[str, Any]]:
    identities = {row["body_id"]: row for row in composition_result["selected_bodies"]}
    maximum: dict[int, float] = dict.fromkeys(composition_result["body_ids"], 0.0)
    covered: dict[int, list[str]] = {body: [] for body in maximum}
    for stimulus in stimuli:
        for radius in stimulus.radii_lattice_steps:
            active = frozenset(active_column_set(stimulus, grid, radius))
            for body_id in maximum:
                value = compute_body_exposure(
                    records_by_body[body_id], summaries[body_id], stimulus, active
                )["column_overlap_fraction"]
                if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                    raise BoundedSensoryScale64Error("anatomical exposure is invalid.")
                maximum[body_id] = max(maximum[body_id], float(value))
                if value > 0.0:
                    covered[body_id].append(stimulus.stimulus_id)
    return [
        {
            "body_id": body,
            "neuron_type": identities[body]["neuron_type"],
            "side": identities[body]["side"],
            "maximum_column_overlap_fraction": maximum[body],
            "covered_stimulus_ids": list(dict.fromkeys(covered[body])),
            "body_stimulus_covered": maximum[body] > 0.0,
            "coverage_semantics": "SOFTWARE_EXPERIMENT_COVERAGE_ONLY",
        }
        for body in composition_result["body_ids"]
    ]


def make_coverage_plan64(
    composition: Mapping[str, Any],
    phase7k_experiment: Any,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Audit retained 14-stimulus anatomy, then set-cover uncovered bodies."""
    comp = _as_input(composition)
    if (
        comp.get("artifact_schema") != COMPOSITION_ARTIFACT_SCHEMA
        or len(comp.get("result", {}).get("body_ids", ())) != POPULATION64_SIZE
    ):
        raise BoundedSensoryScale64Error(
            "coverage planning needs a valid 64-body union."
        )
    if (
        phase7k_experiment.artifact_id == ""
        or phase7k_experiment.result.get("coverage_totals", {}).get("denominator") != 32
    ):
        raise BoundedSensoryScale64Error(
            "canonical Phase 7K stimulus source is invalid."
        )
    entries = phase7k_experiment.config.get("stimuli", ())
    ids = [item.get("config", {}).get("stimulus_id") for item in entries]
    if ids != list(CANONICAL_BATTERY_IDS) or len(entries) != 14:
        raise BoundedSensoryScale64Error(
            "Phase 7K canonical 14-stimulus battery changed."
        )
    for item in entries:
        config = item.get("config")
        if not isinstance(config, Mapping) or item.get("sha256") != sha256_bytes(
            canonical_json_bytes(dict(config))
        ):
            raise BoundedSensoryScale64Error(
                "persisted Phase 7K stimulus hash mismatch."
            )
    base_stimuli = tuple(
        RelativeColumnStimulus.from_dict(dict(item["config"])) for item in entries
    )
    body_ids = comp["result"]["body_ids"]
    records_by_body, summaries = _source_records(body_ids, source)
    initial = _coverage_rows(
        comp["result"], records_by_body, summaries, grid, base_stimuli
    )
    uncovered = [row["body_id"] for row in initial if not row["body_stimulus_covered"]]
    selected_disks: list[dict[str, Any]] = []
    searches = []
    identities = {row["body_id"]: row for row in comp["result"]["selected_bodies"]}
    if uncovered:
        for side in ("L", "R"):
            side_uncovered = [
                body for body in uncovered if identities[body]["side"] == side
            ]
            disks, summary = _coverage_candidates_for_side(
                side, side_uncovered, records_by_body, summaries, grid
            )
            if any(
                not 1 <= row["radius_lattice_steps"] <= MAX_RADIUS_LATTICE_STEPS
                for row in disks
            ):
                raise BoundedSensoryScale64Error(
                    "coverage planner exceeded radius 1–4."
                )
            selected_disks.extend(disks)
            searches.append(summary)
    else:
        searches = [
            {
                "side": side,
                "source_centre_count": 0,
                "candidate_disks_evaluated": 0,
                "nonempty_unique_coverage_masks": 0,
                "selected_disks": 0,
            }
            for side in ("L", "R")
        ]

    extension_entries = []
    extension_rows = []
    for disk in selected_disks:
        h1, h2 = disk["centre_hex"]
        stimulus_id = (
            f"coverage64_{disk['side'].lower()}_{h1:02d}_{h2:02d}_"
            f"r{disk['radius_lattice_steps']}"
        )
        stimulus = RelativeColumnStimulus(
            stimulus_id=stimulus_id,
            side=disk["side"],
            centre_hex1=h1,
            centre_hex2=h2,
            dt_ms=0.1,
            radii_lattice_steps=(disk["radius_lattice_steps"],),
        )
        serialized = stimulus.to_dict()
        if stimulus_id in ids:
            raise BoundedSensoryScale64Error(
                "coverage extension duplicates a retained stimulus."
            )
        extension_entries.append(
            {
                "origin": "PHASE7L_ANATOMY_ONLY_COVERAGE_EXTENSION",
                "config": serialized,
                "sha256": sha256_bytes(canonical_json_bytes(serialized)),
            }
        )
        extension_rows.append(
            {
                **disk,
                "stimulus_id": stimulus_id,
                "centre_is_source_column": True,
                "coverage_basis": "column_overlap_fraction_gt_zero",
                "model_outcomes_used": False,
            }
        )
    all_entries = [
        {
            "origin": "PHASE7K_RETAINED_UNCHANGED",
            "config": dict(item["config"]),
            "sha256": item["sha256"],
        }
        for item in entries
    ] + extension_entries
    all_stimuli = tuple(
        RelativeColumnStimulus.from_dict(item["config"]) for item in all_entries
    )
    final_coverage = _coverage_rows(
        comp["result"], records_by_body, summaries, grid, all_stimuli
    )
    if not all(row["body_stimulus_covered"] for row in final_coverage):
        raise BoundedSensoryScale64Error(
            "radius-limited anatomy-only coverage did not cover all 64 bodies."
        )
    covered_by_extensions = {
        body for row in extension_rows for body in row["covered_body_ids"]
    }
    if covered_by_extensions != set(uncovered):
        raise BoundedSensoryScale64Error(
            "coverage extensions do not exactly cover uncovered bodies."
        )

    config = {
        "schema": PLAN_CONFIG_SCHEMA,
        "artifact_schema": PLAN_ARTIFACT_SCHEMA,
        "plan_method_id": COVERAGE_METHOD_ID,
        "composition_artifact": _artifact_reference(comp, COMPOSITION_ARTIFACT_SCHEMA),
        "phase7k_battery_source": _phase7k_reference(
            phase7k_experiment, "bounded_sensory_population_32_artifact_v1"
        ),
        "source_contract_identity": dict(source.source_identity),
        "column_grid_identity": grid.to_identity_dict(),
        "body_ids": list(body_ids),
        "coverage_metric": "column_overlap_fraction_gt_zero",
        "candidate_centres": "selected_uncovered_bodies_actual_source_columns_only",
        "candidate_radius_lattice_steps": list(range(1, MAX_RADIUS_LATTICE_STEPS + 1)),
        "objective_order": [
            "minimum_added_stimulus_count",
            "minimum_total_radius",
            "lexicographic_radius_then_source_centre",
        ],
        "model_outcomes_used_for_battery_design": False,
        "neural_dynamics_computed": False,
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimuli": all_entries,
    }
    result = {
        "schema": PLAN_RESULT_SCHEMA,
        "body_ids": list(body_ids),
        "initial_stimulus_ids": ids,
        "initial_coverage": initial,
        "initial_uncovered_body_ids": uncovered,
        "candidate_search_summary": searches,
        "coverage_extension_stimuli": extension_rows,
        "final_coverage": final_coverage,
        "final_covered_body_ids": [
            row["body_id"] for row in final_coverage if row["body_stimulus_covered"]
        ],
        "model_outcomes_used": False,
        "dn_p01_outputs_read_for_design": False,
        "neural_dynamics_computed": False,
        "purpose": "SOFTWARE_PATH_COVERAGE",
        "maximum_added_radius_lattice_steps": MAX_RADIUS_LATTICE_STEPS,
    }
    return config, result


def _body_sample_labels(
    parent_sample_ids: Mapping[str, Sequence[int]],
) -> dict[int, str]:
    labels: dict[int, str] = {}
    for label, ids in parent_sample_ids.items():
        for body in ids:
            if body in labels:
                raise BoundedSensoryScale64Error("sample identity sets overlap.")
            labels[body] = label
    return labels


def _coverage_path_rows(
    composition_result: Mapping[str, Any],
    assignment: Mapping[str, Any],
    trajectories: Mapping[str, Sequence[Mapping[str, Any]]],
    stimulus_conditions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    anatomical: dict[int, dict[str, Any]] = {}
    for sample in assignment["samples"]:
        for row in sample["assignments"]:
            item = anatomical.setdefault(
                row["body_id"],
                {
                    "body_id": row["body_id"],
                    "maximum_column_overlap_fraction": 0.0,
                    "positive_exposure_stimulus_ids": [],
                },
            )
            item["maximum_column_overlap_fraction"] = max(
                item["maximum_column_overlap_fraction"],
                row["column_overlap_fraction"],
            )
            if row["column_overlap_fraction"] > 0.0:
                item["positive_exposure_stimulus_ids"].append(sample["stimulus_id"])
    state_peaks = dict.fromkeys(composition_result["body_ids"], 0.0)
    for stimulus_id, rows in trajectories.items():
        for row in rows:
            state_peaks[row["body_id"]] = max(
                state_peaks[row["body_id"]], row["peak_exploratory_state"]
            )
    transfer_peaks = dict.fromkeys(composition_result["body_ids"], 0.0)
    positive_stimuli: dict[int, list[str]] = {
        body: [] for body in composition_result["body_ids"]
    }
    for condition in stimulus_conditions:
        stimulus_id = condition["condition_id"].removeprefix("stimulus::")
        for interval in condition["source_contributions_by_interval"]:
            for row in interval["contributions"]:
                transfer_peaks[row["source_body_id"]] = max(
                    transfer_peaks[row["source_body_id"]], row["model_drive_mveq"]
                )
                if row["model_drive_mveq"] > 0.0:
                    positive_stimuli[row["source_body_id"]].append(stimulus_id)
    identities = {row["body_id"]: row for row in composition_result["selected_bodies"]}
    output = []
    for body in composition_result["body_ids"]:
        row = anatomical[body]
        output.append(
            {
                "body_id": body,
                "neuron_type": identities[body]["neuron_type"],
                "side": identities[body]["side"],
                "target_body_id": identities[body]["target_body_id"],
                **row,
                "max_exploratory_state": state_peaks[body],
                "max_transfer_contribution_mveq": transfer_peaks[body],
                "body_stimulus_covered": row["maximum_column_overlap_fraction"] > 0.0,
                "body_state_exercised": state_peaks[body] > 0.0,
                "body_transfer_exercised": transfer_peaks[body] > 0.0,
                "positive_transfer_stimulus_ids": list(
                    dict.fromkeys(positive_stimuli[body])
                ),
                "coverage_semantics": "SOFTWARE_EXPERIMENT_COVERAGE_ONLY",
            }
        )
    return output


def _assert_accounting64(conditions: Sequence[Mapping[str, Any]]) -> int:
    comparisons = 0
    for condition in conditions:
        targets = {item["body_id"]: item for item in condition["targets"]}
        for interval in condition["source_contributions_by_interval"]:
            for target in TARGET_IDS:
                contributions = [
                    item["model_drive_mveq"]
                    for item in interval["contributions"]
                    if item["target_body_id"] == target
                ]
                value = sum(contributions)
                stored = targets[target]["drive_mveq_by_interval"][interval["step"]]
                if not math.isclose(value, stored, rel_tol=0.0, abs_tol=1e-15):
                    raise BoundedSensoryScale64Error(
                        "64-source target accounting mismatch."
                    )
                comparisons += 1
    return comparisons


def _assert_parent_additivity(
    conditions: Sequence[Mapping[str, Any]],
    body_to_sample: Mapping[int, str],
) -> int:
    comparisons = 0
    for condition in conditions:
        targets = {item["body_id"]: item for item in condition["targets"]}
        for interval in condition["source_contributions_by_interval"]:
            group_sums = {
                name: {target: 0.0 for target in TARGET_IDS} for name in "ABCD"
            }
            for row in interval["contributions"]:
                group = body_to_sample[row["source_body_id"]]
                group_sums[group][row["target_body_id"]] += row["model_drive_mveq"]
            for target in TARGET_IDS:
                parent_sum = sum(group_sums[name][target] for name in "ABCD")
                stored = targets[target]["drive_mveq_by_interval"][interval["step"]]
                if not math.isclose(parent_sum, stored, rel_tol=0.0, abs_tol=1e-15):
                    raise BoundedSensoryScale64Error(
                        "A+B+C+D per-step additivity failed."
                    )
                comparisons += 1
    return comparisons


def _target_fields_equal(
    current: Mapping[str, Any], previous: Mapping[str, Any]
) -> bool:
    return all(
        current[field] == previous[field]
        for field in (
            "drive_mveq_by_interval",
            "membrane_mv_by_boundary",
            "filtered_synaptic_mveq_by_boundary",
            "simulated_spikes",
        )
    )


def compute_population64_experiment(
    composition: Mapping[str, Any],
    coverage_plan: Mapping[str, Any],
    phase7k_experiment: Any,
    phase7h_experiment: Any,
    phase7i_experiment: Any,
    phase7j_experiment: Any,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the fixed 64 union after its parent samples and coverage plan exist."""
    comp = _as_input(composition)
    plan = _as_input(coverage_plan)
    expected_plan_config, expected_plan_result = make_coverage_plan64(
        comp, phase7k_experiment, source, grid
    )
    if (
        plan.get("artifact_schema") != PLAN_ARTIFACT_SCHEMA
        or plan.get("config") != expected_plan_config
        or plan.get("result") != expected_plan_result
    ):
        raise BoundedSensoryScale64Error(
            "persisted 64-body anatomy plan failed replay."
        )
    if (
        comp.get("artifact_schema") != COMPOSITION_ARTIFACT_SCHEMA
        or comp["config"].get("body_ids") != comp["result"].get("body_ids")
        or len(comp["result"]["body_ids"]) != POPULATION64_SIZE
    ):
        raise BoundedSensoryScale64Error("invalid 64-body composition artifact.")

    sample_result = comp["result"]
    stimuli = tuple(
        RelativeColumnStimulus.from_dict(item["config"])
        for item in plan["config"]["stimuli"]
    )
    assignment = _assignment_result(sample_result, source, grid, stimuli)
    trajectories = _sensory_trajectories(assignment, sample_result)
    if tuple(trajectories) != tuple(stimulus.stimulus_id for stimulus in stimuli):
        raise BoundedSensoryScale64Error("64-body sensory stimulus identity changed.")

    sample_sets = {
        label: set(ids)
        for label, ids in comp["result"]["parent_sample_body_ids"].items()
    }
    # The source data and selected-body records, not array position, determine routes.
    routes = []
    body_rows = {row["body_id"]: row for row in sample_result["selected_bodies"]}
    source_rows, _ = _body_index(source, circuit)
    for body in sample_result["body_ids"]:
        row = body_rows[body]
        if (row["neuron_type"], row["side"], row["target_body_id"]) != (
            source_rows[body]["neuron_type"],
            source_rows[body]["side"],
            source_rows[body]["target_body_id"],
        ):
            raise BoundedSensoryScale64Error(
                "route does not match pinned CircuitContract."
            )
        if row["structural_weight"] != source_rows[body]["structural_weight"]:
            raise BoundedSensoryScale64Error(
                "structural route count differs from CircuitContract."
            )
        routes.append(
            Route(
                source_body_id=body,
                target_body_id=row["target_body_id"],
                structural_weight=row["structural_weight"],
                source_type=row["neuron_type"],
                side=row["side"],
            )
        )
    routes = tuple(sorted(routes, key=lambda row: row.source_body_id))
    if (
        len(routes) != POPULATION64_SIZE
        or len({route.source_body_id for route in routes}) != POPULATION64_SIZE
    ):
        raise BoundedSensoryScale64Error(
            "64-body route set is incomplete or duplicated."
        )
    target_counts = Counter(route.target_body_id for route in routes)
    if target_counts != Counter({10001: 32, 10010: 32}):
        raise BoundedSensoryScale64Error("64-body route target counts changed.")

    expected_sensory = phase7k_experiment.config["sensory_model"]
    expected_transfer = phase7k_experiment.config["transfer_model"]
    expected_dnp01 = phase7k_experiment.config["dnp01_model"]
    if (
        expected_sensory.get("model_id") != SOURCE_MODEL_ID
        or expected_sensory.get("tau_sens_ms") != 1.0
        or expected_sensory.get("gain") != 1.0
        or expected_sensory.get("initial_state") != 0.0
        or expected_sensory.get("input_metric_id") != "column_overlap_fraction"
        or expected_transfer.get("model_id") != TRANSFER_MODEL_ID
        or expected_transfer.get("k_transfer_mveq_per_state") != REFERENCE_K
        or expected_transfer.get("structural_weight_used_as_gain") is not False
        or expected_dnp01 != phase7h_experiment.config["dnp01_model"]
        or expected_dnp01 != phase7j_experiment.config["dnp01_model"]
    ):
        raise BoundedSensoryScale64Error(
            "Phase 7E/F/DNp01 reference assumptions changed."
        )

    # Nested trajectory checks use the canonical parent outputs only after C/D
    # and the coverage plan have already been fixed and persisted.
    nested_states = {"A": 0, "B": 0, "C": 0, "D": 0}
    for label, prior_experiment in (
        ("A", phase7i_experiment),
        ("B", phase7j_experiment),
    ):
        previous = prior_experiment.result["sensory_trajectories_by_stimulus"]
        parent_ids = sample_sets[label]
        for stimulus_id in previous:
            current_rows = {row["body_id"]: row for row in trajectories[stimulus_id]}
            for body in parent_ids:
                if current_rows[body] != next(
                    row for row in previous[stimulus_id] if row["body_id"] == body
                ):
                    raise BoundedSensoryScale64Error(
                        f"Sample {label} sensory trajectory changed for "
                        f"{body}/{stimulus_id}."
                    )
                nested_states[label] += 1

    standalone_state_checks = {"C": 0, "D": 0}
    for label in ("C", "D"):
        subset_ids = sample_sets[label]
        subset_result = {
            **sample_result,
            "body_ids": sorted(subset_ids),
            "selected_bodies": [body_rows[body] for body in sorted(subset_ids)],
        }
        subset_assignment = {
            **assignment,
            "body_ids": sorted(subset_ids),
            "samples": [
                {
                    **sample,
                    "assignments": [
                        row
                        for row in sample["assignments"]
                        if row["body_id"] in subset_ids
                    ],
                }
                for sample in assignment["samples"]
            ],
        }
        standalone = _sensory_trajectories(subset_assignment, subset_result)
        for stimulus_id in trajectories:
            standalone_by_body = {
                row["body_id"]: row for row in standalone[stimulus_id]
            }
            for body in subset_ids:
                current = next(
                    row for row in trajectories[stimulus_id] if row["body_id"] == body
                )
                if current != standalone_by_body[body]:
                    raise BoundedSensoryScale64Error(
                        "C/D standalone state calculation changed."
                    )
                standalone_state_checks[label] += 1

    # Every stimulus is run for all 64 bodies and for the already-validated A+B
    # subset. The latter must reproduce the immutable Phase 7K result.
    conditions: list[dict[str, Any]] = []
    stimulus_conditions: dict[str, dict[str, Any]] = {}
    ab_stimulus_conditions: dict[str, dict[str, Any]] = {}
    union_ids = set(sample_result["body_ids"])
    ab_ids = sample_sets["A"] | sample_sets["B"]
    for stimulus in stimuli:
        states = {
            row["body_id"]: [sample["state_value"] for sample in row["state_timeline"]]
            for row in trajectories[stimulus.stimulus_id]
        }
        steps = len(next(iter(states.values()))) - 1
        full = _simulate_condition(
            condition_id=f"stimulus::{stimulus.stimulus_id}",
            pathway_mask="all64",
            active_body_ids=union_ids,
            k=REFERENCE_K,
            states=states,
            dt_ms=stimulus.dt_ms,
            steps=steps,
            routes=routes,
            circuit=circuit,
        )
        _add_source_annotations(full, states, body_rows)
        ab = _simulate_condition(
            condition_id=f"sample_ab_stimulus::{stimulus.stimulus_id}",
            pathway_mask="sample_ab",
            active_body_ids=ab_ids,
            k=REFERENCE_K,
            states=states,
            dt_ms=stimulus.dt_ms,
            steps=steps,
            routes=routes,
            circuit=circuit,
        )
        _add_source_annotations(ab, states, body_rows)
        conditions.extend((full, ab))
        stimulus_conditions[stimulus.stimulus_id] = full
        ab_stimulus_conditions[stimulus.stimulus_id] = ab

    reference_states, reference_dt, reference_steps = _condition_states(
        trajectories, sample_result, "left_expand_33_29", "right_expand_23_09"
    )
    mask_specs = (
        ("all64_reference", "all64", union_ids, REFERENCE_K),
        ("k_zero", "all64", union_ids, 0.0),
        ("no_sources", "none", set(), REFERENCE_K),
        (
            "lc4_only",
            "LC4",
            {body for body in union_ids if body_rows[body]["neuron_type"] == "LC4"},
            REFERENCE_K,
        ),
        (
            "lplc2_only",
            "LPLC2",
            {body for body in union_ids if body_rows[body]["neuron_type"] == "LPLC2"},
            REFERENCE_K,
        ),
        (
            "left_only",
            "left",
            {body for body in union_ids if body_rows[body]["side"] == "L"},
            REFERENCE_K,
        ),
        (
            "right_only",
            "right",
            {body for body in union_ids if body_rows[body]["side"] == "R"},
            REFERENCE_K,
        ),
        ("sample_a_only", "sample_a", sample_sets["A"], REFERENCE_K),
        ("sample_b_only", "sample_b", sample_sets["B"], REFERENCE_K),
        ("sample_c_only", "sample_c", sample_sets["C"], REFERENCE_K),
        ("sample_d_only", "sample_d", sample_sets["D"], REFERENCE_K),
        ("sample_ab_only", "sample_ab", ab_ids, REFERENCE_K),
        (
            "sample_cd_only",
            "sample_cd",
            sample_sets["C"] | sample_sets["D"],
            REFERENCE_K,
        ),
        ("sensitivity_k_0_5", "all64", union_ids, 0.5),
        ("sensitivity_k_2", "all64", union_ids, 2.0),
    )
    for condition_id, mask, active, coefficient in mask_specs:
        condition = _simulate_condition(
            condition_id=condition_id,
            pathway_mask=mask,
            active_body_ids=set(active),
            k=coefficient,
            states=reference_states,
            dt_ms=reference_dt,
            steps=reference_steps,
            routes=routes,
            circuit=circuit,
        )
        _add_source_annotations(condition, reference_states, body_rows)
        conditions.append(condition)

    accounting_comparisons = _assert_accounting64(conditions)
    body_to_sample = {
        body: label
        for label, ids_for_sample in sample_sets.items()
        for body in ids_for_sample
    }
    additivity_comparisons = _assert_parent_additivity(conditions, body_to_sample)

    k_conditions = {
        row["condition_id"]: row for row in phase7k_experiment.result["conditions"]
    }
    nested_32 = []
    for stimulus_id, current in ab_stimulus_conditions.items():
        previous = k_conditions.get(f"stimulus::{stimulus_id}")
        if previous is None:
            if stimulus_id in CANONICAL_BATTERY_IDS:
                raise BoundedSensoryScale64Error(
                    "a retained Phase 7K stimulus condition is missing."
                )
            continue
        for target in TARGET_IDS:
            now = next(row for row in current["targets"] if row["body_id"] == target)
            old = next(row for row in previous["targets"] if row["body_id"] == target)
            if not _target_fields_equal(now, old):
                raise BoundedSensoryScale64Error(
                    f"A+B-only mask differs from Phase 7K for {target}/{stimulus_id}."
                )
        for interval_now, interval_old in zip(
            current["source_contributions_by_interval"],
            previous["source_contributions_by_interval"],
            strict=True,
        ):
            now_rows = {
                row["source_body_id"]: row
                for row in interval_now["contributions"]
                if row["source_body_id"] in ab_ids
            }
            old_rows = {
                row["source_body_id"]: row for row in interval_old["contributions"]
            }
            if now_rows != old_rows:
                raise BoundedSensoryScale64Error(
                    f"A+B per-source ledger differs from Phase 7K at {stimulus_id}."
                )
        nested_32.append(
            {
                "stimulus_id": stimulus_id,
                "per_source_contributions_identical": True,
                "dn_p01_drive_membrane_events_identical": True,
            }
        )

    k_reference = next(
        row for row in conditions if row["condition_id"] == "sample_ab_only"
    )
    previous_reference = next(
        row
        for row in phase7k_experiment.result["conditions"]
        if row["condition_id"] == "all32_reference"
    )
    for target in TARGET_IDS:
        now = next(row for row in k_reference["targets"] if row["body_id"] == target)
        old = next(
            row for row in previous_reference["targets"] if row["body_id"] == target
        )
        if not _target_fields_equal(now, old):
            raise BoundedSensoryScale64Error(
                "A+B reference control differs from Phase 7K."
            )

    coverage_rows = _coverage_path_rows(
        sample_result, assignment, trajectories, list(stimulus_conditions.values())
    )
    if len(coverage_rows) != POPULATION64_SIZE or any(
        not row["body_stimulus_covered"]
        or not row["body_state_exercised"]
        or not row["body_transfer_exercised"]
        for row in coverage_rows
    ):
        raise BoundedSensoryScale64Error("64/64 non-zero-path coverage failed.")

    side_checks = 0
    assignment_by_key = {
        (sample["stimulus_id"], row["body_id"]): row
        for sample in assignment["samples"]
        for row in sample["assignments"]
    }
    for stimulus in stimuli:
        condition = stimulus_conditions[stimulus.stimulus_id]
        for row in sample_result["selected_bodies"]:
            if row["side"] == stimulus.side:
                continue
            if any(
                assignment_by_key[(stimulus.stimulus_id, row["body_id"])][
                    "column_overlap_fraction"
                ]
                != 0.0
                for _ in (0,)
            ):
                raise BoundedSensoryScale64Error(
                    "unilateral anatomical input crossed sides."
                )
            for interval in condition["source_contributions_by_interval"]:
                contribution = next(
                    item
                    for item in interval["contributions"]
                    if item["source_body_id"] == row["body_id"]
                )
                if (
                    contribution["sensory_state"] != 0.0
                    or contribution["model_drive_mveq"] != 0.0
                ):
                    raise BoundedSensoryScale64Error(
                        "unilateral neural/model path crossed sides."
                    )
                side_checks += 1

    # Check source states against 7H/7I/7J on every equivalent body/stimulus.
    sample_a_state_comparisons = nested_states["A"]
    sample_b_state_comparisons = nested_states["B"]
    parent_mask_regressions = []
    previous_masks = (
        ("sample_a_only", phase7h_experiment.result, "all16_reference"),
        ("sample_b_only", phase7j_experiment.result, "reference_all16"),
    )
    for current_id, old_result, old_id in previous_masks:
        current = next(row for row in conditions if row["condition_id"] == current_id)
        previous = next(
            row for row in old_result["conditions"] if row["condition_id"] == old_id
        )
        if any(
            not _target_fields_equal(
                next(row for row in current["targets"] if row["body_id"] == target),
                next(row for row in previous["targets"] if row["body_id"] == target),
            )
            for target in TARGET_IDS
        ):
            raise BoundedSensoryScale64Error(f"Sample {current_id} reference changed.")
        parent_mask_regressions.append({"condition_id": current_id, "identical": True})

    config = {
        "schema": EXPERIMENT_CONFIG_SCHEMA,
        "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "composition_artifact": _artifact_reference(comp, COMPOSITION_ARTIFACT_SCHEMA),
        "coverage_plan_artifact": _artifact_reference(plan, PLAN_ARTIFACT_SCHEMA),
        "phase7k_32_body_artifact_id": phase7k_experiment.artifact_id,
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "column_grid_identity": grid.to_identity_dict(),
        "parent_sample_artifacts": comp["config"]["parent_sample_artifacts"],
        "body_ids": list(sample_result["body_ids"]),
        "body_count": POPULATION64_SIZE,
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimuli": plan["config"]["stimuli"],
        "sensory_model": expected_sensory,
        "transfer_model": expected_transfer,
        "dnp01_model": expected_dnp01,
        "route_contract": [route.to_dict() for route in routes],
        "sample_masks": {label: sorted(ids) for label, ids in sample_sets.items()},
        "pathway_controls": [row[0] for row in mask_specs],
        "sensitivity_k_transfer_mveq_per_state": list(K_SENSITIVITY),
        "population_normalization": "none",
        "time_alignment": "sensory_state_boundary_n_drives_interval_n_to_n_plus_1",
        "model_outcomes_used_for_selection_or_coverage": False,
        "scientific_boundary": {
            "absolute_visual_angle_present": False,
            "functional_receptive_field_claim": False,
            "physiological_calibration": False,
            "structural_count_is_efficacy": False,
            "body_specific_gain": False,
            "behavior_or_body_mechanics": False,
            "sensory_state_is_exploratory": True,
            "dn_p01_is_existing_model_output": True,
        },
    }
    target_summary = {}
    for target in TARGET_IDS:
        rows = [
            target_row
            for condition in conditions
            for target_row in condition["targets"]
            if target_row["body_id"] == target
        ]
        target_summary[str(target)] = {
            "maximum_peak_drive_mveq": max(
                (row["peak_drive_mveq"] for row in rows), default=0.0
            ),
            "minimum_membrane_mv": min(
                (row["minimum_membrane_mv"] for row in rows), default=-52.0
            ),
            "maximum_membrane_mv": max(
                (row["maximum_membrane_mv"] for row in rows), default=-52.0
            ),
            "simulated_spike_count": sum(len(row["simulated_spikes"]) for row in rows),
        }

    result = {
        "schema": EXPERIMENT_RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "composition_artifact_id": comp["artifact_id"],
        "coverage_plan_artifact_id": plan["artifact_id"],
        "body_ids": list(sample_result["body_ids"]),
        "assignment": assignment,
        "sensory_trajectories_by_stimulus": trajectories,
        "anatomical_coverage": plan["result"]["final_coverage"],
        "body_coverage": coverage_rows,
        "coverage_totals": {
            "body_stimulus_covered": sum(
                row["body_stimulus_covered"] for row in coverage_rows
            ),
            "body_state_exercised": sum(
                row["body_state_exercised"] for row in coverage_rows
            ),
            "body_transfer_exercised": sum(
                row["body_transfer_exercised"] for row in coverage_rows
            ),
            "denominator": POPULATION64_SIZE,
        },
        "conditions": conditions,
        "condition_count": len(conditions),
        "per_step_source_accounting_comparisons": accounting_comparisons,
        "per_step_A_B_C_D_additivity_comparisons": additivity_comparisons,
        "sample_a_state_trace_comparisons": sample_a_state_comparisons,
        "sample_b_state_trace_comparisons": sample_b_state_comparisons,
        "sample_c_standalone_state_comparisons": standalone_state_checks["C"],
        "sample_d_standalone_state_comparisons": standalone_state_checks["D"],
        "sample_a_only_and_sample_b_only_reference": parent_mask_regressions,
        "phase7k_A_B_only_nested_regression": nested_32,
        "side_isolation_checks": side_checks,
        "target_summary": target_summary,
        "source_bodies_by_stratum": {
            f"{neuron_type}_{side}": [
                body
                for body in sample_result["body_ids"]
                if body_rows[body]["neuron_type"] == neuron_type
                and body_rows[body]["side"] == side
            ]
            for neuron_type, side in STRATA
        },
        "source_bodies_by_parent_sample": {
            label: sorted(ids) for label, ids in sample_sets.items()
        },
        "source_contribution_accounting_validated": True,
        "parent_additivity_validated": True,
        "comparison_semantics": (
            "COMPOSITIONAL_ARCHITECTURE_ONLY_NOT_BIOLOGICAL_REPLICATION"
        ),
        "result_semantics": (
            "SIMULTANEOUS_64_BODY_EXPLORATORY_SENSORY_TO_DNP01_EXPERIMENT"
        ),
    }
    return config, result


def canonical_phase7l_context() -> dict[str, Any]:
    """Replay A/B/7K first, then return their immutable source artifacts."""
    composition32 = load_composition32_artifact(DEFAULT_COMPOSITION32_PATH)
    phase7k = replay_population32_artifact(
        DEFAULT_EXPERIMENT32_PATH, DEFAULT_COMPOSITION32_PATH
    )
    if composition32.artifact_id != phase7k.result["composition_artifact_id"]:
        raise BoundedSensoryScale64Error(
            "Phase 7K parent composition reference mismatch."
        )
    sample_a = load_sample_artifact(DEFAULT_SAMPLE_A_PATH)
    sample_b = load_sample_b_artifact(DEFAULT_SAMPLE_B_PATH)
    if (
        sample_a.artifact_id != CANONICAL_SAMPLE_A_ID
        or sample_b.artifact_id != CANONICAL_SAMPLE_B_ID
    ):
        raise BoundedSensoryScale64Error("canonical persisted A/B identity changed.")
    # The full Phase 7K replay above replays and verifies A, B, 7D–7J and the
    # 32-body composition against pinned source data before any new selection.
    phase7h = load_population_artifact(DEFAULT_PHASE7H_PATH)
    phase7i = load_coverage_experiment(DEFAULT_PHASE7I_EXPERIMENT_PATH)
    phase7j = load_sample_b_experiment_artifact(DEFAULT_PHASE7J_PATH)
    if (
        phase7h.artifact_id != CANONICAL_PHASE7H_ID
        or phase7i.artifact_id != CANONICAL_PHASE7I_EXPERIMENT_ID
        or phase7j.artifact_id != CANONICAL_PHASE7J_EXPERIMENT_ID
        or phase7k.artifact_id
        != "b6be84a66d3cecde3e7bf05992515dc31521a8ebc5e8feebadf9b5f0560d9405"
    ):
        raise BoundedSensoryScale64Error(
            "a canonical parent artifact identity changed."
        )
    source, grid, circuit = make_source_bundle()
    return {
        "sample_a": sample_a,
        "sample_b": sample_b,
        "composition32": composition32,
        "phase7k": phase7k,
        "phase7h": phase7h,
        "phase7i": phase7i,
        "phase7j": phase7j,
        "source": source,
        "grid": grid,
        "circuit": circuit,
    }
