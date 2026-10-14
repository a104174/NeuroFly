"""Independent scalar expectations and real pinned recorded input; no dynamics."""

import copy
import dataclasses
import hashlib
import json
import math

import pytest

from neurofly import dng100_t1_motor_input_shadow as s


@pytest.fixture(scope="module")
def genuine():
    return s.load_inputs()


@pytest.fixture
def artifact(genuine, monkeypatch):
    p, samples, structure = genuine
    monkeypatch.setattr(s, "load_inputs", lambda: genuine)
    return s.package(s.configuration(p, samples, structure), s.run(p, samples))


def test_real_pinned_source_and_motor_edge(genuine):
    p, samples, evidence = genuine
    assert p["dataset_uuid"] == "4b2087c0fbe046bfaf0d60bc970e3e5d"
    assert p["edge"] == {"pre": 903216, "post": 804257, "synapse_count": 23}
    assert evidence["source"]["annotation"]["type"] == "INXXX466"
    target = evidence["target"]
    assert (target["type"], target["somaSide"], target["somaNeuromere"]) == (
        "Ti extensor MN",
        "R",
        "T1",
    )
    assert (target["status"], target["statusLabel"]) == ("Traced", "Reviewed")
    assert len(samples) == 2001 and samples[0] == s.SourceSample(0, 0.0, 0.0)
    assert samples[-1].time_s == 2.0
    for edge in evidence["edges"]:
        assert edge["synapse_count"] == 23
        assert edge["roi_counts"]["LegNp(T1)(R)"]["post"] == 23
    assert p["source_trace"] == "3.125e-05"
    assert p["source_model"]["b"] == 0.06


@pytest.mark.parametrize(
    "sign, expected",
    [(1, (0.0, 3.0, 6.0)), (-1, (0.0, -3.0, -6.0)), (0, (0.0, 0.0, 0.0))],
)
def test_literal_linear_transfer(sign, expected):
    # Explicit independently specified numbers, not an expected-value helper.
    samples = (
        s.SourceSample(0, 0.0, 0.0),
        s.SourceSample(1, 0.1, 1.5),
        s.SourceSample(2, 0.2, 3.0),
    )
    assert s.transfer(samples, sign, 2.0) == expected


@pytest.mark.parametrize("sign", [2, -2, 1.0, True, None])
def test_invalid_sign(sign):
    with pytest.raises(ValueError):
        s.transfer((s.SourceSample(0, 0.0, 1.0),), sign, 1.0)


@pytest.mark.parametrize("gain", [0, -1, math.nan, math.inf, True, None])
def test_invalid_gain(gain):
    with pytest.raises(ValueError):
        s.transfer((s.SourceSample(0, 0.0, 1.0),), 1, gain)


def test_overflow_not_clipped_or_substituted():
    with pytest.raises(ValueError, match="nonfinite"):
        s.transfer((s.SourceSample(0, 0.0, 1e308),), 1, 1e308)


@pytest.mark.parametrize(
    "samples",
    [
        (),
        [s.SourceSample(0, 0.0, 1)],
        (s.SourceSample(1, 0.0, 1),),
        (s.SourceSample(0, 0.1, 1),),
        (s.SourceSample(0, 0.0, math.nan),),
        (s.SourceSample(0, 0.0, -1),),
        (s.SourceSample(0, 0.0, 1), s.SourceSample(1, 0.0, 2)),
        (s.SourceSample(0, 0.0, 1), s.SourceSample(1, math.inf, 2)),
    ],
)
def test_missing_nonfinite_unordered_source(samples):
    with pytest.raises(ValueError):
        s.transfer(samples, 0, 1.0)  # Route-off must still reject corrupt inputs.


@pytest.mark.parametrize(
    "change", ["direction", "count", "dataset", "source", "target"]
)
def test_contradictory_structural_policy_rejected(genuine, change):
    p = copy.deepcopy(genuine[0])
    if change == "direction":
        p["edge"]["pre"], p["edge"]["post"] = p["edge"]["post"], p["edge"]["pre"]
    elif change == "count":
        p["edge"]["synapse_count"] = 24
    elif change == "dataset":
        p["dataset_uuid"] = "different-connectome"
    else:
        p[f"{change}_annotation"]["bodyId"] = 1
    with pytest.raises(ValueError, match="unregistered"):
        s.structural_evidence(p)


@pytest.fixture(scope="module")
def recorded(genuine):
    p = genuine[0]
    return json.loads(
        (
            s.convergence.DEFAULT_ROOT / p["source_artifact_id"] / "convergence.json"
        ).read_bytes()
    )["result"]["traces"][p["source_trace"]]


@pytest.mark.parametrize(
    "change", ["missing", "duplicate", "time", "nan", "other_state", "order"]
)
def test_recorded_boundary_validation(recorded, genuine, change):
    t = copy.deepcopy(recorded)
    ids = genuine[0]["state_order"].copy()
    if change == "missing":
        t["states"].pop()
    elif change == "duplicate":
        t["times_s"][10] = t["times_s"][9]
    elif change == "time":
        t["times_s"][10] += 0.0001
    elif change in ("nan", "other_state"):
        t["states"][10][4 if change == "nan" else 0] = math.nan
    else:
        ids.reverse()
    with pytest.raises(ValueError):
        s.recorded_samples(t, ids)


def test_source_file_raw_integrity(genuine, monkeypatch, tmp_path):
    p = genuine[0]
    monkeypatch.setattr(s, "structural_evidence", lambda policy: genuine[2])
    original, selected = s.convergence.source(s.convergence.policy())
    monkeypatch.setattr(s.convergence, "source", lambda policy: (original, selected))
    monkeypatch.setattr(s.convergence, "DEFAULT_ROOT", tmp_path)
    with pytest.raises(ValueError, match="missing"):
        s.load_inputs()
    folder = tmp_path / p["source_artifact_id"]
    folder.mkdir()
    (folder / "convergence.json").write_text("{}\n")
    (folder / "manifest.json").write_text("{}\n")
    with pytest.raises(ValueError, match="checksum"):
        s.load_inputs()


def test_real_source_no_dynamics_execution(genuine, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("neural dynamics must never execute in shadow transfer")

    monkeypatch.setattr(s.convergence.model, "simulate", forbidden)
    monkeypatch.setattr(s.convergence, "solve_piecewise", forbidden)
    monkeypatch.setattr(s.convergence.v0, "run", forbidden)
    p, samples, structure = s.load_inputs()
    assert (p, samples, structure) == genuine
    before = copy.deepcopy(samples)
    r = s.run(p, samples)
    assert samples == before
    with pytest.raises(dataclasses.FrozenInstanceError):
        samples[1].source_state = 99
    a, b, off, sham = [c["telemetry"] for c in r["conditions"]]
    for i, sample in enumerate(samples):
        assert a[i]["shadow_input"] == sample.source_state  # Gain is1, NOT23.
        assert b[i]["shadow_input"] == -sample.source_state
        assert off[i]["shadow_input"] == 0.0
        assert sham[i]["shadow_input"] == a[i]["shadow_input"]
        for rows in (a, b, off, sham):
            assert (rows[i]["time_s"], rows[i]["source_state"]) == (
                sample.time_s,
                sample.source_state,
            )
            assert set(rows[i]) == {
                "step",
                "time_s",
                "source_state",
                "condition",
                "source_body_id",
                "target_body_id",
                "shadow_input",
            }
    assert r["summary"]["semantics"]["motor_neuron_membrane_dynamics"] == "NOT_MODELLED"
    assert all(r["summary"]["checks"].values())


@pytest.mark.parametrize(
    "change",
    ["value", "time", "count", "gain", "sign", "body", "application", "unknown"],
)
def test_rehashed_contradictions_rejected(artifact, change):
    a = copy.deepcopy(artifact)
    if change in ("value", "time", "body"):
        sample = a["result"]["conditions"][0]["telemetry"][10]
        key = {"value": "shadow_input", "time": "time_s", "body": "target_body_id"}[
            change
        ]
        sample[key] += 1
    elif change == "count":
        a["config"]["preregistration"]["edge"]["synapse_count"] = 24
    elif change == "gain":
        a["config"]["preregistration"]["transfer"]["gain"] = 23
    elif change == "sign":
        a["config"]["preregistration"]["conditions"][1]["sign_assumption"] = 1
    elif change == "application":
        a["config"]["preregistration"]["semantics"]["application"] = "APPLIED"
    else:
        a["config"]["preregistration"]["semantics"]["existing_15_signs"] = "VERIFIED"
    with pytest.raises(ValueError, match="contradictory"):
        s.validate(s.package(a["config"], a["result"]))


def test_deterministic_artifact_replay(artifact, genuine, tmp_path):
    path = s.generate(tmp_path)
    assert s.replay(path) == artifact
    assert s.package(s.configuration(*genuine), s.run(*genuine[:2])) == artifact
    with pytest.raises(ValueError, match="overwrite"):
        s.generate(tmp_path)
    raw = (path / "shadow.json").read_bytes()
    manifest = json.loads((path / "manifest.json").read_bytes())
    assert manifest["files"]["shadow.json"]["sha256"] == hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="outside Git"):
        s.generate(s.REPO)
    (path / "shadow.json").write_bytes(raw + b" ")
    with pytest.raises(ValueError, match="integrity"):
        s.replay(path)


def test_policy_rehash_not_accepted(genuine, monkeypatch, tmp_path):
    p = copy.deepcopy(genuine[0])
    p["transfer"]["gain"] = 2
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(p))
    monkeypatch.setattr(s, "POLICY_PATH", path)
    with pytest.raises(ValueError, match="preregistration"):
        s.policy()
