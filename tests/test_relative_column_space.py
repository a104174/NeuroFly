"""Phase 7C offline column-space semantics, never encoder behaviour."""

from pathlib import Path

import pytest

from neurofly.malecns.column_snapshot import load_column_contract
from neurofly.malecns.columns import ColumnInputRecord
from neurofly.malecns.contract import load_circuit_contract
from research.relative_column_space import (
    FIXED_BODIES,
    anatomical_exposure,
    body_anatomy,
    hex_distance,
    load_official_columns,
)

SOURCE_ROOT = Path("data/derived/malecns/looming_giant_fiber_v1")


def _record(
    hex1: int, hex2: int, count: int, *, side: str = "L", neuropil: str = "LO"
) -> ColumnInputRecord:
    return ColumnInputRecord(1, "LC4", side, neuropil, hex1, hex2, count)


def test_six_neighbour_distance_is_not_euclidean() -> None:
    origin = (18, 19)
    neighbours = ((19, 19), (17, 19), (18, 20), (18, 18), (19, 20), (17, 18))
    assert all(hex_distance(origin, neighbour) == 1 for neighbour in neighbours)
    assert hex_distance(origin, (19, 18)) == 2
    assert hex_distance((19, 18), origin) == 2
    assert hex_distance(origin, origin) == 0


def test_anatomical_centres_keep_structural_weight_separate() -> None:
    records = (_record(10, 10, 1), _record(12, 12, 3))
    result = body_anatomy(
        records,
        relevant_sites=5,
        edge_hexes={(12, 12)},
        classified_hexes={(10, 10), (12, 12)},
    )
    assert result["unweighted_anatomical_column_centroid"] == (11, 11)
    assert result["structural_input_weighted_anatomical_column_centroid"] == (
        11.5,
        11.5,
    )
    assert result["assigned_fraction"] == 0.8
    assert result["missing_fraction"] == 0.2
    assert result["edge_hex_fraction_of_classified"] == 0.5
    assert (
        result["unweighted_rms_hex_spread"]
        != result["structural_input_weighted_rms_hex_spread"]
    )
    assert not any("gain" in key or "azimuth" in key for key in result)


def test_unclassified_workbook_hex_is_not_discarded_or_called_non_edge() -> None:
    result = body_anatomy(
        (_record(17, 34, 7), _record(18, 34, 3)),
        relevant_sites=10,
        edge_hexes={(18, 34)},
        classified_hexes={(18, 34)},
    )
    assert result["assigned_sites"] == 10
    assert result["workbook_unclassified_hex_count"] == 1
    assert result["edge_hex_fraction_of_classified"] == 1.0


def test_relative_exposure_is_anatomical_and_side_isolated() -> None:
    records = (
        _record(10, 10, 1),
        _record(10, 10, 3, neuropil="LOP"),
        _record(11, 11, 6),
    )
    left = anatomical_exposure(records, stimulus_side="L", active_hexes={(10, 10)})
    assert left == {
        "any_source_column_overlap": 1.0,
        "source_column_overlap_fraction": 2 / 3,
        "unique_hex_occupancy_overlap_fraction": 0.5,
        "structural_input_site_overlap_fraction": 0.4,
    }
    assert anatomical_exposure(records, stimulus_side="R", active_hexes={(10, 10)}) == {
        key: 0.0 for key in left
    }
    assert records[0].input_count == 1  # Source objects are untouched.


def test_synthetic_radius_expansion_is_deterministic_and_monotone() -> None:
    records = (_record(10, 10, 2), _record(11, 11, 7), _record(13, 13, 1))
    small = {
        (record.ol_hex1, record.ol_hex2)
        for record in records
        if hex_distance((record.ol_hex1, record.ol_hex2), (10, 10)) <= 1
    }
    large = {
        (record.ol_hex1, record.ol_hex2)
        for record in records
        if hex_distance((record.ol_hex1, record.ol_hex2), (10, 10)) <= 3
    }
    first = anatomical_exposure(records, stimulus_side="L", active_hexes=small)
    repeat = anatomical_exposure(records, stimulus_side="L", active_hexes=small)
    expanded = anatomical_exposure(records, stimulus_side="L", active_hexes=large)
    assert first == repeat
    assert small < large
    assert all(first[key] <= expanded[key] for key in first)
    assert expanded["structural_input_site_overlap_fraction"] == 1.0


def test_mixed_body_sides_fail_closed() -> None:
    records = (_record(10, 10, 1), _record(10, 10, 2, side="R"))
    with pytest.raises(ValueError, match="mix left and right"):
        body_anatomy(
            records,
            relevant_sites=3,
            edge_hexes=set(),
            classified_hexes={(10, 10)},
        )
    with pytest.raises(ValueError, match="single-side"):
        anatomical_exposure(records, stimulus_side="L", active_hexes={(10, 10)})


def test_unpinned_workbook_is_rejected(tmp_path: Path) -> None:
    workbook = tmp_path / "wrong.xlsx"
    workbook.write_bytes(b"not the official workbook")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_official_columns(workbook)


@pytest.mark.skipif(not SOURCE_ROOT.exists(), reason="ignored MaleCNS data absent")
def test_real_311_body_source_and_four_body_regression() -> None:
    circuit = load_circuit_contract(SOURCE_ROOT)
    contract = load_column_contract(
        SOURCE_ROOT / "body_columns_v1", circuit_contract=circuit
    )
    assert (len(contract.summaries), len(contract.records)) == (311, 25438)
    assert sum(row.assigned_input_count for row in contract.summaries) == 574745
    assert sum(row.unassigned_input_count for row in contract.summaries) == 2790
    assert {
        neuron_type: sum(row.neuron_type == neuron_type for row in contract.summaries)
        for neuron_type in ("LC4", "LPLC2")
    } == {"LC4": 126, "LPLC2": 185}
    expected = {
        12032: (75, 2436, 2477, 33.47, 30.73),
        16128: (66, 3709, 3710, 22.62, 10.08),
        11498: (95, 1254, 1263, 15.95, 5.98),
        14465: (105, 1854, 1859, 23.65, 12.00),
    }
    for body_id in FIXED_BODIES:
        records = tuple(row for row in contract.records if row.body_id == body_id)
        source = next(row for row in contract.summaries if row.body_id == body_id)
        result = body_anatomy(
            records,
            relevant_sites=source.relevant_input_count,
            edge_hexes=set(),
            classified_hexes={(row.ol_hex1, row.ol_hex2) for row in records},
        )
        count, assigned, relevant, hex1, hex2 = expected[body_id]
        assert (
            result["source_column_count"],
            result["assigned_sites"],
            result["relevant_sites"],
        ) == (count, assigned, relevant)
        assert result["structural_input_weighted_anatomical_column_centroid"] == (
            pytest.approx(hex1, abs=0.005),
            pytest.approx(hex2, abs=0.005),
        )
