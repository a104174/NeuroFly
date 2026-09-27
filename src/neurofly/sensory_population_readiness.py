"""Phase 7N: arbitrary-N sensory population planning without dynamics.

The full target population is read directly from the pinned MaleCNS
CircuitContract and body_column_input_v1 source. This module validates and
persists identity, anatomy-only coverage, and a future execution dry-run; it
does not integrate sensory state or run DNp01.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.bounded_sensory_coverage import (
    MAX_RADIUS_LATTICE_STEPS,
    _coverage_candidates_for_side,
)
from neurofly.bounded_sensory_population import _body_index
from neurofly.bounded_sensory_scale128 import (
    CANONICAL_PLAN128_ID,
)
from neurofly.malecns.contract import CircuitContract, load_circuit_contract
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    RelativeColumnAssignmentSource,
    RelativeColumnGrid,
    RelativeColumnStimulus,
    active_column_set,
    canonical_json_bytes,
    load_relative_column_grid,
    load_relative_column_source,
    sha256_bytes,
)

POPULATION_SIZE = 311
TYPE_COUNTS = {"LC4": 126, "LPLC2": 185}
TYPE_SIDE_COUNTS = {
    ("LC4", "L"): 71,
    ("LC4", "R"): 55,
    ("LPLC2", "L"): 94,
    ("LPLC2", "R"): 91,
}
TARGET_IDS = (10001, 10010)
PHASE7M_PLAN_ROOT_ID = CANONICAL_PLAN128_ID
PHASE7M_EXPERIMENT_ID = (
    "3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6"
)
PHASE7M_BATTERY_SHA256 = (
    "93cf3de37b21906535fbb61c2e6012f2da6909637bf026fe594a729e8b967fb4"
)
PHASE7M_EXPERIMENT_CONFIG_SHA256 = (
    "ffdd914eb703aef94820632dbf3129c430519ca1e29b10e31e28269f2151e82a"
)
SENSORY_MODEL_ID = "relative_column_exploratory_sensory_state_v1"
TRANSFER_MODEL_ID = "exploratory_edge_routed_model_drive_v1"
REFERENCE_K_MVEQ_PER_STATE = 1.0
RECOVERY_TAIL_STEPS = 10

_REFERENCE_SENSORY_MODEL = {
    "classification": "MODEL_ASSUMPTION",
    "gain": 1.0,
    "initial_state": 0.0,
    "input_metric_id": "column_overlap_fraction",
    "integration_scheme": "exact_exponential_zero_order_hold_v1",
    "model_id": SENSORY_MODEL_ID,
    "model_version": 1,
    "recovery_tail_steps": RECOVERY_TAIL_STEPS,
    "tau_sens_ms": 1.0,
}
_REFERENCE_TRANSFER_MODEL = {
    "classification": "MODEL_ASSUMPTION",
    "equation": "d_i[n]=k_transfer*x_i[n]; target=sum_routed_source_contributions",
    "k_transfer_mveq_per_state": REFERENCE_K_MVEQ_PER_STATE,
    "model_id": TRANSFER_MODEL_ID,
    "source_normalization": "none",
    "structural_weight_used_as_gain": False,
}
_REFERENCE_DNP01_MODEL = {
    "config": {
        "baseline_policy": "zero",
        "delay_ms": 1.8,
        "delay_steps": 18,
        "dt_ms": 0.1,
        "external_drive_semantics": "voltage_equivalent_mV_eq_v1",
        "graph_scope_id": "phase7f_two_dnp01_readouts_v1",
        "input_drive_provenance_id": "phase7f_edge_routed_exploratory_model_drive_v1",
        "k_syn_mv_per_contact": 0.01,
        "model_id": "lif_filtered_synapse",
        "model_version": "phase2b_v1",
        "refractory_ms": 2.2,
        "refractory_steps": 22,
        "reset_mv": -52.0,
        "rest_mv": -52.0,
        "sign_policy_id": "direct_visual_dnp01_depolarizing_assumption_v1",
        "stochastic_policy": "deterministic",
        "tau_m_ms": 20.0,
        "tau_s_ms": 5.0,
        "threshold_mv": -45.0,
    },
    "configuration_source": "unchanged Phase 7F reference readout model",
    "model_id": "lif_filtered_synapse",
}

POPULATION_CONFIG_SCHEMA = "full_sensory_population_plan_config_v1"
POPULATION_RESULT_SCHEMA = "full_sensory_population_plan_result_v1"
POPULATION_ARTIFACT_SCHEMA = "full_sensory_population_plan_artifact_v1"
COVERAGE_CONFIG_SCHEMA = "full_sensory_population_coverage_config_v1"
COVERAGE_RESULT_SCHEMA = "full_sensory_population_coverage_result_v1"
COVERAGE_ARTIFACT_SCHEMA = "full_sensory_population_coverage_artifact_v1"
EXECUTION_CONFIG_SCHEMA = "sensory_population_execution_config_v1"
EXECUTION_RESULT_SCHEMA = "sensory_population_execution_manifest_v1"
EXECUTION_ARTIFACT_SCHEMA = "sensory_population_execution_dry_run_artifact_v1"

DEFAULT_POPULATION_ROOT = DEFAULT_SOURCE_ROOT / "full_sensory_population_plan_v1"
DEFAULT_COVERAGE_ROOT = DEFAULT_SOURCE_ROOT / "full_sensory_coverage_plan_v1"
DEFAULT_EXECUTION_ROOT = DEFAULT_SOURCE_ROOT / "sensory_population_execution_311_v1"

_ARTIFACTS = {
    "population": (
        POPULATION_ARTIFACT_SCHEMA,
        POPULATION_CONFIG_SCHEMA,
        POPULATION_RESULT_SCHEMA,
        "population_config.json",
        "population_result.json",
        DEFAULT_POPULATION_ROOT,
    ),
    "coverage": (
        COVERAGE_ARTIFACT_SCHEMA,
        COVERAGE_CONFIG_SCHEMA,
        COVERAGE_RESULT_SCHEMA,
        "coverage_config.json",
        "coverage_result.json",
        DEFAULT_COVERAGE_ROOT,
    ),
    "execution": (
        EXECUTION_ARTIFACT_SCHEMA,
        EXECUTION_CONFIG_SCHEMA,
        EXECUTION_RESULT_SCHEMA,
        "execution_config.json",
        "execution_manifest.json",
        DEFAULT_EXECUTION_ROOT,
    ),
}
_MANIFEST_FILENAME = "manifest.json"


class SensoryPopulationReadinessError(ValueError):
    """A full-population dry-run input, plan, or artifact is invalid."""


@dataclass(frozen=True, slots=True)
class LoadedReadinessArtifact:
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
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "manifest_sha256": sha256_bytes(
                canonical_json_bytes(self.manifest) + b"\n"
            ),
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
            "stimulus_count": self.result.get("stimulus_count"),
            "covered_body_count": self.result.get("covered_body_count"),
            "expected_ledger_rows": self.result.get(
                "expected_contribution_ledger_rows"
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "artifact_bytes_including_manifest": sum(
                child.stat().st_size for child in self.path.iterdir()
            ),
        }


def _sha256_json(value: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(value)) + b"\n")


def _circuit_identity(circuit: CircuitContract) -> dict[str, Any]:
    return {
        "dataset": circuit.provenance.dataset,
        "candidate_id": circuit.candidate.identifier,
        "candidate_version": circuit.candidate.version,
        "file_sha256": dict(circuit.integrity.sha256_by_file),
    }


def _artifact_ref(artifact: Any) -> dict[str, Any]:
    value = artifact.as_input() if hasattr(artifact, "as_input") else dict(artifact)
    return {
        "artifact_schema": value["artifact_schema"],
        "artifact_id": value["artifact_id"],
        "config_sha256": value["config_sha256"],
        "result_sha256": value["result_sha256"],
        "manifest_sha256": value["manifest_sha256"],
    }


def build_full_population_plan(
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
    grid: RelativeColumnGrid,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build source-only identities and descriptors for all authorized bodies."""
    body_rows, records_by_body = _body_index(source, circuit)
    body_ids = sorted(body_rows)
    sensory_nodes = {
        node.body_id: node for node in circuit.neurons if node.type in {"LC4", "LPLC2"}
    }
    if (
        len(body_ids) != POPULATION_SIZE
        or len(set(body_ids)) != POPULATION_SIZE
        or set(body_ids) != set(sensory_nodes)
    ):
        raise SensoryPopulationReadinessError(
            "CircuitContract does not define the complete unique 311-body population."
        )

    selected_rows = []
    summary_by_body = {item.body_id: item for item in source.contract.summaries}
    for body_id in body_ids:
        row = body_rows[body_id]
        records = records_by_body[body_id]
        summary = summary_by_body[body_id]
        coordinate_keys = sorted({(item.ol_hex1, item.ol_hex2) for item in records})
        if not coordinate_keys or any(
            (item.ol_hex1, item.ol_hex2) not in grid.columns_by_side[row["side"]]
            for item in records
        ):
            raise SensoryPopulationReadinessError(
                f"body {body_id} has missing or invalid relative-column coordinates."
            )
        unclassified = [
            list(key)
            for key in coordinate_keys
            if key not in grid.official_classes_by_side[row["side"]]
        ]
        selected_rows.append(
            {
                "body_id": body_id,
                "neuron_type": row["neuron_type"],
                "side": row["side"],
                "target_body_id": row["target_body_id"],
                "structural_edge_count": row["structural_weight"],
                "structural_edge_count_semantics": (
                    "SOURCE_STRUCTURAL_COUNT_METADATA_ONLY"
                ),
                "body_column_record_count": len(records),
                "unique_source_column_count": len(coordinate_keys),
                "valid_relative_hex_coordinate_count": len(coordinate_keys),
                "unclassified_source_column_coordinates": unclassified,
                "assigned_input_site_count": summary.assigned_input_count,
                "relevant_input_site_count": summary.relevant_input_count,
                "unassigned_input_site_count": summary.unassigned_input_count,
                "assigned_site_fraction": summary.assignment_fraction,
                "body_column_source_available": True,
                "dynamic_state_present": False,
                "model_outcome_present": False,
            }
        )

    type_counts = Counter(row["neuron_type"] for row in selected_rows)
    type_side_counts = Counter(
        (row["neuron_type"], row["side"]) for row in selected_rows
    )
    target_counts = Counter(row["target_body_id"] for row in selected_rows)
    if (
        type_counts != Counter(TYPE_COUNTS)
        or type_side_counts != Counter(TYPE_SIDE_COUNTS)
        or set(target_counts) != set(TARGET_IDS)
        or sum(target_counts.values()) != POPULATION_SIZE
    ):
        raise SensoryPopulationReadinessError(
            "full-population type, side, or source-derived target counts changed."
        )

    source_only_coordinates = {
        side: [
            list(coordinate)
            for coordinate in sorted(
                grid.columns_by_side[side] - set(grid.official_classes_by_side[side])
            )
        ]
        for side in ("L", "R")
    }
    all_unclassified_bodies = [
        row["body_id"]
        for row in selected_rows
        if row["unclassified_source_column_coordinates"]
    ]
    config = {
        "schema": POPULATION_CONFIG_SCHEMA,
        "artifact_schema": POPULATION_ARTIFACT_SCHEMA,
        "population_id": "malecns_looming_giant_fiber_all_sensory_bodies_v1",
        "population_semantics": "COMPLETE_TARGET_POPULATION",
        "dataset": source.contract.dataset,
        "dataset_version": source.contract.candidate_version,
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "column_grid_identity": grid.to_identity_dict(),
        "body_ids": body_ids,
        "type_counts": dict(sorted(type_counts.items())),
        "type_side_counts": [
            {
                "neuron_type": neuron_type,
                "side": side,
                "count": type_side_counts[(neuron_type, side)],
            }
            for neuron_type, side in sorted(TYPE_SIDE_COUNTS)
        ],
        "route_target_counts": [
            {"target_body_id": target, "source_count": target_counts[target]}
            for target in sorted(target_counts)
        ],
        "identity_source": "CircuitContract_sensor_neuron_records_only",
        "body_column_validation": (
            "exact_body_id_type_side_match_to_body_column_input_v1"
        ),
        "structural_edge_count_use": "SOURCE_METADATA_ONLY",
        "model_outcomes_used": False,
    }
    result = {
        "schema": POPULATION_RESULT_SCHEMA,
        "population_id": config["population_id"],
        "population_semantics": "COMPLETE_TARGET_POPULATION",
        "body_count": POPULATION_SIZE,
        "body_ids": body_ids,
        "bodies": selected_rows,
        "type_counts": dict(sorted(type_counts.items())),
        "type_side_counts": config["type_side_counts"],
        "route_target_counts": config["route_target_counts"],
        "source_body_column_record_count": sum(
            len(value) for value in records_by_body.values()
        ),
        "assigned_input_site_count": sum(
            row["assigned_input_site_count"] for row in selected_rows
        ),
        "unassigned_input_site_count": sum(
            row["unassigned_input_site_count"] for row in selected_rows
        ),
        "all_bodies_have_column_topology": True,
        "all_source_coordinates_are_valid_relative_hex": True,
        "official_grid_unclassified_source_coordinates": source_only_coordinates,
        "bodies_using_unclassified_coordinates": all_unclassified_bodies,
        "dynamic_state_present": False,
        "model_outcome_present": False,
    }
    return config, result


def _binary_coverage_rows(
    body_rows: list[dict[str, Any]],
    records_by_body: Mapping[int, tuple[Any, ...]],
    stimuli: list[RelativeColumnStimulus],
    grid: RelativeColumnGrid,
) -> list[dict[str, Any]]:
    covered_by: dict[int, list[str]] = {row["body_id"]: [] for row in body_rows}
    for stimulus in stimuli:
        active_columns = set().union(
            *(
                active_column_set(stimulus, grid, radius)
                for radius in stimulus.radii_lattice_steps
            )
        )
        for row in body_rows:
            if row["side"] != stimulus.side:
                continue
            if any(
                (record.ol_hex1, record.ol_hex2) in active_columns
                for record in records_by_body[row["body_id"]]
            ):
                covered_by[row["body_id"]].append(stimulus.stimulus_id)
    return [
        {
            "body_id": row["body_id"],
            "neuron_type": row["neuron_type"],
            "side": row["side"],
            "stimulus_ids_with_positive_column_overlap": covered_by[row["body_id"]],
            "body_stimulus_covered": bool(covered_by[row["body_id"]]),
        }
        for row in body_rows
    ]


def build_full_coverage_plan(
    population_artifact: Any,
    phase7m_plan: Any,
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
    grid: RelativeColumnGrid,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Plan complete 311-body stimulus exposure using source anatomy only."""
    population = (
        population_artifact.as_input()
        if hasattr(population_artifact, "as_input")
        else dict(population_artifact)
    )
    plan128 = (
        phase7m_plan.as_input()
        if hasattr(phase7m_plan, "as_input")
        else dict(phase7m_plan)
    )
    _validate_full_population_input(population, source, circuit, grid)
    if (
        plan128.get("artifact_schema") != "bounded_sensory_coverage128_plan_artifact_v1"
        or plan128.get("artifact_id") != PHASE7M_PLAN_ROOT_ID
        or plan128.get("config", {}).get("neural_dynamics_computed") is not False
    ):
        raise SensoryPopulationReadinessError(
            "the persisted Phase 7M stimulus battery identity changed."
        )
    base_entries = _validated_phase7m_battery(plan128["config"].get("stimuli", ()))
    return _build_full_coverage_plan_from_entries(
        population,
        base_entries,
        plan128["artifact_id"],
        source,
        circuit,
        grid,
    )


def replay_full_coverage_plan(
    population_artifact: Any,
    coverage_artifact: Any,
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
    grid: RelativeColumnGrid,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay a persisted 7N plan from its pinned battery, without sample ancestry."""
    population = (
        population_artifact.as_input()
        if hasattr(population_artifact, "as_input")
        else dict(population_artifact)
    )
    coverage = (
        coverage_artifact.as_input()
        if hasattr(coverage_artifact, "as_input")
        else dict(coverage_artifact)
    )
    _validate_full_population_input(population, source, circuit, grid)
    if (
        coverage.get("artifact_schema") != COVERAGE_ARTIFACT_SCHEMA
        or coverage.get("config", {}).get("inherited_stimulus_battery_id")
        != PHASE7M_PLAN_ROOT_ID
    ):
        raise SensoryPopulationReadinessError(
            "coverage artifact does not reference the pinned Phase 7M battery."
        )
    entries = coverage.get("config", {}).get("stimuli", ())
    if len(entries) < 23 or any(
        entry.get("origin") != "PHASE7M_BATTERY_CONFIG_RETAINED"
        for entry in entries[:23]
    ):
        raise SensoryPopulationReadinessError(
            "persisted coverage plan has an invalid inherited stimulus battery."
        )
    base_entries = _validated_phase7m_battery(
        [
            {"config": entry.get("config"), "sha256": entry.get("sha256")}
            for entry in entries[:23]
        ]
    )
    return _build_full_coverage_plan_from_entries(
        population,
        base_entries,
        PHASE7M_PLAN_ROOT_ID,
        source,
        circuit,
        grid,
    )


def _validate_full_population_input(
    population: dict[str, Any],
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
    grid: RelativeColumnGrid,
) -> None:
    expected_population = build_full_population_plan(source, circuit, grid)
    if (
        population.get("artifact_schema") != POPULATION_ARTIFACT_SCHEMA
        or (population.get("config"), population.get("result")) != expected_population
    ):
        raise SensoryPopulationReadinessError(
            "full-population source artifact failed direct source replay."
        )


def _validated_phase7m_battery(entries: Any) -> list[dict[str, Any]]:
    base_entries = [
        {"config": entry.get("config"), "sha256": entry.get("sha256")}
        for entry in entries
    ]
    base_ids = [entry.get("config", {}).get("stimulus_id") for entry in base_entries]
    if (
        len(base_entries) != 23
        or len(set(base_ids)) != len(base_ids)
        or any(
            entry.get("sha256")
            != sha256_bytes(canonical_json_bytes(entry.get("config", {})))
            for entry in base_entries
        )
        or sha256_bytes(canonical_json_bytes(base_entries)) != PHASE7M_BATTERY_SHA256
    ):
        raise SensoryPopulationReadinessError(
            "the complete Phase 7M 23-stimulus battery is malformed or changed."
        )
    return base_entries


def _build_full_coverage_plan_from_entries(
    population: dict[str, Any],
    base_entries: list[dict[str, Any]],
    inherited_battery_id: str,
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
    grid: RelativeColumnGrid,
) -> tuple[dict[str, Any], dict[str, Any]]:

    body_rows = population["result"]["bodies"]
    summaries = {row.body_id: row for row in source.contract.summaries}
    body_ids = set(population["result"]["body_ids"])
    records_lists: dict[int, list[Any]] = {body_id: [] for body_id in body_ids}
    for record in source.contract.records:
        if record.body_id in body_ids:
            records_lists[record.body_id].append(record)
    records_by_body = {
        body_id: tuple(sorted(records)) for body_id, records in records_lists.items()
    }
    if set(summaries).intersection(body_ids) != body_ids or any(
        not records for records in records_by_body.values()
    ):
        raise SensoryPopulationReadinessError(
            "all-311 body-column summaries/records are incomplete."
        )
    base_ids = [entry.get("config", {}).get("stimulus_id") for entry in base_entries]
    base_stimuli = [
        RelativeColumnStimulus.from_dict(dict(entry["config"]))
        for entry in base_entries
    ]
    initial = _binary_coverage_rows(body_rows, records_by_body, base_stimuli, grid)
    uncovered = [row["body_id"] for row in initial if not row["body_stimulus_covered"]]

    selected_disks = []
    search_summaries = []
    for side in ("L", "R"):
        side_targets = [
            body_id
            for body_id in uncovered
            if next(row["side"] for row in body_rows if row["body_id"] == body_id)
            == side
        ]
        try:
            disks, summary = _coverage_candidates_for_side(
                side, side_targets, records_by_body, summaries, grid
            )
        except Exception as exc:
            if isinstance(exc, SensoryPopulationReadinessError):
                raise
            raise SensoryPopulationReadinessError(
                f"bounded radius-1–{MAX_RADIUS_LATTICE_STEPS} coverage failed "
                f"for {side}: {exc}"
            ) from exc
        if any(
            not 1 <= row["radius_lattice_steps"] <= MAX_RADIUS_LATTICE_STEPS
            for row in disks
        ):
            raise SensoryPopulationReadinessError(
                "coverage planner exceeded authorized radius 1–4."
            )
        selected_disks.extend(disks)
        search_summaries.append(summary)

    extension_entries = []
    extension_rows = []
    for disk in selected_disks:
        centre_1, centre_2 = disk["centre_hex"]
        stimulus_id = (
            f"coverage311_{disk['side'].lower()}_{centre_1:02d}_{centre_2:02d}_"
            f"r{disk['radius_lattice_steps']}"
        )
        if stimulus_id in base_ids:
            raise SensoryPopulationReadinessError(
                "coverage planner produced a duplicate stimulus identity."
            )
        stimulus = RelativeColumnStimulus(
            stimulus_id=stimulus_id,
            side=disk["side"],
            centre_hex1=centre_1,
            centre_hex2=centre_2,
            dt_ms=0.1,
            radii_lattice_steps=(disk["radius_lattice_steps"],),
        )
        stimulus_config = stimulus.to_dict()
        extension_entries.append(
            {
                "origin": "PHASE7N_ANATOMY_ONLY_COVERAGE_EXTENSION",
                "config": stimulus_config,
                "sha256": sha256_bytes(canonical_json_bytes(stimulus_config)),
            }
        )
        extension_rows.append(
            {
                **disk,
                "stimulus_id": stimulus_id,
                "centre_is_source_column": True,
                "coverage_basis": "binary_column_overlap_only",
                "model_outcomes_used": False,
            }
        )
    all_entries = [
        {
            "origin": "PHASE7M_BATTERY_CONFIG_RETAINED",
            "config": dict(entry["config"]),
            "sha256": entry["sha256"],
        }
        for entry in base_entries
    ] + extension_entries
    all_stimuli = [
        RelativeColumnStimulus.from_dict(entry["config"]) for entry in all_entries
    ]
    final = _binary_coverage_rows(body_rows, records_by_body, all_stimuli, grid)
    if not all(row["body_stimulus_covered"] for row in final):
        raise SensoryPopulationReadinessError(
            "authorized radius-1–4 battery cannot cover every target body."
        )
    extension_coverage = {
        body_id for disk in extension_rows for body_id in disk["covered_body_ids"]
    }
    if extension_coverage != set(uncovered):
        raise SensoryPopulationReadinessError(
            "coverage extension does not exactly cover the initial misses."
        )

    config = {
        "schema": COVERAGE_CONFIG_SCHEMA,
        "artifact_schema": COVERAGE_ARTIFACT_SCHEMA,
        "plan_id": "malecns_all_311_relative_column_coverage_v1",
        "population_artifact": _artifact_ref(population),
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "column_grid_identity": grid.to_identity_dict(),
        "inherited_stimulus_battery_id": inherited_battery_id,
        "body_ids": list(population["result"]["body_ids"]),
        "coverage_metric": "BODY_STIMULUS_COVERED_IF_ANY_SOURCE_COLUMN_OVERLAPS",
        "candidate_centres": "actual_uncovered_body_source_columns_only",
        "candidate_radius_lattice_steps": list(range(1, MAX_RADIUS_LATTICE_STEPS + 1)),
        "objective_order": [
            "minimum_added_stimulus_count",
            "minimum_total_radius",
            "lexicographic_radius_then_source_centre",
        ],
        "model_outcomes_used": False,
        "neural_dynamics_computed": False,
        "stimuli": all_entries,
    }

    def coverage_by_stratum(
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        summaries = []
        for neuron_type, side in sorted(TYPE_SIDE_COUNTS):
            members = [
                row
                for row in rows
                if row["neuron_type"] == neuron_type and row["side"] == side
            ]
            summaries.append(
                {
                    "neuron_type": neuron_type,
                    "side": side,
                    "body_count": len(members),
                    "covered_count": sum(
                        row["body_stimulus_covered"] for row in members
                    ),
                    "uncovered_count": sum(
                        not row["body_stimulus_covered"] for row in members
                    ),
                }
            )
        return summaries

    initial_stratum_coverage = coverage_by_stratum(initial)
    final_stratum_coverage = coverage_by_stratum(final)
    result = {
        "schema": COVERAGE_RESULT_SCHEMA,
        "plan_id": config["plan_id"],
        "body_ids": list(population["result"]["body_ids"]),
        "inherited_stimulus_ids": base_ids,
        "initial_coverage": initial,
        "initial_covered_count": sum(row["body_stimulus_covered"] for row in initial),
        "initial_uncovered_body_ids": uncovered,
        "initial_coverage_by_type_side": initial_stratum_coverage,
        "candidate_search_summary": search_summaries,
        "coverage_extension_stimuli": extension_rows,
        "stimulus_count": len(all_entries),
        "final_coverage": final,
        "covered_body_count": sum(row["body_stimulus_covered"] for row in final),
        "uncovered_body_ids": [
            row["body_id"] for row in final if not row["body_stimulus_covered"]
        ],
        "final_coverage_by_type_side": final_stratum_coverage,
        "model_outcomes_used": False,
        "dn_p01_outputs_read_for_design": False,
        "neural_dynamics_computed": False,
        "purpose": "ANATOMICAL_SOFTWARE_PATH_COVERAGE_ONLY",
    }
    if result["covered_body_count"] != POPULATION_SIZE:
        raise SensoryPopulationReadinessError("311/311 anatomy-only coverage failed.")
    return config, result


def build_execution_dry_run(
    population_artifact: Any,
    coverage_artifact: Any,
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Describe, hash, and validate the future arbitrary-N run without running it."""
    population = (
        population_artifact.as_input()
        if hasattr(population_artifact, "as_input")
        else dict(population_artifact)
    )
    coverage = (
        coverage_artifact.as_input()
        if hasattr(coverage_artifact, "as_input")
        else dict(coverage_artifact)
    )
    population_ids = population.get("result", {}).get("body_ids", ())
    if (
        population.get("artifact_schema") != POPULATION_ARTIFACT_SCHEMA
        or len(population_ids) != POPULATION_SIZE
        or len(set(population_ids)) != POPULATION_SIZE
        or population.get("config", {}).get("source_contract_identity")
        != dict(source.source_identity)
        or population.get("config", {}).get("circuit_contract_identity")
        != _circuit_identity(circuit)
        or coverage.get("artifact_schema") != COVERAGE_ARTIFACT_SCHEMA
        or coverage.get("result", {}).get("body_ids") != population_ids
        or coverage.get("result", {}).get("covered_body_count") != POPULATION_SIZE
        or coverage.get("result", {}).get("uncovered_body_ids") != []
        or len(coverage.get("result", {}).get("final_coverage", ())) != POPULATION_SIZE
        or not all(
            row.get("body_stimulus_covered")
            for row in coverage.get("result", {}).get("final_coverage", ())
        )
        or coverage.get("result", {}).get("neural_dynamics_computed") is not False
        or coverage.get("result", {}).get("model_outcomes_used") is not False
        or coverage.get("config", {}).get("source_contract_identity")
        != dict(source.source_identity)
        or coverage.get("config", {}).get("circuit_contract_identity")
        != _circuit_identity(circuit)
        or coverage.get("config", {}).get("population_artifact")
        != _artifact_ref(population)
    ):
        raise SensoryPopulationReadinessError(
            "population or anatomy-only coverage artifact is incomplete."
        )

    # These immutable settings were audited against the committed Phase 7M
    # artifact. Keep the future config self-contained: replay must not walk the
    # historical A–H population chain merely to recover model parameters.
    sensory = dict(_REFERENCE_SENSORY_MODEL)
    transfer = dict(_REFERENCE_TRANSFER_MODEL)
    dnp01 = dict(_REFERENCE_DNP01_MODEL)
    if (
        sensory.get("model_id") != SENSORY_MODEL_ID
        or sensory.get("tau_sens_ms") != 1.0
        or sensory.get("gain") != 1.0
        or sensory.get("initial_state") != 0.0
        or sensory.get("input_metric_id") != "column_overlap_fraction"
        or transfer.get("model_id") != TRANSFER_MODEL_ID
        or transfer.get("k_transfer_mveq_per_state") != REFERENCE_K_MVEQ_PER_STATE
        or transfer.get("source_normalization") != "none"
        or transfer.get("structural_weight_used_as_gain") is not False
        or dnp01.get("model_id") != "lif_filtered_synapse"
        or dnp01.get("config", {}).get("dt_ms") != 0.1
    ):
        raise SensoryPopulationReadinessError(
            "Phase 7E/F or DNp01 reference configuration changed."
        )
    source_rows, _ = _body_index(source, circuit)
    if set(source_rows) != set(population_ids):
        raise SensoryPopulationReadinessError(
            "execution body identities differ from source contracts."
        )
    route_rows = [
        {
            "body_id": body_id,
            "neuron_type": source_rows[body_id]["neuron_type"],
            "side": source_rows[body_id]["side"],
            "target_body_id": source_rows[body_id]["target_body_id"],
            "structural_edge_count": source_rows[body_id]["structural_weight"],
            "structural_edge_count_semantics": "SOURCE_METADATA_ONLY",
        }
        for body_id in population_ids
    ]
    stimuli = coverage["config"]["stimuli"]
    stimulus_configs = [item["config"] for item in stimuli]
    stimulus_ids = [item["stimulus_id"] for item in stimulus_configs]
    if len(stimulus_ids) != len(set(stimulus_ids)):
        raise SensoryPopulationReadinessError("execution stimulus IDs are duplicated.")
    assignment_samples = sum(len(item["radius_schedule"]) for item in stimulus_configs)
    recovery_steps = sensory.get("recovery_tail_steps")
    if not isinstance(recovery_steps, int) or recovery_steps < 0:
        raise SensoryPopulationReadinessError("invalid sensory recovery-tail config.")
    all_stimulus_interval_count = assignment_samples + recovery_steps * len(
        stimulus_configs
    )
    all_state_boundary_count = all_stimulus_interval_count + len(stimulus_configs)
    dt_values = {item["dt_ms"] for item in stimulus_configs}
    if dt_values != {dnp01["config"]["dt_ms"]}:
        raise SensoryPopulationReadinessError(
            "stimulus and DNp01 time steps are incompatible."
        )
    by_id = {item["stimulus_id"]: item for item in stimulus_configs}
    left_id, right_id = "left_expand_33_29", "right_expand_23_09"
    if left_id not in by_id or right_id not in by_id:
        raise SensoryPopulationReadinessError(
            "baseline bilateral control stimuli are missing."
        )
    bilateral_intervals = max(
        len(by_id[stimulus_id]["radius_schedule"]) + recovery_steps
        for stimulus_id in (left_id, right_id)
    )
    controls = [
        {"condition_id": "reference_bilateral", "mask": "all_population", "k": 1.0},
        {"condition_id": "k_zero", "mask": "all_population", "k": 0.0},
        {"condition_id": "no_sources", "mask": "none", "k": 1.0},
        {"condition_id": "lc4_only", "mask": "LC4", "k": 1.0},
        {"condition_id": "lplc2_only", "mask": "LPLC2", "k": 1.0},
        {"condition_id": "left_only", "mask": "left", "k": 1.0},
        {"condition_id": "right_only", "mask": "right", "k": 1.0},
        {"condition_id": "sensitivity_k_2", "mask": "all_population", "k": 2.0},
    ]
    conditions = [
        {
            "condition_id": f"stimulus::{item['stimulus_id']}",
            "stimulus_ids": [item["stimulus_id"]],
            "mask": "all_population",
            "k_transfer_mveq_per_state": REFERENCE_K_MVEQ_PER_STATE,
        }
        for item in stimulus_configs
    ] + [
        {
            **control,
            "stimulus_ids": [left_id, right_id],
            "k_transfer_mveq_per_state": control["k"],
            "interval_count": bilateral_intervals,
        }
        for control in controls
    ]
    total_intervals = all_stimulus_interval_count + len(controls) * bilateral_intervals
    ledger_rows = POPULATION_SIZE * total_intervals
    if any(
        condition["mask"] == "all_population"
        and condition.get("source_normalization", "none") != "none"
        for condition in conditions
    ):
        raise SensoryPopulationReadinessError(
            "population normalization is not authorized."
        )

    model_config_identity = {
        "sensory_model": sensory,
        "transfer_model": transfer,
        "dnp01_model": dnp01,
    }
    model_config_sha256 = _sha256_json(model_config_identity)
    config = {
        "schema": EXECUTION_CONFIG_SCHEMA,
        "artifact_schema": EXECUTION_ARTIFACT_SCHEMA,
        "execution_id": "phase7n_all_311_execution_dry_run_v1",
        "population_artifact": _artifact_ref(population),
        "coverage_artifact": _artifact_ref(coverage),
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "target_body_ids": list(TARGET_IDS),
        "stimuli": stimuli,
        "sensory_model": sensory,
        "transfer_model": transfer,
        "dnp01_model": dnp01,
        "model_config_sha256": model_config_sha256,
        "model_config_reference": {
            "artifact_id": PHASE7M_EXPERIMENT_ID,
            "artifact_schema": "bounded_sensory_population128_artifact_v1",
            "config_sha256": PHASE7M_EXPERIMENT_CONFIG_SHA256,
            "role": "MODEL_PARAMETER_REFERENCE_ONLY_NOT_POPULATION_PROVENANCE",
        },
        "timing": {
            "dt_ms": dnp01["config"]["dt_ms"],
            "time_grid": "integer_sample_steps_v1",
            "transfer_alignment": "state_boundary_n_drives_interval_n_to_n_plus_1",
            "recovery_tail_steps_per_stimulus": recovery_steps,
        },
        "conditions": conditions,
        "population_normalization": "none",
        "structural_edge_count_numerical_use": "none_source_metadata_only",
        "expected_dimensions": {
            "body_count": POPULATION_SIZE,
            "type_counts": TYPE_COUNTS,
            "type_side_counts": [
                {
                    "neuron_type": neuron_type,
                    "side": side,
                    "count": count,
                }
                for (neuron_type, side), count in sorted(TYPE_SIDE_COUNTS.items())
            ],
            "stimulus_count": len(stimulus_configs),
            "assignment_sample_count": assignment_samples,
            "assignment_body_exposure_rows": POPULATION_SIZE * assignment_samples,
            "state_boundary_values_per_body": all_state_boundary_count,
            "total_planned_conditions": len(conditions),
            "total_planned_model_intervals": total_intervals,
            "expected_contribution_ledger_rows": ledger_rows,
        },
        "full_population_provenance_is_direct": True,
        "historical_sample_chain_required": False,
        "dynamics_executed": False,
    }
    result = {
        "schema": EXECUTION_RESULT_SCHEMA,
        "execution_id": config["execution_id"],
        "population_semantics": "COMPLETE_TARGET_POPULATION",
        "body_count": POPULATION_SIZE,
        "body_ids": list(population_ids),
        "body_routes": route_rows,
        "target_body_ids": list(TARGET_IDS),
        "stimulus_ids": stimulus_ids,
        "stimulus_count": len(stimulus_ids),
        "assignment_sample_count": assignment_samples,
        "expected_assignment_body_exposure_rows": POPULATION_SIZE * assignment_samples,
        "expected_state_boundary_values_per_body": all_state_boundary_count,
        "planned_condition_count": len(conditions),
        "planned_model_interval_count": total_intervals,
        "expected_contribution_ledger_rows": ledger_rows,
        "model_config_sha256": model_config_sha256,
        "execution_config_sha256": _sha256_json(config),
        "future_artifact_destination": str(
            DEFAULT_SOURCE_ROOT / "sensory_population_experiment_311_v1"
        ),
        "dynamic_results_present": False,
        "sensory_trajectories_computed": False,
        "transfer_ledger_computed": False,
        "dn_p01_execution_performed": False,
        "historical_sample_chain_required": False,
    }
    return config, result


def _artifact_id(
    kind: str, config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    try:
        schema = _ARTIFACTS[kind][0]
    except KeyError:
        raise SensoryPopulationReadinessError(
            "unknown readiness artifact kind."
        ) from None
    return sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_schema": schema,
                "config_sha256": _sha256_json(config),
                "result_sha256": _sha256_json(result),
            }
        )
    )


def _validate_artifact(
    kind: str, config: dict[str, Any], result: dict[str, Any]
) -> None:
    try:
        schema, config_schema, result_schema, _, _, _ = _ARTIFACTS[kind]
    except KeyError:
        raise SensoryPopulationReadinessError(
            "unknown readiness artifact kind."
        ) from None
    if config.get("schema") != config_schema or result.get("schema") != result_schema:
        raise SensoryPopulationReadinessError("unsupported readiness artifact schema.")
    if kind == "population":
        ids = result.get("body_ids", ())
        if (
            len(ids) != POPULATION_SIZE
            or len(set(ids)) != POPULATION_SIZE
            or len(result.get("bodies", ())) != POPULATION_SIZE
            or config.get("body_ids") != ids
            or result.get("body_count") != POPULATION_SIZE
            or result.get("all_bodies_have_column_topology") is not True
            or result.get("all_source_coordinates_are_valid_relative_hex") is not True
            or result.get("dynamic_state_present") is not False
        ):
            raise SensoryPopulationReadinessError(
                "invalid full-population plan payload."
            )
    elif kind == "coverage":
        ids = result.get("body_ids", ())
        if (
            len(ids) != POPULATION_SIZE
            or config.get("body_ids") != ids
            or result.get("covered_body_count") != POPULATION_SIZE
            or result.get("uncovered_body_ids") != []
            or len(result.get("final_coverage", ())) != POPULATION_SIZE
            or not all(
                row.get("body_stimulus_covered") for row in result["final_coverage"]
            )
            or result.get("model_outcomes_used") is not False
            or result.get("neural_dynamics_computed") is not False
        ):
            raise SensoryPopulationReadinessError("invalid all-311 coverage payload.")
    else:
        if (
            result.get("body_count") != POPULATION_SIZE
            or len(result.get("body_ids", ())) != POPULATION_SIZE
            or len(set(result.get("body_ids", ()))) != POPULATION_SIZE
            or len(result.get("body_routes", ())) != POPULATION_SIZE
            or result.get("dynamic_results_present") is not False
            or result.get("sensory_trajectories_computed") is not False
            or result.get("transfer_ledger_computed") is not False
            or result.get("dn_p01_execution_performed") is not False
            or result.get("historical_sample_chain_required") is not False
            or config.get("dynamics_executed") is not False
            or result.get("execution_config_sha256") != _sha256_json(config)
        ):
            raise SensoryPopulationReadinessError("invalid dry-run execution manifest.")


def load_readiness_artifact(path: str | Path, kind: str) -> LoadedReadinessArtifact:
    try:
        artifact_schema, config_schema, result_schema, config_name, result_name, _ = (
            _ARTIFACTS[kind]
        )
    except KeyError:
        raise SensoryPopulationReadinessError(
            "unknown readiness artifact kind."
        ) from None
    root = Path(path)
    if not root.is_dir() or {item.name for item in root.iterdir()} != {
        config_name,
        result_name,
        _MANIFEST_FILENAME,
    }:
        raise SensoryPopulationReadinessError("readiness artifact file set is invalid.")
    try:
        config_raw = (root / config_name).read_bytes()
        result_raw = (root / result_name).read_bytes()
        manifest_raw = (root / _MANIFEST_FILENAME).read_bytes()
        config = json.loads(config_raw.decode("utf-8"))
        result = json.loads(result_raw.decode("utf-8"))
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise SensoryPopulationReadinessError(
            "readiness artifact JSON is malformed."
        ) from None
    if any(
        raw != canonical_json_bytes(value) + b"\n"
        for raw, value in (
            (config_raw, config),
            (result_raw, result),
            (manifest_raw, manifest),
        )
    ):
        raise SensoryPopulationReadinessError(
            "readiness artifact is not canonical JSON."
        )
    _validate_artifact(kind, config, result)
    expected_id = _artifact_id(kind, config, result)
    if (
        manifest.get("artifact_schema") != artifact_schema
        or manifest.get("artifact_id") != expected_id
        or manifest.get("config_sha256") != sha256_bytes(config_raw)
        or manifest.get("result_sha256") != sha256_bytes(result_raw)
        or manifest.get("config_schema") != config_schema
        or manifest.get("result_schema") != result_schema
    ):
        raise SensoryPopulationReadinessError(
            "readiness artifact integrity check failed."
        )
    return LoadedReadinessArtifact(root, kind, expected_id, config, result, manifest)


def export_readiness_artifact(
    kind: str,
    config: dict[str, Any],
    result: dict[str, Any],
    *,
    output_root: str | Path | None = None,
) -> LoadedReadinessArtifact:
    try:
        (
            artifact_schema,
            config_schema,
            result_schema,
            config_name,
            result_name,
            default_root,
        ) = _ARTIFACTS[kind]
    except KeyError:
        raise SensoryPopulationReadinessError(
            "unknown readiness artifact kind."
        ) from None
    _validate_artifact(kind, config, result)
    artifact_id = _artifact_id(kind, config, result)
    root = Path(output_root) if output_root is not None else default_root
    destination = root / artifact_id
    if destination.exists():
        existing = load_readiness_artifact(destination, kind)
        if existing.config != config or existing.result != result:
            raise SensoryPopulationReadinessError(
                "immutable readiness artifact differs from deterministic replay."
            )
        return existing
    config_raw = canonical_json_bytes(config) + b"\n"
    result_raw = canonical_json_bytes(result) + b"\n"
    manifest = {
        "artifact_schema": artifact_schema,
        "artifact_id": artifact_id,
        "config_schema": config_schema,
        "result_schema": result_schema,
        "config_sha256": sha256_bytes(config_raw),
        "result_sha256": sha256_bytes(result_raw),
    }
    staging: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=destination.parent)
        )
        for name, payload in (
            (config_name, config_raw),
            (result_name, result_raw),
            (_MANIFEST_FILENAME, canonical_json_bytes(manifest) + b"\n"),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        os.replace(staging, destination)
        staging = None
    except OSError as exc:
        raise SensoryPopulationReadinessError(
            "could not persist readiness artifact."
        ) from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_readiness_artifact(destination, kind)


def load_phase7n_sources(
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> tuple[RelativeColumnAssignmentSource, CircuitContract, RelativeColumnGrid]:
    source = load_relative_column_source(source_root)
    circuit = load_circuit_contract(source_root)
    grid = load_relative_column_grid(workbook_path, source)
    return source, circuit, grid
