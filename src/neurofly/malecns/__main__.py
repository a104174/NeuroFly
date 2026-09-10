"""Minimal online acquisition and offline inspection commands."""

import argparse
from pathlib import Path

from neurofly.malecns.acquire import acquire_candidate
from neurofly.malecns.client import create_client
from neurofly.malecns.contract import CircuitContract, load_circuit_contract
from neurofly.malecns.errors import MaleCNSError
from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET, NEUPRINT_ENDPOINT
from neurofly.malecns.snapshot import export_snapshot
from neurofly.malecns.validation import validate_snapshot

DEFAULT_OUTPUT = Path("data/derived/malecns/looming_giant_fiber_v1")


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


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "inspect-snapshot":
            _print_contract(load_circuit_contract(args.path))
            return 0

        client = create_client()
        if args.command == "check-access":
            print(
                f"Authenticated access confirmed: {NEUPRINT_ENDPOINT} {MALECNS_DATASET}"
            )
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
