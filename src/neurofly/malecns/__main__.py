"""Minimal online acquisition and offline inspection commands."""

import argparse
import json
from pathlib import Path

from neurofly.malecns.acquire import acquire_candidate
from neurofly.malecns.client import create_client
from neurofly.malecns.column_snapshot import (
    export_column_contract,
    load_column_contract,
)
from neurofly.malecns.columns import acquire_body_columns
from neurofly.malecns.contract import CircuitContract, load_circuit_contract
from neurofly.malecns.errors import MaleCNSError
from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET, NEUPRINT_ENDPOINT
from neurofly.malecns.morphology_artifacts import (
    generate_dnp01_morphology_artifact_from_official_bulk_swc,
    load_morphology_artifact,
)
from neurofly.malecns.snapshot import export_snapshot
from neurofly.malecns.validation import validate_snapshot

DEFAULT_OUTPUT = Path("data/derived/malecns/looming_giant_fiber_v1")
DEFAULT_COLUMN_OUTPUT = DEFAULT_OUTPUT / "body_columns_v1"
DEFAULT_MORPHOLOGY_ROOT = DEFAULT_OUTPUT / "morphology_artifacts_v1"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NeuroFly MaleCNS data tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check-access", help="check authenticated dataset access")
    snapshot = subparsers.add_parser(
        "snapshot", help="acquire, validate, and export the candidate"
    )
    snapshot.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    inspect_snapshot = subparsers.add_parser(
        "inspect-snapshot", help="validate and describe an existing snapshot offline"
    )
    inspect_snapshot.add_argument("path", type=Path, nargs="?", default=DEFAULT_OUTPUT)
    column_snapshot = subparsers.add_parser(
        "column-snapshot",
        help="acquire and export body-specific MaleCNS column-space inputs",
    )
    column_snapshot.add_argument("--contract", type=Path, default=DEFAULT_OUTPUT)
    column_snapshot.add_argument("--output", type=Path, default=DEFAULT_COLUMN_OUTPUT)
    inspect_columns = subparsers.add_parser(
        "inspect-column-snapshot",
        help="validate and describe an existing column-space snapshot offline",
    )
    inspect_columns.add_argument(
        "path", type=Path, nargs="?", default=DEFAULT_COLUMN_OUTPUT
    )
    inspect_columns.add_argument("--contract", type=Path, default=DEFAULT_OUTPUT)
    morphology = subparsers.add_parser(
        "morphology-artifact",
        help="acquire the fixed raw DNp01 artifact from official bulk SWC",
    )
    morphology.add_argument("--contract", type=Path, default=DEFAULT_OUTPUT)
    morphology.add_argument("--output-root", type=Path, default=DEFAULT_MORPHOLOGY_ROOT)
    inspect_morphology = subparsers.add_parser(
        "inspect-morphology-artifact",
        help="validate and describe one raw DNp01 morphology artifact offline",
    )
    inspect_morphology.add_argument("path", type=Path)
    inspect_morphology.add_argument("--contract", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _print_contract(contract: CircuitContract) -> None:
    summary = contract.structural_summary()
    print(
        f"candidate={contract.candidate.identifier} "
        f"version={contract.candidate.version} dataset={contract.provenance.dataset}"
    )
    print("integrity=SHA-256 verified; record counts verified")
    neuron_counts = ", ".join(
        f"{neuron_type}={count}" for neuron_type, count in summary.neuron_counts_by_type
    )
    print(f"neurons={summary.total_neuron_count} ({neuron_counts})")
    print(
        f"chemical_edges={summary.total_chemical_edge_count} "
        f"total_structural_weight={summary.total_structural_weight}"
    )
    for pair in summary.type_pairs:
        print(
            f"{pair.source_type} -> {pair.target_type}: "
            f"chemical_edges={pair.chemical_edge_count}, "
            f"structural_weight_sum={pair.structural_weight_sum}"
        )


def _print_column_contract(contract: object) -> None:
    summary = contract.descriptive_summary()
    print(
        f"schema={contract.schema_version} candidate={contract.candidate_identifier} "
        f"dataset={contract.dataset}"
    )
    print(
        f"bodies={summary['body_count']} "
        f"sparse_records={summary['sparse_record_count']} "
        f"relevant_inputs={summary['relevant_input_count']} "
        f"assigned_inputs={summary['assigned_input_count']} "
        f"unassigned_inputs={summary['unassigned_input_count']}"
    )
    for neuron_type, values in summary["by_type"].items():
        print(
            f"{neuron_type}: bodies={values['body_count']} "
            f"relevant={values['relevant_input_count']} "
            f"assigned={values['assigned_input_count']} "
            f"unassigned={values['unassigned_input_count']} "
            f"assignment_fraction={values['assignment_fraction']:.12f}"
        )


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "inspect-snapshot":
            _print_contract(load_circuit_contract(args.path))
            return 0

        if args.command == "inspect-column-snapshot":
            circuit = load_circuit_contract(args.contract)
            column_contract = load_column_contract(args.path, circuit_contract=circuit)
            _print_column_contract(column_contract)
            print("integrity=SHA-256 verified; body/count accounting verified")
            return 0

        if args.command == "inspect-morphology-artifact":
            circuit = load_circuit_contract(args.contract)
            artifact = load_morphology_artifact(args.path, circuit=circuit)
            print(json.dumps(artifact.inspection_dict(), sort_keys=True, indent=2))
            return 0

        if args.command == "check-access":
            client = create_client()
            print(
                f"Authenticated access confirmed: {NEUPRINT_ENDPOINT} {MALECNS_DATASET}"
            )
            return 0

        if args.command == "morphology-artifact":
            circuit = load_circuit_contract(args.contract)
            output = generate_dnp01_morphology_artifact_from_official_bulk_swc(
                circuit, args.output_root
            )
            print(f"morphology_artifact={output.name} path={output}")
            return 0

        client = create_client()

        if args.command == "column-snapshot":
            circuit = load_circuit_contract(args.contract)
            column_contract = acquire_body_columns(client, circuit)
            output = export_column_contract(
                column_contract, args.output, circuit_contract=circuit
            )
            _print_column_contract(column_contract)
            print(f"wrote={output}")
            return 0

        candidate = acquire_candidate(client)
        report = validate_snapshot(candidate)
        output = export_snapshot(candidate, args.output)
        print(
            f"Validated {report.total_neuron_count} neurons and "
            f"{report.induced_connection_count} induced chemical connections for "
            f"{CANDIDATE.identifier}; wrote {output}"
        )
        return 0
    except MaleCNSError as error:
        print(f"error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
