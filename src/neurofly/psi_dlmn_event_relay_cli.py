"""Generate, inspect, or replay the offline Phase 8G PSI/DLMn event relay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.psi_dlmn_event_relay import DEFAULT_MOTOR_CONTRACT_PATH
from neurofly.psi_dlmn_event_relay_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    PsiDlmnEventRelayArtifactError,
    generate_psi_dlmn_event_relay_artifact,
    load_psi_dlmn_event_relay_artifact,
    replay_psi_dlmn_event_relay_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    generate.add_argument("--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("artifact", type=Path)
    replay = commands.add_parser("replay")
    replay.add_argument("artifact", type=Path)
    replay.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_psi_dlmn_event_relay_artifact(
                motor_contract_path=args.motor_contract,
                output_root=args.output_root,
            )
            operation = "generated-or-existing-replay-verified"
        elif args.command == "replay":
            artifact = replay_psi_dlmn_event_relay_artifact(
                args.artifact,
                motor_contract_path=args.motor_contract,
            )
            operation = "full-contract-and-result-replay-verified"
        else:
            artifact = load_psi_dlmn_event_relay_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        summary = artifact.summary()
        summary["operation"] = operation
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, PsiDlmnEventRelayArtifactError) as exc:
        print(f"Phase 8G error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
