"""Generate, inspect, and replay the offline Phase 8B motor interface test."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_interface_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    SyntheticMotorArtifactError,
    generate_synthetic_motor_artifact,
    load_synthetic_motor_artifact,
    replay_synthetic_motor_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    generate.add_argument("--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    for name in ("inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)
        if name == "replay":
            command.add_argument(
                "--source-root", type=Path, default=DEFAULT_SOURCE_ROOT
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_synthetic_motor_artifact(
                source_root=args.source_root,
                output_root=args.output_root,
            )
            operation = "generated-or-existing-full-replay-verified"
        elif args.command == "replay":
            artifact = replay_synthetic_motor_artifact(
                args.artifact,
                source_root=args.source_root,
            )
            operation = "full-source-and-result-replay-verified"
        else:
            artifact = load_synthetic_motor_artifact(args.artifact)
            operation = "integrity-and-model-replay-verified"
        output = artifact.summary()
        output["operation"] = operation
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, SyntheticMotorArtifactError) as exc:
        print(f"Phase 8B error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI smoke tests
    raise SystemExit(main())
