"""Read-only acquisition and normalization for the candidate circuit."""

import math
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime
from numbers import Integral, Real
from typing import Any

from neurofly.malecns.errors import MaleCNSAccessError, MaleCNSDataError
from neurofly.malecns.models import (
    CANDIDATE,
    CandidateDefinition,
    CandidateSnapshot,
    ConnectionRecord,
    NeuronRecord,
)

NEURON_COLUMNS = {
    "bodyId",
    "instance",
    "type",
    "status",
    "statusLabel",
    "superclass",
    "class",
    "somaSide",
    "somaNeuromere",
    "pre",
    "post",
    "upstream",
    "downstream",
    "predictedNt",
    "predictedNtConfidence",
    "consensusNt",
    "dimorphism",
}
CONNECTION_COLUMNS = {
    "sourceBodyId",
    "targetBodyId",
    "sourceType",
    "targetType",
    "weight",
}


def _records(table: Any) -> list[Mapping[str, Any]]:
    if hasattr(table, "to_dict"):
        records = table.to_dict("records")
    else:
        records = list(table)
    if not all(isinstance(row, Mapping) for row in records):
        raise MaleCNSDataError("neuPrint result rows must be mappings.")
    return records


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, Real) and not isinstance(value, Integral):
        return math.isnan(float(value))
    return type(value).__name__ in {"NAType", "NaTType"}


def _optional_str(value: Any) -> str | None:
    return None if _missing(value) else str(value)


def _optional_int(value: Any, field: str) -> int | None:
    if _missing(value):
        return None
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise MaleCNSDataError(f"{field} must be an integer or null.")
    return int(value)


def _required_int(value: Any, field: str) -> int:
    result = _optional_int(value, field)
    if result is None:
        raise MaleCNSDataError(f"{field} must not be null.")
    return result


def _require_columns(row: Mapping[str, Any], columns: set[str], kind: str) -> None:
    missing = sorted(columns - row.keys())
    if missing:
        raise MaleCNSDataError(f"Missing required {kind} columns: {', '.join(missing)}")


def normalize_neurons(
    rows: Iterable[Mapping[str, Any]] | Any, dataset: str
) -> tuple[NeuronRecord, ...]:
    normalized = []
    for row in _records(rows):
        _require_columns(row, NEURON_COLUMNS, "neuron")
        confidence = row["predictedNtConfidence"]
        if not _missing(confidence) and (
            isinstance(confidence, bool) or not isinstance(confidence, Real)
        ):
            raise MaleCNSDataError("predictedNtConfidence must be numeric or null.")
        normalized.append(
            NeuronRecord(
                dataset=dataset,
                body_id=_required_int(row["bodyId"], "bodyId"),
                instance=_optional_str(row["instance"]),
                type=_optional_str(row["type"]),
                status=_optional_str(row["status"]),
                status_label=_optional_str(row["statusLabel"]),
                superclass=_optional_str(row["superclass"]),
                class_=_optional_str(row["class"]),
                soma_side=_optional_str(row["somaSide"]),
                soma_neuromere=_optional_str(row["somaNeuromere"]),
                pre=_optional_int(row["pre"], "pre"),
                post=_optional_int(row["post"], "post"),
                upstream=_optional_int(row["upstream"], "upstream"),
                downstream=_optional_int(row["downstream"], "downstream"),
                predicted_nt=_optional_str(row["predictedNt"]),
                predicted_nt_confidence=(
                    None if _missing(confidence) else float(confidence)
                ),
                consensus_nt=_optional_str(row["consensusNt"]),
                dimorphism=_optional_str(row["dimorphism"]),
            )
        )

    body_ids = [neuron.body_id for neuron in normalized]
    if len(body_ids) != len(set(body_ids)):
        raise MaleCNSDataError("Duplicate selected neuron body IDs were returned.")
    return tuple(normalized)


def normalize_connections(
    rows: Iterable[Mapping[str, Any]] | Any, dataset: str
) -> tuple[ConnectionRecord, ...]:
    normalized = []
    for row in _records(rows):
        _require_columns(row, CONNECTION_COLUMNS, "connection")
        weight = _required_int(row["weight"], "ConnectsTo.weight")
        if weight <= 0:
            raise MaleCNSDataError("ConnectsTo.weight must be a positive integer.")
        source_type = _optional_str(row["sourceType"])
        target_type = _optional_str(row["targetType"])
        if source_type is None or target_type is None:
            raise MaleCNSDataError("Connection endpoint types must not be null.")
        normalized.append(
            ConnectionRecord(
                dataset=dataset,
                source_body_id=_required_int(row["sourceBodyId"], "sourceBodyId"),
                target_body_id=_required_int(row["targetBodyId"], "targetBodyId"),
                source_type=source_type,
                target_type=target_type,
                # Exact mapping from chemical ConnectsTo.weight; not simulation weight.
                structural_weight=weight,
            )
        )
    return tuple(normalized)


def _quoted_types(candidate: CandidateDefinition) -> str:
    # Candidate values are project-owned constants, not user input.
    return ", ".join(f"'{value}'" for value in candidate.neuron_types)


def neuron_query(candidate: CandidateDefinition = CANDIDATE) -> str:
    return f"""
MATCH (n:Neuron)
WHERE n.type IN [{_quoted_types(candidate)}]
RETURN n.bodyId AS bodyId, n.instance AS instance, n.type AS type,
       n.status AS status, n.statusLabel AS statusLabel,
       n.superclass AS superclass, n.class AS class,
       n.somaSide AS somaSide, n.somaNeuromere AS somaNeuromere,
       n.pre AS pre, n.post AS post, n.upstream AS upstream,
       n.downstream AS downstream, n.predictedNt AS predictedNt,
       n.predictedNtConfidence AS predictedNtConfidence,
       n.consensusNt AS consensusNt, n.dimorphism AS dimorphism
ORDER BY n.bodyId
""".strip()


def connection_query(body_ids: Iterable[int]) -> str:
    ids = ", ".join(str(body_id) for body_id in sorted(body_ids))
    return f"""
MATCH (source:Neuron)-[connection:ConnectsTo]->(target:Neuron)
WHERE source.bodyId IN [{ids}] AND target.bodyId IN [{ids}]
RETURN source.bodyId AS sourceBodyId, target.bodyId AS targetBodyId,
       source.type AS sourceType, target.type AS targetType,
       connection.weight AS weight
ORDER BY source.bodyId, target.bodyId
""".strip()


def _fetch_custom(query: str, client: Any) -> Any:
    from neuprint import fetch_custom

    return fetch_custom(query, client=client)


def acquire_candidate(
    client: Any,
    *,
    candidate: CandidateDefinition = CANDIDATE,
    query_runner: Callable[[str, Any], Any] = _fetch_custom,
    acquired_at_utc: str | None = None,
) -> CandidateSnapshot:
    """Acquire the complete chemical induced subgraph for the candidate."""
    if client.dataset != candidate.dataset:
        raise MaleCNSAccessError(
            f"Unexpected neuPrint dataset {client.dataset!r}; expected "
            f"{candidate.dataset!r}."
        )
    try:
        neurons = normalize_neurons(
            query_runner(neuron_query(candidate), client), candidate.dataset
        )
        connections = normalize_connections(
            query_runner(connection_query(n.body_id for n in neurons), client),
            candidate.dataset,
        )
    except (MaleCNSDataError, MaleCNSAccessError):
        raise
    except Exception:
        raise MaleCNSAccessError(
            "MaleCNS acquisition failed. Check authentication, network, and neuPrint "
            "service availability."
        ) from None

    return CandidateSnapshot(
        candidate=candidate,
        neurons=neurons,
        connections=connections,
        acquired_at_utc=acquired_at_utc or datetime.now(UTC).isoformat(),
    )
