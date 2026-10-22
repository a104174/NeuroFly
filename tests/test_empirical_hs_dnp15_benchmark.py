"""Synthetic XLSX bytes test parser mechanics only, never biological observations."""

import copy
import io
import json
import math
import os
import zipfile
from pathlib import Path

import pytest

from neurofly import empirical_hs_dnp15_benchmark as benchmark
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


def mechanics_workbook(cell='<c r="B2"><v>-0.25</v></c>', sheet="TEST_ONLY"):
    buffer = io.BytesIO()
    ns = benchmark.NS["s"]
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{ns}" xmlns:r="{benchmark.REL}">'
            f'<sheets><sheet name="{sheet}" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships><Relationship Id="rId1" '
            'Target="worksheets/sheet1.xml"/></Relationships>',
        )
        archive.writestr(
            "xl/sharedStrings.xml", f'<sst xmlns="{ns}"><si><t>mechanics</t></si></sst>'
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            f'<worksheet xmlns="{ns}"><sheetData><row r="2">'
            f'<c r="A2" t="s"><v>0</v></c>{cell}</row></sheetData></worksheet>',
        )
    return buffer.getvalue()


def test_mechanics_sheet_cell_coordinates_shared_strings_and_signed_numeric():
    assert benchmark.parse_xlsx(mechanics_workbook()) == {
        "TEST_ONLY": {"A2": "mechanics", "B2": -0.25}
    }


@pytest.mark.parametrize(
    "cell",
    [
        '<c r="B2"><v>NaN</v></c>',
        '<c r="B2"><v>INF</v></c>',
        '<c r="B2"><v>text</v></c>',
        '<c r="B2"/>',
        '<c r="B2"><f>1+1</f><v>2</v></c>',
        '<c r="B2" t="b"><v>1</v></c>',
        '<c r="B2" t="inlineStr"><is><t>x</t></is></c>',
        '<c r="B2" t="s"><v>-1</v></c>',
        '<c r="A2"><v>1</v></c>',
        '<c r="../"><v>1</v></c>',
    ],
)
def test_invalid_ambiguous_or_unsupported_cells_fail(cell):
    with pytest.raises(ValueError):
        benchmark.parse_xlsx(mechanics_workbook(cell))


@pytest.mark.parametrize("raw", [b"not a zip", b"PK", b"x" * 1_000_001])
def test_corrupt_or_oversize_workbook(raw):
    with pytest.raises(ValueError):
        benchmark.parse_xlsx(raw)


def test_source_replacement_rejected_even_for_readable_synthetic_workbook():
    with pytest.raises(ValueError, match="SHA-256"):
        benchmark.extract_source(mechanics_workbook())


@pytest.mark.parametrize(
    "replacement",
    [
        ('Target="worksheets/sheet1.xml"', 'Target="../sheet.xml"'),
        ('Target="worksheets/sheet1.xml"', 'Target="x" TargetMode="External"'),
        ('name="TEST_ONLY"', 'name="TEST_ONLY" state="hidden"'),
        ("</sheetData>", "</sheetData><mergeCells/>"),
        ("<si><t>mechanics</t></si>", "<si><r><t>mechanics</t></r></si>"),
    ],
)
def test_unimplemented_excel_structures_fail_explicitly(replacement):
    source = mechanics_workbook()
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(source)) as old:
        with zipfile.ZipFile(output, "w") as new:
            for name in old.namelist():
                raw = old.read(name).decode().replace(*replacement)
                new.writestr(name, raw)
    with pytest.raises(ValueError):
        benchmark.parse_xlsx(output.getvalue())


def test_source_manifest_measurement_and_rights_are_explicit():
    source = benchmark.source_manifest()
    assert source["sha256"] == benchmark.SOURCE_SHA
    assert source["figure"] == "Figure 1h"
    assert source["measurement"]["units"] == "dimensionless"
    assert "roi_ids" in source["measurement"]["missing"]
    assert "fly_ids" in source["measurement"]["missing"]
    assert source["zenodo"]["downloaded"] is False
    assert (
        "No separate license"
        in source["storage_and_rights"]["workbook_separate_license"]
    )


def test_missing_or_incorrect_manifest_identity(monkeypatch, tmp_path):
    path = tmp_path / "manifest.json"
    source = benchmark.source_manifest()
    source["sha256"] = "0" * 64
    path.write_text(json.dumps(source))
    monkeypatch.setattr(benchmark, "MANIFEST", path)
    with pytest.raises(ValueError, match="manifest identity"):
        benchmark.source_manifest()


@pytest.mark.parametrize("values", [(0, 0), (1e-14, 0), (math.nan, 1), (math.inf, 1)])
def test_index_rejects_undefined_near_zero_or_nonfinite(values):
    with pytest.raises(ValueError):
        benchmark.discrimination_index(*values)


def test_index_preserves_sign_without_model_equivalence():
    assert benchmark.discrimination_index(1, 3) == -0.5
    assert benchmark.discrimination_index(-1, 3) == -1
    assert benchmark.discrimination_index(3, 1) == 0.5


@pytest.fixture(scope="module")
def real_probes():
    return benchmark.run_probes()


def test_probes_execute_pinned_solver_and_timebase(real_probes):
    model, probes = real_probes
    assert model["solver"] == "experimental_neural_locomotion.advance_neural"
    assert model["selected_HS_R"] == [10015, 10016, 10023]
    assert model["selected_DNp15_R_L"] == [11215, 12069]
    assert len(probes) == 7
    assert sum(p["substeps"] for p in probes.values()) == 70_000
    for probe in probes.values():
        assert len(probe["records"]) == 50
        assert probe["records"][0]["hs_right_left_mean_proxy"] == [0, 0]
        assert probe["records"][0]["dnp15_right_left_proxy"] == [0, 0]
        assert probe["records"][0]["mean_readout_eq"] == 0


def test_yaw_sign_mirror_and_translation_cancellation(real_probes):
    _, probes = real_probes
    positive = probes["YAW_PLUS"]["records"]
    negative = probes["YAW_MINUS"]["records"]
    assert positive[25]["mean_readout_eq"] < 0
    assert negative[25]["mean_readout_eq"] > 0
    for p, n in zip(positive, negative, strict=True):
        assert p["mean_readout_eq"] == -n["mean_readout_eq"]
    for name in ("STATIC", "FORWARD", "REVERSE"):
        assert all(r["mean_readout_eq"] == 0 for r in probes[name]["records"])
    assert probes["LATERAL_PLUS"]["peak_absolute_mean_readout_eq"] > 0


def test_initial_hold_state_continuity_and_recovery(real_probes):
    _, probes = real_probes
    rows = probes["YAW_PLUS"]["records"]
    assert all(r["mean_readout_eq"] == 0 for r in rows[:6])
    assert rows[6]["mean_readout_eq"] < 0
    assert rows[7]["dnp15_right_left_proxy"][0] < rows[6]["dnp15_right_left_proxy"][0]
    assert abs(rows[-1]["mean_readout_eq"]) < 1e-12


def test_independent_execution_is_deterministic_and_unknown_probe_fails(real_probes):
    model, probes = real_probes
    assert benchmark.run_probes() == (model, probes)
    with pytest.raises(ValueError):
        benchmark.probe_frames("UNILATERAL_LED")


def test_comparability_never_claims_direct_calcium_or_model_di(real_probes):
    matrix = benchmark.compatibility()
    assert all(row["category"] != "DIRECTLY_COMPARABLE" for row in matrix)
    assert matrix[2]["category"] == "NOT_COMPARABLE"
    assert matrix[3]["category"] == "SOURCE_DATA_UNAVAILABLE"
    rows = benchmark.assessment(real_probes[1])
    assert rows[1]["classification"] == "NOT_COMPARABLE"
    assert rows[1]["model_output"] is None
    assert not any("COMPATIBLE" in r["classification"] for r in rows)


def official_source():
    path = os.environ.get("NEUROFLY_FIG1_SOURCE")
    if not path:
        pytest.skip("official external workbook not supplied; no synthetic replacement")
    return Path(path)


def test_official_extraction_counts_semantics_and_descriptive_results():
    result = benchmark.extract_source(official_source().read_bytes())
    assert result["inventory"]["numeric_observations"] == 24
    assert result["inventory"]["sheets"] == ["1h"]
    assert result["groups"]["DNp15"]["n_roi_indices"] == 7
    assert result["groups"]["HS"]["n_roi_indices"] == 17
    assert result["groups"]["DNp15"]["mean"] == pytest.approx(-0.6409234916912421)
    for group in result["groups"].values():
        assert group["confidence_interval"] is None
        assert group["fly_ids_and_clustering"] is None
        assert group["roi_ids"] is None
    assert result["published_p"]["recomputed"] is False


@pytest.mark.parametrize(
    "fault", ["sheet", "header", "label", "column", "nonfinite", "range", "extra"]
)
def test_layout_validation_independent_of_checksum(monkeypatch, fault):
    # Fault injection after parsing authentic bytes tests semantic defenses only.
    # No synthetic workbook is ever accepted as an experimental source.
    raw = official_source().read_bytes()
    parsed = benchmark.parse_xlsx(raw)
    cells = parsed["1h"]
    if fault == "sheet":
        parsed = {"wrong": cells}
    elif fault == "header":
        cells["A1"] = "unknown normalization"
    elif fault == "label":
        cells["A2"] = "ambiguous"
    elif fault == "column":
        cells.pop("B2")
    elif fault == "nonfinite":
        cells["B2"] = math.nan
    elif fault == "range":
        cells["B2"] = 1.1
    else:
        cells["Z9"] = 0.0
    monkeypatch.setattr(benchmark, "parse_xlsx", lambda _: parsed)
    with pytest.raises(ValueError):
        benchmark.extract_source(raw)


def test_full_output_repeatability_identity_and_reporting(monkeypatch, real_probes):
    source = official_source()
    # Reuse only already executed real probe results; no artificial neural fixture.
    monkeypatch.setattr(benchmark, "run_probes", lambda: copy.deepcopy(real_probes))
    first = benchmark.benchmark(source)
    second = benchmark.benchmark(source)
    assert first["result"] == second["result"]
    assert first["result_sha256"] == canonical_sha256(second["result"])
    assert first["result"]["simulation"]["flight_plant_executed"] is False
    assert "source_access_date" not in first["result"]
    report = benchmark.readable_report(first)
    assert "not empirical agreement" in report
    assert "No independent-fly statistics" in report


def test_cli_missing_source_prohibited_output_and_solver_failure(tmp_path, capsys):
    missing = tmp_path / "missing.xlsx"
    output = tmp_path / "result.json"
    assert benchmark.main(["--source", str(missing), "--output", str(output)]) == 2
    assert not output.exists()
    assert "COMPUTATION_FAILED" in capsys.readouterr().err
    assert (
        benchmark.main(
            ["--source", str(missing), "--output", str(benchmark.ROOT / "never.json")]
        )
        == 2
    )
    output.write_text("preserve")
    assert benchmark.main(["--source", str(missing), "--output", str(output)]) == 2
    assert output.read_text() == "preserve"


def test_cli_writes_both_outputs_and_rejects_unwritable_parent(monkeypatch, tmp_path):
    source = official_source()
    output = tmp_path / "result.json"
    assert benchmark.main(["--source", str(source), "--output", str(output)]) == 0
    data = json.loads(output.read_text())
    assert data["result_sha256"] == canonical_sha256(data["result"])
    assert output.with_suffix(".md").exists()
    assert (
        benchmark.main(
            ["--source", str(source), "--output", str(tmp_path / "missing" / "x.json")]
        )
        == 2
    )


def test_failed_reference_execution_does_not_produce_report(monkeypatch, tmp_path):
    source = official_source()

    def fail():
        raise ValueError("pinned neural contract mismatch")

    monkeypatch.setattr(benchmark, "run_probes", fail)
    output = tmp_path / "failed.json"
    assert benchmark.main(["--source", str(source), "--output", str(output)]) == 2
    assert not output.exists()
    assert not output.with_suffix(".md").exists()
