"""Bounded Phase 6C DNp01-to-TTMn exploratory model slice.

MaleCNS identities and chemical edge counts are carried as source evidence.
The downstream event-integrator and its parameters are separate NeuroFly model
assumptions.  This module contains no muscle, movement, or behavior model.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from neurofly.experiments import ExperimentConfig, ExperimentResult, ExperimentRunner
from neurofly.malecns.models import MALECNS_DATASET, NEUPRINT_ENDPOINT
from neurofly.simulation import SpikeEvent

MOTOR_EVIDENCE_SCHEMA_VERSION = "malecns_dnp01_ttmn_evidence_v1"
MOTOR_RUN_CONFIG_SCHEMA_VERSION = "motor_pathway_run_config_v1"
MOTOR_RESULT_SCHEMA_VERSION = "motor_pathway_result_v1"
MOTOR_MODEL_ID = "ttmn_dimensionless_event_integrator"
MOTOR_MODEL_VERSION = "phase6c_v1"
MOTOR_REFERENCE_ASSUMPTION_SET = "phase6c_reference_model_assumptions_v1"
MOTOR_PARAMETER_CLASSIFICATION = "MODEL_ASSUMPTION"
MOTOR_STATE_UNIT = "dimensionless"
MOTOR_INPUT_SEMANTICS = "same_boundary_as_dnp01_event_v1"
MOTOR_INTEGRATION_SCHEME = "exact_exponential_decay_then_boundary_input_v1"

UPSTREAM_CANDIDATE_ID = "looming_giant_fiber_v1"
UPSTREAM_CANDIDATE_VERSION = 1
UPSTREAM_SOURCE_HASHES = (
    (
        "connections.jsonl",
        "f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a",
    ),
    (
        "neurons.jsonl",
        "00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e",
    ),
)
UPSTREAM_CONTRACT_SHA256 = hashlib.sha256(
    json.dumps(
        {
            "candidate_identifier": UPSTREAM_CANDIDATE_ID,
            "candidate_version": UPSTREAM_CANDIDATE_VERSION,
            "dataset": MALECNS_DATASET,
            "source_hashes": [list(pair) for pair in UPSTREAM_SOURCE_HASHES],
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

_DNP01_IDENTITIES = (
    {
        "body_id": 10001,
        "type": "DNp01",
        "instance": "DNp01(GF)_R",
        "side": "R",
        "node_index": 0,
        "status": "Traced",
        "status_label": "Roughly traced",
        "superclass": "descending_neuron",
    },
    {
        "body_id": 10010,
        "type": "DNp01",
        "instance": "DNp01(GF)_L",
        "side": "L",
        "node_index": 1,
        "status": "Traced",
        "status_label": "Roughly traced",
        "superclass": "descending_neuron",
    },
)
_TTMN_IDENTITIES = (
    {
        "body_id": 800146,
        "type": "TTMn",
        "instance": "TTMn_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "neuromere": "T2",
    },
    {
        "body_id": 804642,
        "type": "TTMn",
        "instance": "TTMn_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "neuromere": "T2",
    },
)
_CHEMICAL_EDGES = (
    {
        "edge_id": "malecns_v1_10001_800146_chemical",
        "kind": "CHEMICAL_CONNECTOME_EDGE",
        "pre_body_id": 10001,
        "post_body_id": 800146,
        "structural_weight": 70,
        "weight_semantics": "MaleCNS ConnectsTo contact count; not coupling gain",
    },
    {
        "edge_id": "malecns_v1_10010_804642_chemical",
        "kind": "CHEMICAL_CONNECTOME_EDGE",
        "pre_body_id": 10010,
        "post_body_id": 804642,
        "structural_weight": 20,
        "weight_semantics": "MaleCNS ConnectsTo contact count; not coupling gain",
    },
)


class MotorPathwayError(ValueError):
    """Invalid Phase 6C evidence, run configuration, or output."""


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise MotorPathwayError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise MotorPathwayError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise MotorPathwayError(f"{field_name} must be finite.")
    return result


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class MotorPathwayEvidenceContract:
    """Pinned source observations and literature modality references."""

    schema_version: str = MOTOR_EVIDENCE_SCHEMA_VERSION
    contract_id: str = "malecns_dnp01_to_ttmn_v1"
    dataset: str = MALECNS_DATASET
    upstream_candidate_identifier: str = UPSTREAM_CANDIDATE_ID
    upstream_candidate_version: int = UPSTREAM_CANDIDATE_VERSION
    upstream_contract_sha256: str = UPSTREAM_CONTRACT_SHA256
    upstream_source_hashes: tuple[tuple[str, str], ...] = UPSTREAM_SOURCE_HASHES
    dnp01_identities: tuple[dict[str, Any], ...] = _DNP01_IDENTITIES
    ttmn_identities: tuple[dict[str, Any], ...] = _TTMN_IDENTITIES
    chemical_edges: tuple[dict[str, Any], ...] = _CHEMICAL_EDGES
    source_provenance: dict[str, Any] = field(
        default_factory=lambda: {
            "annotation_source_url": (
                "https://storage.googleapis.com/flyem-male-cns/v1.0/"
                "connectome-data/flat-connectome/"
                "body-annotations-male-cns-v1.0-minconf-0.5.feather"
            ),
            "annotation_source_sha256": (
                "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2"
            ),
            "connectivity_endpoint": NEUPRINT_ENDPOINT,
            "connectivity_dataset": MALECNS_DATASET,
            "connectivity_retrieved_at_utc": "2026-09-23",
            "connectivity_roi": "VNC",
            "min_total_weight": 1,
            "include_nonprimary": True,
            "query_body_ids": [10001, 10010, 800146, 804642],
            "source_document": "docs/science/motor_escape_feasibility.md",
            "structural_edge_semantics": "neuPrint chemical ConnectsTo.weight",
            "electrical_dataset_found": False,
        }
    )

    def __post_init__(self) -> None:
        if self.schema_version != MOTOR_EVIDENCE_SCHEMA_VERSION:
            raise MotorPathwayError("unsupported motor evidence schema.")
        if self.dataset != MALECNS_DATASET:
            raise MotorPathwayError("motor evidence dataset must be male-cns:v1.0.")
        if tuple(self.upstream_source_hashes) != UPSTREAM_SOURCE_HASHES:
            raise MotorPathwayError("upstream contract source hashes differ.")
        if tuple(self.dnp01_identities) != _DNP01_IDENTITIES:
            raise MotorPathwayError("DNp01 identities differ from the audited set.")
        if tuple(self.ttmn_identities) != _TTMN_IDENTITIES:
            raise MotorPathwayError("TTMn identities differ from the audited set.")
        if tuple(self.chemical_edges) != _CHEMICAL_EDGES:
            raise MotorPathwayError("chemical motor edges differ from the audit.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "dataset": self.dataset,
            "upstream_contract": {
                "candidate_identifier": self.upstream_candidate_identifier,
                "candidate_version": self.upstream_candidate_version,
                "sha256": self.upstream_contract_sha256,
                "source_hashes": [list(pair) for pair in self.upstream_source_hashes],
            },
            "bodies": [*self.dnp01_identities, *self.ttmn_identities],
            "chemical_edges": list(self.chemical_edges),
            "electrical_coupling_evidence": [
                {
                    "kind": "ELECTRICAL_COUPLING",
                    "source_body_id": source,
                    "target_body_id": target,
                    "evidence_classification": "SUPPORTED_LITERATURE",
                    "literature_sources": [
                        "King-Wyman-1980",
                        "Phelan-1996",
                        "Augustin-2019",
                    ],
                    "male_cns_pair_specific_strength": None,
                    "numeric_value": None,
                    "parameter_classification": "UNKNOWN_MODEL_ASSUMPTION",
                }
                for source, target in ((10001, 800146), (10010, 804642))
            ],
            "mixed_connections": [
                {
                    "kind": "MIXED_CONNECTION",
                    "source_body_id": source,
                    "target_body_id": target,
                    "component_evidence_ids": [
                        edge["edge_id"],
                        f"literature_electrical_{source}_{target}",
                    ],
                    "combined_weight": None,
                }
                for edge, source, target in zip(
                    self.chemical_edges,
                    (10001, 10010),
                    (800146, 804642),
                    strict=True,
                )
            ],
            "source_provenance": dict(self.source_provenance),
        }

    @property
    def sha256(self) -> str:
        return _canonical_sha256(self.to_dict())

    @property
    def target_by_source(self) -> MappingProxyType:
        return MappingProxyType(
            {edge["pre_body_id"]: edge["post_body_id"] for edge in self.chemical_edges}
        )

    def validate_upstream_contract(self, circuit_contract: Any) -> None:
        candidate = getattr(circuit_contract, "candidate", None)
        provenance = getattr(circuit_contract, "provenance", None)
        integrity = getattr(circuit_contract, "integrity", None)
        if (
            candidate is None
            or provenance is None
            or integrity is None
            or candidate.identifier != self.upstream_candidate_identifier
            or candidate.version != self.upstream_candidate_version
            or provenance.dataset != self.dataset
            or tuple(sorted(integrity.sha256_by_file)) != self.upstream_source_hashes
        ):
            raise MotorPathwayError(
                "upstream CircuitContract identity or provenance mismatch."
            )
        neurons = getattr(circuit_contract, "neurons_by_body_id", {})
        for expected in self.dnp01_identities:
            actual = neurons.get(expected["body_id"])
            if actual is None or any(
                getattr(actual, field_name) != expected_value
                for field_name, expected_value in (
                    ("type", expected["type"]),
                    ("instance", expected["instance"]),
                    ("soma_side", expected["side"]),
                    ("status", expected["status"]),
                    ("status_label", expected["status_label"]),
                    ("superclass", expected["superclass"]),
                )
            ):
                raise MotorPathwayError(
                    f"upstream DNp01 identity mismatch for {expected['body_id']}."
                )
        # The selected 313-body graph intentionally omits TTMn and its edges.
        # Verify no fake downstream edge has been inserted into that contract.
        body_ids = set(neurons)
        if body_ids & {800146, 804642}:
            raise MotorPathwayError("TTMn must remain outside the upstream contract.")

    def validate_upstream_config(self, config: Any) -> None:
        """Require a persisted run to reference this exact upstream source."""

        if (
            getattr(config, "candidate_identifier", None)
            != self.upstream_candidate_identifier
            or getattr(config, "candidate_version", None)
            != self.upstream_candidate_version
            or getattr(config, "dataset", None) != self.dataset
            or getattr(config, "source_endpoint", None) != NEUPRINT_ENDPOINT
            or tuple(sorted(getattr(config, "circuit_integrity", ())))
            != self.upstream_source_hashes
        ):
            raise MotorPathwayError(
                "upstream experiment configuration provenance mismatch."
            )


MOTOR_PATHWAY_EVIDENCE = MotorPathwayEvidenceContract()


@dataclass(frozen=True, slots=True)
class TTMnIntegratorConfig:
    """Explicit exploratory dimensionless state parameters, not physiology."""

    tau_motor_ms: float = 10.0
    event_gain: float = 0.25
    model_id: str = MOTOR_MODEL_ID
    model_version: str = MOTOR_MODEL_VERSION
    assumption_set_id: str = MOTOR_REFERENCE_ASSUMPTION_SET
    parameter_classification: str = MOTOR_PARAMETER_CLASSIFICATION
    state_unit: str = MOTOR_STATE_UNIT
    integration_scheme: str = MOTOR_INTEGRATION_SCHEME
    input_semantics: str = MOTOR_INPUT_SEMANTICS

    def __post_init__(self) -> None:
        tau = _finite(self.tau_motor_ms, "tau_motor_ms")
        gain = _finite(self.event_gain, "event_gain")
        if tau <= 0.0:
            raise MotorPathwayError("tau_motor_ms must be positive.")
        if gain <= 0.0:
            raise MotorPathwayError("event_gain must be positive.")
        if self.model_id != MOTOR_MODEL_ID or self.model_version != MOTOR_MODEL_VERSION:
            raise MotorPathwayError("unsupported TTMn model identity.")
        if self.assumption_set_id != MOTOR_REFERENCE_ASSUMPTION_SET:
            raise MotorPathwayError("unsupported TTMn reference assumption set.")
        if self.parameter_classification != MOTOR_PARAMETER_CLASSIFICATION:
            raise MotorPathwayError("motor parameters must be model assumptions.")
        if self.state_unit != MOTOR_STATE_UNIT:
            raise MotorPathwayError("TTMn model state must remain dimensionless.")
        if self.integration_scheme != MOTOR_INTEGRATION_SCHEME:
            raise MotorPathwayError("unsupported motor integration scheme.")
        if self.input_semantics != MOTOR_INPUT_SEMANTICS:
            raise MotorPathwayError("unsupported motor event timing semantics.")
        object.__setattr__(self, "tau_motor_ms", tau)
        object.__setattr__(self, "event_gain", gain)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "assumption_set_id": self.assumption_set_id,
            "state_unit": self.state_unit,
            "integration_scheme": self.integration_scheme,
            "input_semantics": self.input_semantics,
            "stochastic_policy": "deterministic",
            "parameters": {
                "tau_motor_ms": {
                    "value": self.tau_motor_ms,
                    "units": "ms",
                    "classification": self.parameter_classification,
                },
                "event_gain": {
                    "value": self.event_gain,
                    "units": "dimensionless",
                    "classification": self.parameter_classification,
                },
            },
        }


@dataclass(frozen=True, slots=True)
class MotorPathwayRunConfig:
    """Downstream configuration composed with one immutable upstream run."""

    model: TTMnIntegratorConfig = field(default_factory=TTMnIntegratorConfig)
    dnp01_to_ttmn_silenced: bool = False
    evidence_contract_sha256: str = MOTOR_PATHWAY_EVIDENCE.sha256
    schema_version: str = MOTOR_RUN_CONFIG_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != MOTOR_RUN_CONFIG_SCHEMA_VERSION:
            raise MotorPathwayError("unsupported motor run configuration schema.")
        if not isinstance(self.model, TTMnIntegratorConfig):
            raise MotorPathwayError("model must be TTMnIntegratorConfig.")
        if not isinstance(self.dnp01_to_ttmn_silenced, bool):
            raise MotorPathwayError("dnp01_to_ttmn_silenced must be boolean.")
        if self.evidence_contract_sha256 != MOTOR_PATHWAY_EVIDENCE.sha256:
            raise MotorPathwayError("motor evidence contract identity mismatch.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "evidence_contract_sha256": self.evidence_contract_sha256,
            "model": self.model.to_dict(),
            "intervention": {
                "id": (
                    "DNP01_TO_TTMN_OUTPUT_SILENCED"
                    if self.dnp01_to_ttmn_silenced
                    else "NONE"
                ),
                "dnp01_to_ttmn_silenced": self.dnp01_to_ttmn_silenced,
                "semantics": (
                    "blocks persisted DNp01 events at the motor input boundary"
                ),
            },
        }

    @property
    def sha256(self) -> str:
        return _canonical_sha256(self.to_dict())


@dataclass(frozen=True, slots=True)
class TTMnInputEvent:
    """One exact persisted DNp01 event mapped to its audited TTMn identity."""

    source_body_id: int
    source_node_index: int
    target_body_id: int
    step: int
    time_ms: float
    event_gain: float
    event_semantics: str = MOTOR_INPUT_SEMANTICS

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_body_id": self.source_body_id,
            "source_node_index": self.source_node_index,
            "target_body_id": self.target_body_id,
            "step": self.step,
            "time_ms": self.time_ms,
            "event_gain": self.event_gain,
            "event_semantics": self.event_semantics,
        }


@dataclass(frozen=True, slots=True)
class TTMnStateTrajectory:
    body_id: int
    neuron_type: str
    side: str
    times_ms: tuple[float, ...]
    state: tuple[float, ...]
    input_event_count: int
    peak_state: float
    peak_step: int
    peak_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "neuron_type": self.neuron_type,
            "side": self.side,
            "state_unit": MOTOR_STATE_UNIT,
            "times_ms": list(self.times_ms),
            "state": list(self.state),
            "input_event_count": self.input_event_count,
            "peak_state": self.peak_state,
            "peak_step": self.peak_step,
            "peak_time_ms": self.peak_time_ms,
        }


@dataclass(frozen=True, slots=True)
class MotorSensitivityPoint:
    tau_motor_ms: float
    event_gain: float
    peak_state_by_body_id: tuple[tuple[int, float], ...]
    peak_step_by_body_id: tuple[tuple[int, int], ...]
    delivered_event_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "tau_motor_ms": self.tau_motor_ms,
            "event_gain": self.event_gain,
            "parameter_classification": MOTOR_PARAMETER_CLASSIFICATION,
            "peak_state_by_body_id": [
                {"body_id": body, "peak_state": value}
                for body, value in self.peak_state_by_body_id
            ],
            "peak_step_by_body_id": [
                {"body_id": body, "peak_step": value}
                for body, value in self.peak_step_by_body_id
            ],
            "delivered_event_count": self.delivered_event_count,
        }


@dataclass(frozen=True, slots=True)
class MotorPathwayExperimentResult:
    """A downstream layer referencing, but not rewriting, an upstream run."""

    upstream_result: ExperimentResult
    run_config: MotorPathwayRunConfig
    evidence_contract: MotorPathwayEvidenceContract
    source_dnp01_spike_events: tuple[SpikeEvent, ...]
    delivered_motor_inputs: tuple[TTMnInputEvent, ...]
    ttmn_trajectories: tuple[TTMnStateTrajectory, ...]
    sensitivity: tuple[MotorSensitivityPoint, ...]
    result_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.upstream_result, ExperimentResult):
            raise MotorPathwayError("upstream_result must be ExperimentResult.")
        if not isinstance(self.run_config, MotorPathwayRunConfig):
            raise MotorPathwayError("run_config must be MotorPathwayRunConfig.")
        if not isinstance(self.evidence_contract, MotorPathwayEvidenceContract):
            raise MotorPathwayError("evidence_contract is invalid.")
        if self.evidence_contract != MOTOR_PATHWAY_EVIDENCE:
            raise MotorPathwayError("evidence contract differs from the pinned audit.")
        self.evidence_contract.validate_upstream_config(self.upstream_result.config)
        source_events = tuple(self.source_dnp01_spike_events)
        inputs = tuple(self.delivered_motor_inputs)
        trajectories = tuple(self.ttmn_trajectories)
        sensitivity = tuple(self.sensitivity)
        expected_source_events = tuple(
            event
            for event in self.upstream_result.spike_events
            if event.neuron_type == "DNp01"
        )
        if source_events != expected_source_events:
            raise MotorPathwayError("source DNp01 events differ from upstream result.")
        expected_inputs = _map_motor_inputs(
            source_events,
            dt_ms=self.upstream_result.config.dt_ms,
            steps=self.upstream_result.config.steps,
            model=self.run_config.model,
            evidence_contract=self.evidence_contract,
        )
        if self.run_config.dnp01_to_ttmn_silenced and inputs:
            raise MotorPathwayError("silenced motor input must deliver no events.")
        if not self.run_config.dnp01_to_ttmn_silenced and inputs != expected_inputs:
            raise MotorPathwayError("motor inputs do not match source events.")
        times = self.upstream_result.times_ms
        expected_trajectories = _integrate_ttmn(
            times_ms=times,
            dt_ms=self.upstream_result.config.dt_ms,
            inputs=inputs,
            model=self.run_config.model,
            evidence_contract=self.evidence_contract,
        )
        if trajectories != expected_trajectories:
            raise MotorPathwayError("TTMn state does not match the model contract.")
        expected_sensitivity = _sensitivity_points(
            times_ms=times,
            dt_ms=self.upstream_result.config.dt_ms,
            source_events=source_events,
            run_config=self.run_config,
            evidence_contract=self.evidence_contract,
        )
        if sensitivity != expected_sensitivity:
            raise MotorPathwayError("motor sensitivity does not match its sweep.")
        object.__setattr__(self, "source_dnp01_spike_events", source_events)
        object.__setattr__(self, "delivered_motor_inputs", inputs)
        object.__setattr__(self, "ttmn_trajectories", trajectories)
        object.__setattr__(self, "sensitivity", sensitivity)
        object.__setattr__(
            self, "result_sha256", _canonical_sha256(self.to_dict(False))
        )

    def to_dict(self, include_sha256: bool = True) -> dict[str, Any]:
        value = {
            "schema_version": MOTOR_RESULT_SCHEMA_VERSION,
            "upstream_config_sha256": self.upstream_result.config_sha256,
            "upstream_result_sha256": self.upstream_result.result_sha256,
            "evidence_contract": self.evidence_contract.to_dict(),
            "evidence_contract_sha256": self.evidence_contract.sha256,
            "run_config": self.run_config.to_dict(),
            "run_config_sha256": self.run_config.sha256,
            "source_dnp01_spike_events": [
                {
                    "body_id": event.body_id,
                    "node_index": event.node_index,
                    "step": event.step,
                    "time_ms": event.time_ms,
                    "neuron_type": event.neuron_type,
                }
                for event in self.source_dnp01_spike_events
            ],
            "delivered_motor_inputs": [
                item.to_dict() for item in self.delivered_motor_inputs
            ],
            "ttmn_model_state": [item.to_dict() for item in self.ttmn_trajectories],
            "sensitivity": [item.to_dict() for item in self.sensitivity],
            "output_semantics": "SIMULATED_EXPLORATORY_TTMN_MODEL_STATE",
            "validation_status": "NOT_EVALUATED",
        }
        if include_sha256:
            value["result_sha256"] = self.result_sha256
        return value


def _map_motor_inputs(
    source_events: Iterable[SpikeEvent],
    *,
    dt_ms: float,
    steps: int,
    model: TTMnIntegratorConfig,
    evidence_contract: MotorPathwayEvidenceContract = MOTOR_PATHWAY_EVIDENCE,
) -> tuple[TTMnInputEvent, ...]:
    mapped: list[TTMnInputEvent] = []
    targets = evidence_contract.target_by_source
    node_indices = {
        identity["body_id"]: identity["node_index"]
        for identity in evidence_contract.dnp01_identities
    }
    for event in source_events:
        if event.neuron_type != "DNp01" or event.body_id not in targets:
            raise MotorPathwayError("motor input source is not an audited DNp01 body.")
        if event.node_index != node_indices[event.body_id]:
            raise MotorPathwayError("DNp01 graph node index does not match identity.")
        if event.step < 1 or event.step > steps:
            raise MotorPathwayError("DNp01 event step is outside the experiment grid.")
        event_time = event.step * dt_ms
        if not math.isfinite(event.time_ms) or not math.isclose(
            event.time_ms, event_time, rel_tol=0.0, abs_tol=1e-12
        ):
            raise MotorPathwayError("DNp01 event time does not match its step.")
        mapped.append(
            TTMnInputEvent(
                source_body_id=event.body_id,
                source_node_index=event.node_index,
                target_body_id=targets[event.body_id],
                step=event.step,
                time_ms=event.time_ms,
                event_gain=model.event_gain,
            )
        )
    return tuple(sorted(mapped, key=lambda item: (item.step, item.source_body_id)))


def _integrate_ttmn(
    *,
    times_ms: tuple[float, ...],
    dt_ms: float,
    inputs: tuple[TTMnInputEvent, ...],
    model: TTMnIntegratorConfig,
    evidence_contract: MotorPathwayEvidenceContract = MOTOR_PATHWAY_EVIDENCE,
) -> tuple[TTMnStateTrajectory, ...]:
    if len(times_ms) < 2 or dt_ms <= 0:
        raise MotorPathwayError("motor state requires a valid simulation grid.")
    expected_times = tuple(step * dt_ms for step in range(len(times_ms)))
    if times_ms != expected_times:
        raise MotorPathwayError("motor grid differs from upstream experiment grid.")
    inputs_by_body_step: dict[tuple[int, int], int] = defaultdict(int)
    identities = {item["body_id"]: item for item in evidence_contract.ttmn_identities}
    target_ids = tuple(sorted(identities))
    for item in inputs:
        if item.target_body_id not in identities:
            raise MotorPathwayError("unsupported TTMn target identity.")
        inputs_by_body_step[(item.target_body_id, item.step)] += 1

    decay = math.exp(-dt_ms / model.tau_motor_ms)
    trajectories: list[TTMnStateTrajectory] = []
    for body_id in target_ids:
        values = [0.0] * len(times_ms)
        for step in range(len(times_ms)):
            if step > 0:
                values[step] = values[step - 1] * decay
            # Events are injected at their stored DNp01 boundary; no delay is
            # added and structural_weight is not an input to this update.
            values[step] += inputs_by_body_step[(body_id, step)] * model.event_gain
        peak_step = max(range(len(values)), key=values.__getitem__)
        identity = identities[body_id]
        trajectories.append(
            TTMnStateTrajectory(
                body_id=body_id,
                neuron_type="TTMn",
                side=identity["side"],
                times_ms=times_ms,
                state=tuple(values),
                input_event_count=sum(
                    count
                    for (target_id, _), count in inputs_by_body_step.items()
                    if target_id == body_id
                ),
                peak_state=values[peak_step],
                peak_step=peak_step,
                peak_time_ms=times_ms[peak_step],
            )
        )
    return tuple(trajectories)


def _sensitivity_points(
    *,
    times_ms: tuple[float, ...],
    dt_ms: float,
    source_events: tuple[SpikeEvent, ...],
    run_config: MotorPathwayRunConfig,
    evidence_contract: MotorPathwayEvidenceContract = MOTOR_PATHWAY_EVIDENCE,
) -> tuple[MotorSensitivityPoint, ...]:
    tau_values = (5.0, 10.0, 20.0)
    gain_values = (0.1, 0.25, 0.5)
    result: list[MotorSensitivityPoint] = []
    for tau_motor_ms in tau_values:
        for event_gain in gain_values:
            model = TTMnIntegratorConfig(
                tau_motor_ms=tau_motor_ms, event_gain=event_gain
            )
            inputs = (
                ()
                if run_config.dnp01_to_ttmn_silenced
                else _map_motor_inputs(
                    source_events,
                    dt_ms=dt_ms,
                    steps=len(times_ms) - 1,
                    model=model,
                    evidence_contract=evidence_contract,
                )
            )
            trajectories = _integrate_ttmn(
                times_ms=times_ms,
                dt_ms=dt_ms,
                inputs=inputs,
                model=model,
                evidence_contract=evidence_contract,
            )
            result.append(
                MotorSensitivityPoint(
                    tau_motor_ms=tau_motor_ms,
                    event_gain=event_gain,
                    peak_state_by_body_id=tuple(
                        (item.body_id, item.peak_state) for item in trajectories
                    ),
                    peak_step_by_body_id=tuple(
                        (item.body_id, item.peak_step) for item in trajectories
                    ),
                    delivered_event_count=len(inputs),
                )
            )
    return tuple(result)


class MotorPathwayExperimentRunner:
    """Run the existing upstream experiment, then the explicit TTMn model."""

    def __init__(self, circuit_contract: Any) -> None:
        self.evidence_contract = MOTOR_PATHWAY_EVIDENCE
        self.evidence_contract.validate_upstream_contract(circuit_contract)
        self._upstream_runner = ExperimentRunner(circuit_contract)

    def run(
        self,
        config: ExperimentConfig,
        motor_config: MotorPathwayRunConfig | None = None,
    ) -> MotorPathwayExperimentResult:
        run_config = motor_config or MotorPathwayRunConfig()
        upstream = self._upstream_runner.run(config)
        source_events = tuple(
            event for event in upstream.spike_events if event.neuron_type == "DNp01"
        )
        inputs = (
            ()
            if run_config.dnp01_to_ttmn_silenced
            else _map_motor_inputs(
                source_events,
                dt_ms=config.dt_ms,
                steps=config.steps,
                model=run_config.model,
                evidence_contract=self.evidence_contract,
            )
        )
        trajectories = _integrate_ttmn(
            times_ms=upstream.times_ms,
            dt_ms=config.dt_ms,
            inputs=inputs,
            model=run_config.model,
            evidence_contract=self.evidence_contract,
        )
        sensitivity = _sensitivity_points(
            times_ms=upstream.times_ms,
            dt_ms=config.dt_ms,
            source_events=source_events,
            run_config=run_config,
            evidence_contract=self.evidence_contract,
        )
        return MotorPathwayExperimentResult(
            upstream_result=upstream,
            run_config=run_config,
            evidence_contract=self.evidence_contract,
            source_dnp01_spike_events=source_events,
            delivered_motor_inputs=inputs,
            ttmn_trajectories=trajectories,
            sensitivity=sensitivity,
        )


def run_phase6c_reference_suite(
    *,
    circuit_contract: Any,
    reference_artifact_root: str,
    reference_artifact_id: str,
    output_root: str,
) -> tuple[Any, ...]:
    """Generate bounded real reference and control artifacts from a pinned run."""

    from dataclasses import replace
    from pathlib import Path

    from neurofly.experiment_artifacts import (
        LoadedExperimentArtifact,
        load_experiment_artifact,
    )
    from neurofly.motor_pathway_artifacts import export_motor_pathway_artifact
    from neurofly.trajectory_characterization import PathwayCondition

    source_root = Path(reference_artifact_root)
    try:
        candidates = tuple(
            sorted(
                (entry for entry in source_root.iterdir() if entry.is_dir()),
                key=lambda entry: entry.name,
            )
        )
    except OSError:
        raise MotorPathwayError(
            "reference experiment artifact root is unavailable."
        ) from None
    reference: LoadedExperimentArtifact | None = None
    for candidate in candidates:
        loaded = load_experiment_artifact(candidate)
        if loaded.artifact_id == reference_artifact_id:
            reference = loaded
            break
    if reference is None:
        raise MotorPathwayError("pinned Phase 6A reference artifact was not found.")
    if reference.result.dataset != MALECNS_DATASET:
        raise MotorPathwayError("reference artifact dataset is incompatible.")

    base_config = reference.result.config
    reference_stimulus = base_config.stimulus
    static_far_field = replace(
        reference_stimulus,
        approach_velocity_m_s=0.0,
        initial_distance_m=1_000_000.0,
    )
    scenarios = (
        (
            "reference_combined",
            replace(
                base_config,
                experiment_id="phase6c_reference_combined_v1",
                pathway_condition=PathwayCondition.COMBINED,
            ),
            MotorPathwayRunConfig(),
        ),
        (
            "static_far_field_no_loom",
            replace(
                base_config,
                experiment_id="phase6c_static_far_field_no_loom_v1",
                stimulus=static_far_field,
                pathway_condition=PathwayCondition.COMBINED,
            ),
            MotorPathwayRunConfig(),
        ),
        (
            "dnp01_to_ttmn_output_silenced",
            replace(
                base_config,
                experiment_id="phase6c_dnp01_to_ttmn_output_silenced_v1",
                pathway_condition=PathwayCondition.COMBINED,
            ),
            MotorPathwayRunConfig(dnp01_to_ttmn_silenced=True),
        ),
        (
            "lc4_only",
            replace(
                base_config,
                experiment_id="phase6c_lc4_only_v1",
                pathway_condition=PathwayCondition.LC4_ONLY,
            ),
            MotorPathwayRunConfig(),
        ),
        (
            "lplc2_only",
            replace(
                base_config,
                experiment_id="phase6c_lplc2_only_v1",
                pathway_condition=PathwayCondition.LPLC2_ONLY,
            ),
            MotorPathwayRunConfig(),
        ),
    )
    runner = MotorPathwayExperimentRunner(circuit_contract)
    destination_root = Path(output_root)
    artifacts = []
    for name, experiment_config, motor_config in scenarios:
        result = runner.run(experiment_config, motor_config)
        artifacts.append(export_motor_pathway_artifact(result, destination_root / name))
    return tuple(artifacts)


def main() -> int:
    """Run the five reproducible Phase 6C reference/control artifacts."""

    import argparse
    from pathlib import Path

    from neurofly.malecns.contract import load_circuit_contract

    parser = argparse.ArgumentParser(
        description="Run the bounded exploratory Phase 6C DNp01-to-TTMn slice"
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("data/derived/malecns/looming_giant_fiber_v1"),
    )
    parser.add_argument(
        "--reference-artifact-root",
        type=Path,
        default=Path("data/derived/experiments"),
    )
    parser.add_argument(
        "--reference-artifact-id",
        default="63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656",
    )
    parser.add_argument(
        "--output-root", type=Path, default=Path("data/derived/motor_experiments")
    )
    args = parser.parse_args()
    circuit = load_circuit_contract(args.contract)
    artifacts = run_phase6c_reference_suite(
        circuit_contract=circuit,
        reference_artifact_root=str(args.reference_artifact_root),
        reference_artifact_id=args.reference_artifact_id,
        output_root=str(args.output_root),
    )
    for artifact in artifacts:
        print(f"artifact_id={artifact.artifact_id} path={artifact.path}")
        print(
            f"  upstream={artifact.upstream_artifact.artifact_id} "
            f"config={artifact.result.upstream_result.config_sha256} "
            f"condition={artifact.result.upstream_result.config.pathway_condition.value}"
        )
        print(
            f"  motor_run_config={artifact.result.run_config.sha256} "
            f"motor_result={artifact.result.result_sha256} "
            f"model={artifact.result.run_config.model.assumption_set_id}"
        )
        events_by_body: dict[int, list[float]] = {10001: [], 10010: []}
        for event in artifact.result.source_dnp01_spike_events:
            events_by_body[event.body_id].append(event.time_ms)
        for body_id, times in events_by_body.items():
            print(f"  DNp01 {body_id} source events (ms): {times}")
        for trajectory in artifact.result.ttmn_trajectories:
            print(
                f"  TTMn {trajectory.body_id} {trajectory.side}: "
                f"input_events={trajectory.input_event_count} "
                f"peak_state={trajectory.peak_state:.12g} "
                f"peak_time_ms={trajectory.peak_time_ms:.12g}"
            )
        print(
            f"  delivered_motor_inputs={len(artifact.result.delivered_motor_inputs)} "
            f"dnp01_to_ttmn_silenced="
            f"{artifact.result.run_config.dnp01_to_ttmn_silenced}"
        )
    return 0


__all__ = [
    "MOTOR_EVIDENCE_SCHEMA_VERSION",
    "MOTOR_MODEL_ID",
    "MOTOR_MODEL_VERSION",
    "MOTOR_PATHWAY_EVIDENCE",
    "MOTOR_REFERENCE_ASSUMPTION_SET",
    "MOTOR_RESULT_SCHEMA_VERSION",
    "MOTOR_STATE_UNIT",
    "MotorPathwayError",
    "MotorPathwayEvidenceContract",
    "MotorPathwayExperimentResult",
    "MotorPathwayExperimentRunner",
    "MotorPathwayRunConfig",
    "MotorSensitivityPoint",
    "TTMnInputEvent",
    "TTMnIntegratorConfig",
    "TTMnStateTrajectory",
    "UPSTREAM_CONTRACT_SHA256",
    "run_phase6c_reference_suite",
]
