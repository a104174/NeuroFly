"""Bounded deterministic world→311 sensory→genuine motor→body feedback runtime."""

from __future__ import annotations

import copy
import math
from dataclasses import asdict, dataclass

import numpy as np

from neurofly.bounded_sensory_population import _reference_lif_config
from neurofly.g1_proxy_passive_electrical import (
    DEFAULT_PROXY_ARTIFACT,
    electrical_boundary_step,
)
from neurofly.g1_proxy_passive_electrical import (
    reference_config as electrical_config,
)
from neurofly.malecns.sensory import angular_half_size
from neurofly.model_derived_ttmn_target_dispatch import (
    _target_contract,
    dispatch_runtime_output,
)
from neurofly.motor_pathway import (
    MOTOR_PATHWAY_EVIDENCE,
    TTMnIntegratorConfig,
    _map_motor_inputs,
    ttmn_boundary_step,
)
from neurofly.muscle_activation import activate_samples
from neurofly.muscle_activation import reference_config as activation_config
from neurofly.planar_body_plant import (
    body_interval_step,
    common_mode_speed,
)
from neurofly.planar_body_plant import (
    reference_config as plant_config,
)
from neurofly.planar_body_plant_artifacts import DEFAULT_ARTIFACT_ROOT as BODY_ROOT
from neurofly.planar_body_plant_artifacts import replay_plant_artifact
from neurofly.relative_column_assignment import (
    RelativeColumnStimulus,
    active_column_set,
    compute_body_exposure,
)
from neurofly.relative_column_dnp01_transfer import route_population_drive
from neurofly.relative_column_sensory_dynamics import sensory_state_step
from neurofly.sensory_dnp01_motor_adapter_artifacts import (
    DEFAULT_ARTIFACT_ROOT as MOTOR_ROOT,
)
from neurofly.sensory_dnp01_motor_adapter_artifacts import (
    replay_sensory_dnp01_motor_artifact,
)
from neurofly.sensory_population_execution import _assert_sources, _routes
from neurofly.sensory_population_execution_artifacts import DEFAULT_ROOT as SENSORY_ROOT
from neurofly.sensory_population_execution_artifacts import load_execution_artifact
from neurofly.sensory_population_execution_cli import _inputs
from neurofly.simulation import (
    PHASE7F_READOUT_SCOPE_ID,
    LIFSimulator,
    SimulationGraph,
    apply_spike_reset,
    lif_interval_step,
    make_spike_event,
)
from neurofly.synthetic_ttmn_output_rule import (
    REFERENCE_THRESHOLD_DIMENSIONLESS,
    threshold_crossed,
)
from neurofly.ttm_abstract_electrical_input import token_runtime_receipt
from neurofly.ttm_actuator import ACTION, actuator_channel
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_proxy_mapping_artifacts import replay_proxy_artifact
from neurofly.ttm_neuromuscular_input_receipt import receipt_runtime_dispatch

CONFIG_SCHEMA = "closed_loop_scenario_config_v1"
RESULT_SCHEMA = "closed_loop_scenario_result_v1"
ARTIFACT_SCHEMA = "closed_loop_scenario_artifact_v1"
KINDS = ("BASELINE_CONTROL", "LOOMING_CIRCUIT_VALIDATION")
TICK_SEMANTICS = (
    "BOUNDARY_SPIKES_TO_COMMANDS_N_SENSORY_N_DRIVES_NEURAL_N_PLUS_1_BODY_N_TO_N_PLUS_1"
)
EXCLUSIONS = [
    "EXPLORATORY_UNREGISTERED_RETINOTOPY_MODEL_SPACE_ONLY",
    "NO_CALIBRATION_RETUNING_SCRIPTED_BEHAVIOR_OR_LLM_CONTROL",
    "NO_PHYSICAL_FORCE_CONTACT_STEERING_OR_ESCAPE_CLAIM",
    "NO_FRONTEND_API_OR_CANONICAL_EVENT_INJECTION",
]
HISTORICAL_IDS = {
    "phase7o": "99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5",
    "phase8c": "5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf",
    "phase9b": "72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f",
    "phase10b": "4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb",
    "phase11b": "478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40",
    "phase12b": "bb3696faae558778555601991de3fd36081d5853c889fcb7aac5ffd79593eba3",
}


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True, slots=True)
class ScenarioConfig:
    kind: str
    body_x_world_eq: float = 0.0
    body_z_world_eq: float = 0.0
    object_x_world_eq: float = 0.0
    object_z_world_eq: float = 4.0
    radius_world_eq: float = 1.0
    vx_world_eq_per_ms: float = 0.0
    vz_world_eq_per_ms: float = -1.0
    dt_ms: float = 0.1
    interval_count: int = 14

    def __post_init__(self):
        if (
            self.kind not in KINDS
            or type(self.interval_count) is not int
            or self.interval_count != 14
            or self.dt_ms != 0.1
        ):
            raise ValueError("require supported scenario and pinned 14×0.1 ms grid")
        if any(
            not _finite(getattr(self, name))
            for name in self.__dataclass_fields__
            if name not in ("kind", "interval_count")
        ):
            raise ValueError("scenario coordinates/timing must be finite")
        if self.radius_world_eq <= 0:
            raise ValueError("require positive object radius")

    def payload(self):
        return {
            "schema_version": CONFIG_SCHEMA,
            "scenario_kind": self.kind,
            "dt_ms": self.dt_ms,
            "interval_count": self.interval_count,
            "body_initial": {
                "x_world_eq": float(self.body_x_world_eq),
                "z_world_eq": float(self.body_z_world_eq),
                "fixed_heading": "POSITIVE_Z",
            },
            "stimulus_enabled": self.kind == KINDS[1],
            "object": {
                name: float(getattr(self, name))
                for name in (
                    "object_x_world_eq",
                    "object_z_world_eq",
                    "radius_world_eq",
                    "vx_world_eq_per_ms",
                    "vz_world_eq_per_ms",
                )
            }
            if self.kind == KINDS[1]
            else None,
            "projection": {
                "side": "R",
                "centre_q": 23,
                "centre_r": 9,
                "angular_to_lattice_scale": 10,
                "radius_discretization": "FLOOR",
            },
            "tick_semantics": TICK_SEMANTICS,
            "assumptions": {
                key: "MODEL_ASSUMPTION"
                for key in (
                    "body_reset",
                    "object_geometry",
                    "object_velocity",
                    "FIXED_RELATIVE_COLUMN_CENTRE_ASSUMPTION",
                    "FIXED_RIGHT_SIDE_ASSUMPTION",
                    "HALF_ANGLE_TO_LATTICE_RADIUS_SCALE_ASSUMPTION",
                    "INTEGER_FLOOR_DISCRETIZATION_ASSUMPTION",
                )
            },
            "scientific_exclusions": list(EXCLUSIONS),
        }

    @classmethod
    def from_payload(cls, payload):
        try:
            body = payload["body_initial"]
            config = cls(
                payload["scenario_kind"],
                body["x_world_eq"],
                body["z_world_eq"],
                **(payload["object"] or {}),
                dt_ms=payload["dt_ms"],
                interval_count=payload["interval_count"],
            )
        except (KeyError, TypeError) as exc:
            raise ValueError("malformed scenario config") from exc
        if canonical_json_bytes(config.payload()) != canonical_json_bytes(payload):
            raise ValueError("scenario semantics changed")
        return config


def scenario_metadata():
    return [
        {
            "id": kind,
            "title": title,
            "availability": "BACKEND_SCIENTIFIC_RUNTIME",
            "description": description,
            "configurable_fields": ["body_initial", "object"],
            "caveats": list(EXCLUSIONS),
        }
        for kind, title, description in (
            (
                KINDS[0],
                "Baseline Control",
                "Empty-stimulus neutral control; no locomotor baseline demonstrated.",
            ),
            (
                KINDS[1],
                "Looming Circuit Validation",
                "Initial circuit-validation world, not biological escape prediction.",
            ),
        )
    ]


def load_scenario_sources():
    # Historical references establish model authority, never supply runtime events.
    replay_plant_artifact(BODY_ROOT / HISTORICAL_IDS["phase12b"])
    sensory_path = SENSORY_ROOT / HISTORICAL_IDS["phase7o"]
    load_execution_artifact(sensory_path)
    replay_sensory_dnp01_motor_artifact(
        MOTOR_ROOT / HISTORICAL_IDS["phase8c"], sensory_path, "reference_bilateral"
    )
    p, coverage, manifest, source, circuit, grid = _inputs()[0]
    population, _, execution = _assert_sources(
        p, coverage, manifest, source, circuit, grid
    )
    model = execution["config"]
    if (
        model["sensory_model"]["tau_sens_ms"] != 1.0
        or model["sensory_model"]["gain"] != 1.0
        or model["transfer_model"]["k_transfer_mveq_per_state"] != 1.0
    ):
        raise ValueError("pinned sensory model parameters changed")
    target, target_reference = _target_contract()
    proxy = replay_proxy_artifact(DEFAULT_PROXY_ARTIFACT)
    rows = tuple(population["result"]["bodies"])
    if (
        len(rows) != 311
        or [r["body_id"] for r in rows] != population["result"]["body_ids"]
    ):
        raise ValueError("canonical sensory population changed")
    by_body = {row["body_id"]: [] for row in rows}
    for record in source.contract.records:
        if record.body_id in by_body:
            by_body[record.body_id].append(record)
    summaries = {r.body_id: r for r in source.contract.summaries}
    graph = SimulationGraph(
        candidate_identifier=circuit.candidate.identifier,
        candidate_version=circuit.candidate.version,
        dataset=circuit.provenance.dataset,
        graph_scope_id=PHASE7F_READOUT_SCOPE_ID,
        nodes=tuple(circuit.neurons_by_body_id[i] for i in (10001, 10010)),
        edges=(),
        circuit_integrity=tuple(circuit.integrity.sha256_by_file),
    )
    lif = _reference_lif_config(0.1)
    LIFSimulator(graph, lif)  # retain graph/config authority validation
    return {
        "rows": rows,
        "records": {i: tuple(sorted(r)) for i, r in by_body.items()},
        "summaries": summaries,
        "grid": grid,
        "graph": graph,
        "lif": lif,
        "routes": _routes(population, source, circuit),
        "target": target,
        "proxy": proxy.contract["result"],
        "identity": {
            "historical_model_references_not_runtime_input": dict(HISTORICAL_IDS),
            "population_artifact_id": p.artifact_id,
            "coverage_artifact_id": coverage.artifact_id,
            "execution_manifest_id": manifest.artifact_id,
            "column_source": copy.deepcopy(p.config["source_contract_identity"])
            if "source_contract_identity" in p.config
            else canonical_sha256(source.contract.to_dict()),
            "target_contract": target_reference,
            "proxy_artifact_id": proxy.artifact_id,
            "lif_model": lif.to_dict(),
            "motor_model": TTMnIntegratorConfig().to_dict(),
            "electrical_model": electrical_config().payload(),
            "activation_model": activation_config().payload(),
            "body_model": plant_config().payload(),
            "threshold_dimensionless": REFERENCE_THRESHOLD_DIMENSIONLESS,
            "actuator_action": ACTION,
        },
    }


def project_world(config, body, object_position):
    if any(not _finite(v) for v in (*body, *object_position)):
        raise ValueError("nonfinite authoritative geometry")
    dx, dz = object_position[0] - body[0], object_position[1] - body[1]
    distance = math.hypot(dx, dz)
    if dz <= 0 or not math.isfinite(distance) or distance <= 0:
        raise ValueError("unsupported behind-body/nonpositive projection geometry")
    angle = angular_half_size(config.radius_world_eq, distance)
    radius = math.floor(
        config.payload()["projection"]["angular_to_lattice_scale"] * angle
    )
    if type(radius) is not int or radius < 0:
        raise ValueError("invalid projected lattice radius")
    return {
        "relative_x_world_eq": dx,
        "relative_z_world_eq": dz,
        "relative_distance_world_eq": distance,
        "half_angle": angle,
        "lattice_radius": radius,
    }


def exposure_vector(config, body, object_position, sources):
    if config.kind == KINDS[0]:
        return None, [], [0.0] * 311
    geometry = project_world(config, body, object_position)
    stimulus = RelativeColumnStimulus(
        "scenario_looming", "R", 23, 9, config.dt_ms, (geometry["lattice_radius"],)
    )
    active = active_column_set(stimulus, sources["grid"], geometry["lattice_radius"])
    exposures = [
        compute_body_exposure(
            sources["records"][row["body_id"]],
            sources["summaries"][row["body_id"]],
            stimulus,
            frozenset(active),
        )["column_overlap_fraction"]
        for row in sources["rows"]
    ]
    if any(not _finite(v) or not 0 <= v <= 1 for v in exposures):
        raise ValueError("invalid sensory exposure")
    return geometry, [list(c) for c in active], exposures


class DownstreamRuntime:
    """Scenario-owned event composition without production injection options."""

    def __init__(self, execution_id, config, sources):
        self.execution_id, self.config, self.sources = execution_id, config, sources
        self.motor, self.electrical = [0.0, 0.0], [0.0, 0.0]
        self.next_step = 0
        self.ledgers = {
            key: []
            for key in (
                "motor_inputs",
                "motor_outputs",
                "dispatches",
                "receipts",
                "electrical_inputs",
            )
        }

    def advance(self, spikes, step):
        if step != self.next_step:
            raise ValueError("downstream boundaries must be contiguous")
        if any(s.step != step for s in spikes) or len(
            {s.body_id for s in spikes}
        ) != len(spikes):
            raise ValueError("spikes must be distinct events at this boundary")
        self.next_step += 1
        model, electrical = TTMnIntegratorConfig(), electrical_config()
        inputs = _map_motor_inputs(
            spikes,
            dt_ms=self.config.dt_ms,
            steps=self.config.interval_count,
            model=model,
        )
        for value in inputs:
            parent = next(s for s in spikes if s.body_id == value.source_body_id)
            record = {
                "schema_version": "scenario_motor_input_v1",
                "parent_dnp01_event_id": canonical_sha256(
                    {"scenario_execution_id": self.execution_id, **asdict(parent)}
                ),
                "scenario_execution_id": self.execution_id,
                **value.to_dict(),
            }
            self.ledgers["motor_inputs"].append(
                {"event_id": canonical_sha256(record), **record}
            )
        counts = [0, 0]
        for index, (body, side) in enumerate(((800146, "R"), (804642, "L"))):
            mapped = [v for v in inputs if v.target_body_id == body]
            previous = self.motor[index]
            current = ttmn_boundary_step(
                previous,
                len(mapped),
                math.exp(-self.config.dt_ms / model.tau_motor_ms),
                model.event_gain,
            )
            self.motor[index] = current
            if step and threshold_crossed(
                previous, current, REFERENCE_THRESHOLD_DIMENSIONLESS
            ):
                parent_ids = [
                    canonical_sha256(
                        {"scenario_execution_id": self.execution_id, **asdict(s)}
                    )
                    for s in spikes
                    if MOTOR_PATHWAY_EVIDENCE.target_by_source[s.body_id] == body
                ]
                event = {
                    "schema_version": "scenario_ttmn_output_event_v1",
                    "scenario_execution_id": self.execution_id,
                    "parent_dnp01_event_ids": parent_ids,
                    "motor_neuron_body_id": body,
                    "neural_side": side,
                    "step": step,
                    "time_ms": step * self.config.dt_ms,
                    "previous_state": previous,
                    "state": current,
                    "threshold_dimensionless": REFERENCE_THRESHOLD_DIMENSIONLESS,
                    "provenance_kind": "SCENARIO_MODEL_DERIVED_TTMN_OUTPUT",
                }
                event = {"event_id": canonical_sha256(event), **event}
                dispatch = dispatch_runtime_output(event, self.sources["target"])
                receipt = receipt_runtime_dispatch(dispatch)
                token = token_runtime_receipt(receipt)
                for key, record in (
                    ("motor_outputs", event),
                    ("dispatches", dispatch),
                    ("receipts", receipt),
                    ("electrical_inputs", token),
                ):
                    self.ledgers[key].append(record)
                counts[index] = 1
            self.electrical[index] = electrical_boundary_step(
                self.electrical[index],
                counts[index],
                math.exp(-self.config.dt_ms / electrical.tau_effective_ms),
                electrical.event_scale_effective_mV_eq,
            )
        activation = activate_samples(self.electrical, activation_config())
        commands = {
            actuator_channel(body, side): value
            for (body, side), value in zip(
                ((800146, "R"), (804642, "L")), activation, strict=True
            )
        }
        if any(not _finite(v) for v in (*self.motor, *self.electrical)):
            raise ValueError("nonfinite downstream state")
        return {
            "ttmn_state": list(self.motor),
            "voltage_deviation_mV_eq": list(self.electrical),
            "proxy_voltage_mV_eq": [
                electrical.reference_voltage_mV_eq + u for u in self.electrical
            ],
            "activation_proxy": activation,
            "actuator_commands": commands,
        }


def run_closed_loop_scenario(
    config: ScenarioConfig,
    sources=None,
    *,
    geometry_guard=None,
    result_schema=RESULT_SCHEMA,
):
    """Shared causal runner; optional guard stops before exposure, never pads state.

    Historical configurations retain their strict schema and unguarded behavior.
    New experiment contracts own their geometry policy and result version.
    """
    sources = load_scenario_sources() if sources is None else sources
    configuration = {"scenario": config.payload(), "sources": sources["identity"]}
    enabled = configuration["scenario"]["stimulus_enabled"]
    termination = None
    execution_id = canonical_sha256(configuration)
    dt, count = config.dt_ms, config.interval_count
    body = (config.body_x_world_eq, config.body_z_world_eq)
    object_position = (config.object_x_world_eq, config.object_z_world_eq)
    sensory = np.zeros(311, dtype=np.float64)
    v = np.full(2, sources["lif"].rest_mv, dtype=np.float64)
    synaptic, refractory = np.zeros(2), np.zeros(2, dtype=np.int64)
    spikes, all_spikes = [], []
    downstream = DownstreamRuntime(execution_id, config, sources)
    (
        boundaries,
        sensory_states,
        exposures_by_boundary,
        membrane,
        synaptic_states,
        downstream_states,
        telemetry,
    ) = [], [], [], [], [], [], []
    drives, contributions, speeds = [], [], []
    ids = [r["body_id"] for r in sources["rows"]]
    for n in range(count + 1):
        if geometry_guard is not None:
            termination = geometry_guard(config, body, object_position, n)
            if termination is not None:
                break
        geometry, active, exposures = exposure_vector(
            config, body, object_position, sources
        )
        state = downstream.advance(spikes, n)
        boundary = {
            "step": n,
            "time_ms": n * dt,
            "x_world_eq": body[0],
            "z_world_eq": body[1],
            "object_enabled": enabled,
            "object_x_world_eq": object_position[0] if enabled else None,
            "object_z_world_eq": object_position[1] if enabled else None,
            "geometry": geometry,
            "active_columns": active,
        }
        boundaries.append(boundary)
        sensory_states.append(sensory.tolist())
        exposures_by_boundary.append(exposures)
        membrane.append(v.tolist())
        synaptic_states.append(synaptic.tolist())
        downstream_states.append(state)
        summaries = [
            {
                "neuron_type": typ,
                "side": side,
                "state_sum": sum(
                    float(sensory[i])
                    for i, row in enumerate(sources["rows"])
                    if (row["neuron_type"], row["side"]) == (typ, side)
                ),
            }
            for typ in ("LC4", "LPLC2")
            for side in ("L", "R")
        ]
        telemetry.append(
            {
                "step": n,
                "time_ms": n * dt,
                "body": {
                    "x_world_eq": body[0],
                    "z_world_eq": body[1],
                    "fixed_heading": "POSITIVE_Z",
                },
                "object": {
                    "x_world_eq": object_position[0],
                    "z_world_eq": object_position[1],
                }
                if enabled
                else None,
                "relative_distance_world_eq": geometry["relative_distance_world_eq"]
                if geometry
                else None,
                "lattice_radius": geometry["lattice_radius"] if geometry else None,
                "active_sensory_body_count": sum(e > 0 for e in exposures),
                "sensory_summaries": summaries,
                "dnp01_membrane_mv": v.tolist(),
                "dnp01_spike_body_ids": [s.body_id for s in spikes],
                "ttmn_state": state["ttmn_state"],
                "actuator_commands": state["actuator_commands"],
            }
        )
        if n == count:
            break
        drive, ledger = route_population_drive(
            dict(zip(ids, sensory.tolist(), strict=True)),
            sources["routes"],
            target_body_ids=(10001, 10010),
            active_source_ids=set(ids),
            k_transfer_mveq_per_state=1.0,
        )
        drives.append([drive[i] for i in (10001, 10010)])
        contributions.append(ledger)
        next_v, synaptic, thresholded = lif_interval_step(
            sources["lif"], v, synaptic, refractory, np.array(drives[-1])
        )
        spikes = []
        for index in thresholded.tolist():
            spike = make_spike_event(
                sources["graph"].nodes[index], index, n + 1, sources["lif"]
            )
            spikes.append(spike)
            all_spikes.append(
                {
                    "event_id": canonical_sha256(
                        {"scenario_execution_id": execution_id, **asdict(spike)}
                    ),
                    **asdict(spike),
                }
            )
            apply_spike_reset(sources["lif"], next_v, refractory, index)
        v = next_v
        sensory = np.array(
            [
                sensory_state_step(float(s), e, math.exp(-dt), 1.0)
                for s, e in zip(sensory, exposures, strict=True)
            ]
        )
        common, speed = common_mode_speed(
            state["actuator_commands"]["RIGHT_TTM_ACTUATOR"],
            state["actuator_commands"]["LEFT_TTM_ACTUATOR"],
            plant_config(),
        )
        speeds.append(
            {
                "step": n,
                "common_mode_drive": common,
                "forward_speed_world_eq_per_ms": speed,
            }
        )
        body = body_interval_step(*body, (n + 1) * dt - n * dt, speed)
        if enabled:
            object_position = (
                object_position[0] + dt * config.vx_world_eq_per_ms,
                object_position[1] + dt * config.vz_world_eq_per_ms,
            )
    movement = body != (config.body_x_world_eq, config.body_z_world_eq) or any(
        (b["x_world_eq"], b["z_world_eq"])
        != (config.body_x_world_eq, config.body_z_world_eq)
        for b in boundaries
    )
    environmental_change = any(
        e != exposures_by_boundary[0] for e in exposures_by_boundary[1:]
    )
    statuses = {
        "closed_loop_execution_completed": termination is None,
        "environment_affected_sensory_input": environmental_change,
        "body_state_feedback_wired": True,
        "body_state_feedback_realized": movement and enabled,
        "genuine_nonzero_actuation_occurred": any(
            any(v > 0 for v in s["actuator_commands"].values())
            for s in downstream_states
        ),
        "body_movement_occurred": movement,
    }
    result = {
        "schema_version": result_schema,
        "scenario_execution_id": execution_id,
        "scenario_kind": config.kind,
        "boundary_indices": [b["step"] for b in boundaries],
        "time_ms": [b["time_ms"] for b in boundaries],
        "world_body": boundaries,
        "sensory_identities": list(sources["rows"]),
        "sensory_state_by_boundary": sensory_states,
        "exposure_by_boundary": exposures_by_boundary,
        "dnp01_body_ids": [10001, 10010],
        "dnp01_membrane_mv": membrane,
        "dnp01_synaptic_mV_eq": synaptic_states,
        "dnp01_spikes": all_spikes,
        "dnp01_drive_by_interval": drives,
        "source_contributions_by_interval": contributions,
        "downstream_identities": [
            {"body_id": 800146, "side": "R"},
            {"body_id": 804642, "side": "L"},
        ],
        "proxy_ancestry": copy.deepcopy(sources["proxy"]),
        "downstream_state_by_boundary": downstream_states,
        "downstream_events": downstream.ledgers,
        "body_intervals": speeds,
        "telemetry": telemetry,
        "statuses": statuses,
        "provenance_kind": "EXPLORATORY_GENUINE_CLOSED_LOOP_SCENARIO",
    }
    if geometry_guard is not None:
        result["termination"] = termination or {
            "status": "COMPLETED_VALID_HORIZON",
            "step": count,
            "time_ms": count * dt,
            "reason": None,
            "attempted_boundary_state": None,
        }
    return {
        "config": configuration,
        "result": result,
        "result_id": canonical_sha256(result),
    }


def build_scenario_battery():
    sources = load_scenario_sources()
    runs = [run_closed_loop_scenario(ScenarioConfig(kind), sources) for kind in KINDS]
    config = {
        "schema_version": CONFIG_SCHEMA,
        "scenarios": [r["config"] for r in runs],
        "metadata": scenario_metadata(),
    }
    result = {"schema_version": RESULT_SCHEMA, "runs": runs}
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema_version": RESULT_SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, ch, rh]),
    }


def validate_scenario_battery(payload):
    expected = build_scenario_battery()
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError(
            "scenario world/config/state/ancestry differs from offline replay"
        )
    return expected
