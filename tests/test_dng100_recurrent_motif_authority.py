"""Independent small structural graphs; fixtures never enter acquisition/replay."""

import copy
import json

import pytest

from neurofly import dng100_recurrent_motif_authority as m
from neurofly import dng100_walking_route_authority as base
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


def node(
    body, neuron_type, side, superclass="vnc_intrinsic", segment="T1", subclass=None
):
    return dict(
        zip(
            base.NODE_FIELDS,
            [
                body,
                neuron_type,
                f"{neuron_type}_{side}",
                side,
                superclass,
                None,
                subclass,
                segment,
                "Traced",
                "Reviewed",
            ],
            strict=True,
        )
    )


@pytest.fixture
def fixture():
    # Explicit engineering IDs; the production builder rejects this fake source pin.
    nodes = [
        node(10045, "DNg100", "L", "descending_neuron"),
        node(10056, "DNg100", "R", "descending_neuron"),
        node(500, "TEST_MN", "L", "vnc_motor", subclass="fl"),
        node(501, "TEST_MN", "R", "vnc_motor", subclass="fl"),
        node(600, "TEST_INTERMEDIATE", "L"),
    ]
    for side, segment, ids in [
        ("L", "T1", [101, 102, 103]),
        ("R", "T1", [201, 202, 203]),
        ("L", "T2", [301, 302, 303]),
    ]:
        nodes += [
            node(i, t, side, segment=segment)
            for i, t in zip(ids, ["IN17A001", "INXXX466", "IN16B036"], strict=True)
        ]
    index = {n["bodyId"]: n for n in nodes}

    def edge(a, b, count):
        n = index[b]
        return [
            a,
            b,
            count,
            json.dumps(
                {f"LegNp({n['somaNeuromere']})({n['somaSide']})": {"post": count}}
            ),
        ]

    induced = [
        edge(a, b, w)
        for a, b, w in [
            (101, 102, 8),
            (101, 103, 2),
            (102, 103, 9),
            (103, 101, 10),
            (103, 102, 3),
            (201, 201, 1),
            (201, 202, 8),
            (202, 203, 9),
            (203, 201, 10),
            (301, 302, 8),
            (302, 303, 9),
            (303, 301, 10),
            (101, 301, 2),
        ]
    ]
    additional = [
        edge(a, b, w)
        for a, b, w in [
            (101, 500, 7),
            (201, 501, 7),
            (600, 500, 3),
            (102, 600, 6),
            (600, 101, 6),
            (600, 102, 5),
            (301, 500, 1),
            (500, 501, 2),
        ]
    ]
    graph = sorted(induced + additional)
    members = set(range(101, 104)) | set(range(201, 204)) | set(range(301, 304))
    primary = set(range(101, 104)) | set(range(201, 204))
    first = sorted([edge(10045, 101, 10), edge(10045, 600, 5), edge(10056, 201, 20)])
    dn = sorted({r[1] for r in first})
    output = [r for r in graph if r[0] in primary]
    neighbours = sorted({r[1] for r in output})

    def query(cypher, rows, columns=base.EDGE_COLUMNS):
        return {"cypher": cypher, "columns": columns, "data": sorted(rows)}

    previous = {
        "schema": base.SOURCE_SCHEMA,
        "dataset": base.MALECNS_DATASET,
        "endpoint": base.NEUPRINT_ENDPOINT,
        "annotation_sha256": base.HISTORICAL_ANNOTATION_SHA256,
        "neuprint_python_version": base.PINNED_NEUPRINT_PYTHON_VERSION,
        "metadata": {
            "dataset": "male-cns",
            "tag": "v1.0",
            "uuid": base.DATASET_UUID,
            "lastDatabaseEdit": "TEST_ONLY",
            "latestMutationId": 1,
            "postHighAccuracyThreshold": 0.5,
            "postHPThreshold": 0.7,
            "preHPThreshold": 0,
            "primaryRois": base.policy()["front_leg_synapse_rois"],
        },
        "queries": {
            "outputs": query(base.edge_query([10045, 10056]), first),
            "motor_inputs": query(
                base.edge_query(dn, [500, 501]),
                [r for r in graph if r[0] in dn and r[1] in (500, 501)],
            ),
        },
    }
    source = {
        "schema": m.SOURCE_SCHEMA,
        "dataset": base.MALECNS_DATASET,
        "endpoint": base.NEUPRINT_ENDPOINT,
        "metadata": copy.deepcopy(previous["metadata"]),
        "neuprint_python_version": base.PINNED_NEUPRINT_PYTHON_VERSION,
        "queries": {
            "presence": query(
                m.presence_query(sorted(members | {10045, 10056, 500, 501})),
                [
                    [index[i][k] for k in m.PRESENCE_FIELDS]
                    for i in sorted(members | {10045, 10056, 500, 501})
                ],
                m.PRESENCE_FIELDS,
            ),
            "induced": query(
                base.edge_query(sorted(members), sorted(members)), induced
            ),
            "induced_count": query(
                m.count_query(sorted(members)), [[len(induced)]], ["edge_count"]
            ),
            "dng_intermediate_inputs": query(
                base.edge_query(dn, sorted(members)),
                [r for r in graph if r[0] in dn and r[1] in members],
            ),
            "primary_outputs": query(base.edge_query(sorted(primary)), output),
            "other_motor_outputs": query(
                base.edge_query(sorted(members - primary), [500, 501]),
                [r for r in graph if r[0] in members - primary and r[1] in (500, 501)],
            ),
            "motor_inputs": query(
                base.edge_query(neighbours, [500, 501]),
                [r for r in graph if r[0] in neighbours and r[1] in (500, 501)],
            ),
        },
    }
    return source, previous, nodes


def test_known_directed_cycles_thresholds_and_context(fixture):
    s, p, n = fixture
    result = m.extract_graph(s, p, n)
    cycles = {tuple(c["nodes"]) for c in result["threshold_sensitivity"]["1"]["cycles"]}
    assert cycles == {
        (101, 103),
        (102, 103),
        (101, 102, 103),
        (201, 202, 203),
        (301, 302, 303),
    }
    assert result["decision"] == "DNG100_RECURRENT_MOTIF_AUTHORITY_VERIFIED"
    assert {
        tuple(c["nodes"]) for c in result["threshold_sensitivity"]["5"]["cycles"]
    } == {(101, 102, 103), (201, 202, 203), (301, 302, 303)}
    assert result["threshold_sensitivity"]["10"]["cycles"] == []
    assert [10045, 600, 102] in [r["nodes"] for r in result["dng_inputs"]]
    assert [102, 600, 500] in [r["nodes"] for r in result["motor_outputs"]]
    assert [301, 500, 501] not in [r["nodes"] for r in result["motor_outputs"]]
    assert result["rhythm"] == "NOT_SIMULATED"
    assert result["physiological_sign"] == "NOT_ASSIGNED"
    assert result["functional_gain"] == result["conduction_delay"] == "NOT_DEFINED"
    assert result["body_actuation"] == "NOT_DEFINED"
    assert all(
        r["physiological_recruitment"] == "NOT_VALIDATED"
        for r in result["motor_outputs"]
    )
    pairs = {(r["pre"], r["post"]): r for r in result["pair_inventory"]}
    assert pairs[201, 201]["status"] == "OBSERVED"  # self is not a two-node cycle
    assert pairs[101, 301]["cross_segment"]
    assert pairs[101, 201]["cross_side"]
    assert pairs[102, 101]["status"] == "VERIFIED_SOURCE_COMPLETE_ABSENT"
    assert pairs[102, 101]["synapse_count"] is None
    assert len(result["dng_direct_inventory"]) == 2 * 9
    assert len(result["motor_direct_inventory"]) == 9 * 2


@pytest.mark.parametrize("other", [201, 301])
def test_cross_side_or_segment_cycle_remains_context(fixture, other):
    s, p, n = fixture
    by_id = {r["bodyId"]: r for r in n}
    for a, b in [(101, other), (other, 101)]:
        target = by_id[b]
        row = [
            a,
            b,
            2,
            json.dumps(
                {f"LegNp({target['somaNeuromere']})({target['somaSide']})": {"post": 2}}
            ),
        ]
        for label in ["induced", "primary_outputs", "dng_intermediate_inputs"]:
            if label == "primary_outputs" and by_id[a]["somaNeuromere"] != "T1":
                continue
            if label == "dng_intermediate_inputs" and a not in [101, 201, 600]:
                continue
            data = s["queries"][label]["data"]
            if not any(r[:2] == [a, b] for r in data):
                data.append(row.copy())
                data.sort()
    s["queries"]["induced_count"]["data"] = [[len(s["queries"]["induced"]["data"])]]
    result = m.extract_graph(s, p, n)
    cycle = next(
        c
        for c in result["threshold_sensitivity"]["1"]["cycles"]
        if c["nodes"] == [101, other]
    )
    assert not cycle["qualifying_three_type_motif"]
    assert "CROSS_SIDE_OR_SEGMENT_CONTEXT_ONLY" in cycle["qualification_reasons"]


def test_cycles_are_independently_known_not_repeated_nodes():
    edges = {(1, 2), (2, 1), (2, 3), (3, 1), (1, 1)}
    assert m.enumerate_cycles([1, 2, 3], edges) == [(1, 2), (1, 2, 3)]
    assert m.enumerate_cycles([1, 2, 3], {(1, 2), (2, 3)}) == []
    assert m.canonical_cycle([3, 1, 2]) == (1, 2, 3)
    assert m.canonical_cycle([3, 2, 1]) == (1, 3, 2)
    for ids in ([1, 1], [1, 2, 1], [1], [1, 2, 3, 4]):
        with pytest.raises(ValueError):
            m.canonical_cycle(ids)


def test_order_and_annotation_uncertainty(fixture):
    s, p, n = fixture
    original = m.extract_graph(s, p, n)
    assert m.extract_graph(s, p, list(reversed(n))) == original
    member = next(x for x in n if x["bodyId"] == 101)
    member["statusLabel"] = None
    result = m.extract_graph(s, p, n)
    assert result["decision"] == "DNG100_RECURRENT_MOTIF_AUTHORITY_PARTIAL"
    record = next(x for x in result["members"] if x["body_id"] == 101)
    assert record["classification"] == "CLASSIFICATION_UNRESOLVED"
    assert "TRACING_NOT_REVIEWED_OR_INCOMPLETE" in record["anatomical_reasons"]


@pytest.mark.parametrize(
    "kind", ["side", "segment", "duplicate", "conflict", "unknown"]
)
def test_identity_anatomy_adversaries(fixture, kind):
    s, p, n = fixture
    member = next(x for x in n if x["bodyId"] == 101)
    if kind == "side":
        member["somaSide"] = "R"
        with pytest.raises(ValueError):
            m.anatomy(member)
    elif kind == "segment":
        member["somaNeuromere"] = "T9"
        assert "SEGMENT_UNRESOLVED" in m.anatomy(member)
    elif kind == "unknown":
        member["type"] = "UNKNOWN"
        assert 101 not in [r["bodyId"] for r in m.select_members(n)]
    else:
        n.append(member.copy())
        if kind == "conflict":
            n[-1]["somaNeuromere"] = "T2"
        with pytest.raises(ValueError):
            m.extract_graph(s, p, n)


@pytest.mark.parametrize(
    "kind",
    [
        "dataset",
        "uuid",
        "confidence",
        "version",
        "presence",
        "count",
        "scope",
        "missing",
    ],
)
def test_source_coverage_and_metadata_fail(fixture, kind):
    s, p, n = fixture
    if kind == "dataset":
        s["dataset"] = "manc:v1.2"
    if kind == "uuid":
        s["metadata"]["uuid"] = "WRONG_UUID"
    if kind == "confidence":
        s["metadata"]["postHighAccuracyThreshold"] = float("nan")
    if kind == "version":
        s["neuprint_python_version"] = "OTHER"
    if kind == "presence":
        s["queries"]["presence"]["data"].pop()
    if kind == "count":
        s["queries"]["induced_count"]["data"][0][0] += 1
    if kind == "scope":
        s["queries"]["induced"]["cypher"] += " LIMIT 5"
    if kind == "missing":
        del s["queries"]["motor_inputs"]
    with pytest.raises(ValueError):
        m.extract_graph(s, p, n)


@pytest.mark.parametrize("count", [0, -1, True, 1.5, float("inf")])
def test_invalid_native_counts_fail(fixture, count):
    s, p, n = fixture
    s["queries"]["induced"]["data"][0][2] = count
    with pytest.raises(ValueError):
        m.extract_graph(s, p, n)


def test_absence_cannot_contradict_other_source_queries(fixture):
    s, p, n = fixture
    s["queries"]["induced"]["data"].pop(0)
    s["queries"]["induced_count"]["data"][0][0] -= 1
    with pytest.raises(ValueError, match="absence contradicts"):
        m.extract_graph(s, p, n)


def test_context_roi_cannot_become_motor_evidence(fixture):
    s, p, n = fixture
    for q in s["queries"].values():
        for row in q["data"]:
            if len(row) == 4 and row[1] in (500, 501):
                row[3] = "{}"
    result = m.extract_graph(s, p, n)
    assert result["decision"] == "DNG100_RECURRENT_MOTIF_AUTHORITY_PARTIAL"
    assert all(
        "FINAL_SEGMENT_ROI_UNRESOLVED" in r["unresolved_reasons"]
        for r in result["motor_outputs"]
    )


def test_motif_roi_is_not_inferred_from_soma_segment(fixture):
    s, p, n = fixture
    for q in s["queries"].values():
        for row in q["data"]:
            if len(row) == 4 and row[:2] == [102, 103]:
                row[3] = "{}"
    result = m.extract_graph(s, p, n)
    cycle = next(
        c
        for c in result["threshold_sensitivity"]["1"]["cycles"]
        if c["nodes"] == [101, 102, 103]
    )
    assert not cycle["qualifying_three_type_motif"]
    assert "CYCLE_SEGMENT_ROI_UNRESOLVED" in cycle["qualification_reasons"]


def test_wrong_direction_and_conflicting_duplicates_fail(fixture):
    s, p, n = fixture
    s["queries"]["dng_intermediate_inputs"]["data"][0][0] = 999999
    with pytest.raises(ValueError):
        m.extract_graph(s, p, n)


def test_overlapping_query_conflict_is_not_silently_normalized(fixture):
    s, p, n = fixture
    # Fixture rows intentionally share source content; isolate just one query.
    s["queries"]["primary_outputs"] = copy.deepcopy(s["queries"]["primary_outputs"])
    row = next(
        r for r in s["queries"]["primary_outputs"]["data"] if r[:2] == [101, 102]
    )
    row[2] += 1
    with pytest.raises(ValueError, match="conflicting duplicate"):
        m.extract_graph(s, p, n)


def test_synthetic_fixture_cannot_enter_production_artifact_builder(fixture):
    s, p, _ = fixture
    with pytest.raises(ValueError, match="prior scoped source pin"):
        m.build_artifact(s, p, b"FAKE_ANNOTATIONS")


def test_zero_induced_graph_is_a_complete_negative(fixture):
    s, p, n = fixture
    members = {x["bodyId"] for x in m.select_members(n)}
    for key in m.EDGE_QUERIES:
        s["queries"][key]["data"] = [
            r
            for r in s["queries"][key]["data"]
            if not (r[0] in members and r[1] in members)
        ]
    s["queries"]["induced_count"]["data"] = [[0]]
    neighbours = sorted({r[1] for r in s["queries"]["primary_outputs"]["data"]})
    s["queries"]["motor_inputs"]["cypher"] = base.edge_query(neighbours, [500, 501])
    s["queries"]["motor_inputs"]["data"] = [
        r for r in s["queries"]["motor_inputs"]["data"] if r[0] in neighbours
    ]
    result = m.extract_graph(s, p, n)
    assert result["decision"] == "DNG100_RECURRENT_MOTIF_NO_SUPPORTED_CYCLE"
    assert result["threshold_sensitivity"]["1"]["cycles"] == []


def test_invalid_policy_and_unavailable_sources(tmp_path, monkeypatch):
    changed = m.policy()
    changed["primary_minimum_synapse_count"] = 5
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(m, "POLICY_PATH", path)
    with pytest.raises(ValueError):
        m.policy()
    with pytest.raises(ValueError):
        m.load_artifact(tmp_path / "missing", reference={})


@pytest.fixture(scope="module")
def real():
    ref = json.loads(m.REFERENCE_PATH.read_bytes())
    path = m.DEFAULT_ROOT / ref["artifact_id"]
    value = m.load_artifact(
        path
    )  # Strict real-source gate; no skip or fixture substitution.
    return (
        value,
        json.loads((path / "source.json").read_bytes()),
        json.loads((path / "prior_source.json").read_bytes()),
        (path / "annotations.feather").read_bytes(),
    )


def test_real_source_ids_and_independent_edge_cycle_inventory(real):
    value, source, _, _ = real
    reference = json.loads(m.REFERENCE_PATH.read_bytes())
    assert reference["members"] == value["result"]["members"]
    assert reference["pair_inventory"] == value["result"]["pair_inventory"]
    assert reference["group_sensitivity"] == {
        k: v["groups"] for k, v in value["result"]["threshold_sensitivity"].items()
    }
    nodes = {x["body_id"]: x["annotation"] for x in value["result"]["members"]}
    assert {i for i, n in nodes.items() if n["somaNeuromere"] == "T1"} == {
        800173,
        800288,
        800863,
        903216,
        801884,
        803183,
    }
    raw = {(a, b): w for a, b, w, _ in source["queries"]["induced"]["data"]}
    observed = {
        (p["pre"], p["post"]): p["synapse_count"]
        for p in value["result"]["pair_inventory"]
        if p["status"] == "OBSERVED"
    }
    assert observed == raw
    assert len(raw) == 36
    assert {
        pair: raw[pair]
        for pair in [
            (800173, 800863),
            (800863, 800173),
            (800173, 801884),
            (801884, 800173),
            (800863, 801884),
            (801884, 800863),
            (800288, 903216),
            (903216, 800288),
            (800288, 803183),
            (803183, 800288),
            (903216, 803183),
            (803183, 903216),
        ]
    } == {
        (800173, 800863): 465,
        (800863, 800173): 11,
        (800173, 801884): 6,
        (801884, 800173): 526,
        (800863, 801884): 38,
        (801884, 800863): 121,
        (800288, 903216): 328,
        (903216, 800288): 5,
        (800288, 803183): 1,
        (803183, 800288): 439,
        (903216, 803183): 27,
        (803183, 903216): 96,
    }
    assert {
        k: len(v["cycles"]) for k, v in value["result"]["threshold_sensitivity"].items()
    } == {"1": 30, "5": 28, "10": 21}
    # Walk raw adjacency to establish closure; do not invoke cycle/extractor helpers.
    actual_cycles = {
        tuple(c["nodes"])
        for c in value["result"]["threshold_sensitivity"]["1"]["cycles"]
    }
    for path in actual_cycles:
        assert len(set(path)) == len(path)
        assert all(
            (a, b) in raw for a, b in zip(path, path[1:] + path[:1], strict=True)
        )
    for a in nodes:
        for b in nodes:
            if a < b and (a, b) in raw and (b, a) in raw:
                assert (a, b) in actual_cycles
            for c in nodes:
                if (
                    a < b
                    and a < c
                    and b != c
                    and all(e in raw for e in [(a, b), (b, c), (c, a)])
                ):
                    assert (a, b, c) in actual_cycles
    assert len(value["result"]["pair_inventory"]) == len(nodes) ** 2


@pytest.mark.parametrize(
    "kind",
    [
        "body",
        "direction",
        "cycles",
        "reachability",
        "rhythm",
        "gain",
        "actuation",
        "policy",
    ],
)
def test_real_rehashed_semantic_tampering_rejected(real, kind):
    value, s, p, raw = real
    wrong = copy.deepcopy(value)
    if kind == "body":
        wrong["result"]["members"][0]["body_id"] = 1
    if kind == "direction":
        wrong["result"]["pair_inventory"][0]["pre"] = 1
    if kind == "cycles":
        wrong["result"]["threshold_sensitivity"]["1"]["cycles"] = []
    if kind == "reachability":
        wrong["result"]["motor_outputs"] = []
    if kind == "rhythm":
        wrong["result"]["rhythm"] = "VALIDATED_CPG"
    if kind == "gain":
        wrong["result"]["functional_gain"] = 1.0
    if kind == "actuation":
        wrong["result"]["body_actuation"] = "WALKING"
    if kind == "policy":
        wrong["config"]["policy"]["primary_minimum_synapse_count"] = 5
    wrong["config_sha256"] = canonical_sha256(wrong["config"])
    wrong["result_sha256"] = canonical_sha256(wrong["result"])
    wrong["artifact_id"] = canonical_sha256(
        [m.SCHEMA, wrong["config_sha256"], wrong["result_sha256"]]
    )
    with pytest.raises(ValueError, match="semantic"):
        m.validate_artifact(wrong, s, p, raw)


def test_real_reproduction_and_manifest_integrity(real, tmp_path):
    value, s, p, raw = real
    assert m.build_artifact(s, p, raw)["artifact_id"] == value["artifact_id"]
    target = m.write_artifact(tmp_path, s, p, raw)
    assert m.load_artifact(target) == value
    (target / "source.json").write_bytes((target / "source.json").read_bytes() + b" ")
    with pytest.raises(ValueError, match="integrity"):
        m.load_artifact(target)
    with pytest.raises(ValueError):
        m.write_artifact(base.REPO / "scratch", s, p, raw)
