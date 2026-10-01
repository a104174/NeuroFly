import copy
import json
import socket
from dataclasses import replace

import numpy as np
import pytest

import neurofly.dnp01_subthreshold_diagnostic as diagnosis
import neurofly.dnp01_subthreshold_diagnostic_artifacts as artifacts
from neurofly.dnp01_subthreshold_diagnostic_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)


@pytest.fixture(scope="module")
def verified():
    # Real full scenario/source numerical replay once, then reuse read-only inputs.
    return diagnosis.load_verified_inputs()


@pytest.fixture
def inputs(verified, monkeypatch):
    monkeypatch.setattr(diagnosis, "load_verified_inputs", lambda path: verified)
    return verified


@pytest.fixture
def diagnostic(inputs):
    return diagnosis.build_diagnostic()


def test_accounting_and_immutable_inputs(diagnostic, inputs):
    battery, sources, _ = inputs
    before = canonical_json_bytes(battery)
    repeat = diagnosis.build_diagnostic()
    assert diagnostic == repeat
    assert canonical_json_bytes(battery) == before
    assert diagnostic["result"]["source_artifact_id"] == diagnosis.SOURCE_ID
    assert len(diagnostic["result"]["runs"]) == 2
    for run in diagnostic["result"]["runs"]:
        assert len(run["boundaries"]) == 15
        assert len(run["lif_terms_by_interval"]) == 14
        for index, body in enumerate((10001, 10010)):
            assert run["targets"][index]["body_id"] == body
            for b in run["boundaries"]:
                assert b["threshold_margin_mV_eq"][index] == (
                    sources["lif"].threshold_mv - b["membrane_mV_eq"][index]
                )
                assert b["refractory_remaining_steps"] == [0, 0]
        assert not run["boundaries"][-1]["drives_outgoing_interval"]


def test_baseline_and_right_only_peak(diagnostic):
    baseline, looming = diagnostic["result"]["runs"]
    for b in baseline["boundaries"]:
        assert b["geometry"] is None
        assert b["active_columns"] == []
        assert b["exposed_body_count"] == 0
        assert b["membrane_mV_eq"] == [-52, -52]
        assert b["available_model_drive_mV_eq"] == [0, 0]
    right, left = looming["targets"]
    assert right["peak_step"] == 14
    assert right["peak_membrane_mV_eq"] == pytest.approx(-51.933657842035174)
    assert right["threshold_margin_at_peak_mV_eq"] == pytest.approx(6.933657842035174)
    assert right["fraction_of_rest_to_threshold_excursion"] == pytest.approx(
        0.009477451137832256
    )
    assert left["peak_membrane_mV_eq"] == -52
    assert left["integrated_used_drive_mV_eq_ms"] == 0
    assert left["identity_contributions"] == []
    assert left["fraction_of_integrated_drive"] == {"LC4": None, "LPLC2": None}
    assert right["spike_count"] == left["spike_count"] == 0


def test_population_and_identity_additive_contributions(diagnostic):
    looming = diagnostic["result"]["runs"][1]
    right = looming["targets"][0]
    assert right["fraction_of_integrated_drive"]["LC4"] == pytest.approx(
        0.27494841751533466
    )
    assert sum(right["integrated_population_drive_mV_eq_ms"].values()) == pytest.approx(
        right["integrated_used_drive_mV_eq_ms"]
    )
    assert sum(
        r["integrated_used_drive_mV_eq_ms"] for r in right["identity_contributions"]
    ) == pytest.approx(right["integrated_used_drive_mV_eq_ms"])
    assert right["largest_contributing_body_ids"] == [20749, 18929, 16128, 14465, 17551]
    for b in looming["boundaries"]:
        parts = b["population_drive_mV_eq"]
        assert np.array(parts["LC4"]) + np.array(parts["LPLC2"]) == pytest.approx(
            b["available_model_drive_mV_eq"]
        )
        for group in b["sensory_groups"]:
            if group["side"] == "L":
                assert group["exposure_sum"] == group["state_sum"] == 0


def test_geometry_and_exposure_discretization_latency(diagnostic):
    r = diagnostic["result"]
    boundaries = r["runs"][1]["boundaries"]
    assert boundaries[0]["geometry"]["relative_distance_world_eq"] == 4
    assert boundaries[-1]["geometry"]["relative_distance_world_eq"] == pytest.approx(
        2.6
    )
    assert [boundaries[i]["geometry"]["lattice_radius"] for i in (0, 14)] == [2, 3]
    assert [boundaries[i]["exposed_body_count"] for i in (0, 14)] == [19, 22]
    latency = r["causal_latency"]
    assert latency["first_exposed_boundary"] == 0
    assert latency["first_nonzero_drive_boundary"] == 1
    assert latency["first_depolarized_boundary"] == 2
    changed = next(
        n for n, b in enumerate(boundaries) if b["geometry"]["lattice_radius"] == 3
    )
    # Expansion at n produces new sensory state at n+1, not instantaneous drive.
    new_bodies = [
        body
        for body in r["runs"][1]["targets"][0]["identity_contributions"]
        if body["exposure_by_boundary"][changed - 1] == 0
        and body["exposure_by_boundary"][changed] > 0
    ]
    assert new_bodies
    for body in new_bodies:
        assert body["state_by_boundary"][changed] == 0
        assert body["state_by_boundary"][changed + 1] > 0
    assert r["temporal_window"]["duration_over_tau_m"] == pytest.approx(0.07)


def test_lif_term_decomposition(diagnostic):
    for run in diagnostic["result"]["runs"]:
        for term in run["lif_terms_by_interval"]:
            terms = [
                term[k]
                for k in (
                    "leak_delta_mV_eq",
                    "external_drive_delta_mV_eq",
                    "synaptic_delta_mV_eq",
                    "reset_refractory_delta_mV_eq",
                )
            ]
            assert np.sum(terms, axis=0) == pytest.approx(term["net_delta_mV_eq"])
            assert term["synaptic_delta_mV_eq"] == [0, 0]
            assert term["reset_refractory_delta_mV_eq"] == [0, 0]
            assert all(v <= 0 for v in term["leak_delta_mV_eq"])
            assert all(v >= 0 for v in term["external_drive_delta_mV_eq"])


def test_structural_counts_never_scale_drive(inputs):
    battery, sources, model = inputs
    states = battery["result"]["runs"][1]["result"]["sensory_state_by_boundary"][-1]
    transfer = model["transfer_model"]["k_transfer_mveq_per_state"]
    first = diagnosis._route_states(states, sources["rows"], sources, transfer)
    altered = {
        **sources,
        "routes": tuple(
            replace(r, structural_weight=r.structural_weight * 1000)
            for r in sources["routes"]
        ),
    }
    assert diagnosis._route_states(states, sources["rows"], altered, transfer) == first


def test_maximum_exposure_audit_reproduces_phase13a(diagnostic):
    bound = diagnostic["result"]["maximum_exposure_audit"]
    assert bound["route_counts_R_L"] == [146, 165]
    assert bound["peak_membrane_mV_eq_R_L"] == pytest.approx(
        [-47.66741697736826, -47.103587679902496]
    )
    assert bound["spike_count"] == 0
    assert not bound["canonical_geometry"]


def test_recorded_exposure_amplitude_bound_is_scoped_and_subthreshold(diagnostic):
    projection = diagnostic["result"]["bottlenecks"][0]
    assert projection["component"] == "WORLD_TO_COLUMN_PROJECTION"
    assert projection["classification"] == "MATERIAL_MODEL_LIMITER"
    assert diagnostic["result"]["maximum_exposure_audit"]["spike_count"] == 0
    envelope = diagnostic["result"]["recorded_exposure_envelope"]
    assert envelope["external_drive_upper_bound_mV_eq_R_L"] == pytest.approx(
        [3.4740711291281734, 0]
    )
    assert envelope["bound_below_threshold_excursion_R_L"] == [True, True]
    assert envelope["threshold_margin_lower_bound_mV_eq_R_L"] == pytest.approx(
        [3.5259288708718266, 7]
    )
    assert "Only histories bounded" in envelope["scope"]


def test_no_retuning_config_or_spike_search(diagnostic):
    assert (
        diagnostic["result"]["counterfactual_drive_factor"]
        == "NOT_COMPUTED_NO_SPIKE_TARGETING_NEEDED"
    )
    assert set(diagnostic["config"]["analysis_semantics"]) == {
        "threshold_margin",
        "baseline_comparison",
        "integration",
        "terms",
        "identity_ranking",
        "maximum_exposure",
    }
    for key in (
        "gain",
        "tau_m_ms",
        "threshold_mv",
        "duration_ms",
        "k_transfer_mveq_per_state",
    ):
        assert key not in diagnostic["config"]


@pytest.mark.parametrize(
    "path",
    [
        ("config", "source_artifact_id"),
        ("config", "source_model_identity_sha256"),
        ("result", "runs", 1, "scenario_execution_id"),
        ("result", "model_parameters_snapshot_not_alternates", "lif", "threshold_mv"),
        ("result", "runs", 1, "boundaries", 14, "time_ms"),
        ("result", "runs", 1, "boundaries", 14, "membrane_mV_eq", 0),
        ("result", "runs", 1, "boundaries", 14, "threshold_mV_eq"),
        ("result", "runs", 1, "boundaries", 14, "population_drive_mV_eq", "LC4", 0),
        (
            "result",
            "runs",
            1,
            "targets",
            0,
            "identity_contributions",
            0,
            "integrated_used_drive_mV_eq_ms",
        ),
        ("result", "bottlenecks", 0, "classification"),
        ("config_sha256",),
        ("result_sha256",),
        ("artifact_id",),
    ],
)
def test_rehashed_tampering_is_rejected(diagnostic, path):
    bad = copy.deepcopy(diagnostic)
    parent = bad
    for key in path[:-1]:
        parent = parent[key]
    original = parent[path[-1]]
    parent[path[-1]] = original + 1 if isinstance(original, (int, float)) else "ALTERED"
    # Attackers recomputing hashes do not bypass numerical/source reconstruction.
    if len(path) > 1:
        bad["config_sha256"] = canonical_sha256(bad["config"])
        bad["result_sha256"] = canonical_sha256(bad["result"])
        bad["artifact_id"] = canonical_sha256(
            [diagnosis.ARTIFACT_SCHEMA, bad["config_sha256"], bad["result_sha256"]]
        )
    with pytest.raises(ValueError, match="offline replay"):
        diagnosis.validate_diagnostic(bad)


def test_artifact_offline_replay_and_manifest_rejection(
    inputs, tmp_path, monkeypatch, capsys
):
    def no_network(*args, **kwargs):
        raise AssertionError("diagnostic must be offline")

    monkeypatch.setattr(socket, "create_connection", no_network)
    path = artifacts.generate_diagnostic_artifact(output_root=tmp_path)
    first = (path / artifacts.RESULT_FILENAME).read_bytes()
    assert artifacts.generate_diagnostic_artifact(output_root=tmp_path) == path
    assert artifacts.replay_diagnostic_artifact(path)["artifact_id"] == path.name
    assert (path / artifacts.RESULT_FILENAME).read_bytes() == first
    assert main(["inspect", str(path)]) == 0
    assert "NO RETUNING PERFORMED" in capsys.readouterr().out
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["artifact_id"] = "ALTERED"
    manifest_path.write_bytes(canonical_json_bytes(manifest, newline=True))
    with pytest.raises(ValueError, match="manifest/hash"):
        artifacts.replay_diagnostic_artifact(path)


def test_accounting_detects_source_contradiction_and_never_repairs(inputs):
    battery, sources, model = inputs
    bad = copy.deepcopy(battery["result"]["runs"][1])
    bad["result"]["dnp01_membrane_mv"][2][0] += 0.1
    with pytest.raises(diagnosis.DiagnosticCompositionError):
        diagnosis._diagnose_run(bad, sources, model)


def test_wrong_source_identity_fails_closed(monkeypatch):
    monkeypatch.setattr(
        diagnosis, "replay_scenario_artifact", lambda path: {"artifact_id": "WRONG"}
    )
    with pytest.raises(ValueError, match="exact pinned"):
        diagnosis.load_verified_inputs()
