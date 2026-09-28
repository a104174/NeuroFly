"""Generate, inspect, or replay a condition-explicit Phase 8H event adapter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.psi_dlmn_event_relay import DEFAULT_MOTOR_CONTRACT_PATH
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.sensory_psi_dlmn_event_adapter_artifacts import (
    DEFAULT_OUTPUT_ROOT,
    SensoryPsiDlmnEventArtifactError,
    generate_sensory_psi_dlmn_event_artifact,
    load_sensory_psi_dlmn_event_artifact,
    replay_sensory_psi_dlmn_event_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument("phase7o_artifact", type=Path)
    generate.add_argument("condition_id")
    generate.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    generate.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    generate.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    inspect = commands.add_parser("inspect")
    inspect.add_argument("artifact", type=Path)
    replay = commands.add_parser("replay")
    replay.add_argument("artifact", type=Path)
    replay.add_argument("phase7o_artifact", type=Path)
    replay.add_argument("condition_id")
    replay.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    replay.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_sensory_psi_dlmn_event_artifact(
                args.phase7o_artifact,
                args.condition_id,
                output_root=args.output_root,
                source_root=args.source_root,
                motor_contract_path=args.motor_contract,
            )
            operation = "generated-or-existing-replay-verified"
        elif args.command == "replay":
            artifact = replay_sensory_psi_dlmn_event_artifact(
                args.artifact,
                args.phase7o_artifact,
                args.condition_id,
                source_root=args.source_root,
                motor_contract_path=args.motor_contract,
            )
            operation = "full-source-contract-and-relay-replay-verified"
        else:
            artifact = load_sensory_psi_dlmn_event_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        summary = artifact.summary()
        summary["operation"] = operation
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, SensoryPsiDlmnEventArtifactError) as exc:
        print(f"Phase 8H error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
