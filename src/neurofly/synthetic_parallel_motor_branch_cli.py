"""Generate, inspect, or replay the offline Phase 8I branch composition."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.psi_dlmn_event_relay import DEFAULT_MOTOR_CONTRACT_PATH
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_parallel_motor_branch_artifacts import (
    DEFAULT_OUTPUT_ROOT,
    SyntheticParallelMotorArtifactError,
    generate_synthetic_parallel_motor_artifact,
    load_synthetic_parallel_motor_artifact,
    replay_synthetic_parallel_motor_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    generate.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    generate.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("artifact", type=Path)
    replay = commands.add_parser("replay")
    replay.add_argument("artifact", type=Path)
    replay.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    replay.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_synthetic_parallel_motor_artifact(
                source_root=args.source_root,
                motor_contract_path=args.motor_contract,
                output_root=args.output_root,
            )
            operation = "generated-or-existing-full-replay-verified"
        elif args.command == "replay":
            artifact = replay_synthetic_parallel_motor_artifact(
                args.artifact,
                source_root=args.source_root,
                motor_contract_path=args.motor_contract,
            )
            operation = "full-child-source-and-composition-replay-verified"
        else:
            artifact = load_synthetic_parallel_motor_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        output = artifact.summary()
        output["operation"] = operation
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, SyntheticParallelMotorArtifactError) as exc:
        print(f"Phase 8I error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
