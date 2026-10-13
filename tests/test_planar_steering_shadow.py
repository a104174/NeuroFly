"""Analytical engineering controls; never fixtures for a scientific API."""

import copy
import json
import math
from dataclasses import asdict, replace

import pytest

from neurofly import exploratory_course_control as course
from neurofly import planar_motion_observation as observation
from neurofly import planar_steering_validation as model
from neurofly.orientation_to_horizontal_motion import (
    ObservationInterval,
    OrientationBoundary,
    WorldReference,
)
from neurofly.orientation_to_horizontal_motion import (
    observe_interval as orientation_observation,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)


@pytest.fixture(scope="module")
def protocol():
    return observation.load_preregistration()


@pytest.fixture(scope="module")
def components(protocol):
    return model.load_sources(protocol)[0]


@pytest.fixture(scope="module")
def artifact():
    return model.build_shadow_artifact()


def geometry(protocol, name="SYMMETRIC"):
    return observation.VisualGeometry(
        tuple(observation.Landmark(**v) for v in protocol["geometries"][name])
    )


def poses(*, dx=0.0, dz=0.0, dh=0.0, dt=0.1):
    return (
        observation.PoseBoundary(0, 0, 0, 0, 0),
        observation.PoseBoundary(1, dt, dx, dz, dh),
    )


def runs(artifact):
    return {r["condition_id"]: r for r in artifact["result"]["runs"]}


def test_preregistration_identity_and_declared_authorities(protocol, artifact):
    # These are recorded declarations, not independent evidence of chronology.
    assert canonical_sha256(protocol) == observation.PREREGISTRATION_ID
    assert protocol["frozen_before_operator_implementation"]
    assert not protocol["output_based_parameter_selection"]
    assert protocol["stage_a"]["stage_b_permitted"]
    assert len(protocol["conditions"]) == 12
    config = artifact["config"]
    assert config["preregistration"] == protocol
    assert config["random_policy"] == "NONE" and config["seed"] is None
    assert set(artifact["result"]["target_order"][i]["body_id"] for i in range(2)) == {
        11215,
        12069,
    }
    assert {n["body_id"] for n in artifact["result"]["source_order"]} == {
        10015,
        10016,
        10023,
        10034,
        10181,
        10419,
    }
    assert len(artifact["result"]["selected_routes"]) == 6
    assert artifact["result"]["controls"]["all_pass"]


@pytest.mark.parametrize("dh", [0.001, -0.001])
def test_rotation_sign_and_exact_course_reduction(protocol, dh):
    before, after = poses(dh=dh)
    result = observation.observe_interval(geometry(protocol), before, after)
    previous = orientation_observation(
        ObservationInterval(
            WorldReference("WORLD_FIXED_HEADING_ZERO", 0),
            OrientationBoundary(0, 0, 0),
            OrientationBoundary(1, 0.1, dh),
        )
    )
    assert result.sides == previous.sides
    assert result.sides.right == -50 * dh / 0.1
    assert result.sides.left == 50 * dh / 0.1
    assert result.prescribed_cause == "ROTATION"


@pytest.mark.parametrize("dx,dz", [(0, 0.1), (0, -0.1), (0.1, 0), (-0.1, 0)])
@pytest.mark.parametrize("name", ["SYMMETRIC", "ASYMMETRIC"])
def test_translation_against_independent_endpoint_bearings(protocol, dx, dz, name):
    world = geometry(protocol, name)
    result = observation.observe_interval(world, *poses(dx=dx, dz=dz, dt=20))
    for sample in result.samples:
        landmark = sample.landmark
        shift = math.atan2(
            landmark.x_world_eq - dx, landmark.z_world_eq - dz
        ) - math.atan2(landmark.x_world_eq, landmark.z_world_eq)
        expected = 50 * shift / math.tau / 20 * (1 if landmark.side == "R" else -1)
        assert sample.normalized_side_descriptor == pytest.approx(expected, abs=1e-12)
        assert not sample.clipped
    assert result.prescribed_cause == "TRANSLATION"
    if dx == 0 and name == "SYMMETRIC":
        assert result.sides.right == result.sides.left
        assert (result.sides.right > 0) == (dz > 0)
    if dx > 0:
        assert result.sides.right < 0 < result.sides.left
    if dx < 0:
        assert result.sides.left < 0 < result.sides.right


def test_neutral_observation_is_exact_zero(protocol):
    result = observation.observe_interval(geometry(protocol), *poses())
    assert result.sides.right == result.sides.left == 0
    assert all(
        s.world_bearing_shift_rad_model == s.relative_shift_eq == 0
        for s in result.samples
    )
    assert result.prescribed_cause == "STATIONARY"


def test_rigid_coordinate_invariance(protocol):
    angle, tx, tz = 0.7, 3.0, -2.0

    def transform(x, z):
        return math.cos(angle) * x + math.sin(angle) * z + tx, -math.sin(
            angle
        ) * x + math.cos(angle) * z + tz

    world = geometry(protocol, "ASYMMETRIC")
    a = observation.PoseBoundary(0, 0, 0.01, 0.02, 0.03)
    b = observation.PoseBoundary(1, 0.1, 0.012, 0.023, 0.0301)
    transformed_world = observation.VisualGeometry(
        tuple(
            observation.Landmark(
                point.id, point.side, *transform(point.x_world_eq, point.z_world_eq)
            )
            for point in world.landmarks
        )
    )
    transformed_poses = [
        observation.PoseBoundary(
            p.index,
            p.time_ms,
            *transform(p.x_world_eq, p.z_world_eq),
            p.heading_eq + angle / math.tau,
        )
        for p in (a, b)
    ]
    original = observation.observe_interval(world, a, b)
    transformed = observation.observe_interval(transformed_world, *transformed_poses)
    assert transformed.sides.right == pytest.approx(original.sides.right, abs=1e-12)
    assert transformed.sides.left == pytest.approx(original.sides.left, abs=1e-12)


def test_branch_seam_and_singularity_are_distinct():
    world = observation.VisualGeometry(
        (observation.Landmark("R", "R", 0, -4), observation.Landmark("L", "L", -2, 4))
    )
    a = observation.PoseBoundary(0, 0, -0.01, 0, 0)
    b = observation.PoseBoundary(1, 1, 0.01, 0, 0)
    sample = observation.observe_interval(world, a, b).samples[0]
    assert sample.world_bearing_before_rad_model > 3
    assert sample.world_bearing_after_rad_model < -3
    assert abs(sample.world_bearing_shift_rad_model) < 0.01


def test_translation_and_rotation_can_have_the_same_descriptors(protocol):
    world = geometry(protocol)
    a = observation.PoseBoundary(0, 0, -0.05, 0, 0)
    b = observation.PoseBoundary(1, 20, 0.05, 0, 0)
    translated = observation.observe_interval(world, a, b)
    # Independent endpoint geometry, not an output of the operator under test:
    # R bearing decreases from atan2(2.05,4) to atan2(1.95,4).
    # L has the same decrement by reflection about X=0.
    dh = (math.atan2(2.05, 4) - math.atan2(1.95, 4)) / math.tau
    rotated = observation.observe_interval(world, *poses(dh=dh, dt=20))
    expected = 50 * dh / 20
    assert translated.sides.right == pytest.approx(-expected, abs=1e-12)
    assert translated.sides.left == pytest.approx(expected, abs=1e-12)
    assert translated.prescribed_cause == "TRANSLATION"
    assert rotated.prescribed_cause == "ROTATION"
    assert translated.sides.right == pytest.approx(rotated.sides.right, abs=1e-12)
    assert translated.sides.left == pytest.approx(rotated.sides.left, abs=1e-12)


def test_mixed_motion_against_independent_relative_endpoint_bearings(protocol):
    """Test-only input: beta=atan2(X,Z)-2*pi*h, completed interval [7,8]."""
    before = observation.PoseBoundary(7, 7, 0, 0, 0.02)
    after = observation.PoseBoundary(8, 27, 0.1, 0.2, 0.021)
    result = observation.observe_interval(geometry(protocol), before, after)
    assert result.before_index == 7 and result.available_boundary_index == 8
    assert result.dt_ms == 20
    assert result.translation_increment_world_eq == (0.1, 0.2)
    assert result.heading_increment_eq == pytest.approx(0.001, abs=1e-15)
    assert result.prescribed_cause == "MIXED"
    for sample in result.samples:
        x, z = sample.landmark.x_world_eq, sample.landmark.z_world_eq
        beta_before = math.atan2(x, z) - math.tau * 0.02
        beta_after = math.atan2(x - 0.1, z - 0.2) - math.tau * 0.021
        # No branch seam for these explicit values. Float64 tolerance is 1e-12.
        shift = (beta_after - beta_before) / math.tau
        rate = shift / 20
        expected = 50 * rate * (1 if sample.landmark.side == "R" else -1)
        assert sample.relative_shift_eq == pytest.approx(shift, abs=1e-12)
        assert sample.raw_motion_eq_per_ms == pytest.approx(rate, abs=1e-12)
        assert sample.bounded_side_descriptor == pytest.approx(expected, abs=1e-12)
        assert not sample.clipped
    assert result.sides.right < 0 < result.sides.left


def test_clipping_can_erase_distinct_geometric_observations(protocol):
    first = observation.observe_interval(geometry(protocol), *poses(dh=0.01))
    second = observation.observe_interval(geometry(protocol), *poses(dh=0.02))
    assert first.sides == second.sides
    assert first.sides.right == -1 and first.sides.left == 1
    for a, b in zip(first.samples, second.samples, strict=True):
        assert a.relative_shift_eq == -0.01 and b.relative_shift_eq == -0.02
        assert a.raw_motion_eq_per_ms == pytest.approx(-0.1, abs=1e-12)
        assert b.raw_motion_eq_per_ms == pytest.approx(-0.2, abs=1e-12)
        sign = -1 if a.landmark.side == "R" else 1
        assert a.normalized_side_descriptor == 5 * sign
        assert b.normalized_side_descriptor == 10 * sign
        assert a.clipped and b.clipped


@pytest.mark.parametrize("dt,dh", [(0.1, 0.01), (0.1, -0.01)])
def test_clipping_is_explicit_and_finite(protocol, dt, dh):
    result = observation.observe_interval(geometry(protocol), *poses(dh=dh, dt=dt))
    for sample in result.samples:
        assert abs(sample.normalized_side_descriptor) == 5
        assert abs(sample.bounded_side_descriptor) == 1
        assert sample.clipped


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), True])
def test_nonfinite_or_boolean_coordinates_fail(bad):
    with pytest.raises(ValueError):
        observation.PoseBoundary(0, 0, bad, 0, 0)
    with pytest.raises(ValueError):
        observation.Landmark("R", "R", 0, bad)


@pytest.mark.parametrize(
    "index,time,heading",
    [(1, 0, 0), (1, -1, 0), (2, 0.1, 0), (1, 0.1, 0.5), (1, 0.1, -0.5)],
)
def test_order_time_and_half_cycle_domain(protocol, index, time, heading):
    with pytest.raises(ValueError):
        observation.observe_interval(
            geometry(protocol),
            observation.PoseBoundary(0, 0, 0, 0, 0),
            observation.PoseBoundary(index, time, 0, 0, heading),
        )


def test_invalid_frame_contract_and_swept_geometry(protocol):
    with pytest.raises(ValueError):
        observation.VisualGeometry(geometry(protocol).landmarks, frame="UNKNOWN")
    with pytest.raises(ValueError):
        observation.PlanarObservationContract(reference_window_ms=51)
    with pytest.raises(ValueError):
        observation.VisualGeometry(
            (observation.Landmark("A", "R", 0, 4), observation.Landmark("B", "L", 0, 4))
        )
    with pytest.raises(ValueError, match="singular"):
        observation.observe_interval(geometry(protocol), *poses(dx=2, dz=4))
    world = observation.VisualGeometry(
        (observation.Landmark("R", "R", 0, 4), observation.Landmark("L", "L", -2, 4))
    )
    with pytest.raises(ValueError, match="singular"):
        observation.observe_interval(
            world,
            observation.PoseBoundary(0, 0, -1, 4, 0),
            observation.PoseBoundary(1, 1, 1, 4, 0),
        )
    with pytest.raises(ValueError, match="projection"):
        observation.observe_interval(geometry(protocol), *poses(dx=1e308))
    with pytest.raises(ValueError):
        observation.PoseBoundary(0, 0, 10**1000, 0, 0)


def test_preregistration_mutation_and_missing_authority_fail(tmp_path, protocol):
    changed = copy.deepcopy(protocol)
    changed["operator"]["reference_window_ms"] = 100
    file = tmp_path / "modified.json"
    file.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="authority"):
        observation.load_preregistration(file)
    with pytest.raises(ValueError):
        observation.load_preregistration(tmp_path / "absent.json")
    with pytest.raises(ValueError):
        model.prescribed_inputs(changed)


def test_all_boundaries_preserve_inputs_and_follow_frozen_kernels(
    protocol, components, artifact
):
    inputs = {r.condition_id: r for r in model.prescribed_inputs(protocol)}
    for run in artifact["result"]["runs"]:
        r = inputs[run["condition_id"]]
        rows = run["boundaries"]
        assert len(rows) == 501
        for n, row in enumerate(rows):
            assert row["pose"] == asdict(r.poses[n])
            assert row["time_ms"] == n * 0.1
            assert row["readout"]["classification"] == "SHADOW_ONLY"
            assert not row["readout"]["applied_to_pose"]
            if n == 0:
                assert row["observation"] is None
            else:
                assert row["observation"] == asdict(
                    observation.observe_interval(r.geometry, r.poses[n - 1], r.poses[n])
                )
            if n == 500:
                assert row["readout"]["proposed_increment_eq"] is None
                assert row["route_contributions"] is row["target_drives"] is None
                continue
            following = rows[n + 1]
            kernel = components.neural_contract
            drives = course.neural.route_contributions(
                dict(
                    zip(
                        [i["body_id"] for i in kernel["source_identities"]],
                        row["hs_states"],
                        strict=True,
                    )
                ),
                kernel["selected_routes"],
                kernel["target_identities"],
                kernel["transfer"]["coefficient"],
            )[1]
            assert row["target_drives"] == tuple(drives)
            expected_hs = tuple(
                course.neural.proxy_step(
                    state,
                    row["sensory_descriptor"][
                        "right" if source["side"] == "R" else "left"
                    ],
                    0.1,
                    kernel["source_model"]["tau_ms"],
                )
                for source, state in zip(
                    kernel["source_identities"], row["hs_states"], strict=True
                )
            )
            expected_dn = tuple(
                course.neural.proxy_step(
                    state, drive, 0.1, kernel["target_model"]["tau_ms"]
                )
                for state, drive in zip(row["dnp15_states"], drives, strict=True)
            )
            assert following["hs_states"] == expected_hs
            assert following["dnp15_states"] == expected_dn
            delta, drive, proposal = course.embodiment.integrate_orientation(
                [0, following["time_ms"] - row["time_ms"]],
                [list(row["dnp15_states"])] * 2,
                components.embodiment_contract,
            )
            assert row["bilateral_differential"] == delta[0]
            assert row["readout"]["computed_yaw_drive_eq"] == drive[0]
            assert row["readout"]["proposed_increment_eq"] == proposal[-1]


def test_latency_controls_and_response_signs(artifact):
    result = runs(artifact)
    rows = result["ROTATION_POSITIVE"]["boundaries"]
    assert rows[1]["sensory_descriptor"]["right"] < 0
    assert rows[1]["hs_states"] == (0.0,) * 6
    assert rows[2]["hs_states"][0] < 0
    assert rows[2]["dnp15_states"] == (0.0,) * 2
    assert rows[3]["readout"]["computed_yaw_drive_eq"] < 0
    for positive, negative in zip(
        rows, result["ROTATION_NEGATIVE"]["boundaries"], strict=True
    ):
        assert positive["hs_states"] == tuple(-v for v in negative["hs_states"])
        assert positive["bilateral_differential"] == -negative["bilateral_differential"]
    sym = result["TRANSLATION_Z_POSITIVE_SYMMETRIC"]
    assert sym["diagnostics"]["peak_abs_dnp15"] > 0
    assert (
        sym["diagnostics"]["max_differential"]
        == sym["diagnostics"]["min_differential"]
        == 0
    )
    assert artifact["result"]["controls"]["all_pass"]
    assert all(r["diagnostics"]["clipped_intervals"] == 0 for r in result.values())


def test_unsupported_intervention_and_kernel_mutation_fail(protocol, components):
    inputs = model.prescribed_inputs(protocol)[0]
    with pytest.raises(ValueError):
        model.run_condition(
            replace(inputs, control="BIOLOGICAL_ABLATION"), protocol, components
        )
    changed = copy.deepcopy(components)
    changed.neural_contract["source_model"]["tau_ms"] = 6
    with pytest.raises(ValueError, match="unsupported"):
        model.run_condition(inputs, protocol, changed)
    with pytest.raises(ValueError):
        replace(inputs, poses=inputs.poses[:-1])
    with pytest.raises(ValueError):
        replace(inputs, poses=(inputs.poses[1], inputs.poses[0], *inputs.poses[2:]))


def test_complete_configuration_and_exact_reproducibility(artifact):
    again = model.build_shadow_artifact()
    assert canonical_json_bytes(artifact) == canonical_json_bytes(again)
    assert artifact["config_sha256"] == canonical_sha256(artifact["config"])
    assert artifact["result_sha256"] == canonical_sha256(artifact["result"])
    assert artifact["config"]["source_definitions"]["authority_documents_utf8"]
    assert len(artifact["config"]["prescribed_inputs"]) == 12
    for r in artifact["config"]["prescribed_inputs"]:
        assert len(r["poses"]) == 501


@pytest.mark.parametrize(
    "kind",
    [
        "pose",
        "neural",
        "null",
        "identity",
        "time",
        "geometry",
        "boundary_count",
        "source_identity",
        "random_policy",
        "application",
    ],
)
def test_semantic_tampering_fails_even_after_rehash(artifact, kind):
    changed = copy.deepcopy(artifact)
    row = changed["result"]["runs"][0]["boundaries"][0]
    if kind == "pose":
        row["pose"]["x_world_eq"] = 1
    elif kind == "neural":
        row["bilateral_differential"] = 0.1
    elif kind == "null":
        row["observation"] = {}
    elif kind == "identity":
        changed["config"]["experiment_id"] = "EXPLORATORY_COURSE_CONTROL"
    elif kind == "time":
        row["time_ms"] = 0.1
    elif kind == "geometry":
        # Valid coordinates, but incompatible with the registered geometry.
        changed["config"]["prescribed_inputs"][0]["geometry"]["landmarks"][0][
            "x_world_eq"
        ] = 2.1
    elif kind == "boundary_count":
        changed["result"]["runs"][0]["boundaries"].pop()
    elif kind == "source_identity":
        changed["result"]["source_order"][0]["body_id"] = 10001
    elif kind == "random_policy":
        changed["config"]["random_policy"] = "RANDOM_WALK"
    elif kind == "application":
        changed["result"]["readout_application"] = "BODY_FEEDBACK"
        row["readout"]["classification"] = "APPLIED"
        row["readout"]["applied_to_pose"] = True
    changed["config_sha256"] = canonical_sha256(changed["config"])
    changed["result_sha256"] = canonical_sha256(changed["result"])
    changed["artifact_id"] = canonical_sha256(
        [model.ARTIFACT_SCHEMA, changed["config_sha256"], changed["result_sha256"]]
    )
    with pytest.raises(ValueError, match="replay"):
        model.validate_shadow_artifact(changed)


def test_shadow_readouts_never_change_independently_prescribed_poses(
    protocol, components, artifact
):
    # Verify recipes without using prescribed_inputs as the expected-value oracle.
    by_condition = runs(artifact)
    for condition in protocol["conditions"]:
        rows = by_condition[condition["id"]]["boundaries"]
        dx, dz = condition["displacement_world_eq"]
        dh = condition["heading_change_eq"]
        for n, row in enumerate(rows):
            fraction = n / 200 if n < 200 else 1
            assert row["pose"] == {
                "index": n,
                "time_ms": n * 0.1,
                "x_world_eq": dx * fraction,
                "z_world_eq": dz * fraction,
                "heading_eq": dh * fraction,
                "source": "ENGINEERING_PRESCRIBED_POSE",
            }
            assert row["readout"]["classification"] == "SHADOW_ONLY"
            assert row["readout"]["applied_to_pose"] is False
    intact = by_condition["TRANSLATION_Z_POSITIVE_ASYMMETRIC"]["boundaries"]
    disabled = by_condition["READOUT_DISABLED_TRANSLATION_Z_POSITIVE_ASYMMETRIC"][
        "boundaries"
    ]
    assert any(r["readout"]["enabled_shadow_drive_eq"] != 0 for r in intact)
    assert all(r["readout"]["enabled_shadow_drive_eq"] == 0 for r in disabled)
    for a, b in zip(intact, disabled, strict=True):
        for field in (
            "pose",
            "observation",
            "sensory_descriptor",
            "hs_states",
            "dnp15_states",
            "bilateral_differential",
        ):
            assert a[field] == b[field]
        for field in ("computed_yaw_drive_eq", "proposed_increment_eq"):
            assert a["readout"][field] == b["readout"][field]
    # The runner must not mutate even the immutable input supplied by its caller.
    inputs = next(
        r
        for r in model.prescribed_inputs(protocol)
        if r.condition_id == "TRANSLATION_Z_POSITIVE_ASYMMETRIC"
    )
    original = canonical_json_bytes(asdict(inputs))
    model.run_condition(inputs, protocol, components)
    assert canonical_json_bytes(asdict(inputs)) == original


def test_export_reopen_manifest_and_no_repository_output(tmp_path, artifact):
    path = model.generate_shadow_artifact(tmp_path)
    assert path.name == artifact["artifact_id"]
    assert canonical_json_bytes(
        model.replay_shadow_artifact(path)
    ) == canonical_json_bytes(artifact)
    assert model.generate_shadow_artifact(tmp_path) == path
    with pytest.raises(ValueError, match="outside"):
        model.generate_shadow_artifact(model.REPO_ROOT / "data/derived/new-shadow")
    manifest = path / "manifest.json"
    manifest.write_text("{}\n")
    with pytest.raises(ValueError):
        model.replay_shadow_artifact(path)
    with pytest.raises(ValueError):
        model.replay_shadow_artifact(tmp_path / "missing")
