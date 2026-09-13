"""Synthetic tests for the model-neutral MaleCNS spatial contract."""

import json
from dataclasses import FrozenInstanceError
from types import MappingProxyType, SimpleNamespace

import pytest

from neurofly.malecns.errors import MaleCNSValidationError
from neurofly.malecns.spatial import (
    MALECNS_EM_COORDINATE_FRAME,
    MALECNS_EM_COORDINATE_UNIT,
    MorphologyMode,
    NeuronSpatialRecord,
    SkeletonComponent,
    SkeletonLink,
    SkeletonLinkProvenance,
    SkeletonNode,
    SpatialEvidenceCategory,
    SpatialPoint,
    current_raw_spatial_record,
    validate_spatial_record_against_circuit,
)

SOURCE_HASH = "a" * 64


def _component(
    component_id: int = 0,
    *,
    offset: int = 0,
    provenance: SkeletonLinkProvenance = SkeletonLinkProvenance.RAW,
) -> SkeletonComponent:
    return SkeletonComponent(
        component_id=component_id,
        nodes=(
            SkeletonNode(1 + offset, SpatialPoint(10.25, 20.5, 30.75), 4.0),
            SkeletonNode(2 + offset, SpatialPoint(11.25, 21.5, 31.75), None),
        ),
        links=(SkeletonLink(2 + offset, 1 + offset, provenance),),
    )


def _record(**updates) -> NeuronSpatialRecord:
    values = {
        "body_id": 10001,
        "node_index": 0,
        "neuron_type": "DNp01",
        "side": "R",
        "components": (_component(),),
        "source_swc_sha256": SOURCE_HASH,
        "soma_location": SpatialPoint(37124.0, 22258.0, 36274.0),
    }
    values.update(updates)
    return current_raw_spatial_record(**values)


def test_raw_record_is_immutable_and_preserves_source_coordinates() -> None:
    record = _record()

    assert record.coordinate_unit == MALECNS_EM_COORDINATE_UNIT
    assert record.coordinate_frame_id == MALECNS_EM_COORDINATE_FRAME
    assert record.components[0].nodes[0].location == SpatialPoint(10.25, 20.5, 30.75)
    assert "transform" not in record.to_dict()
    with pytest.raises(FrozenInstanceError):
        record.body_id = 9  # type: ignore[misc]
    with pytest.raises(MaleCNSValidationError, match="immutable component tuple"):
        _record(components=[_component()])


@pytest.mark.parametrize("coordinate", [float("nan"), float("inf"), -float("inf")])
def test_spatial_coordinates_must_be_finite(coordinate: float) -> None:
    with pytest.raises(MaleCNSValidationError, match="finite"):
        SpatialPoint(coordinate, 0.0, 0.0)


def test_components_remain_separate_and_cross_component_links_are_rejected() -> None:
    first = _component()
    second = _component(1, offset=10)
    record = _record(components=(first, second))

    assert record.component_count == 2
    assert [component.component_id for component in record.components] == [0, 1]
    with pytest.raises(MaleCNSValidationError, match="within their component"):
        SkeletonComponent(
            component_id=0,
            nodes=first.nodes,
            links=(SkeletonLink(2, 11, SkeletonLinkProvenance.RAW),),
        )


def test_raw_record_cannot_hide_artificial_repair_link() -> None:
    repaired = _component(provenance=SkeletonLinkProvenance.ARTIFICIAL_REPAIR)

    with pytest.raises(MaleCNSValidationError, match="RAW morphology"):
        _record(components=(repaired,))

    healed = NeuronSpatialRecord(
        dataset_id="male-cns:v1.0",
        candidate_id="looming_giant_fiber_v1",
        candidate_version=1,
        body_id=10001,
        node_index=0,
        neuron_type="DNp01",
        side="R",
        source_category=SpatialEvidenceCategory.NEUROFLY_MODELLING_ASSUMPTION,
        morphology_source="JANELIA_NEUPRINT_MALECNS_SKELETON_WITH_REPAIR",
        morphology_mode=MorphologyMode.HEALED,
        coordinate_unit=MALECNS_EM_COORDINATE_UNIT,
        coordinate_frame_id=MALECNS_EM_COORDINATE_FRAME,
        components=(repaired,),
        source_swc_sha256=SOURCE_HASH,
    )
    assert (
        healed.components[0].links[0].provenance
        is SkeletonLinkProvenance.ARTIFICIAL_REPAIR
    )


def test_serialization_and_identity_are_deterministic_and_json_safe() -> None:
    first = _record()
    second = _record()

    assert first.spatial_record_id == second.spatial_record_id
    assert first.spatial_record_id.startswith("sha256:")
    assert json.loads(json.dumps(first.to_dict())) == first.to_dict()
    assert first.to_dict()["source_category"] == "MALECNS_DIRECT_DATA"


def test_exact_body_id_mapping_is_validated_against_circuit() -> None:
    neuron = SimpleNamespace(type="DNp01", soma_side="R")
    circuit = SimpleNamespace(
        provenance=SimpleNamespace(dataset="male-cns:v1.0"),
        candidate=SimpleNamespace(identifier="looming_giant_fiber_v1", version=1),
        neurons_by_body_id=MappingProxyType({10001: neuron}),
        node_index_by_body_id=MappingProxyType({10001: 0}),
    )
    record = _record()

    validate_spatial_record_against_circuit(record, circuit)
    with pytest.raises(MaleCNSValidationError, match="node_index"):
        validate_spatial_record_against_circuit(
            _record(node_index=1),
            circuit,
        )


def test_contract_has_no_behavior_or_anatomical_direction_fields() -> None:
    keys = set(_record().to_dict())

    assert not keys & {
        "behavior",
        "motor_output",
        "signal_direction",
        "anatomical_position",
        "browser_transform",
    }
