"""Offline synthetic fixtures used only to test Phase 1A behavior."""

from datetime import UTC, datetime

import pytest

from neurofly.malecns.models import (
    CANDIDATE,
    CandidateSnapshot,
    ConnectionRecord,
    NeuronRecord,
)


def neuron(body_id: int, neuron_type: str, instance: str | None = None) -> NeuronRecord:
    return NeuronRecord(
        dataset=CANDIDATE.dataset,
        body_id=body_id,
        instance=instance,
        type=neuron_type,
        status="Traced",
        status_label=None,
        superclass=(
            "descending_neuron" if neuron_type == "DNp01" else "visual_projection"
        ),
        class_=None,
        soma_side="L",
        soma_neuromere=None,
        pre=1,
        post=2,
        upstream=3,
        downstream=4,
        predicted_nt="acetylcholine",
        predicted_nt_confidence=0.9,
        consensus_nt="acetylcholine",
        dimorphism=None,
    )


@pytest.fixture
def valid_snapshot() -> CandidateSnapshot:
    lc4 = [neuron(20_000 + index, "LC4") for index in range(126)]
    lplc2 = [neuron(30_000 + index, "LPLC2") for index in range(185)]
    dnp01 = [
        neuron(10010, "DNp01", "DNp01(GF)_L"),
        neuron(10001, "DNp01", "DNp01(GF)_R"),
    ]
    connections = [
        ConnectionRecord(
            CANDIDATE.dataset,
            source.body_id,
            10010,
            "LC4",
            "DNp01",
            50 if index < 125 else 112,
        )
        for index, source in enumerate(lc4)
    ]
    connections.extend(
        ConnectionRecord(
            CANDIDATE.dataset,
            source.body_id,
            10010,
            "LPLC2",
            "DNp01",
            26 if index < 184 else 78,
        )
        for index, source in enumerate(lplc2)
    )
    # A real induced subgraph is not limited to the primary feed-forward motif.
    connections.append(
        ConnectionRecord(CANDIDATE.dataset, 10010, 20_000, "DNp01", "LC4", 7)
    )
    return CandidateSnapshot(
        candidate=CANDIDATE,
        neurons=tuple(lc4 + lplc2 + dnp01),
        connections=tuple(connections),
        acquired_at_utc=datetime(2026, 9, 10, tzinfo=UTC).isoformat(),
    )
