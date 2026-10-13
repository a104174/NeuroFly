"""Pinned, bounded structural recurrence. No neural dynamics or body actuation."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import shutil
import tempfile
from importlib.metadata import version
from pathlib import Path

from neurofly import dng100_walking_route_authority as base
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

SCHEMA = "dng100_recurrent_motif_authority_artifact_v1"
SOURCE_SCHEMA = "dng100_recurrent_motif_source_v1"
POLICY_PATH = base.REPO / "docs/science/dng100_recurrent_motif_policy.json"
REFERENCE_PATH = base.REPO / "docs/science/dng100_recurrent_motif_reference.json"
DEFAULT_ROOT = base.REPO.parent / "neurofly-science/work/dng100-recurrent-motif-v1"
POLICY_ID = "1b71c798cb291e76378fa5ec3e03e836b6a1910e4b07ac0e9b68f4537e96f4a8"
PRESENCE_FIELDS = ["bodyId", "type", "somaSide", "somaNeuromere", "superclass"]
EDGE_QUERIES = (
    "induced",
    "dng_intermediate_inputs",
    "primary_outputs",
    "other_motor_outputs",
    "motor_inputs",
)


def policy():
    value = json.loads(POLICY_PATH.read_bytes())
    if canonical_sha256(value) != POLICY_ID:
        raise ValueError("unrecognized preregistered motif policy")
    return value


def select_members(nodes):
    base.validate_nodes(nodes)
    types = policy()["type_labels"]
    return sorted(
        [n for n in nodes if n["type"] in types],
        key=lambda n: n["bodyId"],
    )


def anatomy(n):
    p = policy()
    reasons = []
    if n["type"] not in p["type_labels"]:
        reasons.append("UNKNOWN_MOTIF_TYPE")
    if n["superclass"] != p["anatomy"]["superclass"]:
        reasons.append("NOT_ANNOTATED_VNC_INTRINSIC")
    if n["somaSide"] not in p["anatomy"]["sides"]:
        reasons.append("SIDE_UNRESOLVED")
    elif n["instance"] != f"{n['type']}_{n['somaSide']}":
        raise ValueError("conflicting type/side/instance authority")
    if n["somaNeuromere"] not in p["anatomy"]["segments"]:
        reasons.append("SEGMENT_UNRESOLVED")
    if any(n[k] != v for k, v in p["tracing_for_verified_motif"].items()):
        reasons.append("TRACING_NOT_REVIEWED_OR_INCOMPLETE")
    return reasons


def presence_query(ids):
    return (
        "MATCH (n:Neuron) WHERE n.bodyId IN "
        + json.dumps(sorted(ids))
        + " RETURN "
        + ", ".join(f"n.{k} AS {k}" for k in PRESENCE_FIELDS)
        + " ORDER BY bodyId"
    )


def count_query(ids):
    return (
        base.edge_query(ids, ids).split(" RETURN ")[0]
        + " RETURN count(e) AS edge_count"
    )


def required_queries(nodes, previous, queries):
    members = select_members(nodes)
    ids = [n["bodyId"] for n in members]
    primary = [n["bodyId"] for n in members if n["somaNeuromere"] == "T1"]
    other = sorted(set(ids) - set(primary))
    motors = base.motor_ids(nodes)
    prior_first, _ = base.validate_source(previous, nodes)
    dng_neighbours = sorted({e["post"] for e in prior_first})
    output = base.parse_edges(queries["primary_outputs"], "primary_outputs")
    neighbours = sorted({e["post"] for e in output})
    return {
        "presence": presence_query(sorted(set(ids + [10045, 10056] + motors))),
        "induced": base.edge_query(ids, ids),
        "induced_count": count_query(ids),
        "dng_intermediate_inputs": base.edge_query(dng_neighbours, ids),
        "primary_outputs": base.edge_query(primary),
        "other_motor_outputs": base.edge_query(other, motors),
        "motor_inputs": base.edge_query(neighbours, motors),
    }


def validate_sources(source, previous, nodes):
    """Parser validation; production provenance pins are enforced by build_artifact."""
    if set(source) != {
        "schema",
        "dataset",
        "endpoint",
        "metadata",
        "neuprint_python_version",
        "queries",
    } or (
        source["schema"] != SOURCE_SCHEMA
        or source["dataset"] != base.MALECNS_DATASET
        or source["endpoint"] != base.NEUPRINT_ENDPOINT
        or source["neuprint_python_version"] != base.PINNED_NEUPRINT_PYTHON_VERSION
        or source["metadata"] != previous["metadata"]
    ):
        raise ValueError("source version/metadata differs from prior pinned authority")
    q = source["queries"]
    if set(q) != {*EDGE_QUERIES, "presence", "induced_count"}:
        raise ValueError("incomplete bounded query coverage")
    expected = required_queries(nodes, previous, q)
    if any(q[k]["cypher"] != v for k, v in expected.items()):
        raise ValueError("incorrect directed query scope")
    by_id = base.validate_nodes(nodes)
    ids = {n["bodyId"] for n in select_members(nodes)}
    primary = {i for i in ids if by_id[i]["somaNeuromere"] == "T1"}
    motors = set(base.motor_ids(nodes))
    presence_ids = sorted(ids | {10045, 10056} | motors)
    presence = q["presence"]
    if set(presence) != {"cypher", "columns", "data"} or (
        presence["columns"] != PRESENCE_FIELDS
        or presence["data"]
        != [[by_id[i][k] for k in PRESENCE_FIELDS] for i in presence_ids]
    ):
        raise ValueError("missing/conflicting official neuron presence/anatomy")
    parsed = {k: base.parse_edges(q[k], k) for k in EDGE_QUERIES}
    count = q["induced_count"]
    if set(count) != {"cypher", "columns", "data"} or (
        count["columns"] != ["edge_count"]
        or type(count["data"]) is not list
        or len(count["data"]) != 1
        or type(count["data"][0]) is not list
        or len(count["data"][0]) != 1
        or type(count["data"][0][0]) is not int
        or count["data"][0][0] != len(parsed["induced"])
    ):
        raise ValueError("induced graph coverage/count contradiction")
    first, _ = base.validate_source(previous, nodes)
    dng_neighbours = {e["post"] for e in first}
    neighbours = {e["post"] for e in parsed["primary_outputs"]}
    scopes = {
        "induced": (ids, ids),
        "dng_intermediate_inputs": (dng_neighbours, ids),
        "primary_outputs": (primary, None),
        "other_motor_outputs": (ids - primary, motors),
        "motor_inputs": (neighbours, motors),
    }
    for k, (starts, ends) in scopes.items():
        if any(
            e["pre"] not in starts or (ends is not None and e["post"] not in ends)
            for e in parsed[k]
        ):
            raise ValueError("reversed/out-of-scope directed edge")
    return parsed, first


def canonical_cycle(ids):
    ids = tuple(ids)
    if len(ids) not in (2, 3) or len(set(ids)) != len(ids):
        raise ValueError("repeated-node pseudo-cycle or unsupported cycle length")
    return min(ids[i:] + ids[:i] for i in range(len(ids)))


def enumerate_cycles(ids, edges):
    found = set()
    for length in (2, 3):
        for path in itertools.permutations(sorted(ids), length):
            if all((path[i], path[(i + 1) % length]) in edges for i in range(length)):
                found.add(canonical_cycle(path))
    return sorted(found)


def has_roi(edge, segment):
    return any(
        edge["roi_counts"].get(f"LegNp({segment})({side})", {}).get("post", 0) > 0
        for side in ("L", "R")
    )


def extract_graph(source, previous, nodes):
    """Pure structural extraction; synthetic graphs are isolated parser tests only."""
    members = select_members(nodes)
    by_id = base.validate_nodes(nodes)
    parsed, first = validate_sources(source, previous, nodes)
    p = policy()
    graph = {}
    for label, edges in [("prior_outputs", first), *parsed.items()]:
        for e in edges:
            key = (e["pre"], e["post"])
            ref = {
                **e["source_reference"],
                "file": "prior_source.json"
                if label == "prior_outputs"
                else "source.json",
            }
            if label == "prior_outputs":
                ref["query"] = "outputs"
            if key in graph:
                if any(graph[key][k] != e[k] for k in ("synapse_count", "roi_counts")):
                    raise ValueError("conflicting duplicate directed evidence")
                graph[key]["source_references"].append(ref)
            else:
                graph[key] = {k: v for k, v in e.items() if k != "source_reference"}
                graph[key]["source_references"] = [ref]
    # Only the all-pair query establishes presence/absence of induced edges.
    induced = {
        (e["pre"], e["post"]): graph[e["pre"], e["post"]] for e in parsed["induced"]
    }
    ids = [n["bodyId"] for n in members]
    if any(a in ids and b in ids and (a, b) not in induced for a, b in graph):
        raise ValueError("induced absence contradicts observed context edge")
    for (a, b), edge in graph.items():
        edge["dataset"] = base.MALECNS_DATASET
        edge["confidence_policy"] = p["confidence_policy"]
        for field, body in (("pre_anatomy", a), ("post_anatomy", b)):
            n = by_id.get(body)
            edge[field] = (
                {k: n[k] for k in ("type", "somaSide", "somaNeuromere", "superclass")}
                if n is not None
                else None
            )
        edge["annotation_sha256"] = base.HISTORICAL_ANNOTATION_SHA256
    node_records = [
        {
            "body_id": n["bodyId"],
            "annotation": n,
            "literature_role": p["literature_role_labels"][n["type"]],
            "anatomical_reasons": anatomy(n),
            "classification": "CLASSIFICATION_UNRESOLVED"
            if anatomy(n)
            else "ANNOTATED_MOTIF_MEMBER",
            "evidence": {
                "file": "annotations.feather",
                "body_id": n["bodyId"],
                "sha256": base.HISTORICAL_ANNOTATION_SHA256,
            },
        }
        for n in members
    ]

    def inventory(starts, ends, evidence):
        def cross(a, b, field, valid):
            left, right = by_id[a][field], by_id[b][field]
            return left != right if left in valid and right in valid else None

        return [
            {
                "pre": a,
                "post": b,
                "status": "OBSERVED"
                if (a, b) in evidence
                else "VERIFIED_SOURCE_COMPLETE_ABSENT",
                "synapse_count": evidence[a, b]["synapse_count"]
                if (a, b) in evidence
                else None,
                "cross_side": cross(a, b, "somaSide", ("L", "R")),
                "cross_segment": cross(a, b, "somaNeuromere", ("T1", "T2", "T3")),
            }
            for a in sorted(starts)
            for b in sorted(ends)
        ]

    pair_inventory = inventory(ids, ids, induced)
    dng_direct = inventory(
        [10045, 10056], ids, {(e["pre"], e["post"]): e for e in first}
    )
    motor_direct = inventory(
        ids,
        base.motor_ids(nodes),
        {
            (e["pre"], e["post"]): e
            for e in parsed["primary_outputs"] + parsed["other_motor_outputs"]
        },
    )

    def routes(starts, direct, second, targets, *, indirect_starts=None):
        output, rejected = [], []
        downstream = {}
        for e in second:
            downstream.setdefault(e["pre"], []).append(e["post"])
        for e in direct:
            a, b = e["pre"], e["post"]
            if a not in starts:
                continue
            paths = [[a, b]] if b in targets else []
            if indirect_starts is None or a in indirect_starts:
                paths += [[a, b, c] for c in downstream.get(b, [])]
            for path in paths:
                if len(set(path)) != len(path):
                    rejected.append({"nodes": path, "reason": "REPEATED_NODE_CYCLE"})
                    continue
                reasons = []
                records = [by_id.get(i) for i in path]
                if any(
                    n is None or not n["type"] or n["somaSide"] not in ("L", "R")
                    for n in records
                ):
                    reasons.append("CONTEXT_IDENTITY_UNRESOLVED")
                if len(path) == 3 and (
                    records[1] is None or records[1]["superclass"] != "vnc_intrinsic"
                ):
                    reasons.append("INTERMEDIATE_NOT_ANNOTATED_VNC_INTRINSIC")
                pairs = list(zip(path[:-1], path[1:], strict=True))
                target = records[-1]
                segment = target["somaNeuromere"] if target else None
                if segment not in ("T1", "T2", "T3") or not has_roi(
                    graph[pairs[-1]], segment
                ):
                    reasons.append("FINAL_SEGMENT_ROI_UNRESOLVED")
                output.append(
                    {
                        "nodes": path,
                        "classification": "STRUCTURAL_REACHABILITY"
                        if not reasons
                        else "CLASSIFICATION_UNRESOLVED",
                        "unresolved_reasons": reasons,
                        "side_sequence": [
                            n["somaSide"] if n else None for n in records
                        ],
                        "segment_sequence": [
                            n["somaNeuromere"] if n else None for n in records
                        ],
                        "physiological_recruitment": "NOT_VALIDATED",
                    }
                )
        return sorted(output, key=lambda r: r["nodes"]), sorted(
            rejected, key=lambda r: r["nodes"]
        )

    inputs, input_rejected = routes(
        {10045, 10056}, first, parsed["dng_intermediate_inputs"], set(ids)
    )
    outputs, output_rejected = routes(
        set(ids),
        parsed["primary_outputs"] + parsed["other_motor_outputs"],
        parsed["motor_inputs"],
        set(base.motor_ids(nodes)),
        indirect_starts={n["bodyId"] for n in members if n["somaNeuromere"] == "T1"},
    )
    # Nonprimary members have direct output coverage only.
    # Their unqueried indirect routes are never labeled absent.
    sensitivity = {}
    for threshold in [
        p["primary_minimum_synapse_count"],
        *p["sensitivity_minimum_synapse_counts"],
    ]:
        eligible = {
            key for key, e in induced.items() if e["synapse_count"] >= threshold
        }
        cycles = []
        for cycle in enumerate_cycles(ids, eligible):
            ns = [by_id[i] for i in cycle]
            sides = {n["somaSide"] for n in ns}
            segments = {n["somaNeuromere"] for n in ns}
            reasons = []
            if any(anatomy(n) for n in ns):
                reasons.append("ANATOMY_OR_TRACING_UNRESOLVED")
            if len(sides) != 1 or len(segments) != 1:
                reasons.append("CROSS_SIDE_OR_SEGMENT_CONTEXT_ONLY")
            if len(cycle) != 3 or {n["type"] for n in ns} != set(p["type_labels"]):
                reasons.append("NOT_THREE_DISTINCT_LITERATURE_TYPES")
            segment = ns[0]["somaNeuromere"]
            if segment not in ("T1", "T2", "T3") or not all(
                has_roi(induced[cycle[i], cycle[(i + 1) % len(cycle)]], segment)
                for i in range(len(cycle))
            ):
                reasons.append("CYCLE_SEGMENT_ROI_UNRESOLVED")
            cycles.append(
                {
                    "nodes": list(cycle),
                    "length": len(cycle),
                    "qualifying_three_type_motif": not reasons,
                    "qualification_reasons": reasons,
                    "rhythm": "NOT_SIMULATED",
                }
            )

        def eligible_route(r):
            return all(
                graph[a, b]["synapse_count"] >= threshold
                for a, b in zip(r["nodes"][:-1], r["nodes"][1:], strict=True)
            )

        groups = []
        for segment in ("T1", "T2", "T3"):
            for side in ("L", "R"):
                group = {
                    n["bodyId"]
                    for n in members
                    if n["somaNeuromere"] == segment and n["somaSide"] == side
                }
                local = [c for c in cycles if set(c["nodes"]).issubset(group)]
                ins = [
                    r for r in inputs if r["nodes"][-1] in group and eligible_route(r)
                ]
                outs = [
                    r for r in outputs if r["nodes"][0] in group and eligible_route(r)
                ]
                groups.append(
                    {
                        "segment": segment,
                        "side": side,
                        "members": sorted(group),
                        "types_present": sorted({by_id[i]["type"] for i in group}),
                        "cycles_two": sum(c["length"] == 2 for c in local),
                        "cycles_three": sum(c["length"] == 3 for c in local),
                        "qualifying_motifs": sum(
                            c["qualifying_three_type_motif"] for c in local
                        ),
                        "dng_inputs_resolved": sum(
                            not r["unresolved_reasons"] for r in ins
                        ),
                        "dng_inputs_unresolved": sum(
                            bool(r["unresolved_reasons"]) for r in ins
                        ),
                        "motor_outputs_resolved": sum(
                            not r["unresolved_reasons"] for r in outs
                        ),
                        "motor_outputs_unresolved": sum(
                            bool(r["unresolved_reasons"]) for r in outs
                        ),
                        "indirect_motor_coverage": "ASSESSED"
                        if segment == "T1"
                        else "NOT_QUERIED",
                    }
                )
        sensitivity[str(threshold)] = {"cycles": cycles, "groups": groups}
    primary_groups = [g for g in sensitivity["1"]["groups"] if g["segment"] == "T1"]
    primary_members = {n["bodyId"] for n in members if n["somaNeuromere"] == "T1"}
    anatomy_complete = all(
        set(g["types_present"]) == set(p["type_labels"]) for g in primary_groups
    ) and all(not anatomy(by_id[i]) for i in primary_members)
    dng_cover = {
        r["nodes"][0]
        for r in inputs
        if r["nodes"][-1] in primary_members and not r["unresolved_reasons"]
    }
    selection_unresolved = any(anatomy(n) for n in members)
    verified = (
        anatomy_complete
        and not selection_unresolved
        and dng_cover == {10045, 10056}
        and all(
            g["qualifying_motifs"]
            and g["dng_inputs_resolved"]
            and g["motor_outputs_resolved"]
            for g in primary_groups
        )
    )
    decision = (
        "DNG100_RECURRENT_MOTIF_AUTHORITY_VERIFIED"
        if verified
        else "DNG100_RECURRENT_MOTIF_NO_SUPPORTED_CYCLE"
        if anatomy_complete
        and not selection_unresolved
        and not any(g["cycles_two"] or g["cycles_three"] for g in primary_groups)
        else "DNG100_RECURRENT_MOTIF_AUTHORITY_PARTIAL"
    )
    context_ids = {i for r in inputs + outputs for i in r["nodes"]} | {10045, 10056}
    return {
        "classification": "STRUCTURAL_AUTHORITY_ONLY",
        "decision": decision,
        "members": node_records,
        "pair_inventory": pair_inventory,
        "dng_direct_inventory": dng_direct,
        "motor_direct_inventory": motor_direct,
        "front_motor_authority": [by_id[i] for i in base.motor_ids(nodes)],
        "edges": [graph[key] for key in sorted(graph)],
        "context_annotations": [
            {"body_id": i, "annotation": by_id.get(i)} for i in sorted(context_ids)
        ],
        "dng_inputs": inputs,
        "motor_outputs": outputs,
        "rejected_context_routes": input_rejected + output_rejected,
        "threshold_sensitivity": sensitivity,
        "coverage": "COMPLETE_REQUESTED_NEURON_PAIR_SCOPE_NOT_COMPLETE_BIOLOGY",
        "neurotransmitter_predictions": "UNAVAILABLE_IN_PINNED_ANNOTATION_AUTHORITY",
        "receptor_identity": "NOT_ESTABLISHED",
        "physiological_sign": "NOT_ASSIGNED",
        "functional_gain": "NOT_DEFINED",
        "conduction_delay": "NOT_DEFINED",
        "rhythm": "NOT_SIMULATED",
        "body_actuation": "NOT_DEFINED",
    }


def build_artifact(source, previous, raw):
    if canonical_sha256(previous) != policy()["prior_source_snapshot_sha256"]:
        raise ValueError("prior scoped source pin mismatch")
    result = extract_graph(source, previous, base.annotation_nodes(raw))
    config = {
        "policy": policy(),
        "policy_sha256": POLICY_ID,
        "annotation_sha256": base.HISTORICAL_ANNOTATION_SHA256,
        "prior_source_sha256": canonical_sha256(previous),
        "source_sha256": canonical_sha256(source),
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


def validate_artifact(value, source, previous, raw):
    expected = build_artifact(source, previous, raw)
    if canonical_json_bytes(value) != canonical_json_bytes(expected):
        raise ValueError("contradictory semantic motif replay")
    return expected


def prior_artifact():
    ref = json.loads(base.REFERENCE_PATH.read_bytes())
    if ref["artifact_id"] != policy()["prior_artifact_id"]:
        raise ValueError("incorrect previous route authority")
    path = base.DEFAULT_ROOT / ref["artifact_id"]
    base.load_artifact(path)
    return json.loads((path / "source.json").read_bytes()), (
        path / "annotations.feather"
    ).read_bytes()


def acquire_source():
    from neuprint import fetch_meta

    from neurofly.malecns.client import create_client

    if version("neuprint-python") != base.PINNED_NEUPRINT_PYTHON_VERSION:
        raise ValueError("unsupported source SDK")
    previous, raw = prior_artifact()
    nodes = base.annotation_nodes(raw)
    client = create_client()
    before_meta = fetch_meta(client=client)
    before = {k: before_meta[k] for k in base.META_FIELDS}
    if before != previous["metadata"]:
        raise ValueError("source drift from previous pinned metadata")
    members = select_members(nodes)
    ids = [n["bodyId"] for n in members]
    primary = [n["bodyId"] for n in members if n["somaNeuromere"] == "T1"]
    motors = base.motor_ids(nodes)
    neighbours = sorted({r[1] for r in previous["queries"]["outputs"]["data"]})

    def fetch(q):
        response = client.fetch_custom(q, format="json")
        return {"cypher": q, "columns": response["columns"], "data": response["data"]}

    queries = {
        "presence": fetch(presence_query(sorted(set(ids + [10045, 10056] + motors)))),
        "induced": fetch(base.edge_query(ids, ids)),
        "induced_count": fetch(count_query(ids)),
        "dng_intermediate_inputs": fetch(base.edge_query(neighbours, ids)),
        "primary_outputs": fetch(base.edge_query(primary)),
        "other_motor_outputs": fetch(
            base.edge_query(sorted(set(ids) - set(primary)), motors)
        ),
    }
    outgoing = sorted({r[1] for r in queries["primary_outputs"]["data"]})
    queries["motor_inputs"] = fetch(base.edge_query(outgoing, motors))
    after_meta = fetch_meta(client=client)
    if before != {k: after_meta[k] for k in base.META_FIELDS}:
        raise ValueError("source changed during motif acquisition")
    source = {
        "schema": SOURCE_SCHEMA,
        "dataset": client.dataset,
        "endpoint": base.NEUPRINT_ENDPOINT,
        "metadata": before,
        "neuprint_python_version": base.PINNED_NEUPRINT_PYTHON_VERSION,
        "queries": queries,
    }
    validate_sources(source, previous, nodes)
    if (
        REFERENCE_PATH.exists()
        and canonical_sha256(source)
        != json.loads(REFERENCE_PATH.read_bytes())["source_sha256"]
    ):
        raise ValueError("motif source drift; do not replace existing pin")
    return source, previous, raw


def write_artifact(root, source, previous, raw):
    root = Path(root).resolve()
    if root.is_relative_to(base.REPO):
        raise ValueError("scientific artifacts must remain outside repository")
    value = build_artifact(source, previous, raw)
    payloads = {
        "source.json": canonical_json_bytes(source),
        "prior_source.json": canonical_json_bytes(previous),
        "annotations.feather": raw,
        "contract.json": canonical_json_bytes(value),
    }
    manifest = {
        "schema": SCHEMA,
        "artifact_id": value["artifact_id"],
        "files": {
            n: {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
            for n, b in payloads.items()
        },
    }
    root.mkdir(parents=True, exist_ok=True)
    target = root / value["artifact_id"]
    if target.exists():
        load_artifact(
            target,
            reference={
                "artifact_id": value["artifact_id"],
                "source_sha256": canonical_sha256(source),
            },
        )
        return target
    staging = Path(tempfile.mkdtemp(prefix=".motif-", dir=root))
    try:
        for name, b in payloads.items():
            (staging / name).write_bytes(b)
        (staging / "manifest.json").write_bytes(canonical_json_bytes(manifest))
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return target


def load_artifact(path, *, reference=None):
    path = Path(path)
    pin = json.loads(REFERENCE_PATH.read_bytes()) if reference is None else reference
    names = {
        "source.json",
        "prior_source.json",
        "annotations.feather",
        "contract.json",
        "manifest.json",
    }
    if (
        not path.is_dir()
        or {p.name for p in path.iterdir()} != names
        or any((path / n).is_symlink() for n in names)
    ):
        raise ValueError("missing or unsafe source authority")
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
        raise ValueError("source manifest integrity failure")
    parsed = {
        n: json.loads(data[n])
        for n in ("source.json", "prior_source.json", "contract.json")
    }
    if any(data[n] != canonical_json_bytes(parsed[n]) for n in parsed):
        raise ValueError("noncanonical source serialization")
    if canonical_sha256(parsed["source.json"]) != pin["source_sha256"]:
        raise ValueError("motif source pin mismatch")
    result = validate_artifact(
        parsed["contract.json"],
        parsed["source.json"],
        parsed["prior_source.json"],
        data["annotations.feather"],
    )
    if result["artifact_id"] != pin["artifact_id"]:
        raise ValueError("logical motif identity mismatch")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acquire", type=Path)
    group.add_argument("--replay", type=Path)
    args = parser.parse_args()
    try:
        if args.acquire:
            source, previous, raw = acquire_source()
            path = write_artifact(args.acquire, source, previous, raw)
            value = build_artifact(source, previous, raw)
        else:
            path, value = args.replay, load_artifact(args.replay)
        print(
            json.dumps(
                {
                    "local_path": str(path),
                    "artifact_id": value["artifact_id"],
                    "config_sha256": value["config_sha256"],
                    "result_sha256": value["result_sha256"],
                    "source_sha256": value["config"]["source_sha256"],
                    "decision": value["result"]["decision"],
                    "groups": value["result"]["threshold_sensitivity"]["1"]["groups"],
                },
                indent=2,
            )
        )
    except Exception as exc:
        parser.exit(
            1,
            f"Motif authority failed ({type(exc).__name__}); no source substitution.\n",
        )


if __name__ == "__main__":
    main()
