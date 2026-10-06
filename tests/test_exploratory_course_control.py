"""Frozen contracts compose; no physiological steering or output-targeted tuning."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest

from neurofly import exploratory_course_control as model
from neurofly import orientation_to_horizontal_motion as observation
from neurofly.exploratory_course_control_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    _load,
    _manifest,
    generate_closed_loop_artifact,
    replay_closed_loop_artifact,
)
from neurofly.exploratory_course_control_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

ARTIFACT_ID = "f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581"


@pytest.fixture(scope="module")
def artifact():
    return replay_closed_loop_artifact(DEFAULT_ARTIFACT_ROOT / ARTIFACT_ID)


@pytest.fixture(scope="module")
def preregistration():
    return model.load_preregistration()


@pytest.fixture(scope="module")
def components(preregistration):
    return model.load_components(preregistration)


def runs_by_id(artifact):
    return {r["condition"]["id"]: r for r in artifact["result"]["runs"]}


def test_preregistration_frozen_authorities_and_analysis(preregistration, artifact):
    assert canonical_sha256(preregistration) == model.PREREGISTRATION_ID
    assert canonical_sha256(preregistration["analysis"]) == model.ANALYSIS_ID
    assert preregistration["frozen_before_closed_loop_execution"]
    assert not preregistration["output_based_parameter_selection"]
    assert preregistration["analysis"]["stage_b_permitted"]
    assert preregistration["analysis"]["decision"] == (
        "CLOSED_LOOP_COMPOSITION_MARGINAL_BUT_BOUNDED_FOR_FINITE_HORIZON_TEST"
    )
    assert artifact["config"]["preregistration"] == preregistration
    assert artifact["artifact_id"] == ARTIFACT_ID
    assert len(preregistration["authority_records"]) == 8
    assert len(preregistration["conditions"]) == 4


def test_analytical_motion_stability_and_full_orientation_unit_mode(
    preregistration, components
):
    record = preregistration["analysis"]
    model.verify_analysis(preregistration, components)
    roots = np.linalg.eigvals(np.array(record["differential_matrix"]))
    assert max(abs(roots)) == pytest.approx(0.985517664092702, abs=1e-12)
    assert all(abs(root) < 1 for root in roots)
    a, b = record["source_decay"], record["target_decay"]
    matrix = np.zeros((12, 12))
    n = components.neural_contract
    for i, source in enumerate(n["source_identities"]):
        matrix[i, i] = a
        matrix[i, 10 if source["side"] == "R" else 11] = 1 - a
    for j, target in enumerate(n["target_identities"]):
        matrix[6 + j, 6 + j] = b
        for i, source in enumerate(n["source_identities"]):
            if source["side"] == target["side"]:
                matrix[6 + j, i] = (1 - b) / 3
    matrix[8, 8] = 1
    matrix[8, 6], matrix[8, 7] = 0.002, -0.002
    matrix[9, 8] = 1
    matrix[10, 6], matrix[10, 7] = -1, 1
    matrix[11, 6], matrix[11, 7] = 1, -1
    full = np.linalg.eigvals(matrix)
    assert max(abs(full)) == pytest.approx(1)
    assert sum(abs(root - 1) < 1e-12 for root in full) == 1
    assert np.linalg.matrix_rank(matrix - np.eye(12)) == 11
    assert record["clipping_role"].startswith("Frozen observation-domain bound only")


def test_complete_identity_route_and_no_unmodelled_outputs(artifact, components):
    result = artifact["result"]
    assert result["source_order"] == components.neural_contract["source_identities"]
    assert result["target_order"] == components.neural_contract["target_identities"]
    assert result["active_routes"] == components.neural_contract["selected_routes"]
    assert len(result["active_routes"]) == 6
    assert result["translation"] == "NOT_MODELLED"
    assert result["chemical_recurrence"] == result["electrical_coupling"] == "NONE"
    assert result["event_semantics"] == "NOT_DEFINED"
    for run in result["runs"]:
        assert run["termination"]["status"] == "COMPLETED_VALID_HORIZON"
        assert len(run["boundaries"]) == 501
        for boundary in run["boundaries"]:
            assert (
                len(boundary["hs_states"]) == len(boundary["route_contributions"]) == 6
            )
            assert len(boundary["dnp15_states"]) == len(boundary["target_drives"]) == 2
            assert (
                not {"x", "z", "force", "torque", "motor", "yaw_rate", "spikes"}
                & boundary.keys()
            )


def test_all_boundaries_follow_actual_component_apis(artifact, components):
    n = components.neural_contract
    for run in artifact["result"]["runs"]:
        rows = run["boundaries"]
        assert rows[0]["observation"] is None
        assert rows[0]["previous_orientation_eq"] is None
        assert (
            rows[0]["latched_motion"]["right"] == rows[0]["latched_motion"]["left"] == 0
        )
        for index, row in enumerate(rows):
            assert row["boundary_index"] == index
            assert row["time_ms"] == index * n["dt_ms"]
            assert (
                row["dnp15_differential"]
                == row["dnp15_states"][0] - row["dnp15_states"][1]
            )
            assert row["yaw_drive_eq"] == row["dnp15_differential"]
            if index:
                expected = observation.observe_interval(
                    observation.ObservationInterval(
                        observation.WorldReference("WORLD_FIXED_HEADING_ZERO", 0),
                        observation.OrientationBoundary(
                            index - 1,
                            rows[index - 1]["time_ms"],
                            rows[index - 1]["yaw_orientation_eq"],
                        ),
                        observation.OrientationBoundary(
                            index, row["time_ms"], row["yaw_orientation_eq"]
                        ),
                    ),
                    contract=components.observation_contract,
                )
                assert row["observation"] == expected.payload()
                assert expected.available_boundary_index == index
                assert row["latched_motion"]["right"] == expected.sides.right
                assert row["latched_motion"]["left"] == expected.sides.left
            if index == len(rows) - 1:
                assert row["applied_neural_orientation_increment_eq"] is None
                assert row["external_orientation_increment_eq"] is None
                continue
            following = rows[index + 1]
            step = model.compose_neural_interval(
                row["hs_states"],
                row["dnp15_states"],
                observation.SideDescriptors(
                    row["latched_motion"]["right"], row["latched_motion"]["left"]
                ),
                following["time_ms"] - row["time_ms"],
                components,
            )
            assert following["hs_states"] == step["next_sources"]
            assert following["dnp15_states"] == step["next_targets"]
            assert following["yaw_orientation_eq"] == (
                row["yaw_orientation_eq"]
                + row["applied_neural_orientation_increment_eq"]
                + row["external_orientation_increment_eq"]
            )


def test_old_state_latency_no_same_boundary_algebraic_loop(artifact):
    rows = runs_by_id(artifact)["CLOSED_LOOP_PERTURBATION"]["boundaries"]
    assert rows[1]["yaw_orientation_eq"] == 0.001
    assert rows[1]["hs_states"] == [0] * 6
    assert rows[1]["dnp15_states"] == [0, 0]
    assert rows[1]["latched_motion"]["right"] == -0.5
    assert rows[2]["dnp15_states"] == [0, 0]
    assert rows[3]["yaw_orientation_eq"] == 0.001
    assert rows[3]["observation"]["global_horizontal_motion_eq"] == 0
    # Perturbation is exogenous once, not a permanent bias.
    assert rows[0]["external_orientation_increment_eq"] == 0.001
    assert all(r["external_orientation_increment_eq"] == 0 for r in rows[1:-1])


def test_neutral_control_exact_and_open_loop_disconnect(artifact):
    runs = runs_by_id(artifact)
    for row in runs["NO_PERTURBATION_CONTROL"]["boundaries"]:
        assert row["yaw_orientation_eq"] == 0
        assert row["hs_states"] == [0] * 6
        assert row["dnp15_states"] == [0, 0]
        assert row["latched_motion"]["right"] == row["latched_motion"]["left"] == 0
    rows = runs["OPEN_LOOP_PERTURBATION"]["boundaries"]
    assert all(row["yaw_orientation_eq"] == 0.001 for row in rows[1:])
    assert all(row["applied_neural_orientation_increment_eq"] == 0 for row in rows[:-1])
    assert all(row["latched_motion"]["right"] == 0 for row in rows[2:])


def test_identical_perturbation_and_sign_reversed_model_symmetry(artifact):
    runs = runs_by_id(artifact)
    opened = runs["OPEN_LOOP_PERTURBATION"]["boundaries"]
    closed = runs["CLOSED_LOOP_PERTURBATION"]["boundaries"]
    reversed_rows = runs["SIGN_REVERSED_PERTURBATION"]["boundaries"]
    assert (
        opened[0]["external_orientation_increment_eq"]
        == closed[0]["external_orientation_increment_eq"]
    )
    for forward, reverse in zip(closed, reversed_rows, strict=True):
        for name in ("yaw_orientation_eq", "dnp15_differential", "yaw_drive_eq"):
            assert reverse[name] == -forward[name]
        assert reverse["hs_states"] == [-v for v in forward["hs_states"]]
        assert reverse["dnp15_states"] == [-v for v in forward["dnp15_states"]]
        assert reverse["latched_motion"]["right"] == -forward["latched_motion"]["right"]
        assert reverse["latched_motion"]["left"] == -forward["latched_motion"]["left"]


def test_contact_count_mutation_has_no_numerical_effect(components):
    changed = copy.deepcopy(components.neural_contract)
    for edge in changed["selected_routes"]:
        edge["structural_count"] *= 1001
    altered = model.Components(
        changed, components.embodiment_contract, components.observation_contract
    )
    args = ([0.125] * 6, [0.25, -0.125], observation.SideDescriptors(0.5, -0.5), 0.1)
    assert model.compose_neural_interval(
        *args, components
    ) == model.compose_neural_interval(*args, altered)


def test_clipping_telemetry_and_robust_crossing_definition(artifact):
    for run in artifact["result"]["runs"]:
        rows = run["boundaries"]
        diag = model.diagnostics(rows, run["diagnostics"]["initial_perturbation_eq"])
        assert diag == run["diagnostics"]
        assert diag["clipping"]["observed_interval_count"] == 500
        assert diag["clipping"]["count"] == sum(r["observation_clipped"] for r in rows)
    r = observation.observe_interval(
        observation.ObservationInterval(
            observation.WorldReference("WORLD", 0),
            observation.OrientationBoundary(0, 0, 0),
            observation.OrientationBoundary(1, 0.1, 0.1),
        )
    )
    assert r.clipped and r.global_horizontal_motion_eq == -1
    row = copy.deepcopy(artifact["result"]["runs"][0]["boundaries"][1])
    row["observation"] = r.payload()
    row["observation_clipped"] = r.clipped
    row["latched_motion"]["right"] = r.sides.right
    result = model.diagnostics([row], 0)
    assert result["clipping"] == {
        "count": 1,
        "observed_interval_count": 1,
        "fraction": 1,
        "positive_count": 0,
        "negative_count": 1,
        "duration_ms": 0.1,
    }
    assert model._crossings([0, 1e-300, 0, -1e-300, 0]) == 1


def test_runtime_invalid_observation_stops_without_fabrication(
    preregistration, components, monkeypatch
):
    original = observation.observe_interval

    def reject_second_interval(interval, **kwargs):
        if interval.after.index == 2:
            raise observation.ObservationError(
                observation.ObservationErrorCode.AMBIGUOUS_OR_DISCONTINUOUS_INTERVAL,
                "TEST_ONLY_INVALID_DOMAIN",
            )
        return original(interval, **kwargs)

    monkeypatch.setattr(observation, "observe_interval", reject_second_interval)
    run = model.run_condition(
        preregistration["conditions"][2], preregistration, components
    )
    assert run["termination"]["status"] == "TERMINATED_INVALID_STATE"
    assert run["termination"]["boundary_index"] == 2
    assert len(run["boundaries"]) == 2
    assert "TEST_ONLY_INVALID_DOMAIN" in run["termination"]["reason"]


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("perturbation", "positive_increment_eq", 0.002),
        ("analysis", "decision", "CLOSED_LOOP_LOCAL_DYNAMICS_UNSTABLE"),
        ("analysis", "full_spectral_radius", 2),
        ("equations", "sources", "use new states"),
        ("world", "heading_eq", 1),
    ],
)
def test_preregistration_or_analysis_mutation_rejected(
    preregistration, tmp_path, section, key, value
):
    changed = copy.deepcopy(preregistration)
    changed[section][key] = value
    assert canonical_sha256(changed) != model.PREREGISTRATION_ID
    path = tmp_path / "modified.json"
    path.write_bytes(canonical_json_bytes(changed))
    with pytest.raises(ValueError):
        model.load_preregistration(path)


@pytest.mark.parametrize(
    "mutation",
    [
        "authority",
        "order",
        "perturbation",
        "condition",
        "observation",
        "source",
        "target",
        "drive",
        "orientation",
        "clipping",
        "termination",
        "analysis",
        "hash",
    ],
)
def test_rehashed_tampering_rejected(artifact, tmp_path, mutation):
    changed = copy.deepcopy(artifact)
    p = changed["config"]["preregistration"]
    run = changed["result"]["runs"][2]
    boundary = run["boundaries"][4]
    if mutation == "authority":
        changed["config"]["source_artifacts"]["phase25"]["artifact_id"] = "0" * 64
    elif mutation == "order":
        p["boundary_order"].reverse()
    elif mutation == "perturbation":
        p["perturbation"]["positive_increment_eq"] *= 2
    elif mutation == "condition":
        run["condition"]["orientation_feedback_connected"] = False
    elif mutation == "observation":
        boundary["observation"]["global_horizontal_motion_eq"] += 0.1
    elif mutation == "source":
        boundary["hs_states"][0] += 0.1
    elif mutation == "target":
        boundary["dnp15_states"][0] += 0.1
    elif mutation == "drive":
        boundary["yaw_drive_eq"] += 0.1
    elif mutation == "orientation":
        boundary["yaw_orientation_eq"] += 0.1
    elif mutation == "clipping":
        boundary["observation_clipped"] = True
        run["diagnostics"]["clipping"]["count"] += 1
    elif mutation == "termination":
        run["termination"]["status"] = "TERMINATED_INVALID_STATE"
    elif mutation == "analysis":
        p["analysis"]["differential_matrix"][0][0] += 0.1
    else:
        changed["result_sha256"] = "0" * 64
    if mutation != "hash":
        changed["config_sha256"] = canonical_sha256(changed["config"])
        changed["result_sha256"] = canonical_sha256(changed["result"])
    changed["artifact_id"] = canonical_sha256(
        [changed["schema"], changed["config_sha256"], changed["result_sha256"]]
    )
    folder = tmp_path / changed["artifact_id"]
    folder.mkdir()
    (folder / "closed_loop.json").write_bytes(
        canonical_json_bytes(changed, newline=True)
    )
    (folder / "manifest.json").write_bytes(
        canonical_json_bytes(_manifest(changed), newline=True)
    )
    with pytest.raises(ValueError):
        replay_closed_loop_artifact(folder)


def test_source_authority_mismatch_prevents_execution(preregistration, monkeypatch):
    original = Path.read_bytes
    name = preregistration["authority_records"][0]["document"]

    def altered(self):
        raw = original(self)
        if self.name == name:
            record = json.loads(raw)
            record["status"]["TEST_ONLY_MUTATION"] = True
            return canonical_json_bytes(record)
        return raw

    monkeypatch.setattr(Path, "read_bytes", altered)

    def forbidden(*args, **kwargs):
        pytest.fail("execution occurred before authority validation")

    monkeypatch.setattr(model, "run_condition", forbidden)
    with pytest.raises(ValueError, match="authority mismatch"):
        model.build_closed_loop_artifact()


def test_deterministic_replay_generation_and_cli(artifact, tmp_path, capsys):
    assert model.build_closed_loop_artifact() == artifact
    folder = generate_closed_loop_artifact(output_root=tmp_path)
    assert folder.name == ARTIFACT_ID
    assert _load(folder) == artifact
    assert replay_closed_loop_artifact(folder) == artifact
    assert main(["inspect", str(folder)]) == 0
    assert json.loads(capsys.readouterr().out)["artifact_id"] == ARTIFACT_ID
    assert main(["replay", str(folder)]) == 0
    assert (
        json.loads(capsys.readouterr().out)["preregistration_id"]
        == model.PREREGISTRATION_ID
    )
    assert main(["inspect", str(tmp_path / "missing")]) == 2
    assert "validation error" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        main(["generate", "--gain", "2"])


def test_final_boundary_no_extra_integration(
    artifact, monkeypatch, components, preregistration
):
    calls = 0
    original = model.compose_neural_interval

    def count(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(model, "compose_neural_interval", count)
    run = model.run_condition(
        preregistration["conditions"][0], preregistration, components
    )
    assert calls == 500
    assert run == artifact["result"]["runs"][0]
    assert run["boundaries"][-1]["time_ms"] == 50


def test_no_new_gain_or_recurrent_routes_and_claim_limits(preregistration, artifact):
    assert preregistration["no_translation"]
    assert not preregistration["structural_count_is_efficacy"]
    assert preregistration["physical_mechanics"] == "NONE"
    assert preregistration["electrical_coupling"] == "NONE"
    assert (
        "No absolute heading-error observation"
        in preregistration["motion_only_limitation"]
    )
    assert "Biological optomotor stabilization" in preregistration["forbidden_claims"]
    assert "no_zero_heading_success_metric" in preregistration["diagnostics"]
    source = Path(model.__file__).read_text()
    assert "neural.proxy_step(" in source
    assert "neural.route_contributions(" in source
    assert "embodiment.integrate_orientation(" in source
    assert "observation.observe_interval(" in source
    assert all(
        token not in source
        for token in ["fastapi", "planar_body_plant", "ttm_actuator"]
    )
    assert len(artifact["result"]["active_routes"]) == 6
