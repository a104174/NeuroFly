"""Independent geometric observation, never a candidate closed-loop run."""

import ast
import copy
import hashlib
import json
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path

import pytest

from neurofly import orientation_to_horizontal_motion as model
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def contract_record():
    return json.loads(model.CONTRACT_PATH.read_bytes())


def interval(a=0, b=0, dt=1, heading=0, index=0, start=0):
    return model.ObservationInterval(
        model.WorldReference("WORLD_FIXED_HEADING_ZERO", heading),
        model.OrientationBoundary(index, start, a),
        model.OrientationBoundary(index + 1, start + dt, b),
    )


def test_frozen_gate_preregistration_and_canonical_identity(contract_record):
    assert canonical_sha256(contract_record) == model.CONTRACT_ID
    assert contract_record["schema"] == model.CONTRACT_SCHEMA
    assert contract_record["preregistration_schema"] == (
        "orientation_to_horizontal_motion_preregistration_v1"
    )
    assert contract_record["frozen_before_numerical_validation"]
    assert not contract_record["output_driven_design"]
    assert not contract_record["closed_loop_executed"]
    assert contract_record["stage_a"]["decision"] == (
        "ORIENTATION_TO_MOTION_OBSERVATION_IDENTIFIABLE"
    )
    assert contract_record["stage_a"]["classification"] == (
        "GEOMETRIC_OBSERVATION_REQUIRES_BOUNDED_EXPLORATORY_ASSUMPTIONS"
    )
    assert contract_record["stage_a"]["stage_b_permitted"]
    assert model.load_contract().contract_id == model.CONTRACT_ID
    assert len({layer["id"] for layer in contract_record["layers"]}) == 5
    assert not contract_record["operator"]["condition_specific_normalization"]


def test_frozen_authorities_without_running_models(contract_record):
    authorities = contract_record["authorities"]
    for filename, inner, id_key, key in [
        ("neurofly_v1_scientific_status.json", "status", "status_id", "v1_status_id"),
        (
            "second_circuit_selection_gate.json",
            "selection",
            "selection_id",
            "phase24_selection_id",
        ),
        (
            "hs_dnp15_network_context_audit.json",
            "audit",
            "audit_id",
            "phase26_audit_id",
        ),
        (
            "dnp15_yaw_mapping_evidence_gate.json",
            "gate",
            "gate_id",
            "phase28_evidence_gate_id",
        ),
    ]:
        record = json.loads((ROOT / "docs/science" / filename).read_bytes())
        assert canonical_sha256(record[inner]) == record[id_key] == authorities[key]
    for filename, key in [
        (
            "hs_dnp15_neural_validation_preregistration.json",
            "phase25_preregistration_id",
        ),
        ("dnp15_exploratory_yaw_preregistration.json", "phase28_preregistration_id"),
    ]:
        record = json.loads((ROOT / "docs/science" / filename).read_bytes())
        assert canonical_sha256(record) == authorities[key]
    path = ROOT / "docs/science/horizontal_motion_neural_scenario_integration.md"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == (authorities["phase27_document_sha256"])
    )


@pytest.mark.parametrize("offset", [0, 0.25, -0.25, 10, -10])
def test_exact_zero_motion_and_static_offset(offset):
    result = model.observe_interval(interval(offset, offset))
    assert result.horizontal_view_shift_eq == 0
    assert result.raw_view_motion_eq_per_ms == 0
    assert result.global_horizontal_motion_eq == 0
    assert result.sides.right == result.sides.left == 0
    assert not result.clipped
    assert model.neutral_initial_descriptors() == model.SideDescriptors(0, 0)
    model.validate_observation(result)


def test_positive_negative_and_sign_reversal():
    positive = model.observe_interval(interval(0, 0.01))
    negative = model.observe_interval(interval(0, -0.01))
    assert positive.horizontal_view_shift_eq == -0.01
    assert positive.raw_view_motion_eq_per_ms == -0.01
    assert positive.global_horizontal_motion_eq == -0.5
    assert positive.sides.right == -0.5
    assert positive.sides.left == 0.5
    assert negative.global_horizontal_motion_eq == 0.5
    assert negative.sides.right == 0.5
    assert negative.sides.left == -0.5
    reversed_step = model.observe_interval(interval(0.01, 0))
    assert reversed_step.global_horizontal_motion_eq == 0.5


def test_world_reference_is_independent_and_common_frame_shift_invariant():
    original = model.observe_interval(interval(0, 0.125, dt=10, heading=0.25))
    shifted = model.observe_interval(interval(2, 2.125, dt=10, heading=2.25))
    assert original.relative_lift_before_eq == shifted.relative_lift_before_eq
    assert original.relative_lift_after_eq == shifted.relative_lift_after_eq
    assert original.relative_view_before_eq == shifted.relative_view_before_eq
    assert original.relative_view_after_eq == shifted.relative_view_after_eq
    assert original.global_horizontal_motion_eq == shifted.global_horizontal_motion_eq
    other = model.observe_interval(interval(0, 0.125, dt=10, heading=0.375))
    assert original.relative_view_before_eq != other.relative_view_before_eq
    assert original.global_horizontal_motion_eq == other.global_horizontal_motion_eq


def test_rate_like_descriptor_sample_rate_invariance():
    # Fixed rate .01 eq/ms, different interval lengths. Not physical velocity.
    values = [
        model.observe_interval(interval(0, 0.01 * dt, dt=dt)) for dt in [0.1, 0.5, 1, 2]
    ]
    assert all(r.global_horizontal_motion_eq == pytest.approx(-0.5) for r in values)
    assert len({r.horizontal_view_shift_eq for r in values}) == 4


def test_constant_rate_and_declared_synthetic_cases(contract_record):
    expected = {
        "ZERO_MOTION": [0],
        "STATIC_OFFSET": [0],
        "POSITIVE_STEP": [-0.5],
        "NEGATIVE_STEP": [0.5],
        "CONSTANT_RATE": [-0.5, -0.5],
        "REVERSAL": [-0.5, 0.5],
        "VIEW_WRAP_CROSSING": [-1],
        "SATURATION": [-1],
    }
    for case in contract_record["synthetic_cases"]:
        outputs = []
        for n in range(len(case["time_ms"]) - 1):
            r = model.observe_interval(
                interval(
                    case["body_eq"][n],
                    case["body_eq"][n + 1],
                    dt=case["time_ms"][n + 1] - case["time_ms"][n],
                    heading=case["world_eq"],
                    index=n,
                    start=case["time_ms"][n],
                )
            )
            assert r.available_boundary_index == n + 1
            model.validate_observation(r)
            outputs.append(r.global_horizontal_motion_eq)
        assert outputs == pytest.approx(expected[case["id"]])


def test_wrap_crossing_no_false_full_cycle_impulse():
    # Unwrapped endpoints cross the view seam; the wrapped view changes sign.
    r = model.observe_interval(interval(0.49, 0.51, dt=10))
    assert r.relative_view_before_eq == pytest.approx(-0.49)
    assert r.relative_view_after_eq == pytest.approx(0.49)
    assert r.horizontal_view_shift_eq == pytest.approx(-0.02)
    assert r.global_horizontal_motion_eq == pytest.approx(-0.1)
    assert not r.clipped
    inverse = model.observe_interval(interval(0.51, 0.49, dt=10))
    assert inverse.global_horizontal_motion_eq == pytest.approx(0.1)
    tie = model.observe_interval(interval(0.5, 0.5))
    assert tie.relative_view_before_eq == -0.5
    assert tie.global_horizontal_motion_eq == 0


def test_saturation_is_explicit_global_and_odd():
    a = model.observe_interval(interval(0, 0.1))
    b = model.observe_interval(interval(0, -0.1))
    assert a.normalized_unclipped == -5
    assert a.global_horizontal_motion_eq == -1
    assert b.normalized_unclipped == 5
    assert b.global_horizontal_motion_eq == 1
    assert a.clipped and b.clipped
    exact_bound = model.observe_interval(interval(0, 0.02))
    assert exact_bound.global_horizontal_motion_eq == -1
    assert not exact_bound.clipped  # No value changed at the saturation boundary.


def test_schema_units_causal_order_and_immutable_result():
    r = model.observe_interval(interval(0, 0.01, index=2, start=5))
    assert r.schema == "horizontal_motion_observation_v1"
    assert r.interval.before.index == 2
    assert r.available_boundary_index == r.interval.after.index == 3
    assert r.interval.before.time_ms == 5
    assert r.interval.after.time_ms == 6
    assert r.units.normalized == r.sides.units == "horizontal_motion_eq"
    assert r.units.body == "yaw_orientation_eq"
    assert r.units.raw_motion == "relative_view_eq_per_ms"
    assert "NOT_VISUAL_TRANSDUCTION" in r.status
    assert not {"neuron_id", "weight", "force", "torque", "x", "z"} & r.payload().keys()
    with pytest.raises(FrozenInstanceError):
        r.dt_ms = 5


def test_determinism_and_canonical_ordering():
    a, b = (
        model.observe_interval(interval(0, 0.01)),
        model.observe_interval(interval(0, 0.01)),
    )
    assert a == b and a.canonical_bytes() == b.canonical_bytes()
    assert a.result_sha256() == canonical_sha256(b.payload())
    reordered = dict(reversed(list(a.payload().items())))
    assert a.canonical_bytes() == canonical_json_bytes(reordered)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf"), True, "0"])
def test_nonfinite_or_non_numeric_coordinate_rejection(bad):
    with pytest.raises(model.ObservationError) as exc:
        model.OrientationBoundary(0, 0, bad)
    assert exc.value.code == model.ObservationErrorCode.INVALID_COORDINATE
    with pytest.raises(model.ObservationError) as exc:
        model.WorldReference("WORLD", bad)
    assert exc.value.code == model.ObservationErrorCode.INVALID_WORLD_REFERENCE


@pytest.mark.parametrize("dt", [0, -1, float("nan"), float("inf")])
def test_invalid_dt_is_error_not_neutral_or_clipping(dt):
    with pytest.raises(model.ObservationError) as exc:
        interval(0, 0.01, dt=dt)
    assert exc.value.code == model.ObservationErrorCode.INVALID_TIME_INTERVAL


@pytest.mark.parametrize("jump", [0.5, -0.5, 1, -1, 10, -10])
def test_ambiguous_alias_or_discontinuous_interval_rejected(jump):
    with pytest.raises(model.ObservationError) as exc:
        model.observe_interval(interval(0, jump))
    assert exc.value.code == (
        model.ObservationErrorCode.AMBIGUOUS_OR_DISCONTINUOUS_INTERVAL
    )
    with pytest.raises(model.ObservationError):
        model.observe_interval(interval(0.49, -0.49))  # Missing unwrapped winding.


def test_invalid_types_world_and_boundary_order():
    for name in ["", " ", " WORLD", None]:
        with pytest.raises(model.ObservationError) as exc:
            model.WorldReference(name, 0)
        assert exc.value.code == model.ObservationErrorCode.INVALID_WORLD_REFERENCE
    with pytest.raises(model.ObservationError):
        model.WorldReference("WORLD", 0, "another_schema")
    for index in [-1, True, 1.5]:
        with pytest.raises(model.ObservationError):
            model.OrientationBoundary(index, 0, 0)
    with pytest.raises(model.ObservationError):
        model.ObservationInterval(
            model.WorldReference("WORLD", 0),
            model.OrientationBoundary(0, 0, 0),
            model.OrientationBoundary(2, 1, 0),
        )
    with pytest.raises(model.ObservationError):
        model.ObservationInterval({}, model.OrientationBoundary(0, 0, 0), None)
    with pytest.raises(model.ObservationError):
        model.observe_interval({})


def test_overflow_rejected_not_saturated():
    with pytest.raises(model.ObservationError) as exc:
        model.observe_interval(interval(0, 0.1, dt=5e-324))
    assert exc.value.code == model.ObservationErrorCode.INVALID_COORDINATE
    with pytest.raises(model.ObservationError) as exc:
        model.observe_interval(interval(-1e308, -1e308, heading=1e308))
    assert exc.value.code == model.ObservationErrorCode.INVALID_COORDINATE


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("operator", "sign", "opposite sign"),
        ("operator", "reference_window_ms", 100),
        ("operator", "normalization", "per-condition"),
        ("operator", "equation_version", "v2"),
        ("coordinates", "period_eq", 2),
        ("coordinates", "wrap", "different convention"),
        ("temporal", "signal", "displacement only"),
        ("side_projection", "global_to_left", "left = global"),
        ("stage_a", "stage_b_permitted", False),
    ],
)
def test_material_semantics_change_hash_and_are_rejected(
    contract_record, tmp_path, section, key, value
):
    changed = copy.deepcopy(contract_record)
    changed[section][key] = value
    assert canonical_sha256(changed) != model.CONTRACT_ID
    path = tmp_path / "modified_contract.json"
    path.write_bytes(canonical_json_bytes(changed))
    with pytest.raises(model.ObservationError) as exc:
        model.load_contract(path)
    assert exc.value.code == model.ObservationErrorCode.CONTRACT_AUTHORITY_MISMATCH


def test_missing_malformed_contract_and_invalid_configuration(tmp_path):
    with pytest.raises(model.ObservationError):
        model.load_contract(tmp_path / "missing.json")
    path = tmp_path / "broken.json"
    path.write_text("not-json")
    with pytest.raises(model.ObservationError):
        model.load_contract(path)
    config = model.load_contract()
    for change in [
        {"period_eq": 0},
        {"reference_window_ms": -1},
        {"reference_window_ms": 100},
        {"contract_id": "other"},
        {"right_basis": -1},
    ]:
        with pytest.raises(model.ObservationError):
            replace(config, **change)


@pytest.mark.parametrize(
    "field,value",
    [
        ("horizontal_view_shift_eq", 0.2),
        ("global_horizontal_motion_eq", 0.9),
        ("raw_view_motion_eq_per_ms", 9),
        ("clipped", True),
        ("available_boundary_index", 99),
        ("contract_id", "forged"),
    ],
)
def test_result_mutation_rejected_even_with_new_result_hash(field, value):
    result = model.observe_interval(interval(0, 0.01))
    changed = replace(result, **{field: value})
    assert changed.result_sha256() != result.result_sha256()
    with pytest.raises(model.ObservationError):
        model.validate_observation(changed)


def test_phase28_trace_api_compatibility_only(contract_record):
    a = contract_record["authorities"]
    path = (
        ROOT
        / "data/derived/experiments/dnp15_exploratory_yaw_artifact_v1"
        / a["phase28_artifact_id"]
    )
    raw = (path / "orientation.json").read_bytes()
    manifest = json.loads((path / "manifest.json").read_bytes())
    assert (
        hashlib.sha256(raw).hexdigest()
        == manifest["files"]["orientation.json"]["sha256"]
    )
    source = json.loads(raw)
    assert source["artifact_id"] == a["phase28_artifact_id"]
    assert canonical_sha256(source["config"]) == a["phase28_config_sha256"]
    assert canonical_sha256(source["result"]) == a["phase28_result_sha256"]
    # No replay/simulation is invoked by this compatibility check: stored arrays
    # are accepted as completed geometry intervals, never sent back to neurons.
    times = source["result"]["time_ms"]
    assert len(times) == 501 and times[-1] == 50
    for run in source["result"]["runs"]:
        orientations = run["yaw_orientation_eq"]
        for n in range(len(times) - 1):
            output = model.observe_interval(
                interval(
                    orientations[n],
                    orientations[n + 1],
                    dt=times[n + 1] - times[n],
                    index=n,
                    start=times[n],
                )
            )
            assert -1 <= output.sides.right <= 1
            assert -1 <= output.sides.left <= 1
            assert output.available_boundary_index == n + 1


def test_no_neural_body_frontend_or_contact_dependency(monkeypatch):
    source = Path(model.__file__).read_text()
    imports = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }
    assert {name for name in imports if name and name.startswith("neurofly.")} == {
        "neurofly.ttm_g1_electrophysiology_observations"
    }
    assert all(
        token not in source for token in ["body_id", "ConnectsTo", "structural_count"]
    )
    assert "weight" not in {f.name for f in fields(model.WorldReference)}
    with pytest.raises(TypeError):
        model.WorldReference("WORLD", 0, weight=999)

    # These existing kernels must never be called by the new observation.
    from neurofly import dnp15_exploratory_yaw, hs_dnp15_neural_validation

    def forbidden(*args, **kwargs):
        pytest.fail("observation called a neural or embodiment executor")

    monkeypatch.setattr(hs_dnp15_neural_validation, "_execute", forbidden)
    monkeypatch.setattr(hs_dnp15_neural_validation, "proxy_step", forbidden)
    monkeypatch.setattr(dnp15_exploratory_yaw, "integrate_orientation", forbidden)
    assert model.observe_interval(interval(0, 0.01)).sides.right == -0.5


def test_claim_limits_no_physical_calibration_or_hidden_loop(contract_record):
    assert contract_record["world"]["no_texture_or_hemifield_geometry"]
    assert contract_record["temporal"]["no_same_boundary_algebraic_loop"]
    assert contract_record["coordinates"]["period_status"] == (
        "EXPLORATORY_BOUNDED_ASSUMPTION"
    )
    assert contract_record["operator"]["reference_status"] == (
        "EXPLORATORY_BOUNDED_ASSUMPTION"
    )
    assert contract_record["side_projection"]["status"] == (
        "EXPLORATORY_BOUNDED_ASSUMPTION"
    )
    assert (
        "Demonstrated closed-loop stabilization" in contract_record["forbidden_claims"]
    )
    assert contract_record["final_decision"] == (
        "OBSERVATION_OPERATOR_SPECIFIED_WITH_EXPLORATORY_NORMALIZATION"
    )
