"""Offline, model-neutral contract for the selected MaleCNS circuit."""

import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

from neurofly.malecns.errors import (
    MaleCNSValidationError,
    SnapshotIntegrityError,
)
from neurofly.malecns.models import (
    CANDIDATE,
    MALECNS_DATASET,
    NEUPRINT_ENDPOINT,
    CandidateDefinition,
    ConnectionRecord,
    NeuronRecord,
    PrimaryMetrics,
)
from neurofly.malecns.validation import (
    EXPECTED_ANNOTATIONS,
    EXPECTED_DNP01_IDENTITIES,
)

NEURON_FILENAME = "neurons.jsonl"
CONNECTION_FILENAME = "connections.jsonl"
MANIFEST_FILENAME = "manifest.json"
DATA_FILENAMES = (NEURON_FILENAME, CONNECTION_FILENAME)

NEURON_FIELDS = {
    "dataset",
    "body_id",
    "instance",
    "type",
    "status",
    "status_label",
    "superclass",
    "class",
    "soma_side",
    "soma_neuromere",
    "pre",
    "post",
    "upstream",
    "downstream",
    "predicted_nt",
    "predicted_nt_confidence",
    "consensus_nt",
    "dimorphism",
}
CONNECTION_FIELDS = {
    "dataset",
    "source_body_id",
    "target_body_id",
    "source_type",
    "target_type",
    "structural_weight",
}


@dataclass(frozen=True)
class ExperimentalBoundary:
    """NeuroFly's selection decision, not metadata supplied by MaleCNS."""

    sensory_side_types: tuple[str, ...]
    descending_readout_types: tuple[str, ...]
    provenance: str = "NeuroFly experimental design decision"


EXPERIMENTAL_BOUNDARY = ExperimentalBoundary(
    sensory_side_types=("LC4", "LPLC2"),
    descending_readout_types=("DNp01",),
)


@dataclass(frozen=True)
class SnapshotProvenance:
    """Where the derived snapshot came from; this is not an integrity claim."""

    source: str
    endpoint: str
    dataset: str
    acquired_at_utc: str
    neuprint_python_version: str


@dataclass(frozen=True)
class SnapshotIntegrity:
    """Verification state for local files, not proof of biological truth."""

    sha256_by_file: tuple[tuple[str, str], ...]
    sha256_verified: bool
    record_counts_verified: bool


@dataclass(frozen=True, order=True)
class TypePairSummary:
    source_type: str
    target_type: str
    chemical_edge_count: int
    structural_weight_sum: int


@dataclass(frozen=True)
class StructuralSummary:
    """Purely descriptive chemical-connectome counts."""

    neuron_counts_by_type: tuple[tuple[str, int], ...]
    total_neuron_count: int
    type_pairs: tuple[TypePairSummary, ...]
    total_chemical_edge_count: int
    total_structural_weight: int


@dataclass(frozen=True)
class CircuitContract:
    """Validated biological records plus explicit model-neutral metadata."""

    candidate: CandidateDefinition
    provenance: SnapshotProvenance
    integrity: SnapshotIntegrity
    boundary: ExperimentalBoundary
    neurons: tuple[NeuronRecord, ...]
    connections: tuple[ConnectionRecord, ...]
    source_manifest: Mapping[str, Any]
    node_index_by_body_id: Mapping[int, int] = field(init=False, repr=False)
    body_id_by_node_index: tuple[int, ...] = field(init=False)
    neurons_by_body_id: Mapping[int, NeuronRecord] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        body_ids = tuple(neuron.body_id for neuron in self.neurons)
        object.__setattr__(self, "body_id_by_node_index", body_ids)
        object.__setattr__(
            self,
            "node_index_by_body_id",
            MappingProxyType(
                {body_id: index for index, body_id in enumerate(body_ids)}
            ),
        )
        object.__setattr__(
            self,
            "neurons_by_body_id",
            MappingProxyType({neuron.body_id: neuron for neuron in self.neurons}),
        )

    def structural_summary(self) -> StructuralSummary:
        return summarize_structure(self.neurons, self.connections)


@dataclass(frozen=True)
class _SnapshotExpectations:
    neuron_counts: tuple[tuple[str, int], ...]
    connection_count: int
    total_structural_weight: int
    type_pairs: tuple[TypePairSummary, ...]
    primary: tuple[tuple[str, PrimaryMetrics], ...]


CURRENT_EXPECTATIONS = _SnapshotExpectations(
    neuron_counts=(("DNp01", 2), ("LC4", 126), ("LPLC2", 185)),
    connection_count=20_607,
    total_structural_weight=79_112,
    type_pairs=(
        TypePairSummary("DNp01", "DNp01", 2, 2),
        TypePairSummary("DNp01", "LC4", 32, 45),
        TypePairSummary("DNp01", "LPLC2", 8, 8),
        TypePairSummary("LC4", "DNp01", 126, 6_362),
        TypePairSummary("LC4", "LC4", 5_334, 18_392),
        TypePairSummary("LC4", "LPLC2", 306, 361),
        TypePairSummary("LPLC2", "DNp01", 185, 4_862),
        TypePairSummary("LPLC2", "LC4", 1_180, 2_902),
        TypePairSummary("LPLC2", "LPLC2", 13_434, 46_178),
    ),
    primary=(
        ("LC4", PrimaryMetrics(126, 126, 6_362)),
        ("LPLC2", PrimaryMetrics(185, 185, 4_862)),
    ),
)


def _fail(label: str, actual: object, expected: object) -> None:
    raise MaleCNSValidationError(
        f"Circuit contract mismatch for {label}: "
        f"actual={actual!r}, expected={expected!r}."
    )


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SnapshotIntegrityError(f"{label} must be a JSON object.")
    return value


def _require_string(
    value: Any, field_name: str, *, nullable: bool = False
) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str):
        raise SnapshotIntegrityError(f"{field_name} must be a string")
    return value


def _require_int(value: Any, field_name: str, *, nullable: bool = False) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        suffix = " or null" if nullable else ""
        raise SnapshotIntegrityError(f"{field_name} must be an integer{suffix}.")
    return value


def _require_fields(record: Mapping[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - record.keys())
    extra = sorted(record.keys() - expected)
    if missing or extra:
        raise SnapshotIntegrityError(
            f"Invalid {label} fields: missing={missing!r}, unexpected={extra!r}."
        )


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value}")


def _read_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_json_constant
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise SnapshotIntegrityError(f"Malformed {label}: {error}") from None
    return _require_mapping(value, label)


def _read_jsonl(path: Path, label: str) -> list[Mapping[str, Any]]:
    records = []
    try:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    raise SnapshotIntegrityError(
                        f"Malformed {label} at line {line_number}: blank line."
                    )
                try:
                    value = json.loads(line, parse_constant=_reject_json_constant)
                except (json.JSONDecodeError, ValueError) as error:
                    raise SnapshotIntegrityError(
                        f"Malformed {label} at line {line_number}: {error}"
                    ) from None
                records.append(_require_mapping(value, f"{label} line {line_number}"))
    except (OSError, UnicodeError) as error:
        raise SnapshotIntegrityError(f"Could not read {label}: {error}") from None
    return records


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise SnapshotIntegrityError(f"Could not read {path.name}: {error}") from None
    return digest.hexdigest()


def _parse_neuron(record: Mapping[str, Any], line_number: int) -> NeuronRecord:
    label = f"neuron record {line_number}"
    _require_fields(record, NEURON_FIELDS, label)
    confidence = record["predicted_nt_confidence"]
    if confidence is not None and (
        isinstance(confidence, bool) or not isinstance(confidence, (int, float))
    ):
        raise SnapshotIntegrityError(
            f"{label} predicted_nt_confidence must be numeric or null."
        )
    return NeuronRecord(
        dataset=_require_string(record["dataset"], f"{label} dataset"),
        body_id=_require_int(record["body_id"], f"{label} body_id"),
        instance=_require_string(
            record["instance"], f"{label} instance", nullable=True
        ),
        type=_require_string(record["type"], f"{label} type"),
        status=_require_string(record["status"], f"{label} status", nullable=True),
        status_label=_require_string(
            record["status_label"], f"{label} status_label", nullable=True
        ),
        superclass=_require_string(
            record["superclass"], f"{label} superclass", nullable=True
        ),
        class_=_require_string(record["class"], f"{label} class", nullable=True),
        soma_side=_require_string(
            record["soma_side"], f"{label} soma_side", nullable=True
        ),
        soma_neuromere=_require_string(
            record["soma_neuromere"], f"{label} soma_neuromere", nullable=True
        ),
        pre=_require_int(record["pre"], f"{label} pre", nullable=True),
        post=_require_int(record["post"], f"{label} post", nullable=True),
        upstream=_require_int(record["upstream"], f"{label} upstream", nullable=True),
        downstream=_require_int(
            record["downstream"], f"{label} downstream", nullable=True
        ),
        predicted_nt=_require_string(
            record["predicted_nt"], f"{label} predicted_nt", nullable=True
        ),
        predicted_nt_confidence=(None if confidence is None else float(confidence)),
        consensus_nt=_require_string(
            record["consensus_nt"], f"{label} consensus_nt", nullable=True
        ),
        dimorphism=_require_string(
            record["dimorphism"], f"{label} dimorphism", nullable=True
        ),
    )


def _parse_connection(record: Mapping[str, Any], line_number: int) -> ConnectionRecord:
    label = f"connection record {line_number}"
    _require_fields(record, CONNECTION_FIELDS, label)
    structural_weight = _require_int(
        record["structural_weight"], f"{label} structural_weight"
    )
    if structural_weight <= 0:
        raise SnapshotIntegrityError(
            f"{label} structural_weight must be a positive structural count."
        )
    return ConnectionRecord(
        dataset=_require_string(record["dataset"], f"{label} dataset"),
        source_body_id=_require_int(
            record["source_body_id"], f"{label} source_body_id"
        ),
        target_body_id=_require_int(
            record["target_body_id"], f"{label} target_body_id"
        ),
        source_type=_require_string(record["source_type"], f"{label} source_type"),
        target_type=_require_string(record["target_type"], f"{label} target_type"),
        structural_weight=structural_weight,
    )


def summarize_structure(
    neurons: tuple[NeuronRecord, ...], connections: tuple[ConnectionRecord, ...]
) -> StructuralSummary:
    neuron_counts = Counter(neuron.type for neuron in neurons)
    edge_counts: Counter[tuple[str, str]] = Counter()
    weight_sums: Counter[tuple[str, str]] = Counter()
    for edge in connections:
        pair = (edge.source_type, edge.target_type)
        edge_counts[pair] += 1
        weight_sums[pair] += edge.structural_weight
    pairs = tuple(
        TypePairSummary(
            source, target, edge_counts[(source, target)], weight_sums[(source, target)]
        )
        for source, target in sorted(edge_counts)
    )
    return StructuralSummary(
        neuron_counts_by_type=tuple(
            (neuron_type, neuron_counts[neuron_type])
            for neuron_type in sorted(neuron_counts)
        ),
        total_neuron_count=len(neurons),
        type_pairs=pairs,
        total_chemical_edge_count=len(connections),
        total_structural_weight=sum(edge.structural_weight for edge in connections),
    )


def _validate_content(
    neurons: tuple[NeuronRecord, ...],
    connections: tuple[ConnectionRecord, ...],
    expectations: _SnapshotExpectations,
) -> StructuralSummary:
    body_ids = [neuron.body_id for neuron in neurons]
    if len(body_ids) != len(set(body_ids)):
        raise MaleCNSValidationError("Duplicate neuron body ID in circuit snapshot.")

    neurons_by_body = {neuron.body_id: neuron for neuron in neurons}
    identities = {
        neuron.body_id: neuron.instance for neuron in neurons if neuron.type == "DNp01"
    }
    if identities != EXPECTED_DNP01_IDENTITIES:
        _fail("DNp01 identities", identities, EXPECTED_DNP01_IDENTITIES)

    for neuron_type, fields in EXPECTED_ANNOTATIONS.items():
        population = [neuron for neuron in neurons if neuron.type == neuron_type]
        for field_name, expected in fields.items():
            actual = {getattr(neuron, field_name) for neuron in population}
            if actual != expected:
                _fail(f"{neuron_type} {field_name}", actual, expected)

    seen_edges: set[tuple[int, int]] = set()
    for edge in connections:
        source = neurons_by_body.get(edge.source_body_id)
        target = neurons_by_body.get(edge.target_body_id)
        if source is None or target is None:
            raise MaleCNSValidationError(
                "Chemical connection references a body outside the selected neurons: "
                f"{edge.source_body_id} -> {edge.target_body_id}."
            )
        if edge.source_type != source.type:
            raise MaleCNSValidationError(
                f"Source type mismatch for body {edge.source_body_id}: "
                f"edge={edge.source_type!r}, neuron={source.type!r}."
            )
        if edge.target_type != target.type:
            raise MaleCNSValidationError(
                f"Target type mismatch for body {edge.target_body_id}: "
                f"edge={edge.target_type!r}, neuron={target.type!r}."
            )
        pair = (edge.source_body_id, edge.target_body_id)
        if pair in seen_edges:
            raise MaleCNSValidationError(
                f"Duplicate body-level ConnectsTo relationship: {pair[0]} -> {pair[1]}."
            )
        seen_edges.add(pair)

    datasets = {record.dataset for record in neurons} | {
        record.dataset for record in connections
    }
    if datasets != {MALECNS_DATASET}:
        _fail("record datasets", datasets, {MALECNS_DATASET})

    summary = summarize_structure(neurons, connections)
    for source_type, expected in expectations.primary:
        edges = [
            edge
            for edge in connections
            if edge.source_type == source_type and edge.target_type == "DNp01"
        ]
        actual = PrimaryMetrics(
            edge_count=len(edges),
            distinct_source_count=len({edge.source_body_id for edge in edges}),
            structural_weight_sum=sum(edge.structural_weight for edge in edges),
        )
        if actual != expected:
            _fail(f"{source_type} -> DNp01", actual, expected)

    if summary.neuron_counts_by_type != expectations.neuron_counts:
        _fail(
            "neuron counts by type",
            summary.neuron_counts_by_type,
            expectations.neuron_counts,
        )
    if summary.total_chemical_edge_count != expectations.connection_count:
        _fail(
            "chemical edge count",
            summary.total_chemical_edge_count,
            expectations.connection_count,
        )
    if summary.total_structural_weight != expectations.total_structural_weight:
        _fail(
            "total structural weight",
            summary.total_structural_weight,
            expectations.total_structural_weight,
        )
    if summary.type_pairs != expectations.type_pairs:
        _fail(
            "type-pair structural summary", summary.type_pairs, expectations.type_pairs
        )

    return summary


def _freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _freeze_json(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _load_circuit_contract(
    snapshot_path: Path,
    expectations: _SnapshotExpectations,
) -> CircuitContract:
    path = Path(snapshot_path)
    if not path.is_dir():
        raise SnapshotIntegrityError(f"Snapshot directory does not exist: {path}")
    files = {name: path / name for name in (*DATA_FILENAMES, MANIFEST_FILENAME)}
    missing_files = [
        name for name, file_path in files.items() if not file_path.is_file()
    ]
    if missing_files:
        raise SnapshotIntegrityError(
            f"Snapshot is missing required files: {', '.join(sorted(missing_files))}."
        )

    manifest = _read_json(files[MANIFEST_FILENAME], "manifest")
    candidate = _require_mapping(manifest.get("candidate"), "manifest candidate")
    actual_candidate = (
        _require_string(candidate.get("identifier"), "candidate identifier"),
        _require_int(candidate.get("version"), "candidate version"),
    )
    expected_candidate = (CANDIDATE.identifier, CANDIDATE.version)
    if actual_candidate != expected_candidate:
        raise SnapshotIntegrityError(
            f"Unsupported candidate: actual={actual_candidate!r}, "
            f"supported={expected_candidate!r}."
        )
    selected_types = candidate.get("selected_neuron_types")
    if not isinstance(selected_types, list) or not all(
        isinstance(value, str) for value in selected_types
    ):
        raise SnapshotIntegrityError(
            "Manifest selected_neuron_types must be a JSON array of strings."
        )
    if tuple(selected_types) != CANDIDATE.neuron_types:
        raise SnapshotIntegrityError("Manifest selected neuron types are unsupported.")
    manifest_dataset = _require_string(manifest.get("dataset"), "manifest dataset")
    if manifest_dataset != MALECNS_DATASET:
        raise SnapshotIntegrityError(
            f"Wrong dataset: actual={manifest_dataset!r}, expected={MALECNS_DATASET!r}."
        )
    if manifest.get("structural_weight_source") != "neuPrint ConnectsTo.weight":
        raise SnapshotIntegrityError(
            "Manifest structural-weight source is unsupported."
        )
    if manifest.get("structural_weight_is_physiological_coupling") is not False:
        raise SnapshotIntegrityError(
            "Manifest must identify structural weight as non-physiological."
        )

    expected_neuron_count = sum(count for _, count in expectations.neuron_counts)
    manifest_neuron_count = _require_int(
        manifest.get("neuron_count"), "manifest neuron_count"
    )
    if manifest_neuron_count != expected_neuron_count:
        raise SnapshotIntegrityError(
            "Manifest neuron count mismatch: "
            f"actual={manifest_neuron_count!r}, "
            f"expected={expected_neuron_count}."
        )
    manifest_connection_count = _require_int(
        manifest.get("induced_connection_count"),
        "manifest induced_connection_count",
    )
    if manifest_connection_count != expectations.connection_count:
        raise SnapshotIntegrityError(
            "Manifest connection count mismatch: "
            f"actual={manifest_connection_count!r}, "
            f"expected={expectations.connection_count}."
        )

    manifest_hashes = _require_mapping(manifest.get("sha256"), "manifest sha256")
    if set(manifest_hashes) != set(DATA_FILENAMES):
        raise SnapshotIntegrityError(
            "Manifest sha256 must list exactly neurons.jsonl and connections.jsonl."
        )
    actual_hashes = tuple((name, _sha256(files[name])) for name in DATA_FILENAMES)
    for name, actual_hash in actual_hashes:
        if manifest_hashes[name] != actual_hash:
            raise SnapshotIntegrityError(
                f"SHA-256 mismatch for {name}: local file does not match manifest."
            )

    neuron_rows = _read_jsonl(files[NEURON_FILENAME], NEURON_FILENAME)
    connection_rows = _read_jsonl(files[CONNECTION_FILENAME], CONNECTION_FILENAME)
    if len(neuron_rows) != manifest["neuron_count"]:
        raise SnapshotIntegrityError(
            f"{NEURON_FILENAME} record count does not match manifest."
        )
    if len(connection_rows) != manifest["induced_connection_count"]:
        raise SnapshotIntegrityError(
            f"{CONNECTION_FILENAME} record count does not match manifest."
        )

    neurons = tuple(
        sorted(
            (_parse_neuron(row, index) for index, row in enumerate(neuron_rows, 1)),
            key=lambda neuron: neuron.body_id,
        )
    )
    connections = tuple(
        sorted(
            (
                _parse_connection(row, index)
                for index, row in enumerate(connection_rows, 1)
            ),
            key=lambda edge: (
                edge.source_body_id,
                edge.target_body_id,
                edge.source_type,
                edge.target_type,
            ),
        )
    )
    _validate_content(neurons, connections, expectations)

    provenance = SnapshotProvenance(
        source=_require_string(manifest.get("source"), "manifest source"),
        endpoint=_require_string(manifest.get("endpoint"), "manifest endpoint"),
        dataset=MALECNS_DATASET,
        acquired_at_utc=_require_string(
            manifest.get("acquired_at_utc"), "manifest acquired_at_utc"
        ),
        neuprint_python_version=_require_string(
            manifest.get("neuprint_python_version"),
            "manifest neuprint_python_version",
        ),
    )
    if provenance.endpoint != NEUPRINT_ENDPOINT:
        raise SnapshotIntegrityError(f"Wrong source endpoint: {provenance.endpoint!r}.")
    integrity = SnapshotIntegrity(
        sha256_by_file=actual_hashes,
        sha256_verified=True,
        record_counts_verified=True,
    )
    return CircuitContract(
        candidate=CANDIDATE,
        provenance=provenance,
        integrity=integrity,
        boundary=EXPERIMENTAL_BOUNDARY,
        neurons=neurons,
        connections=connections,
        source_manifest=_freeze_json(manifest),
    )


def load_circuit_contract(snapshot_path: Path) -> CircuitContract:
    """Load and fully validate the supported circuit snapshot without network access."""
    return _load_circuit_contract(Path(snapshot_path), CURRENT_EXPECTATIONS)
