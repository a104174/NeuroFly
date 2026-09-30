import copy
import math

import pytest

from neurofly.planar_body_plant import (
    DEFAULT_SOURCE_ARTIFACT,
    FIXTURE_IDS,
    PlantConfig,
    integrate_commands,
    reference_config,
    transform_commands,
    validate_plant,
)
from neurofly.planar_body_plant_artifacts import (
    generate_plant_artifact,
    replay_plant_artifact,
)
from neurofly.ttm_actuator_artifacts import replay_command_artifact
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes


@pytest.fixture(scope="module")
def source():
    return replay_command_artifact(DEFAULT_SOURCE_ARTIFACT)


@pytest.fixture(scope="module")
def result(source):
    return transform_commands(source, reference_config())


def test_all_canonical_samples(source, result):
    body = result["result"]
    assert body["trajectory_count"] == 6
    assert body["sample_count"] == 486
    assert tuple(f["fixture_id"] for f in body["fixtures"]) == FIXTURE_IDS
    assert body["time_ms"] == source["result"]["time_ms"]
    assert body["interval_start_boundary_indices"] == list(range(80))
    for original, output in zip(
        source["result"]["fixtures"], body["fixtures"], strict=True
    ):
        right, left = original["instances"]
        times = body["time_ms"]
        expected = math.fsum(
            (times[n + 1] - times[n])
            * (right["actuator_command"][n] + left["actuator_command"][n])
            / 2
            for n in range(80)
        )
        assert output["z_world_eq"][-1] == pytest.approx(expected)
        assert output["x_world_eq"] == [0.0] * 81
        assert len(output["z_world_eq"]) == 81
        assert len(output["common_mode_drive"]) == 80
        assert output["common_mode_drive"] == output["forward_speed_world_eq_per_ms"]
        assert all(
            a <= b for a, b in zip(output["z_world_eq"], output["z_world_eq"][1:])
        )
        for n in range(80):
            assert (
                output["common_mode_drive"][n]
                == (right["actuator_command"][n] + left["actuator_command"][n]) / 2
            )
        assert [
            a["source_actuator_trajectory_id"] for a in output["source_actuators"]
        ] == [right["trajectory_id"], left["trajectory_id"]]
        assert [a["source_body_id"] for a in output["source_actuators"]] == [
            800146,
            804642,
        ]


def test_fixture_behavior_and_timing(result):
    zero, right, left, bilateral, repeated_right, repeated_left = result["result"][
        "fixtures"
    ]
    assert zero["z_world_eq"] == [0.0] * 81
    assert right["z_world_eq"] == left["z_world_eq"]
    assert repeated_right["z_world_eq"] == repeated_left["z_world_eq"]
    assert bilateral["z_world_eq"] == pytest.approx(
        [2 * z for z in right["z_world_eq"]]
    )
    assert right["z_world_eq"][:11] == [0.0] * 11
    assert right["z_world_eq"][11] == pytest.approx(0.01)
    assert right["summary"]["maximum_forward_speed_world_eq_per_ms"] == 0.1
    assert bilateral["summary"]["maximum_forward_speed_world_eq_per_ms"] == 0.2


def test_interval_final_boundary_and_no_inertia():
    config = reference_config()
    initial = integrate_commands([0, 1, 2], [1, 0, 0], [1, 0, 0], config)
    terminal = integrate_commands([0, 1, 2], [1, 0, 1], [1, 0, 1], config)
    assert initial == terminal
    assert initial["z_world_eq"] == [0, 1, 1]
    assert initial["forward_speed_world_eq_per_ms"] == [1, 0]
    offset = integrate_commands([0, 1], [1, 1], [1, 1], PlantConfig(2, 3, 4))
    assert offset["x_world_eq"] == [3, 3]
    assert offset["z_world_eq"] == [4, 6]


@pytest.mark.parametrize("value", [0, -1, math.nan, math.inf, -math.inf, True])
def test_invalid_gain(value):
    with pytest.raises(ValueError):
        PlantConfig(value)


@pytest.mark.parametrize("field", ["initial_x_world_eq", "initial_z_world_eq"])
def test_invalid_initial_position(field):
    with pytest.raises(ValueError):
        PlantConfig(1, **{field: math.inf})


@pytest.mark.parametrize(
    "times,right,left",
    [
        ([0, 0], [0, 0], [0, 0]),
        ([0, math.nan], [0, 0], [0, 0]),
        ([0, 1], [0], [0, 0]),
        ([0, 1], [0, 1.1], [0, 0]),
        ([0, 1], [0, math.inf], [0, 0]),
        ([0, 1], [-0.1, 0], [0, 0]),
    ],
)
def test_invalid_commands(times, right, left):
    with pytest.raises(ValueError):
        integrate_commands(times, right, left, reference_config())


@pytest.mark.parametrize(
    "field",
    [
        "coordinate_convention",
        "source_result_schema",
        "common_mode_semantics",
        "update_semantics",
    ],
)
def test_semantic_validation(field):
    payload = reference_config().payload()
    payload[field] = "tampered"
    with pytest.raises(ValueError):
        PlantConfig.from_payload(payload)


@pytest.mark.parametrize(
    "mutation",
    [
        "artifact_id",
        "channel",
        "body",
        "side",
        "command",
        "grid",
        "fixture",
        "duplicate",
    ],
)
def test_source_tampering(source, mutation):
    payload = copy.deepcopy(source)
    fixture = payload["result"]["fixtures"][0]
    row = fixture["instances"][0]
    if mutation == "artifact_id":
        payload["artifact_id"] = "changed"
    elif mutation == "grid":
        payload["result"]["time_ms"][1] = 0.2
    elif mutation == "fixture":
        fixture["fixture_id"] = "unknown"
    elif mutation == "duplicate":
        fixture["instances"].append(copy.deepcopy(row))
    else:
        field = {
            "channel": "actuator_id",
            "body": "source_body_id",
            "side": "source_side",
            "command": "actuator_command",
        }[mutation]
        row[field] = [0.5] * 81 if mutation == "command" else "changed"
    with pytest.raises(ValueError):
        transform_commands(payload, reference_config())


@pytest.mark.parametrize(
    "mutation", ["gain", "initial", "semantics", "position", "hash", "source"]
)
def test_result_tampering(result, mutation):
    payload = copy.deepcopy(result)
    if mutation == "gain":
        payload["config"]["model"]["motion_gain_world_eq_per_ms"] = 2
    elif mutation == "initial":
        payload["config"]["model"]["initial_z_world_eq"] = 1
    elif mutation == "semantics":
        payload["config"]["model"]["update_semantics"] = "changed"
    elif mutation == "position":
        payload["result"]["fixtures"][0]["z_world_eq"][1] = 1
    elif mutation == "source":
        payload["config"]["source_phase11b"]["artifact_id"] = "changed"
    else:
        payload["result_sha256"] = "changed"
    with pytest.raises(ValueError):
        validate_plant(payload)


def test_reset_replay_and_immutable_artifact(source, result, tmp_path):
    assert canonical_json_bytes(result) == canonical_json_bytes(
        transform_commands(source, reference_config())
    )
    path = generate_plant_artifact(reference_config(), output_root=tmp_path)
    before = (path / "body.json").read_bytes()
    assert replay_plant_artifact(path) == result
    assert generate_plant_artifact(reference_config(), output_root=tmp_path) == path
    assert (path / "body.json").read_bytes() == before
    (path / "manifest.json").write_bytes(b"{}\n")
    with pytest.raises(ValueError):
        replay_plant_artifact(path)


def test_no_physical_state_fields(result):
    forbidden = {
        "mass",
        "force",
        "torque",
        "gravity",
        "acceleration",
        "meters",
        "Newtons",
        "joint_angle",
        "heading",
        "yaw",
    }

    def visit(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(result)
