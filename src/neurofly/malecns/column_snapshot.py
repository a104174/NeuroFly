"""Deterministic offline storage for the Phase 1E column-space contract."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path
from typing import Any

from neurofly.malecns.columns import (
    COLUMN_INPUT_FILENAME,
    COLUMN_MANIFEST_FILENAME,
    COLUMN_SCHEMA_VERSION,
    COLUMN_SUMMARY_FILENAME,
    VISUAL_TYPES,
    BodyColumnInputContract,
    BodyColumnSummary,
    ColumnInputRecord,
    validate_column_contract,
)
from neurofly.malecns.errors import SnapshotExportError, SnapshotIntegrityError
from neurofly.malecns.models import MALECNS_DATASET

OFFICIAL_COLUMN_RESOURCE = {
    "file": "optic-column-type-assignments-v1.0.xlsx",
    "source": "https://github.com/flyconnectome/2025malecns",
    "commit": "67767d2233657983993ff6c2be48e836a935863c",
    "sha256": "d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3",
    "identifier_format": "ME_<L|R>_col_<hex1>_<hex2>",
}


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value}")


def _json_line(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> str:
    digest = sha256()
    with path.open("wb") as stream:
        for record in records:
            encoded = _json_line(record)
            stream.write(encoded)
            digest.update(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_json_constant
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise SnapshotIntegrityError(f"Malformed {label}: {error}") from None
    if not isinstance(value, dict):
        raise SnapshotIntegrityError(f"{label} must be a JSON object.")
    return value


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    raise SnapshotIntegrityError(
                        f"Malformed {label} at line {line_number}: blank line."
                    )
                try:
                    value = json.loads(line, parse_constant=_reject_json_constant)
                except (json.JSONDecodeError, ValueError) as error:
                    raise SnapshotIntegrityError(
                        f"Malformed {label} at line {line_number}: {error}"
                    ) from None
                if not isinstance(value, dict):
                    raise SnapshotIntegrityError(
                        f"Malformed {label} at line {line_number}: object required."
                    )
                records.append(value)
    except (OSError, UnicodeError) as error:
        raise SnapshotIntegrityError(f"Could not read {label}: {error}") from None
    return records


def _sha256(path: Path) -> str:
    digest = sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise SnapshotIntegrityError(f"Could not read {path.name}: {error}") from None
    return digest.hexdigest()


def _require_fields(record: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - record.keys())
    extra = sorted(record.keys() - expected)
    if missing or extra:
        raise SnapshotIntegrityError(
            f"Invalid {label} fields: missing={missing!r}, unexpected={extra!r}."
        )


def _required_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SnapshotIntegrityError(f"{field_name} must be an integer.")
    return value


def _required_nonnegative_int(value: Any, field_name: str) -> int:
    result = _required_int(value, field_name)
    if result < 0:
        raise SnapshotIntegrityError(f"{field_name} must be non-negative.")
    return result


def _required_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise SnapshotIntegrityError(f"{field_name} must be a string.")
    return value


def _parse_input_record(record: dict[str, Any], line_number: int) -> ColumnInputRecord:
    label = f"column input record {line_number}"
    _require_fields(
        record,
        {
            "body_id",
            "column_id",
            "eye_side",
            "input_count",
            "neuron_type",
            "neuropil",
            "ol_hex1",
            "ol_hex2",
        },
        label,
    )
    result = ColumnInputRecord(
        body_id=_required_int(record["body_id"], f"{label} body_id"),
        neuron_type=_required_str(record["neuron_type"], f"{label} neuron_type"),
        eye_side=_required_str(record["eye_side"], f"{label} eye_side"),
        neuropil=_required_str(record["neuropil"], f"{label} neuropil"),
        ol_hex1=_required_int(record["ol_hex1"], f"{label} ol_hex1"),
        ol_hex2=_required_int(record["ol_hex2"], f"{label} ol_hex2"),
        input_count=_required_int(record["input_count"], f"{label} input_count"),
    )
    if record["column_id"] != result.column_id:
        raise SnapshotIntegrityError(f"{label} has a non-canonical column_id.")
    return result


def _parse_summary(record: dict[str, Any], line_number: int) -> BodyColumnSummary:
    label = f"body summary {line_number}"
    _require_fields(
        record,
        {
            "assigned_input_count",
            "assignment_fraction",
            "body_id",
            "distinct_occupied_column_count",
            "eye_side",
            "malformed_hex_count",
            "multiple_column_count",
            "neuron_type",
            "neuropil_assigned_counts",
            "neuropil_input_counts",
            "relevant_input_count",
            "unassigned_input_count",
            "unknown_column_count",
        },
        label,
    )
    input_counts = record["neuropil_input_counts"]
    assigned_counts = record["neuropil_assigned_counts"]
    if not isinstance(input_counts, dict) or not isinstance(assigned_counts, dict):
        raise SnapshotIntegrityError(f"{label} neuropil counts must be objects.")
    if not all(isinstance(key, str) for key in input_counts):
        raise SnapshotIntegrityError(f"{label} has an invalid neuropil key.")
    if not all(isinstance(key, str) for key in assigned_counts):
        raise SnapshotIntegrityError(f"{label} has an invalid assigned neuropil key.")
    parsed_input_counts = tuple(
        sorted(
            (
                key,
                _required_nonnegative_int(value, f"{label} input count {key}"),
            )
            for key, value in input_counts.items()
        )
    )
    parsed_assigned_counts = tuple(
        sorted(
            (
                key,
                _required_nonnegative_int(value, f"{label} assigned count {key}"),
            )
            for key, value in assigned_counts.items()
        )
    )
    fraction = record["assignment_fraction"]
    if isinstance(fraction, bool) or not isinstance(fraction, (int, float)):
        raise SnapshotIntegrityError(f"{label} assignment_fraction must be numeric.")
    return BodyColumnSummary(
        body_id=_required_int(record["body_id"], f"{label} body_id"),
        neuron_type=_required_str(record["neuron_type"], f"{label} neuron_type"),
        eye_side=_required_str(record["eye_side"], f"{label} eye_side"),
        relevant_input_count=_required_int(
            record["relevant_input_count"], f"{label} relevant_input_count"
        ),
        assigned_input_count=_required_int(
            record["assigned_input_count"], f"{label} assigned_input_count"
        ),
        unassigned_input_count=_required_int(
            record["unassigned_input_count"], f"{label} unassigned_input_count"
        ),
        assignment_fraction=float(fraction),
        distinct_occupied_column_count=_required_int(
            record["distinct_occupied_column_count"],
            f"{label} distinct_occupied_column_count",
        ),
        malformed_hex_count=_required_int(
            record["malformed_hex_count"], f"{label} malformed_hex_count"
        ),
        multiple_column_count=_required_int(
            record["multiple_column_count"], f"{label} multiple_column_count"
        ),
        unknown_column_count=_required_int(
            record["unknown_column_count"], f"{label} unknown_column_count"
        ),
        neuropil_input_counts=parsed_input_counts,
        neuropil_assigned_counts=parsed_assigned_counts,
    )


def _manifest_for(
    contract: BodyColumnInputContract,
    checksums: dict[str, str],
    file_sizes: dict[str, int],
) -> dict[str, Any]:
    summary = contract.descriptive_summary()
    return {
        "acquired_at_utc": contract.acquired_at_utc,
        "aggregation_method": contract.aggregation_method,
        "body_count": len(contract.summaries),
        "candidate": {
            "identifier": contract.candidate_identifier,
            "version": contract.candidate_version,
            "selected_neuron_types": list(VISUAL_TYPES),
        },
        "column_schema_version": COLUMN_SCHEMA_VERSION,
        "dataset": contract.dataset,
        "endpoint": contract.endpoint,
        "file_sizes_bytes": file_sizes,
        "provenance": dict(contract.provenance),
        "query_counts": dict(contract.query_counts),
        "sha256": checksums,
        "source": "Janelia neuPrint / MaleCNS",
        "source_snapshot": contract.source_snapshot,
        "sparse_record_count": len(contract.records),
        "summary": summary,
        "territory_rule": contract.visual_territory_rule,
        "official_column_resource": OFFICIAL_COLUMN_RESOURCE,
        "files": [COLUMN_INPUT_FILENAME, COLUMN_SUMMARY_FILENAME],
    }


def export_column_contract(
    contract: BodyColumnInputContract,
    output: Path,
    *,
    circuit_contract: Any | None = None,
    expected_population: bool | None = None,
) -> Path:
    """Atomically export deterministic column records, summaries, and manifest."""
    if expected_population is None:
        expected_population = len(contract.summaries) == 311
    validate_column_contract(
        contract, circuit_contract, expected_population=expected_population
    )
    output = Path(output)
    if output.exists():
        raise SnapshotExportError(
            f"Column-contract output already exists: {output}. Remove it explicitly "
            "before regenerating."
        )
    staging: Path | None = None
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
        records = [
            record.to_dict()
            for record in sorted(
                contract.records,
                key=lambda item: (
                    item.body_id,
                    item.neuron_type,
                    item.eye_side,
                    item.neuropil,
                    item.ol_hex1,
                    item.ol_hex2,
                ),
            )
        ]
        summaries = [
            summary.to_dict()
            for summary in sorted(contract.summaries, key=lambda item: item.body_id)
        ]
        checksums = {
            COLUMN_INPUT_FILENAME: _write_jsonl(
                staging / COLUMN_INPUT_FILENAME, records
            ),
            COLUMN_SUMMARY_FILENAME: _write_jsonl(
                staging / COLUMN_SUMMARY_FILENAME, summaries
            ),
        }
        file_sizes = {
            filename: (staging / filename).stat().st_size for filename in checksums
        }
        manifest = _manifest_for(contract, checksums, file_sizes)
        (staging / COLUMN_MANIFEST_FILENAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(staging, output)
    except Exception as error:
        raise SnapshotExportError(
            f"Could not export column contract to {output}: {error}"
        ) from None
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
    return output


def load_column_contract(
    path: Path,
    *,
    circuit_contract: Any | None = None,
) -> BodyColumnInputContract:
    """Load and verify a column contract without network access."""
    path = Path(path)
    required = {
        COLUMN_INPUT_FILENAME,
        COLUMN_SUMMARY_FILENAME,
        COLUMN_MANIFEST_FILENAME,
    }
    if not path.is_dir() or set(item.name for item in path.iterdir()) < required:
        raise SnapshotIntegrityError("Column contract is missing required files.")
    manifest = _read_json(path / COLUMN_MANIFEST_FILENAME, COLUMN_MANIFEST_FILENAME)
    if manifest.get("column_schema_version") != COLUMN_SCHEMA_VERSION:
        raise SnapshotIntegrityError("Unsupported column schema version.")
    if manifest.get("dataset") != MALECNS_DATASET:
        raise SnapshotIntegrityError("Wrong column-contract dataset.")
    if manifest.get("files") != [COLUMN_INPUT_FILENAME, COLUMN_SUMMARY_FILENAME]:
        raise SnapshotIntegrityError("Column manifest files are unsupported.")
    checksums = manifest.get("sha256")
    if not isinstance(checksums, dict):
        raise SnapshotIntegrityError("Column manifest sha256 must be an object.")
    if set(checksums) != {COLUMN_INPUT_FILENAME, COLUMN_SUMMARY_FILENAME}:
        raise SnapshotIntegrityError("Column manifest sha256 has invalid files.")
    for filename in (COLUMN_INPUT_FILENAME, COLUMN_SUMMARY_FILENAME):
        expected = checksums.get(filename)
        if not isinstance(expected, str) or _sha256(path / filename) != expected:
            raise SnapshotIntegrityError(f"SHA-256 mismatch for {filename}.")
    file_sizes = manifest.get("file_sizes_bytes")
    if not isinstance(file_sizes, dict):
        raise SnapshotIntegrityError("Column manifest file sizes must be an object.")
    for filename in (COLUMN_INPUT_FILENAME, COLUMN_SUMMARY_FILENAME):
        expected_size = _required_nonnegative_int(
            file_sizes.get(filename), f"file_sizes_bytes.{filename}"
        )
        if (path / filename).stat().st_size != expected_size:
            raise SnapshotIntegrityError(f"File-size mismatch for {filename}.")

    input_records = [
        _parse_input_record(record, line_number)
        for line_number, record in enumerate(
            _read_jsonl(path / COLUMN_INPUT_FILENAME, COLUMN_INPUT_FILENAME),
            start=1,
        )
    ]
    summaries = [
        _parse_summary(record, line_number)
        for line_number, record in enumerate(
            _read_jsonl(path / COLUMN_SUMMARY_FILENAME, COLUMN_SUMMARY_FILENAME),
            start=1,
        )
    ]
    candidate = manifest.get("candidate")
    if not isinstance(candidate, dict):
        raise SnapshotIntegrityError("Column manifest candidate must be an object.")
    if candidate.get("selected_neuron_types") != list(VISUAL_TYPES):
        raise SnapshotIntegrityError(
            "Column manifest selected neuron types are unsupported."
        )
    query_counts = manifest.get("query_counts", {})
    provenance = manifest.get("provenance", {})
    if not isinstance(query_counts, dict) or not isinstance(provenance, dict):
        raise SnapshotIntegrityError("Column manifest metadata has an invalid schema.")
    contract = BodyColumnInputContract(
        schema_version=COLUMN_SCHEMA_VERSION,
        candidate_identifier=_required_str(
            candidate.get("identifier"), "candidate.identifier"
        ),
        candidate_version=_required_int(candidate.get("version"), "candidate.version"),
        dataset=_required_str(manifest.get("dataset"), "manifest.dataset"),
        endpoint=_required_str(manifest.get("endpoint"), "manifest.endpoint"),
        acquired_at_utc=_required_str(
            manifest.get("acquired_at_utc"), "manifest.acquired_at_utc"
        ),
        source_snapshot=_required_str(
            manifest.get("source_snapshot"), "manifest.source_snapshot"
        ),
        visual_territory_rule=_required_str(
            manifest.get("territory_rule"), "manifest.territory_rule"
        ),
        aggregation_method=_required_str(
            manifest.get("aggregation_method"), "manifest.aggregation_method"
        ),
        records=tuple(input_records),
        summaries=tuple(summaries),
        query_counts=tuple(
            sorted(
                (str(key), _required_int(value, f"query_counts.{key}"))
                for key, value in query_counts.items()
            )
        ),
        provenance=tuple(
            sorted(
                (str(key), _required_str(value, f"provenance.{key}"))
                for key, value in provenance.items()
            )
        ),
    )
    body_count = _required_nonnegative_int(manifest.get("body_count"), "body_count")
    sparse_record_count = _required_nonnegative_int(
        manifest.get("sparse_record_count"), "sparse_record_count"
    )
    if body_count != len(contract.summaries):
        raise SnapshotIntegrityError("Column manifest body count mismatch.")
    if sparse_record_count != len(contract.records):
        raise SnapshotIntegrityError("Column manifest sparse record count mismatch.")
    manifest_summary = manifest.get("summary")
    if not isinstance(manifest_summary, dict):
        raise SnapshotIntegrityError("Column manifest summary must be an object.")
    if manifest_summary.get("body_count") != body_count:
        raise SnapshotIntegrityError("Column manifest summary body count mismatch.")
    if manifest_summary.get("sparse_record_count") != sparse_record_count:
        raise SnapshotIntegrityError(
            "Column manifest summary sparse record count mismatch."
        )
    expected_population = body_count == 311
    validate_column_contract(
        contract, circuit_contract, expected_population=expected_population
    )
    return contract
