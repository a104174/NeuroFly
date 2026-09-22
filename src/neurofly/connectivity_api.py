"""Read-only fixed-sample structural projection from a validated CircuitContract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.malecns.contract import CircuitContract, load_circuit_contract
from neurofly.malecns.errors import MaleCNSValidationError, SnapshotIntegrityError

STRUCTURAL_CONNECTIVITY_SCHEMA = "malecns_structural_connectivity_v1"
STRUCTURAL_CONNECTIVITY_PROJECTION_ID = "phase5i_six_body_visual_to_dnp01_v1"
STRUCTURAL_CONNECTIVITY_BODY_IDS = (10001, 10010, 11498, 12032, 14465, 16128)
STRUCTURAL_CONNECTIVITY_IDENTITIES = {
    10001: (0, "DNp01", "R"),
    10010: (1, "DNp01", "L"),
    11498: (2, "LPLC2", "L"),
    12032: (3, "LC4", "L"),
    14465: (12, "LPLC2", "R"),
    16128: (16, "LC4", "R"),
}
STRUCTURAL_WEIGHT_SOURCE = "neuPrint ConnectsTo.weight"
STRUCTURAL_CONNECTIVITY_SOURCE_HASHES = {
    "neurons.jsonl": "00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e",
    "connections.jsonl": (
        "f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a"
    ),
}
STRUCTURAL_CONNECTIVITY_SOURCE_METADATA = {
    "source": "Janelia neuPrint / MaleCNS",
    "endpoint": "https://neuprint.janelia.org",
    "dataset": "male-cns:v1.0",
    "acquired_at_utc": "2026-09-10T20:39:56.889520+00:00",
    "neuprint_python_version": "0.6.3",
}


class ConnectivityApiError(RuntimeError):
    """Base failure for the read-only connectivity application boundary."""


class ConnectivitySourceUnavailableError(ConnectivityApiError):
    """The CircuitContract root is not configured."""


class CircuitContractNotFoundError(ConnectivityApiError):
    """The configured root does not contain a CircuitContract snapshot."""


class InvalidCircuitContractError(ConnectivityApiError):
    """The local CircuitContract failed parsing or integrity validation."""


class ConnectivityProvenanceError(ConnectivityApiError):
    """The loaded contract does not match the pinned projection identities."""


class UnsupportedConnectivityProjectionError(ConnectivityApiError):
    """The requested projection is outside the fixed Phase 5I sample."""


def _body_identity(contract: CircuitContract, body_id: int) -> dict[str, Any]:
    neuron = contract.neurons_by_body_id[body_id]
    node_index, neuron_type, side = STRUCTURAL_CONNECTIVITY_IDENTITIES[body_id]
    if (
        contract.node_index_by_body_id.get(body_id) != node_index
        or neuron.type != neuron_type
        or neuron.soma_side != side
        or neuron.status != "Traced"
        or neuron.dataset != contract.candidate.dataset
    ):
        raise ConnectivityProvenanceError("CircuitContract body identity mismatch")
    return {
        "body_id": body_id,
        "node_index": node_index,
        "neuron_type": neuron_type,
        "source_side": side,
        "source_status": neuron.status,
    }


def _validate_contract(
    contract: CircuitContract,
) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    if (
        contract.candidate.identifier != "looming_giant_fiber_v1"
        or contract.candidate.version != 1
        or contract.candidate.dataset != "male-cns:v1.0"
        or {
            "source": contract.provenance.source,
            "endpoint": contract.provenance.endpoint,
            "dataset": contract.provenance.dataset,
            "acquired_at_utc": contract.provenance.acquired_at_utc,
            "neuprint_python_version": contract.provenance.neuprint_python_version,
        }
        != STRUCTURAL_CONNECTIVITY_SOURCE_METADATA
        or not contract.integrity.sha256_verified
        or not contract.integrity.record_counts_verified
    ):
        raise ConnectivityProvenanceError("CircuitContract provenance mismatch")
    expected_hash_files = {"neurons.jsonl", "connections.jsonl"}
    hashes = dict(contract.integrity.sha256_by_file)
    if (
        set(hashes) != expected_hash_files
        or hashes != STRUCTURAL_CONNECTIVITY_SOURCE_HASHES
        or any(
            len(value) != 64 or any(char not in "0123456789abcdef" for char in value)
            for value in hashes.values()
        )
    ):
        raise ConnectivityProvenanceError(
            "CircuitContract integrity provenance mismatch"
        )

    identities: dict[int, dict[str, Any]] = {}
    try:
        for body_id in STRUCTURAL_CONNECTIVITY_BODY_IDS:
            identities[body_id] = _body_identity(contract, body_id)
    except KeyError:
        raise ConnectivityProvenanceError(
            "CircuitContract is missing a required body"
        ) from None

    manifest = contract.source_manifest
    if (
        manifest.get("structural_weight_source") != STRUCTURAL_WEIGHT_SOURCE
        or manifest.get("structural_weight_is_physiological_coupling") is not False
    ):
        raise ConnectivityProvenanceError(
            "CircuitContract structural-weight provenance mismatch"
        )
    provenance = {
        "source": contract.provenance.source,
        "endpoint": contract.provenance.endpoint,
        "dataset": contract.provenance.dataset,
        "acquired_at_utc": contract.provenance.acquired_at_utc,
        "neuprint_python_version": contract.provenance.neuprint_python_version,
        "integrity": {
            "sha256_verified": contract.integrity.sha256_verified,
            "record_counts_verified": contract.integrity.record_counts_verified,
            "sha256_by_file": [
                {"file": name, "sha256": digest}
                for name, digest in contract.integrity.sha256_by_file
            ],
        },
        "structural_weight_source": STRUCTURAL_WEIGHT_SOURCE,
        "structural_weight_is_physiological_coupling": False,
    }
    return identities, provenance


def project_structural_connectivity(
    contract: CircuitContract,
    projection_id: str = STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
) -> dict[str, Any]:
    """Derive only the fixed six-body LC4/LPLC2 -> DNp01 source edges."""
    if projection_id != STRUCTURAL_CONNECTIVITY_PROJECTION_ID:
        raise UnsupportedConnectivityProjectionError(
            "unsupported fixed connectivity projection"
        )
    identities, provenance = _validate_contract(contract)
    fixed_ids = set(STRUCTURAL_CONNECTIVITY_BODY_IDS)
    visual_types = {"LC4", "LPLC2"}
    edges: list[dict[str, Any]] = []
    for edge in contract.connections:
        if (
            edge.source_body_id not in fixed_ids
            or edge.target_body_id not in fixed_ids
            or edge.source_type not in visual_types
            or edge.target_type != "DNp01"
        ):
            continue
        source = identities[edge.source_body_id]
        target = identities[edge.target_body_id]
        if (
            edge.source_type != source["neuron_type"]
            or edge.target_type != target["neuron_type"]
        ):
            raise ConnectivityProvenanceError("CircuitContract edge role mismatch")
        edges.append(
            {
                "pre_body_id": edge.source_body_id,
                "pre_node_index": source["node_index"],
                "pre_neuron_type": source["neuron_type"],
                "pre_source_side": source["source_side"],
                "post_body_id": edge.target_body_id,
                "post_node_index": target["node_index"],
                "post_neuron_type": target["neuron_type"],
                "post_source_side": target["source_side"],
                "structural_weight": edge.structural_weight,
            }
        )
    edges.sort(key=lambda item: (item["pre_node_index"], item["post_node_index"]))
    weight_by_source_type = {
        neuron_type: sum(
            edge["structural_weight"]
            for edge in edges
            if edge["pre_neuron_type"] == neuron_type
        )
        for neuron_type in ("LC4", "LPLC2")
    }
    return {
        "schema": STRUCTURAL_CONNECTIVITY_SCHEMA,
        "kind": "bounded_structural_connectivity",
        "dataset": contract.candidate.dataset,
        "candidate": {
            "identifier": contract.candidate.identifier,
            "version": contract.candidate.version,
        },
        "source_contract": provenance,
        "fixed_sample": {
            "id": STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
            "body_ids": list(STRUCTURAL_CONNECTIVITY_BODY_IDS),
            "bodies": [
                identities[body_id] for body_id in STRUCTURAL_CONNECTIVITY_BODY_IDS
            ],
        },
        "projection": {
            "id": STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
            "pre_neuron_types": ["LC4", "LPLC2"],
            "post_neuron_type": "DNp01",
            "direction": "pre_body_id -> post_body_id",
            "canonical_order": "pre_node_index, then post_node_index",
            "edge_semantics": (
                "directed structural ConnectsTo relationships from the CircuitContract"
            ),
        },
        "edge_semantics": {
            "weight_field": "structural_weight",
            "weight_source": STRUCTURAL_WEIGHT_SOURCE,
            "structural_weight_is_physiological_coupling": False,
        },
        "edges": edges,
        "aggregates": {
            "edge_count": len(edges),
            "total_structural_weight": sum(edge["structural_weight"] for edge in edges),
            "structural_weight_by_source_type": weight_by_source_type,
        },
    }


@dataclass(frozen=True, slots=True)
class StructuralConnectivityStore:
    """Explicit local CircuitContract root; reads never access a network."""

    root: Path

    def __init__(self, root: str | Path) -> None:
        object.__setattr__(self, "root", Path(root))

    def get_projection(
        self, projection_id: str = STRUCTURAL_CONNECTIVITY_PROJECTION_ID
    ) -> dict[str, Any]:
        if projection_id != STRUCTURAL_CONNECTIVITY_PROJECTION_ID:
            raise UnsupportedConnectivityProjectionError(
                "unsupported fixed connectivity projection"
            )
        if not self.root.is_dir() or any(
            not (self.root / filename).is_file()
            for filename in ("manifest.json", "neurons.jsonl", "connections.jsonl")
        ):
            raise CircuitContractNotFoundError("CircuitContract snapshot was not found")
        try:
            contract = load_circuit_contract(self.root)
        except (SnapshotIntegrityError, MaleCNSValidationError):
            raise InvalidCircuitContractError(
                "CircuitContract failed validation"
            ) from None
        return project_structural_connectivity(contract, projection_id)


__all__ = [
    "STRUCTURAL_CONNECTIVITY_SCHEMA",
    "STRUCTURAL_CONNECTIVITY_PROJECTION_ID",
    "STRUCTURAL_CONNECTIVITY_BODY_IDS",
    "STRUCTURAL_CONNECTIVITY_SOURCE_HASHES",
    "ConnectivityApiError",
    "ConnectivitySourceUnavailableError",
    "CircuitContractNotFoundError",
    "InvalidCircuitContractError",
    "ConnectivityProvenanceError",
    "UnsupportedConnectivityProjectionError",
    "StructuralConnectivityStore",
    "project_structural_connectivity",
]
