"""Offline tests for the model-neutral body-to-column contract."""

from dataclasses import replace
from types import SimpleNamespace

import pytest

from neurofly.malecns.columns import (
    FROZEN_PHASE_1D_BODY_IDS,
    BodyColumnInputContract,
    RawInputObservation,
    build_column_contract,
    compare_method_equivalence,
    normalize_aggregate_rows,
    validate_column_contract,
)
from neurofly.malecns.errors import MaleCNSDataError, MaleCNSValidationError
from neurofly.malecns.models import CANDIDATE, NeuronRecord


def _neuron(body_id: int, neuron_type: str = "LC4", side: str = "L") -> NeuronRecord:
    return NeuronRecord(
        dataset=CANDIDATE.dataset,
        body_id=body_id,
        instance=f"{neuron_type}({side})",
        type=neuron_type,
        status="Traced",
        status_label=None,
        superclass="visual_projection",
        class_=None,
        soma_side=side,
        soma_neuromere=None,
        pre=1,
        post=2,
        upstream=3,
        downstream=4,
        predicted_nt=None,
        predicted_nt_confidence=None,
        consensus_nt=None,
        dimorphism=None,
    )


def _circuit(*neurons: NeuronRecord) -> SimpleNamespace:
    return SimpleNamespace(candidate=CANDIDATE, neurons=tuple(neurons))


def _rois() -> dict[str, tuple[str, ...]]:
    return {
        "L": ("ME(L)", "LO(L)", "LOP(L)", "Optic-unspecified(L)"),
        "R": ("ME(R)", "LO(R)", "LOP(R)", "Optic-unspecified(R)"),
    }


def _rows() -> list[dict[str, object]]:
    return [
        {
            "bodyId": 1,
            "neuronType": "LC4",
            "somaSide": "L",
            "primaryRoi": "ME(L)",
            "olHex1": 1,
            "olHex2": 2,
            "columnRois": ["ME_L_col_01_02"],
            "inputCount": 2,
        },
        {
            "bodyId": 1,
            "neuronType": "LC4",
            "somaSide": "L",
            "primaryRoi": "LO(L)",
            "olHex1": None,
            "olHex2": None,
            "columnRois": [],
            "inputCount": 1,
        },
    ]


def test_build_contract_preserves_neuropil_and_unassigned_accounting() -> None:
    contract = build_column_contract(
        _rows(), _circuit(_neuron(1)), _rois(), expected_population=False
    )
    assert len(contract.records) == 1
    assert contract.records[0].neuropil == "ME"
    assert contract.records[0].ol_hex1 == 1
    summary = contract.summaries[0]
    assert summary.relevant_input_count == 3
    assert summary.assigned_input_count == 2
    assert summary.unassigned_input_count == 1
    assert summary.assignment_fraction == pytest.approx(2 / 3)
    assert dict(summary.neuropil_input_counts) == {"LO": 1, "ME": 2}
    assert dict(summary.neuropil_assigned_counts) == {"ME": 2}


def test_malformed_hex_is_unassigned_and_reported() -> None:
    rows = [dict(_rows()[0], olHex1=1, olHex2=None, columnRois=[])]
    contract = build_column_contract(
        rows, _circuit(_neuron(1)), _rois(), expected_population=False
    )
    summary = contract.summaries[0]
    assert not contract.records
    assert summary.malformed_hex_count == 2
    assert summary.unassigned_input_count == 2


def test_duplicate_sparse_key_is_rejected() -> None:
    contract = build_column_contract(
        _rows(), _circuit(_neuron(1)), _rois(), expected_population=False
    )
    duplicate = replace(contract, records=contract.records + contract.records[:1])
    with pytest.raises(MaleCNSValidationError, match="Duplicate sparse"):
        validate_column_contract(duplicate, expected_population=False)


def test_unknown_or_multiple_column_ids_are_unassigned() -> None:
    unknown = dict(_rows()[0], columnRois=["not_a_column"])
    multiple = dict(_rows()[0], columnRois=["ME_L_col_01_02", "ME_L_col_01_03"])
    contract = build_column_contract(
        [unknown, multiple], _circuit(_neuron(1)), _rois(), expected_population=False
    )
    summary = contract.summaries[0]
    assert not contract.records
    assert summary.unknown_column_count == 2
    assert summary.multiple_column_count == 2
    assert summary.unassigned_input_count == 4


def test_normalize_rejects_malformed_column_rois() -> None:
    row = dict(_rows()[0], columnRois="ME_L_col_01_02")
    with pytest.raises(MaleCNSDataError, match="columnRois is invalid"):
        normalize_aggregate_rows([row])


def test_method_equivalence_compares_sparse_distribution_exactly() -> None:
    body_id = FROZEN_PHASE_1D_BODY_IDS[0]
    neuron = _neuron(body_id)
    aggregate = build_column_contract(
        [dict(_rows()[0], bodyId=body_id)],
        _circuit(neuron),
        _rois(),
        expected_population=False,
    )
    raw = RawInputObservation(
        sparse_counts={
            (body_id, "LC4", "L", "ME", 1, 2): 2,
        },
        per_body={body_id: (2, 2, 0)},
    )
    compare_method_equivalence(aggregate, raw, body_ids=(body_id,))


def test_side_and_type_are_preserved() -> None:
    neuron = _neuron(2, "LPLC2", "R")
    row = dict(_rows()[0], bodyId=2, neuronType="LPLC2", somaSide="R")
    row.update(primaryRoi="ME(R)", columnRois=["ME_R_col_01_02"])
    contract = build_column_contract(
        [row], _circuit(neuron), _rois(), expected_population=False
    )
    assert contract.records[0].neuron_type == "LPLC2"
    assert contract.records[0].eye_side == "R"


def test_visual_population_validation_excludes_non_visual_body() -> None:
    neuron = _neuron(1)
    contract = build_column_contract(
        _rows(), _circuit(neuron), _rois(), expected_population=False
    )
    bad_summary = replace(contract.summaries[0], neuron_type="DNp01")
    bad_contract = replace(contract, summaries=(bad_summary,))
    with pytest.raises(MaleCNSValidationError, match="non-visual"):
        validate_column_contract(bad_contract, expected_population=False)


def test_contract_is_immutable() -> None:
    contract = BodyColumnInputContract(
        schema_version="body_column_input_v1",
        candidate_identifier=CANDIDATE.identifier,
        candidate_version=CANDIDATE.version,
        dataset=CANDIDATE.dataset,
        endpoint="https://neuprint.janelia.org",
        acquired_at_utc="2026-09-11T00:00:00+00:00",
        source_snapshot="snapshot",
        visual_territory_rule="matching_side_optic_primary_post_v1",
        aggregation_method="server_primary_optic_group_v1",
        records=(),
        summaries=(),
    )
    with pytest.raises(AttributeError):
        contract.dataset = "other"  # type: ignore[misc]
