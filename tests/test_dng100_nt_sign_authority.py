"""Independent expectations; synthetic rows never enter production replay."""

import copy
import hashlib
import json

import pytest

from neurofly import dng100_nt_sign_authority as nt
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

EXPECTED_IDS = [10045, 10056, 800173, 800288, 800863, 801884, 803183, 903216]
# Independently transcribed from the published structural authority.
EXPECTED_EDGES = {
    (10045, 800288): 100,
    (10056, 800173): 155,
    (10056, 800863): 1,
    (800173, 800863): 465,
    (800173, 801884): 6,
    (800288, 803183): 1,
    (800288, 903216): 328,
    (800863, 800173): 11,
    (800863, 801884): 38,
    (801884, 800173): 526,
    (801884, 800863): 121,
    (803183, 800288): 439,
    (803183, 903216): 96,
    (903216, 800288): 5,
    (903216, 803183): 27,
}


@pytest.fixture
def row():
    # Explicit test-only row, not a replacement for the official source.
    return {
        "body": 800173,
        "cell_type": "IN17A001",
        "total_nt_predictions": 100,
        "predicted_nt_confidence": 0.75,
        "predicted_nt": "acetylcholine",
        "ground_truth": None,
        "celltype_total_nt_predictions": 200,
        "celltype_predicted_nt": "acetylcholine",
        "celltype_predicted_nt_confidence": 0.8,
        "consensus_nt": "acetylcholine",
    }


@pytest.fixture(scope="module")
def official():
    # Mandatory real-source gate: not skipped or replaced by synthetic data.
    return nt.load_inputs(nt.NT_SOURCE, nt.MOTIF_SOURCE, nt.SDK_SOURCE)


@pytest.fixture(scope="module")
def completed(official):
    return nt.build_artifact(*official)


def test_official_source_eight_bodies_fifteen_edges(official, completed):
    raw, annotation, structural, sdk = official
    assert hashlib.sha256(raw).hexdigest() == (
        "95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621"
    )
    assert hashlib.sha256(annotation).hexdigest() == (
        "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2"
    )
    assert sdk["metadata"]["uuid"] == "4b2087c0fbe046bfaf0d60bc970e3e5d"
    assert structural["artifact_id"] == (
        "baae20599455c2a7acb3271e6eeb6b73326d17185b6e705022b74818ff0f8934"
    )
    result = completed["result"]
    assert [n["body_id"] for n in result["neurons"]] == EXPECTED_IDS
    assert {
        (e["structural"]["pre"], e["structural"]["post"]): e["structural"][
            "synapse_count"
        ]
        for e in result["edges"]
    } == EXPECTED_EDGES
    assert all(e["functional_sign"] == "UNKNOWN" for e in result["edges"])
    assert result["unknown_sign_count"] == 15
    assert result["decision"] == "DNG100_NT_SOURCE_VERIFIED_SIGNS_UNKNOWN"
    assert all(n["raw_annotation_receptorType"] is None for n in result["neurons"])
    assert [n["body_id"] for n in result["neurons"] if n["raw"]["ground_truth"]] == [
        800173,
        800288,
        801884,
        803183,
    ]
    # Real independent representative expectation, not two calls to one helper.
    assert result["neurons"][0]["raw"]["predicted_nt_confidence"] == pytest.approx(
        0.9529439618305637, abs=1e-12
    )
    for n in result["neurons"]:
        assert all(not e["direct_experiment_on_selected_body"] for e in n["evidence"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("body", 800173.0),
        ("body", True),
        ("body", 800003),
        ("cell_type", "IN16B036"),
        ("cell_type", None),
        ("predicted_nt_confidence", -0.1),
        ("predicted_nt_confidence", 1.1),
        ("predicted_nt_confidence", float("nan")),
        ("celltype_predicted_nt_confidence", float("inf")),
        ("predicted_nt_confidence", True),
        ("total_nt_predictions", -1),
        ("total_nt_predictions", 2.5),
        ("consensus_nt", ""),
    ],
)
def test_invalid_raw_values(row, field, value):
    row[field] = value
    with pytest.raises(ValueError):
        nt.validate_raw(row)


@pytest.mark.parametrize(
    "field", ["predicted_nt", "consensus_nt", "ground_truth", "celltype_predicted_nt"]
)
def test_nulls_preserved(row, field):
    row[field] = None
    classified = nt.classify(row)
    assert (
        next(e for e in classified["evidence"] if e["field"] == field)["value"] is None
    )
    assert row[field] is None


def test_low_confidence_is_not_invented_ground_truth(row):
    row["predicted_nt_confidence"] = 0.05
    evidence = nt.classify(row)["evidence"]
    e = next(e for e in evidence if e["field"] == "predicted_nt")
    assert e["confidence"] == 0.05
    assert e["category"] == "MALECNS_NEURON_PREDICTION"
    assert not e["direct_experiment_on_selected_body"]
    assert nt.assess_sign()["functional_sign"] == "UNKNOWN"


@pytest.mark.parametrize("field", ["consensus_nt", "ground_truth"])
def test_conflicting_prediction_or_ground_truth_not_repaired(row, field):
    row[field] = "glutamate"
    before = copy.deepcopy(row)
    value = nt.classify(row)
    assert value["conflict"]
    assert value["primary_evidence"] == "UNKNOWN"
    assert row == before
    assert (
        next(e for e in value["evidence"] if e["field"] == field)["value"]
        == "glutamate"
    )


@pytest.mark.parametrize("label", ["unclear", "UNRECOGNIZED_TEST_LABEL", None])
def test_unknowns_do_not_acquire_transmitter_or_sign(row, label):
    for field in ["predicted_nt", "celltype_predicted_nt", "consensus_nt"]:
        row[field] = label
    value = nt.classify(row)
    assert value["primary_evidence"] == "UNKNOWN"
    assert value["primary_field"] is None
    assert nt.assess_sign()["functional_sign"] == "UNKNOWN"


def test_ground_truth_is_type_resolution_not_selected_body_experiment(row):
    row["ground_truth"] = "acetylcholine"
    e = nt.classify(row)["evidence"][0]
    assert e["category"] == "EXPERIMENTAL_GROUND_TRUTH"
    assert "CELLTYPE" in e["resolution"]
    assert not e["direct_experiment_on_selected_body"]
    assert e["confidence"] is None


@pytest.mark.parametrize("conflict", [False, True])
def test_multiple_records_or_fragments_rejected(row, conflict):
    second = dict(row)
    if conflict:
        second["predicted_nt"] = "gaba"
    with pytest.raises(ValueError, match="multiple rows"):
        nt.select_records([(0, row), (1, second)])


def test_missing_record_not_replaced_with_fixture(row):
    with pytest.raises(ValueError, match="missing primary"):
        nt.select_records([(0, row)])


@pytest.mark.parametrize(
    "claim",
    [
        {"receptor": "GluClalpha", "resolution": "EXTERNAL_CELLTYPE"},
        {"functional_sign": "INHIBITORY_SUPPORTED", "reason": "glutamate"},
        {"body_id": 800173, "receptor": "nicotinic", "source": "invented"},
        {"model_label": "I1"},
        {"raw_receptorType": "putative_ppk25"},
        {"resolution": "CONFLICTING"},
    ],
)
def test_external_or_invented_receptor_claim_not_promoted(claim):
    with pytest.raises(ValueError, match="unsupported receptor"):
        nt.assess_sign(receptor_claims=[claim])


@pytest.mark.parametrize(
    "field,value",
    [
        ("somaSide", "R"),
        ("somaNeuromere", "T2"),
        ("type", "INXXX466"),
        ("statusLabel", "Prelim Roughly traced"),
    ],
)
def test_conflicting_anatomy(official, field, value):
    nodes = nt.motif.base.annotation_nodes(official[1])
    next(n for n in nodes if n["bodyId"] == 800173)[field] = value
    with pytest.raises(ValueError):
        nt.validate_anatomy(nodes)


@pytest.mark.parametrize(
    "mode",
    [
        "reverse",
        "missing",
        "duplicate",
        "no_provenance",
        "invalid_count",
        "wrong_dataset",
    ],
)
def test_graph_scope_and_provenance(official, mode):
    graph = copy.deepcopy(nt.select_edges(official[2]["result"]["edges"]))
    if mode == "reverse":
        graph[0]["pre"], graph[0]["post"] = graph[0]["post"], graph[0]["pre"]
    elif mode == "missing":
        graph.pop()
    elif mode == "duplicate":
        graph.append(copy.deepcopy(graph[0]))
    elif mode == "no_provenance":
        graph[0]["source_references"] = []
    elif mode == "invalid_count":
        graph[0]["synapse_count"] = 0
    else:
        graph[0]["dataset"] = "manc:v1.0"
    with pytest.raises(ValueError):
        nt.select_edges(graph)


@pytest.mark.parametrize("mode", ["uuid", "nt_file", "structural_count"])
def test_source_tamper_cannot_repin(official, mode):
    inputs = list(official)
    if mode == "uuid":
        inputs[3] = copy.deepcopy(inputs[3])
        inputs[3]["metadata"]["uuid"] = "different"
    elif mode == "nt_file":
        inputs[0] = inputs[0][:-1] + b"x"
    else:
        inputs[2] = copy.deepcopy(inputs[2])
        inputs[2]["result"]["edges"][0]["synapse_count"] += 1
    with pytest.raises(ValueError):
        nt.build_artifact(*inputs)


@pytest.mark.parametrize(
    "mode", ["prediction", "receptor", "sign", "body", "count", "experiment", "policy"]
)
def test_recomputed_hashes_do_not_replace_semantics(official, completed, mode):
    value = copy.deepcopy(completed)
    if mode == "prediction":
        value["result"]["neurons"][0]["raw"]["predicted_nt"] = "gaba"
    elif mode == "receptor":
        value["result"]["edges"][0]["receptor_evidence_references"] = ["invented"]
    elif mode == "sign":
        value["result"]["edges"][0]["functional_sign"] = "EXCITATORY_SUPPORTED"
    elif mode == "body":
        value["result"]["neurons"][0]["body_id"] = 10056
    elif mode == "count":
        value["result"]["edges"][0]["structural"]["synapse_count"] = 99
    elif mode == "experiment":
        value["result"]["experiment_id"] = "EXPLORATORY_COURSE_CONTROL"
    else:
        value["config"]["policy"]["body_actuation"] = "APPLIED"
    ch, rh = canonical_sha256(value["config"]), canonical_sha256(value["result"])
    value.update(
        config_sha256=ch,
        result_sha256=rh,
        artifact_id=canonical_sha256([nt.SCHEMA, ch, rh]),
    )
    with pytest.raises(ValueError, match="semantic"):
        nt.validate_artifact(value, *official)


def test_deterministic_semantic_reproduction(official, completed):
    assert nt.validate_artifact(completed, *official) == completed
    assert nt.load_artifact(nt.DEFAULT_ROOT / completed["artifact_id"]) == completed
    assert json.loads(nt.REFERENCE_PATH.read_bytes()) == completed
    assert (
        completed["artifact_id"]
        != hashlib.sha256(canonical_json_bytes(completed)).hexdigest()
    )


def test_missing_source_explicit(tmp_path):
    with pytest.raises(FileNotFoundError):
        nt.load_inputs(tmp_path / "absent.feather", nt.MOTIF_SOURCE, nt.SDK_SOURCE)


def test_no_write_under_repository(completed, official):
    with pytest.raises(ValueError, match="outside Git"):
        nt.write_artifact(nt.motif.base.REPO / "data/forbidden", completed, official[3])
