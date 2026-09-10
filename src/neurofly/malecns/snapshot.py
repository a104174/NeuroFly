"""Deterministic, atomic export of validated derived MaleCNS data."""

import json
import os
import shutil
import tempfile
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from typing import Any

from neurofly.malecns.errors import SnapshotExportError
from neurofly.malecns.models import NEUPRINT_ENDPOINT, CandidateSnapshot
from neurofly.malecns.validation import ValidationReport, validate_snapshot


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


def build_manifest(
    snapshot: CandidateSnapshot,
    report: ValidationReport,
    checksums: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build credential-free provenance for a validated acquisition."""
    candidate = snapshot.candidate
    manifest: dict[str, Any] = {
        "candidate": {
            "identifier": candidate.identifier,
            "version": candidate.version,
            "selected_neuron_types": list(candidate.neuron_types),
        },
        "source": "Janelia neuPrint / MaleCNS",
        "endpoint": NEUPRINT_ENDPOINT,
        "dataset": candidate.dataset,
        "acquired_at_utc": snapshot.acquired_at_utc,
        "neuprint_python_version": version("neuprint-python"),
        "neuron_count": report.total_neuron_count,
        "neuron_counts_by_type": report.neuron_counts,
        "induced_connection_count": report.induced_connection_count,
        "primary_connectivity": {
            "LC4_to_DNp01": report.lc4_to_dnp01.to_dict(),
            "LPLC2_to_DNp01": report.lplc2_to_dnp01.to_dict(),
        },
        "structural_weight_source": "neuPrint ConnectsTo.weight",
        "structural_weight_is_physiological_coupling": False,
    }
    if checksums is not None:
        manifest["sha256"] = checksums
    return manifest


def export_snapshot(snapshot: CandidateSnapshot, output: Path) -> Path:
    """Validate, then atomically create a new snapshot directory.

    Existing output is never replaced. Remove it explicitly before regeneration.
    """
    report = validate_snapshot(snapshot)
    output = Path(output)
    if output.exists():
        raise SnapshotExportError(
            f"Snapshot output already exists: {output}. Remove it explicitly before "
            "regenerating."
        )

    staging: Path | None = None
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
        neuron_records = [
            neuron.to_dict()
            for neuron in sorted(snapshot.neurons, key=lambda item: item.body_id)
        ]
        connection_records = [
            edge.to_dict()
            for edge in sorted(
                snapshot.connections,
                key=lambda item: (
                    item.source_body_id,
                    item.target_body_id,
                    item.source_type,
                    item.target_type,
                ),
            )
        ]
        checksums = {
            "neurons.jsonl": _write_jsonl(staging / "neurons.jsonl", neuron_records),
            "connections.jsonl": _write_jsonl(
                staging / "connections.jsonl", connection_records
            ),
        }
        manifest = build_manifest(snapshot, report, checksums)
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(staging, output)
    except Exception as error:
        raise SnapshotExportError(
            f"Could not export snapshot to {output}: {error}"
        ) from None
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
    return output
