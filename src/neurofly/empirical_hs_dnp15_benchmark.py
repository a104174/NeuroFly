"""Offline v9.2 source inventory and explicitly non-equivalent model diagnostics.

No calcium forward model, fitting, input substitution or flight modification.
The only empirical input accepted is the byte-pinned official Figure 1 workbook.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import statistics
import sys
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from neurofly import hs_dnp15_neural_validation as frozen
from neurofly.neural_flight_reference import neural_reference
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

SCHEMA = "empirical_hs_dnp15_response_benchmark_v9_2"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/science/empirical_hs_dnp15_v9_2_source.json"
SOURCE_SHA = "b5a36e2363279a1bf908bcdcc9da7dda93ce6710487ceb31add0a284d9db9488"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CONDITIONS = (
    "STATIC",
    "YAW_PLUS",
    "YAW_MINUS",
    "FORWARD",
    "REVERSE",
    "LATERAL_PLUS",
    "LATERAL_MINUS",
)


def source_manifest():
    value = json.loads(MANIFEST.read_bytes())
    if (
        value["schema"] != "empirical_hs_dnp15_source_v9_2"
        or value["doi"] != "10.1038/s41593-025-01948-9"
        or value["figure"] != "Figure 1h"
        or value["sha256"] != SOURCE_SHA
        or value["sheet"] != "1h"
    ):
        raise ValueError("unsupported source manifest identity")
    return value


def parse_xlsx(raw):
    """Bounded ZIP/XML reader for the literal-cell subset used by this source.

    Unsupported formulas, merged cells, external links, rich inline strings and
    unexpected cell types fail explicitly. Never execute spreadsheet content.
    Synthetic files may test this mechanics function, never the benchmark.
    """
    if len(raw) > 1_000_000:
        raise ValueError("source workbook exceeds 1 MB limit")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            names = [entry.filename for entry in infos]
            if (
                len(names) != len(set(names))
                or len(names) > 40
                or sum(entry.file_size for entry in infos) > 4_000_000
                or any(entry.flag_bits & 1 for entry in infos)
                or any(
                    "externalLinks/" in name or "vbaProject" in name for name in names
                )
            ):
                raise ValueError("unsupported ZIP members/size/encryption/links")

            def xml(name):
                content = archive.read(name)
                if b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
                    raise ValueError("XML entities are unsupported")
                return ET.fromstring(content)

            workbook = xml("xl/workbook.xml")
            relationships = {}
            for relation in xml("xl/_rels/workbook.xml.rels"):
                if relation.get("TargetMode") == "External":
                    raise ValueError("external workbook relationship")
                if relation.get("Id") in relationships:
                    raise ValueError("duplicate relationship")
                relationships[relation.get("Id")] = relation.get("Target")
            shared = []
            if "xl/sharedStrings.xml" in names:
                for item in xml("xl/sharedStrings.xml"):
                    if any(child.tag != f"{{{NS['s']}}}t" for child in item):
                        raise ValueError("unsupported rich shared string")
                    shared.append("".join(item.itertext()))
            result = {}
            for sheet in workbook.findall("s:sheets/s:sheet", NS):
                name = sheet.get("name")
                if (
                    not name
                    or name in result
                    or sheet.get("state", "visible") != "visible"
                ):
                    raise ValueError("duplicate/hidden/unnamed worksheet")
                target = relationships[sheet.get(f"{{{REL}}}id")]
                if not re.fullmatch(r"worksheets/sheet[1-9][0-9]*\.xml", target):
                    raise ValueError("unsupported worksheet target")
                root = xml("xl/" + target)
                if root.find("s:mergeCells", NS) is not None:
                    raise ValueError("merged cells are unsupported")
                cells = {}
                for cell in root.findall("s:sheetData/s:row/s:c", NS):
                    address = cell.get("r")
                    if (
                        not address
                        or not re.fullmatch(r"[A-Z]{1,2}[1-9][0-9]{0,3}", address)
                        or address in cells
                        or cell.find("s:f", NS) is not None
                    ):
                        raise ValueError("invalid/duplicate cell or formula")
                    kind = cell.get("t", "n")
                    node = cell.find("s:v", NS)
                    if node is None or node.text is None:
                        raise ValueError("missing cell value")
                    if kind == "s":
                        index = int(node.text)
                        if not 0 <= index < len(shared):
                            raise ValueError("invalid shared-string index")
                        value = shared[index]
                    elif kind == "n":
                        value = float(node.text)
                        if not math.isfinite(value):
                            raise ValueError("non-finite observation")
                    else:
                        raise ValueError("unsupported cell type " + kind)
                    cells[address] = value
                result[name] = cells
            if not result:
                raise ValueError("no worksheets")
            return result
    except (
        zipfile.BadZipFile,
        ET.ParseError,
        KeyError,
        IndexError,
        TypeError,
        NotImplementedError,
    ) as exc:
        raise ValueError("corrupt or unsupported XLSX structure") from exc


def extract_source(raw):
    """Validate literal semantics as well as the exact external byte identity."""
    manifest = source_manifest()
    workbook = parse_xlsx(raw)
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("source SHA-256 mismatch; no silent source replacement")
    if set(workbook) != {"1h"}:
        raise ValueError("unexpected source worksheets")
    cells = workbook["1h"]
    expected = {"A1", "A2", "A3", "A4"}
    groups = {}
    for label, row, count in (("DNp15", 2, 7), ("HS", 3, 17)):
        if cells.get(f"A{row}") != label:
            raise ValueError("ambiguous cell-type label")
        addresses = [f"{chr(66 + i)}{row}" for i in range(count)]
        expected.update(addresses)
        values = [cells.get(address) for address in addresses]
        if any(type(v) is not float or not -1 <= v <= 1 for v in values):
            raise ValueError("missing/non-numeric/out-of-range discrimination index")
        groups[label] = {
            "measurement": manifest["measurement"]["variable"],
            "source_cells": addresses,
            "n_roi_indices": count,
            "fly_count_from_paper_not_workbook": manifest["mapping"][label][
                "paper_fly_count"
            ],
            "roi_ids": None,
            "fly_ids_and_clustering": None,
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "minimum": min(values),
            "maximum": max(values),
            "negative_count": sum(v < 0 for v in values),
            "confidence_interval": None,
            "inference": "DESCRIPTIVE_ONLY_NO_INDEPENDENT_FLY_ASSUMPTION",
        }
    if (
        set(cells) != expected
        or cells["A1"] != manifest["header"]
        or cells["A4"] != "p = 0.00076248"
    ):
        raise ValueError("unexpected cells/header/statistic")
    return {
        "inventory": {
            "sheets": ["1h"],
            "nonempty_rows": 4,
            "nonempty_cells": len(cells),
            "numeric_observations": 24,
            "column_semantics": "A labels, B:H DNp15 ROI DI, B:R HS ROI DI",
            "missing_values_within_declared_ranges": 0,
            "raw_calcium_or_trace_timepoints": False,
            "reported_group_means_sem_sd_ci_in_workbook": False,
        },
        "groups": groups,
        "published_p": {
            "value": 0.00076248,
            "source_cell": "A4",
            "recomputed": False,
            "method_from_caption": "two-sided Wilcoxon rank-sum",
            "limitation": "no fly-to-ROI clustering supplied; no new inference made",
        },
    }


def discrimination_index(translation, yaw):
    """Arithmetic only; using this on model proxies is prohibited in this benchmark."""
    if any(
        type(v) not in (float, int) or not math.isfinite(v) for v in (translation, yaw)
    ):
        raise ValueError("non-finite response")
    denominator = abs(translation) + abs(yaw)
    if denominator <= 1e-12:
        raise ValueError("undefined or near-zero discrimination denominator")
    return (translation - yaw) / denominator


def probe_frames(condition):
    if condition not in CONDITIONS:
        raise ValueError("unsupported diagnostic pose condition")
    frames = []
    for step in range(51):
        elapsed = min(20, max(0, step - 5)) * 0.02
        x, z, yaw = 0.0, 0.0, 0.0
        if condition.startswith("YAW_"):
            yaw = elapsed * (0.5 if condition == "YAW_PLUS" else -0.5)
        elif condition in ("FORWARD", "REVERSE"):
            z = elapsed * (0.18 if condition == "FORWARD" else -0.18)
        elif condition.startswith("LATERAL_"):
            x = elapsed * (0.18 if condition == "LATERAL_PLUS" else -0.18)
        frames.append(
            {"step": step, "time": step * 0.02, "position": [x, 0.2, z], "heading": yaw}
        )
    return frames


def run_probes():
    probes = {}
    identity = None
    for name in CONDITIONS:
        result = neural_reference(probe_frames(name))
        if identity is None:
            identity = {
                "source_raw_sha256": result["source_raw_sha256"],
                "model_config_schema": frozen.CONFIG_SCHEMA,
                "preregistration_id": frozen.PREREGISTRATION_ID,
                "neural_contract_sha256": result["neural_contract_sha256"],
                "dataset": "male-cns:v1.0",
                "selected_HS_R": [10015, 10016, 10023],
                "selected_HS_L": [10034, 10181, 10419],
                "selected_DNp15_R_L": [11215, 12069],
                "solver": "experimental_neural_locomotion.advance_neural",
                "observer": "experimental_neural_locomotion.observation",
            }
        # neural_reference checks the pinned source and contract on every call.
        records = []
        for row in result["records"]:
            observation = row["observation"]
            records.append(
                {
                    "step": row["step"],
                    "time_s": row["step"] * 0.02,
                    "neural_after_time_s": (row["step"] + 1) * 0.02,
                    "input_clipped": (
                        observation["clipped"]
                        if observation is not None
                        else [False] * 2
                    ),
                    "right_left_input": (
                        [observation["right"], observation["left"]]
                        if observation is not None
                        else [0.0, 0.0]
                    ),
                    "hs_right_left_mean_proxy": [
                        statistics.mean(row["hs_after"][:3]),
                        statistics.mean(row["hs_after"][3:]),
                    ],
                    "dnp15_right_left_proxy": row["dn_after"],
                    "mean_readout_eq": row["mean_yaw_drive_eq"],
                    "orientation_increment_eq": row["orientation_increment_eq"],
                }
            )
        probes[name] = {
            "classification": "MODEL_SIDE_SURROGATE_ONLY",
            "substeps": result["substeps"],
            "last_motion_boundary": records[25],
            "final_recovery_boundary": records[-1],
            "peak_absolute_mean_readout_eq": max(
                abs(r["mean_readout_eq"]) for r in records
            ),
            "records": records,
        }
    return identity, probes


def compatibility():
    return [
        {
            "condition": "binocular yaw-like LED motion",
            "category": "MODEL_SIDE_SURROGATE_ONLY",
            "reason": (
                "imposed self-yaw changes two landmark bearings; no retinal/LED "
                "field or speed equivalence"
            ),
        },
        {
            "condition": "binocular symmetric bFtoB LED motion",
            "category": "MODEL_SIDE_SURROGATE_ONLY",
            "reason": (
                "self-translation changes finite landmarks; not a binocular "
                "visual-field stimulus"
            ),
        },
        {
            "condition": "unilateral left/right FtoB/BtoF",
            "category": "NOT_COMPARABLE",
            "reason": (
                "no independent unilateral moving-field input through the frozen "
                "encoder"
            ),
        },
        {
            "condition": "directional calcium traces / response amplitudes",
            "category": "SOURCE_DATA_UNAVAILABLE",
            "reason": (
                "Figure 1h workbook contains derived DI only; no traces, "
                "hemisphere or component responses"
            ),
        },
        {
            "condition": "published bFtoB-yaw DI versus model DI",
            "category": "NOT_COMPARABLE",
            "reason": (
                "neither stimuli nor calcium/model observables have an operational "
                "equivalence; no model DI calculated"
            ),
        },
    ]


def assessment(probes):
    return [
        {
            "claim_id": "DIRECTION",
            "source_reference": "10.1038/s41593-025-01948-9 Fig 1g",
            "experimental_condition": "unilateral/bilateral horizontal visual motion",
            "claim": "model-side mirrored yaw gives opposite signed readouts",
            "classification": "MODEL_SIDE_ONLY",
            "experimental_measurement": None,
            "method": "same frozen observer/solver, opposite imposed pose yaw",
            "model_output": {
                name: probes[name]["last_motion_boundary"]["mean_readout_eq"]
                for name in ("YAW_PLUS", "YAW_MINUS")
            },
            "limitation": (
                "not a test of biological preferred direction; workbook lacks "
                "directional responses"
            ),
        },
        {
            "claim_id": "ROTATION_SELECTIVITY",
            "source_reference": "10.1038/s41593-025-01948-9 Fig 1h, sheet 1h",
            "experimental_condition": "binocular bFtoB versus yaw",
            "claim": "reduced model reproduces published DNp15 bFtoB-yaw DI",
            "classification": "NOT_COMPARABLE",
            "experimental_measurement": "published derived per-ROI DI, sheet 1h",
            "model_output": None,
            "method": "comparability gate refuses a surrogate DI",
            "limitation": (
                "no matched stimulus or calcium observation model; no quantitative "
                "agreement or contradiction asserted"
            ),
        },
        {
            "claim_id": "BINOCULAR_NETWORK",
            "source_reference": "10.1038/s41593-025-01948-9 Figs 1g, 2-6",
            "experimental_condition": "unilateral versus binocular visual fields",
            "claim": (
                "reduced feedforward motif reproduces experimental binocular "
                "interactions"
            ),
            "classification": "INSUFFICIENT_DATA",
            "experimental_measurement": "Figure 1h DI only; Fig 1g traces absent",
            "model_output": (
                "same-side means without H2/bIPS/uLPTCrn, recurrence or electrical "
                "interactions"
            ),
            "method": "circuit coverage and workbook inventory",
            "limitation": (
                "bilateral readout subtraction is not evidence for the full "
                "disinhibitory network"
            ),
        },
        {
            "claim_id": "AIRBORNE_YAW_GAIN",
            "source_reference": "10.1038/s41593-025-01948-9 Fig 1h; Methods",
            "experimental_condition": "immobilized two-photon imaging",
            "claim": "calcium selectivity validates the v9 airborne yaw mapping",
            "classification": "NOT_COMPARABLE",
            "experimental_measurement": (
                "immobilized calcium-derived DI, not free-flight angular velocity"
            ),
            "model_output": (
                "v9 projection remains unchanged and is not executed by this benchmark"
            ),
            "method": "measurement/units gate",
            "limitation": (
                "no conversion of proxy state or fluorescence into measured body yaw"
            ),
        },
    ]


def benchmark(source):
    source = Path(source)
    if source.stat().st_size > 1_000_000:
        raise ValueError("source workbook exceeds 1 MB limit")
    start = time.perf_counter()
    raw = source.read_bytes()
    loaded = time.perf_counter()
    extracted = extract_source(raw)
    parsed = time.perf_counter()
    model, probes = run_probes()
    simulated = time.perf_counter()
    manifest = source_manifest()
    # Retrieval date/path and timing are excluded from scientific content identity.
    authority = {k: v for k, v in manifest.items() if k != "access_date"}
    content = {
        "schema": SCHEMA,
        "execution_status": "COMPLETED",
        "scientific_status": "STIMULUS_AND_OBSERVABLE_INCOMPATIBILITY",
        "source": authority,
        "experimental_results": extracted,
        "model": model,
        "simulation": {
            "adapter": "existing_horizontal_landmark_pose_diagnostics_v9_2",
            "world": "Y_UP_X_RIGHT_Z_FORWARD_heading_positive_toward_plus_X",
            "landmarks_x_z": [[0.6, 0.4], [-0.6, 0.4]],
            "altitude": "excluded from observation; initial Y=0.2",
            "initial_state": (
                "zero six HS and two DNp15 proxies; pose XYZ=[0,0.2,0], yaw=0"
            ),
            "body_dt_s": 0.02,
            "neural_dt_ms": 0.1,
            "substeps_per_interval": 200,
            "boundaries": 51,
            "duration_s": 1.0,
            "motion_interval_s": [0.1, 0.5],
            "pose_speeds": {"yaw_rad_s": 0.5, "translation_scene_units_s": 0.18},
            "condition_order": list(CONDITIONS),
            "reset": (
                "independent zero state per condition; persistent within condition"
            ),
            "units": "dimensionless model proxies; not calcium, voltage or firing rate",
            "reporting": "20ms boundaries; no calcium resampling or forward transform",
            "record_timing": (
                "time_s is interval start and observation availability; "
                "hs/dnp15 proxy values are after the outgoing neural interval "
                "at neural_after_time_s; readout is that interval's mean"
            ),
            "seed": None,
            "flight_plant_executed": False,
        },
        "compatibility": compatibility(),
        "model_probes": probes,
        "assessments": assessment(probes),
        "limitations": [
            "No supported direct model-versus-experiment quantitative comparison.",
            (
                "ROI indices have no fly clustering; no new p-values, CI or SEM "
                "calculated."
            ),
            "Published DI is extracted, never recomputed from unavailable traces.",
            "Same-side feedforward proxies omit H2, bIPS, uLPTCrn and disinhibition.",
            "No inference about airborne yaw calibration or calcium dynamics.",
        ],
    }
    return {
        "result": content,
        "result_sha256": canonical_sha256(content),
        "metadata_not_hashed": {
            "source_access_date": manifest["access_date"],
            "python": sys.version.split()[0],
            "diagnostics_seconds": {
                "load": loaded - start,
                "extraction": parsed - loaded,
                "model_probes": simulated - parsed,
            },
            "source_bytes": len(raw),
            "total_neural_substeps": sum(p["substeps"] for p in probes.values()),
        },
    }


def readable_report(envelope):
    result = envelope["result"]
    lines = [
        "# NeuroFly empirical HS/DNp15 response benchmark v9.2",
        "",
        (
            "Execution: COMPLETED. Scientific outcome: "
            "STIMULUS_AND_OBSERVABLE_INCOMPATIBILITY."
        ),
        (
            "This is an extraction and model-side diagnostic result, not "
            "empirical agreement."
        ),
        f"Result SHA-256: {envelope['result_sha256']}",
        f"Source: {result['source']['url']}",
        f"Source SHA-256: {SOURCE_SHA}",
        "",
        "Published individual derived ROI indices (not raw calcium):",
    ]
    for label, group in result["experimental_results"]["groups"].items():
        lines.append(
            f"- {label}: n={group['n_roi_indices']} ROIs; "
            f"mean DI={group['mean']:.10f}, median={group['median']:.10f}, "
            f"range=[{group['minimum']:.10f}, {group['maximum']:.10f}]."
        )
    lines += [
        (
            "No fly grouping, component OF values, traces or trial data are in "
            "this workbook."
        ),
        "No independent-fly statistics, confidence intervals or model DI are computed.",
        "",
        "## Comparability",
    ]
    for item in result["compatibility"]:
        lines.append(f"- {item['condition']}: {item['category']}. {item['reason']}")
    lines += ["", "## Model-side probes (dimensionless, not fluorescence)"]
    for name, probe in result["model_probes"].items():
        row = probe["last_motion_boundary"]
        lines.append(
            f"- {name} at {row['time_s']:.2f}s: "
            f"HS R/L={row['hs_right_left_mean_proxy']}, "
            f"DNp15 R/L={row['dnp15_right_left_proxy']}, "
            f"readout={row['mean_readout_eq']:.12g}."
        )
    lines += ["", "## Assessment"]
    for item in result["assessments"]:
        lines.append(
            f"- {item['claim_id']}: {item['classification']}. {item['limitation']}"
        )
    lines += ["", *result["limitations"], ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, required=True, help="new JSON output path"
    )
    args = parser.parse_args(argv)
    summary = args.output.with_suffix(".md")
    try:
        # Generated results stay outside the published source tree.
        for path in (args.output, summary):
            if path.resolve().is_relative_to(ROOT) or path.exists():
                raise ValueError("outputs must be new paths outside the repository")
            if not path.parent.is_dir():
                raise ValueError("output parent directory does not exist")
        if summary == args.output:
            raise ValueError("output must have a non-Markdown suffix")
        envelope = benchmark(args.source)
        raw = canonical_json_bytes(envelope, newline=True)
        report = readable_report(envelope)
        written = []
        try:
            for path, data in ((args.output, raw), (summary, report.encode())):
                with path.open("xb") as stream:
                    written.append(path)
                    stream.write(data)
        except OSError:
            for path in written:
                path.unlink(missing_ok=True)
            raise
        print(
            json.dumps(
                {
                    "execution": "COMPLETED",
                    "scientific_status": envelope["result"]["scientific_status"],
                    "result_sha256": envelope["result_sha256"],
                    "json_bytes": len(raw),
                    "report": str(summary),
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(f"COMPUTATION_FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
