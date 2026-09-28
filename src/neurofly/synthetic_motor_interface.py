"""Provenance-explicit synthetic DNp01 events for the Phase 6C TTMn model.

This bounded test path reuses Phase 6C's validated event mapper and TTMn
integrator without constructing or impersonating an upstream ExperimentResult.
It is intentionally not a general external-event injection API.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any

from neurofly.motor_pathway import (
    MOTOR_PATHWAY_EVIDENCE,
    TTMnIntegratorConfig,
    _integrate_ttmn,
    _map_motor_inputs,
)
from neurofly.simulation import SpikeEvent

FIXTURE_SCHEMA_VERSION = "synthetic_dnp01_motor_event_fixture_v1"
RESULT_SCHEMA_VERSION = "synthetic_dnp01_ttmn_interface_result_v1"
ARTIFACT_SCHEMA_VERSION = "synthetic_dnp01_ttmn_interface_artifact_v1"
SYNTHETIC_SOURCE_KIND = "SYNTHETIC_MOTOR_INTERFACE_TEST"
REFERENCE_DT_MS = 0.1
REFERENCE_INTERVAL_COUNT = 80
FIXTURE_IDS = (
    "ZERO_EVENT_CONTROL",
    "RIGHT_SINGLE_EVENT",
    "LEFT_SINGLE_EVENT",
    "BILATERAL_SIMULTANEOUS_EVENT",
    "RIGHT_REPEATED_EVENTS",
    "LEFT_REPEATED_EVENTS",
)
_DNP01_BY_BODY_ID = {
    identity["body_id"]: identity
    for identity in MOTOR_PATHWAY_EVIDENCE.dnp01_identities
}
_TTMN_BY_BODY_ID = {
    identity["body_id"]: identity for identity in MOTOR_PATHWAY_EVIDENCE.ttmn_identities
}


class SyntheticMotorInterfaceError(ValueError):
    """Invalid synthetic fixture, source identity, timing, or replay input."""


def _canonical_sha256(value: Any) -> str:
    try:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SyntheticMotorInterfaceError(
            "synthetic fixture must be deterministic JSON"
        ) from exc
    return hashlib.sha256(payload).hexdigest()


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SyntheticMotorInterfaceError(f"{label} must be a positive integer.")
    return value


def _finite_float(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise SyntheticMotorInterfaceError(f"{label} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise SyntheticMotorInterfaceError(f"{label} must be finite.") from None
    if not math.isfinite(result):
        raise SyntheticMotorInterfaceError(f"{label} must be finite.")
    return result


@dataclass(frozen=True, slots=True)
class SyntheticDNp01Event:
    """One synthetic event with identity/provenance outside SpikeEvent itself."""

    source_body_id: int
    source_side: str
    source_node_index: int
    step: int
    time_ms: float
    neuron_type: str = "DNp01"
    source_kind: str = SYNTHETIC_SOURCE_KIND

    def __post_init__(self) -> None:
        if (
            isinstance(self.source_body_id, bool)
            or not isinstance(self.source_body_id, int)
            or self.source_body_id not in _DNP01_BY_BODY_ID
        ):
            raise SyntheticMotorInterfaceError("unknown DNp01 source body.")
        identity = _DNP01_BY_BODY_ID[self.source_body_id]
        if self.source_side != identity["side"]:
            raise SyntheticMotorInterfaceError("DNp01 source side does not match body.")
        if (
            isinstance(self.source_node_index, bool)
            or not isinstance(self.source_node_index, int)
            or self.source_node_index != identity["node_index"]
        ):
            raise SyntheticMotorInterfaceError(
                "DNp01 node index does not match body identity."
            )
        if self.neuron_type != "DNp01":
            raise SyntheticMotorInterfaceError("synthetic source type must be DNp01.")
        if self.source_kind != SYNTHETIC_SOURCE_KIND:
            raise SyntheticMotorInterfaceError(
                "synthetic event source kind is unsupported."
            )
        if isinstance(self.step, bool) or not isinstance(self.step, int):
            raise SyntheticMotorInterfaceError("event step must be an integer.")
        if self.step < 1:
            raise SyntheticMotorInterfaceError("event step must be positive.")
        object.__setattr__(self, "time_ms", _finite_float(self.time_ms, "time_ms"))

    @property
    def event_id(self) -> str:
        return f"synthetic-dnp01-{self.source_body_id}-step-{self.step}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source_kind": self.source_kind,
            "source_body_id": self.source_body_id,
            "source_side": self.source_side,
            "source_node_index": self.source_node_index,
            "neuron_type": self.neuron_type,
            "step": self.step,
            "time_ms": self.time_ms,
        }

    def to_spike_event(self) -> SpikeEvent:
        """Convert only after this containing synthetic fixture is validated."""

        return SpikeEvent(
            time_ms=self.time_ms,
            step=self.step,
            body_id=self.source_body_id,
            node_index=self.source_node_index,
            neuron_type=self.neuron_type,
        )


@dataclass(frozen=True, slots=True)
class SyntheticDNp01FixtureConfig:
    """Fixed-grid, synthetic-only input contract for one named fixture."""

    fixture_id: str
    events: tuple[SyntheticDNp01Event, ...]
    dt_ms: float = REFERENCE_DT_MS
    interval_count: int = REFERENCE_INTERVAL_COUNT
    source_kind: str = SYNTHETIC_SOURCE_KIND
    sensory_source_artifact_id: None = None
    schema_version: str = FIXTURE_SCHEMA_VERSION
    motor_model: TTMnIntegratorConfig = field(default_factory=TTMnIntegratorConfig)

    def __post_init__(self) -> None:
        if self.schema_version != FIXTURE_SCHEMA_VERSION:
            raise SyntheticMotorInterfaceError("unsupported fixture schema.")
        if self.fixture_id not in FIXTURE_IDS:
            raise SyntheticMotorInterfaceError("unsupported fixture identity.")
        if self.source_kind != SYNTHETIC_SOURCE_KIND:
            raise SyntheticMotorInterfaceError("fixture source kind must be synthetic.")
        if self.sensory_source_artifact_id is not None:
            raise SyntheticMotorInterfaceError(
                "synthetic fixture cannot reference a sensory event artifact."
            )
        dt_ms = _finite_float(self.dt_ms, "dt_ms")
        if dt_ms <= 0:
            raise SyntheticMotorInterfaceError("dt_ms must be positive.")
        interval_count = _positive_int(self.interval_count, "interval_count")
        if not isinstance(self.motor_model, TTMnIntegratorConfig):
            raise SyntheticMotorInterfaceError("motor model config is invalid.")
        if self.motor_model != TTMnIntegratorConfig():
            raise SyntheticMotorInterfaceError(
                "fixture must use the committed Phase 6C reference assumptions."
            )
        events = tuple(self.events)
        if any(not isinstance(event, SyntheticDNp01Event) for event in events):
            raise SyntheticMotorInterfaceError("fixture events are malformed.")
        expected_order = tuple(
            sorted(events, key=lambda event: (event.step, event.source_body_id))
        )
        if events != expected_order:
            raise SyntheticMotorInterfaceError(
                "fixture events must use deterministic step/body ordering."
            )
        event_keys = [(event.source_body_id, event.step) for event in events]
        if len(event_keys) != len(set(event_keys)):
            raise SyntheticMotorInterfaceError(
                "a DNp01 body cannot emit duplicate events at one step."
            )
        for event in events:
            if event.source_kind != self.source_kind:
                raise SyntheticMotorInterfaceError(
                    "event and fixture provenance differ."
                )
            if event.step > interval_count:
                raise SyntheticMotorInterfaceError(
                    "event step is outside the fixture duration."
                )
            # Strict equality is intentional: integer steps define event time.
            if event.time_ms != event.step * dt_ms:
                raise SyntheticMotorInterfaceError(
                    "event time_ms must exactly equal step * dt_ms."
                )
        object.__setattr__(self, "dt_ms", dt_ms)
        object.__setattr__(self, "interval_count", interval_count)
        object.__setattr__(self, "events", events)

    def to_dict(self) -> dict[str, Any]:
        value = {
            "schema_version": self.schema_version,
            "fixture_id": self.fixture_id,
            "source_kind": self.source_kind,
            "sensory_source_artifact_id": self.sensory_source_artifact_id,
            "sensory_generated_events": False,
            "purpose": (
                "Validate the synthetic DNp01-event to TTMn model-state interface."
            ),
            "dt_ms": self.dt_ms,
            "interval_count": self.interval_count,
            "event_time_semantics": "time_ms_equals_integer_step_times_dt_ms_v1",
            "events": [event.to_dict() for event in self.events],
            "motor_model": self.motor_model.to_dict(),
            "motor_evidence_contract_sha256": MOTOR_PATHWAY_EVIDENCE.sha256,
        }
        config_sha256 = _canonical_sha256(value)
        value["fixture_config_sha256"] = config_sha256
        value["synthetic_run_id"] = (
            f"synthetic_motor_interface_run_v1:{self.fixture_id}:{config_sha256}"
        )
        return value


def _event(body_id: int, step: int, dt_ms: float) -> SyntheticDNp01Event:
    identity = _DNP01_BY_BODY_ID[body_id]
    return SyntheticDNp01Event(
        source_body_id=body_id,
        source_side=identity["side"],
        source_node_index=identity["node_index"],
        step=step,
        time_ms=step * dt_ms,
    )


def build_reference_fixture_battery() -> tuple[SyntheticDNp01FixtureConfig, ...]:
    """Return the six predeclared fixtures; no sensory/model outcomes select them."""

    dt_ms = REFERENCE_DT_MS
    right_single = (_event(10001, 10, dt_ms),)
    left_single = (_event(10010, 10, dt_ms),)
    right_repeated = (_event(10001, 10, dt_ms), _event(10001, 30, dt_ms))
    left_repeated = (_event(10010, 10, dt_ms), _event(10010, 30, dt_ms))
    event_sets = (
        (),
        right_single,
        left_single,
        (_event(10001, 10, dt_ms), _event(10010, 10, dt_ms)),
        right_repeated,
        left_repeated,
    )
    return tuple(
        SyntheticDNp01FixtureConfig(fixture_id=fixture_id, events=events)
        for fixture_id, events in zip(FIXTURE_IDS, event_sets, strict=True)
    )


def _source_contract_identity(circuit_contract: Any) -> dict[str, Any]:
    MOTOR_PATHWAY_EVIDENCE.validate_upstream_contract(circuit_contract)
    return {
        "candidate_identifier": circuit_contract.candidate.identifier,
        "candidate_version": circuit_contract.candidate.version,
        "dataset": circuit_contract.provenance.dataset,
        "source_hashes": [
            list(pair) for pair in sorted(circuit_contract.integrity.sha256_by_file)
        ],
        "upstream_contract_sha256": MOTOR_PATHWAY_EVIDENCE.upstream_contract_sha256,
    }


def _expected_source_contract_identity() -> dict[str, Any]:
    return {
        "candidate_identifier": MOTOR_PATHWAY_EVIDENCE.upstream_candidate_identifier,
        "candidate_version": MOTOR_PATHWAY_EVIDENCE.upstream_candidate_version,
        "dataset": MOTOR_PATHWAY_EVIDENCE.dataset,
        "source_hashes": [
            list(pair) for pair in MOTOR_PATHWAY_EVIDENCE.upstream_source_hashes
        ],
        "upstream_contract_sha256": MOTOR_PATHWAY_EVIDENCE.upstream_contract_sha256,
    }


def _route_records() -> list[dict[str, Any]]:
    dnp01 = _DNP01_BY_BODY_ID
    ttmn = _TTMN_BY_BODY_ID
    records = []
    for edge in MOTOR_PATHWAY_EVIDENCE.chemical_edges:
        source = dnp01[edge["pre_body_id"]]
        target = ttmn[edge["post_body_id"]]
        records.append(
            {
                "source_body_id": source["body_id"],
                "source_type": source["type"],
                "source_side": source["side"],
                "target_body_id": target["body_id"],
                "target_type": target["type"],
                "target_side": target["side"],
                "structural_weight": edge["structural_weight"],
                "structural_weight_semantics": "SOURCE_STRUCTURAL_COUNT_ONLY",
            }
        )
    return records


def build_fixture_configuration(
    circuit_contract: Any,
) -> dict[str, Any]:
    """Build the content-addressed battery config after validating source hashes."""

    source_identity = _source_contract_identity(circuit_contract)
    fixture_configs = [config.to_dict() for config in build_reference_fixture_battery()]
    value = {
        "schema_version": "synthetic_dnp01_ttmn_interface_config_v1",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "sensory_source_artifact_id": None,
        "statement": "No sensory experiment generated these synthetic events.",
        "source_circuit_contract_identity": source_identity,
        "routing_evidence_contract": MOTOR_PATHWAY_EVIDENCE.to_dict(),
        "routing_evidence_contract_sha256": MOTOR_PATHWAY_EVIDENCE.sha256,
        "verified_routes": _route_records(),
        "motor_model": TTMnIntegratorConfig().to_dict(),
        "transmission_delay": {
            "modeled_additional_delay_ms": 0.0,
            "classification": "MODEL_ASSUMPTION",
            "semantics": "same_boundary_as_dnp01_event_v1",
        },
        "population_normalization": "none",
        "structural_weight_numerical_use": "none_source_metadata_only",
        "scientific_boundary": {
            "identity_and_route": "MALECNS_STRUCTURAL_EVIDENCE",
            "event": "SYNTHETIC_TEST_FIXTURE",
            "ttmn_state": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
            "structural_count": "SOURCE_METADATA_ONLY",
            "muscle_or_behavior_model": False,
            "phase7o_event_source": False,
        },
        "fixture_configs": fixture_configs,
    }
    value["config_sha256"] = _canonical_sha256(value)
    return value


def _expected_fixture_configuration() -> dict[str, Any]:
    fixture_configs = [config.to_dict() for config in build_reference_fixture_battery()]
    value = {
        "schema_version": "synthetic_dnp01_ttmn_interface_config_v1",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "sensory_source_artifact_id": None,
        "statement": "No sensory experiment generated these synthetic events.",
        "source_circuit_contract_identity": _expected_source_contract_identity(),
        "routing_evidence_contract": MOTOR_PATHWAY_EVIDENCE.to_dict(),
        "routing_evidence_contract_sha256": MOTOR_PATHWAY_EVIDENCE.sha256,
        "verified_routes": _route_records(),
        "motor_model": TTMnIntegratorConfig().to_dict(),
        "transmission_delay": {
            "modeled_additional_delay_ms": 0.0,
            "classification": "MODEL_ASSUMPTION",
            "semantics": "same_boundary_as_dnp01_event_v1",
        },
        "population_normalization": "none",
        "structural_weight_numerical_use": "none_source_metadata_only",
        "scientific_boundary": {
            "identity_and_route": "MALECNS_STRUCTURAL_EVIDENCE",
            "event": "SYNTHETIC_TEST_FIXTURE",
            "ttmn_state": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
            "structural_count": "SOURCE_METADATA_ONLY",
            "muscle_or_behavior_model": False,
            "phase7o_event_source": False,
        },
        "fixture_configs": fixture_configs,
    }
    value["config_sha256"] = _canonical_sha256(value)
    return value


def _run_fixture(
    fixture: SyntheticDNp01FixtureConfig,
) -> dict[str, Any]:
    events = tuple(event.to_spike_event() for event in fixture.events)
    inputs = _map_motor_inputs(
        events,
        dt_ms=fixture.dt_ms,
        steps=fixture.interval_count,
        model=fixture.motor_model,
        evidence_contract=MOTOR_PATHWAY_EVIDENCE,
    )
    times_ms = tuple(step * fixture.dt_ms for step in range(fixture.interval_count + 1))
    trajectories = _integrate_ttmn(
        times_ms=times_ms,
        dt_ms=fixture.dt_ms,
        inputs=inputs,
        model=fixture.motor_model,
        evidence_contract=MOTOR_PATHWAY_EVIDENCE,
    )
    return {
        "fixture_id": fixture.fixture_id,
        "fixture_config_sha256": fixture.to_dict()["fixture_config_sha256"],
        "synthetic_run_id": fixture.to_dict()["synthetic_run_id"],
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "sensory_source_artifact_id": None,
        "source_events": [event.to_dict() for event in fixture.events],
        "mapped_motor_inputs": [item.to_dict() for item in inputs],
        "ttmn_model_state": [item.to_dict() for item in trajectories],
    }


def execute_reference_battery(
    circuit_contract: Any,
    *,
    fixtures: tuple[SyntheticDNp01FixtureConfig, ...] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the fixed synthetic battery through Phase 6C's pure primitives.

    A composing phase may pass the already-validated immutable fixture objects
    so parallel branches share one logical upstream event set. The supplied
    objects must serialize exactly to the canonical six-fixture battery.
    """

    config = build_fixture_configuration(circuit_contract)
    canonical_fixtures = build_reference_fixture_battery()
    selected_fixtures = canonical_fixtures if fixtures is None else tuple(fixtures)
    if tuple(item.to_dict() for item in selected_fixtures) != tuple(
        item.to_dict() for item in canonical_fixtures
    ):
        raise SyntheticMotorInterfaceError(
            "supplied fixtures differ from the canonical six-fixture battery."
        )
    results = [_run_fixture(fixture) for fixture in selected_fixtures]
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "sensory_source_artifact_id": None,
        "provenance_semantics": "SYNTHETIC_MOTOR_INTERFACE_TEST_ONLY",
        "time_alignment": "event_step_is_ttmn_state_boundary_v1",
        "scientific_boundary": {
            "identity_and_route": "MALECNS_STRUCTURAL_EVIDENCE",
            "event": "SYNTHETIC_TEST_FIXTURE",
            "ttmn_state": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
            "structural_count": "SOURCE_METADATA_ONLY",
            "muscle_or_behavior_model": False,
            "phase7o_event_source": False,
        },
        "fixtures": results,
    }
    result["result_sha256"] = _canonical_sha256(result)
    return config, result


def validate_and_replay_payload(
    config: dict[str, Any], result: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate a stored fixture payload against the fixed config and equation."""

    if config != _expected_fixture_configuration():
        raise SyntheticMotorInterfaceError(
            "synthetic fixture source/config identity mismatch."
        )
    if (
        result.get("schema_version") != RESULT_SCHEMA_VERSION
        or result.get("source_kind") != SYNTHETIC_SOURCE_KIND
        or result.get("sensory_source_artifact_id") is not None
        or result.get("provenance_semantics") != "SYNTHETIC_MOTOR_INTERFACE_TEST_ONLY"
    ):
        raise SyntheticMotorInterfaceError("unsupported synthetic result semantics.")
    recomputed = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "sensory_source_artifact_id": None,
        "provenance_semantics": "SYNTHETIC_MOTOR_INTERFACE_TEST_ONLY",
        "time_alignment": "event_step_is_ttmn_state_boundary_v1",
        "scientific_boundary": {
            "identity_and_route": "MALECNS_STRUCTURAL_EVIDENCE",
            "event": "SYNTHETIC_TEST_FIXTURE",
            "ttmn_state": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
            "structural_count": "SOURCE_METADATA_ONLY",
            "muscle_or_behavior_model": False,
            "phase7o_event_source": False,
        },
        "fixtures": [
            _run_fixture(fixture) for fixture in build_reference_fixture_battery()
        ],
    }
    recomputed["result_sha256"] = _canonical_sha256(recomputed)
    if result != recomputed:
        raise SyntheticMotorInterfaceError(
            "synthetic event or TTMn state differs from the fixture model."
        )
    return config, recomputed


def replay_synthetic_fixture_configuration(
    config: dict[str, Any], circuit_contract: Any
) -> None:
    """Fail closed if a caller's pinned local CircuitContract differs."""

    expected_source = _source_contract_identity(circuit_contract)
    if config.get("source_circuit_contract_identity") != expected_source:
        raise SyntheticMotorInterfaceError("source CircuitContract identity mismatch.")
    if config != _expected_fixture_configuration():
        raise SyntheticMotorInterfaceError("synthetic fixture config mismatch.")


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "FIXTURE_IDS",
    "FIXTURE_SCHEMA_VERSION",
    "REFERENCE_DT_MS",
    "REFERENCE_INTERVAL_COUNT",
    "RESULT_SCHEMA_VERSION",
    "SYNTHETIC_SOURCE_KIND",
    "SyntheticDNp01Event",
    "SyntheticDNp01FixtureConfig",
    "SyntheticMotorInterfaceError",
    "build_fixture_configuration",
    "build_reference_fixture_battery",
    "execute_reference_battery",
    "replay_synthetic_fixture_configuration",
    "validate_and_replay_payload",
]
