"""Small synthetic parser graphs; real-source authority is mandatory separately."""

import copy
import json

import pytest

from neurofly import dng100_walking_route_authority as model
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_sha256,
)


def node(body, neuron_type, side, superclass, subclass=None, neuromere="T1"):
    return dict(
        zip(
            model.NODE_FIELDS,
            [
                body,
                neuron_type,
                f"{neuron_type}_{side}",
                side,
                superclass,
                None,
                subclass,
                neuromere,
                "Traced",
                "Reviewed",
            ],
            strict=True,
        )
    )


@pytest.fixture
def fixture():
    # Engineering fixture IDs/classes; never passed to the production builder.
    nodes = [
        node(10045, "DNg100", "L", "descending_neuron"),
        node(10056, "DNg100", "R", "descending_neuron"),
        node(500, "TEST_IN", "L", "vnc_intrinsic"),
        node(501, "TEST_IN", "R", "vnc_intrinsic"),
        node(600, "TEST_MN", "L", "vnc_motor", "fl"),
        node(601, "TEST_MN", "R", "vnc_motor", "fl"),
    ]

    def edge(a, b, weight, side="L"):
        return [
            a,
            b,
            weight,
            json.dumps({f"LegNp(T1)({side})": {"pre": 1, "post": weight}}),
        ]

    rows = [edge(10045, 500, 10), edge(10045, 600, 1), edge(10056, 501, 2, "R")]
    source = {
        "schema": model.SOURCE_SCHEMA,
        "dataset": "male-cns:v1.0",
        "endpoint": model.NEUPRINT_ENDPOINT,
        "annotation_sha256": model.HISTORICAL_ANNOTATION_SHA256,
        "neuprint_python_version": "0.6.3",
        "metadata": {
            "dataset": "male-cns",
            "uuid": model.DATASET_UUID,
            "tag": "v1.0",
            "lastDatabaseEdit": "TEST_ONLY",
            "latestMutationId": 1,
            "postHighAccuracyThreshold": 0.5,
            "preHPThreshold": 0,
            "postHPThreshold": 0.7,
            "primaryRois": model.policy()["front_leg_synapse_rois"],
        },
        "queries": {
            "outputs": {
                "cypher": model.edge_query([10045, 10056]),
                "columns": model.EDGE_COLUMNS,
                "data": rows,
            },
            "motor_inputs": {
                "cypher": model.edge_query([500, 501, 600], [600, 601]),
                "columns": model.EDGE_COLUMNS,
                "data": [edge(500, 600, 6), edge(501, 601, 3, "R")],
            },
        },
    }
    return source, nodes


def test_independent_expected_paths_and_asymmetry(fixture):
    source, nodes = fixture
    result = model.extract_routes(source, nodes)
    assert [r["nodes"] for r in result["routes"]] == [
        [10045, 500, 600],
        [10045, 600],
        [10056, 501, 601],
    ]
    assert result["threshold_sensitivity"]["1"] == {
        "10045": {"direct": 1, "indirect": 1, "unresolved": 0},
        "10056": {"direct": 0, "indirect": 1, "unresolved": 0},
    }
    assert result["threshold_sensitivity"]["5"]["10045"]["indirect"] == 1
    assert result["threshold_sensitivity"]["5"]["10056"]["indirect"] == 0
    assert result["decision"] == "DNG100_ROUTE_AUTHORITY_VERIFIED"
    assert result["body_actuation"] == "NOT_DEFINED"
    assert result["neurotransmitter_sign"] == "NOT_INFERRED"
    for r in result["routes"]:
        assert r["length_edges"] == len(r["nodes"]) - 1
        assert r["physiological_function"] == "NOT_VALIDATED"
    edge = result["edges"][0]
    ref = edge["source_references"][0]
    assert ref["query"] == "motor_inputs" and ref["row"] == 0
    assert ref["row_sha256"] == canonical_sha256(
        source["queries"]["motor_inputs"]["data"][0]
    )


@pytest.mark.parametrize(
    "kind", ["wrong_side", "wrong_type", "duplicate", "invalid_id", "field"]
)
def test_identity_conflicts_fail(fixture, kind):
    source, nodes = fixture
    if kind == "wrong_side":
        nodes[0]["somaSide"] = "R"
    if kind == "wrong_type":
        nodes[0]["type"] = "DNp15"
    if kind == "duplicate":
        nodes.append(nodes[0].copy())
    if kind == "invalid_id":
        nodes[0]["bodyId"] = True
    if kind == "field":
        nodes[0]["superclass"] = 17
    with pytest.raises(ValueError):
        model.extract_routes(source, nodes)


@pytest.mark.parametrize(
    "kind",
    ["dataset", "version", "release", "uuid", "confidence", "roi", "query", "missing"],
)
def test_contradictory_source_metadata_fails(fixture, kind):
    source, nodes = fixture
    if kind == "dataset":
        source["dataset"] = "male-cns:v0.9"
    if kind == "version":
        source["neuprint_python_version"] = "unverified"
    if kind == "release":
        source["metadata"]["tag"] = "v0.9"
    if kind == "uuid":
        source["metadata"]["uuid"] = "OTHER_DATASET"
    if kind == "confidence":
        source["metadata"]["postHighAccuracyThreshold"] = float("nan")
    if kind == "roi":
        source["metadata"]["primaryRois"] = []
    if kind == "query":
        source["queries"]["outputs"]["cypher"] = "REVERSED_QUERY"
    if kind == "missing":
        source["queries"].pop("motor_inputs")
    with pytest.raises(ValueError):
        model.extract_routes(source, nodes)


@pytest.mark.parametrize("weight", [0, -1, 1.5, True, float("inf")])
def test_invalid_counts_fail(fixture, weight):
    source, nodes = fixture
    source["queries"]["outputs"]["data"][0][2] = weight
    with pytest.raises(ValueError):
        model.extract_routes(source, nodes)


@pytest.mark.parametrize(
    "kind", ["direction", "columns", "duplicate", "roi", "ordering"]
)
def test_malformed_directed_graph_fails(fixture, kind):
    source, nodes = fixture
    q = source["queries"]["outputs"]
    if kind == "direction":
        q["data"][0][0:2] = [500, 10045]
    if kind == "columns":
        q["columns"] = ["post", "pre", "weight", "roiInfo"]
    if kind == "duplicate":
        q["data"].append(q["data"][0])
    if kind == "roi":
        q["data"][0][3] = '{"LegNp(T1)(L)":{"post":-1}}'
    if kind == "ordering":
        q["data"].reverse()
    with pytest.raises(ValueError):
        model.extract_routes(source, nodes)


@pytest.mark.parametrize(
    "kind", ["unknown_type", "unknown_side", "nonpremotor", "no_roi"]
)
def test_unresolved_candidates_are_not_promoted(fixture, kind):
    source, nodes = fixture
    if kind == "unknown_type":
        nodes[2]["type"] = None
    if kind == "unknown_side":
        nodes[2]["somaSide"] = None
    if kind == "nonpremotor":
        nodes[2]["superclass"] = "UNKNOWN"
    if kind == "no_roi":
        source["queries"]["motor_inputs"]["data"][0][3] = "{}"
    r = model.extract_routes(source, nodes)
    assert r["routes"][0]["classification"] == "CLASSIFICATION_UNRESOLVED"
    assert r["threshold_sensitivity"]["1"]["10045"]["unresolved"] == 1
    assert r["decision"] == "DNG100_ROUTE_AUTHORITY_PARTIAL"


def test_undocumented_motor_identity_is_rejected_by_query_scope(fixture):
    source, nodes = fixture
    nodes[4]["subclass"] = "UNKNOWN"
    with pytest.raises(ValueError, match="target query"):
        model.extract_routes(source, nodes)


def test_empty_paths_and_deterministic_enumeration(fixture):
    source, nodes = fixture
    original = model.extract_routes(source, nodes)
    assert model.extract_routes(source, list(reversed(nodes))) == original
    source["queries"]["outputs"]["data"] = []
    source["queries"]["motor_inputs"]["data"] = []
    source["queries"]["motor_inputs"]["cypher"] = model.edge_query([], [600, 601])
    result = model.extract_routes(source, nodes)
    assert result["routes"] == []
    assert [n["body_id"] for n in result["neurons"]] == [10045, 10056]
    assert result["decision"] == "DNG100_ROUTE_AUTHORITY_NO_SUPPORTED_PATH"


def test_repeated_nodes_are_excluded_not_traversed(fixture):
    source, nodes = fixture
    source["queries"]["outputs"]["data"] = [[10045, 10045, 1, "{}"]]
    source["queries"]["motor_inputs"] = {
        "cypher": model.edge_query([10045], [600, 601]),
        "columns": model.EDGE_COLUMNS,
        "data": [[10045, 600, 1, "{}"]],
    }
    r = model.extract_routes(source, nodes)
    assert r["routes"] == []
    assert r["excluded"][0]["reason"] == "REPEATED_NODE_CYCLE"


def test_invalid_policy_and_missing_artifact_fail(tmp_path, monkeypatch):
    changed = model.policy()
    changed["primary_minimum_synapse_count"] = 0
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(model, "POLICY_PATH", path)
    with pytest.raises(ValueError, match="policy"):
        model.policy()
    with pytest.raises(ValueError):
        model.annotation_nodes(b"FAKE_FEATHER")
    with pytest.raises(ValueError):
        model.load_artifact(tmp_path / "missing", reference={})


@pytest.fixture(scope="module")
def real_artifact():
    # Strict real-source integrity gate: missing authority is a failure, not skip.
    reference = json.loads(model.REFERENCE_PATH.read_bytes())
    path = model.DEFAULT_ROOT / reference["artifact_id"]
    result = model.load_artifact(path)
    source = json.loads((path / "source.json").read_bytes())
    raw = (path / "annotations.feather").read_bytes()
    return result, source, raw


def test_real_official_source_identity_and_complete_replay(real_artifact):
    result, source, raw = real_artifact
    assert result["config"]["annotation_sha256"] == model.HISTORICAL_ANNOTATION_SHA256
    assert source["dataset"] == "male-cns:v1.0"
    origins = {
        n["body_id"]: n["annotation"]
        for n in result["result"]["neurons"]
        if n["body_id"] in (10045, 10056)
    }
    assert origins[10045]["type"] == origins[10056]["type"] == "DNg100"
    assert origins[10045]["somaSide"] == "L" and origins[10056]["somaSide"] == "R"
    assert model.validate_artifact(result, source, raw) == result


def test_real_paths_independently_enumerated_from_source_rows(real_artifact):
    """Enumerate raw pairs without using the extractor or its edge parser."""
    artifact, source, _ = real_artifact
    result = artifact["result"]
    motors = {n["bodyId"] for n in result["front_motor_authority"]}
    first = source["queries"]["outputs"]["data"]
    second = source["queries"]["motor_inputs"]["data"]
    expected = {(a, b) for a, b, _, _ in first if b in motors and a != b}
    expected.update(
        (a, b, d)
        for a, b, _, _ in first
        for c, d, _, _ in second
        if b == c and len({a, b, d}) == 3
    )
    assert len(expected) == 9342
    assert expected == {tuple(r["nodes"]) for r in result["routes"]}
    assert len(result["edges"]) == 11880
    assert result["threshold_sensitivity"]["1"] == {
        "10045": {"direct": 22, "indirect": 2470, "unresolved": 1265},
        "10056": {"direct": 32, "indirect": 3927, "unresolved": 1626},
    }


@pytest.mark.parametrize(
    "kind", ["direction", "classification", "application", "policy"]
)
def test_rehashed_semantic_tampering_fails(real_artifact, kind):
    artifact, source, raw = real_artifact
    changed = copy.deepcopy(artifact)
    if kind == "direction":
        changed["result"]["edges"][0]["pre"] = 10001
    if kind == "classification":
        changed["result"]["classification"] = "BIOLOGICAL_WALKING"
    if kind == "application":
        changed["result"]["body_actuation"] = "FORWARD_SPEED"
    if kind == "policy":
        changed["config"]["policy"]["primary_minimum_synapse_count"] = 10
    changed["config_sha256"] = canonical_sha256(changed["config"])
    changed["result_sha256"] = canonical_sha256(changed["result"])
    changed["artifact_id"] = canonical_sha256(
        [model.SCHEMA, changed["config_sha256"], changed["result_sha256"]]
    )
    with pytest.raises(ValueError, match="semantic replay"):
        model.validate_artifact(changed, source, raw)


def test_manifest_pin_rejects_modified_connectivity(real_artifact, tmp_path):
    artifact, source, raw = real_artifact
    target = model.write_artifact(tmp_path, source, raw)
    data = (target / "source.json").read_bytes()
    (target / "source.json").write_bytes(data + b" ")
    with pytest.raises(ValueError, match="integrity"):
        model.load_artifact(target)
    with pytest.raises(ValueError, match="outside"):
        model.write_artifact(model.REPO / "scratch", source, raw)
