"""Reproducible access to the pinned MaleCNS candidate circuit."""

from neurofly.malecns.acquire import acquire_candidate
from neurofly.malecns.benchmarks import BENCHMARKS, SENSORY_BOUNDARY
from neurofly.malecns.client import create_client
from neurofly.malecns.column_snapshot import (
    export_column_contract,
    load_column_contract,
)
from neurofly.malecns.columns import (
    BodyColumnInputContract,
    BodyColumnSummary,
    ColumnInputRecord,
    acquire_body_columns,
    validate_column_contract,
)
from neurofly.malecns.contract import CircuitContract, load_circuit_contract
from neurofly.malecns.models import CANDIDATE, CandidateSnapshot
from neurofly.malecns.sensory import LoomingSample, LoomingStimulus, VisualPoint
from neurofly.malecns.snapshot import export_snapshot
from neurofly.malecns.validation import validate_snapshot

__all__ = [
    "CANDIDATE",
    "BENCHMARKS",
    "BodyColumnInputContract",
    "BodyColumnSummary",
    "SENSORY_BOUNDARY",
    "ColumnInputRecord",
    "CircuitContract",
    "CandidateSnapshot",
    "LoomingSample",
    "LoomingStimulus",
    "VisualPoint",
    "acquire_candidate",
    "acquire_body_columns",
    "create_client",
    "export_column_contract",
    "export_snapshot",
    "load_column_contract",
    "load_circuit_contract",
    "validate_column_contract",
    "validate_snapshot",
]
