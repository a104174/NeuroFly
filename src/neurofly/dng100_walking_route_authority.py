"""Bounded MaleCNS structural authority; no dynamics or body actuation."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import tempfile
from importlib.metadata import version
from pathlib import Path

from neurofly.malecns.models import MALECNS_DATASET, NEUPRINT_ENDPOINT
from neurofly.motor_neural_contract import (
    ANNOTATION_SOURCE_URL,
    HISTORICAL_ANNOTATION_SHA256,
    PINNED_NEUPRINT_PYTHON_VERSION,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

REPO = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO / "docs/science/dng100_walking_route_policy.json"
REFERENCE_PATH = REPO / "docs/science/dng100_walking_route_authority_reference.json"
DEFAULT_ROOT = REPO.parent / "neurofly-science/work/dng100-route-authority-v1"
POLICY_ID = "432bab639860f7778339871d203e9e4e26bdd576956ae54631e55b11a90d9ee5"
SCHEMA = "dng100_walking_route_authority_artifact_v1"
SOURCE_SCHEMA = "dng100_walking_route_source_v1"
DATASET_UUID = "4b2087c0fbe046bfaf0d60bc970e3e5d"
NODE_FIELDS = (
    "bodyId",
    "type",
    "instance",
    "somaSide",
    "superclass",
    "class",
    "subclass",
    "somaNeuromere",
    "status",
    "statusLabel",
)
EDGE_COLUMNS = ["pre", "post", "weight", "roiInfo"]
META_FIELDS = (
    "dataset",
    "uuid",
    "tag",
    "lastDatabaseEdit",
    "latestMutationId",
    "postHighAccuracyThreshold",
    "postHPThreshold",
    "preHPThreshold",
    "primaryRois",
)


def policy() -> dict:
    p = json.loads(POLICY_PATH.read_bytes())
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unrecognized structural selection policy")
    return p


def _positive_int(v):
    return type(v) is int and v > 0


def validate_nodes(nodes: list[dict]) -> dict[int, dict]:
    if type(nodes) is not list:
        raise ValueError("require annotation records")
    by_id = {}
    for n in nodes:
        if set(n) != set(NODE_FIELDS) or not _positive_int(n["bodyId"]):
            raise ValueError("invalid annotation schema/body identity")
        if n["bodyId"] in by_id:
            raise ValueError("duplicate/conflicting annotation identity")
        if any(
            v is not None and type(v) is not str for k, v in n.items() if k != "bodyId"
        ):
            raise ValueError("invalid annotation value")
        by_id[n["bodyId"]] = n
    for required in policy()["sources"]:
        n = by_id.get(required["body_id"])
        if (
            n is None
            or any(
                n[k] != required[v]
                for k, v in [
                    ("type", "type"),
                    ("instance", "instance"),
                    ("somaSide", "side"),
                ]
            )
            or n["superclass"] != "descending_neuron"
        ):
            raise ValueError("DNg100 bilateral authority conflict")
    return by_id


def annotation_nodes(raw: bytes) -> list[dict]:
    if hashlib.sha256(raw).hexdigest() != HISTORICAL_ANNOTATION_SHA256:
        raise ValueError("pinned annotation source integrity failure")
    import pandas as pd

    table = pd.read_feather(io.BytesIO(raw))
    if not set(NODE_FIELDS).issubset(table.columns):
        raise ValueError("unrecognized annotation dataset schema")
    # Preserve nulls; do not infer identity from morphology or rename neurons.
    nodes = json.loads(table[list(NODE_FIELDS)].to_json(orient="records"))
    validate_nodes(nodes)
    return nodes


def motor_ids(nodes: list[dict]) -> list[int]:
    definition = policy()["motor_annotation"]
    return sorted(
        n["bodyId"] for n in nodes if all(n[k] == v for k, v in definition.items())
    )


def edge_query(sources: list[int], targets: list[int] | None = None) -> str:
    selection = f"s.bodyId IN {json.dumps(sorted(sources))}"
    if targets is not None:
        selection += f" AND t.bodyId IN {json.dumps(sorted(targets))}"
    return (
        "MATCH (s:Neuron)-[e:ConnectsTo]->(t:Neuron) WHERE "
        + selection
        + " RETURN s.bodyId AS pre, t.bodyId AS post, e.weight AS weight, "
        "e.roiInfo AS roiInfo ORDER BY pre, post"
    )


def parse_edges(query: dict, name: str) -> list[dict]:
    if set(query) != {"cypher", "columns", "data"} or query["columns"] != EDGE_COLUMNS:
        raise ValueError("malformed directed connectivity source")
    if type(query["data"]) is not list or type(query["cypher"]) is not str:
        raise ValueError("invalid query evidence")
    edges, seen = [], set()
    for i, row in enumerate(query["data"]):
        if type(row) is not list or len(row) != 4:
            raise ValueError("invalid connectivity row")
        pre, post, count, raw_roi = row
        if not all(_positive_int(v) for v in (pre, post, count)):
            raise ValueError("invalid directed ID/synapse count")
        if (pre, post) in seen:
            raise ValueError("duplicate/conflicting directed edge")
        seen.add((pre, post))
        if type(raw_roi) is not str:
            raise ValueError("missing serialized ROI evidence")
        roi = json.loads(raw_roi)
        if type(roi) is not dict:
            raise ValueError("invalid ROI source")
        for label, values in roi.items():
            if type(label) is not str or type(values) is not dict:
                raise ValueError("invalid ROI record")
            if "post" not in values or any(
                type(v) is not int or v < 0 for v in values.values()
            ):
                raise ValueError("invalid ROI counts")
        edges.append(
            {
                "pre": pre,
                "post": post,
                "synapse_count": count,
                "roi_counts": roi,
                "source_reference": {
                    "query": name,
                    "row": i,
                    "row_sha256": canonical_sha256(row),
                },
            }
        )
    if [(e["pre"], e["post"]) for e in edges] != sorted(seen):
        raise ValueError("unordered connectivity source")
    return edges


def validate_source(source: dict, nodes: list[dict]) -> tuple[list, list]:
    p = policy()
    if set(source) != {
        "schema",
        "dataset",
        "endpoint",
        "annotation_sha256",
        "neuprint_python_version",
        "metadata",
        "queries",
    }:
        raise ValueError("contradictory source schema")
    if (
        source["schema"] != SOURCE_SCHEMA
        or source["dataset"] != MALECNS_DATASET
        or source["endpoint"] != NEUPRINT_ENDPOINT
        or source["annotation_sha256"] != HISTORICAL_ANNOTATION_SHA256
        or source["neuprint_python_version"] != PINNED_NEUPRINT_PYTHON_VERSION
    ):
        raise ValueError("wrong source dataset/version/provenance")
    meta = source["metadata"]
    if (
        set(meta) != set(META_FIELDS)
        or (meta["dataset"], meta["tag"]) != ("male-cns", "v1.0")
        or meta["uuid"] != DATASET_UUID
    ):
        raise ValueError("invalid dataset metadata")
    if not meta["uuid"] or not meta["lastDatabaseEdit"]:
        raise ValueError("missing release metadata")
    if type(meta["postHighAccuracyThreshold"]) is not float or (
        meta["postHighAccuracyThreshold"] != p["required_post_high_accuracy_threshold"]
    ):
        raise ValueError("unsupported source confidence convention")
    for field in ("postHPThreshold", "preHPThreshold"):
        v = meta[field]
        if type(v) not in (int, float) or not 0 <= v <= 1:
            raise ValueError("invalid confidence metadata")
    if not set(p["front_leg_synapse_rois"]).issubset(meta["primaryRois"]):
        raise ValueError("front-leg ROI authority missing")
    if set(source["queries"]) != {"outputs", "motor_inputs"}:
        raise ValueError("missing interval of graph evidence")
    first = parse_edges(source["queries"]["outputs"], "outputs")
    second = parse_edges(source["queries"]["motor_inputs"], "motor_inputs")
    starts = [s["body_id"] for s in p["sources"]]
    neighbours = sorted({e["post"] for e in first})
    motors = motor_ids(nodes)
    if not motors:
        raise ValueError("front-leg motor classification authority missing")
    if source["queries"]["outputs"]["cypher"] != edge_query(starts):
        raise ValueError("contradictory directed source query")
    if source["queries"]["motor_inputs"]["cypher"] != edge_query(neighbours, motors):
        raise ValueError("contradictory bounded target query")
    if any(e["pre"] not in starts for e in first) or any(
        e["pre"] not in neighbours or e["post"] not in motors for e in second
    ):
        raise ValueError("reversed/out-of-scope connectivity")
    return first, second


def extract_routes(source: dict, nodes: list[dict]) -> dict:
    """Pure parser/extractor; synthetic inputs are only suitable for unit tests."""
    by_id = validate_nodes(nodes)
    first, second = validate_source(source, nodes)
    p = policy()
    motors = set(motor_ids(nodes))
    # One structural edge may occur in both queries. Preserve both references.
    graph = {}
    for e in first + second:
        key = (e["pre"], e["post"])
        if key in graph:
            existing = graph[key]
            if any(existing[k] != e[k] for k in ("synapse_count", "roi_counts")):
                raise ValueError("conflicting duplicate edge evidence")
            existing["source_references"].append(e["source_reference"])
        else:
            graph[key] = {k: v for k, v in e.items() if k != "source_reference"}
            graph[key]["source_references"] = [e["source_reference"]]
    edges = []
    for key, e in sorted(graph.items()):
        e["dataset"] = MALECNS_DATASET
        e["confidence_policy"] = p["confidence_policy"]
        e["edge_id"] = canonical_sha256(["directed_chemical_edge", *key, e])
        edges.append(e)
    candidates, excluded = [], []
    outgoing = {}
    for e in second:
        outgoing.setdefault(e["pre"], []).append(e["post"])
    for e in first:
        start, neighbour = e["pre"], e["post"]
        paths = [[start, neighbour]] if neighbour in motors else []
        paths += [[start, neighbour, target] for target in outgoing.get(neighbour, [])]
        if not paths:
            excluded.append(
                {
                    "edge": [start, neighbour],
                    "reason": "NO_DIRECT_OR_ONE_INTERNEURON_FRONT_MOTOR_ROUTE",
                }
            )
        for ids in paths:
            if len(ids) != len(set(ids)):
                excluded.append({"nodes": ids, "reason": "REPEATED_NODE_CYCLE"})
                continue
            route_edges = [graph[a, b] for a, b in zip(ids[:-1], ids[1:], strict=True)]
            records = [by_id.get(i) for i in ids]
            reasons = []
            if any(
                n is None or not n["type"] or n["somaSide"] not in ("L", "R")
                for n in records
            ):
                reasons.append("MISSING_OR_UNRESOLVED_IDENTITY")
            if len(ids) == 3 and (
                records[1] is None or records[1]["superclass"] != "vnc_intrinsic"
            ):
                reasons.append("INTERMEDIATE_NOT_ANNOTATED_VNC_INTRINSIC")
            if not any(
                route_edges[-1]["roi_counts"].get(r, {}).get("post", 0) > 0
                for r in p["front_leg_synapse_rois"]
            ):
                reasons.append("FRONT_LEG_SYNAPSE_ROI_UNRESOLVED")
            candidates.append(
                {
                    "nodes": ids,
                    "length_edges": len(ids) - 1,
                    "edge_ids": [e["edge_id"] for e in route_edges],
                    "classification": "CLASSIFICATION_UNRESOLVED"
                    if reasons
                    else "STRUCTURAL_FRONT_LEG_MOTOR_ROUTE",
                    "unresolved_reasons": reasons,
                    "physiological_function": "NOT_VALIDATED",
                }
            )
    candidates.sort(key=lambda r: r["nodes"])
    sensitivity = {}
    for threshold in [
        p["primary_minimum_synapse_count"],
        *p["sensitivity_minimum_synapse_counts"],
    ]:
        eligible = [
            r
            for r in candidates
            if all(
                graph[a, b]["synapse_count"] >= threshold
                for a, b in zip(r["nodes"][:-1], r["nodes"][1:], strict=True)
            )
        ]
        sensitivity[str(threshold)] = {
            str(s["body_id"]): {
                "direct": sum(
                    r["nodes"][0] == s["body_id"]
                    and r["length_edges"] == 1
                    and not r["unresolved_reasons"]
                    for r in eligible
                ),
                "indirect": sum(
                    r["nodes"][0] == s["body_id"]
                    and r["length_edges"] == 2
                    and not r["unresolved_reasons"]
                    for r in eligible
                ),
                "unresolved": sum(
                    r["nodes"][0] == s["body_id"] and bool(r["unresolved_reasons"])
                    for r in eligible
                ),
            }
            for s in p["sources"]
        }
    resolved = [r for r in candidates if not r["unresolved_reasons"]]
    decision = (
        "DNG100_ROUTE_AUTHORITY_VERIFIED"
        if resolved
        and len(resolved) == len(candidates)
        and {r["nodes"][0] for r in resolved} == {10045, 10056}
        else "DNG100_ROUTE_AUTHORITY_PARTIAL"
        if candidates
        else "DNG100_ROUTE_AUTHORITY_NO_SUPPORTED_PATH"
    )
    relevant_ids = sorted(
        {10045, 10056} | {i for e in edges for i in (e["pre"], e["post"])}
    )
    premotor_candidates = {r["nodes"][1] for r in resolved if r["length_edges"] == 2}

    def record(i):
        n = by_id.get(i)
        role = (
            "DNG100_SOURCE"
            if i in (10045, 10056)
            else "ANNOTATED_FRONT_LEG_MOTOR"
            if i in motors
            else "STRUCTURAL_PREMOTOR_CANDIDATE"
            if i in premotor_candidates
            else "CLASSIFICATION_UNRESOLVED"
            if n is None or not n["type"] or n["somaSide"] not in ("L", "R")
            else "OUT_OF_RESOLVED_ROUTE_SELECTION"
        )
        return {
            "body_id": i,
            "annotation": n,
            "structural_role": role,
            "annotation_status": "AVAILABLE"
            if n is not None
            else "CLASSIFICATION_UNRESOLVED",
            "annotation_evidence": {
                "file": "annotations.feather",
                "body_id": i,
                "sha256": HISTORICAL_ANNOTATION_SHA256,
            },
        }

    return {
        "classification": "STRUCTURAL_AUTHORITY_ONLY",
        "decision": decision,
        "neurons": [record(i) for i in relevant_ids],
        "front_motor_authority": [by_id[i] for i in sorted(motors)],
        "edges": edges,
        "routes": candidates,
        "excluded": excluded,
        "threshold_sensitivity": sensitivity,
        "completeness": "BOUNDED_NEURON_GRAPH_NO_LONGER_PATH_OR_SYNAPSE_SEARCH",
        "neurotransmitter_sign": "NOT_INFERRED",
        "body_actuation": "NOT_DEFINED",
    }


def build_artifact(source: dict, raw: bytes) -> dict:
    nodes = annotation_nodes(raw)
    result = extract_routes(source, nodes)
    config = {
        "policy": policy(),
        "policy_sha256": POLICY_ID,
        "source_snapshot_sha256": canonical_sha256(source),
        "annotation_sha256": HISTORICAL_ANNOTATION_SHA256,
        "extractor_version": SCHEMA,
        "extractor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
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


def validate_artifact(artifact: dict, source: dict, raw: bytes) -> dict:
    expected = build_artifact(source, raw)
    if canonical_json_bytes(artifact) != canonical_json_bytes(expected):
        raise ValueError("artifact differs from complete structural semantic replay")
    return expected


def acquire_source() -> tuple[dict, bytes]:
    """Official, read-only bounded queries; never replace a pinned source."""
    from urllib.request import urlopen

    from neuprint import fetch_meta

    from neurofly.malecns.client import create_client

    if version("neuprint-python") != PINNED_NEUPRINT_PYTHON_VERSION:
        raise ValueError("unrecognized source client version")
    raw = urlopen(ANNOTATION_SOURCE_URL, timeout=30).read()
    nodes = annotation_nodes(raw)
    client = create_client()
    initial = fetch_meta(client=client)
    meta = {k: initial[k] for k in META_FIELDS}

    def fetch(q):
        value = client.fetch_custom(q, format="json")
        return {"cypher": q, "columns": value["columns"], "data": value["data"]}

    first = fetch(edge_query([10045, 10056]))
    neighbours = sorted({e["post"] for e in parse_edges(first, "outputs")})
    second = fetch(edge_query(neighbours, motor_ids(nodes)))
    final = fetch_meta(client=client)
    if meta != {k: final[k] for k in META_FIELDS}:
        raise ValueError("source database changed during bounded acquisition")
    source = {
        "schema": SOURCE_SCHEMA,
        "dataset": client.dataset,
        "endpoint": NEUPRINT_ENDPOINT,
        "annotation_sha256": HISTORICAL_ANNOTATION_SHA256,
        "neuprint_python_version": PINNED_NEUPRINT_PYTHON_VERSION,
        "metadata": meta,
        "queries": {"outputs": first, "motor_inputs": second},
    }
    validate_source(source, nodes)
    if REFERENCE_PATH.exists():
        pin = json.loads(REFERENCE_PATH.read_bytes())
        if canonical_sha256(source) != pin["source_snapshot_sha256"]:
            raise ValueError("source drift; existing pin must not be replaced")
    return source, raw


def write_artifact(root: Path, source: dict, raw: bytes) -> Path:
    root = Path(root).resolve()
    if root.is_relative_to(REPO):
        raise ValueError("source artifacts must remain outside repository")
    result = build_artifact(source, raw)
    payloads = {
        "source.json": canonical_json_bytes(source),
        "contract.json": canonical_json_bytes(result),
        "annotations.feather": raw,
    }
    manifest = {
        "schema": SCHEMA,
        "artifact_id": result["artifact_id"],
        "files": {
            n: {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
            for n, b in payloads.items()
        },
    }
    root.mkdir(parents=True, exist_ok=True)
    target = root / result["artifact_id"]
    if target.exists():
        load_artifact(
            target,
            reference={
                "artifact_id": result["artifact_id"],
                "source_snapshot_sha256": canonical_sha256(source),
            },
        )
        return target
    staging = Path(tempfile.mkdtemp(prefix=".dng100-", dir=root))
    try:
        for name, b in payloads.items():
            (staging / name).write_bytes(b)
        (staging / "manifest.json").write_bytes(canonical_json_bytes(manifest))
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return target


def load_artifact(path: Path, *, reference: dict | None = None) -> dict:
    path = Path(path)
    pin = json.loads(REFERENCE_PATH.read_bytes()) if reference is None else reference
    names = {"annotations.feather", "source.json", "contract.json", "manifest.json"}
    if not path.is_dir() or {p.name for p in path.iterdir()} != names:
        raise ValueError("missing/unexpected source artifact files")
    if any((path / name).is_symlink() for name in names):
        raise ValueError("symlinked authority input")
    manifest = json.loads((path / "manifest.json").read_bytes())
    payloads = {n: (path / n).read_bytes() for n in names - {"manifest.json"}}
    expected = {
        "schema": SCHEMA,
        "artifact_id": pin["artifact_id"],
        "files": {
            n: {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
            for n, b in payloads.items()
        },
    }
    if manifest != expected or path.name != pin["artifact_id"]:
        raise ValueError("artifact manifest/source integrity failure")
    source = json.loads(payloads["source.json"])
    if payloads["source.json"] != canonical_json_bytes(source):
        raise ValueError("noncanonical source serialization")
    if canonical_sha256(source) != pin["source_snapshot_sha256"]:
        raise ValueError("pinned connectivity source integrity failure")
    artifact = json.loads(payloads["contract.json"])
    if payloads["contract.json"] != canonical_json_bytes(artifact):
        raise ValueError("noncanonical contract serialization")
    result = validate_artifact(artifact, source, payloads["annotations.feather"])
    if result["artifact_id"] != pin["artifact_id"]:
        raise ValueError("pinned semantic result identity failure")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acquire", type=Path, metavar="EXTERNAL_OUTPUT_ROOT")
    group.add_argument("--replay", type=Path, metavar="PINNED_ARTIFACT")
    args = parser.parse_args()
    try:
        if args.acquire:
            source, raw = acquire_source()
            path = write_artifact(args.acquire, source, raw)
            result = build_artifact(source, raw)
        else:
            path, result = args.replay, load_artifact(args.replay)
        print(
            json.dumps(
                {
                    "local_path": str(path),
                    "artifact_id": result["artifact_id"],
                    "source_snapshot_sha256": result["config"][
                        "source_snapshot_sha256"
                    ],
                    "config_sha256": result["config_sha256"],
                    "result_sha256": result["result_sha256"],
                    "decision": result["result"]["decision"],
                    "threshold_sensitivity": result["result"]["threshold_sensitivity"],
                },
                indent=2,
            )
        )
    except Exception as exc:
        # Third-party exceptions can include authentication/request details.
        parser.exit(
            1,
            f"Structural authority failed ({type(exc).__name__}); "
            "no source substitution or automatic retry.\n",
        )


if __name__ == "__main__":
    main()
