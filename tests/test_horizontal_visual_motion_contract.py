"""Synthetic descriptors test contract mechanics, never biological stimuli."""

import copy
import hashlib
import json
import math
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from neurofly import horizontal_visual_motion_contract as contract


def descriptor():
    return {
        "schema": contract.SCHEMA,
        "adapter": contract.ADAPTER,
        "source_id": "FIGURE_1H",
        "source_doi": contract.DOI,
        "source_sha256": contract.SOURCES["FIGURE_1H"],
        "condition": "ZERO",
        "original_label": "TEST_ONLY_NOT_AN_EXPERIMENTAL_STIMULUS",
        "coordinates": contract.FRAME,
        "hemisphere": None,
        "angular_velocity": 0,
        "units": "rad/s",
        "start_ms": 0,
        "end_ms": 20,
        "timing_rule": "HALF_OPEN_CONSTANT_HOLD_NO_INTERPOLATION",
        "mask": None,
        "aggregation": "UNRESOLVED_NO_REDUCTION",
        "evidence": [
            {"field": field, "status": "UNRESOLVED", "reference": "TEST_ONLY"}
            for field in sorted(contract.FIELDS)
        ],
    }


@pytest.fixture
def authentic_artifact():
    path = Path("/tmp/neurofly-v9-2a/figure1.xlsx")
    if not path.exists():
        pytest.skip("external official workbook absent; no synthetic substitution")
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest() == contract.SOURCES["FIGURE_1H"]
    )
    return path


@pytest.mark.parametrize("field", list(descriptor()))
def test_no_missing_fields_or_silent_defaults(field):
    value = descriptor()
    del value[field]
    with pytest.raises(ValueError):
        contract.parse_descriptor(value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", "v0"),
        ("adapter", "v0"),
        ("source_id", "UNKNOWN"),
        ("source_doi", "other"),
        ("source_sha256", "0" * 64),
        ("condition", "UNKNOWN"),
        ("coordinates", "YAW_FROM_FLIGHT"),
        ("hemisphere", "unknown"),
        ("units", "pixels/s"),
        ("angular_velocity", math.inf),
        ("angular_velocity", math.nan),
        ("angular_velocity", True),
        ("angular_velocity", 1),
        ("start_ms", -1),
        ("start_ms", math.nan),
        ("start_ms", 0.15),
        ("end_ms", 0),
        ("end_ms", None),
        ("end_ms", math.inf),
        ("timing_rule", "INTERPOLATE"),
        ("aggregation", "FIT_TO_CALCIUM"),
        ("original_label", ""),
        ("mask", []),
        ("evidence", []),
    ],
)
def test_invalid_and_contradictory_fields(field, value):
    data = descriptor()
    data[field] = value
    with pytest.raises(ValueError):
        contract.parse_descriptor(data)


def test_unknown_metadata_remains_unknown_and_immutable():
    value = contract.parse_descriptor(descriptor())
    assert value.mask is None and value.hemisphere is None
    with pytest.raises(FrozenInstanceError):
        value.mask = ()


@pytest.mark.parametrize("condition", sorted(contract.CONDITIONS))
def test_all_conditions_refused_even_with_claimed_verified_fields(
    condition, authentic_artifact, monkeypatch
):
    from neurofly import experimental_neural_locomotion as solver

    def forbidden(*args, **kwargs):
        pytest.fail("closed Gate A must never advance neural state")

    monkeypatch.setattr(solver, "advance_neural", forbidden)
    data = descriptor()
    data["condition"] = condition
    for evidence in data["evidence"]:
        evidence["status"] = "SOURCE_VERIFIED"
    result = contract.assess(contract.parse_descriptor(data), authentic_artifact)[
        "result"
    ]
    assert result["scientific_status"] == "SOURCE_METADATA_INCOMPLETE"
    assert result["gate_a"] == "CLOSED"
    assert result["neural_substeps"] == 0
    assert result["normalized_neural_input"] is None
    assert result["model_output"] is None
    assert result["clipped_intervals"] is None  # not fabricated zero clipping
    assert result["calcium_equivalence"] is False


def test_descriptor_never_rewrites_source_or_old_classifications(authentic_artifact):
    from neurofly.empirical_hs_dnp15_benchmark import compatibility

    previous = copy.deepcopy(compatibility())
    data = descriptor()
    snapshot = copy.deepcopy(data)
    value = contract.parse_descriptor(data)
    a = contract.assess(value, authentic_artifact)
    b = contract.assess(value, authentic_artifact)
    assert a == b
    assert snapshot == data and previous == compatibility()
    assert a["result_sha256"] == contract.canonical_sha256(a["result"])
    data["original_label"] = "different documentation"
    assert contract.assess(contract.parse_descriptor(data), authentic_artifact) != a


def test_source_replacement_rejected(tmp_path):
    source = tmp_path / "fake.xlsx"
    source.write_bytes(b"not experimental evidence")
    with pytest.raises(ValueError, match="SHA-256"):
        contract.assess(contract.parse_descriptor(descriptor()), source)


@pytest.mark.parametrize(
    "side,start,end",
    [
        ("R", -0.1, 0.1),
        ("L", -0.1, 0.1),
        ("B", 0, 1),
        ("R", 1, 0),
        ("R", 0, math.inf),
        ("L", -4, -1),
    ],
)
def test_invalid_sectors_and_implicit_wrap_rejected(side, start, end):
    with pytest.raises(ValueError):
        contract.Sector(side, start, end, True)


def test_independent_anatomical_reflection_geometry_only():
    # Reflection alpha -> -alpha maps [a,b] to [-b,-a], swaps anatomical side.
    right = contract.Sector("R", math.pi / 4, math.pi / 2, True)
    left = contract.Sector("L", -math.pi / 2, -math.pi / 4, True)
    assert left.start_rad == -right.end_rad
    assert left.end_rad == -right.start_rad
    # This validates schema geometry, NOT a neural sensory transformation.
    data = descriptor()
    data.update(
        hemisphere="B",
        mask=[
            {"hemisphere": "R", "start_rad": 0, "end_rad": 1, "visible": False},
            {"hemisphere": "L", "start_rad": -1, "end_rad": 0, "visible": True},
        ],
    )
    value = contract.parse_descriptor(data)
    assert value.mask[0].visible is False
    assert value.mask[1].visible is True


def test_overlap_and_side_contradiction():
    data = descriptor()
    data["hemisphere"] = "R"
    sector = {"hemisphere": "R", "start_rad": 0, "end_rad": 1, "visible": True}
    data["mask"] = [sector, sector]
    with pytest.raises(ValueError, match="overlap"):
        contract.parse_descriptor(data)
    data["mask"] = [sector]
    data["hemisphere"] = "L"
    with pytest.raises(ValueError, match="contradictory"):
        contract.parse_descriptor(data)


def test_duplicate_evidence_and_unsupported_status():
    data = descriptor()
    data["evidence"][0] = data["evidence"][1]
    with pytest.raises(ValueError):
        contract.parse_descriptor(data)


def test_extra_evidence_and_top_level_fields_not_silently_discarded():
    data = descriptor()
    data["evidence"].append({"surprise": "must not disappear"})
    with pytest.raises(ValueError, match="evidence shape"):
        contract.parse_descriptor(data)
    data = descriptor()
    data["normalized_inputs"] = [1, -1]
    with pytest.raises(ValueError):
        contract.parse_descriptor(data)
    data = descriptor()
    data["evidence"][0]["status"] = "TRUST_ME"
    with pytest.raises(ValueError):
        contract.parse_descriptor(data)


def test_cli_scientific_refusal_success_invalid_failure_no_overwrite(
    tmp_path, authentic_artifact, capsys
):
    stimulus, output = tmp_path / "stimulus.json", tmp_path / "result.json"
    stimulus.write_text(json.dumps(descriptor()))
    args = [
        "--stimulus",
        str(stimulus),
        "--source",
        str(authentic_artifact),
        "--output",
        str(output),
    ]
    assert contract.main(args) == 0
    assert json.loads(output.read_text())["result"]["gate_a"] == "CLOSED"
    original = output.read_bytes()
    assert contract.main(args) == 2
    assert original == output.read_bytes()
    stimulus.write_text('{"schema": 1, "schema": 2}')
    assert contract.main(args) == 2
    assert "duplicate JSON key" in capsys.readouterr().err


def test_cli_repository_output_rejected(tmp_path):
    assert (
        contract.main(
            [
                "--stimulus",
                str(tmp_path / "missing"),
                "--source",
                str(tmp_path / "missing"),
                "--output",
                str(Path(contract.__file__).with_suffix(".json")),
            ]
        )
        == 2
    )
