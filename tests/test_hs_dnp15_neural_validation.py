"""Frozen exploratory proxy invariants, not physiological response targets."""

import copy
import json
from pathlib import Path

import pytest

from neurofly import hs_dnp15_neural_validation as model
from neurofly.hs_dnp15_neural_validation_artifacts import (
    _manifest,
    generate_neural_artifact,
    replay_neural_artifact,
)
from neurofly.hs_dnp15_neural_validation_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

ARTIFACT_ID = "2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113"


@pytest.fixture(scope="module")
def response():
    return model.build_neural_validation()


def _runs(response):
    return {r["condition_id"]: r for r in response["result"]["runs"]}


def test_frozen_authorities_config_and_no_output_targeting(response):
    contract = model.load_preregistration()
    authority = model.load_structural_authority()
    assert canonical_sha256(contract) == model.PREREGISTRATION_ID
    assert response["config"]["preregistration"] == contract
    assert response["artifact_id"] == ARTIFACT_ID
    assert canonical_sha256(response["result"]) == response["result_sha256"]
    assert canonical_sha256(response["config"]) == response["config_sha256"]
    assert len(contract["source_identities"]) == 6
    assert len(contract["target_identities"]) == 2
    assert len(contract["selected_routes"]) == 6
    assert len(contract["omitted_induced_edges"]) == 7
    assert (
        contract["omitted_induced_edges"]
        == authority["full_induced_edges_not_selected"]
    )
    assert contract["frozen_before_neural_execution"] is True
    assert contract["randomness"] == "NONE; NO_SEED_REQUIRED"
    assert contract["target_model"]["events"] == "NOT_DEFINED"
    assert contract["target_model"]["threshold"] == "NOT_DEFINED"
    assert contract["transfer"]["structural_count_is_efficacy"] is False
    text = canonical_json_bytes(contract).decode()
    for field in (
        "target_spikes",
        "target_movement",
        "desired_displacement",
        "target_threshold_crossing",
    ):
        assert field not in text
    assert not {"body", "actuator", "motor", "yaw_command"} & response["result"].keys()


def test_all_identity_trajectories_and_declared_timing(response):
    result = response["result"]
    contract = response["config"]["preregistration"]
    assert len(result["time_ms"]) == 501
    assert result["time_ms"][-1] == contract["duration_ms"] == 50
    assert [s["body_id"] for s in result["source_order"]] == [
        10015,
        10016,
        10023,
        10034,
        10181,
        10419,
    ]
    assert result["route_order"] == contract["selected_routes"]
    for run in result["runs"]:
        assert run["execution_completed"] is True
        assert (
            run["target_events"] is None
        )  # absent semantics, not zero measured spikes
        for n in range(501):
            assert (
                len(run["source_states"][n]) == len(run["route_contributions"][n]) == 6
            )
            assert len(run["target_states"][n]) == len(run["target_drives"][n]) == 2
            if n < 500:
                for j in range(2):
                    assert run["target_states"][n + 1][j] == model.proxy_step(
                        run["target_states"][n][j],
                        run["target_drives"][n][j],
                        contract["dt_ms"],
                        contract["target_model"]["tau_ms"],
                    )
        assert run["input_descriptors"][200] == {"R": 0.0, "L": 0.0}
    right = _runs(response)["RIGHT_SIDE_MOTION"]
    assert right["target_states"][0] == right["target_states"][1] == [0, 0]
    assert right["source_states"][1][0] != 0
    assert right["target_states"][2][0] != 0  # two-boundary causal response


def test_neutral_matched_swapped_and_reversed_controls(response):
    runs = _runs(response)
    neutral = response["config"]["preregistration"]["source_model"]["initial_state"]
    for row in runs["NO_MOTION_CONTROL"]["source_states"]:
        assert row == [neutral] * 6
    for row in runs["NO_MOTION_CONTROL"]["target_states"]:
        assert (
            row
            == [response["config"]["preregistration"]["target_model"]["initial_state"]]
            * 2
        )
    for row in runs["BILATERAL_MATCHED_MOTION"]["target_states"]:
        assert row[0] == row[1]
    assert (
        runs["SIDE_SWAPPED_EQUIVALENT"]["target_states"]
        == runs["LEFT_SIDE_MOTION"]["target_states"]
    )
    for right, left, reverse in zip(
        runs["RIGHT_SIDE_MOTION"]["target_states"],
        runs["SIDE_SWAPPED_EQUIVALENT"]["target_states"],
        runs["DIRECTION_REVERSED"]["target_states"],
        strict=True,
    ):
        assert left == right[::-1]
        assert reverse == [-v for v in right]
    for p, m in zip(
        runs["RIGHT_SIDE_MOTION"]["source_states"],
        runs["DIRECTION_REVERSED"]["source_states"],
        strict=True,
    ):
        assert m == [-v for v in p]


def test_route_provenance_and_no_cross_side(response):
    result = response["result"]
    sources = result["source_order"]
    sides = {s["body_id"]: s["side"] for s in sources + result["target_order"]}
    indices = {s["body_id"]: i for i, s in enumerate(sources)}
    for route in result["route_order"]:
        assert sides[route["source_id"]] == sides[route["target_id"]]
    for run in result["runs"]:
        for state, contributions in zip(
            run["source_states"], run["route_contributions"], strict=True
        ):
            for route, value in zip(result["route_order"], contributions, strict=True):
                assert (route["source_id"], route["target_id"]) in model.ROUTE_KEYS
                assert value == state[indices[route["source_id"]]] / 3


def test_count_mutation_and_query_order_do_not_change_execution():
    contract = model.load_preregistration()
    states = {
        s["body_id"]: (i + 1) / 10 for i, s in enumerate(contract["source_identities"])
    }
    expected = model.route_contributions(
        states, contract["selected_routes"], contract["target_identities"], 1
    )
    mutated = copy.deepcopy(contract["selected_routes"])
    for route in mutated:
        route["structural_count"] *= 1001
    assert (
        model.route_contributions(
            states, mutated[::-1], contract["target_identities"][::-1], 1
        )
        == expected
    )
    # Test-local count mutation changes provenance, not any numerical trajectory.
    altered = copy.deepcopy(contract)
    altered["selected_routes"] = mutated[::-1]
    result = model._execute(altered)
    reference = model._execute(contract)
    assert result["runs"] == reference["runs"]
    with pytest.raises(ValueError):
        model.route_contributions(
            states,
            mutated + contract["omitted_induced_edges"],
            contract["target_identities"],
            1,
        )
    swapped = copy.deepcopy(mutated)
    swapped[0]["target_id"] = 12069
    with pytest.raises(ValueError):
        model.route_contributions(states, swapped, contract["target_identities"], 1)


@pytest.mark.parametrize(
    "location",
    [
        "source_identity",
        "target_identity",
        "route",
        "authority",
        "parameter",
        "condition",
        "source_state",
        "target_state",
        "hash",
        "omitted_edge",
    ],
)
def test_semantic_tampering_rejected_even_with_rehashed_manifest(response, location):
    bad = copy.deepcopy(response)
    c = bad["config"]["preregistration"]
    if location == "source_identity":
        c["source_identities"][0]["body_id"] += 1
    elif location == "target_identity":
        c["target_identities"][0]["body_id"] += 1
    elif location == "route":
        c["selected_routes"][0]["target_id"] = 12069
    elif location == "authority":
        bad["config"]["structural_authority_id"] = "0" * 64
    elif location == "parameter":
        c["source_model"]["tau_ms"] += 1
    elif location == "condition":
        c["conditions"][0]["right"] = 1
    elif location == "source_state":
        bad["result"]["runs"][0]["source_states"][2][0] = 1
    elif location == "target_state":
        bad["result"]["runs"][0]["target_states"][2][0] = 1
    elif location == "hash":
        bad["result_sha256"] = "0" * 64
    else:
        c["selected_routes"].append(c["omitted_induced_edges"][0])
    if location != "hash":
        bad["config_sha256"] = canonical_sha256(bad["config"])
        bad["result_sha256"] = canonical_sha256(bad["result"])
    with pytest.raises(ValueError, match="frozen offline replay"):
        model.validate_neural_validation(bad)


def test_preregistration_and_authority_mutation_are_fail_closed(tmp_path, monkeypatch):
    contract = model.load_preregistration()
    contract["duration_ms"] += 1
    path = tmp_path / "changed.json"
    path.write_bytes(canonical_json_bytes(contract))
    with pytest.raises(ValueError, match="preregistration"):
        model.load_preregistration(path)
    for name in (
        "neurofly_v1_scientific_status.json",
        "second_circuit_selection_gate.json",
    ):
        (tmp_path / name).write_bytes((model.SCIENCE_ROOT / name).read_bytes())
    doc = json.loads((tmp_path / "second_circuit_selection_gate.json").read_bytes())
    doc["selection"]["selected_contract"]["structural_edges"][0][
        "structural_count"
    ] += 1
    (tmp_path / "second_circuit_selection_gate.json").write_bytes(
        canonical_json_bytes(doc)
    )
    monkeypatch.setattr(model, "SCIENCE_ROOT", tmp_path)
    with pytest.raises(ValueError, match="structural authority"):
        model.load_structural_authority()


def test_artifact_bytes_replay_tamper_and_cli(tmp_path, capsys, response):
    path = generate_neural_artifact(output_root=tmp_path)
    assert replay_neural_artifact(path) == response
    assert generate_neural_artifact(output_root=tmp_path) == path
    assert main(["inspect", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["artifact_id"] == ARTIFACT_ID
    bad = copy.deepcopy(response)
    bad["result"]["runs"][0]["target_states"][3][0] = 1
    (path / "validation.json").write_bytes(canonical_json_bytes(bad, newline=True))
    (path / "manifest.json").write_bytes(
        canonical_json_bytes(_manifest(bad), newline=True)
    )
    with pytest.raises(ValueError):
        replay_neural_artifact(path)
    assert main(["replay", str(path)]) == 2
    assert "validation error" in capsys.readouterr().err


@pytest.mark.parametrize(
    "args",
    [
        (0, 1, 0, 5),
        (0, 1, 0.1, 0),
        (float("nan"), 1, 0.1, 5),
        (0, float("inf"), 0.1, 5),
        (False, 1, 0.1, 5),
    ],
)
def test_step_rejects_invalid_coordinates(args):
    with pytest.raises(ValueError):
        model.proxy_step(*args)


def test_no_motor_frontend_or_body_dependency():
    root = Path(__file__).resolve().parents[1]
    source = (root / "src/neurofly/hs_dnp15_neural_validation.py").read_text()
    for module in (
        "closed_loop_scenario",
        "planar_body_plant",
        "muscle_activation",
        "ttm_actuator",
        "simulation",
    ):
        assert f"from neurofly.{module}" not in source
    for folder in ("web",):
        for path in (root / folder).rglob("*.ts"):
            if "node_modules" not in path.parts and ".next" not in path.parts:
                assert "hs_dnp15_neural_validation" not in path.read_text()
