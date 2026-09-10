"""Minimal execution surface for Phase 1A."""

import argparse
from pathlib import Path

from neurofly.malecns.acquire import acquire_candidate
from neurofly.malecns.client import create_client
from neurofly.malecns.errors import MaleCNSError
from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET, NEUPRINT_ENDPOINT
from neurofly.malecns.snapshot import export_snapshot
from neurofly.malecns.validation import validate_snapshot

DEFAULT_OUTPUT = Path("data/derived/malecns/looming_giant_fiber_v1")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NeuroFly MaleCNS Phase 1A")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check-access", help="check authenticated dataset access")
    snapshot = subparsers.add_parser(
        "snapshot", help="acquire, validate, and export the candidate"
    )
    snapshot.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
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
