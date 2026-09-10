"""Model-neutral body-to-optic-column input topology for Phase 1E.

This module deliberately stops at anatomical column-space counts.  It does not
contain visual-angle coordinates, physiological weights, or neural-model state.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from numbers import Integral, Real
from typing import Any, Callable

from neurofly.malecns.errors import (
    MaleCNSAccessError,
    MaleCNSDataError,
    MaleCNSValidationError,
)
from neurofly.malecns.models import (
    MALECNS_DATASET,
    NEUPRINT_ENDPOINT,
    NeuronRecord,
)

COLUMN_SCHEMA_VERSION = "body_column_input_v1"
COLUMN_INPUT_FILENAME = "column_inputs.jsonl"
COLUMN_SUMMARY_FILENAME = "column_body_summaries.jsonl"
COLUMN_MANIFEST_FILENAME = "column_manifest.json"
VISUAL_TERRITORY_RULE_ID = "matching_side_optic_primary_post_v1"
AGGREGATION_METHOD_ID = "server_primary_optic_group_v1"
VISUAL_TYPES = ("LC4", "LPLC2")
FROZEN_PHASE_1D_BODY_IDS = (
    35616,
    18432,
    524899,
    30087,
    16138,
    23098,
    19954,
    19260,
    20329,
    18936,
    524366,
    30893,
    26915,
    21808,
    19034,
    20471,
)
VALID_OPTIC_NEUROPILS = frozenset({"AME", "LA", "ME", "LO", "LOP", "Optic-unspecified"})
_COLUMN_KEY_RE = re.compile(
    r"^(?P<neuropil>ME|LO|LOP)_(?P<side>[LR])_col_"
    r"(?P<hex1>[0-9]+)_(?P<hex2>[0-9]+)$"
)


def _records(table: Any) -> list[Mapping[str, Any]]:
    if hasattr(table, "to_dict"):
        records = table.to_dict("records")
    else:
        records = list(table)
    if not all(isinstance(row, Mapping) for row in records):
        raise MaleCNSDataError("Column query rows must be mappings.")
    return records


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, Real) and not isinstance(value, Integral):
        return math.isnan(float(value))
    return type(value).__name__ in {"NAType", "NaTType"}


def _int_value(value: Any, field_name: str, *, nullable: bool = False) -> int | None:
    if _missing(value):
        if nullable:
            return None
        raise MaleCNSDataError(f"{field_name} must be an integer.")
    if isinstance(value, bool):
        raise MaleCNSDataError(f"{field_name} must be an integer.")
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real) and math.isfinite(float(value)):
        numeric = float(value)
        if numeric.is_integer():
            return int(numeric)
    raise MaleCNSDataError(f"{field_name} must be an integer.")


def _positive_count(value: Any, field_name: str) -> int:
    result = _int_value(value, field_name)
    assert result is not None
    if result <= 0:
        raise MaleCNSDataError(f"{field_name} must be a positive integer.")
    return result


def _side(value: Any, field_name: str) -> str:
    if value not in {"L", "R"}:
        raise MaleCNSDataError(f"{field_name} must be 'L' or 'R'.")
    return str(value)


def _roi_neuropil(roi: str, side: str) -> str:
    suffix = f"({side})"
    if not roi.endswith(suffix):
        raise MaleCNSDataError(
            f"Primary ROI {roi!r} does not match body side {side!r}."
        )
    neuropil = roi[: -len(suffix)]
    if neuropil not in VALID_OPTIC_NEUROPILS:
        raise MaleCNSDataError(f"Unsupported optic neuropil {neuropil!r}.")
    return neuropil


def _column_key_parts(value: str) -> tuple[str, str, int, int] | None:
    match = _COLUMN_KEY_RE.fullmatch(value)
    if match is None:
        return None
    return (
        match.group("neuropil"),
        match.group("side"),
        int(match.group("hex1")),
        int(match.group("hex2")),
    )


def canonical_column_id(neuropil: str, side: str, hex1: int, hex2: int) -> str:
    """Return the direct MaleCNS ROI-style identifier for one sparse entry."""
    if neuropil not in {"ME", "LO", "LOP"}:
        raise MaleCNSDataError(
            f"Assigned sparse entries require a column neuropil, got {neuropil!r}."
        )
    _side(side, "eye_side")
    if not isinstance(hex1, int) or isinstance(hex1, bool) or hex1 < 0:
        raise MaleCNSDataError("ol_hex1 must be a non-negative integer.")
    if not isinstance(hex2, int) or isinstance(hex2, bool) or hex2 < 0:
        raise MaleCNSDataError("ol_hex2 must be a non-negative integer.")
    return f"{neuropil}_{side}_col_{hex1:02d}_{hex2:02d}"


@dataclass(frozen=True, order=True)
class ColumnInputRecord:
    """One sparse body/neuropil/hex input-site count."""

    body_id: int
    neuron_type: str
    eye_side: str
    neuropil: str
    ol_hex1: int
    ol_hex2: int
    input_count: int

    @property
    def column_id(self) -> str:
        return canonical_column_id(
            self.neuropil, self.eye_side, self.ol_hex1, self.ol_hex2
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "column_id": self.column_id,
            "eye_side": self.eye_side,
            "input_count": self.input_count,
            "neuron_type": self.neuron_type,
            "neuropil": self.neuropil,
            "ol_hex1": self.ol_hex1,
            "ol_hex2": self.ol_hex2,
        }


@dataclass(frozen=True, order=True)
class BodyColumnSummary:
    """Per-body accounting for relevant, assigned, and missing input sites."""

    body_id: int
    neuron_type: str
    eye_side: str
    relevant_input_count: int
    assigned_input_count: int
    unassigned_input_count: int
    assignment_fraction: float
    distinct_occupied_column_count: int
    malformed_hex_count: int = 0
    multiple_column_count: int = 0
    unknown_column_count: int = 0
    neuropil_input_counts: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    neuropil_assigned_counts: tuple[tuple[str, int], ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "assigned_input_count": self.assigned_input_count,
            "assignment_fraction": self.assignment_fraction,
            "body_id": self.body_id,
            "distinct_occupied_column_count": self.distinct_occupied_column_count,
            "eye_side": self.eye_side,
            "malformed_hex_count": self.malformed_hex_count,
            "multiple_column_count": self.multiple_column_count,
            "neuron_type": self.neuron_type,
            "neuropil_assigned_counts": dict(self.neuropil_assigned_counts),
            "neuropil_input_counts": dict(self.neuropil_input_counts),
            "relevant_input_count": self.relevant_input_count,
            "unassigned_input_count": self.unassigned_input_count,
            "unknown_column_count": self.unknown_column_count,
        }


@dataclass(frozen=True)
class BodyColumnInputContract:
    """Immutable, model-neutral column-space data linked by body ID."""

    schema_version: str
    candidate_identifier: str
    candidate_version: int
    dataset: str
    endpoint: str
    acquired_at_utc: str
    source_snapshot: str
    visual_territory_rule: str
    aggregation_method: str
    records: tuple[ColumnInputRecord, ...]
    summaries: tuple[BodyColumnSummary, ...]
    query_counts: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    provenance: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", tuple(self.records))
        object.__setattr__(self, "summaries", tuple(self.summaries))
        object.__setattr__(self, "query_counts", tuple(self.query_counts))
        object.__setattr__(self, "provenance", tuple(self.provenance))

    @property
    def body_ids(self) -> tuple[int, ...]:
        return tuple(summary.body_id for summary in self.summaries)

    def descriptive_summary(self) -> dict[str, Any]:
        by_type: dict[str, list[BodyColumnSummary]] = defaultdict(list)
        for summary in self.summaries:
            by_type[summary.neuron_type].append(summary)
        result: dict[str, Any] = {
            "body_count": len(self.summaries),
            "sparse_record_count": len(self.records),
            "relevant_input_count": sum(
                summary.relevant_input_count for summary in self.summaries
            ),
            "assigned_input_count": sum(
                summary.assigned_input_count for summary in self.summaries
            ),
            "unassigned_input_count": sum(
                summary.unassigned_input_count for summary in self.summaries
            ),
            "by_type": {},
        }
        for neuron_type in sorted(by_type):
            summaries = by_type[neuron_type]
            relevant = sum(item.relevant_input_count for item in summaries)
            assigned = sum(item.assigned_input_count for item in summaries)
            neuropils: Counter[str] = Counter()
            for item in summaries:
                neuropils.update(dict(item.neuropil_input_counts))
            result["by_type"][neuron_type] = {
                "body_count": len(summaries),
                "relevant_input_count": relevant,
                "assigned_input_count": assigned,
                "unassigned_input_count": sum(
                    item.unassigned_input_count for item in summaries
                ),
                "assignment_fraction": (assigned / relevant if relevant else 0.0),
                "occupied_column_count_min": min(
                    item.distinct_occupied_column_count for item in summaries
                ),
                "occupied_column_count_max": max(
                    item.distinct_occupied_column_count for item in summaries
                ),
                "neuropil_input_counts": dict(sorted(neuropils.items())),
            }
        return result


@dataclass(frozen=True)
class AggregateSynapseRow:
    """Normalized server-side grouped row, before sparse contract derivation."""

    body_id: int
    neuron_type: str
    eye_side: str
    primary_roi: str
    ol_hex1: int | None
    ol_hex2: int | None
    column_rois: tuple[str, ...]
    input_count: int


@dataclass(frozen=True)
class RawInputObservation:
    """Small raw-query observation used only for method-equivalence validation."""

    sparse_counts: Mapping[tuple[int, str, str, str, int, int], int]
    per_body: Mapping[int, tuple[int, int, int]]


def _candidate_visual_neurons(
    circuit_contract: Any,
) -> tuple[NeuronRecord, ...]:
    neurons = tuple(
        neuron for neuron in circuit_contract.neurons if neuron.type in VISUAL_TYPES
    )
    return tuple(sorted(neurons, key=lambda neuron: neuron.body_id))


def _descendants(node: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    name = node.get("name")
    if isinstance(name, str):
        names.add(name)
    for child in node.get("children", ()):
        if isinstance(child, Mapping):
            names.update(_descendants(child))
    return names


def optic_primary_rois(client: Any) -> dict[str, tuple[str, ...]]:
    """Get matching-side primary optic ROIs from live neuPrint metadata."""
    try:
        hierarchy = client.meta["roiHierarchy"]
        primary = set(client.primary_rois)
    except Exception:
        raise MaleCNSAccessError(
            "MaleCNS ROI metadata did not expose the primary optic hierarchy."
        ) from None

    nodes: dict[str, Mapping[str, Any]] = {}

    def collect(node: Mapping[str, Any]) -> None:
        name = node.get("name")
        if isinstance(name, str):
            nodes[name] = node
        for child in node.get("children", ()):
            if isinstance(child, Mapping):
                collect(child)

    if not isinstance(hierarchy, Mapping):
        raise MaleCNSAccessError("MaleCNS ROI hierarchy has an invalid schema.")
    collect(hierarchy)

    result: dict[str, tuple[str, ...]] = {}
    for side in ("L", "R"):
        root = nodes.get(f"Optic({side})")
        if root is None:
            raise MaleCNSAccessError(f"Missing Optic({side}) ROI hierarchy.")
        rois = tuple(sorted(_descendants(root) & primary))
        if not rois:
            raise MaleCNSAccessError(f"No primary Optic({side}) ROIs were found.")
        result[side] = rois
    return result


def _cypher_quote(value: str) -> str:
    return value.replace("`", "``")


def identity_query(body_ids: Iterable[int]) -> str:
    ids = sorted({int(body_id) for body_id in body_ids})
    if not ids:
        raise MaleCNSDataError("At least one body ID is required.")
    joined = ", ".join(str(body_id) for body_id in ids)
    return f"""
MATCH (n:Neuron)
WHERE n.bodyId IN [{joined}]
RETURN n.bodyId AS bodyId, n.instance AS instance, n.type AS type,
       n.status AS status, n.superclass AS superclass, n.somaSide AS somaSide
ORDER BY n.bodyId
""".strip()


def aggregate_query(
    body_ids: Iterable[int],
    primary_rois_by_side: Mapping[str, Sequence[str]],
) -> str:
    ids = sorted({int(body_id) for body_id in body_ids})
    if not ids:
        raise MaleCNSDataError("At least one body ID is required.")
    rois = sorted(
        set(primary_rois_by_side.get("L", ())) | set(primary_rois_by_side.get("R", ()))
    )
    if not rois:
        raise MaleCNSDataError("At least one primary optic ROI is required.")
    case_parts = " ".join(
        f"WHEN s.`{_cypher_quote(roi)}` = true THEN '{roi}'" for roi in rois
    )
    joined = ", ".join(str(body_id) for body_id in ids)
    return f"""
MATCH (n:Neuron)-[:Contains]->(:SynapseSet)-[:Contains]->(s:Synapse)
WHERE n.bodyId IN [{joined}] AND s.type = 'post'
WITH DISTINCT n, s
WITH n, s, CASE {case_parts} ELSE null END AS primaryRoi,
     [k IN keys(s) WHERE k CONTAINS '_col_'] AS columnRois
WHERE primaryRoi IS NOT NULL
RETURN n.bodyId AS bodyId, n.type AS neuronType, n.somaSide AS somaSide,
       primaryRoi, s.olHex1 AS olHex1, s.olHex2 AS olHex2,
       columnRois, count(s) AS inputCount
ORDER BY bodyId, primaryRoi, olHex1, olHex2, columnRois
""".strip()


def normalize_aggregate_rows(
    rows: Iterable[Mapping[str, Any]] | Any,
) -> tuple[AggregateSynapseRow, ...]:
    normalized: list[AggregateSynapseRow] = []
    for index, row in enumerate(_records(rows), start=1):
        required = {
            "bodyId",
            "neuronType",
            "somaSide",
            "primaryRoi",
            "olHex1",
            "olHex2",
            "columnRois",
            "inputCount",
        }
        missing = sorted(required - row.keys())
        if missing:
            raise MaleCNSDataError(
                f"Aggregate row {index} is missing columns: {', '.join(missing)}"
            )
        column_rois = row["columnRois"]
        if column_rois is None:
            column_rois = ()
        if isinstance(column_rois, str) or not isinstance(column_rois, Sequence):
            raise MaleCNSDataError(f"Aggregate row {index} columnRois is invalid.")
        if not all(isinstance(value, str) for value in column_rois):
            raise MaleCNSDataError(f"Aggregate row {index} columnRois is invalid.")
        normalized.append(
            AggregateSynapseRow(
                body_id=_int_value(row["bodyId"], f"row {index} bodyId"),
                neuron_type=str(row["neuronType"]),
                eye_side=_side(row["somaSide"], f"row {index} somaSide"),
                primary_roi=str(row["primaryRoi"]),
                ol_hex1=_int_value(row["olHex1"], f"row {index} olHex1", nullable=True),
                ol_hex2=_int_value(row["olHex2"], f"row {index} olHex2", nullable=True),
                column_rois=tuple(sorted(set(column_rois))),
                input_count=_positive_count(
                    row["inputCount"], f"row {index} inputCount"
                ),
            )
        )
    return tuple(normalized)


def _identity_rows(
    rows: Iterable[Mapping[str, Any]] | Any,
) -> dict[int, Mapping[str, Any]]:
    result: dict[int, Mapping[str, Any]] = {}
    for row in _records(rows):
        body_id = _int_value(row.get("bodyId"), "identity bodyId")
        if body_id in result:
            raise MaleCNSValidationError(f"Duplicate live identity for body {body_id}.")
        result[body_id] = row
    return result


def validate_live_identities(
    rows: Iterable[Mapping[str, Any]] | Any,
    circuit_contract: Any,
) -> None:
    """Require exact live identity agreement for all visual contract bodies."""
    expected = {
        neuron.body_id: neuron for neuron in _candidate_visual_neurons(circuit_contract)
    }
    actual = _identity_rows(rows)
    if set(actual) != set(expected):
        raise MaleCNSValidationError(
            "Live visual body IDs differ from the CircuitContract: "
            f"missing={sorted(set(expected) - set(actual))}, "
            f"unexpected={sorted(set(actual) - set(expected))}."
        )
    for body_id, neuron in expected.items():
        row = actual[body_id]
        checks = {
            "type": row.get("type"),
            "instance": row.get("instance"),
            "somaSide": row.get("somaSide"),
            "status": row.get("status"),
            "superclass": row.get("superclass"),
        }
        expected_values = {
            "type": neuron.type,
            "instance": neuron.instance,
            "somaSide": neuron.soma_side,
            "status": neuron.status,
            "superclass": neuron.superclass,
        }
        if checks != expected_values:
            raise MaleCNSValidationError(
                f"Live identity mismatch for body {body_id}: "
                f"actual={checks!r}, expected={expected_values!r}."
            )


def _matching_rois(
    primary_rois_by_side: Mapping[str, Sequence[str]], side: str
) -> set[str]:
    return set(primary_rois_by_side.get(side, ()))


def build_column_contract(
    rows: Iterable[Mapping[str, Any]] | Any,
    circuit_contract: Any,
    primary_rois_by_side: Mapping[str, Sequence[str]],
    *,
    acquired_at_utc: str | None = None,
    source_snapshot: str = "data/derived/malecns/looming_giant_fiber_v1",
    query_counts: Mapping[str, int] | None = None,
    provenance: Mapping[str, str] | None = None,
    expected_population: bool = True,
) -> BodyColumnInputContract:
    """Build and validate the sparse contract from grouped live rows."""
    visual_neurons = _candidate_visual_neurons(circuit_contract)
    expected = {neuron.body_id: neuron for neuron in visual_neurons}
    grouped_rows = normalize_aggregate_rows(rows)
    sparse: dict[tuple[int, str, str, str, int, int], int] = defaultdict(int)
    totals: dict[int, int] = Counter()
    assigned_totals: dict[int, int] = Counter()
    malformed_totals: dict[int, int] = Counter()
    multiple_totals: dict[int, int] = Counter()
    unknown_totals: dict[int, int] = Counter()
    neuropil_totals: dict[int, Counter[str]] = defaultdict(Counter)
    neuropil_assigned: dict[int, Counter[str]] = defaultdict(Counter)

    for row in grouped_rows:
        neuron = expected.get(row.body_id)
        if neuron is None:
            raise MaleCNSValidationError(
                f"Aggregate row references non-visual or unknown body {row.body_id}."
            )
        if row.neuron_type != neuron.type or row.eye_side != neuron.soma_side:
            raise MaleCNSValidationError(
                f"Aggregate identity mismatch for body {row.body_id}."
            )
        if row.primary_roi not in _matching_rois(primary_rois_by_side, row.eye_side):
            raise MaleCNSValidationError(
                f"Aggregate row has an invalid matching-side ROI: {row.primary_roi!r}."
            )
        neuropil = _roi_neuropil(row.primary_roi, row.eye_side)
        count = row.input_count
        totals[row.body_id] += count
        neuropil_totals[row.body_id][neuropil] += count

        has_hex1 = row.ol_hex1 is not None
        has_hex2 = row.ol_hex2 is not None
        if has_hex1 != has_hex2:
            malformed_totals[row.body_id] += count
            continue
        if not has_hex1:
            continue

        if len(row.column_rois) != 1:
            if len(row.column_rois) > 1:
                multiple_totals[row.body_id] += count
            else:
                unknown_totals[row.body_id] += count
            continue
        parts = _column_key_parts(row.column_rois[0])
        if parts is None:
            unknown_totals[row.body_id] += count
            continue
        key_neuropil, key_side, key_hex1, key_hex2 = parts
        if (
            key_side != row.eye_side
            or key_neuropil != neuropil
            or key_hex1 != row.ol_hex1
            or key_hex2 != row.ol_hex2
        ):
            unknown_totals[row.body_id] += count
            continue
        key = (
            row.body_id,
            neuron.type or "",
            row.eye_side,
            neuropil,
            row.ol_hex1,
            row.ol_hex2,
        )
        sparse[key] += count
        assigned_totals[row.body_id] += count
        neuropil_assigned[row.body_id][neuropil] += count

    summaries: list[BodyColumnSummary] = []
    for neuron in visual_neurons:
        body_id = neuron.body_id
        relevant = totals.get(body_id, 0)
        assigned = assigned_totals.get(body_id, 0)
        malformed = malformed_totals.get(body_id, 0)
        multiple = multiple_totals.get(body_id, 0)
        unknown = unknown_totals.get(body_id, 0)
        unassigned = relevant - assigned
        if unassigned < 0:
            raise MaleCNSValidationError(
                f"Assigned input count exceeds relevant count for body {body_id}."
            )
        body_records = [key for key in sparse if key[0] == body_id]
        summaries.append(
            BodyColumnSummary(
                body_id=body_id,
                neuron_type=neuron.type or "",
                eye_side=neuron.soma_side or "",
                relevant_input_count=relevant,
                assigned_input_count=assigned,
                unassigned_input_count=unassigned,
                assignment_fraction=(assigned / relevant if relevant else 0.0),
                distinct_occupied_column_count=len(body_records),
                malformed_hex_count=malformed,
                multiple_column_count=multiple,
                unknown_column_count=unknown,
                neuropil_input_counts=tuple(sorted(neuropil_totals[body_id].items())),
                neuropil_assigned_counts=tuple(
                    sorted(neuropil_assigned[body_id].items())
                ),
            )
        )

    candidate = circuit_contract.candidate
    contract = BodyColumnInputContract(
        schema_version=COLUMN_SCHEMA_VERSION,
        candidate_identifier=candidate.identifier,
        candidate_version=candidate.version,
        dataset=candidate.dataset,
        endpoint=NEUPRINT_ENDPOINT,
        acquired_at_utc=acquired_at_utc or datetime.now(UTC).isoformat(),
        source_snapshot=source_snapshot,
        visual_territory_rule=VISUAL_TERRITORY_RULE_ID,
        aggregation_method=AGGREGATION_METHOD_ID,
        records=tuple(
            ColumnInputRecord(
                body_id=key[0],
                neuron_type=key[1],
                eye_side=key[2],
                neuropil=key[3],
                ol_hex1=key[4],
                ol_hex2=key[5],
                input_count=count,
            )
            for key, count in sorted(sparse.items())
        ),
        summaries=tuple(sorted(summaries)),
        query_counts=tuple(sorted((query_counts or {}).items())),
        provenance=tuple(sorted((provenance or {}).items())),
    )
    validate_column_contract(
        contract, circuit_contract, expected_population=expected_population
    )
    return contract


def validate_column_contract(
    contract: BodyColumnInputContract,
    circuit_contract: Any | None = None,
    *,
    expected_population: bool = True,
) -> None:
    """Validate sparse records, summaries, body linkage, and accounting."""
    if contract.schema_version != COLUMN_SCHEMA_VERSION:
        raise MaleCNSValidationError("Unsupported body-column schema version.")
    if contract.dataset != MALECNS_DATASET:
        raise MaleCNSValidationError("Body-column dataset is not male-cns:v1.0.")
    if contract.endpoint != NEUPRINT_ENDPOINT:
        raise MaleCNSValidationError("Body-column endpoint is not official neuPrint.")
    if contract.visual_territory_rule != VISUAL_TERRITORY_RULE_ID:
        raise MaleCNSValidationError("Unexpected body-column territory rule.")
    if contract.aggregation_method != AGGREGATION_METHOD_ID:
        raise MaleCNSValidationError("Unexpected body-column aggregation method.")
    if any(
        not isinstance(name, str)
        or isinstance(count, bool)
        or not isinstance(count, int)
        or count < 0
        for name, count in contract.query_counts
    ):
        raise MaleCNSValidationError("Body-column query counts are invalid.")
    summaries = {summary.body_id: summary for summary in contract.summaries}
    if len(summaries) != len(contract.summaries):
        raise MaleCNSValidationError("Duplicate body summaries were serialized.")
    if expected_population:
        counts = Counter(summary.neuron_type for summary in contract.summaries)
        expected_counts = {"LC4": 126, "LPLC2": 185}
        if counts != expected_counts or len(contract.summaries) != 311:
            raise MaleCNSValidationError(
                f"Unexpected body-column population: counts={dict(counts)!r}."
            )
    if circuit_contract is not None:
        if (
            contract.candidate_identifier != circuit_contract.candidate.identifier
            or contract.candidate_version != circuit_contract.candidate.version
        ):
            raise MaleCNSValidationError(
                "Body-column candidate does not match the CircuitContract."
            )
        expected = {
            neuron.body_id: neuron
            for neuron in _candidate_visual_neurons(circuit_contract)
        }
        if set(summaries) != set(expected):
            raise MaleCNSValidationError("Body-column IDs do not match the contract.")
        for body_id, summary in summaries.items():
            neuron = expected[body_id]
            if (summary.neuron_type, summary.eye_side) != (
                neuron.type,
                neuron.soma_side,
            ):
                raise MaleCNSValidationError(
                    f"Body-column type/side mismatch for body {body_id}."
                )

    for summary in summaries.values():
        if summary.neuron_type not in VISUAL_TYPES:
            raise MaleCNSValidationError(
                f"Body summary has a non-visual type: {summary.neuron_type!r}."
            )
        if summary.eye_side not in {"L", "R"}:
            raise MaleCNSValidationError("Body summary side must be 'L' or 'R'.")
        if summary.body_id <= 0:
            raise MaleCNSValidationError("Body summary body_id must be positive.")

    record_keys: set[tuple[int, str, str, str, int, int]] = set()
    biological_keys: set[tuple[int, str, str, int, int]] = set()
    record_totals: Counter[int] = Counter()
    for record in contract.records:
        key = (
            record.body_id,
            record.neuron_type,
            record.eye_side,
            record.neuropil,
            record.ol_hex1,
            record.ol_hex2,
        )
        if key in record_keys:
            raise MaleCNSValidationError(f"Duplicate sparse column key: {key!r}.")
        record_keys.add(key)
        biological_key = (
            record.body_id,
            record.eye_side,
            record.neuropil,
            record.ol_hex1,
            record.ol_hex2,
        )
        if biological_key in biological_keys:
            raise MaleCNSValidationError(
                f"Duplicate biological sparse column key: {biological_key!r}."
            )
        biological_keys.add(biological_key)
        if record.body_id not in summaries:
            raise MaleCNSValidationError(
                f"Sparse record references body {record.body_id} without a summary."
            )
        if record.neuron_type not in VISUAL_TYPES:
            raise MaleCNSValidationError("DNp01 or another non-visual type was added.")
        if record.neuron_type != summaries[record.body_id].neuron_type:
            raise MaleCNSValidationError("Sparse record type differs from its body.")
        if record.eye_side != summaries[record.body_id].eye_side:
            raise MaleCNSValidationError("Sparse record side differs from its body.")
        if record.neuropil not in {"ME", "LO", "LOP"}:
            raise MaleCNSValidationError(
                f"Invalid sparse source neuropil {record.neuropil!r}."
            )
        if not isinstance(record.input_count, int) or record.input_count <= 0:
            raise MaleCNSValidationError("Sparse input_count must be positive.")
        if record.ol_hex1 < 0 or record.ol_hex2 < 0:
            raise MaleCNSValidationError("Sparse hex coordinates must be non-negative.")
        expected_column_id = canonical_column_id(
            record.neuropil,
            record.eye_side,
            record.ol_hex1,
            record.ol_hex2,
        )
        if record.column_id != expected_column_id:
            raise MaleCNSValidationError("Sparse column ID is not canonical.")
        record_totals[record.body_id] += record.input_count

    for body_id, summary in summaries.items():
        if summary.relevant_input_count < 0:
            raise MaleCNSValidationError("Relevant input count cannot be negative.")
        if summary.assigned_input_count < 0 or summary.unassigned_input_count < 0:
            raise MaleCNSValidationError(
                "Assigned/unassigned counts cannot be negative."
            )
        if any(
            value < 0
            for value in (
                summary.malformed_hex_count,
                summary.multiple_column_count,
                summary.unknown_column_count,
                summary.distinct_occupied_column_count,
            )
        ):
            raise MaleCNSValidationError("Body summary counts cannot be negative.")
        if summary.assigned_input_count != record_totals[body_id]:
            raise MaleCNSValidationError(
                f"Sparse counts do not sum for body {body_id}."
            )
        if summary.assigned_input_count + summary.unassigned_input_count != (
            summary.relevant_input_count
        ):
            raise MaleCNSValidationError(
                f"Assigned/unassigned accounting does not sum for body {body_id}."
            )
        if summary.distinct_occupied_column_count != sum(
            1 for key in record_keys if key[0] == body_id
        ):
            raise MaleCNSValidationError(
                f"Distinct occupied-column count does not sum for body {body_id}."
            )
        expected_fraction = (
            summary.assigned_input_count / summary.relevant_input_count
            if summary.relevant_input_count
            else 0.0
        )
        if not math.isclose(
            summary.assignment_fraction, expected_fraction, rel_tol=0, abs_tol=1e-12
        ):
            raise MaleCNSValidationError(
                f"Assignment fraction is inconsistent for body {body_id}."
            )
        if any(value < 0 for _, value in summary.neuropil_input_counts):
            raise MaleCNSValidationError("Neuropil counts cannot be negative.")
        if any(
            neuropil not in VALID_OPTIC_NEUROPILS
            for neuropil, _ in summary.neuropil_input_counts
        ):
            raise MaleCNSValidationError("Unknown neuropil in body input counts.")
        if sum(value for _, value in summary.neuropil_input_counts) != (
            summary.relevant_input_count
        ):
            raise MaleCNSValidationError(
                f"Neuropil input counts do not sum for body {body_id}."
            )
        if any(value < 0 for _, value in summary.neuropil_assigned_counts):
            raise MaleCNSValidationError("Neuropil assigned counts cannot be negative.")
        if any(
            neuropil not in {"ME", "LO", "LOP"}
            for neuropil, _ in summary.neuropil_assigned_counts
        ):
            raise MaleCNSValidationError("Unknown neuropil in assigned counts.")
        if sum(value for _, value in summary.neuropil_assigned_counts) != (
            summary.assigned_input_count
        ):
            raise MaleCNSValidationError(
                f"Neuropil assigned counts do not sum for body {body_id}."
            )
        assigned_by_neuropil = dict(summary.neuropil_assigned_counts)
        input_by_neuropil = dict(summary.neuropil_input_counts)
        if any(
            assigned_by_neuropil.get(neuropil, 0) > input_count
            for neuropil, input_count in input_by_neuropil.items()
        ):
            raise MaleCNSValidationError(
                f"Assigned neuropil count exceeds input count for body {body_id}."
            )


def summarize_raw_synapses(
    rows: Iterable[Mapping[str, Any]] | Any,
    circuit_contract: Any,
    primary_rois_by_side: Mapping[str, Sequence[str]],
) -> RawInputObservation:
    """Summarize raw primary-only rows for the 16-body equivalence gate."""
    expected = {
        neuron.body_id: neuron for neuron in _candidate_visual_neurons(circuit_contract)
    }
    sparse: Counter[tuple[int, str, str, str, int, int]] = Counter()
    totals: Counter[int] = Counter()
    assigned: Counter[int] = Counter()
    for index, row in enumerate(_records(rows), start=1):
        body_id = _int_value(row.get("bodyId"), f"raw row {index} bodyId")
        neuron = expected.get(body_id)
        if neuron is None:
            raise MaleCNSValidationError(
                f"Raw equivalence rows reference body {body_id} outside the visual set."
            )
        if row.get("type") != "post":
            raise MaleCNSDataError("Raw equivalence rows must be postsynaptic.")
        roi = row.get("roi")
        if roi not in _matching_rois(primary_rois_by_side, neuron.soma_side or ""):
            continue
        neuropil = _roi_neuropil(str(roi), neuron.soma_side or "")
        totals[body_id] += 1
        hex1 = _int_value(row.get("olHex1"), "raw olHex1", nullable=True)
        hex2 = _int_value(row.get("olHex2"), "raw olHex2", nullable=True)
        if hex1 is None or hex2 is None:
            continue
        assigned[body_id] += 1
        key = (
            body_id,
            neuron.type or "",
            neuron.soma_side or "",
            neuropil,
            hex1,
            hex2,
        )
        sparse[key] += 1
    per_body = {
        body_id: (
            totals[body_id],
            assigned[body_id],
            totals[body_id] - assigned[body_id],
        )
        for body_id in expected
        if totals[body_id] or body_id in totals
    }
    return RawInputObservation(sparse_counts=sparse, per_body=per_body)


def compare_method_equivalence(
    aggregated: BodyColumnInputContract,
    raw: RawInputObservation,
    body_ids: Iterable[int] = FROZEN_PHASE_1D_BODY_IDS,
) -> None:
    """Require exact raw-vs-server aggregation equality for the frozen sample."""
    summaries = {summary.body_id: summary for summary in aggregated.summaries}
    body_id_set = set(body_ids)
    aggregate_sparse = {
        (
            record.body_id,
            record.neuron_type,
            record.eye_side,
            record.neuropil,
            record.ol_hex1,
            record.ol_hex2,
        ): record.input_count
        for record in aggregated.records
        if record.body_id in body_id_set
    }
    for body_id in body_ids:
        summary = summaries.get(body_id)
        expected = raw.per_body.get(body_id)
        if summary is None or expected is None:
            raise MaleCNSValidationError(
                f"Method-equivalence body {body_id} is missing from one method."
            )
        actual = (
            summary.relevant_input_count,
            summary.assigned_input_count,
            summary.unassigned_input_count,
        )
        if actual != expected:
            raise MaleCNSValidationError(
                f"Method-equivalence count mismatch for body {body_id}: "
                f"aggregate={actual!r}, raw={expected!r}."
            )
    raw_sparse = {
        key: value for key, value in raw.sparse_counts.items() if key[0] in body_id_set
    }
    if aggregate_sparse != raw_sparse:
        raise MaleCNSValidationError(
            "Method-equivalence sparse column distribution mismatch."
        )


def _fetch_custom(query: str, client: Any) -> Any:
    from neuprint import fetch_custom

    return fetch_custom(query, client=client)


def acquire_body_columns(
    client: Any,
    circuit_contract: Any,
    *,
    query_runner: Callable[[str, Any], Any] = _fetch_custom,
    raw_fetcher: Callable[..., Any] | None = None,
    acquired_at_utc: str | None = None,
) -> BodyColumnInputContract:
    """Run the frozen equivalence gate, then aggregate all 311 visual bodies."""
    if client.dataset != circuit_contract.candidate.dataset:
        raise MaleCNSAccessError(
            f"Unexpected neuPrint dataset {client.dataset!r}; expected "
            f"{circuit_contract.candidate.dataset!r}."
        )
    visual_neurons = _candidate_visual_neurons(circuit_contract)
    visual_ids = tuple(neuron.body_id for neuron in visual_neurons)
    rois_by_side = optic_primary_rois(client)

    identity_rows = query_runner(identity_query(visual_ids), client)
    validate_live_identities(identity_rows, circuit_contract)

    if raw_fetcher is None:
        from neuprint import NeuronCriteria as NC
        from neuprint import SynapseCriteria as SC
        from neuprint import fetch_synapses

        def raw_fetcher(body_ids: Sequence[int], client: Any) -> Any:
            return fetch_synapses(
                NC(bodyId=list(body_ids)),
                SC(type="post", primary_only=True),
                batch_size=4,
                client=client,
            )

    equivalence_rows = query_runner(
        aggregate_query(FROZEN_PHASE_1D_BODY_IDS, rois_by_side), client
    )
    equivalence_aggregate = build_column_contract(
        equivalence_rows,
        circuit_contract,
        rois_by_side,
        acquired_at_utc=acquired_at_utc,
        query_counts={"equivalence_aggregate_rows": len(_records(equivalence_rows))},
        expected_population=False,
    )
    raw_rows = raw_fetcher(FROZEN_PHASE_1D_BODY_IDS, client)
    raw_observation = summarize_raw_synapses(raw_rows, circuit_contract, rois_by_side)
    compare_method_equivalence(equivalence_aggregate, raw_observation)

    full_rows = query_runner(aggregate_query(visual_ids, rois_by_side), client)
    full_row_records = _records(full_rows)
    query_counts = {
        "identity_records": len(_records(identity_rows)),
        "equivalence_aggregate_rows": len(_records(equivalence_rows)),
        "equivalence_raw_synapse_records": len(_records(raw_rows)),
        "full_aggregate_rows": len(full_row_records),
        "distinct_visual_bodies": len(visual_ids),
    }
    return build_column_contract(
        full_row_records,
        circuit_contract,
        rois_by_side,
        acquired_at_utc=acquired_at_utc,
        query_counts=query_counts,
        provenance={
            "malecns_direct": (
                "bodyId, postsynaptic site, primary ROI, olHex1, olHex2, side, dataset"
            ),
            "published_derived": "MaleCNS optic-column definitions and assignments",
            "neurofly_derived": (
                "sparse per-body column counts and deterministic summaries"
            ),
            "official_column_resource": (
                "optic-column-type-assignments-v1.0.xlsx; flyconnectome/2025malecns"
            ),
        },
    )
