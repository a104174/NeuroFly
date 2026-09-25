"""Four-body relative-column anatomical assignment; no neural transfer model."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from neurofly.malecns.column_lattice import (
    OFFICIAL_COLUMN_WORKBOOK_COMMIT,
    OFFICIAL_COLUMN_WORKBOOK_SHA256,
    hex_distance,
    load_official_columns,
)
from neurofly.malecns.column_snapshot import load_column_contract
from neurofly.malecns.columns import (
    COLUMN_INPUT_FILENAME,
    COLUMN_SCHEMA_VERSION,
    COLUMN_SUMMARY_FILENAME,
    BodyColumnInputContract,
    BodyColumnSummary,
    ColumnInputRecord,
)
from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.models import MALECNS_DATASET

RELATIVE_STIMULUS_SCHEMA = "relative_column_stimulus_v1"
RELATIVE_STIMULUS_MODEL_ID = "relative_column_expanding_disk_v1"
RELATIVE_EXPERIMENT_CONFIG_SCHEMA = "relative_column_assignment_config_v1"
RELATIVE_ASSIGNMENT_RESULT_SCHEMA = "relative_sensory_assignment_result_v1"
EXPERIMENT_ID = "phase7d_four_body_relative_column_assignment_v1"

DEFAULT_SOURCE_ROOT = Path("data/derived/malecns/looming_giant_fiber_v1")
DEFAULT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "relative_column_assignment_v1"
DEFAULT_WORKBOOK = Path("data/raw/malecns/optic-column-type-assignments-v1.0.xlsx")

BODY_IDENTITIES = (
    {"body_id": 12032, "neuron_type": "LC4", "side": "L"},
    {"body_id": 16128, "neuron_type": "LC4", "side": "R"},
    {"body_id": 11498, "neuron_type": "LPLC2", "side": "L"},
    {"body_id": 14465, "neuron_type": "LPLC2", "side": "R"},
)
BODY_IDS = tuple(item["body_id"] for item in BODY_IDENTITIES)
EXPECTED_COLUMN_FILE_HASHES = {
    COLUMN_INPUT_FILENAME: (
        "4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e"
    ),
    COLUMN_SUMMARY_FILENAME: (
        "ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b"
    ),
}
EXPECTED_CIRCUIT_FILE_HASHES = {
    "connections.jsonl": (
        "f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a"
    ),
    "neurons.jsonl": (
        "00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e"
    ),
}
_STIMULUS_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class RelativeColumnAssignmentError(ValueError):
    """Invalid source identity, relative stimulus, or anatomical assignment."""


def canonical_json_bytes(value: Any) -> bytes:
    """Project-standard deterministic JSON encoding for assignment identities."""

    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RelativeColumnAssignmentError("value is not deterministic JSON") from exc


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with Path(path).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise RelativeColumnAssignmentError(
            f"could not read {Path(path).name}"
        ) from exc
    return digest.hexdigest()


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _freeze_nested(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(mapping))


@dataclass(frozen=True, slots=True)
class RelativeColumnStimulus:
    """A discrete disk schedule in one MaleCNS relative column lattice."""

    stimulus_id: str
    side: str
    centre_hex1: int
    centre_hex2: int
    dt_ms: float
    radii_lattice_steps: tuple[int, ...]
    start_step: int = 0
    schema: str = RELATIVE_STIMULUS_SCHEMA
    model_id: str = RELATIVE_STIMULUS_MODEL_ID

    def __post_init__(self) -> None:
        if self.schema != RELATIVE_STIMULUS_SCHEMA:
            raise RelativeColumnAssignmentError("unsupported relative stimulus schema.")
        if self.model_id != RELATIVE_STIMULUS_MODEL_ID:
            raise RelativeColumnAssignmentError("unsupported relative stimulus model.")
        if not _STIMULUS_ID_RE.fullmatch(self.stimulus_id):
            raise RelativeColumnAssignmentError("stimulus_id is malformed.")
        if self.side not in {"L", "R"}:
            raise RelativeColumnAssignmentError("stimulus side must be L or R.")
        if not _is_int(self.centre_hex1) or not _is_int(self.centre_hex2):
            raise RelativeColumnAssignmentError(
                "stimulus centre must be an integer hex pair."
            )
        if not _is_int(self.start_step) or self.start_step < 0:
            raise RelativeColumnAssignmentError(
                "start_step must be a non-negative integer."
            )
        if isinstance(self.dt_ms, bool) or not isinstance(self.dt_ms, (int, float)):
            raise RelativeColumnAssignmentError("dt_ms must be finite and positive.")
        dt_ms = float(self.dt_ms)
        if not math.isfinite(dt_ms) or dt_ms <= 0:
            raise RelativeColumnAssignmentError("dt_ms must be finite and positive.")
        if (
            not isinstance(self.radii_lattice_steps, tuple)
            or not self.radii_lattice_steps
        ):
            raise RelativeColumnAssignmentError("radius schedule must contain samples.")
        if any(
            not _is_int(radius) or radius < 0 for radius in self.radii_lattice_steps
        ):
            raise RelativeColumnAssignmentError(
                "radius values must be non-negative integer lattice steps."
            )
        if not math.isfinite(
            (self.start_step + len(self.radii_lattice_steps) - 1) * dt_ms
        ):
            raise RelativeColumnAssignmentError("stimulus sample time is not finite.")
        object.__setattr__(self, "dt_ms", dt_ms)

    @property
    def end_step(self) -> int:
        return self.start_step + len(self.radii_lattice_steps) - 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "model_id": self.model_id,
            "stimulus_id": self.stimulus_id,
            "side": self.side,
            "centre_hex": [self.centre_hex1, self.centre_hex2],
            "spatial_unit": "MaleCNS_hex_lattice_steps",
            "time_unit": "ms",
            "dt_ms": self.dt_ms,
            "time_grid_semantics": "integer_sample_steps_v1",
            "start_step": self.start_step,
            "end_step": self.end_step,
            "radius_schedule": [
                {"step": self.start_step + offset, "radius_lattice_steps": radius}
                for offset, radius in enumerate(self.radii_lattice_steps)
            ],
            "assumption_label": "SYNTHETIC_RELATIVE_COLUMN_STIMULUS",
            "absolute_visual_angle_present": False,
        }

    @classmethod
    def from_dict(cls, value: Any) -> RelativeColumnStimulus:
        expected = {
            "schema",
            "model_id",
            "stimulus_id",
            "side",
            "centre_hex",
            "spatial_unit",
            "time_unit",
            "dt_ms",
            "time_grid_semantics",
            "start_step",
            "end_step",
            "radius_schedule",
            "assumption_label",
            "absolute_visual_angle_present",
        }
        if not isinstance(value, dict) or set(value) != expected:
            raise RelativeColumnAssignmentError("invalid relative stimulus fields.")
        centre = value["centre_hex"]
        schedule = value["radius_schedule"]
        if (
            value["spatial_unit"] != "MaleCNS_hex_lattice_steps"
            or value["time_unit"] != "ms"
            or value["time_grid_semantics"] != "integer_sample_steps_v1"
            or value["assumption_label"] != "SYNTHETIC_RELATIVE_COLUMN_STIMULUS"
            or value["absolute_visual_angle_present"] is not False
            or not isinstance(centre, list)
            or len(centre) != 2
            or not isinstance(schedule, list)
            or not schedule
        ):
            raise RelativeColumnAssignmentError(
                "relative stimulus semantics are invalid."
            )
        if any(
            not isinstance(item, dict)
            or set(item) != {"step", "radius_lattice_steps"}
            or not _is_int(item["step"])
            or not _is_int(item["radius_lattice_steps"])
            for item in schedule
        ):
            raise RelativeColumnAssignmentError("radius schedule is malformed.")
        start = value["start_step"]
        end = value["end_step"]
        if not _is_int(start) or start < 0:
            raise RelativeColumnAssignmentError(
                "start_step must be a non-negative integer."
            )
        expected_steps = list(range(start, start + len(schedule)))
        if [item["step"] for item in schedule] != expected_steps:
            raise RelativeColumnAssignmentError(
                "radius schedule steps are not contiguous."
            )
        if not _is_int(end) or end != expected_steps[-1]:
            raise RelativeColumnAssignmentError(
                "end_step does not match the sample grid."
            )
        return cls(
            schema=value["schema"],
            model_id=value["model_id"],
            stimulus_id=value["stimulus_id"],
            side=value["side"],
            centre_hex1=centre[0],
            centre_hex2=centre[1],
            dt_ms=value["dt_ms"],
            radii_lattice_steps=tuple(
                item["radius_lattice_steps"] for item in schedule
            ),
            start_step=start,
        )


@dataclass(frozen=True, slots=True)
class RelativeColumnAssignmentSource:
    """Hash-validated source topology and exact authorized body identities."""

    source_root: Path
    contract: BodyColumnInputContract
    source_identity: Mapping[str, Any]
    body_records: Mapping[int, tuple[ColumnInputRecord, ...]]
    body_summaries: Mapping[int, BodyColumnSummary]


@dataclass(frozen=True, slots=True)
class RelativeColumnGrid:
    """Pinned official medulla lattice plus validated source-only coordinates."""

    columns_by_side: Mapping[str, frozenset[tuple[int, int]]]
    official_classes_by_side: Mapping[str, Mapping[tuple[int, int], str]]
    workbook_sha256: str
    workbook_commit: str = OFFICIAL_COLUMN_WORKBOOK_COMMIT

    def __post_init__(self) -> None:
        if set(self.columns_by_side) != {"L", "R"}:
            raise RelativeColumnAssignmentError(
                "column grid must contain L and R sides."
            )
        if set(self.official_classes_by_side) != {"L", "R"}:
            raise RelativeColumnAssignmentError(
                "column classes must contain L and R sides."
            )
        if self.workbook_sha256 != OFFICIAL_COLUMN_WORKBOOK_SHA256:
            raise RelativeColumnAssignmentError(
                "column grid workbook hash is not pinned."
            )
        if self.workbook_commit != OFFICIAL_COLUMN_WORKBOOK_COMMIT:
            raise RelativeColumnAssignmentError(
                "column grid workbook commit is not pinned."
            )

    def to_identity_dict(self) -> dict[str, Any]:
        return {
            "resource": "optic-column-type-assignments-v1.0.xlsx",
            "repository": "flyconnectome/2025malecns",
            "commit": self.workbook_commit,
            "sha256": self.workbook_sha256,
            "official_medulla_column_counts": {
                side: len(self.official_classes_by_side[side]) for side in ("L", "R")
            },
            "source_only_coordinate_counts": {
                side: len(
                    self.columns_by_side[side]
                    - frozenset(self.official_classes_by_side[side])
                )
                for side in ("L", "R")
            },
            "source_only_coordinates_are_unclassified": True,
        }


def load_relative_column_source(
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
) -> RelativeColumnAssignmentSource:
    """Load and pin the existing local circuit and body-column contracts."""

    root = Path(source_root)
    try:
        circuit = load_circuit_contract(root)
        column_path = root / "body_columns_v1"
        contract = load_column_contract(column_path, circuit_contract=circuit)
        column_manifest_path = column_path / "column_manifest.json"
        column_manifest = json.loads(column_manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        if isinstance(exc, RelativeColumnAssignmentError):
            raise
        raise RelativeColumnAssignmentError(
            f"source contract failed integrity or identity validation: {exc}"
        ) from exc

    if contract.schema_version != COLUMN_SCHEMA_VERSION:
        raise RelativeColumnAssignmentError(
            "source column schema is not body_column_input_v1."
        )
    if contract.dataset != MALECNS_DATASET:
        raise RelativeColumnAssignmentError("source dataset must be male-cns:v1.0.")
    if (contract.candidate_identifier, contract.candidate_version) != (
        "looming_giant_fiber_v1",
        1,
    ):
        raise RelativeColumnAssignmentError("source candidate identity is not pinned.")
    column_hashes = dict(column_manifest.get("sha256", {}))
    if column_hashes != EXPECTED_COLUMN_FILE_HASHES:
        raise RelativeColumnAssignmentError(
            "source body-column file hashes are not pinned."
        )
    if dict(circuit.integrity.sha256_by_file) != EXPECTED_CIRCUIT_FILE_HASHES:
        raise RelativeColumnAssignmentError(
            "source CircuitContract file hashes are not pinned."
        )
    official_resource = column_manifest.get("official_column_resource", {})
    if official_resource != {
        "file": "optic-column-type-assignments-v1.0.xlsx",
        "source": "https://github.com/flyconnectome/2025malecns",
        "commit": OFFICIAL_COLUMN_WORKBOOK_COMMIT,
        "sha256": OFFICIAL_COLUMN_WORKBOOK_SHA256,
        "identifier_format": "ME_<L|R>_col_<hex1>_<hex2>",
    }:
        raise RelativeColumnAssignmentError(
            "source manifest references another column workbook."
        )

    summaries = {summary.body_id: summary for summary in contract.summaries}
    by_body: dict[int, list[ColumnInputRecord]] = defaultdict(list)
    for record in contract.records:
        by_body[record.body_id].append(record)
    expected = {item["body_id"]: item for item in BODY_IDENTITIES}
    if len(summaries) != 311:
        raise RelativeColumnAssignmentError(
            "source body-column population is not 311 bodies."
        )
    if set(expected) - set(summaries):
        raise RelativeColumnAssignmentError(
            "one or more authorized bodies are absent from source."
        )
    for body_id, identity in expected.items():
        summary = summaries[body_id]
        neuron = circuit.neurons_by_body_id.get(body_id)
        if neuron is None or (neuron.type, neuron.soma_side) != (
            identity["neuron_type"],
            identity["side"],
        ):
            raise RelativeColumnAssignmentError(
                f"CircuitContract identity mismatch for body {body_id}."
            )
        if (summary.neuron_type, summary.eye_side) != (
            identity["neuron_type"],
            identity["side"],
        ):
            raise RelativeColumnAssignmentError(
                f"body-column source identity mismatch for body {body_id}."
            )
        records = by_body.get(body_id, [])
        if not records or any(
            (record.neuron_type, record.eye_side)
            != (
                identity["neuron_type"],
                identity["side"],
            )
            or record.input_count <= 0
            for record in records
        ):
            raise RelativeColumnAssignmentError(
                f"malformed or side/type-mismatched source records for body {body_id}."
            )
        if (
            sum(record.input_count for record in records)
            != summary.assigned_input_count
        ):
            raise RelativeColumnAssignmentError(
                f"source count mismatch for body {body_id}."
            )
        if summary.assigned_input_count <= 0 or summary.relevant_input_count <= 0:
            raise RelativeColumnAssignmentError(
                f"zero exposure denominator for body {body_id}."
            )

    circuit_identity = {
        "candidate_id": circuit.candidate.identifier,
        "candidate_version": circuit.candidate.version,
        "dataset": circuit.candidate.dataset,
        "source_file_sha256": dict(circuit.integrity.sha256_by_file),
    }
    source_identity = {
        "schema": contract.schema_version,
        "dataset": contract.dataset,
        "candidate_id": contract.candidate_identifier,
        "candidate_version": contract.candidate_version,
        "source_file_sha256": column_hashes,
        "source_manifest_sha256": sha256_file(column_manifest_path),
        "circuit_contract": circuit_identity,
    }
    identity_fields = (
        "schema",
        "dataset",
        "candidate_id",
        "candidate_version",
        "source_file_sha256",
        "circuit_contract",
    )
    source_identity["contract_identity_sha256"] = sha256_bytes(
        canonical_json_bytes({key: source_identity[key] for key in identity_fields})
    )
    return RelativeColumnAssignmentSource(
        source_root=root,
        contract=contract,
        source_identity=_freeze_nested(source_identity),
        body_records=MappingProxyType(
            {body_id: tuple(by_body[body_id]) for body_id in BODY_IDS}
        ),
        body_summaries=MappingProxyType(
            {body_id: summaries[body_id] for body_id in BODY_IDS}
        ),
    )


def load_relative_column_grid(
    workbook_path: str | Path,
    source: RelativeColumnAssignmentSource,
) -> RelativeColumnGrid:
    """Read the pinned grid and retain validated source-only LO/LOP coordinates."""

    try:
        official = load_official_columns(Path(workbook_path))
    except Exception as exc:
        raise RelativeColumnAssignmentError(
            f"could not validate official column grid: {exc}"
        ) from exc
    source_coords: dict[str, set[tuple[int, int]]] = {"L": set(), "R": set()}
    for record in source.contract.records:
        source_coords[record.eye_side].add((record.ol_hex1, record.ol_hex2))
    classes: dict[str, Mapping[tuple[int, int], str]] = {}
    columns: dict[str, frozenset[tuple[int, int]]] = {}
    for side in ("L", "R"):
        official_coords = set(official[side])
        classes[side] = MappingProxyType(dict(official[side]))
        columns[side] = frozenset(official_coords | source_coords[side])
    return RelativeColumnGrid(
        columns_by_side=MappingProxyType(columns),
        official_classes_by_side=MappingProxyType(classes),
        workbook_sha256=OFFICIAL_COLUMN_WORKBOOK_SHA256,
    )


def fixed_stimuli() -> tuple[RelativeColumnStimulus, ...]:
    """Phase 7C bounded proof expressed as deterministic sample schedules."""

    return (
        RelativeColumnStimulus("left_expand_33_29", "L", 33, 29, 0.1, (1, 2, 3, 4)),
        RelativeColumnStimulus("left_lplc2_11498_18_04", "L", 18, 4, 0.1, (2,)),
        RelativeColumnStimulus("right_expand_23_09", "R", 23, 9, 0.1, (1, 2, 3, 4)),
        RelativeColumnStimulus("right_translate_23_11", "R", 23, 11, 0.1, (2,)),
    )


def build_experiment_config(
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
) -> dict[str, Any]:
    stimuli = [stimulus.to_dict() for stimulus in fixed_stimuli()]
    return {
        "schema": RELATIVE_EXPERIMENT_CONFIG_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "assignment_schema": RELATIVE_ASSIGNMENT_RESULT_SCHEMA,
        "model_id": RELATIVE_STIMULUS_MODEL_ID,
        "body_identities": [dict(item) for item in BODY_IDENTITIES],
        "source_identity": dict(source.source_identity),
        "column_grid_identity": grid.to_identity_dict(),
        "stimuli": [
            {
                "config": stimulus,
                "stimulus_sha256": sha256_bytes(canonical_json_bytes(stimulus)),
            }
            for stimulus in stimuli
        ],
        "scientific_boundary": {
            "result_semantics": "ANATOMICAL_EXPOSURE",
            "structural_site_counts_are_physiological_weights": False,
            "type_level_encoder_drive_mixed": False,
            "visual_angle_present": False,
            "functional_receptive_field_claim": False,
            "neural_dynamics_present": False,
        },
    }


def _validate_experiment_config(
    value: Any,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
) -> tuple[RelativeColumnStimulus, ...]:
    expected_fields = {
        "schema",
        "experiment_id",
        "assignment_schema",
        "model_id",
        "body_identities",
        "source_identity",
        "column_grid_identity",
        "stimuli",
        "scientific_boundary",
    }
    if not isinstance(value, dict) or set(value) != expected_fields:
        raise RelativeColumnAssignmentError(
            "invalid assignment experiment configuration."
        )
    if (
        value["schema"] != RELATIVE_EXPERIMENT_CONFIG_SCHEMA
        or value["experiment_id"] != EXPERIMENT_ID
        or value["assignment_schema"] != RELATIVE_ASSIGNMENT_RESULT_SCHEMA
        or value["model_id"] != RELATIVE_STIMULUS_MODEL_ID
        or value["body_identities"] != [dict(item) for item in BODY_IDENTITIES]
        or value["source_identity"] != dict(source.source_identity)
        or value["column_grid_identity"] != grid.to_identity_dict()
    ):
        raise RelativeColumnAssignmentError(
            "assignment configuration identity mismatch."
        )
    if value["scientific_boundary"] != {
        "result_semantics": "ANATOMICAL_EXPOSURE",
        "structural_site_counts_are_physiological_weights": False,
        "type_level_encoder_drive_mixed": False,
        "visual_angle_present": False,
        "functional_receptive_field_claim": False,
        "neural_dynamics_present": False,
    }:
        raise RelativeColumnAssignmentError(
            "assignment configuration crosses science boundary."
        )
    entries = value["stimuli"]
    if not isinstance(entries, list) or len(entries) != len(fixed_stimuli()):
        raise RelativeColumnAssignmentError(
            "fixed four-body experiment has wrong stimulus count."
        )
    stimuli: list[RelativeColumnStimulus] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"config", "stimulus_sha256"}:
            raise RelativeColumnAssignmentError(
                "malformed stimulus configuration entry."
            )
        stimulus_dict = entry["config"]
        if entry["stimulus_sha256"] != sha256_bytes(
            canonical_json_bytes(stimulus_dict)
        ):
            raise RelativeColumnAssignmentError("stimulus configuration hash mismatch.")
        stimuli.append(RelativeColumnStimulus.from_dict(stimulus_dict))
    expected_stimuli = tuple(stimulus.to_dict() for stimulus in fixed_stimuli())
    if tuple(stimulus.to_dict() for stimulus in stimuli) != expected_stimuli:
        raise RelativeColumnAssignmentError(
            "stimulus set differs from fixed Phase 7D experiment."
        )
    return tuple(stimuli)


def active_column_set(
    stimulus: RelativeColumnStimulus,
    grid: RelativeColumnGrid,
    radius_lattice_steps: int,
) -> tuple[tuple[int, int], ...]:
    if not _is_int(radius_lattice_steps) or radius_lattice_steps < 0:
        raise RelativeColumnAssignmentError(
            "radius must be non-negative integer lattice steps."
        )
    valid = grid.columns_by_side[stimulus.side]
    centre = (stimulus.centre_hex1, stimulus.centre_hex2)
    if centre not in valid:
        raise RelativeColumnAssignmentError(
            f"unknown {stimulus.side} column coordinate {centre}."
        )
    return tuple(
        sorted(
            coordinate
            for coordinate in valid
            if hex_distance(centre, coordinate) <= radius_lattice_steps
        )
    )


def _exposure_for_body(
    records: tuple[ColumnInputRecord, ...],
    summary: BodyColumnSummary,
    stimulus: RelativeColumnStimulus,
    active_columns: frozenset[tuple[int, int]],
) -> dict[str, Any]:
    if not records or summary.assigned_input_count <= 0:
        raise RelativeColumnAssignmentError(
            f"body {summary.body_id} has no assigned source-site denominator."
        )
    if any(
        (record.neuron_type, record.eye_side) != (summary.neuron_type, summary.eye_side)
        or record.input_count <= 0
        for record in records
    ):
        raise RelativeColumnAssignmentError(
            f"malformed identity or source count for body {summary.body_id}."
        )
    if summary.eye_side != stimulus.side:
        column_overlap = 0.0
        unique_overlap = 0.0
        site_overlap = 0.0
    else:
        matching = tuple(
            record
            for record in records
            if (record.ol_hex1, record.ol_hex2) in active_columns
        )
        unique_hexes = {(record.ol_hex1, record.ol_hex2) for record in records}
        column_overlap = len(matching) / len(records)
        unique_overlap = len(unique_hexes & active_columns) / len(unique_hexes)
        site_overlap = (
            sum(record.input_count for record in matching)
            / summary.assigned_input_count
        )
    fractions = (
        column_overlap,
        unique_overlap,
        site_overlap,
        summary.assignment_fraction,
    )
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in fractions):
        raise RelativeColumnAssignmentError("anatomical exposure is outside [0,1].")
    return {
        "body_id": summary.body_id,
        "neuron_type": summary.neuron_type,
        "side": summary.eye_side,
        "semantic_classification": "ANATOMICAL_EXPOSURE",
        "source_column_record_count": len(records),
        "source_unique_hex_count": len(
            {(record.ol_hex1, record.ol_hex2) for record in records}
        ),
        "source_assigned_input_sites": summary.assigned_input_count,
        "source_relevant_input_sites": summary.relevant_input_count,
        "source_unassigned_input_sites": summary.unassigned_input_count,
        "source_coverage_fraction": summary.assignment_fraction,
        "active_source_column_record_count": sum(
            1
            for record in records
            if summary.eye_side == stimulus.side
            and (record.ol_hex1, record.ol_hex2) in active_columns
        ),
        "column_overlap_fraction": column_overlap,
        "unique_hex_overlap_fraction": unique_overlap,
        "structural_input_site_overlap_fraction": site_overlap,
        "structural_weight_semantics": "source_anatomical_input_site_count_only",
        "neural_response_present": False,
    }


def compute_assignment_result(
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    config: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Derive time-indexed four-body exposure, without any neural transfer."""

    experiment_config = (
        build_experiment_config(source, grid) if config is None else config
    )
    stimuli = _validate_experiment_config(experiment_config, source, grid)
    samples: list[dict[str, Any]] = []
    for stimulus in stimuli:
        for offset, radius in enumerate(stimulus.radii_lattice_steps):
            step = stimulus.start_step + offset
            active = active_column_set(stimulus, grid, radius)
            active_set = frozenset(active)
            body_assignments = [
                _exposure_for_body(
                    source.body_records[body_id],
                    source.body_summaries[body_id],
                    stimulus,
                    active_set,
                )
                for body_id in BODY_IDS
            ]
            samples.append(
                {
                    "stimulus_id": stimulus.stimulus_id,
                    "side": stimulus.side,
                    "step": step,
                    "time_ms": step * stimulus.dt_ms,
                    "dt_ms": stimulus.dt_ms,
                    "radius_lattice_steps": radius,
                    "active_column_count": len(active),
                    "active_column_set_sha256": sha256_bytes(
                        canonical_json_bytes([list(item) for item in active])
                    ),
                    "active_columns": [list(item) for item in active],
                    "assignments": body_assignments,
                }
            )
    result = {
        "schema": RELATIVE_ASSIGNMENT_RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "semantics": "ANATOMICAL_EXPOSURE_ONLY",
        "spatial_unit": "MaleCNS_hex_lattice_steps",
        "sample_time_semantics": "integer_step_is_authoritative",
        "sample_count": len(samples),
        "body_ids": list(BODY_IDS),
        "samples": samples,
        "limitations": {
            "absolute_visual_angle_present": False,
            "functional_receptive_field_present": False,
            "neural_dynamics_present": False,
            "type_level_encoder_drive_mixed": False,
            "exposure_is_neural_drive": False,
            "structural_input_site_count_is_physiological_weight": False,
        },
    }
    return experiment_config, result


def fixed_body_exposure_summary(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Compact reporting view; it contains anatomy-only min/max summaries."""

    totals: dict[int, dict[str, Any]] = {}
    for body in BODY_IDENTITIES:
        body_id = body["body_id"]
        values = [
            assignment
            for sample in result["samples"]
            for assignment in sample["assignments"]
            if assignment["body_id"] == body_id
        ]
        totals[body_id] = {
            **body,
            "sample_count": len(values),
            "column_overlap_fraction_min": min(
                item["column_overlap_fraction"] for item in values
            ),
            "column_overlap_fraction_max": max(
                item["column_overlap_fraction"] for item in values
            ),
            "structural_input_site_overlap_fraction_min": min(
                item["structural_input_site_overlap_fraction"] for item in values
            ),
            "structural_input_site_overlap_fraction_max": max(
                item["structural_input_site_overlap_fraction"] for item in values
            ),
        }
    return [totals[body_id] for body_id in BODY_IDS]
