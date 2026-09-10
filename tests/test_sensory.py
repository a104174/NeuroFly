"""Offline tests for deterministic, model-neutral looming geometry."""

import json
import math

import pytest

from neurofly.malecns.benchmarks import BENCHMARKS, SENSORY_BOUNDARY
from neurofly.malecns.errors import StimulusSpecificationError
from neurofly.malecns.sensory import LoomingStimulus, VisualPoint


def stimulus(velocity: float = 2.0) -> LoomingStimulus:
    return LoomingStimulus(
        object_radius_m=0.5,
        approach_velocity_m_s=velocity,
        initial_distance_m=10.0,
        center=VisualPoint(azimuth_rad=0.25, elevation_rad=-0.1),
    )


def test_looming_geometry_is_deterministic_and_unit_explicit() -> None:
    first = stimulus().sample(2.0)
    second = stimulus().sample(2.0)
    assert first == second
    assert first.distance_m == pytest.approx(6.0)
    assert first.angular_size_rad == pytest.approx(2 * math.atan2(0.5, 6.0))
    assert first.angular_expansion_velocity_rad_s == pytest.approx(
        2 * 0.5 * 2 / (6**2 + 0.5**2)
    )
    assert first.center.azimuth_rad == pytest.approx(0.25)
    assert first.approaching is True
    assert first.collided is False


def test_no_approach_has_zero_expansion_and_no_collision() -> None:
    sample = stimulus(0.0).sample(100.0)
    assert sample.distance_m == 10.0
    assert sample.time_to_collision_s is None
    assert sample.angular_expansion_velocity_rad_s == 0.0
    assert sample.approaching is False
    assert sample.collided is False


def test_receding_object_has_negative_expansion() -> None:
    sample = stimulus(-2.0).sample(2.0)
    assert sample.distance_m == 14.0
    assert sample.time_to_collision_s is None
    assert sample.angular_expansion_velocity_rad_s < 0
    assert sample.approaching is False


def test_collision_boundary_is_explicit_terminal_geometry() -> None:
    approaching = stimulus()
    at_collision = approaching.sample(5.0)
    after_collision = approaching.sample(7.0)
    assert at_collision.collided is True
    assert after_collision.collided is True
    assert at_collision.distance_m == 0.0
    assert at_collision.angular_size_rad == math.pi
    assert at_collision.angular_expansion_velocity_rad_s is None
    assert at_collision.time_to_collision_s == pytest.approx(5.0)
    assert after_collision.angular_size_rad == math.pi


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("object_radius_m", 0.0),
        ("object_radius_m", -1.0),
        ("initial_distance_m", 0.0),
        ("initial_distance_m", -1.0),
        ("approach_velocity_m_s", math.inf),
    ],
)
def test_invalid_physical_parameters_are_rejected(field, value) -> None:
    values = {
        "object_radius_m": 0.5,
        "approach_velocity_m_s": 2.0,
        "initial_distance_m": 10.0,
        "center": VisualPoint(0.0, 0.0),
    }
    values[field] = value
    with pytest.raises(StimulusSpecificationError):
        LoomingStimulus(**values)


def test_invalid_time_and_center_are_rejected() -> None:
    with pytest.raises(StimulusSpecificationError, match="time_s"):
        stimulus().sample(-1.0)
    with pytest.raises(StimulusSpecificationError, match="azimuth_rad"):
        VisualPoint(math.nan, 0.0)


def test_stimulus_serialization_contains_no_neural_fields() -> None:
    serialized = json.dumps(stimulus().sample(1.0).to_dict())
    assert "angular_size_rad" in serialized
    assert "membrane" not in serialized
    assert "current" not in serialized
    assert "firing" not in serialized
    assert "simulation_weight" not in serialized


def test_benchmarks_are_explicit_and_model_neutral() -> None:
    identifiers = {benchmark.identifier for benchmark in BENCHMARKS}
    assert identifiers == {
        "lplc2_localized_outward_selectivity",
        "lc4_lplc2_feature_separation",
        "dnp01_combined_integration",
    }
    serialized = repr(BENCHMARKS).lower()
    assert "membrane" not in serialized
    assert "synaptic conductance" not in serialized
    lplc2 = next(
        benchmark
        for benchmark in BENCHMARKS
        if benchmark.identifier == "lplc2_localized_outward_selectivity"
    )
    condition_ids = {condition.identifier for condition in lplc2.conditions}
    assert {"dark_loom", "dark_recede", "contraction"} <= condition_ids


def test_sensory_boundary_keeps_feature_evidence_distinct_from_mapping() -> None:
    assert SENSORY_BOUNDARY.candidate_identifier == "looming_giant_fiber_v1"
    assert SENSORY_BOUNDARY.dataset == "male-cns:v1.0"
    assert SENSORY_BOUNDARY.mapping_status == (
        "MaleCNS per-neuron visual mapping not established"
    )
    assert {
        association.target_population
        for association in SENSORY_BOUNDARY.feature_associations
    } == {"LC4", "LPLC2"}
    assert all(
        "not a MaleCNS per-body map" in association.classification
        for association in SENSORY_BOUNDARY.feature_associations
    )
