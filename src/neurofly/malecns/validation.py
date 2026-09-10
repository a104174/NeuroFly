"""Scientific validation for the pinned MaleCNS v1.0 candidate."""

from collections import Counter

from neurofly.malecns.errors import MaleCNSValidationError
from neurofly.malecns.models import (
    CANDIDATE,
    CandidateSnapshot,
    PrimaryMetrics,
    ValidationReport,
)

EXPECTED_COUNTS = {"LC4": 126, "LPLC2": 185, "DNp01": 2}
EXPECTED_DNP01_IDENTITIES = {10010: "DNp01(GF)_L", 10001: "DNp01(GF)_R"}
EXPECTED_PRIMARY = {
    "LC4": PrimaryMetrics(126, 126, 6362),
    "LPLC2": PrimaryMetrics(185, 185, 4862),
}
EXPECTED_ANNOTATIONS = {
    "LC4": {
        "status": {"Traced"},
        "superclass": {"visual_projection"},
        "predicted_nt": {"acetylcholine"},
        "consensus_nt": {"acetylcholine"},
    },
    "LPLC2": {
        "status": {"Traced"},
        "superclass": {"visual_projection"},
        "predicted_nt": {"acetylcholine"},
        "consensus_nt": {"acetylcholine"},
    },
    "DNp01": {
        "status": {"Traced"},
        "superclass": {"descending_neuron"},
        "predicted_nt": {"acetylcholine"},
        "consensus_nt": {"acetylcholine"},
    },
}


def _fail(label: str, actual: object, expected: object) -> None:
    raise MaleCNSValidationError(
        f"Pinned MaleCNS invariant mismatch for {label}: "
        f"actual={actual!r}, expected={expected!r}."
    )


def _primary_metrics(snapshot: CandidateSnapshot, source_type: str) -> PrimaryMetrics:
    edges = [
        edge
        for edge in snapshot.connections
        if edge.source_type == source_type and edge.target_type == "DNp01"
    ]
    return PrimaryMetrics(
        edge_count=len(edges),
        distinct_source_count=len({edge.source_body_id for edge in edges}),
        structural_weight_sum=sum(edge.structural_weight for edge in edges),
    )


def validate_snapshot(snapshot: CandidateSnapshot) -> ValidationReport:
    """Fail if acquired data differs from manually verified v1.0 invariants."""
    if snapshot.candidate != CANDIDATE:
        _fail("candidate definition", snapshot.candidate, CANDIDATE)

    datasets = {record.dataset for record in snapshot.neurons} | {
        record.dataset for record in snapshot.connections
    }
    if datasets != {CANDIDATE.dataset}:
        _fail("record datasets", datasets, {CANDIDATE.dataset})

    body_ids = [neuron.body_id for neuron in snapshot.neurons]
    if len(body_ids) != len(set(body_ids)):
        raise MaleCNSValidationError("Duplicate selected neuron body IDs found.")

    counts = Counter(neuron.type for neuron in snapshot.neurons)
    actual_counts = {kind: counts[kind] for kind in CANDIDATE.neuron_types}
    if actual_counts != EXPECTED_COUNTS:
        _fail("selected population counts", actual_counts, EXPECTED_COUNTS)
    if len(body_ids) != 313:
        _fail("total selected unique bodies", len(body_ids), 313)

    for neuron_type, fields in EXPECTED_ANNOTATIONS.items():
        population = [
            neuron for neuron in snapshot.neurons if neuron.type == neuron_type
        ]
        for field, expected in fields.items():
            actual = {getattr(neuron, field) for neuron in population}
            if actual != expected:
                _fail(f"{neuron_type} {field}", actual, expected)

    identities = {
        neuron.body_id: neuron.instance
        for neuron in snapshot.neurons
        if neuron.type == "DNp01"
    }
    if identities != EXPECTED_DNP01_IDENTITIES:
        _fail("DNp01 identities", identities, EXPECTED_DNP01_IDENTITIES)

    if not snapshot.connections:
        raise MaleCNSValidationError("The complete induced ConnectsTo graph is empty.")
    selected = set(body_ids)
    invalid_endpoints = [
        (edge.source_body_id, edge.target_body_id)
        for edge in snapshot.connections
        if edge.source_body_id not in selected or edge.target_body_id not in selected
    ]
    if invalid_endpoints:
        raise MaleCNSValidationError(
            "Induced connection data contains endpoints outside the selected bodies."
        )

    primary = {
        source_type: _primary_metrics(snapshot, source_type)
        for source_type in ("LC4", "LPLC2")
    }
    for source_type, expected in EXPECTED_PRIMARY.items():
        if primary[source_type] != expected:
            _fail(f"{source_type} -> DNp01", primary[source_type], expected)

    return ValidationReport(
        neuron_counts=actual_counts,
        total_neuron_count=len(body_ids),
        induced_connection_count=len(snapshot.connections),
        lc4_to_dnp01=primary["LC4"],
        lplc2_to_dnp01=primary["LPLC2"],
    )
