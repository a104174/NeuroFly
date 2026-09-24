"""Phase 7C: source-validated, non-physiological column-space analysis.

Run with ``python -m research.relative_column_space --workbook PATH --output PATH``.
The only distance unit is a step on the documented MaleCNS hex lattice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import median
from xml.etree import ElementTree
from zipfile import ZipFile

from neurofly.malecns.column_snapshot import load_column_contract
from neurofly.malecns.columns import ColumnInputRecord
from neurofly.malecns.contract import load_circuit_contract

SCHEMA = "malecns_relative_retinotopy_analysis_v1"
WORKBOOK_SHA256 = "d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3"
DEFAULT_ROOT = Path("data/derived/malecns/looming_giant_fiber_v1")
FIXED_BODIES = (12032, 16128, 11498, 14465)
PROOF_BODIES = (*FIXED_BODIES, 12349, 16138, 12384, 17551)
COLUMN_RE = re.compile(r"^ME_([LR])_col_(\d+)_(\d+)$")
XML_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

# Explicit synthetic addresses, never physical stimulus locations or degrees.
STIMULI = (
    ("L_33_29_r1", "L", (33, 29), 1),
    ("L_33_29_r4", "L", (33, 29), 4),
    ("L_18_04_r2", "L", (18, 4), 2),
    ("R_23_09_r1", "R", (23, 9), 1),
    ("R_23_09_r4", "R", (23, 9), 4),
    ("R_23_11_r2", "R", (23, 11), 2),
)


def hex_distance(first: tuple[int, int], second: tuple[int, int]) -> int:
    """Six-neighbour p/q distance: ±p, ±q, ±(p+q); hex1=q, hex2=p."""
    dq = first[0] - second[0]
    dp = first[1] - second[1]
    return max(abs(dp), abs(dq), abs(dp - dq))


def _hex_norm(first: tuple[float, float], second: tuple[float, float]) -> float:
    dq = first[0] - second[0]
    dp = first[1] - second[1]
    return max(abs(dp), abs(dq), abs(dp - dq))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cell_text(cell: ElementTree.Element, shared: list[str]) -> str:
    value = cell.find("m:v", XML_NS)
    if value is None or value.text is None:
        return ""
    return shared[int(value.text)] if cell.attrib.get("t") == "s" else value.text


def load_official_columns(path: Path) -> dict[str, dict[tuple[int, int], str]]:
    """Read only the pinned bilateral key/class columns of the official XLSX."""
    if _sha256(path) != WORKBOOK_SHA256:
        raise ValueError("Official column workbook SHA-256 mismatch")
    result: dict[str, dict[tuple[int, int], str]] = {"L": {}, "R": {}}
    with ZipFile(path) as workbook:
        strings_root = ElementTree.fromstring(workbook.read("xl/sharedStrings.xml"))
        shared = [
            "".join(text.text or "" for text in item.findall(".//m:t", XML_NS))
            for item in strings_root.findall("m:si", XML_NS)
        ]
        for side, sheet in (("R", "sheet1.xml"), ("L", "sheet2.xml")):
            root = ElementTree.fromstring(workbook.read(f"xl/worksheets/{sheet}"))
            for row in root.findall(".//m:row", XML_NS)[1:]:
                cells = {
                    re.match(r"[A-Z]+", cell.attrib["r"]).group(): _cell_text(
                        cell, shared
                    )
                    for cell in row.findall("m:c", XML_NS)
                }
                match = COLUMN_RE.fullmatch(cells.get("A", ""))
                if match is None or match.group(1) != side:
                    raise ValueError("Invalid official column identity or side")
                coord = (int(match.group(2)), int(match.group(3)))
                if coord in result[side]:
                    raise ValueError("Duplicate official column coordinate")
                result[side][coord] = cells.get("G", "")
    if (len(result["L"]), len(result["R"])) != (880, 892):
        raise ValueError("Official bilateral column counts changed")
    return result


def _centroid(
    records: tuple[ColumnInputRecord, ...], *, structural: bool
) -> tuple[float, float]:
    weights = [record.input_count if structural else 1 for record in records]
    total = sum(weights)
    return (
        sum(record.ol_hex1 * weight for record, weight in zip(records, weights))
        / total,
        sum(record.ol_hex2 * weight for record, weight in zip(records, weights))
        / total,
    )


def _spread(
    records: tuple[ColumnInputRecord, ...],
    centre: tuple[float, float],
    *,
    structural: bool,
) -> float:
    weights = [record.input_count if structural else 1 for record in records]
    return math.sqrt(
        sum(
            weight * _hex_norm((record.ol_hex1, record.ol_hex2), centre) ** 2
            for record, weight in zip(records, weights)
        )
        / sum(weights)
    )


def body_anatomy(
    records: tuple[ColumnInputRecord, ...],
    *,
    relevant_sites: int,
    edge_hexes: set[tuple[int, int]],
    classified_hexes: set[tuple[int, int]],
) -> dict[str, object]:
    """Centres/spreads describe source-column occupancy, not functional RFs."""
    if not records or relevant_sites <= 0:
        raise ValueError("A body needs assigned and relevant source sites")
    sides = {record.eye_side for record in records}
    if len(sides) != 1:
        raise ValueError("A body cannot mix left and right column systems")
    if any(record.input_count <= 0 for record in records):
        raise ValueError("Source counts must be positive")
    assigned = sum(record.input_count for record in records)
    if assigned > relevant_sites:
        raise ValueError("Assigned sites exceed relevant source sites")
    unique_hexes = {(record.ol_hex1, record.ol_hex2) for record in records}
    known_hexes = unique_hexes & classified_hexes
    plain = _centroid(records, structural=False)
    weighted = _centroid(records, structural=True)
    return {
        "source_column_count": len(records),
        "unique_hex_count": len(unique_hexes),
        "assigned_sites": assigned,
        "relevant_sites": relevant_sites,
        "assigned_fraction": assigned / relevant_sites,
        "missing_fraction": (relevant_sites - assigned) / relevant_sites,
        "unweighted_anatomical_column_centroid": plain,
        "structural_input_weighted_anatomical_column_centroid": weighted,
        "unweighted_rms_hex_spread": _spread(records, plain, structural=False),
        "structural_input_weighted_rms_hex_spread": _spread(
            records, weighted, structural=True
        ),
        "edge_hex_fraction_of_classified": (
            len(known_hexes & edge_hexes) / len(known_hexes) if known_hexes else None
        ),
        "workbook_unclassified_hex_count": len(unique_hexes - known_hexes),
    }


def anatomical_exposure(
    records: tuple[ColumnInputRecord, ...],
    *,
    stimulus_side: str,
    active_hexes: set[tuple[int, int]],
) -> dict[str, float]:
    """Binary, unweighted and structural-site-weighted overlap; no drive."""
    if not records or len({record.eye_side for record in records}) != 1:
        raise ValueError("Exposure requires one body's single-side source records")
    if records[0].eye_side != stimulus_side:
        return {
            "any_source_column_overlap": 0.0,
            "source_column_overlap_fraction": 0.0,
            "unique_hex_occupancy_overlap_fraction": 0.0,
            "structural_input_site_overlap_fraction": 0.0,
        }
    matching = [
        record for record in records if (record.ol_hex1, record.ol_hex2) in active_hexes
    ]
    unique_hexes = {(record.ol_hex1, record.ol_hex2) for record in records}
    return {
        "any_source_column_overlap": float(bool(matching)),
        "source_column_overlap_fraction": len(matching) / len(records),
        "unique_hex_occupancy_overlap_fraction": (
            len(unique_hexes & active_hexes) / len(unique_hexes)
        ),
        "structural_input_site_overlap_fraction": (
            sum(record.input_count for record in matching)
            / sum(record.input_count for record in records)
        ),
    }


def _summary(values: list[float]) -> dict[str, float]:
    return {"min": min(values), "median": median(values), "max": max(values)}


def analyze(column_root: Path, circuit_root: Path, workbook: Path) -> dict:
    circuit = load_circuit_contract(circuit_root)
    contract = load_column_contract(column_root, circuit_contract=circuit)
    official = load_official_columns(workbook)
    grouped: dict[int, list[ColumnInputRecord]] = defaultdict(list)
    source_only: dict[str, dict[tuple[int, int], int]] = {"L": {}, "R": {}}
    for record in contract.records:
        coord = (record.ol_hex1, record.ol_hex2)
        if coord not in official[record.eye_side]:
            side_counts = source_only[record.eye_side]
            side_counts[coord] = side_counts.get(coord, 0) + record.input_count
        grouped[record.body_id].append(record)
    if len(grouped) != 311:
        raise ValueError("Expected exactly 311 body-specific source distributions")

    body_rows = []
    for source in sorted(contract.summaries, key=lambda item: item.body_id):
        records = tuple(grouped[source.body_id])
        edge = {
            coord for coord, kind in official[source.eye_side].items() if kind == "edge"
        }
        anatomy = body_anatomy(
            records,
            relevant_sites=source.relevant_input_count,
            edge_hexes=edge,
            classified_hexes=set(official[source.eye_side]),
        )
        if anatomy["assigned_sites"] != source.assigned_input_count:
            raise ValueError("Body summary and sparse source counts disagree")
        body_rows.append(
            {
                "body_id": source.body_id,
                "neuron_type": source.neuron_type,
                "side": source.eye_side,
                **anatomy,
            }
        )

    populations = {}
    for neuron_type in ("LC4", "LPLC2"):
        for side in ("L", "R"):
            rows = [
                row
                for row in body_rows
                if row["neuron_type"] == neuron_type and row["side"] == side
            ]
            hex_occupancy: dict[tuple[int, int], int] = defaultdict(int)
            for row in rows:
                hexes = {
                    (record.ol_hex1, record.ol_hex2)
                    for record in grouped[row["body_id"]]
                }
                for coord in hexes:
                    hex_occupancy[coord] += 1
            populations[f"{neuron_type}_{side}"] = {
                "bodies": len(rows),
                "source_columns": _summary(
                    [row["source_column_count"] for row in rows]
                ),
                "assigned_fraction": _summary(
                    [row["assigned_fraction"] for row in rows]
                ),
                "missing_sites_total": sum(
                    row["relevant_sites"] - row["assigned_sites"] for row in rows
                ),
                "centroid_hex1_range": [
                    min(
                        row["unweighted_anatomical_column_centroid"][0] for row in rows
                    ),
                    max(
                        row["unweighted_anatomical_column_centroid"][0] for row in rows
                    ),
                ],
                "centroid_hex2_range": [
                    min(
                        row["unweighted_anatomical_column_centroid"][1] for row in rows
                    ),
                    max(
                        row["unweighted_anatomical_column_centroid"][1] for row in rows
                    ),
                ],
                "unweighted_rms_hex_spread": _summary(
                    [row["unweighted_rms_hex_spread"] for row in rows]
                ),
                "structural_input_weighted_rms_hex_spread": _summary(
                    [row["structural_input_weighted_rms_hex_spread"] for row in rows]
                ),
                "edge_hex_fraction_of_classified": _summary(
                    [
                        row["edge_hex_fraction_of_classified"]
                        for row in rows
                        if row["edge_hex_fraction_of_classified"] is not None
                    ]
                ),
                "workbook_unclassified_hex_count_total": sum(
                    row["workbook_unclassified_hex_count"] for row in rows
                ),
                "distinct_population_hexes": len(hex_occupancy),
                "official_hex_coverage_fraction": len(
                    set(hex_occupancy) & set(official[side])
                )
                / len(official[side]),
                "bodies_per_occupied_hex": _summary(list(hex_occupancy.values())),
            }

    proof = {}
    for name, side, centre, radius in STIMULI:
        if centre not in official[side]:
            raise ValueError("Synthetic centre must be an official source column")
        lattice = set(official[side]) | set(source_only[side])
        active = {coord for coord in lattice if hex_distance(coord, centre) <= radius}
        proof[name] = {
            "side": side,
            "centre_hex": centre,
            "radius_hex_steps": radius,
            "active_source_or_workbook_columns": len(active),
            "bodies": {
                str(body_id): anatomical_exposure(
                    tuple(grouped[body_id]),
                    stimulus_side=side,
                    active_hexes=active,
                )
                for body_id in PROOF_BODIES
            },
        }

    manifest = json.loads((column_root / "column_manifest.json").read_text())
    return {
        "schema": SCHEMA,
        "semantics": "anatomical_relative_column_space_only_no_neural_dynamics",
        "dataset": contract.dataset,
        "candidate": contract.candidate_identifier,
        "source_schema": contract.schema_version,
        "source_file_sha256": manifest["sha256"],
        "official_workbook_sha256": WORKBOOK_SHA256,
        "source_hexes_absent_from_workbook": {
            side: [
                {"hex": coord, "input_sites": count}
                for coord, count in sorted(source_only[side].items())
            ]
            for side in ("L", "R")
        },
        "lattice": "hex1=q;hex2=p;six_neighbors=(+/-1,0),(0,+/-1),(+/-1,+/-1)",
        "bodies": body_rows,
        "populations": populations,
        "synthetic_proof": proof,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--columns", type=Path, default=DEFAULT_ROOT / "body_columns_v1"
    )
    parser.add_argument("--circuit", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.columns, args.circuit, args.workbook)
    encoded = (
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest()
    print(f"schema={SCHEMA} bodies={len(result['bodies'])} sha256={digest}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
