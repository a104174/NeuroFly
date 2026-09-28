"""Generate, inspect, or replay the offline Phase 8L target-dispatch artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.synthetic_motor_target_dispatch import (
    DEFAULT_TARGET_CONTRACT_PATH,
    SyntheticMotorTargetDispatchError,
)
from neurofly.synthetic_motor_target_dispatch_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    SyntheticMotorTargetArtifactError,
    generate_synthetic_motor_target_artifact,
    load_synthetic_motor_target_artifact,
    replay_synthetic_motor_target_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument(
        "--target-contract", type=Path, default=DEFAULT_TARGET_CONTRACT_PATH
    )
    generate.add_argument("--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    for name in ("inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)
        if name == "replay":
            command.add_argument(
                "--target-contract", type=Path, default=DEFAULT_TARGET_CONTRACT_PATH
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_synthetic_motor_target_artifact(
                target_contract_path=args.target_contract,
                output_root=args.output_root,
            )
            operation = "generated-or-existing-full-replay-verified"
        elif args.command == "replay":
            artifact = replay_synthetic_motor_target_artifact(
                args.artifact,
                target_contract_path=args.target_contract,
            )
            operation = "offline-source-replay-verified"
        else:
            artifact = load_synthetic_motor_target_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        summary = artifact.summary()
        summary["operation"] = operation
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (
        OSError,
        ValueError,
        SyntheticMotorTargetDispatchError,
        SyntheticMotorTargetArtifactError,
    ) as exc:
        print(f"Phase 8L target-dispatch error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
