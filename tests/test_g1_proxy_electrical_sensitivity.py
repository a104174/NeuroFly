"""Phase 9C model-internal sensitivity is not empirical parameter identification."""

from __future__ import annotations

import copy
import json
import math
import shutil
import socket
from dataclasses import replace

import pytest

import neurofly.g1_proxy_electrical_sensitivity as sensitivity
from neurofly.g1_proxy_electrical_sensitivity_artifacts import (
    generate_sensitivity_artifact,
    replay_sensitivity_artifact,
)
from neurofly.g1_proxy_electrical_sensitivity_cli import main
from neurofly.g1_proxy_passive_electrical import (
    FIXTURE_IDS,
    build_response,
    reference_config,
)
from neurofly.g1_proxy_passive_electrical_artifacts import replay_response_artifact
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping_artifacts import replay_ttm_g1_mapping_artifact
from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS


@pytest.fixture(scope="module")
def executed():
    responses = []
    for tau in sensitivity.FACTORS:
        for scale in sensitivity.FACTORS:
            responses.append(
                build_response(
                    replace(
                        reference_config(),
                        tau_effective_ms=tau,
                        event_scale_effective_mV_eq=2 * scale,
                    )
                )
            )
    return responses


@pytest.fixture(scope="module")
def experiment():
    return sensitivity.build_sensitivity()


def rows(response):
    return {
        (f["fixture_id"], i["source_body_id"]): i
        for f in response["result"]["fixtures"]
        for i in f["instances"]
    }


def test_exact_grid_coverage_and_reference(experiment):
    cells = experiment["result"]["cells"]
    assert len(cells) == 9
    assert [
        (
            c["model_config"]["tau_effective_ms"],
            c["model_config"]["event_scale_effective_mV_eq"],
        )
        for c in cells
    ] == [(t, q) for t in (0.5, 1.0, 2.0) for q in (1.0, 2.0, 4.0)]
    assert len({c["cell_id"] for c in cells}) == 9
    assert [c["is_reference_cell"] for c in cells] == [False] * 4 + [True] + [False] * 4
    assert cells[4]["response_artifact_id"] == sensitivity.SOURCE_ID
    assert experiment["result"]["fixture_run_count"] == 54
    assert experiment["result"]["trajectory_count"] == 108
    for cell in cells:
        assert len(cell["summaries"]) == 12
        assert (
            tuple(dict.fromkeys(s["fixture_id"] for s in cell["summaries"]))
            == FIXTURE_IDS
        )
        assert sum(s["input_token_count"] for s in cell["summaries"]) == 8
        for field in (
            "reference_voltage_mV_eq",
            "dt_ms",
            "interval_count",
            "proxy_domain_id",
            "event_order",
            "timing_assumption",
        ):
            assert cell["model_config"][field] == reference_config().payload()[field]


def test_existing_simulator_is_called_exactly_nine_times(monkeypatch, experiment):
    configs = []
    original = sensitivity.build_response

    def record(config):
        configs.append(config)
        return original(config)

    monkeypatch.setattr(sensitivity, "build_response", record)
    assert sensitivity.build_sensitivity() == experiment
    assert len(configs) == 9
    assert configs[4] == reference_config()


def test_scale_linearity_and_normalized_invariance(executed):
    for ti in range(3):
        ref = rows(executed[ti * 3 + 1])
        for qi, factor in enumerate(sensitivity.FACTORS):
            for key, row in rows(executed[ti * 3 + qi]).items():
                assert row["voltage_deviation_mV_eq"] == [
                    factor * v for v in ref[key]["voltage_deviation_mV_eq"]
                ]
                assert [v / (2 * factor) for v in row["voltage_deviation_mV_eq"]] == [
                    v / 2 for v in ref[key]["voltage_deviation_mV_eq"]
                ]
                assert row["token_count"] == ref[key]["token_count"]
                assert row["source_token_ids"] == ref[key]["source_token_ids"]


def test_tau_closed_form_retention_and_repeated_residual(executed, experiment):
    for response, cell in zip(executed, experiment["result"]["cells"], strict=True):
        tau = cell["model_config"]["tau_effective_ms"]
        q = cell["model_config"]["event_scale_effective_mV_eq"]
        values = rows(response)[("RIGHT_SINGLE_EVENT", 800146)][
            "voltage_deviation_mV_eq"
        ]
        assert values[10] == q
        assert values[10:] == pytest.approx(
            [q * math.exp(-k * 0.1 / tau) for k in range(71)], rel=1e-13
        )
        assert values[20] / values[10] == pytest.approx(math.exp(-1 / tau), rel=1e-13)
        repeated = rows(response)[("RIGHT_REPEATED_EVENTS", 800146)][
            "voltage_deviation_mV_eq"
        ]
        assert repeated[30] == pytest.approx(q * (1 + math.exp(-2 / tau)), rel=1e-13)
        summary = next(
            s
            for s in cell["summaries"]
            if s["fixture_id"] == "RIGHT_REPEATED_EVENTS"
            and s["source_body_id"] == 800146
        )
        assert summary["repeated_second_peak_ratio"] == pytest.approx(
            1 + math.exp(-2 / tau), rel=1e-13
        )
    for qi in range(3):
        active = [rows(executed[ti * 3 + qi]) for ti in range(3)]
        for n in range(11, 81):
            vals = [
                r[("RIGHT_SINGLE_EVENT", 800146)]["voltage_deviation_mV_eq"][n]
                for r in active
            ]
            assert vals[0] < vals[1] < vals[2]
        peaks = [
            r[("RIGHT_REPEATED_EVENTS", 800146)]["voltage_deviation_mV_eq"][30]
            for r in active
        ]
        assert peaks[0] < peaks[1] < peaks[2]


def test_zero_inactive_bilateral_and_symmetry(executed):
    for response in executed:
        instances = rows(response)
        for body in (800146, 804642):
            zero = instances[("ZERO_EVENT_CONTROL", body)]
            assert zero["voltage_deviation_mV_eq"] == [0.0] * 81
            assert zero["proxy_voltage_mV_eq"] == [0.0] * 81
            single = instances[
                ("RIGHT_SINGLE_EVENT" if body == 800146 else "LEFT_SINGLE_EVENT", body)
            ]
            bilateral = instances[("BILATERAL_SIMULTANEOUS_EVENT", body)]
            assert (
                single["voltage_deviation_mV_eq"]
                == bilateral["voltage_deviation_mV_eq"]
            )
            assert single["instance_id"] != bilateral["instance_id"]
        assert (
            instances[("RIGHT_SINGLE_EVENT", 804642)]["voltage_deviation_mV_eq"]
            == [0.0] * 81
        )
        assert (
            instances[("LEFT_SINGLE_EVENT", 800146)]["voltage_deviation_mV_eq"]
            == [0.0] * 81
        )
        assert (
            instances[("RIGHT_REPEATED_EVENTS", 800146)]["voltage_deviation_mV_eq"]
            == instances[("LEFT_REPEATED_EVENTS", 804642)]["voltage_deviation_mV_eq"]
        )


def test_analysis_rejects_unexpected_model_behavior(executed):
    bad = copy.deepcopy(executed)
    bad[0]["result"]["fixtures"][1]["instances"][0]["voltage_deviation_mV_eq"][10] = 5.0
    with pytest.raises(ValueError):
        sensitivity.analyze_cells(bad)
    with pytest.raises(ValueError):
        sensitivity.analyze_cells(executed[:-1])


def test_no_empirical_identification_and_historical_identity(experiment):
    analysis = experiment["result"]["analysis"]
    assert (
        analysis["structural_separability"]
        == sensitivity.DECISIONS["structural_separability"]
    )
    assert (
        analysis["biological_tau"]
        == analysis["biological_event_scale"]
        == "NOT_BIOLOGICALLY_IDENTIFIABLE_CURRENTLY"
    )
    assert (
        replay_ttm_g1_mapping_artifact(DEFAULT_SOURCE_PATHS["phase8u"]).contract[
            "result"
        ]["formal_ready_mapping_count"]
        == 0
    )
    source = replay_response_artifact(sensitivity.DEFAULT_MODEL_ARTIFACT)
    assert source["artifact_id"] == sensitivity.SOURCE_ID
    assert source["config"]["model"] == reference_config().payload()
    assert (
        source["config_sha256"]
        == "d3807d88f777e8f6754a8e3aab591e42b643974e7417451509771581d7c013d0"
    )
    assert (
        source["result_sha256"]
        == "fa11b093b1a3013d397bb459c3c1f39b1a96543b8380a792e89dc0bdfa8e91d8"
    )


@pytest.mark.parametrize(
    "path,value",
    [
        (("config", "tau_factors", 0), 0.25),
        (("config", "source_phase9b", "artifact_id"), "wrong"),
        (("result", "cells", 0, "model_config", "tau_effective_ms"), 0.6),
        (("result", "cells", 0, "model_config", "event_scale_effective_mV_eq"), 3.0),
        (("result", "cells", 0, "is_reference_cell"), True),
        (("result", "cells", 0, "summaries", 2, "fixture_id"), "OTHER"),
        (("result", "cells", 0, "summaries", 2, "source_token_ids", 0), "altered"),
        (("result", "cells", 0, "summaries", 2, "peak_deviation_mV_eq"), 45.0),
        (("result", "analysis", "structural_separability"), "NOT_SEPARABLE"),
        (("artifact_id",), "wrong"),
        (("result_sha256",), "wrong"),
    ],
)
def test_tamper_rejection(experiment, path, value):
    bad = copy.deepcopy(experiment)
    target = bad
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        sensitivity.validate_sensitivity(bad)


def test_rehashed_tamper_and_source_mutation(experiment, tmp_path):
    bad = copy.deepcopy(experiment)
    bad["result"]["cells"][0]["summaries"][2]["final_deviation_mV_eq"] = 123.0
    bad["result_sha256"] = canonical_sha256(bad["result"])
    bad["artifact_id"] = canonical_sha256(
        [sensitivity.ARTIFACT_SCHEMA, bad["config_sha256"], bad["result_sha256"]]
    )
    with pytest.raises(ValueError):
        sensitivity.validate_sensitivity(bad)
    destination = tmp_path / sensitivity.SOURCE_ID
    shutil.copytree(sensitivity.DEFAULT_MODEL_ARTIFACT, destination)
    source = json.loads((destination / "response.json").read_bytes())
    source["result"]["fixtures"][1]["instances"][0]["token_count"][10] = 2
    (destination / "response.json").write_bytes(
        canonical_json_bytes(source, newline=True)
    )
    with pytest.raises(ValueError):
        sensitivity.build_sensitivity(model_artifact=destination)


def test_compact_deterministic_identity(experiment):
    assert (
        experiment["artifact_id"]
        == "dfe98ec90078124f4a66df825b552d05ed317fcb89d33e0f374b99c6bfd4bfa4"
    )
    assert (
        experiment["config_sha256"]
        == "58ec7a9fa8125b48ed62a4ca66f794e4a47c83a0d789e6fbd078a05555b80073"
    )
    assert (
        experiment["result_sha256"]
        == "bd24acf765556e8f0e2b2189ba5d6a0cf14824253c44ba951c07bd0d24d804f3"
    )
    assert "voltage_deviation_mV_eq" not in canonical_json_bytes(experiment).decode()
    assert "best_cell" not in canonical_json_bytes(experiment).decode()


def test_offline_byte_replay_and_cli(tmp_path, monkeypatch, capsys, experiment):
    def deny_network(*args, **kwargs):
        raise AssertionError("network forbidden")

    monkeypatch.setattr(socket, "create_connection", deny_network)
    path = generate_sensitivity_artifact(output_root=tmp_path)
    raw = {p.name: p.read_bytes() for p in path.iterdir()}
    assert replay_sensitivity_artifact(path) == experiment
    assert generate_sensitivity_artifact(output_root=tmp_path) == path
    assert raw == {p.name: p.read_bytes() for p in path.iterdir()}
    for command in ("inspect", "replay"):
        assert main([command, str(path)]) == 0
        output = json.loads(capsys.readouterr().out)
        assert output["cell_count"] == 9
    (path / "manifest.json").write_bytes(raw["manifest.json"] + b" ")
    with pytest.raises(ValueError):
        replay_sensitivity_artifact(path)
    assert main(["replay", str(path)]) == 2
