"""Independent boundary assertions against published Python v1 evidence."""

import json
from functools import lru_cache

import pytest

from neurofly import experimental_neural_locomotion as v1
from neurofly.interactive_neural_locomotion_reference import run_reference
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


@lru_cache
def reference():
    return run_reference()


def test_switched_reference_preserves_source_and_initial_conditions():
    result = reference()
    old = json.loads(v1.OUTPUT.read_bytes())
    assert result["source_artifact_id"] == old["artifact_id"]
    assert result["frames"][0]["position"] == old["config"]["body"]["initial_position"]
    assert result["frames"][0]["neural_summary"]["hs_states"] == [0.0] * 6
    assert len(result["frames"]) == 401
    assert result["neural_substeps"] == 80000
    assert sum(f["neural_summary"]["substeps"] for f in result["frames"]) == 80000


def test_intervention_has_exact_timing_and_continuous_neural_state():
    result = reference()
    baseline = json.loads(v1.OUTPUT.read_bytes())["result"]["runs"][1]["frames"]
    assert result["events"] == [
        {"step": 100, "time": 2.0, "old_plane": 0.4, "new_plane": -0.4}
    ]
    for n in range(100):
        for key in baseline[n]:
            assert result["frames"][n][key] == baseline[n][key]
    f = result["frames"][100]
    assert f["position"] == baseline[100]["position"]
    assert (
        f["neural_summary"]["hs_states"] == baseline[100]["neural_summary"]["hs_states"]
    )
    assert (
        f["neural_summary"]["dnp15_states"]
        == baseline[100]["neural_summary"]["dnp15_states"]
    )
    assert f["sensory_summary"]["right"] != baseline[100]["sensory_summary"]["right"]
    assert (
        f["neural_summary"]["mean_yaw_drive_eq"]
        != baseline[100]["neural_summary"]["mean_yaw_drive_eq"]
    )
    assert result["frames"][200]["orientation"] != baseline[200]["orientation"]


def test_compact_browser_fixture_is_recoverable_real_python_output():
    path = v1.body.ROOT / "web/tests/fixtures/interactive-neural-reference-v2.json"
    envelope = json.loads(path.read_bytes())
    assert canonical_sha256(envelope["reference"]) == envelope["reference_sha256"]
    for f in envelope["reference"]["frames"]:
        assert f == reference()["frames"][f["step"]]


@pytest.mark.parametrize(
    "events",
    [
        ((100, 0.4),),
        ((100, -0.4), (99, 0.4)),
        ((400, -0.4),),
        ((100, 0),),
        ((100.0, -0.4),),
    ],
)
def test_invalid_event_sequences_are_rejected(events):
    with pytest.raises(ValueError):
        run_reference(events)
