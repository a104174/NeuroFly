"""Phase 7M: deterministic eight-sample composition at 128 sensory bodies.

Selection and coverage planning are source/anatomy-only and are persisted
before sensory states or DNp01 model outputs are computed. The 128-body path
reuses the validated Phase 7E/7F primitives without changing their meaning.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from neurofly.bounded_sensory_composition import _add_source_annotations
from neurofly.bounded_sensory_coverage import (
    MAX_RADIUS_LATTICE_STEPS,
    _coverage_candidates_for_side,
)
from neurofly.bounded_sensory_population import (
    STRATA,
    _assignment_result,
    _body_index,
    _condition_states,
    _maximin_candidate,
    _sensory_trajectories,
    _simulate_condition,
)
from neurofly.bounded_sensory_robustness import (
    CANONICAL_SAMPLE_A_ID,
)
from neurofly.bounded_sensory_scale64 import (
    CANONICAL_COMPOSITION64_ID,
    CANONICAL_EXPERIMENT64_ID,
    CANONICAL_PLAN64_ID,
    CANONICAL_SAMPLE_C_ID,
    CANONICAL_SAMPLE_D_ID,
    _assert_accounting64,
    _coverage_path_rows,
    _coverage_rows,
    _target_fields_equal,
    canonical_phase7l_context,
    compose_four_samples,
    compute_population64_experiment,
    make_coverage_plan64,
)
from neurofly.bounded_sensory_scale64 import (
    _artifact_reference as _reference64,
)
from neurofly.bounded_sensory_scale64_artifacts import (
    load_scale64_artifact,
    scale64_artifact_path,
)
from neurofly.malecns.contract import CircuitContract
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    RelativeColumnAssignmentSource,
    RelativeColumnGrid,
    RelativeColumnStimulus,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.relative_column_dnp01_transfer import Route

SAMPLE_SIZE = 16
POPULATION_SIZE = 128
SAMPLE_LABELS = tuple("ABCDEFGH")
NEW_SAMPLE_LABELS = tuple("EFGH")
SAMPLE_IDS = {
    label: f"phase7m_disjoint_16_body_sample_{label.lower()}_v1"
    for label in NEW_SAMPLE_LABELS
}
SELECTION_METHOD_ID = "rank_quartile_centroid_maximin_all_prior_samples_v1"
COMPOSITION_METHOD_ID = "eight_persisted_pairwise_disjoint_sample_union_v1"
COVERAGE_METHOD_ID = "minimum_source_column_disk_set_cover_128_v1"
EXPERIMENT_ID = "phase7m_simultaneous_128_body_composition_v1"
REFERENCE_K = 1.0
K_SENSITIVITY = (0.0, 1.0, 2.0)
TARGET_IDS = (10001, 10010)
SOURCE_MODEL_ID = "relative_column_exploratory_sensory_state_v1"
TRANSFER_MODEL_ID = "exploratory_edge_routed_model_drive_v1"

SAMPLE_CONFIG_SCHEMA = "bounded_sensory_scale128_sample_config_v1"
SAMPLE_RESULT_SCHEMA = "bounded_sensory_scale128_sample_result_v1"
SAMPLE_ARTIFACT_SCHEMA = "bounded_sensory_scale128_sample_artifact_v1"
COMPOSITION_CONFIG_SCHEMA = "bounded_sensory_composition128_config_v1"
COMPOSITION_RESULT_SCHEMA = "bounded_sensory_composition128_result_v1"
COMPOSITION_ARTIFACT_SCHEMA = "bounded_sensory_composition128_artifact_v1"
PLAN_CONFIG_SCHEMA = "bounded_sensory_coverage128_plan_config_v1"
PLAN_RESULT_SCHEMA = "bounded_sensory_coverage128_plan_result_v1"
PLAN_ARTIFACT_SCHEMA = "bounded_sensory_coverage128_plan_artifact_v1"
EXPERIMENT_CONFIG_SCHEMA = "bounded_sensory_population128_config_v1"
EXPERIMENT_RESULT_SCHEMA = "bounded_sensory_population128_result_v1"
EXPERIMENT_ARTIFACT_SCHEMA = "bounded_sensory_population128_artifact_v1"

DEFAULT_SAMPLE_ROOTS = {
    label: DEFAULT_SOURCE_ROOT / f"bounded_sensory_sample_{label.lower()}_128_v1"
    for label in NEW_SAMPLE_LABELS
}
DEFAULT_COMPOSITION_ROOT = (
    DEFAULT_SOURCE_ROOT / "bounded_sensory_composed_sample_128_v1"
)
DEFAULT_PLAN_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_coverage_plan_128_v1"
DEFAULT_EXPERIMENT_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_population_128_v1"

CANONICAL_SAMPLE_IDS = {
    "E": "311ebc053a677618d0155812395d04a4995e39a06b93a9c67ecbefca3e512b92",
    "F": "915b7a1a1fd3d1072f760e7b52400f19e1fcfcbaf81d516abba3f797c7aef9ee",
    "G": "4fc1f3a6f25b06d240ed0fad87e16bbc6825f176f5212992dd5558caf8fe7e5a",
    "H": "5dea356903c85950e1f87729c6bedbb591419bb4ba9ae689761f24add1d0d754",
}
CANONICAL_COMPOSITION128_ID = (
    "d77ed3bf0db9d09b66e047fc349cee1b29bff59459d5d6b5639f695ef2cc983c"
)
CANONICAL_PLAN128_ID = (
    "2e0750448f72640b0231c3efe5638235ceddada459821cb31ccc9ce7795d922d"
)
CANONICAL_EXPERIMENT128_ID = (
    "3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6"
)


class BoundedSensoryScale128Error(ValueError):
    """Invalid Phase 7M source, sample, coverage plan, or experiment."""


def _as_input(artifact: Any) -> dict[str, Any]:
    return artifact.as_input() if hasattr(artifact, "as_input") else dict(artifact)


def _circuit_identity(circuit: CircuitContract) -> dict[str, Any]:
    return {
        "dataset": circuit.provenance.dataset,
        "candidate_id": circuit.candidate.identifier,
        "candidate_version": circuit.candidate.version,
        "file_sha256": dict(circuit.integrity.sha256_by_file),
    }


def _artifact_reference(artifact: Any) -> dict[str, Any]:
    item = _as_input(artifact)
    return {
        "artifact_schema": item.get("artifact_schema"),
        "artifact_id": item["artifact_id"],
        "manifest_sha256": item.get("manifest_sha256"),
        "config_sha256": item.get("config_sha256"),
        "result_sha256": item.get("result_sha256"),
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


def scale128_artifact_id(
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
        raise BoundedSensoryScale128Error("unknown Phase 7M artifact kind.") from None
    return _artifact_id(schema, config, result)


def scale128_artifact_path(kind: str, artifact_id: str, *, label: str | None = None):
    if kind == "sample":
        if label not in NEW_SAMPLE_LABELS:
            raise BoundedSensoryScale128Error("sample path requires E, F, G, or H.")
        root = DEFAULT_SAMPLE_ROOTS[label]
    else:
        roots = {
            "composition": DEFAULT_COMPOSITION_ROOT,
            "plan": DEFAULT_PLAN_ROOT,
            "experiment": DEFAULT_EXPERIMENT_ROOT,
        }
        try:
            root = roots[kind]
        except KeyError:
            raise BoundedSensoryScale128Error(
                "unknown Phase 7M artifact kind."
            ) from None
    return root / artifact_id


def canonical_phase7m_context() -> dict[str, Any]:
    """Replay the committed 64-body experiment before any 7M selection."""
    context = canonical_phase7l_context()
    sample_c = load_scale64_artifact(
        scale64_artifact_path("sample", CANONICAL_SAMPLE_C_ID, sample_label="C"),
        "sample",
    )
    sample_d = load_scale64_artifact(
        scale64_artifact_path("sample", CANONICAL_SAMPLE_D_ID, sample_label="D"),
        "sample",
    )
    composition64 = load_scale64_artifact(
        scale64_artifact_path("composition", CANONICAL_COMPOSITION64_ID),
        "composition",
    )
    plan64 = load_scale64_artifact(
        scale64_artifact_path("plan", CANONICAL_PLAN64_ID), "plan"
    )
    experiment64 = load_scale64_artifact(
        scale64_artifact_path("experiment", CANONICAL_EXPERIMENT64_ID), "experiment"
    )
    if (
        sample_c.artifact_id != CANONICAL_SAMPLE_C_ID
        or sample_d.artifact_id != CANONICAL_SAMPLE_D_ID
    ):
        raise BoundedSensoryScale128Error("canonical 7L C/D samples changed.")
    expected_comp = compose_four_samples(
        [
            context["sample_a"].as_input(),
            context["sample_b"].as_input(),
            sample_c.as_input(),
            sample_d.as_input(),
        ],
        context["source"],
        context["circuit"],
    )
    if expected_comp != (composition64.config, composition64.result):
        raise BoundedSensoryScale128Error(
            "canonical 64-body composition replay failed."
        )
    expected_plan = make_coverage_plan64(
        composition64.as_input(), context["phase7k"], context["source"], context["grid"]
    )
    if expected_plan != (plan64.config, plan64.result):
        raise BoundedSensoryScale128Error("canonical 64-body coverage replay failed.")
    expected_experiment = compute_population64_experiment(
        composition64.as_input(),
        plan64.as_input(),
        context["phase7k"],
        context["phase7h"],
        context["phase7i"],
        context["phase7j"],
        context["source"],
        context["grid"],
        context["circuit"],
    )
    if expected_experiment != (experiment64.config, experiment64.result):
        raise BoundedSensoryScale128Error(
            "canonical Phase 7L experiment replay failed."
        )
    context.update(
        {
            "sample_c": sample_c,
            "sample_d": sample_d,
            "composition64": composition64,
            "plan64": plan64,
            "experiment64": experiment64,
        }
    )
    return context


def _prior_samples_for_label(
    label: str, context: Mapping[str, Any], new_samples: Mapping[str, Any]
) -> list[Any]:
    all_samples = {
        "A": context["sample_a"],
        "B": context["sample_b"],
        "C": context["sample_c"],
        "D": context["sample_d"],
        **new_samples,
    }
    return [all_samples[item] for item in SAMPLE_LABELS[: SAMPLE_LABELS.index(label)]]


def select_sample128(
    label: str,
    prior_samples: Sequence[Any],
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Select one outcome-blind 4×4 sample using the Phase 7L rank/maximin rule."""
    if label not in NEW_SAMPLE_LABELS:
        raise BoundedSensoryScale128Error("Phase 7M may select only samples E–H.")
    expected_prior_count = SAMPLE_LABELS.index(label)
    inputs = [_as_input(item) for item in prior_samples]
    if len(inputs) != expected_prior_count:
        raise BoundedSensoryScale128Error("wrong prior sample count.")
    expected_parent_ids = [
        context_id
        for context_id in (
            CANONICAL_SAMPLE_A_ID,
            "873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33",
            CANONICAL_SAMPLE_C_ID,
            CANONICAL_SAMPLE_D_ID,
        )
    ]
    if [item["artifact_id"] for item in inputs[:4]] != expected_parent_ids:
        raise BoundedSensoryScale128Error("persisted parent A–D identities changed.")
    if any(
        item.get("result", {}).get("model_outcomes_used") is True for item in inputs
    ):
        raise BoundedSensoryScale128Error("model outcomes cannot be selection inputs.")

    body_rows, _ = _body_index(source, circuit)
    used: set[int] = set()
    prior_rows_by_stratum = {key: [] for key in STRATA}
    for item in inputs:
        ids = item.get("result", {}).get("body_ids", ())
        selected = item.get("result", {}).get("selected_bodies", ())
        if len(ids) != SAMPLE_SIZE or len(set(ids)) != SAMPLE_SIZE:
            raise BoundedSensoryScale128Error("prior sample identity is malformed.")
        if set(ids) & used or {row.get("body_id") for row in selected} != set(ids):
            raise BoundedSensoryScale128Error("prior samples overlap or are malformed.")
        used.update(ids)
        for body_id in ids:
            row = body_rows.get(body_id)
            if row is None:
                raise BoundedSensoryScale128Error(
                    "prior body missing from pinned source."
                )
            prior_rows_by_stratum[(row["neuron_type"], row["side"])].append(row)

    from neurofly.bounded_sensory_scale64 import _balanced_quartile_ranks

    selected_rows = []
    rank_summaries = []
    parent_ids = [item["artifact_id"] for item in inputs]
    for neuron_type, side in STRATA:
        prior = prior_rows_by_stratum[(neuron_type, side)]
        candidates = [
            row
            for row in body_rows.values()
            if row["neuron_type"] == neuron_type
            and row["side"] == side
            and row["body_id"] not in used
        ]
        ranks = _balanced_quartile_ranks(candidates)
        selected_here = list(prior)
        for group in range(4):
            group_candidates = [
                row
                for row in candidates
                if ranks[row["body_id"]]["rank_group_zero_based"] == group
            ]
            chosen, distance = _maximin_candidate(group_candidates, selected_here)
            rank = ranks[chosen["body_id"]]
            body = dict(chosen)
            body.update(
                {
                    "selection_rank_group": group + 1,
                    "selection_rank_zero_based": rank["rank_zero_based"],
                    "rank_within_group_zero_based": rank[
                        "rank_within_group_zero_based"
                    ],
                    "rank_group_candidate_count": len(group_candidates),
                    "minimum_hex_centroid_distance_to_prior_samples_and_new_sample": (
                        distance
                    ),
                    "tie_break": "smallest_body_id_among_exact_maximin_ties",
                    "selected_against_sample_artifact_ids": parent_ids,
                    "sentinel": False,
                }
            )
            selected_rows.append(body)
            selected_here.append(body)
            rank_summaries.append(
                {
                    "neuron_type": neuron_type,
                    "side": side,
                    "rank_group": group + 1,
                    "candidate_count": len(group_candidates),
                    "selected_body_id": chosen["body_id"],
                    "structural_edge_count_descriptor": chosen["structural_weight"],
                    "minimum_hex_centroid_distance": distance,
                }
            )
    ids = [row["body_id"] for row in selected_rows]
    if len(ids) != SAMPLE_SIZE or len(set(ids)) != SAMPLE_SIZE or set(ids) & used:
        raise BoundedSensoryScale128Error("new sample is not 16 unique unused bodies.")
    counts = [
        {
            "neuron_type": neuron_type,
            "side": side,
            "count": sum(
                row["neuron_type"] == neuron_type and row["side"] == side
                for row in selected_rows
            ),
        }
        for neuron_type, side in STRATA
    ]
    if [row["count"] for row in counts] != [4] * 4:
        raise BoundedSensoryScale128Error("new sample is not exactly 4×4 stratified.")
    config = {
        "schema": SAMPLE_CONFIG_SCHEMA,
        "artifact_schema": SAMPLE_ARTIFACT_SCHEMA,
        "sample_id": SAMPLE_IDS[label],
        "sample_label": label,
        "sample_size": SAMPLE_SIZE,
        "body_ids": ids,
        "selection_method_id": SELECTION_METHOD_ID,
        "selection_inputs": [
            "body_id",
            "neuron_type",
            "side",
            "structural_DNp01_edge_count_descriptor",
            "unweighted_anatomical_column_centroid",
            "body_column_topology_and_occupancy",
            "source_assignment_fraction",
        ],
        "structural_count_semantics": "DESCRIPTIVE_RANK_PARTITION_ONLY_NOT_EFFICACY",
        "centroid_semantics": "UNWEIGHTED_RELATIVE_COLUMN_ANATOMY_ONLY",
        "exclusion_parent_artifacts": [_reference64(item) for item in inputs],
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "strata": [
            {"neuron_type": neuron_type, "side": side, "count": 4}
            for neuron_type, side in STRATA
        ],
        "algorithm": {
            "candidate_sort": "structural_weight_then_body_id",
            "rank_partition": "balanced_floor_rank_times_4_over_candidate_count",
            "within_group_choice": (
                "maximin_centroid_distance_from_all_prior_and_new_sample"
            ),
            "tie_break": "smallest_body_id",
        },
        "model_outcomes_used": False,
    }
    result = {
        "schema": SAMPLE_RESULT_SCHEMA,
        "sample_id": SAMPLE_IDS[label],
        "sample_label": label,
        "sample_size": SAMPLE_SIZE,
        "body_ids": ids,
        "selected_bodies": selected_rows,
        "stratum_counts": counts,
        "rank_group_summaries": rank_summaries,
        "excluded_prior_sample_ids": parent_ids,
        "prior_overlap_count": 0,
        "selection_semantics": "OUTCOME_BLIND_STRUCTURAL_ANATOMICAL_SAMPLE",
        "model_outcomes_used": False,
        "selection_stage_has_neural_dynamics": False,
    }
    return config, result


def compose_eight_samples(
    samples: Sequence[Any],
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create exactly A–H union, without rerunning any parent selection."""
    if len(samples) != 8:
        raise BoundedSensoryScale128Error("128-body union requires A–H artifacts.")
    inputs = [_as_input(item) for item in samples]
    canonical_ids = [
        CANONICAL_SAMPLE_A_ID,
        "873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33",
        CANONICAL_SAMPLE_C_ID,
        CANONICAL_SAMPLE_D_ID,
    ]
    if [item["artifact_id"] for item in inputs[:4]] != canonical_ids:
        raise BoundedSensoryScale128Error("canonical A–D parent identities changed.")
    if [item.get("config", {}).get("sample_label") for item in inputs[4:]] != list(
        NEW_SAMPLE_LABELS
    ):
        raise BoundedSensoryScale128Error(
            "E–H parent labels are not ordered correctly."
        )
    body_rows, _ = _body_index(source, circuit)
    parent_sets = []
    selected_by_id: dict[int, dict[str, Any]] = {}
    for item in inputs:
        ids = item.get("result", {}).get("body_ids", ())
        selected = item.get("result", {}).get("selected_bodies", ())
        if len(ids) != SAMPLE_SIZE or len(set(ids)) != SAMPLE_SIZE:
            raise BoundedSensoryScale128Error(
                "parent sample must contain 16 unique bodies."
            )
        current = set(ids)
        if any(current & prior for prior in parent_sets):
            raise BoundedSensoryScale128Error("A–H parent samples are not disjoint.")
        if {row.get("body_id") for row in selected} != current:
            raise BoundedSensoryScale128Error(
                "parent selected-body table is malformed."
            )
        parent_sets.append(current)
        for body in selected:
            body_id = body["body_id"]
            expected = body_rows.get(body_id)
            if expected is None or any(
                body.get(key) != expected.get(key)
                for key in (
                    "body_id",
                    "neuron_type",
                    "side",
                    "target_body_id",
                    "structural_weight",
                    "anatomical_column_centroid",
                )
            ):
                raise BoundedSensoryScale128Error(
                    f"body {body_id} differs from pinned sources."
                )
            selected_by_id[body_id] = dict(body)
    ids = sorted(selected_by_id)
    if len(ids) != POPULATION_SIZE:
        raise BoundedSensoryScale128Error("A–H union is not exactly 128 bodies.")
    counts = [
        {
            "neuron_type": neuron_type,
            "side": side,
            "count": sum(
                selected_by_id[body]["neuron_type"] == neuron_type
                and selected_by_id[body]["side"] == side
                for body in ids
            ),
        }
        for neuron_type, side in STRATA
    ]
    if [row["count"] for row in counts] != [32] * 4:
        raise BoundedSensoryScale128Error("union is not exactly 32×4 stratified.")
    target_counts = Counter(selected_by_id[body]["target_body_id"] for body in ids)
    if target_counts != Counter({10001: 64, 10010: 64}):
        raise BoundedSensoryScale128Error("source route target counts changed.")
    pairwise = []
    for left in range(8):
        for right in range(left + 1, 8):
            overlap = parent_sets[left] & parent_sets[right]
            pairwise.append(
                {
                    "sample_left": SAMPLE_LABELS[left],
                    "sample_right": SAMPLE_LABELS[right],
                    "overlap_count": len(overlap),
                    "disjoint": not overlap,
                }
            )
    config = {
        "schema": COMPOSITION_CONFIG_SCHEMA,
        "artifact_schema": COMPOSITION_ARTIFACT_SCHEMA,
        "composition_id": "phase7m_eight_sample_128_body_union_v1",
        "composition_method": COMPOSITION_METHOD_ID,
        "parent_sample_artifacts": [_artifact_reference(item) for item in inputs],
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "body_ids": ids,
        "sample_size": POPULATION_SIZE,
        "expected_strata": [
            {"neuron_type": neuron_type, "side": side, "count": 32}
            for neuron_type, side in STRATA
        ],
        "model_outcomes_used_for_composition": False,
    }
    result = {
        "schema": COMPOSITION_RESULT_SCHEMA,
        "body_ids": ids,
        "sample_size": POPULATION_SIZE,
        "selected_bodies": [selected_by_id[body] for body in ids],
        "stratum_counts": counts,
        "target_route_counts": [
            {"target_body_id": target, "source_count": target_counts[target]}
            for target in TARGET_IDS
        ],
        "parent_artifact_ids": [item["artifact_id"] for item in inputs],
        "parent_sample_body_ids": {
            label: sorted(parent)
            for label, parent in zip(SAMPLE_LABELS, parent_sets, strict=True)
        },
        "pairwise_disjointness": pairwise,
        "pairwise_disjoint": len(pairwise) == 28
        and all(item["disjoint"] for item in pairwise),
        "model_outcomes_used": False,
    }
    return config, result


def make_coverage_plan128(
    composition: Any,
    phase7l_plan: Any,
    phase7l_experiment: Any,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Audit the entire persisted Phase 7L battery, then anatomy-only set cover."""
    comp = _as_input(composition)
    if (
        comp.get("artifact_schema") != COMPOSITION_ARTIFACT_SCHEMA
        or len(comp.get("result", {}).get("body_ids", ())) != POPULATION_SIZE
    ):
        raise BoundedSensoryScale128Error("coverage planner needs the 128-body union.")
    plan64 = _as_input(phase7l_plan)
    if (
        plan64["artifact_id"] != CANONICAL_PLAN64_ID
        or len(plan64["config"].get("stimuli", ())) != 19
    ):
        raise BoundedSensoryScale128Error(
            "the canonical 19-stimulus Phase 7L battery changed."
        )
    if phase7l_experiment.artifact_id != CANONICAL_EXPERIMENT64_ID:
        raise BoundedSensoryScale128Error("Phase 7L experiment identity changed.")
    entries = plan64["config"]["stimuli"]
    stimulus_ids = [item["config"]["stimulus_id"] for item in entries]
    if len(stimulus_ids) != len(set(stimulus_ids)) or any(
        item.get("sha256") != sha256_bytes(canonical_json_bytes(item.get("config", {})))
        for item in entries
    ):
        raise BoundedSensoryScale128Error("Phase 7L stimulus source/hash mismatch.")
    stimuli0 = tuple(
        RelativeColumnStimulus.from_dict(dict(item["config"])) for item in entries
    )
    body_ids = comp["result"]["body_ids"]
    records_by_body, summaries = _source_records128(body_ids, source)
    initial = _coverage_rows(comp["result"], records_by_body, summaries, grid, stimuli0)
    uncovered = [row["body_id"] for row in initial if not row["body_stimulus_covered"]]
    identities = {row["body_id"]: row for row in comp["result"]["selected_bodies"]}
    extensions = []
    searches = []
    for side in ("L", "R"):
        side_uncovered = [
            body for body in uncovered if identities[body]["side"] == side
        ]
        if side_uncovered:
            disks, summary = _coverage_candidates_for_side(
                side, side_uncovered, records_by_body, summaries, grid
            )
            if any(
                not 1 <= row["radius_lattice_steps"] <= MAX_RADIUS_LATTICE_STEPS
                for row in disks
            ):
                raise BoundedSensoryScale128Error(
                    "coverage planner exceeded radius 1–4."
                )
            extensions.extend(disks)
            searches.append(summary)
        else:
            searches.append(
                {
                    "side": side,
                    "source_centre_count": 0,
                    "candidate_disks_evaluated": 0,
                    "nonempty_unique_coverage_masks": 0,
                    "selected_disks": 0,
                }
            )
    extension_entries = []
    extension_rows = []
    for item in extensions:
        h1, h2 = item["centre_hex"]
        stimulus_id = (
            f"coverage128_{item['side'].lower()}_{h1:02d}_{h2:02d}_"
            f"r{item['radius_lattice_steps']}"
        )
        stimulus = RelativeColumnStimulus(
            stimulus_id=stimulus_id,
            side=item["side"],
            centre_hex1=h1,
            centre_hex2=h2,
            dt_ms=0.1,
            radii_lattice_steps=(item["radius_lattice_steps"],),
        )
        if stimulus_id in stimulus_ids:
            raise BoundedSensoryScale128Error(
                "coverage extension duplicates a stimulus identity."
            )
        config = stimulus.to_dict()
        extension_entries.append(
            {
                "origin": "PHASE7M_ANATOMY_ONLY_COVERAGE_EXTENSION",
                "config": config,
                "sha256": sha256_bytes(canonical_json_bytes(config)),
            }
        )
        extension_rows.append(
            {
                **item,
                "stimulus_id": stimulus_id,
                "centre_is_source_column": True,
                "coverage_basis": "column_overlap_fraction_gt_zero",
                "model_outcomes_used": False,
            }
        )
    all_entries = [
        {
            "origin": "PHASE7L_RETAINED_UNCHANGED",
            "config": dict(item["config"]),
            "sha256": item["sha256"],
        }
        for item in entries
    ] + extension_entries
    all_stimuli = tuple(
        RelativeColumnStimulus.from_dict(item["config"]) for item in all_entries
    )
    final = _coverage_rows(
        comp["result"], records_by_body, summaries, grid, all_stimuli
    )
    if not all(row["body_stimulus_covered"] for row in final):
        raise BoundedSensoryScale128Error(
            "radius 1–4 anatomy-only coverage failed for the 128 union."
        )
    extension_covered = {
        body for item in extension_rows for body in item["covered_body_ids"]
    }
    if extension_covered != set(uncovered):
        raise BoundedSensoryScale128Error(
            "coverage disks do not exactly cover initial misses."
        )
    config = {
        "schema": PLAN_CONFIG_SCHEMA,
        "artifact_schema": PLAN_ARTIFACT_SCHEMA,
        "plan_method_id": COVERAGE_METHOD_ID,
        "composition_artifact": _artifact_reference(comp),
        "phase7l_plan_artifact": _artifact_reference(plan64),
        "phase7l_experiment_artifact": _artifact_reference(phase7l_experiment),
        "source_contract_identity": dict(source.source_identity),
        "column_grid_identity": grid.to_identity_dict(),
        "body_ids": list(body_ids),
        "coverage_metric": "column_overlap_fraction_gt_zero",
        "candidate_centres": "uncovered_bodies_actual_source_columns_only",
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
        "initial_stimulus_ids": stimulus_ids,
        "initial_coverage": initial,
        "initial_uncovered_body_ids": uncovered,
        "candidate_search_summary": searches,
        "coverage_extension_stimuli": extension_rows,
        "final_coverage": final,
        "final_covered_body_ids": [
            row["body_id"] for row in final if row["body_stimulus_covered"]
        ],
        "model_outcomes_used": False,
        "dn_p01_outputs_read_for_design": False,
        "neural_dynamics_computed": False,
        "purpose": "SOFTWARE_PATH_COVERAGE",
        "maximum_added_radius_lattice_steps": MAX_RADIUS_LATTICE_STEPS,
    }
    return config, result


def _source_records128(body_ids: Sequence[int], source: RelativeColumnAssignmentSource):
    selected = set(body_ids)
    records = {body: [] for body in body_ids}
    for record in source.contract.records:
        if record.body_id in selected:
            records[record.body_id].append(record)
    summaries = {
        row.body_id: row for row in source.contract.summaries if row.body_id in selected
    }
    if set(summaries) != selected or any(not records[body] for body in selected):
        raise BoundedSensoryScale128Error(
            "selected body source columns are incomplete."
        )
    return {body: tuple(sorted(rows)) for body, rows in records.items()}, summaries


def _assert_additivity128(
    conditions: Sequence[Mapping[str, Any]], body_parent: Mapping[int, str]
) -> int:
    comparisons = 0
    for condition in conditions:
        targets = {row["body_id"]: row for row in condition["targets"]}
        for interval in condition["source_contributions_by_interval"]:
            by_parent = {
                label: {target: 0.0 for target in TARGET_IDS} for label in SAMPLE_LABELS
            }
            for row in interval["contributions"]:
                by_parent[body_parent[row["source_body_id"]]][
                    row["target_body_id"]
                ] += row["model_drive_mveq"]
            for target in TARGET_IDS:
                total = sum(by_parent[label][target] for label in SAMPLE_LABELS)
                stored = targets[target]["drive_mveq_by_interval"][interval["step"]]
                if not math.isclose(total, stored, rel_tol=0.0, abs_tol=1e-15):
                    raise BoundedSensoryScale128Error("A–H per-step additivity failed.")
                comparisons += 1
    return comparisons


def compute_population128_experiment(
    composition: Any,
    coverage_plan: Any,
    phase7l_plan: Any,
    phase7l_experiment: Any,
    context: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the fixed 128-body union using the existing sensory/transfer/LIF code."""
    comp = _as_input(composition)
    plan = _as_input(coverage_plan)
    expected_plan = make_coverage_plan128(
        comp, phase7l_plan, phase7l_experiment, context["source"], context["grid"]
    )
    if (
        plan.get("artifact_schema") != PLAN_ARTIFACT_SCHEMA
        or (plan.get("config"), plan.get("result")) != expected_plan
    ):
        raise BoundedSensoryScale128Error(
            "persisted 128-body coverage plan failed replay."
        )
    if (
        comp.get("artifact_schema") != COMPOSITION_ARTIFACT_SCHEMA
        or len(comp["result"].get("body_ids", ())) != POPULATION_SIZE
    ):
        raise BoundedSensoryScale128Error("invalid 128-body composition artifact.")
    selected = comp["result"]
    stimuli = tuple(
        RelativeColumnStimulus.from_dict(item["config"])
        for item in plan["config"]["stimuli"]
    )
    assignment = _assignment_result(
        selected, context["source"], context["grid"], stimuli
    )
    trajectories = _sensory_trajectories(assignment, selected)
    body_rows = {row["body_id"]: row for row in selected["selected_bodies"]}
    source_rows, _ = _body_index(context["source"], context["circuit"])
    routes = []
    for body in selected["body_ids"]:
        row = body_rows[body]
        pinned = source_rows[body]
        if any(
            row[key] != pinned[key]
            for key in ("neuron_type", "side", "target_body_id", "structural_weight")
        ):
            raise BoundedSensoryScale128Error(
                f"route/source identity differs for {body}."
            )
        routes.append(
            Route(
                body,
                row["target_body_id"],
                row["structural_weight"],
                row["neuron_type"],
                row["side"],
            )
        )
    routes = tuple(sorted(routes, key=lambda row: row.source_body_id))
    target_counts = Counter(row.target_body_id for row in routes)
    if (
        len(routes) != POPULATION_SIZE
        or len({row.source_body_id for row in routes}) != POPULATION_SIZE
        or target_counts != Counter({10001: 64, 10010: 64})
    ):
        raise BoundedSensoryScale128Error(
            "128-body route topology is incomplete or changed."
        )

    base_config = context["experiment64"].config
    sensory = base_config["sensory_model"]
    transfer = base_config["transfer_model"]
    dnp01 = base_config["dnp01_model"]
    if (
        sensory
        != {
            "model_id": SOURCE_MODEL_ID,
            "tau_sens_ms": 1.0,
            "gain": 1.0,
            "initial_state": 0.0,
            "input_metric_id": "column_overlap_fraction",
            **{
                key: value
                for key, value in sensory.items()
                if key
                not in {
                    "model_id",
                    "tau_sens_ms",
                    "gain",
                    "initial_state",
                    "input_metric_id",
                }
            },
        }
        or transfer.get("model_id") != TRANSFER_MODEL_ID
        or transfer.get("k_transfer_mveq_per_state") != REFERENCE_K
        or transfer.get("structural_weight_used_as_gain") is not False
    ):
        raise BoundedSensoryScale128Error(
            "Phase 7E/F reference model assumptions changed."
        )
    if dnp01 != context["experiment64"].config["dnp01_model"]:
        raise BoundedSensoryScale128Error("DNp01 model configuration changed.")

    # Parent state traces are checked exactly before simultaneous integration.
    nested_state_checks = {label: 0 for label in "ABCD"}
    for label, previous in zip("ABCD", (context["experiment64"],) * 4, strict=True):
        old_traces = previous.result["sensory_trajectories_by_stimulus"]
        parent_ids = set(selected["parent_sample_body_ids"][label])
        for stimulus_id, old_rows in old_traces.items():
            now = {row["body_id"]: row for row in trajectories[stimulus_id]}
            old = {row["body_id"]: row for row in old_rows}
            for body in parent_ids:
                if now[body] != old[body]:
                    raise BoundedSensoryScale128Error(
                        f"parent {label} trajectory changed for {body}."
                    )
                nested_state_checks[label] += 1

    standalone_state_checks = {label: 0 for label in "EFGH"}
    for label in "EFGH":
        member_ids = set(selected["parent_sample_body_ids"][label])
        subset_result = {
            **selected,
            "body_ids": sorted(member_ids),
            "selected_bodies": [body_rows[body] for body in sorted(member_ids)],
        }
        subset_assignment = {
            **assignment,
            "body_ids": sorted(member_ids),
            "samples": [
                {
                    **sample,
                    "assignments": [
                        row
                        for row in sample["assignments"]
                        if row["body_id"] in member_ids
                    ],
                }
                for sample in assignment["samples"]
            ],
        }
        standalone = _sensory_trajectories(subset_assignment, subset_result)
        for stimulus_id, full_rows in trajectories.items():
            full_by_body = {row["body_id"]: row for row in full_rows}
            standalone_by_body = {
                row["body_id"]: row for row in standalone[stimulus_id]
            }
            for body in member_ids:
                if full_by_body[body] != standalone_by_body[body]:
                    raise BoundedSensoryScale128Error(
                        f"Sample {label} standalone state differs for {body}."
                    )
                standalone_state_checks[label] += 1

    parent_sets = {
        label: set(ids) for label, ids in selected["parent_sample_body_ids"].items()
    }
    abcd_ids = set().union(*(parent_sets[label] for label in "ABCD"))
    efgh_ids = set().union(*(parent_sets[label] for label in "EFGH"))
    all_ids = set(selected["body_ids"])
    conditions = []
    full_by_stimulus = {}
    abcd_by_stimulus = {}
    for stimulus in stimuli:
        states = {
            row["body_id"]: [sample["state_value"] for sample in row["state_timeline"]]
            for row in trajectories[stimulus.stimulus_id]
        }
        steps = len(next(iter(states.values()))) - 1
        full = _simulate_condition(
            condition_id=f"stimulus::{stimulus.stimulus_id}",
            pathway_mask="all128",
            active_body_ids=all_ids,
            k=REFERENCE_K,
            states=states,
            dt_ms=stimulus.dt_ms,
            steps=steps,
            routes=routes,
            circuit=context["circuit"],
        )
        abcd = _simulate_condition(
            condition_id=f"sample_abcd_stimulus::{stimulus.stimulus_id}",
            pathway_mask="sample_abcd",
            active_body_ids=abcd_ids,
            k=REFERENCE_K,
            states=states,
            dt_ms=stimulus.dt_ms,
            steps=steps,
            routes=routes,
            circuit=context["circuit"],
        )
        _add_source_annotations(full, states, body_rows)
        _add_source_annotations(abcd, states, body_rows)
        conditions.extend((full, abcd))
        full_by_stimulus[stimulus.stimulus_id] = full
        abcd_by_stimulus[stimulus.stimulus_id] = abcd

    reference_states, reference_dt, reference_steps = _condition_states(
        trajectories, selected, "left_expand_33_29", "right_expand_23_09"
    )
    masks = (
        ("k_zero", "all128", all_ids, 0.0),
        ("no_sources", "none", set(), REFERENCE_K),
        (
            "lc4_only",
            "LC4",
            {body for body in all_ids if body_rows[body]["neuron_type"] == "LC4"},
            REFERENCE_K,
        ),
        (
            "lplc2_only",
            "LPLC2",
            {body for body in all_ids if body_rows[body]["neuron_type"] == "LPLC2"},
            REFERENCE_K,
        ),
        (
            "left_only",
            "left",
            {body for body in all_ids if body_rows[body]["side"] == "L"},
            REFERENCE_K,
        ),
        (
            "right_only",
            "right",
            {body for body in all_ids if body_rows[body]["side"] == "R"},
            REFERENCE_K,
        ),
        ("sample_abcd_only", "sample_abcd", abcd_ids, REFERENCE_K),
        ("sample_efgh_only", "sample_efgh", efgh_ids, REFERENCE_K),
        ("all128_reference", "all128", all_ids, REFERENCE_K),
        ("sensitivity_k_2", "all128", all_ids, 2.0),
    )
    for condition_id, mask, active, coefficient in masks:
        row = _simulate_condition(
            condition_id=condition_id,
            pathway_mask=mask,
            active_body_ids=set(active),
            k=coefficient,
            states=reference_states,
            dt_ms=reference_dt,
            steps=reference_steps,
            routes=routes,
            circuit=context["circuit"],
        )
        _add_source_annotations(row, reference_states, body_rows)
        conditions.append(row)

    accounting = _assert_accounting64(conditions)
    body_parent = {
        body: label for label, members in parent_sets.items() for body in members
    }
    additivity = _assert_additivity128(conditions, body_parent)
    nested64 = []
    old_conditions = {
        row["condition_id"]: row for row in context["experiment64"].result["conditions"]
    }
    phase7l_stimulus_ids = {
        item["config"]["stimulus_id"] for item in context["plan64"].config["stimuli"]
    }
    for stimulus_id, current in abcd_by_stimulus.items():
        previous = old_conditions.get(f"stimulus::{stimulus_id}")
        if previous is None:
            if stimulus_id in phase7l_stimulus_ids:
                raise BoundedSensoryScale128Error(
                    "Phase 7L stimulus condition is missing."
                )
            continue
        for target in TARGET_IDS:
            now_t = next(row for row in current["targets"] if row["body_id"] == target)
            old_t = next(row for row in previous["targets"] if row["body_id"] == target)
            if not _target_fields_equal(now_t, old_t):
                raise BoundedSensoryScale128Error(
                    f"A–D-only DNp01 result changed for {stimulus_id}."
                )
        for interval_now, interval_old in zip(
            current["source_contributions_by_interval"],
            previous["source_contributions_by_interval"],
            strict=True,
        ):
            now_rows = {
                row["source_body_id"]: row
                for row in interval_now["contributions"]
                if row["source_body_id"] in abcd_ids
            }
            old_rows = {
                row["source_body_id"]: row for row in interval_old["contributions"]
            }
            if now_rows != old_rows:
                raise BoundedSensoryScale128Error(
                    f"A–D contribution ledger changed for {stimulus_id}."
                )
        nested64.append(
            {
                "stimulus_id": stimulus_id,
                "per_source_contributions_identical": True,
                "dn_p01_drive_membrane_events_identical": True,
            }
        )
    current_abcd = next(
        row for row in conditions if row["condition_id"] == "sample_abcd_only"
    )
    old_reference = next(
        row
        for row in context["experiment64"].result["conditions"]
        if row["condition_id"] == "all64_reference"
    )
    if any(
        not _target_fields_equal(
            next(row for row in current_abcd["targets"] if row["body_id"] == target),
            next(row for row in old_reference["targets"] if row["body_id"] == target),
        )
        for target in TARGET_IDS
    ):
        raise BoundedSensoryScale128Error(
            "A–D combined reference differs from Phase 7L."
        )

    coverage_rows = _coverage_path_rows(
        selected,
        assignment,
        trajectories,
        [full_by_stimulus[s.stimulus_id] for s in stimuli],
    )
    if len(coverage_rows) != POPULATION_SIZE or any(
        not row["body_stimulus_covered"]
        or not row["body_state_exercised"]
        or not row["body_transfer_exercised"]
        for row in coverage_rows
    ):
        raise BoundedSensoryScale128Error("128/128 non-zero path coverage failed.")
    side_checks = 0
    assignment_by_key = {
        (sample["stimulus_id"], row["body_id"]): row
        for sample in assignment["samples"]
        for row in sample["assignments"]
    }
    for stimulus in stimuli:
        condition = full_by_stimulus[stimulus.stimulus_id]
        for body in selected["selected_bodies"]:
            if body["side"] == stimulus.side:
                continue
            if (
                assignment_by_key[(stimulus.stimulus_id, body["body_id"])][
                    "column_overlap_fraction"
                ]
                != 0.0
            ):
                raise BoundedSensoryScale128Error(
                    "unilateral anatomical input crossed sides."
                )
            for interval in condition["source_contributions_by_interval"]:
                contribution = next(
                    row
                    for row in interval["contributions"]
                    if row["source_body_id"] == body["body_id"]
                )
                if (
                    contribution["sensory_state"] != 0.0
                    or contribution["model_drive_mveq"] != 0.0
                ):
                    raise BoundedSensoryScale128Error(
                        "unilateral sensory transfer crossed sides."
                    )
                side_checks += 1

    config = {
        "schema": EXPERIMENT_CONFIG_SCHEMA,
        "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "composition_artifact": _artifact_reference(comp),
        "coverage_plan_artifact": _artifact_reference(plan),
        "phase7l_experiment_artifact_id": context["experiment64"].artifact_id,
        "source_contract_identity": dict(context["source"].source_identity),
        "circuit_contract_identity": _circuit_identity(context["circuit"]),
        "column_grid_identity": context["grid"].to_identity_dict(),
        "parent_sample_artifacts": comp["config"]["parent_sample_artifacts"],
        "body_ids": list(selected["body_ids"]),
        "body_count": POPULATION_SIZE,
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimuli": plan["config"]["stimuli"],
        "sensory_model": sensory,
        "transfer_model": transfer,
        "dnp01_model": dnp01,
        "route_contract": [row.to_dict() for row in routes],
        "sample_masks": {
            label: sorted(members) for label, members in parent_sets.items()
        },
        "pathway_controls": [row[0] for row in masks],
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
            item
            for condition in conditions
            for item in condition["targets"]
            if item["body_id"] == target
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
        "body_ids": list(selected["body_ids"]),
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
            "denominator": POPULATION_SIZE,
        },
        "conditions": conditions,
        "condition_count": len(conditions),
        "per_step_source_accounting_comparisons": accounting,
        "per_step_A_H_additivity_comparisons": additivity,
        "nested_parent_state_comparisons": nested_state_checks,
        "standalone_E_H_state_comparisons": standalone_state_checks,
        "phase7l_A_D_only_nested_regression": nested64,
        "side_isolation_checks": side_checks,
        "target_summary": target_summary,
        "source_bodies_by_stratum": {
            f"{neuron_type}_{side}": [
                body
                for body in selected["body_ids"]
                if body_rows[body]["neuron_type"] == neuron_type
                and body_rows[body]["side"] == side
            ]
            for neuron_type, side in STRATA
        },
        "source_bodies_by_parent_sample": {
            label: sorted(members) for label, members in parent_sets.items()
        },
        "source_contribution_accounting_validated": True,
        "parent_additivity_validated": True,
        "comparison_semantics": (
            "COMPOSITIONAL_ARCHITECTURE_ONLY_NOT_BIOLOGICAL_REPLICATION"
        ),
        "result_semantics": (
            "SIMULTANEOUS_128_BODY_EXPLORATORY_SENSORY_TO_DNP01_EXPERIMENT"
        ),
    }
    return config, result
