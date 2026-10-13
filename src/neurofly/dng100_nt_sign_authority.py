"""Bounded MaleCNS transmitter evidence; no physiological sign or dynamics inferred."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import shutil
import struct
import tempfile
from pathlib import Path
from typing import Literal, TypedDict

from neurofly import dng100_recurrent_motif_authority as motif
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

SCHEMA = "dng100_nt_sign_authority_artifact_v1"
POLICY_PATH = motif.base.REPO / "docs/science/dng100_nt_sign_policy.json"
REFERENCE_PATH = motif.base.REPO / "docs/science/dng100_nt_sign_reference.json"
POLICY_ID = "80a851c9ddd55aa32ccbc75016ca289be723a38e16d447db7b9380841db8a78b"
DEFAULT_ROOT = motif.base.REPO.parent / "neurofly-science/work/dng100-nt-sign-v1"
NT_SOURCE = DEFAULT_ROOT / "source/body-neurotransmitters-male-cns-v1.0.feather"
SDK_SOURCE = DEFAULT_ROOT / "source/sdk-source.json"
MOTIF_SOURCE = (
    motif.DEFAULT_ROOT
    / "baae20599455c2a7acb3271e6eeb6b73326d17185b6e705022b74818ff0f8934"
)


class RawNeuronPrediction(TypedDict):
    body: int
    cell_type: str
    total_nt_predictions: int
    predicted_nt_confidence: float | None
    predicted_nt: str | None
    ground_truth: str | None
    celltype_total_nt_predictions: int
    celltype_predicted_nt: str | None
    celltype_predicted_nt_confidence: float | None
    consensus_nt: str | None


class SignAssessment(TypedDict):
    functional_sign: Literal["UNKNOWN"]
    receptor_status: Literal["POSTSYNAPTIC_RECEPTOR_UNRESOLVED"]
    receptor_evidence_references: list
    reason: str


def policy():
    p = json.loads(POLICY_PATH.read_bytes())
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unrecognized evidence policy; a new version is required")
    return p


def validate_raw(row: RawNeuronPrediction):
    """Isolated parser boundary; production additionally pins the complete source."""
    p = policy()
    if set(row) != set(p["columns"]) or type(row["body"]) is not int:
        raise ValueError("malformed neuron prediction row")
    target = {n["body_id"]: n for n in p["targets"]}.get(row["body"])
    if target is None or row["cell_type"] != target["type"]:
        raise ValueError("unexpected body/type, fragment, or segment substitution")
    for key in ("total_nt_predictions", "celltype_total_nt_predictions"):
        if type(row[key]) is not int or row[key] < 0:
            raise ValueError("invalid prediction count")
    for key in ("predicted_nt_confidence", "celltype_predicted_nt_confidence"):
        x = row[key]
        if x is not None and (
            type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= 1
        ):
            raise ValueError("invalid confidence")
    for key in (
        "predicted_nt",
        "celltype_predicted_nt",
        "consensus_nt",
        "ground_truth",
    ):
        if row[key] is not None and (
            not isinstance(row[key], str) or not row[key].strip()
        ):
            raise ValueError("invalid categorical prediction")
    return row


def classify(row: RawNeuronPrediction):
    validate_raw(row)
    p = policy()
    known = set(p["known_labels"])
    categories = {
        "ground_truth": "EXPERIMENTAL_GROUND_TRUTH",
        "consensus_nt": "MALECNS_CONSENSUS",
        "predicted_nt": "MALECNS_NEURON_PREDICTION",
        "celltype_predicted_nt": "MALECNS_CELLTYPE_PREDICTION",
    }
    confidence = {
        "predicted_nt": "predicted_nt_confidence",
        "celltype_predicted_nt": "celltype_predicted_nt_confidence",
    }
    evidence, reasons, resolved = [], [], []
    for key in p["precedence"]:
        value = row[key]
        usable = value in known
        evidence.append(
            {
                "field": key,
                "value": value,
                "category": categories[key] if usable else "UNKNOWN",
                "confidence": row[confidence[key]] if key in confidence else None,
                "resolution": (
                    p["ground_truth_resolution"]
                    if key == "ground_truth"
                    else "BODY_AGGREGATE_PREDICTION"
                    if key == "predicted_nt"
                    else "CELLTYPE_AGGREGATE_OR_CURATED_CONSENSUS"
                ),
                "direct_experiment_on_selected_body": False,
            }
        )
        if usable:
            resolved.append(key)
        else:
            reasons.append(f"{key}:MISSING_UNCLEAR_OR_UNRECOGNIZED")
        if key in confidence and row[confidence[key]] is None:
            reasons.append(f"{key}:CONFIDENCE_UNAVAILABLE")
    conflict = len({row[k] for k in resolved}) > 1
    if conflict:
        reasons.append("TRANSMITTER_EVIDENCE_CONFLICT_NO_AUTOMATIC_REPAIR")
    primary = resolved[0] if resolved and not conflict else None
    return {
        "evidence": evidence,
        "primary_evidence": categories[primary] if primary else "UNKNOWN",
        "primary_field": primary,
        "conflict": conflict,
        "unresolved_reasons": reasons,
    }


def assess_sign(*, receptor_claims=()) -> SignAssessment:
    # No accepted target-specific claims in V1. NT is deliberately not an input.
    # Adding even plausible type-level claims requires a separately reviewed version.
    if receptor_claims:
        raise ValueError("unsupported receptor claim in pinned V1 evidence audit")
    return {
        "functional_sign": "UNKNOWN",
        "receptor_status": "POSTSYNAPTIC_RECEPTOR_UNRESOLVED",
        "receptor_evidence_references": [],
        "reason": "NO_VERIFIED_TARGET_SPECIFIC_RECEPTOR_LOCALIZATION_OR_PHYSIOLOGY",
    }


def select_records(records):
    """Duplicate rows fail; no first-row selection or categorical averaging."""
    ids = {n["body_id"] for n in policy()["targets"]}
    found = {}
    for index, row in records:
        if row.get("body") not in ids:
            continue
        validate_raw(row)
        if row["body"] in found:
            raise ValueError("multiple rows for target body; aggregation undefined")
        if type(index) is not int or index < 0:
            raise ValueError("invalid recoverable source row")
        found[row["body"]] = {"source_row": index, "raw": row}
    if set(found) != ids:
        raise ValueError("missing primary body prediction record")
    return [found[i] for i in sorted(ids)]


def read_predictions(raw):
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.feather as feather

    p = policy()
    if (
        hashlib.sha256(raw).hexdigest() != p["nt_source_sha256"]
        or len(raw) != p["nt_source_bytes"]
    ):
        raise ValueError("official neurotransmitter source pin mismatch")
    table = feather.read_table(io.BytesIO(raw))
    if table.column_names != p["columns"]:
        raise ValueError("unrecognized official Feather schema")
    mask = pc.is_in(
        table["body"],
        value_set=pa.array([n["body_id"] for n in p["targets"]]),
    )
    indices = pc.indices_nonzero(mask)
    return select_records(zip(indices.to_pylist(), table.take(indices).to_pylist()))


def validate_anatomy(annotations):
    by_id = motif.base.validate_nodes(annotations)
    for n in policy()["targets"]:
        a = by_id.get(n["body_id"])
        if a is None or any(
            a[k] != v
            for k, v in {
                "type": n["type"],
                "somaSide": n["side"],
                "somaNeuromere": n["segment"],
                "instance": f"{n['type']}_{n['side']}",
                "superclass": "descending_neuron"
                if n["segment"] is None
                else "vnc_intrinsic",
                "status": "Traced",
                "statusLabel": "Prelim Roughly traced"
                if n["segment"] is None
                else "Reviewed",
            }.items()
        ):
            raise ValueError("body type/laterality/segment/tracing authority conflict")
    return by_id


def validate_sdk(sdk, rows, annotations):
    p = policy()
    if canonical_sha256(sdk) != p["sdk_source_sha256"] or (
        sdk["dataset"] != p["dataset"]
        or sdk["metadata"]["uuid"] != p["dataset_uuid"]
        or sdk["metadata"]["tag"] != "v1.0"
        or sdk["endpoint"] != motif.base.NEUPRINT_ENDPOINT
        or sdk["sdk_version"] != motif.base.PINNED_NEUPRINT_PYTHON_VERSION
    ):
        raise ValueError("official SDK source identity mismatch")
    api = {
        r[0]: dict(zip(sdk["response"]["columns"], r, strict=True))
        for r in sdk["response"]["data"]
    }
    if set(api) != {r["raw"]["body"] for r in rows}:
        raise ValueError("missing or unexpected SDK bodies")
    for record in rows:
        raw = record["raw"]
        body = raw["body"]
        other = api[body]
        for field in ("type", "somaSide", "somaNeuromere"):
            if other[field] != annotations[body][field]:
                raise ValueError("SDK anatomy disagreement")
        for k, alias in {
            "predicted_nt": "predictedNt",
            "consensus_nt": "consensusNt",
            "celltype_predicted_nt": "celltypePredictedNt",
            "predicted_nt_confidence": "predictedNtConfidence",
            "celltype_predicted_nt_confidence": "celltypePredictedNtConfidence",
        }.items():
            expected = raw[k]
            if expected is not None and k.endswith("confidence"):
                expected = struct.unpack("f", struct.pack("f", expected))[0]
            if expected != other[alias]:
                raise ValueError("Feather/SDK evidence disagreement")
    return api


def select_edges(graph):
    requested = {tuple(e) for e in policy()["edges"]}
    selected = [e for e in graph if (e["pre"], e["post"]) in requested]
    keys = [(e["pre"], e["post"]) for e in selected]
    if len(keys) != 15 or set(keys) != requested:
        raise ValueError("missing, duplicate, reversed or invented structural edge")
    for edge in selected:
        if type(edge["synapse_count"]) is not int or edge["synapse_count"] <= 0:
            raise ValueError("invalid structural count")
        if not edge["source_references"] or (
            edge["dataset"] != policy()["dataset"]
            or edge["annotation_sha256"] != policy()["annotation_sha256"]
        ):
            raise ValueError("missing structural provenance")
    return sorted(selected, key=lambda e: (e["pre"], e["post"]))


def build_artifact(nt_raw, annotation_raw, structural, sdk):
    p = policy()
    # Recomputed hashes cannot authorize a changed graph: the published logical pin
    # authenticates its complete config/result, and load_inputs also replays its source.
    ch = canonical_sha256(structural["config"])
    rh = canonical_sha256(structural["result"])
    if structural["artifact_id"] != p["motif_artifact_id"] or (
        canonical_sha256([motif.SCHEMA, ch, rh]) != p["motif_artifact_id"]
        or structural["config"]["source_sha256"] != p["motif_source_sha256"]
    ):
        raise ValueError("published recurrent structural authority mismatch")
    nodes = validate_anatomy(motif.base.annotation_nodes(annotation_raw))
    records = read_predictions(nt_raw)
    api = validate_sdk(sdk, records, nodes)
    import pyarrow.feather as feather

    table = feather.read_table(
        io.BytesIO(annotation_raw), columns=["bodyId", "receptorType"]
    )
    receptors = {
        r["bodyId"]: r["receptorType"] for r in table.to_pylist() if r["bodyId"] in api
    }
    neurons = [
        {
            "body_id": r["raw"]["body"],
            "annotation": nodes[r["raw"]["body"]],
            "annotation_source_sha256": p["annotation_sha256"],
            "source_row": r["source_row"],
            "raw": r["raw"],
            "raw_row_sha256": canonical_sha256(r["raw"]),
            "nt_source_sha256": p["nt_source_sha256"],
            "sdk_raw": api[r["raw"]["body"]],
            "raw_annotation_receptorType": receptors[r["raw"]["body"]],
            **classify(r["raw"]),
        }
        for r in records
    ]
    edges = [
        {
            "structural": e,
            "presynaptic_transmitter_body_id": e["pre"],
            "postsynaptic_body_id": e["post"],
            **assess_sign(),
            "anatomy_prediction_and_function_are_distinct": True,
        }
        for e in select_edges(structural["result"]["edges"])
    ]
    partial = any(n["conflict"] or n["primary_evidence"] == "UNKNOWN" for n in neurons)
    result = {
        "experiment_id": p["experiment_id"],
        "classification": "TRANSMITTER_EVIDENCE_ONLY_NOT_SIGNED_DYNAMICS",
        "neurons": neurons,
        "edges": edges,
        "receptor_audit": p["receptor_audit"],
        "resolved_sign_count": 0,
        "unknown_sign_count": len(edges),
        "decision": "DNG100_NT_SIGN_AUTHORITY_PARTIAL"
        if partial
        else "DNG100_NT_SOURCE_VERIFIED_SIGNS_UNKNOWN",
        "body_actuation": "NOT_DEFINED",
        "neural_dynamics": "NOT_IMPLEMENTED",
    }
    config = {
        "policy": p,
        "policy_sha256": POLICY_ID,
        "dataset": p["dataset"],
        "dataset_uuid": p["dataset_uuid"],
        "annotation_sha256": p["annotation_sha256"],
        "nt_source_sha256": p["nt_source_sha256"],
        "sdk_source_sha256": canonical_sha256(sdk),
        "motif_artifact_id": p["motif_artifact_id"],
        "extractor_version": SCHEMA,
        "extractor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "software_version": "neurofly-0.1.0/python-3.12/neuprint-python-0.6.3",
        "reproduction": "python -m neurofly.dng100_nt_sign_authority --replay ARTIFACT "
        "--nt-source OFFICIAL_FEATHER --motif-source PINNED_MOTIF_ARTIFACT",
    }
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema": SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([SCHEMA, ch, rh]),
    }


def load_inputs(nt_path, motif_path, sdk_path):
    structural = motif.load_artifact(motif_path)
    return (
        Path(nt_path).read_bytes(),
        (Path(motif_path) / "annotations.feather").read_bytes(),
        structural,
        json.loads(Path(sdk_path).read_bytes()),
    )


def validate_artifact(value, *inputs):
    expected = build_artifact(*inputs)
    if canonical_json_bytes(value) != canonical_json_bytes(expected):
        raise ValueError("contradictory semantic transmitter/sign evidence")
    return expected


def write_artifact(root, value, sdk):
    root = Path(root).resolve()
    if root.is_relative_to(motif.base.REPO):
        raise ValueError("raw scientific artifacts must remain outside Git")
    data = {
        "contract.json": canonical_json_bytes(value),
        "sdk-source.json": canonical_json_bytes(sdk),
    }
    manifest = {
        "schema": SCHEMA,
        "artifact_id": value["artifact_id"],
        "files": {
            n: {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
            for n, b in data.items()
        },
    }
    root.mkdir(parents=True, exist_ok=True)
    target = root / value["artifact_id"]
    if target.exists():
        if any((target / n).read_bytes() != b for n, b in data.items()) or (
            (target / "manifest.json").read_bytes() != canonical_json_bytes(manifest)
        ):
            raise ValueError("refuse to overwrite existing evidence artifact")
        return target
    staging = Path(tempfile.mkdtemp(prefix=".nt-", dir=root))
    try:
        for n, b in data.items():
            (staging / n).write_bytes(b)
        (staging / "manifest.json").write_bytes(canonical_json_bytes(manifest))
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return target


def load_artifact(path, nt_path=NT_SOURCE, motif_path=MOTIF_SOURCE):
    path = Path(path)
    pin = json.loads(REFERENCE_PATH.read_bytes())
    names = {"contract.json", "sdk-source.json", "manifest.json"}
    if (
        not path.is_dir()
        or {n.name for n in path.iterdir()} != names
        or any((path / n).is_symlink() for n in names)
    ):
        raise ValueError("missing or unsafe evidence artifact")
    data = {n: (path / n).read_bytes() for n in names - {"manifest.json"}}
    manifest = json.loads((path / "manifest.json").read_bytes())
    expected = {
        "schema": SCHEMA,
        "artifact_id": pin["artifact_id"],
        "files": {
            n: {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
            for n, b in data.items()
        },
    }
    if path.name != pin["artifact_id"] or manifest != expected:
        raise ValueError("evidence manifest integrity failure")
    parsed = {n: json.loads(b) for n, b in data.items()}
    if any(data[n] != canonical_json_bytes(v) for n, v in parsed.items()):
        raise ValueError("noncanonical evidence serialization")
    value = validate_artifact(
        parsed["contract.json"],
        *load_inputs(nt_path, motif_path, path / "sdk-source.json"),
    )
    if value != pin:
        raise ValueError("published scoped reference or logical identity mismatch")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--extract", type=Path)
    group.add_argument("--replay", type=Path)
    parser.add_argument("--nt-source", type=Path, default=NT_SOURCE)
    parser.add_argument("--motif-source", type=Path, default=MOTIF_SOURCE)
    parser.add_argument("--sdk-source", type=Path, default=SDK_SOURCE)
    args = parser.parse_args()
    try:
        if args.extract:
            inputs = load_inputs(args.nt_source, args.motif_source, args.sdk_source)
            value = build_artifact(*inputs)
            path = write_artifact(args.extract, value, inputs[3])
        else:
            path = args.replay
            value = load_artifact(path, args.nt_source, args.motif_source)
        print(
            json.dumps(
                {
                    "local_path": str(path),
                    "artifact_id": value["artifact_id"],
                    "config_sha256": value["config_sha256"],
                    "result_sha256": value["result_sha256"],
                    "decision": value["result"]["decision"],
                },
                indent=2,
            )
        )
    except Exception as exc:
        parser.exit(
            1, f"NT authority failed ({type(exc).__name__}); no substitution.\n"
        )


if __name__ == "__main__":
    main()
