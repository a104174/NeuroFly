"""Small, explicit records for the Phase 1A MaleCNS data slice."""

from dataclasses import asdict, dataclass
from typing import Any

NEUPRINT_ENDPOINT = "https://neuprint.janelia.org"
MALECNS_DATASET = "male-cns:v1.0"
CREDENTIAL_ENV_VAR = "NEUPRINT_APPLICATION_CREDENTIALS"


@dataclass(frozen=True)
class CandidateDefinition:
    """A versioned NeuroFly selection, not a complete biological circuit."""

    identifier: str
    version: int
    dataset: str
    neuron_types: tuple[str, ...]


CANDIDATE = CandidateDefinition(
    identifier="looming_giant_fiber_v1",
    version=1,
    dataset=MALECNS_DATASET,
    neuron_types=("LC4", "LPLC2", "DNp01"),
)


@dataclass(frozen=True)
class NeuronRecord:
    dataset: str
    body_id: int
    instance: str | None
    type: str | None
    status: str | None
    status_label: str | None
    superclass: str | None
    class_: str | None
    soma_side: str | None
    soma_neuromere: str | None
    pre: int | None
    post: int | None
    upstream: int | None
    downstream: int | None
    predicted_nt: str | None
    predicted_nt_confidence: float | None
    consensus_nt: str | None
    dimorphism: str | None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["class"] = result.pop("class_")
        return result


@dataclass(frozen=True)
class ConnectionRecord:
    """A chemical ConnectsTo edge; structural_weight is not physiological."""

    dataset: str
    source_body_id: int
    target_body_id: int
    source_type: str
    target_type: str
    structural_weight: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateSnapshot:
    candidate: CandidateDefinition
    neurons: tuple[NeuronRecord, ...]
    connections: tuple[ConnectionRecord, ...]
    acquired_at_utc: str


@dataclass(frozen=True)
class PrimaryMetrics:
    edge_count: int
    distinct_source_count: int
    structural_weight_sum: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    neuron_counts: dict[str, int]
    total_neuron_count: int
    induced_connection_count: int
    lc4_to_dnp01: PrimaryMetrics
    lplc2_to_dnp01: PrimaryMetrics
