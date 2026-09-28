"""Pinned literature-supported motor-neuron muscle target associations.

This module joins source-verified MaleCNS motor-neuron identities to
class/group-level literature evidence. It contains no dynamics or peripheral
MaleCNS connectivity claims.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any

from neurofly.motor_neural_contract import canonical_sha256
from neurofly.psi_dlmn_event_relay import (
    DEFAULT_MOTOR_CONTRACT_PATH,
    EXPECTED_MOTOR_CONTRACT_ID,
    load_pinned_motor_contract,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT

CONTRACT_SCHEMA_VERSION = "motor_neuron_muscle_target_contract_v1"
ARTIFACT_SCHEMA_VERSION = "motor_neuron_muscle_target_artifact_v1"
MAPPING_POLICY_ID = "phase8j_literature_target_class_mapping_v1"
CONTRACT_FILENAME = "target_contract.json"
MANIFEST_FILENAME = "manifest.json"
DEFAULT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / CONTRACT_SCHEMA_VERSION


class MotorNeuronMuscleContractError(ValueError):
    """Invalid source identity, target mapping, or immutable artifact."""


_EVIDENCE_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "evidence_id": "king_wyman_1980",
        "evidence_kind": "PRIMARY_LITERATURE",
        "citation": (
            "King DG, Wyman RJ (1980), Anatomy of the giant fibre pathway in "
            "Drosophila. I."
        ),
        "doi": "10.1007/BF01205017",
        "supports": [
            "giant-fibre motor pathway anatomy",
            "ipsilateral TTM motor-neuron branch at pathway/class level",
        ],
        "does_not_establish": [
            "peripheral axon endpoint for a particular MaleCNS body ID",
            "motor-neuron-to-muscle efficacy",
        ],
    },
    {
        "evidence_id": "coggshall_1978",
        "evidence_kind": "PRIMARY_LITERATURE",
        "citation": (
            "Coggshall JC (1978), Neurons associated with the dorsal "
            "longitudinal flight muscles of Drosophila melanogaster."
        ),
        "doi": "10.1002/cne.901770410",
        "supports": [
            "DLM motor-neuron innervation at muscle-group level",
            "one motor neuron associated with the dorsal DLM group and four "
            "with the other group",
        ],
        "does_not_establish": [
            "exact MaleCNS-body-to-individual-fiber crosswalk",
            "pair-specific neuromuscular transfer parameters",
        ],
    },
    {
        "evidence_id": "augustin_2017",
        "evidence_kind": "PRIMARY_LITERATURE",
        "citation": (
            "Augustin I et al. (2017), Reduced insulin signaling maintains "
            "electrical transmission in a neural circuit in aging flies."
        ),
        "doi": "10.1371/journal.pbio.2001655",
        "supports": [
            "TTMn-to-TTM and DLM motor-neuron-to-DLM pathway classes",
            "chemical glutamatergic neuromuscular junctions at pathway level",
        ],
        "does_not_establish": [
            "MaleCNS body-specific muscle endpoint",
            "body-specific neuromuscular gain, delay, or force",
        ],
    },
    {
        "evidence_id": "kuehn_duch_2013",
        "evidence_kind": "PRIMARY_LITERATURE",
        "citation": (
            "Kuehn C, Duch C (2013), Putative Excitatory and Putative "
            "Inhibitory Inputs Localize to Different Dendritic Domains in a "
            "Drosophila Flight Motoneuron."
        ),
        "doi": "10.1111/ejn.12104",
        "supports": [
            "historical MN5 class association with the dorsal DLM group",
            "MN5 target muscle is contralateral to its soma",
        ],
        "does_not_establish": [
            "exact mapping from MaleCNS DLMn a,b body IDs to historical MN5",
            "individual muscle-fiber identity for a MaleCNS body",
        ],
    },
    {
        "evidence_id": "hurkey_2023",
        "evidence_kind": "PRIMARY_LITERATURE",
        "citation": (
            "Hürkey S et al. (2023), Gap junctions desynchronize a neural "
            "circuit to stabilize insect flight."
        ),
        "doi": "10.1038/s41586-023-06099-0",
        "supports": [
            "identified DLM motor-neuron output and muscle-group organization",
            "historical MN5 target is contralateral to its soma",
        ],
        "does_not_establish": [
            "exact MaleCNS-body-to-fiber crosswalk",
            "MaleCNS-body-specific neuromuscular parameters",
        ],
    },
)

_EVIDENCE_BY_ID = {row["evidence_id"]: row for row in _EVIDENCE_SOURCES}


def _json_bytes(value: Any, *, newline: bool = False) -> bytes:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MotorNeuronMuscleContractError(
            "contract artifact is not deterministic JSON"
        ) from exc
    return payload + (b"\n" if newline else b"")


def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _artifact_id(contract_sha256: str) -> str:
    return _hash_bytes(
        _json_bytes(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "contract_sha256": contract_sha256,
            }
        )
    )


def _source_contract(pinned: dict[str, Any]) -> dict[str, Any]:
    contract = pinned.get("contract")
    manifest = pinned.get("manifest")
    if not isinstance(contract, dict) or not isinstance(manifest, dict):
        raise MotorNeuronMuscleContractError("pinned motor contract is malformed")
    if (
        contract.get("schema_version") != "motor_neural_pathway_contract_v1"
        or contract.get("contract_id") != EXPECTED_MOTOR_CONTRACT_ID
        or manifest.get("artifact_id") != EXPECTED_MOTOR_CONTRACT_ID
        or not isinstance(manifest.get("contract_sha256"), str)
        or canonical_sha256(contract) != manifest.get("contract_sha256")
    ):
        raise MotorNeuronMuscleContractError(
            "pinned motor neural contract identity or integrity mismatch"
        )
    return contract


def _target_record(
    node: dict[str, Any], *, motor_contract_id: str, motor_contract_sha256: str
) -> dict[str, Any]:
    neuron_type = node.get("type")
    side = node.get("side")
    if side not in {"L", "R"}:
        raise MotorNeuronMuscleContractError("motor-neuron side is invalid")
    if neuron_type == "TTMn":
        target_group = None
        target_granularity = "MUSCLE_CLASS"
        target_side = side
        target_side_status = "QUALIFIED_LITERATURE_IPSILATERAL_CLASS_INFERENCE"
        confidence = "HIGH"
        confidence_scope = "MUSCLE_CLASS_AND_PATHWAY_LATERALITY"
        evidence_refs = ["king_wyman_1980", "augustin_2017"]
        side_basis = "EXPLICIT_TTMN_IPSILATERAL_PATHWAY_EVIDENCE"
        unresolved = ["exact_muscle_fiber", "exact_peripheral_endpoint"]
        unresolved_reasons = {
            "exact_muscle_fiber": (
                "The evidence maps to the TTM class, not a fiber-specific endpoint."
            ),
            "exact_peripheral_endpoint": (
                "The pinned MaleCNS motor query has no peripheral muscle "
                "endpoint for this body."
            ),
        }
        target_class = "TTM"
    elif neuron_type == "DLMn a, b":
        target_group = "a,b"
        target_granularity = "MUSCLE_GROUP"
        target_side = None
        target_side_status = "UNRESOLVED"
        confidence = "MODERATE"
        confidence_scope = "LITERATURE_GROUP_TO_MALECNS_ANNOTATION_CORRESPONDENCE"
        evidence_refs = ["coggshall_1978", "kuehn_duch_2013", "hurkey_2023"]
        side_basis = "UNRESOLVED_EXACT_BODY_TO_HISTORICAL_MN_LATERALITY"
        unresolved = [
            "muscle_target_side",
            "exact_muscle_fiber",
            "exact_peripheral_endpoint",
            "historical_mn5_to_malecns_body_identity",
        ]
        unresolved_reasons = {
            "muscle_target_side": (
                "The literature MN5 target is contralateral, but its identity "
                "is not resolved to this exact MaleCNS body."
            ),
            "exact_muscle_fiber": "The evidence supports the DLM a,b group only.",
            "exact_peripheral_endpoint": (
                "No MaleCNS peripheral endpoint is present in the pinned "
                "neural contract."
            ),
            "historical_mn5_to_malecns_body_identity": (
                "Class-level correspondence does not establish an exact body-ID match."
            ),
        }
        target_class = "DLM"
    elif neuron_type == "DLMn c-f":
        target_group = "c-f"
        target_granularity = "MUSCLE_GROUP"
        target_side = None
        target_side_status = "UNRESOLVED"
        confidence = "MODERATE"
        confidence_scope = "LITERATURE_GROUP_TO_MALECNS_ANNOTATION_CORRESPONDENCE"
        evidence_refs = ["coggshall_1978", "hurkey_2023"]
        side_basis = "NO_AUTOMATIC_NEURAL_TO_MUSCLE_SIDE_INFERENCE"
        unresolved = [
            "muscle_target_side",
            "exact_muscle_fiber",
            "exact_peripheral_endpoint",
            "individual_fiber_crosswalk",
        ]
        unresolved_reasons = {
            "muscle_target_side": (
                "The pinned neural side is not sufficient to establish the "
                "peripheral muscle side for this MaleCNS body."
            ),
            "exact_muscle_fiber": "The evidence supports the DLM c-f group only.",
            "exact_peripheral_endpoint": (
                "No MaleCNS peripheral endpoint is present in the pinned "
                "neural contract."
            ),
            "individual_fiber_crosswalk": (
                "No source maps this body to one individual c, d, e, or f fiber."
            ),
        }
        target_class = "DLM"
    else:
        raise MotorNeuronMuscleContractError(
            f"unsupported motor-neuron target class: {neuron_type!r}"
        )
    return {
        "motor_neuron_body_id": node["body_id"],
        "motor_neuron_type": neuron_type,
        "motor_neuron_instance": node["instance"],
        "neural_side": side,
        "neural_identity_evidence_class": "MALECNS_NEURAL_IDENTITY",
        "neural_identity_source": {
            "dataset": node["source_dataset"],
            "motor_neural_contract_id": motor_contract_id,
            "motor_neural_contract_sha256": motor_contract_sha256,
            "identity_source_sha256": node["identity_source_sha256"],
            "status": node["status"],
            "status_label": node["status_label"],
            "superclass": node["superclass"],
            "subclass": node["subclass"],
            "soma_neuromere": node["soma_neuromere"],
        },
        "association_relation": "LITERATURE_SUPPORTED_MUSCLE_TARGET_ASSOCIATION",
        "target_structure_kind": "SKELETAL_MUSCLE",
        "target_class": target_class,
        "target_group": target_group,
        "exact_target": None,
        "exact_muscle_fiber": None,
        "muscle_target_side": target_side,
        "muscle_target_side_status": target_side_status,
        "muscle_target_side_basis": side_basis,
        "target_granularity": target_granularity,
        "mapping_confidence": confidence,
        "mapping_confidence_scope": confidence_scope,
        "mapping_confidence_semantics": (
            "LITERATURE_TO_MALECNS_IDENTITY_CORRESPONDENCE_NOT_PROBABILITY_OR_EFFICACY"
        ),
        "evidence_classification": "PRIMARY_LITERATURE_TARGET_EVIDENCE",
        "evidence_refs": evidence_refs,
        "unresolved_fields": unresolved,
        "unresolved_reasons": unresolved_reasons,
        "malecns_peripheral_muscle_edge_present": False,
    }


def build_motor_neuron_muscle_target_contract(
    pinned_motor_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build the deterministic no-dynamics target contract from source IDs."""

    source = _source_contract(pinned_motor_contract)
    nodes = source.get("nodes")
    if not isinstance(nodes, list):
        raise MotorNeuronMuscleContractError("motor contract nodes are malformed")
    seen: set[int] = set()
    selected: list[dict[str, Any]] = []
    for node in nodes:
        if not isinstance(node, dict):
            raise MotorNeuronMuscleContractError("motor contract node is malformed")
        body_id = node.get("body_id")
        if not isinstance(body_id, int) or isinstance(body_id, bool):
            raise MotorNeuronMuscleContractError("motor contract body ID is invalid")
        if body_id in seen:
            raise MotorNeuronMuscleContractError("duplicate motor contract body ID")
        seen.add(body_id)
        if node.get("type") in {"TTMn", "DLMn a, b", "DLMn c-f"}:
            selected.append(node)
    type_counts = {
        neuron_type: sum(node.get("type") == neuron_type for node in selected)
        for neuron_type in ("TTMn", "DLMn a, b", "DLMn c-f")
    }
    if type_counts != {"TTMn": 2, "DLMn a, b": 2, "DLMn c-f": 8}:
        raise MotorNeuronMuscleContractError(
            f"unexpected motor-neuron population: {type_counts!r}"
        )
    motor_contract_sha256 = pinned_motor_contract["manifest"]["contract_sha256"]
    motor_contract_id = source["contract_id"]
    records = [
        _target_record(
            node,
            motor_contract_id=motor_contract_id,
            motor_contract_sha256=motor_contract_sha256,
        )
        for node in selected
    ]
    records.sort(key=lambda item: item["motor_neuron_body_id"])
    source_identity = {
        "dataset": source["dataset"],
        "motor_neural_contract_id": motor_contract_id,
        "motor_neural_contract_sha256": motor_contract_sha256,
        "query_response_sha256": source["source_provenance"]["query_response_sha256"],
        "annotation_source_sha256": source["source_provenance"][
            "annotation_source_sha256"
        ],
    }
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "contract_semantics": "NO_DYNAMICS_LITERATURE_SUPPORTED_TARGET_ASSOCIATIONS",
        "population_semantics": "MOTOR_NEURON_TARGET_ASSOCIATIONS_ONLY",
        "source_identity": source_identity,
        "source_identity_sha256": canonical_sha256(source_identity),
        "mapping_policy": {
            "policy_id": MAPPING_POLICY_ID,
            "confidence_vocabulary": ["HIGH", "MODERATE", "LOW", "UNRESOLVED"],
            "confidence_semantics": (
                "mapping confidence is literature-to-MaleCNS identity "
                "correspondence, not probability or efficacy"
            ),
            "neural_side_to_muscle_side_rule": (
                "only TTMn uses the explicit literature-supported ipsilateral "
                "class rule; DLM target side remains null unless exact-body "
                "evidence supports it"
            ),
            "male_cns_peripheral_edges_created": False,
            "dynamics": "NO_DYNAMICS",
            "evidence_sources": list(_EVIDENCE_SOURCES),
        },
        "node_counts": {
            "TTMn": type_counts["TTMn"],
            "DLMn_a_b": type_counts["DLMn a, b"],
            "DLMn_c_f": type_counts["DLMn c-f"],
            "total": len(records),
        },
        "target_associations": records,
    }
    contract_sha256 = canonical_sha256(payload)
    artifact_id = _artifact_id(contract_sha256)
    return {
        **payload,
        "contract_sha256": contract_sha256,
        "contract_id": artifact_id,
    }


def _validate_contract(
    contract: dict[str, Any], pinned_motor_contract: dict[str, Any]
) -> None:
    expected = build_motor_neuron_muscle_target_contract(pinned_motor_contract)
    if contract != expected:
        raise MotorNeuronMuscleContractError(
            "target contract differs from deterministic source replay"
        )
    if not all(
        ref in _EVIDENCE_BY_ID
        for row in contract["target_associations"]
        for ref in row["evidence_refs"]
    ):
        raise MotorNeuronMuscleContractError("target evidence reference is unknown")
    for row in contract["target_associations"]:
        if row["mapping_confidence"] not in {"HIGH", "MODERATE", "LOW", "UNRESOLVED"}:
            raise MotorNeuronMuscleContractError("mapping confidence is invalid")
        if row["muscle_target_side"] is None and row["neural_side"] is not None:
            if row["muscle_target_side_status"] != "UNRESOLVED":
                raise MotorNeuronMuscleContractError(
                    "unresolved muscle side is mislabeled"
                )
        if (
            row["target_granularity"] == "EXACT_FIBER"
            and row["exact_muscle_fiber"] is None
        ):
            raise MotorNeuronMuscleContractError(
                "exact fiber mapping lacks an identity"
            )


@dataclass(frozen=True, slots=True)
class LoadedMotorNeuronMuscleTargetArtifact:
    path: Path
    artifact_id: str
    contract: MappingProxyType
    manifest: MappingProxyType

    def summary(self) -> dict[str, Any]:
        contract = self.contract
        return {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": contract["schema_version"],
            "artifact_id": self.artifact_id,
            "contract_sha256": contract["contract_sha256"],
            "source_identity_sha256": contract["source_identity_sha256"],
            "motor_neural_contract_id": contract["source_identity"][
                "motor_neural_contract_id"
            ],
            "target_association_count": len(contract["target_associations"]),
            "node_counts": dict(contract["node_counts"]),
            "no_dynamics": contract["mapping_policy"]["dynamics"] == "NO_DYNAMICS",
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "path": str(self.path),
            "integrity_validation": "PASSED",
        }


def _read_artifact(
    artifact_path: str | Path,
    *,
    allow_staging: bool = False,
    expected_artifact_id: str | None = None,
) -> LoadedMotorNeuronMuscleTargetArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise MotorNeuronMuscleContractError("target contract artifact not found")
    try:
        if {item.name for item in path.iterdir()} != {
            CONTRACT_FILENAME,
            MANIFEST_FILENAME,
        }:
            raise MotorNeuronMuscleContractError("unexpected artifact file set")
        raw_contract = (path / CONTRACT_FILENAME).read_bytes()
        raw_manifest = (path / MANIFEST_FILENAME).read_bytes()
        contract = json.loads(raw_contract)
        manifest = json.loads(raw_manifest)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MotorNeuronMuscleContractError(
            "malformed target contract artifact"
        ) from exc
    if not isinstance(contract, dict) or not isinstance(manifest, dict):
        raise MotorNeuronMuscleContractError(
            "target contract artifact must contain JSON objects"
        )
    if (
        _json_bytes(contract, newline=True) != raw_contract
        or _json_bytes(manifest, newline=True) != raw_manifest
    ):
        raise MotorNeuronMuscleContractError("artifact JSON is not canonical")
    if (
        set(manifest)
        != {
            "artifact_schema_version",
            "artifact_id",
            "contract_sha256",
            "files",
        }
        or manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
    ):
        raise MotorNeuronMuscleContractError("artifact manifest schema mismatch")
    if not isinstance(manifest.get("files"), dict) or set(manifest["files"]) != {
        CONTRACT_FILENAME
    }:
        raise MotorNeuronMuscleContractError("artifact manifest file set mismatch")
    payload = {
        key: value
        for key, value in contract.items()
        if key not in {"contract_sha256", "contract_id"}
    }
    contract_sha256 = canonical_sha256(payload)
    artifact_id = _artifact_id(contract_sha256)
    file_record = manifest["files"].get(CONTRACT_FILENAME)
    if (
        not isinstance(file_record, dict)
        or set(file_record) != {"schema", "bytes", "sha256"}
        or file_record.get("schema") != CONTRACT_SCHEMA_VERSION
        or file_record.get("bytes") != len(raw_contract)
        or file_record.get("sha256") != _hash_bytes(raw_contract)
        or contract.get("contract_sha256") != contract_sha256
        or contract.get("contract_id") != artifact_id
        or manifest.get("contract_sha256") != contract_sha256
        or manifest.get("artifact_id") != artifact_id
        or (expected_artifact_id is not None and artifact_id != expected_artifact_id)
        or (path.name != artifact_id and not allow_staging)
    ):
        raise MotorNeuronMuscleContractError("target contract integrity mismatch")
    return LoadedMotorNeuronMuscleTargetArtifact(
        path=path,
        artifact_id=artifact_id,
        contract=MappingProxyType(contract),
        manifest=MappingProxyType(manifest),
    )


def load_motor_neuron_muscle_target_artifact(
    artifact_path: str | Path,
) -> LoadedMotorNeuronMuscleTargetArtifact:
    """Check canonical bytes and content-addressed artifact identity."""

    return _read_artifact(artifact_path)


def export_motor_neuron_muscle_target_artifact(
    contract: dict[str, Any],
    destination: str | Path,
    *,
    pinned_motor_contract: dict[str, Any],
) -> LoadedMotorNeuronMuscleTargetArtifact:
    """Validate and atomically persist a deterministic no-dynamics contract."""

    _validate_contract(contract, pinned_motor_contract)
    output = Path(destination)
    if output.exists():
        raise MotorNeuronMuscleContractError(f"destination already exists: {output}")
    contract_bytes = _json_bytes(contract, newline=True)
    contract_sha256 = contract["contract_sha256"]
    artifact_id = contract["contract_id"]
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "contract_sha256": contract_sha256,
        "files": {
            CONTRACT_FILENAME: {
                "schema": CONTRACT_SCHEMA_VERSION,
                "bytes": len(contract_bytes),
                "sha256": _hash_bytes(contract_bytes),
            }
        },
    }
    manifest_bytes = _json_bytes(manifest, newline=True)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=output.parent))
    except OSError as exc:
        raise MotorNeuronMuscleContractError(
            "could not create artifact staging directory"
        ) from exc
    try:
        for filename, payload in (
            (CONTRACT_FILENAME, contract_bytes),
            (MANIFEST_FILENAME, manifest_bytes),
        ):
            with (staging / filename).open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        _read_artifact(staging, allow_staging=True, expected_artifact_id=artifact_id)
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise MotorNeuronMuscleContractError("could not finalize artifact") from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return _read_artifact(output)


def replay_motor_neuron_muscle_target_artifact(
    artifact_path: str | Path,
    *,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
) -> LoadedMotorNeuronMuscleTargetArtifact:
    """Rebuild target records from the pinned motor contract and compare."""

    artifact = _read_artifact(artifact_path)
    try:
        pinned = load_pinned_motor_contract(motor_contract_path)
        _validate_contract(dict(artifact.contract), pinned)
    except (OSError, ValueError) as exc:
        raise MotorNeuronMuscleContractError("full offline replay failed") from exc
    return artifact


def generate_motor_neuron_muscle_target_artifact(
    *,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> LoadedMotorNeuronMuscleTargetArtifact:
    """Generate the source-derived contract, or replay the existing identity."""

    try:
        pinned = load_pinned_motor_contract(motor_contract_path)
        contract = build_motor_neuron_muscle_target_contract(pinned)
    except (OSError, ValueError) as exc:
        raise MotorNeuronMuscleContractError("could not build target contract") from exc
    destination = Path(output_root) / contract["contract_id"]
    if destination.exists():
        return replay_motor_neuron_muscle_target_artifact(
            destination, motor_contract_path=motor_contract_path
        )
    return export_motor_neuron_muscle_target_artifact(
        contract, destination, pinned_motor_contract=pinned
    )


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "CONTRACT_SCHEMA_VERSION",
    "DEFAULT_OUTPUT_ROOT",
    "MANIFEST_FILENAME",
    "MotorNeuronMuscleContractError",
    "build_motor_neuron_muscle_target_contract",
    "export_motor_neuron_muscle_target_artifact",
    "generate_motor_neuron_muscle_target_artifact",
    "load_motor_neuron_muscle_target_artifact",
    "replay_motor_neuron_muscle_target_artifact",
]
