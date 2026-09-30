import copy
import math
import socket

import numpy as np
import pytest

import neurofly.closed_loop_scenario as scenario
from neurofly.closed_loop_scenario_artifacts import (
    generate_scenario_artifact,
    replay_scenario_artifact,
)
from neurofly.g1_proxy_passive_electrical import integrate_counts, reference_config
from neurofly.motor_pathway import (
    TTMnIntegratorConfig,
    _integrate_ttmn,
    _map_motor_inputs,
)
from neurofly.planar_body_plant import body_interval_step, common_mode_speed
from neurofly.planar_body_plant import reference_config as plant_config
from neurofly.relative_column_sensory_dynamics import integrate_exposure_values
from neurofly.simulation import ExternalDriveSchedule, LIFSimulator, SpikeEvent
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)


@pytest.fixture(scope="module")
def sources():
    return scenario.load_scenario_sources()


@pytest.fixture
def battery(sources, monkeypatch):
    # Source replay already performed; no synthetic events enter these runs.
    monkeypatch.setattr(scenario, "load_scenario_sources", lambda: sources)
    return scenario.build_scenario_battery()


def test_canonical_accounting_baseline_and_looming(battery, sources):
    assert [r["result"]["scenario_kind"] for r in battery["result"]["runs"]] == list(
        scenario.KINDS
    )
    for run in battery["result"]["runs"]:
        r = run["result"]
        assert r["time_ms"] == [n * 0.1 for n in range(15)]
        assert len(r["sensory_identities"]) == 311
        assert [b["body_id"] for b in r["sensory_identities"]] == [
            b["body_id"] for b in sources["rows"]
        ]
        assert np.array(r["sensory_state_by_boundary"]).shape == (15, 311)
        assert np.array(r["exposure_by_boundary"]).shape == (15, 311)
        assert len(r["body_intervals"]) == 14
        assert r["dnp01_spikes"] == []
        assert all(records == [] for records in r["downstream_events"].values())
        assert all(b["x_world_eq"] == b["z_world_eq"] == 0 for b in r["world_body"])
        assert all(
            s["ttmn_state"]
            == s["voltage_deviation_mV_eq"]
            == s["activation_proxy"]
            == [0, 0]
            for s in r["downstream_state_by_boundary"]
        )
        assert r["statuses"]["closed_loop_execution_completed"]
        assert r["statuses"]["body_state_feedback_wired"]
        assert not r["statuses"]["body_state_feedback_realized"]
        assert not r["statuses"]["genuine_nonzero_actuation_occurred"]
        assert not r["statuses"]["body_movement_occurred"]
    baseline, looming = [r["result"] for r in battery["result"]["runs"]]
    assert all(
        b["active_columns"] == []
        and b["geometry"] is None
        and b["object_z_world_eq"] is None
        for b in baseline["world_body"]
    )
    assert np.count_nonzero(baseline["exposure_by_boundary"]) == 0
    assert np.count_nonzero(baseline["sensory_state_by_boundary"]) == 0
    assert baseline["dnp01_membrane_mv"] == [[-52, -52]] * 15
    assert not baseline["statuses"]["environment_affected_sensory_input"]
    assert looming["statuses"]["environment_affected_sensory_input"]
    assert looming["world_body"][0]["geometry"]["lattice_radius"] == 2
    assert looming["world_body"][-1]["geometry"]["lattice_radius"] == 3
    assert looming["world_body"][-1]["object_z_world_eq"] == pytest.approx(2.6)
    assert np.max(looming["sensory_state_by_boundary"]) > 0
    assert np.max(looming["dnp01_membrane_mv"]) < -45
    for index, row in enumerate(sources["rows"]):
        if row["side"] == "L":
            assert all(e[index] == 0 for e in looming["exposure_by_boundary"])


def test_sensory_and_dnp01_batch_parity(battery, sources):
    for run in battery["result"]["runs"]:
        r = run["result"]
        for index in range(311):
            trace = integrate_exposure_values(
                [e[index] for e in r["exposure_by_boundary"][:-1]],
                dt_ms=0.1,
                tau_sens_ms=1,
                gain=1,
            )
            assert [t["state_value"] for t in trace] == [
                s[index] for s in r["sensory_state_by_boundary"]
            ]
        drive = ExternalDriveSchedule.from_body_ids(
            {
                body: [d[index] for d in r["dnp01_drive_by_interval"]]
                for index, body in enumerate((10001, 10010))
            },
            steps=14,
            provenance_id="phase7f_edge_routed_exploratory_model_drive_v1",
        )
        old = LIFSimulator(sources["graph"], sources["lif"]).run(
            drive, allow_model_readout_drive=True
        )
        assert old.membrane_mv.tolist() == r["dnp01_membrane_mv"]
        assert old.synaptic_mveq.tolist() == r["dnp01_synaptic_mV_eq"]
        assert list(old.spikes) == []
        # No instant exposure→DNp01 shortcut: first interval has zero drive.
        assert r["dnp01_drive_by_interval"][0] == [0, 0]


def test_nonzero_lif_kernel_parity(sources):
    config, graph = sources["lif"], sources["graph"]
    drives = [[2000.0, 0.0]] * 14
    v = np.array([-52.0, -52.0])
    synaptic = np.zeros(2)
    refractory = np.zeros(2, dtype=np.int64)
    values = [v.tolist()]
    events = []
    for n, drive in enumerate(drives):
        v, synaptic, indices = scenario.lif_interval_step(
            config, v, synaptic, refractory, np.array(drive)
        )
        for i in indices.tolist():
            events.append(scenario.make_spike_event(graph.nodes[i], i, n + 1, config))
            scenario.apply_spike_reset(config, v, refractory, i)
        values.append(v.tolist())
    schedule = ExternalDriveSchedule.from_body_ids(
        {10001: [2000.0] * 14, 10010: [0.0] * 14},
        steps=14,
        provenance_id="phase7f_edge_routed_exploratory_model_drive_v1",
    )
    old = LIFSimulator(graph, config).run(schedule, allow_model_readout_drive=True)
    assert old.membrane_mv.tolist() == values
    assert list(old.spikes) == events
    assert events


@pytest.mark.parametrize("body,node,side", [(10001, 0, "R"), (10010, 1, "L")])
def test_only_noncanonical_full_downstream_feedback_proof(sources, body, node, side):
    config = scenario.ScenarioConfig(scenario.KINDS[1])
    runtime = scenario.DownstreamRuntime("TEST_ONLY_NONCANONICAL", config, sources)
    runtime.advance([], 0)
    spike = SpikeEvent(
        time_ms=0.1, step=1, body_id=body, node_index=node, neuron_type="DNp01"
    )
    output = runtime.advance([spike], 1)
    assert {k: len(v) for k, v in runtime.ledgers.items()} == {
        k: 1 for k in runtime.ledgers
    }
    channel = "RIGHT_TTM_ACTUATOR" if side == "R" else "LEFT_TTM_ACTUATOR"
    other = "LEFT_TTM_ACTUATOR" if side == "R" else "RIGHT_TTM_ACTUATOR"
    assert output["actuator_commands"][channel] == 0.2
    assert output["actuator_commands"][other] == 0
    ledger = runtime.ledgers
    assert ledger["motor_outputs"][0]["parent_dnp01_event_ids"] == [
        ledger["motor_inputs"][0]["parent_dnp01_event_id"]
    ]
    assert (
        ledger["dispatches"][0]["parent_event_id"]
        == ledger["motor_outputs"][0]["event_id"]
    )
    assert (
        ledger["receipts"][0]["parent_dispatch_id"]
        == ledger["dispatches"][0]["dispatch_id"]
    )
    assert (
        ledger["electrical_inputs"][0]["parent_receipt_id"]
        == ledger["receipts"][0]["receipt_id"]
    )
    assert (
        ledger["electrical_inputs"][0]["added_delay_semantics"]
        == "ZERO_ADDED_MODEL_DELAY_ASSUMPTION"
    )
    assert all(
        row["step"] == 1 and row["time_ms"] == 0.1
        for rows in ledger.values()
        for row in rows
    )
    # Integrate a real composed command, then use the updated body in projection.
    common, speed = common_mode_speed(
        output["actuator_commands"]["RIGHT_TTM_ACTUATOR"],
        output["actuator_commands"]["LEFT_TTM_ACTUATOR"],
        plant_config(),
    )
    assert common == speed == 0.1
    updated = body_interval_step(0, 0, 0.1, speed)
    object_position = (0, 1 / math.tan(0.3) + 0.005)
    before, _, exposures_before = scenario.exposure_vector(
        config, (0, 0), object_position, sources
    )
    after, _, exposures_after = scenario.exposure_vector(
        config, updated, object_position, sources
    )
    assert updated == (0, pytest.approx(0.01))
    assert before["relative_distance_world_eq"] != after["relative_distance_world_eq"]
    assert before["lattice_radius"] == 2 and after["lattice_radius"] == 3
    assert exposures_before != exposures_after
    # Same shared kernels reproduce the historical batch numerical authorities.
    states = [runtime.motor.copy()]
    for n in range(2, 15):
        runtime.advance([], n)
        states.append(runtime.motor.copy())
    mapped = _map_motor_inputs(
        [spike], dt_ms=0.1, steps=14, model=TTMnIntegratorConfig()
    )
    batch = _integrate_ttmn(
        times_ms=tuple(n * 0.1 for n in range(15)),
        dt_ms=0.1,
        inputs=mapped,
        model=TTMnIntegratorConfig(),
    )
    index = 0 if side == "R" else 1
    assert [s[index] for s in states] == list(batch[index].state[1:])
    counts = [0, 1] + [0] * 79
    electrical = integrate_counts(reference_config(), counts)
    assert runtime.electrical[index] == electrical["voltage_deviation_mV_eq"][14]


@pytest.mark.parametrize(
    "object_position", [(0, 0), (0, -1), (math.nan, 4), (0, math.inf)]
)
def test_invalid_geometry(object_position):
    with pytest.raises(ValueError):
        scenario.project_world(
            scenario.ScenarioConfig(scenario.KINDS[1]), (0, 0), object_position
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"kind": "unknown"},
        {"kind": scenario.KINDS[1], "radius_world_eq": 0},
        {"kind": scenario.KINDS[1], "dt_ms": 0.2},
        {"kind": scenario.KINDS[1], "interval_count": 15},
        {"kind": scenario.KINDS[1], "vz_world_eq_per_ms": math.inf},
        {"kind": scenario.KINDS[1], "body_z_world_eq": math.nan},
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        scenario.ScenarioConfig(**kwargs)


def test_config_roundtrip_identity_and_no_injection_fields(sources):
    for kind in scenario.KINDS:
        config = scenario.ScenarioConfig(kind)
        assert scenario.ScenarioConfig.from_payload(config.payload()) == config
    config = scenario.ScenarioConfig(scenario.KINDS[1])
    shifted = scenario.ScenarioConfig(scenario.KINDS[1], object_z_world_eq=5)
    assert canonical_sha256(config.payload()) != canonical_sha256(shifted.payload())
    assert not {
        "seed",
        "force_spike",
        "override_actuator",
        "inject_motor_event",
    }.intersection(config.payload())
    payload = config.payload()
    payload["projection"]["side"] = "L"
    with pytest.raises(ValueError):
        scenario.ScenarioConfig.from_payload(payload)
    runtime = scenario.DownstreamRuntime("TEST_ONLY_NONCANONICAL", config, sources)
    with pytest.raises(ValueError):
        runtime.advance([], 1)


@pytest.mark.parametrize(
    "mutation",
    [
        "kind",
        "timing",
        "body_initial",
        "object_initial",
        "velocity",
        "side",
        "centre",
        "scale",
        "discretization",
        "source",
        "tick",
        "sensory",
        "membrane",
        "spikes",
        "ancestry",
        "actuator",
        "body",
        "status",
        "hash",
        "artifact",
    ],
)
def test_semantic_tamper_rejection(battery, mutation):
    payload = copy.deepcopy(battery)
    run = payload["result"]["runs"][1]
    config = run["config"]["scenario"]
    result = run["result"]
    if mutation == "kind":
        config["scenario_kind"] = "BASELINE_CONTROL"
    elif mutation == "timing":
        config["dt_ms"] *= 2
    elif mutation == "body_initial":
        config["body_initial"]["z_world_eq"] = 1
    elif mutation == "object_initial":
        config["object"]["object_z_world_eq"] = 5
    elif mutation == "velocity":
        config["object"]["vz_world_eq_per_ms"] = -2
    elif mutation in ("side", "centre", "scale", "discretization"):
        key = {
            "side": "side",
            "centre": "centre_q",
            "scale": "angular_to_lattice_scale",
            "discretization": "radius_discretization",
        }[mutation]
        config["projection"][key] = "changed"
    elif mutation == "source":
        run["config"]["sources"]["population_artifact_id"] = "changed"
    elif mutation == "tick":
        config["tick_semantics"] = "changed"
    elif mutation == "sensory":
        result["sensory_state_by_boundary"][1][0] = 1
    elif mutation == "membrane":
        result["dnp01_membrane_mv"][1][0] = 0
    elif mutation == "spikes":
        result["dnp01_spikes"].append({"step": 1})
    elif mutation == "ancestry":
        result["downstream_events"]["electrical_inputs"].append(
            {"parent_receipt_id": "forged"}
        )
    elif mutation == "actuator":
        result["downstream_state_by_boundary"][1]["actuator_commands"][
            "RIGHT_TTM_ACTUATOR"
        ] = 0.2
    elif mutation == "body":
        result["world_body"][1]["z_world_eq"] = 1
    elif mutation == "status":
        result["statuses"]["body_movement_occurred"] = True
    elif mutation == "hash":
        payload["result_sha256"] = "changed"
    else:
        payload["artifact_id"] = "changed"
    with pytest.raises(ValueError):
        scenario.validate_scenario_battery(payload)


def test_artifact_offline_reset_bytes_and_manifest(battery, tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline replay attempted network")

    monkeypatch.setattr(socket, "create_connection", no_network)
    path = generate_scenario_artifact(output_root=tmp_path)
    assert replay_scenario_artifact(path) == battery
    raw = (path / "scenarios.json").read_bytes()
    assert raw == canonical_json_bytes(battery, newline=True)
    assert generate_scenario_artifact(output_root=tmp_path) == path
    assert (path / "scenarios.json").read_bytes() == raw
    (path / "manifest.json").write_bytes(b"{}\n")
    with pytest.raises(ValueError):
        replay_scenario_artifact(path)


def test_no_historical_spoofing_or_physical_outputs(battery):
    forbidden = {
        "source_synthetic_run_id",
        "source_fixture_id",
        "force",
        "torque",
        "mass",
        "gravity",
        "joint_angle",
    }

    def walk(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)

    # Historical config references are explicitly references, not runtime inputs.
    for run in battery["result"]["runs"]:
        walk(run["result"])
        assert (
            run["result"]["provenance_kind"]
            == "EXPLORATORY_GENUINE_CLOSED_LOOP_SCENARIO"
        )


def test_full_historical_7o_numerical_replay():
    from neurofly.sensory_population_execution import execute_311
    from neurofly.sensory_population_execution_artifacts import (
        DEFAULT_ROOT,
        load_execution_artifact,
    )
    from neurofly.sensory_population_execution_cli import _inputs

    old = load_execution_artifact(DEFAULT_ROOT / scenario.HISTORICAL_IDS["phase7o"])
    config, result, _ = execute_311(*_inputs()[0])
    assert (old.config, old.result) == (config, result)
