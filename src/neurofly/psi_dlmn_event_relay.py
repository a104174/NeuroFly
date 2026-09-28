"""Bounded Phase 8G synthetic DNp01-to-PSI-to-DLMn event relay.

This module creates identity-resolved route records only. PSI and DLMn do not
receive latent states or simulated SpikeEvent objects.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.motor_neural_contract import (
    DEFAULT_ARTIFACT_ROOT as MOTOR_CONTRACT_ROOT,
)
from neurofly.motor_neural_contract import (
    MOTOR_NEURAL_CONTRACT_SCHEMA,
    canonical_sha256,
    load_pinned_artifact,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_interface import (
    FIXTURE_IDS,
    SYNTHETIC_SOURCE_KIND,
    SyntheticDNp01FixtureConfig,
    build_reference_fixture_battery,
)

RELAY_SCHEMA_VERSION = "psi_dlmn_event_relay_v1"
PSI_EVENT_SCHEMA_VERSION = "psi_routed_event_v1"
DLMN_EVENT_SCHEMA_VERSION = "dlmn_routed_event_v1"
RESULT_SCHEMA_VERSION = "synthetic_psi_dlmn_event_relay_result_v1"
ARTIFACT_SCHEMA_VERSION = "synthetic_psi_dlmn_event_relay_artifact_v1"
RELAY_SEMANTICS = "EXPLORATORY_ROUTED_MOTOR_EVENT"
ACTIVE_ROUTE_POLICY_ID = RELAY_SCHEMA_VERSION
SENSORY_SOURCE_KIND = "SIMULATED_FROM_SENSORY_EXPERIMENT"
EXPECTED_MOTOR_CONTRACT_ID = (
    "a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c"
)
EXPECTED_QUERY_RESPONSE_SHA256 = (
    "845c1c1ddc60183fd02f8ac2ceaac5e1a16cba34c803707fb974e7b52861e43e"
)
DEFAULT_MOTOR_CONTRACT_PATH = MOTOR_CONTRACT_ROOT / EXPECTED_MOTOR_CONTRACT_ID
DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / "synthetic_psi_dlmn_event_relay_v1"
CONFIG_FILENAME = "relay_config.json"
RESULT_FILENAME = "relay_result.json"
MANIFEST_FILENAME = "manifest.json"


class PsiDlmnEventRelayError(ValueError):
    """Invalid pinned topology, fixture, or routed-event provenance."""


@dataclass(frozen=True, slots=True)
class ActiveRoute:
    """One source-derived edge allowed by the versioned relay policy."""

    edge_id: str
    query_group: str
    source_body_id: int
    source_type: str
    source_instance: str
    source_side: str
    target_body_id: int
    target_type: str
    target_instance: str
    target_side: str
    structural_count: int
    modality: str
    source_query_response_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "query_group": self.query_group,
            "source_body_id": self.source_body_id,
            "source_type": self.source_type,
            "source_instance": self.source_instance,
            "source_side": self.source_side,
            "target_body_id": self.target_body_id,
            "target_type": self.target_type,
            "target_instance": self.target_instance,
            "target_side": self.target_side,
            "structural_count": self.structural_count,
            "structural_count_semantics": "SOURCE_METADATA_ONLY",
            "modality": self.modality,
            "source_query_response_sha256": self.source_query_response_sha256,
        }


def _canonical_sha256(value: Any) -> str:
    try:
        return canonical_sha256(value)
    except (TypeError, ValueError) as exc:
        raise PsiDlmnEventRelayError("value is not deterministic JSON") from exc


def _event_id(prefix: str, value: dict[str, Any]) -> str:
    return f"{prefix}:{_canonical_sha256(value)}"


def _validate_pinned_motor_contract(pinned: dict[str, Any]) -> dict[str, Any]:
    if (
        not isinstance(pinned, dict)
        or not isinstance(pinned.get("contract"), dict)
        or not isinstance(pinned.get("manifest"), dict)
    ):
        raise PsiDlmnEventRelayError("a validated pinned motor contract is required")
    contract = pinned["contract"]
    if (
        contract.get("schema_version") != MOTOR_NEURAL_CONTRACT_SCHEMA
        or contract.get("contract_id") != EXPECTED_MOTOR_CONTRACT_ID
        or contract.get("source_provenance", {}).get("query_response_sha256")
        != EXPECTED_QUERY_RESPONSE_SHA256
        or pinned.get("manifest", {}).get("artifact_id") != EXPECTED_MOTOR_CONTRACT_ID
    ):
        raise PsiDlmnEventRelayError("pinned motor contract identity mismatch")
    contract_payload = {
        key: value for key, value in contract.items() if key != "contract_id"
    }
    if _canonical_sha256(contract_payload) != EXPECTED_MOTOR_CONTRACT_ID:
        raise PsiDlmnEventRelayError("pinned motor contract content hash mismatch")
    if pinned["manifest"].get("contract_sha256") != _canonical_sha256(contract):
        raise PsiDlmnEventRelayError("pinned motor contract hash mismatch")
    return contract


def load_pinned_motor_contract(
    contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load and fully replay the immutable Phase 8E source artifact offline."""

    try:
        pinned = load_pinned_artifact(Path(contract_path))
    except (OSError, ValueError) as exc:
        raise PsiDlmnEventRelayError("could not replay pinned motor contract") from exc
    _validate_pinned_motor_contract(pinned)
    return pinned


def active_routes_from_contract(pinned: dict[str, Any]) -> tuple[ActiveRoute, ...]:
    """Select only the two approved edge classes from the pinned contract."""

    contract = _validate_pinned_motor_contract(pinned)
    nodes = contract.get("nodes")
    edges = contract.get("chemical_edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise PsiDlmnEventRelayError("pinned contract nodes or edges are malformed")
    nodes_by_id = {
        item.get("body_id"): item for item in nodes if isinstance(item, dict)
    }
    if len(nodes_by_id) != len(nodes):
        raise PsiDlmnEventRelayError("pinned motor contract has duplicate nodes")
    counts = Counter(edge.get("source_query_id") for edge in edges)
    if counts != Counter(
        {
            "dnp01_to_ttmn": 2,
            "dnp01_to_psi": 4,
            "psi_to_dlmn": 10,
            "psi_to_psi_supplemental": 2,
        }
    ):
        raise PsiDlmnEventRelayError("pinned motor contract topology changed")
    if contract.get("scope", {}).get("direct_dnp01_to_candidate_dlmn_edge_count") != 0:
        raise PsiDlmnEventRelayError("unexpected direct DNp01-to-DLMn route")
    source_hash = contract["source_provenance"]["query_response_sha256"]
    routes: list[ActiveRoute] = []
    seen_edge_ids: set[str] = set()
    for edge in edges:
        group = edge["source_query_id"]
        if group not in {"dnp01_to_psi", "psi_to_dlmn"}:
            continue
        source = nodes_by_id.get(edge.get("source_body_id"))
        target = nodes_by_id.get(edge.get("target_body_id"))
        if source is None or target is None:
            raise PsiDlmnEventRelayError("route references an unknown motor node")
        expected_types = {
            "dnp01_to_psi": ("DNp01", "PSI"),
            "psi_to_dlmn": ("PSI", None),
        }[group]
        if (
            edge.get("modality") != "MALECNS_CHEMICAL_CONNECTIVITY"
            or edge.get("source_query_response_sha256") != source_hash
            or edge.get("source_type") != source.get("type")
            or edge.get("target_type") != target.get("type")
            or source.get("type") != expected_types[0]
            or (
                expected_types[1] is not None
                and target.get("type") != expected_types[1]
            )
            or (
                group == "psi_to_dlmn"
                and not str(target.get("type", "")).startswith("DLMn")
            )
            or isinstance(edge.get("structural_count"), bool)
            or not isinstance(edge.get("structural_count"), int)
            or edge["structural_count"] <= 0
            or not isinstance(edge.get("edge_id"), str)
            or edge["edge_id"] in seen_edge_ids
        ):
            raise PsiDlmnEventRelayError("active route identity or provenance mismatch")
        seen_edge_ids.add(edge["edge_id"])
        routes.append(
            ActiveRoute(
                edge_id=edge["edge_id"],
                query_group=group,
                source_body_id=source["body_id"],
                source_type=source["type"],
                source_instance=source["instance"],
                source_side=source["side"],
                target_body_id=target["body_id"],
                target_type=target["type"],
                target_instance=target["instance"],
                target_side=target["side"],
                structural_count=edge["structural_count"],
                modality=edge["modality"],
                source_query_response_sha256=source_hash,
            )
        )
    routes.sort(
        key=lambda route: (
            route.query_group,
            route.source_body_id,
            route.target_body_id,
        )
    )
    route_counts = Counter(route.query_group for route in routes)
    if route_counts != Counter({"dnp01_to_psi": 4, "psi_to_dlmn": 10}):
        raise PsiDlmnEventRelayError("active relay must contain exactly 14 routes")
    routes_by_group_and_source = Counter(
        (route.query_group, route.source_body_id) for route in routes
    )
    if routes_by_group_and_source != Counter(
        {
            ("dnp01_to_psi", 10001): 2,
            ("dnp01_to_psi", 10010): 2,
            ("psi_to_dlmn", 802401): 5,
            ("psi_to_dlmn", 903327): 5,
        }
    ):
        raise PsiDlmnEventRelayError(
            "pinned route fan-out differs from Phase 8G policy"
        )
    return tuple(routes)


def _contract_reference(pinned: dict[str, Any]) -> dict[str, Any]:
    contract = _validate_pinned_motor_contract(pinned)
    return {
        "schema_version": contract["schema_version"],
        "contract_id": contract["contract_id"],
        "dataset": contract["dataset"],
        "query_response_sha256": contract["source_provenance"]["query_response_sha256"],
        "query_definition_sha256": contract["source_provenance"][
            "query_definition_sha256"
        ],
        "annotation_source_sha256": contract["source_provenance"][
            "annotation_source_sha256"
        ],
        "contract_sha256": pinned["manifest"]["contract_sha256"],
    }


def active_edge_policy_from_contract(pinned: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable Phase 8G active-edge policy from the pinned source."""

    contract = _validate_pinned_motor_contract(pinned)
    routes = active_routes_from_contract(pinned)
    excluded = [
        {
            "edge_id": edge["edge_id"],
            "source_body_id": edge["source_body_id"],
            "target_body_id": edge["target_body_id"],
            "structural_count": edge["structural_count"],
            "query_group": edge["source_query_id"],
            "active": False,
        }
        for edge in contract["chemical_edges"]
        if edge["source_query_id"] == "psi_to_psi_supplemental"
    ]
    if len(excluded) != 2:
        raise PsiDlmnEventRelayError("supplemental PSI routes differ from contract")
    return {
        "policy_id": RELAY_SCHEMA_VERSION,
        "allowed_query_groups": ["dnp01_to_psi", "psi_to_dlmn"],
        "excluded_query_groups": [
            "dnp01_to_ttmn",
            "psi_to_psi_supplemental",
            "dnp01_to_candidate_dlmn",
        ],
        "propagation_layers": 2,
        "recursive_graph_traversal": False,
        "active_routes": [route.to_dict() for route in routes],
        "excluded_supplemental_routes": excluded,
    }


def _event_record(event: Any, fixture: SyntheticDNp01FixtureConfig) -> dict[str, Any]:
    fixture_dict = fixture.to_dict()
    spike = event.to_spike_event()
    spike_fields = {
        "body_id": spike.body_id,
        "node_index": spike.node_index,
        "neuron_type": spike.neuron_type,
        "step": spike.step,
        "time_ms": spike.time_ms,
    }
    if (
        isinstance(event.step, bool)
        or not isinstance(event.step, int)
        or event.step < 1
        or not math.isfinite(event.time_ms)
        or event.step > fixture.interval_count
        or event.time_ms != event.step * fixture.dt_ms
        or spike_fields["body_id"] != event.source_body_id
        or spike_fields["node_index"] != event.source_node_index
        or spike_fields["neuron_type"] != event.neuron_type
        or spike_fields["step"] != event.step
        or spike_fields["time_ms"] != event.time_ms
        or event.source_kind != SYNTHETIC_SOURCE_KIND
    ):
        raise PsiDlmnEventRelayError("synthetic source event identity mismatch")
    return {
        **event.to_dict(),
        "spike_event": spike_fields,
        "fixture_id": fixture.fixture_id,
        "fixture_config_sha256": fixture_dict["fixture_config_sha256"],
        "synthetic_run_id": fixture_dict["synthetic_run_id"],
    }


def _routed_event_id(
    *,
    schema_version: str,
    origin_identity: dict[str, Any],
    origin_event_id: str,
    route_ids: tuple[str, ...],
    target_body_id: int,
    step: int,
    time_ms: float,
    contract_id: str,
) -> str:
    return _event_id(
        schema_version,
        {
            "schema_version": schema_version,
            "relay_semantics": RELAY_SCHEMA_VERSION,
            **origin_identity,
            "origin_event_id": origin_event_id,
            "route_ids": list(route_ids),
            "target_body_id": target_body_id,
            "step": step,
            "time_ms": time_ms,
            "motor_contract_id": contract_id,
        },
    )


def _propagate_origin_events(
    source_events: list[dict[str, Any]],
    routes: tuple[ActiveRoute, ...],
    contract_reference: dict[str, Any],
    *,
    source_kind: str,
    origin_identity: dict[str, Any],
    context_fields: dict[str, Any],
    dt_ms: float,
    maximum_step: int,
) -> dict[str, Any]:
    """Route already-validated origin records through exactly two edge layers.

    This is the single Phase 8G/8H fan-out implementation. Source adapters
    validate their own provenance before invoking it; PSI↔PSI is never walked.
    """

    if source_kind not in {SYNTHETIC_SOURCE_KIND, SENSORY_SOURCE_KIND}:
        raise PsiDlmnEventRelayError("unsupported relay source provenance")
    if not math.isfinite(dt_ms) or dt_ms <= 0:
        raise PsiDlmnEventRelayError("source timestep is invalid")
    if (
        isinstance(maximum_step, bool)
        or not isinstance(maximum_step, int)
        or maximum_step < 1
    ):
        raise PsiDlmnEventRelayError("source run boundary is invalid")
    if source_kind == SYNTHETIC_SOURCE_KIND:
        if set(origin_identity) != {"synthetic_run_id"} or set(context_fields) != {
            "fixture_id",
            "fixture_config_sha256",
            "synthetic_run_id",
        }:
            raise PsiDlmnEventRelayError("synthetic source identity is malformed")
    elif (
        set(origin_identity) != {"upstream_artifact_id", "source_condition_id"}
        or set(context_fields) != {"upstream_artifact_id", "source_condition_id"}
        or not isinstance(origin_identity.get("upstream_artifact_id"), str)
        or len(origin_identity["upstream_artifact_id"]) != 64
        or any(
            char not in "0123456789abcdef"
            for char in origin_identity["upstream_artifact_id"]
        )
        or not isinstance(origin_identity.get("source_condition_id"), str)
        or not origin_identity["source_condition_id"]
    ):
        raise PsiDlmnEventRelayError("production source identity is malformed")
    dnp_routes: dict[int, list[ActiveRoute]] = {}
    psi_routes: dict[int, list[ActiveRoute]] = {}
    for route in routes:
        if route.query_group == "dnp01_to_psi":
            if route.source_type != "DNp01" or route.target_type != "PSI":
                raise PsiDlmnEventRelayError("unauthorized DNp01-to-PSI route")
            dnp_routes.setdefault(route.source_body_id, []).append(route)
        elif route.query_group == "psi_to_dlmn":
            if route.source_type != "PSI" or not route.target_type.startswith("DLMn"):
                raise PsiDlmnEventRelayError("unauthorized PSI-to-DLMn route")
            psi_routes.setdefault(route.source_body_id, []).append(route)
        else:
            raise PsiDlmnEventRelayError("relay received an excluded route class")
    if (
        sum(map(len, dnp_routes.values())) != 4
        or sum(map(len, psi_routes.values())) != 10
    ):
        raise PsiDlmnEventRelayError("active route set differs from Phase 8G policy")

    if any(not isinstance(event, dict) for event in source_events):
        raise PsiDlmnEventRelayError("source event record is malformed")
    event_ids = [event.get("event_id") for event in source_events]
    if any(not isinstance(event_id, str) or not event_id for event_id in event_ids):
        raise PsiDlmnEventRelayError("source event identity is malformed")
    if len(event_ids) != len(set(event_ids)):
        raise PsiDlmnEventRelayError("duplicate source event identity")
    for event in source_events:
        if (
            not isinstance(event, dict)
            or event.get("source_kind") != source_kind
            or isinstance(event.get("source_body_id"), bool)
            or not isinstance(event.get("source_body_id"), int)
            or event.get("neuron_type") != "DNp01"
            or event.get("source_side") not in {"L", "R"}
            or isinstance(event.get("step"), bool)
            or not isinstance(event.get("step"), int)
            or event["step"] < 1
            or event["step"] > maximum_step
            or isinstance(event.get("time_ms"), bool)
            or not isinstance(event.get("time_ms"), (int, float))
            or not math.isfinite(event["time_ms"])
            or event["time_ms"] != event["step"] * dt_ms
            or (
                source_kind == SENSORY_SOURCE_KIND
                and any(
                    event.get(key) != value for key, value in origin_identity.items()
                )
            )
        ):
            raise PsiDlmnEventRelayError("source event identity/timing is invalid")

    psi_events: list[dict[str, Any]] = []
    dlmn_events: list[dict[str, Any]] = []
    source_node_by_id: dict[int, ActiveRoute] = {}
    for route in routes:
        if route.query_group == "dnp01_to_psi":
            source_node_by_id[route.source_body_id] = route
    target_nodes: dict[int, ActiveRoute] = {}
    for route in routes:
        if route.query_group == "psi_to_dlmn":
            target_nodes[route.target_body_id] = route

    for source_event in source_events:
        body_id = source_event["source_body_id"]
        source_route = source_node_by_id.get(body_id)
        if (
            source_route is None
            or source_route.source_type != source_event["neuron_type"]
            or source_route.source_side != source_event["source_side"]
        ):
            raise PsiDlmnEventRelayError("source event differs from contract identity")
        for route in dnp_routes.get(body_id, []):
            psi_body_route = next(
                (candidate for candidate in psi_routes.get(route.target_body_id, [])),
                None,
            )
            if psi_body_route is None:
                raise PsiDlmnEventRelayError(
                    "PSI receipt has no authorized DLMn fan-out"
                )
            psi_id = _routed_event_id(
                schema_version=PSI_EVENT_SCHEMA_VERSION,
                origin_identity=origin_identity,
                origin_event_id=source_event["event_id"],
                route_ids=(route.edge_id,),
                target_body_id=route.target_body_id,
                step=source_event["step"],
                time_ms=source_event["time_ms"],
                contract_id=contract_reference["contract_id"],
            )
            psi_record = {
                "schema_version": PSI_EVENT_SCHEMA_VERSION,
                "event_id": psi_id,
                "event_semantics": RELAY_SEMANTICS,
                "origin_source_kind": source_kind,
                "provenance_kind": RELAY_SEMANTICS,
                **context_fields,
                "origin_event_id": source_event["event_id"],
                "origin_dnp01_body_id": body_id,
                "immediate_source_body_id": body_id,
                "source_type": route.source_type,
                "source_side": route.source_side,
                "target_psi_body_id": route.target_body_id,
                "target_type": route.target_type,
                "target_instance": route.target_instance,
                "target_side": route.target_side,
                "source_step": source_event["step"],
                "source_time_ms": source_event["time_ms"],
                "routed_step": source_event["step"],
                "routed_time_ms": source_event["time_ms"],
                "route_edge_id": route.edge_id,
                "route_query_group": route.query_group,
                "structural_count": route.structural_count,
                "structural_count_semantics": "SOURCE_METADATA_ONLY",
                "motor_contract_id": contract_reference["contract_id"],
                "motor_contract_sha256": contract_reference["contract_sha256"],
                "model_semantics_id": RELAY_SCHEMA_VERSION,
            }
            psi_events.append(psi_record)
            for dlmn_route in psi_routes[route.target_body_id]:
                target = target_nodes.get(dlmn_route.target_body_id)
                if target is None:
                    raise PsiDlmnEventRelayError("DLMn target identity is missing")
                route_ids = (route.edge_id, dlmn_route.edge_id)
                dlmn_id = _routed_event_id(
                    schema_version=DLMN_EVENT_SCHEMA_VERSION,
                    origin_identity=origin_identity,
                    origin_event_id=source_event["event_id"],
                    route_ids=route_ids,
                    target_body_id=dlmn_route.target_body_id,
                    step=source_event["step"],
                    time_ms=source_event["time_ms"],
                    contract_id=contract_reference["contract_id"],
                )
                dlmn_events.append(
                    {
                        "schema_version": DLMN_EVENT_SCHEMA_VERSION,
                        "event_id": dlmn_id,
                        "event_semantics": RELAY_SEMANTICS,
                        "origin_source_kind": source_kind,
                        "provenance_kind": RELAY_SEMANTICS,
                        **context_fields,
                        "origin_event_id": source_event["event_id"],
                        "origin_dnp01_body_id": body_id,
                        "parent_psi_event_id": psi_id,
                        "psi_source_body_id": route.target_body_id,
                        "psi_source_type": route.target_type,
                        "psi_source_side": route.target_side,
                        "target_dlmn_body_id": dlmn_route.target_body_id,
                        "target_type": dlmn_route.target_type,
                        "target_instance": dlmn_route.target_instance,
                        "target_side": dlmn_route.target_side,
                        "step": source_event["step"],
                        "time_ms": source_event["time_ms"],
                        "route_edge_ids": list(route_ids),
                        "dnp01_psi_structural_count": route.structural_count,
                        "psi_dlmn_structural_count": dlmn_route.structural_count,
                        "structural_count_semantics": "SOURCE_METADATA_ONLY",
                        "motor_contract_id": contract_reference["contract_id"],
                        "motor_contract_sha256": contract_reference["contract_sha256"],
                        "model_semantics_id": RELAY_SCHEMA_VERSION,
                    }
                )
    psi_events.sort(
        key=lambda row: (
            row["routed_step"],
            row["origin_event_id"],
            row["route_edge_id"],
            row["target_psi_body_id"],
        )
    )
    dlmn_events.sort(
        key=lambda row: (
            row["step"],
            row["origin_event_id"],
            tuple(row["route_edge_ids"]),
            row["target_dlmn_body_id"],
        )
    )
    return {
        "source_kind": source_kind,
        "event_semantics": RELAY_SEMANTICS,
        "source_events": source_events,
        "psi_routed_events": psi_events,
        "dlmn_routed_events": dlmn_events,
        "supplemental_psi_to_psi_propagated_event_count": 0,
        "counts": {
            "source_events": len(source_events),
            "psi_routed_events": len(psi_events),
            "dlmn_routed_events": len(dlmn_events),
        },
        "timing_semantics": "zero_added_delay_same_integer_boundary_v1",
    }


def _propagate_fixture(
    fixture: SyntheticDNp01FixtureConfig,
    routes: tuple[ActiveRoute, ...],
    contract_reference: dict[str, Any],
) -> dict[str, Any]:
    """Validate a Phase 8B fixture, then call the shared two-layer relay."""

    if fixture.source_kind != SYNTHETIC_SOURCE_KIND:
        raise PsiDlmnEventRelayError("relay accepts synthetic fixture inputs only")
    fixture_dict = fixture.to_dict()
    source_events = [_event_record(event, fixture) for event in fixture.events]
    result = _propagate_origin_events(
        source_events,
        routes,
        contract_reference,
        source_kind=SYNTHETIC_SOURCE_KIND,
        origin_identity={"synthetic_run_id": fixture_dict["synthetic_run_id"]},
        context_fields={
            "fixture_id": fixture.fixture_id,
            "fixture_config_sha256": fixture_dict["fixture_config_sha256"],
            "synthetic_run_id": fixture_dict["synthetic_run_id"],
        },
        dt_ms=fixture.dt_ms,
        maximum_step=fixture.interval_count,
    )
    return {
        "fixture_id": fixture.fixture_id,
        "fixture_config_sha256": fixture_dict["fixture_config_sha256"],
        "synthetic_run_id": fixture_dict["synthetic_run_id"],
        **result,
    }


def build_relay_configuration(pinned: dict[str, Any]) -> dict[str, Any]:
    """Build a content-addressed run config from the pinned contract and 8B fixtures."""

    _validate_pinned_motor_contract(pinned)
    payload = {
        "schema_version": "synthetic_psi_dlmn_event_relay_config_v1",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "relay_schema_version": RELAY_SCHEMA_VERSION,
        "motor_contract": _contract_reference(pinned),
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "derived_event_semantics": RELAY_SEMANTICS,
        "active_edge_policy": active_edge_policy_from_contract(pinned),
        "fixtures": [
            fixture.to_dict() for fixture in build_reference_fixture_battery()
        ],
        "timing": {
            "modeled_additional_delay_ms": 0.0,
            "classification": "ZERO_ADDED_DELAY_EXPLORATORY_ASSUMPTION",
            "semantics": "copy_source_integer_step_and_time_exactly",
        },
        "structural_count_numerical_use": "none_source_metadata_only",
        "latent_psi_or_dlmn_state": False,
        "psi_or_dlmn_spike_event_emission": False,
        "population_normalization": "none",
        "phase7o_production_input": False,
        "phase6c_ttmn_branch_modified": False,
        "scientific_boundary": {
            "topology": "PINNED_MALECNS_STRUCTURAL_CONTRACT",
            "input": "SYNTHETIC_MOTOR_INTERFACE_TEST",
            "derived_records": RELAY_SEMANTICS,
            "psi_dlmn_latent_state": False,
            "muscle_or_behavior_model": False,
        },
    }
    payload["config_sha256"] = _canonical_sha256(payload)
    return payload


def _expected_configuration(pinned: dict[str, Any]) -> dict[str, Any]:
    return build_relay_configuration(pinned)


def execute_reference_relay(
    pinned: dict[str, Any],
    *,
    fixtures: tuple[SyntheticDNp01FixtureConfig, ...] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Execute the six fixed Phase 8B fixtures through the two relay layers.

    A composing phase may supply the same immutable fixture objects already
    consumed by another branch. Their serialized values must equal the
    canonical battery; default execution and artifact identity remain stable.
    """

    return _run_payload_from_config(pinned, fixtures=fixtures)


def validate_and_replay_payload(
    config: dict[str, Any], result: dict[str, Any], pinned: dict[str, Any]
) -> None:
    """Fail closed on configuration/result tampering or source mismatch."""

    expected_config = _expected_configuration(pinned)
    if config != expected_config:
        raise PsiDlmnEventRelayError("stored relay configuration differs from replay")
    config_payload = {
        key: value for key, value in config.items() if key != "config_sha256"
    }
    if config.get("config_sha256") != _canonical_sha256(config_payload):
        raise PsiDlmnEventRelayError("relay configuration hash mismatch")
    if (
        not isinstance(result, dict)
        or result.get("schema_version") != RESULT_SCHEMA_VERSION
    ):
        raise PsiDlmnEventRelayError("unsupported relay result schema")
    result_payload = {
        key: value for key, value in result.items() if key != "result_sha256"
    }
    if result.get("result_sha256") != _canonical_sha256(result_payload):
        raise PsiDlmnEventRelayError("relay result hash mismatch")
    expected_config, expected_result = _run_payload_from_config(pinned)
    if config != expected_config or result != expected_result:
        raise PsiDlmnEventRelayError("relay result differs from deterministic replay")


def _run_payload_from_config(
    pinned: dict[str, Any],
    *,
    fixtures: tuple[SyntheticDNp01FixtureConfig, ...] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Internal replay builder that avoids recursive validation."""

    config = build_relay_configuration(pinned)
    routes = active_routes_from_contract(pinned)
    reference = config["motor_contract"]
    canonical_fixtures = build_reference_fixture_battery()
    selected_fixtures = canonical_fixtures if fixtures is None else tuple(fixtures)
    if tuple(item.to_dict() for item in selected_fixtures) != tuple(
        item.to_dict() for item in canonical_fixtures
    ):
        raise PsiDlmnEventRelayError(
            "supplied fixtures differ from the canonical six-fixture battery"
        )
    fixture_results = [
        _propagate_fixture(fixture, routes, reference) for fixture in selected_fixtures
    ]
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "relay_schema_version": RELAY_SCHEMA_VERSION,
        "config_sha256": config["config_sha256"],
        "motor_contract_id": reference["contract_id"],
        "motor_contract_sha256": reference["contract_sha256"],
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "event_semantics": RELAY_SEMANTICS,
        "sensory_source_artifact_id": None,
        "fixtures": fixture_results,
        "summary": {
            "fixture_count": len(fixture_results),
            "source_event_count": sum(
                item["counts"]["source_events"] for item in fixture_results
            ),
            "psi_routed_event_count": sum(
                item["counts"]["psi_routed_events"] for item in fixture_results
            ),
            "dlmn_routed_event_count": sum(
                item["counts"]["dlmn_routed_events"] for item in fixture_results
            ),
            "supplemental_psi_to_psi_propagated_event_count": 0,
        },
        "scientific_boundary": {
            "source_identity_and_routes": "MALECNS_STRUCTURAL_EVIDENCE",
            "input_event": SYNTHETIC_SOURCE_KIND,
            "routed_records": RELAY_SEMANTICS,
            "psi_dlmn_neural_state": False,
            "biological_spike_claim": False,
            "muscle_or_behavior_output": False,
        },
    }
    result["result_sha256"] = _canonical_sha256(result)
    return config, result


def replay_relay_configuration(
    config: dict[str, Any], pinned: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Rebuild a stored reference config and routed-event result exactly."""

    expected_config, result = _run_payload_from_config(pinned)
    if config != expected_config:
        raise PsiDlmnEventRelayError("relay config does not match pinned reference")
    return expected_config, result


def reference_fixture_ids() -> tuple[str, ...]:
    """Return the exact inherited Phase 8B fixture identities."""

    return FIXTURE_IDS


__all__ = [
    "ACTIVE_ROUTE_POLICY_ID",
    "ActiveRoute",
    "ARTIFACT_SCHEMA_VERSION",
    "DEFAULT_ARTIFACT_ROOT",
    "DEFAULT_MOTOR_CONTRACT_PATH",
    "DLMN_EVENT_SCHEMA_VERSION",
    "EXPECTED_MOTOR_CONTRACT_ID",
    "PSI_EVENT_SCHEMA_VERSION",
    "PsiDlmnEventRelayError",
    "RELAY_SCHEMA_VERSION",
    "RELAY_SEMANTICS",
    "RESULT_SCHEMA_VERSION",
    "SYNTHETIC_SOURCE_KIND",
    "SENSORY_SOURCE_KIND",
    "active_routes_from_contract",
    "active_edge_policy_from_contract",
    "build_relay_configuration",
    "execute_reference_relay",
    "load_pinned_motor_contract",
    "reference_fixture_ids",
    "replay_relay_configuration",
    "validate_and_replay_payload",
]
