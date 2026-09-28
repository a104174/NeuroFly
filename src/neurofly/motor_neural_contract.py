"""Pinned, no-dynamics MaleCNS motor pathway source contract.

This module records a bounded official MaleCNS v1.0 query. Chemical
connectivity counts are structural metadata only; this module provides no
motor dynamics or physiological parameter interface.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import platform
import tempfile
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from neurofly.malecns.errors import MaleCNSAccessError
from neurofly.malecns.models import MALECNS_DATASET, NEUPRINT_ENDPOINT

MOTOR_NEURAL_CONTRACT_SCHEMA = "motor_neural_pathway_contract_v1"
MOTOR_QUERY_RESPONSE_SCHEMA = "motor_neural_query_response_v1"
MOTOR_QUERY_MANIFEST_SCHEMA = "motor_neural_query_source_manifest_v1"
MOTOR_QUERY_ARTIFACT_MANIFEST_SCHEMA = "motor_neural_query_artifact_manifest_v1"
ANNOTATION_SOURCE_URL = (
    "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/"
    "flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather"
)
HISTORICAL_ANNOTATION_SHA256 = (
    "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2"
)
PINNED_NEUPRINT_PYTHON_VERSION = "0.6.3"
DEFAULT_ARTIFACT_ROOT = Path(
    "data/derived/malecns/looming_giant_fiber_v1/motor_neural_pathway_contract_v1"
)
DEFAULT_ANNOTATION_SOURCE_PATH = Path(
    "data/raw/malecns/body-annotations-male-cns-v1.0-minconf-0.5.feather"
)


class MotorNeuralContractError(ValueError):
    """Invalid source response, contract, or immutable artifact."""


class MotorSourceDriftError(MotorNeuralContractError):
    """The live official source differs from the recorded Phase 8D evidence."""


_IDENTITIES: tuple[dict[str, Any], ...] = (
    {
        "body_id": 10001,
        "type": "DNp01",
        "instance": "DNp01(GF)_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Roughly traced",
        "superclass": "descending_neuron",
        "subclass": "lt",
        "soma_neuromere": None,
    },
    {
        "body_id": 10010,
        "type": "DNp01",
        "instance": "DNp01(GF)_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Roughly traced",
        "superclass": "descending_neuron",
        "subclass": "lt",
        "soma_neuromere": None,
    },
    {
        "body_id": 800146,
        "type": "TTMn",
        "instance": "TTMn_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T2",
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
        "soma_neuromere": "T2",
    },
    {
        "body_id": 802401,
        "type": "PSI",
        "instance": "PSI_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_efferent",
        "subclass": None,
        "soma_neuromere": "T2",
    },
    {
        "body_id": 903327,
        "type": "PSI",
        "instance": "PSI_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_efferent",
        "subclass": None,
        "soma_neuromere": "T2",
    },
    {
        "body_id": 800718,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 800890,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 801295,
        "type": "DLMn a, b",
        "instance": "DLMn a, b_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T2",
    },
    {
        "body_id": 801895,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 801970,
        "type": "DLMn a, b",
        "instance": "DLMn a, b_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T2",
    },
    {
        "body_id": 801998,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 802544,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 803013,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 803048,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 1050014552,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
)
_IDENTITY_BY_ID = {row["body_id"]: row for row in _IDENTITIES}


def _query_group(
    query_id: str,
    source_ids: Sequence[int],
    target_ids: Sequence[int],
    scope: str = "HISTORICAL_PHASE_6B_BOUNDED_QUERY",
) -> dict[str, Any]:
    return {
        "query_id": query_id,
        "scope": scope,
        "source_body_ids": sorted(source_ids),
        "target_body_ids": sorted(target_ids),
        "direction": "source_body_id_to_target_body_id",
        "edge_relation": "ConnectsTo",
        "roi": "VNC",
        "min_roi_weight": 1,
        "min_total_weight": 1,
        "include_nonprimary": True,
    }


_DNPS = (10001, 10010)
_TTMNS = (800146, 804642)
_PSIS = (802401, 903327)
_DLMNS = (
    800718,
    800890,
    801295,
    801895,
    801970,
    801998,
    802544,
    803013,
    803048,
    1050014552,
)
QUERY_GROUPS: tuple[dict[str, Any], ...] = (
    _query_group("dnp01_to_ttmn", _DNPS, _TTMNS),
    _query_group("dnp01_to_psi", _DNPS, _PSIS),
    _query_group("psi_to_dlmn", _PSIS, _DLMNS),
    _query_group("dnp01_to_candidate_dlmn", _DNPS, _DLMNS),
    _query_group(
        "psi_to_psi_supplemental",
        _PSIS,
        _PSIS,
        "PHASE_8E_SUPPLEMENTAL_CANDIDATE_SUBGRAPH_AUDIT",
    ),
)
LIVE_API_PARAMETERS = {
    "rois": ["VNC"],
    "min_roi_weight": 1,
    "min_total_weight": 1,
    "include_nonprimary": True,
    "batch_size": 200,
    "weight_props": "all",
    "omit_rois": False,
    "threads": 4,
}
_EXPECTED_ROWS: dict[str, tuple[tuple[int, int, int], ...]] = {
    "dnp01_to_ttmn": ((10001, 800146, 70), (10010, 804642, 20)),
    "dnp01_to_psi": (
        (10001, 802401, 3),
        (10001, 903327, 2),
        (10010, 802401, 9),
        (10010, 903327, 2),
    ),
    "psi_to_dlmn": (
        (802401, 801970, 17),
        (802401, 801998, 40),
        (802401, 802544, 67),
        (802401, 803048, 35),
        (802401, 1050014552, 64),
        (903327, 800718, 68),
        (903327, 800890, 24),
        (903327, 801295, 26),
        (903327, 801895, 58),
        (903327, 803013, 50),
    ),
    "dnp01_to_candidate_dlmn": (),
    "psi_to_psi_supplemental": (
        (802401, 903327, 5),
        (903327, 802401, 17),
    ),
}


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a JSON-compatible value deterministically."""
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MotorNeuralContractError("value is not canonical JSON data") from exc


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _normalize_annotation_value(value: Any) -> str | None:
    import pandas as pd

    if value is None or pd.isna(value):
        return None
    return str(value)


def identities_from_annotation_bytes(payload: bytes) -> tuple[dict[str, Any], ...]:
    """Read the exact candidate identities from the official v1.0 Feather."""
    import pandas as pd

    try:
        table = pd.read_feather(io.BytesIO(payload))
    except Exception as exc:
        raise MotorNeuralContractError(
            "official MaleCNS annotation Feather could not be read"
        ) from exc
    body_ids = tuple(sorted(_IDENTITY_BY_ID))
    selected = table.loc[table["bodyId"].isin(body_ids)].copy()
    rows = []
    for raw in selected.to_dict("records"):
        body_id = int(raw["bodyId"])
        rows.append(
            {
                "body_id": body_id,
                "type": _normalize_annotation_value(raw.get("type")),
                "instance": _normalize_annotation_value(raw.get("instance")),
                "side": _normalize_annotation_value(raw.get("somaSide")),
                "status": _normalize_annotation_value(raw.get("status")),
                "status_label": _normalize_annotation_value(raw.get("statusLabel")),
                "superclass": _normalize_annotation_value(raw.get("superclass")),
                "subclass": _normalize_annotation_value(raw.get("subclass")),
                "soma_neuromere": _normalize_annotation_value(raw.get("somaNeuromere")),
            }
        )
    return tuple(sorted(rows, key=lambda row: row["body_id"]))


def _canonical_rows(
    raw_rows: Sequence[Mapping[str, Any]], query_id: str
) -> list[dict[str, Any]]:
    rows = []
    seen: set[tuple[int, int, str]] = set()
    for row in raw_rows:
        try:
            pre = row.get("source_body_id", row.get("bodyId_pre"))
            post = row.get("target_body_id", row.get("bodyId_post"))
            count = row.get("structural_count", row.get("weight"))
            roi = row.get("roi")
        except AttributeError:
            raise MotorNeuralContractError(
                f"malformed row in query {query_id!r}"
            ) from None
        if (
            not _is_int(pre)
            or not _is_int(post)
            or not _is_int(count)
            or count < 1
            or roi != "VNC"
        ):
            raise MotorNeuralContractError(
                f"malformed or out-of-ROI edge in query {query_id!r}"
            )
        identity = (pre, post, roi)
        if identity in seen:
            raise MotorNeuralContractError(
                f"duplicate edge in query {query_id!r}: {identity!r}"
            )
        seen.add(identity)
        rows.append(
            {
                "source_body_id": pre,
                "target_body_id": post,
                "roi": roi,
                "structural_count": count,
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            row["source_body_id"],
            row["target_body_id"],
            row["roi"],
        ),
    )


def build_source_response(
    identities: Sequence[Mapping[str, Any]],
    query_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    annotation_sha256: str,
) -> dict[str, Any]:
    """Canonicalize normalized annotation identities and directed query rows."""
    if not isinstance(annotation_sha256, str) or len(annotation_sha256) != 64:
        raise MotorNeuralContractError("annotation source SHA-256 is malformed")
    try:
        int(annotation_sha256, 16)
    except ValueError:
        raise MotorNeuralContractError(
            "annotation source SHA-256 is malformed"
        ) from None

    normalized_identities = [dict(row) for row in identities]
    ids = [row.get("body_id") for row in normalized_identities]
    if any(not _is_int(body_id) for body_id in ids) or len(ids) != len(set(ids)):
        raise MotorNeuralContractError("identity rows contain duplicate/invalid IDs")
    normalized_identities.sort(key=lambda row: row["body_id"])
    if set(ids) != set(_IDENTITY_BY_ID):
        raise MotorNeuralContractError(
            "source identity set differs from the bounded set"
        )

    if set(query_rows) != {group["query_id"] for group in QUERY_GROUPS}:
        raise MotorNeuralContractError("directed query group set is incomplete")
    queries = []
    for group in QUERY_GROUPS:
        query_id = group["query_id"]
        queries.append(
            {**group, "rows": _canonical_rows(query_rows[query_id], query_id)}
        )
    return {
        "schema_version": MOTOR_QUERY_RESPONSE_SCHEMA,
        "dataset": MALECNS_DATASET,
        "endpoint": NEUPRINT_ENDPOINT,
        "annotation_source_sha256": annotation_sha256,
        "nodes": normalized_identities,
        "identity_selection": {
            "source": "official MaleCNS v1.0 body-annotations table",
            "body_ids": sorted(ids),
            "annotation_status_filter": None,
            "connectivity_query_uses_exact_body_ids": True,
        },
        "query_groups": queries,
    }


def _rows_by_group(
    response: Mapping[str, Any],
) -> dict[str, tuple[tuple[int, int, int], ...]]:
    groups = response.get("query_groups")
    if not isinstance(groups, list):
        raise MotorNeuralContractError("query response has no query_groups list")
    result: dict[str, tuple[tuple[int, int, int], ...]] = {}
    for group in groups:
        if not isinstance(group, Mapping):
            raise MotorNeuralContractError("query group is malformed")
        query_id = group.get("query_id")
        rows = group.get("rows")
        if not isinstance(query_id, str) or not isinstance(rows, list):
            raise MotorNeuralContractError("query group identity/rows are malformed")
        if query_id in result:
            raise MotorNeuralContractError("duplicate query group identity")
        values = []
        for row in rows:
            if not isinstance(row, Mapping):
                raise MotorNeuralContractError("query edge row is malformed")
            pre = row.get("source_body_id")
            post = row.get("target_body_id")
            count = row.get("structural_count")
            if (
                not _is_int(pre)
                or not _is_int(post)
                or not _is_int(count)
                or row.get("roi") != "VNC"
            ):
                raise MotorNeuralContractError("query edge identity/count is invalid")
            values.append((pre, post, count))
        result[query_id] = tuple(sorted(values))
    if set(result) != {group["query_id"] for group in QUERY_GROUPS}:
        raise MotorNeuralContractError("query response scope has changed")
    return result


def historical_differences(response: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return explicit identity/query differences from the Phase 8D record."""
    differences: list[dict[str, Any]] = []
    if response.get("schema_version") != MOTOR_QUERY_RESPONSE_SCHEMA:
        differences.append(
            {
                "kind": "schema",
                "expected": MOTOR_QUERY_RESPONSE_SCHEMA,
                "actual": response.get("schema_version"),
            }
        )
    if response.get("dataset") != MALECNS_DATASET:
        differences.append(
            {
                "kind": "dataset",
                "expected": MALECNS_DATASET,
                "actual": response.get("dataset"),
            }
        )
    if response.get("endpoint") != NEUPRINT_ENDPOINT:
        differences.append(
            {
                "kind": "endpoint",
                "expected": NEUPRINT_ENDPOINT,
                "actual": response.get("endpoint"),
            }
        )
    if response.get("annotation_source_sha256") != HISTORICAL_ANNOTATION_SHA256:
        differences.append(
            {
                "kind": "annotation_source_sha256",
                "expected": HISTORICAL_ANNOTATION_SHA256,
                "actual": response.get("annotation_source_sha256"),
            }
        )
    selection = response.get("identity_selection")
    expected_selection = {
        "source": "official MaleCNS v1.0 body-annotations table",
        "body_ids": sorted(_IDENTITY_BY_ID),
        "annotation_status_filter": None,
        "connectivity_query_uses_exact_body_ids": True,
    }
    if selection != expected_selection:
        differences.append(
            {
                "kind": "identity_selection",
                "expected": expected_selection,
                "actual": selection,
            }
        )

    # Identity rows are represented by the annotation source in the response's
    # explicit node field (kept separate from edge query results).
    nodes = response.get("nodes")
    if not isinstance(nodes, list):
        differences.append({"kind": "nodes_missing"})
    else:
        expected = list(_IDENTITIES)
        actual = sorted(nodes, key=lambda row: row.get("body_id", -1))
        if actual != expected:
            exp_by = {row["body_id"]: row for row in expected}
            act_by = {
                row.get("body_id"): row for row in actual if isinstance(row, Mapping)
            }
            for body_id in sorted(set(exp_by) | set(act_by), key=str):
                if exp_by.get(body_id) != act_by.get(body_id):
                    differences.append(
                        {
                            "kind": "node",
                            "body_id": body_id,
                            "expected": exp_by.get(body_id),
                            "actual": act_by.get(body_id),
                        }
                    )
    try:
        actual_rows = _rows_by_group(response)
    except MotorNeuralContractError as exc:
        differences.append({"kind": "query_shape", "detail": str(exc)})
    else:
        actual_groups = {
            group.get("query_id"): group
            for group in response.get("query_groups", [])
            if isinstance(group, Mapping)
        }
        expected_group_ids = {group["query_id"] for group in QUERY_GROUPS}
        if set(actual_groups) != expected_group_ids:
            differences.append(
                {
                    "kind": "query_group_ids",
                    "expected": sorted(expected_group_ids),
                    "actual": sorted(str(key) for key in actual_groups),
                }
            )
        for expected_group in QUERY_GROUPS:
            query_id = expected_group["query_id"]
            current_group = actual_groups.get(query_id)
            if current_group is not None:
                metadata = {
                    key: value for key, value in current_group.items() if key != "rows"
                }
                if metadata != expected_group:
                    differences.append(
                        {
                            "kind": "query_parameters",
                            "query_id": query_id,
                            "expected": expected_group,
                            "actual": metadata,
                        }
                    )
        for query_id, expected_rows in _EXPECTED_ROWS.items():
            actual_for_group = actual_rows.get(query_id)
            if actual_for_group != expected_rows:
                differences.append(
                    {
                        "kind": "edges",
                        "query_id": query_id,
                        "expected": expected_rows,
                        "actual": actual_for_group,
                    }
                )
    return differences


def validate_historical_source_response(response: Mapping[str, Any]) -> None:
    differences = historical_differences(response)
    if differences:
        raise MotorSourceDriftError(
            json.dumps(differences, sort_keys=True, separators=(",", ":"))
        )


def _query_definition() -> dict[str, Any]:
    return {
        "endpoint": NEUPRINT_ENDPOINT,
        "dataset": MALECNS_DATASET,
        "method": "neuprint.fetch_adjacencies",
        "relation": "chemical ConnectsTo",
        "api_parameters": LIVE_API_PARAMETERS,
        "historical_explicit_parameters": {
            "rois": ["VNC"],
            "min_total_weight": 1,
            "include_nonprimary": True,
        },
        "identity_source": {
            "url": ANNOTATION_SOURCE_URL,
            "sha256": HISTORICAL_ANNOTATION_SHA256,
            "selection": "exact candidate body IDs in the official annotation snapshot",
            "status_filter": None,
        },
        "groups": list(QUERY_GROUPS),
        "ordering": (
            "source_body_id,target_body_id,roi ascending; row order canonicalized"
        ),
    }


def build_motor_neural_contract(response: Mapping[str, Any]) -> dict[str, Any]:
    """Build the immutable structural contract from an audited source snapshot."""
    validate_historical_source_response(response)
    nodes = [dict(row) for row in response["nodes"]]
    by_id = {row["body_id"]: row for row in nodes}
    source_response_sha256 = canonical_sha256(response)
    edges = []
    for group in response["query_groups"]:
        for row in group["rows"]:
            pre = row["source_body_id"]
            post = row["target_body_id"]
            edges.append(
                {
                    "edge_id": f"malecns_v1_{pre}_{post}_chemical",
                    "source_body_id": pre,
                    "target_body_id": post,
                    "source_type": by_id[pre]["type"],
                    "target_type": by_id[post]["type"],
                    "structural_count": row["structural_count"],
                    "modality": "MALECNS_CHEMICAL_CONNECTIVITY",
                    "roi": row["roi"],
                    "source_query_id": group["query_id"],
                    "source_query_response_sha256": source_response_sha256,
                }
            )
    edges.sort(key=lambda row: (row["source_body_id"], row["target_body_id"]))
    payload: dict[str, Any] = {
        "schema_version": MOTOR_NEURAL_CONTRACT_SCHEMA,
        "dataset": MALECNS_DATASET,
        "source_provenance": {
            "endpoint": NEUPRINT_ENDPOINT,
            "annotation_source_url": ANNOTATION_SOURCE_URL,
            "annotation_source_sha256": response["annotation_source_sha256"],
            "query_definition_sha256": canonical_sha256(_query_definition()),
            "query_response_sha256": source_response_sha256,
            "source_response_schema": MOTOR_QUERY_RESPONSE_SCHEMA,
        },
        "scope": {
            "population": "bounded DNp01/TTMn/PSI/DLMn motor candidates",
            "chemical_pathway_edges": 16,
            "supplementary_psi_to_psi_edges": 2,
            "direct_dnp01_to_candidate_dlmn_edge_count": 0,
            "no_dynamics": True,
        },
        "nodes": [
            {
                **row,
                "source_dataset": MALECNS_DATASET,
                "identity_source_sha256": response["annotation_source_sha256"],
            }
            for row in nodes
        ],
        "chemical_edges": edges,
        "direct_dnp01_to_candidate_dlmn_audit": {
            "query_id": "dnp01_to_candidate_dlmn",
            "source_body_ids": list(_DNPS),
            "target_body_ids": list(_DLMNS),
            "returned_edge_count": 0,
            "scope_limit": "bounded candidate DLMn body set only",
        },
        "literature_pathway_evidence": [
            {
                "pathway": "Giant Fiber / DNp01 identity",
                "evidence_class": "LITERATURE_EVIDENCE",
                "mapping_confidence": "HIGH",
                "basis": (
                    "MaleCNS DNp01 instance names explicitly include GF; "
                    "class/pathway correspondence, not a physiological edge "
                    "calibration."
                ),
            },
            {
                "pathway": "GF to TTMn",
                "evidence_class": "LITERATURE_EVIDENCE",
                "transmission": "MIXED_ELECTRICAL_CHEMICAL",
                "mapping_confidence": "HIGH",
                "basis": (
                    "Established GF/TTMn pathway class; exact MaleCNS chemical "
                    "count is not the electrical component."
                ),
            },
            {
                "pathway": "GF to PSI",
                "evidence_class": "LITERATURE_EVIDENCE",
                "transmission": "ELECTRICAL_AND_MIXED_PATHWAY_EVIDENCE",
                "mapping_confidence": "MODERATE",
                "basis": (
                    "PSI class correspondence is plausible; historic recordings "
                    "are not mapped to these exact MaleCNS body pairs."
                ),
            },
            {
                "pathway": "PSI to DLM motor-neuron class",
                "evidence_class": "LITERATURE_EVIDENCE",
                "transmission": "CHEMICAL_CHOLINERGIC_EXCITATORY_PATHWAY",
                "mapping_confidence": "MODERATE",
                "basis": (
                    "Pathway/cell-class physiology; no exact historical-recording-"
                    "to-MaleCNS-body mapping."
                ),
            },
            {
                "pathway": "MN5 recording to a specific MaleCNS DLMn body",
                "evidence_class": "UNRESOLVED",
                "mapping_confidence": "UNRESOLVED",
                "basis": (
                    "MN5 supplies DLM a,b, but the historical neuron is not "
                    "uniquely matched to a MaleCNS body ID."
                ),
            },
        ],
        "structural_count_boundary": (
            "ConnectsTo structural count is source connectivity metadata only; "
            "not gain, conductance, efficacy, probability, delay, or event amplitude."
        ),
    }
    contract_id = canonical_sha256(payload)
    return {"contract_id": contract_id, **payload}


def _require_canonical_file(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise MotorNeuralContractError(f"could not load {path}") from exc
    if not isinstance(data, dict) or canonical_json_bytes(data) != raw:
        raise MotorNeuralContractError(f"noncanonical or malformed JSON: {path}")
    return data, raw


def source_manifest(
    response: Mapping[str, Any],
    *,
    retrieved_at_utc: str,
    neuprint_python_version: str,
    python_version: str | None = None,
) -> dict[str, Any]:
    if response.get("schema_version") != MOTOR_QUERY_RESPONSE_SCHEMA:
        raise MotorNeuralContractError("unsupported canonical query response")
    return {
        "schema_version": MOTOR_QUERY_MANIFEST_SCHEMA,
        "source": "official neuPrint / MaleCNS",
        "endpoint": NEUPRINT_ENDPOINT,
        "dataset": MALECNS_DATASET,
        "retrieved_at_utc": retrieved_at_utc,
        "python_version": python_version or platform.python_version(),
        "neuprint_python_version": neuprint_python_version,
        "annotation_source": {
            "url": ANNOTATION_SOURCE_URL,
            "sha256": response["annotation_source_sha256"],
            "bytes": 14483314,
            "stored_raw": False,
            "selection_source": "canonical node rows persisted in query_response.json",
        },
        "query_definition": _query_definition(),
        "query_definition_sha256": canonical_sha256(_query_definition()),
        "query_response_sha256": canonical_sha256(response),
        "query_response_serialization": (
            "UTF-8 canonical JSON, sorted keys, compact separators, no trailing newline"
        ),
        "creation_metadata_not_part_of_contract_identity": True,
    }


def _artifact_manifest(
    artifact_id: str,
    source_response: bytes,
    source_manifest_bytes: bytes,
    contract_bytes: bytes,
) -> dict[str, Any]:
    return {
        "schema_version": MOTOR_QUERY_ARTIFACT_MANIFEST_SCHEMA,
        "artifact_id": artifact_id,
        "contract_sha256": sha256_bytes(contract_bytes),
        "source_response_sha256": sha256_bytes(source_response),
        "source_manifest_sha256": sha256_bytes(source_manifest_bytes),
        "files": {
            "query_response.json": sha256_bytes(source_response),
            "source_manifest.json": sha256_bytes(source_manifest_bytes),
            "contract.json": sha256_bytes(contract_bytes),
        },
    }


def write_pinned_artifact(
    output_root: Path,
    response: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> Path:
    """Persist an immutable generated query snapshot and structural contract."""
    validate_historical_source_response(response)
    contract = build_motor_neural_contract(response)
    if (
        manifest.get("schema_version") != MOTOR_QUERY_MANIFEST_SCHEMA
        or manifest.get("dataset") != MALECNS_DATASET
        or manifest.get("endpoint") != NEUPRINT_ENDPOINT
        or manifest.get("neuprint_python_version") != PINNED_NEUPRINT_PYTHON_VERSION
        or manifest.get("annotation_source", {}).get("sha256")
        != response.get("annotation_source_sha256")
        or manifest.get("query_response_sha256") != canonical_sha256(response)
        or manifest.get("query_definition_sha256")
        != canonical_sha256(_query_definition())
    ):
        raise MotorNeuralContractError("source manifest does not match response")

    response_bytes = canonical_json_bytes(response)
    source_manifest_bytes = canonical_json_bytes(dict(manifest))
    contract_bytes = canonical_json_bytes(contract)
    artifact_manifest = _artifact_manifest(
        contract["contract_id"], response_bytes, source_manifest_bytes, contract_bytes
    )
    artifact_manifest_bytes = canonical_json_bytes(artifact_manifest)
    destination = output_root / contract["contract_id"]
    if destination.exists():
        loaded = load_pinned_artifact(destination)
        if loaded["contract"]["contract_id"] != contract["contract_id"] or loaded[
            "response"
        ] != dict(response):
            raise MotorNeuralContractError(
                "content-addressed destination exists with different content"
            )
        return destination

    output_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="motor-neural-contract-", dir=output_root
    ) as temp:
        staging = Path(temp) / "artifact"
        staging.mkdir()
        for name, payload in (
            ("query_response.json", response_bytes),
            ("source_manifest.json", source_manifest_bytes),
            ("contract.json", contract_bytes),
            ("manifest.json", artifact_manifest_bytes),
        ):
            (staging / name).write_bytes(payload)
        os.replace(staging, destination)
    return destination


def load_pinned_artifact(path: Path) -> dict[str, Any]:
    """Offline replay: validate canonical source snapshot, manifest and contract."""
    response, response_bytes = _require_canonical_file(path / "query_response.json")
    source, source_bytes = _require_canonical_file(path / "source_manifest.json")
    contract, contract_bytes = _require_canonical_file(path / "contract.json")
    artifact_manifest, artifact_manifest_bytes = _require_canonical_file(
        path / "manifest.json"
    )
    validate_historical_source_response(response)
    expected_contract = build_motor_neural_contract(response)
    expected_manifest = _artifact_manifest(
        expected_contract["contract_id"], response_bytes, source_bytes, contract_bytes
    )
    if source.get("schema_version") != MOTOR_QUERY_MANIFEST_SCHEMA:
        raise MotorNeuralContractError("source manifest schema mismatch")
    if (
        source.get("dataset") != MALECNS_DATASET
        or source.get("endpoint") != NEUPRINT_ENDPOINT
        or source.get("neuprint_python_version") != PINNED_NEUPRINT_PYTHON_VERSION
        or source.get("annotation_source", {}).get("sha256")
        != response.get("annotation_source_sha256")
        or source.get("query_response_sha256") != canonical_sha256(response)
        or source.get("query_definition") != _query_definition()
        or source.get("query_definition_sha256")
        != canonical_sha256(_query_definition())
    ):
        raise MotorNeuralContractError("source manifest provenance mismatch")
    if contract != expected_contract:
        raise MotorNeuralContractError("contract content differs from source replay")
    if (
        artifact_manifest != expected_manifest
        or path.name != expected_contract["contract_id"]
        or artifact_manifest.get("artifact_id") != expected_contract["contract_id"]
        or sha256_bytes(artifact_manifest_bytes) != canonical_sha256(artifact_manifest)
    ):
        raise MotorNeuralContractError("artifact manifest/identity validation failed")
    return {
        "path": path,
        "response": response,
        "source_manifest": source,
        "contract": contract,
        "manifest": artifact_manifest,
    }


def _download_annotation() -> bytes:
    try:
        with urlopen(ANNOTATION_SOURCE_URL, timeout=60) as response:
            payload = response.read()
    except Exception:
        raise MaleCNSAccessError(
            "Could not download the official MaleCNS v1.0 annotation snapshot."
        ) from None
    return payload


def _live_query_rows(client: Any) -> dict[str, list[dict[str, Any]]]:
    if getattr(client, "dataset", None) != MALECNS_DATASET:
        raise MaleCNSAccessError("neuPrint client is not pinned to male-cns:v1.0")
    try:
        from neuprint import NeuronCriteria, fetch_adjacencies
    except ImportError:
        raise MaleCNSAccessError("neuprint-python is unavailable") from None

    rows_by_group: dict[str, list[dict[str, Any]]] = {}
    for group in QUERY_GROUPS:
        _, edges = fetch_adjacencies(
            NeuronCriteria(bodyId=group["source_body_ids"]),
            NeuronCriteria(bodyId=group["target_body_ids"]),
            client=client,
            **LIVE_API_PARAMETERS,
        )
        rows_by_group[group["query_id"]] = edges.to_dict("records")
    return rows_by_group


def acquire_official_source() -> tuple[dict[str, Any], dict[str, Any]]:
    """Fetch the official annotation file and directed connectivity queries."""
    from importlib.metadata import version

    from neurofly.malecns.client import create_client

    annotation_bytes = _download_annotation()
    annotation_hash = sha256_bytes(annotation_bytes)
    identities = identities_from_annotation_bytes(annotation_bytes)
    client = create_client()
    rows = _live_query_rows(client)
    response = build_source_response(identities, rows, annotation_hash)
    neuprint_version = version("neuprint-python")
    if neuprint_version != PINNED_NEUPRINT_PYTHON_VERSION:
        raise MotorNeuralContractError(
            f"neuprint-python {neuprint_version} differs from pinned "
            f"{PINNED_NEUPRINT_PYTHON_VERSION}"
        )
    metadata = {
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "neuprint_python_version": neuprint_version,
        "python_version": platform.python_version(),
        "endpoint": NEUPRINT_ENDPOINT,
        "dataset": getattr(client, "dataset", None),
    }
    return response, metadata


def source_differences(
    pinned: Mapping[str, Any], current: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Compare canonical query results and return exact changed node/edge rows."""
    differences: list[dict[str, Any]] = []
    if pinned.get("annotation_source_sha256") != current.get(
        "annotation_source_sha256"
    ):
        differences.append(
            {
                "kind": "annotation_source_sha256",
                "pinned": pinned.get("annotation_source_sha256"),
                "current": current.get("annotation_source_sha256"),
            }
        )
    old_nodes = {row["body_id"]: row for row in pinned.get("nodes", [])}
    new_nodes = {row["body_id"]: row for row in current.get("nodes", [])}
    for body_id in sorted(set(old_nodes) | set(new_nodes)):
        if old_nodes.get(body_id) != new_nodes.get(body_id):
            differences.append(
                {
                    "kind": "node",
                    "body_id": body_id,
                    "pinned": old_nodes.get(body_id),
                    "current": new_nodes.get(body_id),
                }
            )
    try:
        old_edges = _rows_by_group(pinned)
        new_edges = _rows_by_group(current)
    except MotorNeuralContractError as exc:
        return [*differences, {"kind": "query_shape", "detail": str(exc)}]
    for query_id in sorted(set(old_edges) | set(new_edges)):
        if old_edges.get(query_id) != new_edges.get(query_id):
            differences.append(
                {
                    "kind": "edges",
                    "query_id": query_id,
                    "pinned": old_edges.get(query_id),
                    "current": new_edges.get(query_id),
                }
            )
    return differences


def refresh_source(path: Path) -> dict[str, Any]:
    """Explicit live check; reports MATCH/DRIFT and never overwrites a pin."""
    pinned = load_pinned_artifact(path)
    current, metadata = acquire_official_source()
    differences = source_differences(pinned["response"], current)
    if current.get("dataset") != MALECNS_DATASET:
        differences.append(
            {
                "kind": "dataset",
                "pinned": MALECNS_DATASET,
                "current": current.get("dataset"),
            }
        )
    return {
        "status": "MATCH" if not differences else "DRIFT",
        "artifact_id": pinned["contract"]["contract_id"],
        "pinned_response_sha256": canonical_sha256(pinned["response"]),
        "current_response_sha256": canonical_sha256(current),
        "current_metadata": metadata,
        "differences": differences,
    }


def pin_official_source(output_root: Path = DEFAULT_ARTIFACT_ROOT) -> Path:
    """Perform the explicit official query and immutably pin an exact match."""
    response, metadata = acquire_official_source()
    validate_historical_source_response(response)
    manifest = source_manifest(
        response,
        retrieved_at_utc=metadata["retrieved_at_utc"],
        neuprint_python_version=metadata["neuprint_python_version"],
        python_version=metadata["python_version"],
    )
    return write_pinned_artifact(output_root, response, manifest)
