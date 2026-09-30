"""Functional routing regressions, not biological actuation validation."""

import copy
import json
import socket

import pytest

from neurofly.muscle_activation_artifacts import replay_activation_artifact
from neurofly.ttm_actuator import (
    ARTIFACT_SCHEMA,
    DEFAULT_SOURCE_ARTIFACT,
    SOURCE_ID,
    build_commands,
    route_activation,
    routing_config,
    validate_commands,
    validate_config,
)
from neurofly.ttm_actuator_artifacts import (
    generate_command_artifact,
    replay_command_artifact,
)
from neurofly.ttm_actuator_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)


@pytest.fixture(scope="module")
def source():
    return replay_activation_artifact(DEFAULT_SOURCE_ARTIFACT)


@pytest.fixture(scope="module")
def result(source):
    return route_activation(source, routing_config())


def rows(payload):
    return {
        (f["fixture_id"], r["source_body_id"]): r
        for f in payload["result"]["fixtures"]
        for r in f["instances"]
    }


def test_exact_passthrough_accounting(source, result):
    assert result["config"]["source_phase10b"]["artifact_id"] == SOURCE_ID
    assert result["result"]["trajectory_count"] == 12
    assert result["result"]["sample_count"] == 972
    for field in ("boundary_indices", "time_ms"):
        assert result["result"][field] == source["result"][field]
    assert len(set(r["trajectory_id"] for r in rows(result).values())) == 12
    for key, row in rows(result).items():
        original = rows(source)[key]
        assert row["actuator_command"] == original["activation_proxy"]
        assert row["source_activation_trajectory_id"] == original["trajectory_id"]
        assert row["source_activation_trajectory_sha256"] == canonical_sha256(original)
        for field in (
            "source_body_id",
            "source_side",
            "proxy_domain_id",
            "proxy_source_mapping_id",
        ):
            assert row[field] == original[field]
        assert row["actuator_side"] == row["source_side"]
        assert row["actuator_id"] == (
            "RIGHT_TTM_ACTUATOR" if key[1] == 800146 else "LEFT_TTM_ACTUATOR"
        )
        assert all(0 <= a <= 1 for a in row["actuator_command"])


def test_fixture_isolation_zero_bilateral_repeated(result):
    r = rows(result)
    for body in (800146, 804642):
        assert r["ZERO_EVENT_CONTROL", body]["actuator_command"] == [0.0] * 81
        assert (
            r["BILATERAL_SIMULTANEOUS_EVENT", body]["summary"]["peak_actuator_command"]
            == 0.2
        )
    for side, body, other in (("RIGHT", 800146, 804642), ("LEFT", 804642, 800146)):
        single = r[f"{side}_SINGLE_EVENT", body]
        assert single["summary"]["peak_actuator_command"] == 0.2
        assert single["summary"]["peak_step"] == 10
        assert single["summary"]["peak_time_ms"] == 1.0
        assert r[f"{side}_SINGLE_EVENT", other]["actuator_command"] == [0.0] * 81
        repeated = r[f"{side}_REPEATED_EVENTS", body]
        assert repeated["summary"]["peak_actuator_command"] == pytest.approx(
            0.22706705664732252
        )
        assert repeated["summary"]["peak_step"] == 30
        assert r[f"{side}_REPEATED_EVENTS", other]["actuator_command"] == [0.0] * 81


def keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from keys(child)


def test_semantic_only_config_and_no_movement(result):
    config = routing_config()
    assert len(config["routing_records"]) == 2
    assert {r["source_body_id"] for r in config["routing_records"]} == {800146, 804642}
    assert len({r["routing_id"] for r in config["routing_records"]}) == 2
    forbidden = {
        "gain",
        "threshold",
        "tau",
        "force_scale",
        "angle_scale",
        "position",
        "velocity",
        "acceleration",
        "angle",
        "force",
        "torque",
        "impulse",
        "jump",
        "contraction",
        "strain",
    }
    assert not forbidden.intersection(keys(result))
    assert result["config"]["provenance_kind"] == "EXPLORATORY_TTM_ACTUATOR_COMMAND"


def test_pinned_deterministic_identity(result):
    assert result["config_sha256"] == (
        "94da685537241558bf1cc64ae9a8c051fce5a651f02bab871f192d518406b974"
    )
    assert result["result_sha256"] == (
        "78f277a4714f983d35212cd4314ec3a257664356426e1caf7cc3ce9214bf8c9f"
    )
    assert result["artifact_id"] == (
        "478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40"
    )


@pytest.mark.parametrize(
    "field", ["magnitude_semantics", "temporal_semantics", "units"]
)
def test_semantic_mutation_rejected(field):
    config = routing_config()
    config[field] = "changed"
    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize(
    "field,value",
    [
        ("actuator_id", "LEFT_TTM_ACTUATOR"),
        ("actuator_side", "L"),
        ("source_body_id", 804642),
        ("source_neural_side", "L"),
        ("action_kind", "OTHER"),
        ("classification", "ANATOMICAL_ATTACHMENT_MAPPING"),
    ],
)
def test_routing_mutations_rejected(field, value):
    config = routing_config()
    config["routing_records"][0][field] = value
    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize("change", ["missing", "third", "swap", "gain", "delay"])
def test_config_shape_rejected(change):
    config = routing_config()
    if change == "missing":
        config["routing_records"].pop()
    elif change == "third":
        config["routing_records"].append(copy.deepcopy(config["routing_records"][0]))
    elif change == "swap":
        config["routing_records"].reverse()
    else:
        config[change] = 1
    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize(
    "change",
    [
        "identity",
        "sample",
        "nan",
        "outside",
        "body",
        "side",
        "proxy",
        "duplicate",
        "fixture",
        "step",
        "time",
        "schema",
    ],
)
def test_source_tamper_rejected(source, change):
    mutated = copy.deepcopy(source)
    row = mutated["result"]["fixtures"][0]["instances"][0]
    if change == "identity":
        mutated["artifact_id"] = "bad"
    elif change in ("sample", "nan", "outside"):
        row["activation_proxy"][0] = {"sample": 0.2, "nan": float("nan"), "outside": 2}[
            change
        ]
    elif change == "body":
        row["source_body_id"] = 123
    elif change == "side":
        row["source_side"] = "L"
    elif change == "proxy":
        row["proxy_domain_id"] = ""
    elif change == "duplicate":
        mutated["result"]["fixtures"][0]["instances"].append(copy.deepcopy(row))
    elif change == "fixture":
        mutated["result"]["fixtures"][0]["fixture_id"] = "other"
    elif change == "step":
        mutated["result"]["boundary_indices"][0] = 1
    elif change == "time":
        mutated["result"]["time_ms"][0] = 1
    else:
        mutated["schema_version"] = "other"
    with pytest.raises(ValueError):
        route_activation(mutated, routing_config())


@pytest.mark.parametrize(
    "change",
    [
        "source",
        "command",
        "body",
        "side",
        "actuator",
        "actuator_side",
        "action",
        "routing_swap",
        "step",
        "time",
        "hash",
    ],
)
def test_rehashed_output_tamper_rejected(result, change, monkeypatch):
    mutated = copy.deepcopy(result)
    row = mutated["result"]["fixtures"][0]["instances"][0]
    fields = {
        "command": ("actuator_command", [1] * 81),
        "body": ("source_body_id", 1),
        "side": ("source_side", "L"),
        "actuator": ("actuator_id", "LEFT_TTM_ACTUATOR"),
        "actuator_side": ("actuator_side", "L"),
        "action": ("action_kind", "other"),
    }
    if change in fields:
        key, value = fields[change]
        row[key] = value
    elif change == "source":
        mutated["config"]["source_phase10b"]["artifact_id"] = "bad"
    elif change == "routing_swap":
        mutated["config"]["adapter"]["routing_records"].reverse()
    elif change in ("step", "time"):
        mutated["result"]["boundary_indices" if change == "step" else "time_ms"][0] = 9
    else:
        mutated["artifact_id"] = "bad"
    if change != "hash":
        mutated["config_sha256"] = canonical_sha256(mutated["config"])
        mutated["result_sha256"] = canonical_sha256(mutated["result"])
        mutated["artifact_id"] = canonical_sha256(
            [ARTIFACT_SCHEMA, mutated["config_sha256"], mutated["result_sha256"]]
        )
    monkeypatch.setattr("neurofly.ttm_actuator.build_commands", lambda **kw: result)
    with pytest.raises(ValueError):
        validate_commands(mutated)


def test_offline_artifact_cli_byte_replay(tmp_path, monkeypatch, capsys, result):
    def no_network(*args, **kwargs):
        raise AssertionError("offline replay attempted network")

    monkeypatch.setattr(socket, "create_connection", no_network)
    assert build_commands() == result
    path = generate_command_artifact(output_root=tmp_path)
    before = (path / "commands.json").read_bytes()
    assert replay_command_artifact(path) == result
    assert generate_command_artifact(output_root=tmp_path) == path
    assert (path / "commands.json").read_bytes() == before
    assert before == canonical_json_bytes(result, newline=True)
    for command in ("inspect", "replay"):
        assert main([command, str(path)]) == 0
        output = json.loads(capsys.readouterr().out)
        assert output["artifact_id"] == result["artifact_id"]
        assert "NO JOINT MOTION" in output["operation"]
    # Test-local generated artifact: ordinary file corruption must fail closed.
    (path / "commands.json").write_bytes(
        before.replace(b'"sample_count":972', b'"sample_count":973')
    )
    with pytest.raises(ValueError):
        replay_command_artifact(path)
    assert main(["replay", str(path)]) == 2
