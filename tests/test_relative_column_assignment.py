"""Phase 7D source-bounded anatomical assignment and artifact tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from neurofly.experiment_artifacts import ARTIFACT_SCHEMA_VERSION
from neurofly.malecns.column_lattice import (
    OFFICIAL_COLUMN_WORKBOOK_SHA256,
    hex_distance,
)
from neurofly.motor_pathway_artifacts import MOTOR_ARTIFACT_SCHEMA_VERSION
from neurofly.relative_column_assignment import (
    BODY_IDENTITIES,
    BODY_IDS,
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    RelativeColumnAssignmentError,
    RelativeColumnStimulus,
    active_column_set,
    build_experiment_config,
    canonical_json_bytes,
    compute_assignment_result,
    fixed_stimuli,
    load_relative_column_grid,
    load_relative_column_source,
    sha256_bytes,
)
from neurofly.relative_column_assignment_artifacts import (
    ARTIFACT_SCHEMA_VERSION as ASSIGNMENT_ARTIFACT_SCHEMA_VERSION,
)
from neurofly.relative_column_assignment_artifacts import (
    RelativeColumnArtifactExportError,
    RelativeColumnArtifactIntegrityError,
    export_relative_column_artifact,
    load_relative_column_artifact,
    relative_column_artifact_id,
    replay_relative_column_artifact,
)

SOURCE_AVAILABLE = DEFAULT_SOURCE_ROOT.exists() and DEFAULT_WORKBOOK.exists()


@pytest.fixture(scope="module")
def source_and_grid():
    if not SOURCE_AVAILABLE:
        pytest.skip("ignored real MaleCNS source and pinned workbook are unavailable")
    source = load_relative_column_source(DEFAULT_SOURCE_ROOT)
    return source, load_relative_column_grid(DEFAULT_WORKBOOK, source)


def _sample(result: dict, stimulus_id: str, step: int) -> dict:
    return next(
        sample
        for sample in result["samples"]
        if sample["stimulus_id"] == stimulus_id and sample["step"] == step
    )


def _assignment(sample: dict, body_id: int) -> dict:
    return next(item for item in sample["assignments"] if item["body_id"] == body_id)


def test_lattice_distance_uses_pq_six_neighbours_not_euclidean() -> None:
    origin = (18, 19)
    neighbours = ((19, 19), (17, 19), (18, 20), (18, 18), (19, 20), (17, 18))
    assert all(hex_distance(origin, item) == 1 for item in neighbours)
    assert hex_distance(origin, (19, 18)) == 2
    assert hex_distance(origin, origin) == 0
    with pytest.raises(ValueError, match="integer pairs"):
        hex_distance((18.0, 19), origin)  # type: ignore[arg-type]


def test_stimulus_config_uses_only_integer_lattice_and_step_units() -> None:
    stimulus = RelativeColumnStimulus("zero_radius", "L", 18, 19, 0.1, (0, 1, 2))
    value = stimulus.to_dict()
    assert value["spatial_unit"] == "MaleCNS_hex_lattice_steps"
    assert value["time_grid_semantics"] == "integer_sample_steps_v1"
    assert [sample["step"] for sample in value["radius_schedule"]] == [0, 1, 2]
    assert [sample["radius_lattice_steps"] for sample in value["radius_schedule"]] == [
        0,
        1,
        2,
    ]
    assert "radians" not in value and "degrees" not in value
    with pytest.raises(RelativeColumnAssignmentError, match="side"):
        RelativeColumnStimulus("bad_side", "B", 18, 19, 0.1, (1,))
    with pytest.raises(RelativeColumnAssignmentError, match="radius"):
        RelativeColumnStimulus("bad_radius", "L", 18, 19, 0.1, (-1,))
    with pytest.raises(RelativeColumnAssignmentError, match="start_step"):
        RelativeColumnStimulus("bad_time", "L", 18, 19, 0.1, (1,), start_step=-1)
    with pytest.raises(RelativeColumnAssignmentError, match="dt_ms"):
        RelativeColumnStimulus("bad_dt", "L", 18, 19, 0.0, (1,))
    with pytest.raises(RelativeColumnAssignmentError, match="dt_ms"):
        RelativeColumnStimulus("string_dt", "L", 18, 19, "0.1", (1,))  # type: ignore[arg-type]
    with pytest.raises(RelativeColumnAssignmentError, match="samples"):
        RelativeColumnStimulus("empty", "L", 18, 19, 0.1, ())
    malformed = value | {"end_step": True}
    with pytest.raises(RelativeColumnAssignmentError, match="end_step"):
        RelativeColumnStimulus.from_dict(malformed)


def test_source_identity_is_pinned_and_exact_four_are_cross_validated(source_and_grid):
    source, grid = source_and_grid
    assert source.contract.schema_version == "body_column_input_v1"
    assert source.contract.dataset == "male-cns:v1.0"
    assert source.contract.candidate_identifier == "looming_giant_fiber_v1"
    assert tuple(source.body_records) == BODY_IDS
    assert [
        (
            body_id,
            source.body_summaries[body_id].neuron_type,
            source.body_summaries[body_id].eye_side,
        )
        for body_id in BODY_IDS
    ] == [
        (item["body_id"], item["neuron_type"], item["side"]) for item in BODY_IDENTITIES
    ]
    assert source.source_identity["source_file_sha256"] == {
        "column_inputs.jsonl": (
            "4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e"
        ),
        "column_body_summaries.jsonl": (
            "ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b"
        ),
    }
    assert source.source_identity["contract_identity_sha256"]
    assert grid.workbook_sha256 == OFFICIAL_COLUMN_WORKBOOK_SHA256
    assert dict(grid.to_identity_dict()["official_medulla_column_counts"]) == {
        "L": 880,
        "R": 892,
    }
    assert grid.to_identity_dict()["source_only_coordinate_counts"] == {"L": 2, "R": 0}
    assert grid.to_identity_dict()["source_only_coordinates_are_unclassified"] is True
    assert {(17, 34), (19, 35)} <= grid.columns_by_side["L"]
    assert not ({(17, 34), (19, 35)} & set(grid.official_classes_by_side["L"]))


def test_active_disks_expand_translate_and_remain_side_local(source_and_grid):
    source, grid = source_and_grid
    left = next(
        item for item in fixed_stimuli() if item.stimulus_id == "left_expand_33_29"
    )
    right = next(
        item for item in fixed_stimuli() if item.stimulus_id == "right_expand_23_09"
    )
    l0 = active_column_set(left, grid, 0)
    l1 = active_column_set(left, grid, 1)
    l4 = active_column_set(left, grid, 4)
    r1 = active_column_set(right, grid, 1)
    r4 = active_column_set(right, grid, 4)
    assert l0 == ((33, 29),)
    assert len(l1) == 7 and len(l4) == 56
    assert len(r1) == 7 and len(r4) == 44
    assert set(l1) < set(l4) and set(r1) < set(r4)
    assert set(active_column_set(left, grid, 2)) != set(
        active_column_set(
            RelativeColumnStimulus("translated", "L", 18, 4, 0.1, (2,)),
            grid,
            2,
        )
    )
    with pytest.raises(RelativeColumnAssignmentError, match="unknown L column"):
        active_column_set(
            RelativeColumnStimulus("unknown", "L", 999, 999, 0.1, (1,)), grid, 1
        )
    with pytest.raises(RelativeColumnAssignmentError, match="radius"):
        active_column_set(left, grid, -1)
    assert set(source.contract.body_ids) >= set(BODY_IDS)


def test_four_body_assignment_matches_phase7c_and_has_no_neural_transfer(
    source_and_grid,
):
    source, grid = source_and_grid
    config, result = compute_assignment_result(source, grid)
    assert config["body_identities"] == [dict(item) for item in BODY_IDENTITIES]
    assert result["body_ids"] == list(BODY_IDS)
    assert result["sample_count"] == 10
    assert result["semantics"] == "ANATOMICAL_EXPOSURE_ONLY"
    assert result["limitations"] == {
        "absolute_visual_angle_present": False,
        "functional_receptive_field_present": False,
        "neural_dynamics_present": False,
        "type_level_encoder_drive_mixed": False,
        "exposure_is_neural_drive": False,
        "structural_input_site_count_is_physiological_weight": False,
    }
    expected = (
        ("left_expand_33_29", 0, 12032, 0.0933333333333, 0.161),
        ("left_expand_33_29", 3, 12032, 0.6266666666667, 0.757),
        ("left_lplc2_11498_18_04", 0, 11498, 0.210526315789, 0.390),
        ("right_expand_23_09", 0, 16128, 0.106060606061, 0.199),
        ("right_expand_23_09", 0, 14465, 0.095238095238, 0.119),
        ("right_expand_23_09", 3, 16128, 0.651515151515, 0.822),
        ("right_expand_23_09", 3, 14465, 0.533333333333, 0.670),
    )
    for stimulus_id, step, body_id, columns, sites in expected:
        item = _assignment(_sample(result, stimulus_id, step), body_id)
        assert item["column_overlap_fraction"] == pytest.approx(columns, abs=0.001)
        assert item["structural_input_site_overlap_fraction"] == pytest.approx(
            sites, abs=0.002
        )
        assert item["column_overlap_fraction"] == pytest.approx(
            item["active_source_column_record_count"]
            / item["source_column_record_count"]
        )
        assert 0.0 <= item["column_overlap_fraction"] <= 1.0
        assert 0.0 <= item["structural_input_site_overlap_fraction"] <= 1.0

    left_sample = _sample(result, "left_expand_33_29", 0)
    assert _assignment(left_sample, 16128)["column_overlap_fraction"] == 0.0
    assert (
        _assignment(left_sample, 14465)["structural_input_site_overlap_fraction"] == 0.0
    )
    right_sample = _sample(result, "right_expand_23_09", 0)
    assert _assignment(right_sample, 12032)["column_overlap_fraction"] == 0.0
    assert (
        _assignment(right_sample, 11498)["structural_input_site_overlap_fraction"]
        == 0.0
    )

    expanding = [_sample(result, "left_expand_33_29", step) for step in range(4)]
    for body_id in BODY_IDS:
        for before, after in zip(expanding, expanding[1:], strict=False):
            first = _assignment(before, body_id)
            second = _assignment(after, body_id)
            assert first["column_overlap_fraction"] <= second["column_overlap_fraction"]
            assert (
                first["structural_input_site_overlap_fraction"]
                <= second["structural_input_site_overlap_fraction"]
            )
    serialized = json.dumps(result, sort_keys=True)
    assert "lc4_drive_mveq" not in serialized
    assert "lplc2_drive_mveq" not in serialized
    assert "spike_probability" not in serialized
    assert "physiological_gain" not in serialized


def test_time_samples_use_steps_as_identity_and_recompute_deterministically(
    source_and_grid,
):
    source, grid = source_and_grid
    config1, result1 = compute_assignment_result(source, grid)
    config2, result2 = compute_assignment_result(source, grid)
    assert config1 == config2 and result1 == result2
    samples = [_sample(result1, "left_expand_33_29", step) for step in range(4)]
    assert [item["step"] for item in samples] == [0, 1, 2, 3]
    assert [item["time_ms"] for item in samples[:3]] == [0.0, 0.1, 0.2]
    assert samples[3]["step"] == 3
    assert samples[3]["radius_lattice_steps"] == 4
    assert samples[3]["time_ms"] == 3 * 0.1


def test_source_integrity_failure_is_fail_closed(tmp_path: Path):
    if not SOURCE_AVAILABLE:
        pytest.skip("ignored real MaleCNS source is unavailable")
    copied_root = tmp_path / "source"
    copied_root.mkdir()
    for filename in ("neurons.jsonl", "connections.jsonl", "manifest.json"):
        shutil.copy2(DEFAULT_SOURCE_ROOT / filename, copied_root / filename)
    copied_columns = copied_root / "body_columns_v1"
    shutil.copytree(DEFAULT_SOURCE_ROOT / "body_columns_v1", copied_columns)
    input_path = copied_columns / "column_inputs.jsonl"
    input_path.write_bytes(input_path.read_bytes() + b"\n")
    with pytest.raises(RelativeColumnAssignmentError, match="integrity"):
        load_relative_column_source(copied_root)

    if DEFAULT_WORKBOOK.exists():
        copied_workbook = tmp_path / "untrusted-workbook.xlsx"
        shutil.copy2(DEFAULT_WORKBOOK, copied_workbook)
        copied_workbook.write_bytes(copied_workbook.read_bytes() + b"tamper")
        source = load_relative_column_source(DEFAULT_SOURCE_ROOT)
        with pytest.raises(RelativeColumnAssignmentError, match="SHA-256 mismatch"):
            load_relative_column_grid(copied_workbook, source)


def test_artifact_hash_replay_tamper_and_old_schema_isolation(
    source_and_grid, tmp_path: Path
):
    source, grid = source_and_grid
    config, result = compute_assignment_result(source, grid)
    repeated_config, repeated_result = compute_assignment_result(source, grid)
    artifact_id = relative_column_artifact_id(config, result)
    assert artifact_id == relative_column_artifact_id(repeated_config, repeated_result)
    assert ASSIGNMENT_ARTIFACT_SCHEMA_VERSION == (
        "relative_column_sensory_assignment_artifact_v1"
    )
    assert ASSIGNMENT_ARTIFACT_SCHEMA_VERSION != ARTIFACT_SCHEMA_VERSION
    assert ASSIGNMENT_ARTIFACT_SCHEMA_VERSION != MOTOR_ARTIFACT_SCHEMA_VERSION

    artifact_path = tmp_path / artifact_id
    artifact = export_relative_column_artifact(config, result, artifact_path)
    assert artifact.artifact_id == artifact_id
    assert artifact.result["sample_count"] == 10
    replayed = replay_relative_column_artifact(
        artifact_path,
        source_root=DEFAULT_SOURCE_ROOT,
        workbook_path=DEFAULT_WORKBOOK,
    )
    assert replayed.artifact_id == artifact.artifact_id
    assert replayed.result == artifact.result
    with pytest.raises(RelativeColumnArtifactExportError, match="immutable"):
        export_relative_column_artifact(config, result, artifact_path)

    result_path = artifact_path / "assignment_result.json"
    result_path.write_bytes(result_path.read_bytes() + b" ")
    with pytest.raises(RelativeColumnArtifactIntegrityError):
        load_relative_column_artifact(artifact_path)


def test_config_rejects_unauthorized_body_and_stimulus_side_changes(source_and_grid):
    source, grid = source_and_grid
    config = build_experiment_config(source, grid)
    config["body_identities"] = config["body_identities"][:-1]
    with pytest.raises(RelativeColumnAssignmentError, match="identity mismatch"):
        compute_assignment_result(source, grid, config)

    config = build_experiment_config(source, grid)
    stimulus = config["stimuli"][0]
    stimulus["config"]["side"] = "R"
    stimulus["stimulus_sha256"] = sha256_bytes(canonical_json_bytes(stimulus["config"]))
    with pytest.raises(RelativeColumnAssignmentError, match="fixed Phase 7D"):
        compute_assignment_result(source, grid, config)
