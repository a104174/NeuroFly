"""Independent geometric controls for the engineering-only arena plant."""

import copy
import math

import pytest

from neurofly.experimental_locomotion import (
    OUTPUT,
    build,
    configuration,
    simulate,
    validate_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


def test_visible_displacement_and_zero_propulsion():
    a, b = build()["result"]["runs"]
    assert a["distance"] > 3 * 0.30  # Asset's rendered long-axis extent.
    assert all(f["position"] == b["frames"][0]["position"] for f in b["frames"])
    assert b["distance"] == 0 and not b["contact_events"]
    assert a["frames"][-1]["linear_velocity"] == [0.0, 0.0, 0.0]
    assert len(a["contact_events"]) == 1


@pytest.mark.parametrize("heading", [0, math.pi / 2, -math.pi / 2, math.pi / 4])
def test_analytic_heading_integration(heading):
    c = configuration()
    c.update(initial_heading_rad=heading, duration_s=0.1)
    run = simulate(c, "CONTROL", 0.18)
    final = run["frames"][-1]
    assert final["position"][0] == pytest.approx(0.018 * math.sin(heading))
    assert final["position"][2] == pytest.approx(
        c["initial_position"][2] + 0.018 * math.cos(heading)
    )
    assert final["orientation"] == heading
    assert final["time"] == 0.1


@pytest.mark.parametrize("heading", [0, math.pi / 2, -math.pi / 2, math.pi])
def test_contact_is_bounded_latched_and_has_no_automatic_turn(heading):
    c = configuration()
    c["initial_heading_rad"] = heading
    r = simulate(c, "CONTROL", 0.18)
    lx = (2.4 - 0.012) / 2 - c["footprint_radius"]
    lz = (1.22 - 0.012) / 2 - c["footprint_radius"]
    assert len(r["contact_events"]) == 1
    for f in r["frames"]:
        assert abs(f["position"][0]) <= lx
        assert abs(f["position"][2]) <= lz
        assert f["orientation"] == heading and f["angular_velocity"] == 0
        if f["contact"]:
            assert f["linear_velocity"] == [0.0, 0.0, 0.0]
    contact_step = r["contact_events"][0]["step"]
    assert all(
        f["position"] == r["frames"][contact_step]["position"]
        for f in r["frames"][contact_step:]
    )


def test_grazing_boundary_does_not_trigger_outward_contact():
    c = configuration()
    c["initial_position"][0] = (2.4 - 0.012) / 2 - c["footprint_radius"]
    c.update(initial_heading_rad=0.0, duration_s=0.1)
    assert not simulate(c, "CONTROL", 0.18)["contact_events"]
    c["initial_heading_rad"] = math.pi / 2
    r = simulate(c, "CONTROL", 0.18)
    assert r["contact_events"][0]["step"] == 0
    assert r["distance"] == 0


@pytest.mark.parametrize(
    "key,value",
    [
        ("dt_s", 0),
        ("dt_s", -0.01),
        ("dt_s", float("nan")),
        ("speed", float("inf")),
        ("speed", 100),
        ("speed", -1),
        ("duration_s", 0.031),
        ("initial_position", [10, 0.1, 0]),
        ("initial_position", [0, -1, 0]),
        ("initial_heading_rad", float("nan")),
        ("footprint_radius", -1),
        ("chamber", {"width": 0, "depth": 1, "height": 1, "wall": 0.01}),
        ("random_policy", "RANDOM_WALK"),
    ],
)
def test_invalid_configuration_is_rejected(key, value):
    c = configuration()
    c[key] = value
    with pytest.raises(ValueError):
        simulate(c, "CONTROL", c["speed"])


def test_reproducibility_source_immutability_and_time_order():
    c = configuration()
    before = copy.deepcopy(c)
    a = simulate(c, "CONTROL", c["speed"])
    assert c == before and a == simulate(c, "CONTROL", c["speed"])
    assert len(a["frames"]) == 401
    for n, f in enumerate(a["frames"]):
        assert f["step"] == n and f["time"] == n * 0.02
        assert f["neural_summary"] is None
        assert f["sensory_summary"] is None
        assert f["steering_model_value"] is None
    assert a["frames"][-1]["time"] == 8


def test_real_published_asset_semantic_replay():
    import json

    assert validate_artifact(json.loads(OUTPUT.read_bytes())) == build()


@pytest.mark.parametrize("kind", ["time", "position", "schema", "neural", "contact"])
def test_recomputed_hashes_do_not_authorize_false_semantics(kind):
    a = build()
    f = a["result"]["runs"][0]["frames"][1]
    if kind == "time":
        f["time"] = 0
    elif kind == "position":
        f["position"][0] = 0.8
    elif kind == "schema":
        a["config"]["model_mode"] = "CONNECTOME_DRIVEN"
    elif kind == "neural":
        f["neural_summary"] = {"spikes": 5}
    else:
        f["contact"] = "NEURAL_WALL_AVOIDANCE"
    a["config_sha256"] = canonical_sha256(a["config"])
    a["result_sha256"] = canonical_sha256(a["result"])
    a["artifact_id"] = canonical_sha256(
        {"config_sha256": a["config_sha256"], "result_sha256": a["result_sha256"]}
    )
    with pytest.raises(ValueError, match="deterministic"):
        validate_artifact(a)
