"""Offline tests for fixed-scope raw MaleCNS morphology artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.errors import (
    MorphologyArtifactExportError,
    MorphologyArtifactIntegrityError,
)
from neurofly.malecns.morphology_artifacts import (
    DNP01_MORPHOLOGY_BODY_IDS,
    MORPHOLOGY_ARTIFACT_SCHEMA_VERSION,
    MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC,
    OFFICIAL_MALECNS_BULK_SWC_URLS,
    OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS,
    PHASE5G_MORPHOLOGY_BODY_IDS,
    MorphologyBodyRecord,
    acquire_dnp01_morphology,
    acquire_dnp01_morphology_from_official_bulk_swc,
    acquire_phase5g_morphology_from_official_bulk_swc,
    export_morphology_artifact,
    generate_dnp01_morphology_artifact_from_official_bulk_swc,
    generate_phase5g_morphology_artifact_from_official_bulk_swc,
    load_morphology_artifact,
    validate_fixed_dnp01_mapping,
    validate_fixed_phase5g_mapping,
)
from neurofly.malecns.spatial import (
    MorphologyMode,
    SkeletonComponent,
    SkeletonLink,
    SkeletonLinkProvenance,
    SkeletonNode,
    SpatialPoint,
    current_raw_spatial_record,
)


@pytest.fixture(scope="module")
def circuit():
    return load_circuit_contract(
        Path(__file__).resolve().parents[1]
        / "data/derived/malecns/looming_giant_fiber_v1"
    )


def _body(body_id: int) -> MorphologyBodyRecord:
    node_index, side, offset = (0, "R", 0.0) if body_id == 10001 else (1, "L", 100.0)
    component = SkeletonComponent(
        component_id=0,
        nodes=(
            SkeletonNode(1, SpatialPoint(offset + 1.25, 2.5, 3.75), 2.0),
            SkeletonNode(2, SpatialPoint(offset + 4.25, 5.5, 6.75), None),
        ),
        links=(SkeletonLink(2, 1, SkeletonLinkProvenance.RAW),),
    )
    return MorphologyBodyRecord(
        current_raw_spatial_record(
            body_id=body_id,
            node_index=node_index,
            neuron_type="DNp01",
            side=side,
            components=(component,),
            source_swc_sha256=("a" if body_id == 10001 else "b") * 64,
            soma_location=SpatialPoint(offset, 0.0, 0.0),
        ),
        "Traced",
    )


def synthetic_morphology_bodies() -> tuple[MorphologyBodyRecord, ...]:
    return (_body(10001), _body(10010))


def synthetic_phase5g_morphology_bodies() -> tuple[MorphologyBodyRecord, ...]:
    mapping = {
        10001: (0, "DNp01", "R"),
        10010: (1, "DNp01", "L"),
        11498: (2, "LPLC2", "L"),
        12032: (3, "LC4", "L"),
        14465: (12, "LPLC2", "R"),
        16128: (16, "LC4", "R"),
    }
    result = []
    for body_id in PHASE5G_MORPHOLOGY_BODY_IDS:
        node_index, neuron_type, side = mapping[body_id]
        offset = float(node_index * 10)
        components = [
            SkeletonComponent(
                component_id=0,
                nodes=(
                    SkeletonNode(1, SpatialPoint(offset, 1.0, 2.0), 1.0),
                    SkeletonNode(2, SpatialPoint(offset + 1.0, 2.0, 3.0), 2.0),
                ),
                links=(SkeletonLink(2, 1, SkeletonLinkProvenance.RAW),),
            )
        ]
        if body_id == 11498:
            components.append(
                SkeletonComponent(
                    component_id=1,
                    nodes=(SkeletonNode(3, SpatialPoint(offset + 2.0, 3.0, 4.0), 1.0),),
                    links=(),
                )
            )
        result.append(
            MorphologyBodyRecord(
                current_raw_spatial_record(
                    body_id=body_id,
                    node_index=node_index,
                    neuron_type=neuron_type,
                    side=side,
                    components=tuple(components),
                    source_swc_sha256=f"{body_id:064x}",
                    soma_location=None,
                ),
                "Traced",
            )
        )
    return tuple(result)


def test_fixed_mapping_matches_committed_circuit(circuit) -> None:
    validate_fixed_dnp01_mapping(circuit)
    validate_fixed_phase5g_mapping(circuit)
    assert DNP01_MORPHOLOGY_BODY_IDS == (10001, 10010)
    assert PHASE5G_MORPHOLOGY_BODY_IDS == (10001, 10010, 11498, 12032, 14465, 16128)


def test_phase5g_official_acquisition_preserves_fragmentation(
    circuit, tmp_path: Path
) -> None:
    calls = []

    def fetcher(body_id: int, url: str) -> bytes:
        calls.append((body_id, url))
        second_root = "3 0 7 8 9 1 -1\n4 0 8 9 10 1 3\n" if body_id == 11498 else ""
        return f"1 0 1 2 3 1 -1\n2 0 4 5 6 1 1\n{second_root}".encode()

    bodies, source_urls = acquire_phase5g_morphology_from_official_bulk_swc(
        circuit, fetcher=fetcher
    )
    assert calls == list(OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS.items())
    assert source_urls == tuple(sorted(OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS.items()))
    fragmented = next(body for body in bodies if body.spatial_record.body_id == 11498)
    assert [
        len(component.nodes) for component in fragmented.spatial_record.components
    ] == [2, 2]
    assert [
        len(component.links) for component in fragmented.spatial_record.components
    ] == [1, 1]
    artifact = generate_phase5g_morphology_artifact_from_official_bulk_swc(
        circuit, tmp_path, fetcher=fetcher
    )
    loaded = load_morphology_artifact(artifact, circuit=circuit)
    assert dict(loaded.source_urls) == dict(OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS)


def test_phase5g_artifact_round_trip_preserves_two_components(
    tmp_path: Path, circuit
) -> None:
    path = export_morphology_artifact(synthetic_phase5g_morphology_bodies(), tmp_path)
    loaded = load_morphology_artifact(path, circuit=circuit)
    assert tuple(body.spatial_record.body_id for body in loaded.bodies) == (
        PHASE5G_MORPHOLOGY_BODY_IDS
    )
    fragmented = loaded.bodies_by_id[11498].spatial_record
    assert fragmented.component_count == 2
    assert all(
        link.child_node_id in {node.node_id for node in component.nodes}
        and link.parent_node_id in {node.node_id for node in component.nodes}
        for component in fragmented.components
        for link in component.links
    )


def test_acquisition_requests_exact_raw_body_set(circuit) -> None:
    calls = []
    swc = "1 0 1 2 3 1 -1\n2 0 4 5 6 1 1\n"

    class Client:
        dataset = "male-cns:v1.0"

        def fetch_skeleton(self, body_id, *, heal, format):
            calls.append((body_id, heal, format))
            return swc

    soma = pd.DataFrame(
        {
            "bodyId": [10001, 10010],
            "somaLocation": [
                {"coordinates": [1, 2, 3]},
                {"coordinates": [4, 5, 6]},
            ],
        }
    )
    bodies = acquire_dnp01_morphology(
        Client(), circuit, soma_fetcher=lambda _client: soma
    )

    assert calls == [(10001, False, "swc"), (10010, False, "swc")]
    assert [body.spatial_record.body_id for body in bodies] == [10001, 10010]


def test_official_bulk_acquisition_preserves_source_mode_and_urls(
    circuit, tmp_path: Path
) -> None:
    calls = []
    swc = b"# official bulk SWC\n1 0 1 2 3 1 -1\n2 0 4 5 6 1 1\n"

    def fetcher(body_id: int, url: str) -> bytes:
        calls.append((body_id, url))
        return swc

    bodies, source_urls = acquire_dnp01_morphology_from_official_bulk_swc(
        circuit, fetcher=fetcher
    )
    assert calls == [
        (10001, OFFICIAL_MALECNS_BULK_SWC_URLS[10001]),
        (10010, OFFICIAL_MALECNS_BULK_SWC_URLS[10010]),
    ]
    assert source_urls == tuple(sorted(OFFICIAL_MALECNS_BULK_SWC_URLS.items()))
    assert all(
        body.spatial_record.morphology_source == "OFFICIAL_MALECNS_BULK_SWC"
        and body.spatial_record.soma_location is None
        for body in bodies
    )

    artifact = generate_dnp01_morphology_artifact_from_official_bulk_swc(
        circuit, tmp_path, fetcher=fetcher
    )
    loaded = load_morphology_artifact(artifact, circuit=circuit)
    assert loaded.source_mode == "OFFICIAL_MALECNS_BULK_SWC"
    assert loaded.retrieval == MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC
    assert dict(loaded.source_urls) == dict(OFFICIAL_MALECNS_BULK_SWC_URLS)
    assert loaded.manifest["generation"]["source_urls"] == {
        str(body_id): url for body_id, url in OFFICIAL_MALECNS_BULK_SWC_URLS.items()
    }
    assert all(body.spatial_record.component_count == 1 for body in bodies)


def test_artifact_round_trip_preserves_raw_coordinates_and_identity(
    tmp_path: Path, circuit
) -> None:
    path = export_morphology_artifact(
        synthetic_morphology_bodies(),
        tmp_path,
        generated_at_utc="2026-09-13T00:00:00+00:00",
        neuprint_python_version="0.test",
    )
    loaded = load_morphology_artifact(path, circuit=circuit)

    assert loaded.artifact_id == path.name
    assert loaded.manifest["artifact_schema_version"] == (
        MORPHOLOGY_ARTIFACT_SCHEMA_VERSION
    )
    assert [body.spatial_record.body_id for body in loaded.bodies] == [10001, 10010]
    assert all(
        body.spatial_record.morphology_mode is MorphologyMode.RAW
        for body in loaded.bodies
    )
    assert loaded.bodies[0].spatial_record.components[0].nodes[0].location == (
        SpatialPoint(1.25, 2.5, 3.75)
    )
    assert all(
        link.provenance is SkeletonLinkProvenance.RAW
        for body in loaded.bodies
        for component in body.spatial_record.components
        for link in component.links
    )
    assert not set(loaded.manifest) & {
        "experiment_id",
        "experiment_config_id",
        "result_id",
    }


def test_logical_identity_excludes_generation_metadata(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = export_morphology_artifact(
        synthetic_morphology_bodies(), first_root, generated_at_utc="2020-01-01Z"
    )
    second = export_morphology_artifact(
        synthetic_morphology_bodies(), second_root, generated_at_utc="2030-01-01Z"
    )
    assert first.name == second.name
    assert load_morphology_artifact(first).artifact_id == first.name
    assert load_morphology_artifact(second).artifact_id == second.name
    with pytest.raises(MorphologyArtifactExportError, match="already exists"):
        export_morphology_artifact(synthetic_morphology_bodies(), first_root)


def test_corruption_is_rejected(tmp_path: Path) -> None:
    path = export_morphology_artifact(synthetic_morphology_bodies(), tmp_path)
    payload_path = path / "bodies/10001.json"
    payload = json.loads(payload_path.read_text())
    payload["spatial_record"]["components"][0]["nodes"][0]["x"] = 999.0
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(MorphologyArtifactIntegrityError, match="mismatch"):
        load_morphology_artifact(path)
