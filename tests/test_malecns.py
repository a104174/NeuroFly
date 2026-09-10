"""Offline tests for acquisition, normalization, and validation."""

from dataclasses import replace

import pytest

from neurofly.malecns.acquire import (
    acquire_candidate,
    normalize_connections,
    normalize_neurons,
)
from neurofly.malecns.client import create_client
from neurofly.malecns.errors import (
    MaleCNSAccessError,
    MaleCNSDataError,
    MaleCNSValidationError,
)
from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET
from neurofly.malecns.validation import validate_snapshot


def neuron_row(body_id: int = 1, neuron_type: str = "LC4") -> dict[str, object]:
    return {
        "bodyId": body_id,
        "instance": None,
        "type": neuron_type,
        "status": "Traced",
        "statusLabel": None,
        "superclass": "visual_projection",
        "class": None,
        "somaSide": "L",
        "somaNeuromere": None,
        "pre": 1,
        "post": 2,
        "upstream": 3,
        "downstream": 4,
        "predictedNt": "acetylcholine",
        "predictedNtConfidence": None,
        "consensusNt": "acetylcholine",
        "dimorphism": None,
    }


def test_missing_credentials_are_actionable_and_secret_safe(monkeypatch) -> None:
    monkeypatch.delenv("NEUPRINT_APPLICATION_CREDENTIALS", raising=False)
    with pytest.raises(MaleCNSAccessError, match="NEUPRINT_APPLICATION_CREDENTIALS"):
        create_client()


def test_candidate_definition_is_explicit_and_pinned() -> None:
    assert CANDIDATE.identifier == "looming_giant_fiber_v1"
    assert CANDIDATE.version == 1
    assert CANDIDATE.dataset == "male-cns:v1.0"
    assert CANDIDATE.neuron_types == ("LC4", "LPLC2", "DNp01")


def test_neuron_normalization_preserves_null_annotations() -> None:
    record = normalize_neurons([neuron_row()], MALECNS_DATASET)[0]
    assert record.body_id == 1
    assert record.status == "Traced"
    assert record.status_label is None
    assert record.predicted_nt_confidence is None
    assert record.consensus_nt == "acetylcholine"
    assert record.to_dict()["class"] is None


def test_neuron_normalization_rejects_duplicate_body_ids() -> None:
    with pytest.raises(MaleCNSDataError, match="Duplicate"):
        normalize_neurons([neuron_row(), neuron_row()], MALECNS_DATASET)


def test_connection_weight_maps_to_structural_weight() -> None:
    record = normalize_connections(
        [
            {
                "sourceBodyId": 1,
                "targetBodyId": 2,
                "sourceType": "LC4",
                "targetType": "DNp01",
                "weight": 42,
            }
        ],
        MALECNS_DATASET,
    )[0]
    assert record.structural_weight == 42
    assert "weight" not in record.to_dict()
    assert "simulation_weight" not in record.to_dict()


def test_invalid_structural_weight_is_rejected() -> None:
    with pytest.raises(MaleCNSDataError, match="positive integer"):
        normalize_connections(
            [
                {
                    "sourceBodyId": 1,
                    "targetBodyId": 2,
                    "sourceType": "LC4",
                    "targetType": "DNp01",
                    "weight": 0,
                }
            ],
            MALECNS_DATASET,
        )


def test_population_identity_and_primary_metrics_are_validated(valid_snapshot) -> None:
    report = validate_snapshot(valid_snapshot)
    assert report.neuron_counts == {"LC4": 126, "LPLC2": 185, "DNp01": 2}
    assert report.total_neuron_count == 313
    assert report.lc4_to_dnp01.edge_count == 126
    assert report.lc4_to_dnp01.structural_weight_sum == 6362
    assert report.lplc2_to_dnp01.edge_count == 185
    assert report.lplc2_to_dnp01.structural_weight_sum == 4862


def test_population_count_mismatch_is_scientifically_visible(valid_snapshot) -> None:
    changed = replace(valid_snapshot, neurons=valid_snapshot.neurons[:-1])
    with pytest.raises(MaleCNSValidationError, match="actual=.*expected"):
        validate_snapshot(changed)


def test_dnp01_identity_mismatch_is_rejected(valid_snapshot) -> None:
    neurons = tuple(
        replace(neuron, instance="wrong") if neuron.body_id == 10010 else neuron
        for neuron in valid_snapshot.neurons
    )
    with pytest.raises(MaleCNSValidationError, match="DNp01 identities"):
        validate_snapshot(replace(valid_snapshot, neurons=neurons))


def test_population_annotation_mismatch_is_rejected(valid_snapshot) -> None:
    neurons = tuple(
        replace(neuron, consensus_nt=None) if neuron.body_id == 20_000 else neuron
        for neuron in valid_snapshot.neurons
    )
    with pytest.raises(MaleCNSValidationError, match="LC4 consensus_nt"):
        validate_snapshot(replace(valid_snapshot, neurons=neurons))


@pytest.mark.parametrize("source_type", ["LC4", "LPLC2"])
def test_primary_connectivity_mismatch_is_rejected(valid_snapshot, source_type) -> None:
    connections = tuple(
        edge
        for edge in valid_snapshot.connections
        if not (edge.source_type == source_type and edge.target_type == "DNp01")
    )
    with pytest.raises(MaleCNSValidationError, match=f"{source_type} -> DNp01"):
        validate_snapshot(replace(valid_snapshot, connections=connections))


def test_acquisition_preserves_complete_induced_edges() -> None:
    class Client:
        dataset = MALECNS_DATASET

    reverse = {
        "sourceBodyId": 10010,
        "targetBodyId": 1,
        "sourceType": "DNp01",
        "targetType": "LC4",
        "weight": 5,
    }

    def runner(query, client):
        del client
        return [neuron_row()] if "RETURN n.bodyId" in query else [reverse]

    snapshot = acquire_candidate(
        Client(), query_runner=runner, acquired_at_utc="2026-09-10T00:00:00+00:00"
    )
    assert len(snapshot.connections) == 1
    assert snapshot.connections[0].source_type == "DNp01"
    assert snapshot.connections[0].target_type == "LC4"


def test_dataset_mismatch_fails_before_query() -> None:
    class Client:
        dataset = "male-cns:other"

    with pytest.raises(MaleCNSAccessError, match="Unexpected neuPrint dataset"):
        acquire_candidate(Client())
