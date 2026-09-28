"""Generate, inspect, and replay the offline Phase 8C sensory-to-motor adapter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.sensory_dnp01_motor_adapter_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    SensoryDnp01MotorArtifactError,
    generate_sensory_dnp01_motor_artifact,
    load_sensory_dnp01_motor_artifact,
    replay_sensory_dnp01_motor_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate")
    generate.add_argument("source_artifact", type=Path)
    generate.add_argument("condition_id")
    generate.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    generate.add_argument("--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)

    inspect = commands.add_parser("inspect")
    inspect.add_argument("artifact", type=Path)

    replay = commands.add_parser("replay")
    replay.add_argument("artifact", type=Path)
    replay.add_argument("source_artifact", type=Path)
    replay.add_argument("condition_id")
    replay.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_sensory_dnp01_motor_artifact(
                args.source_artifact,
                args.condition_id,
                source_root=args.source_root,
                output_root=args.output_root,
            )
            operation = "generated-or-existing"
        elif args.command == "replay":
            artifact = replay_sensory_dnp01_motor_artifact(
                args.artifact,
                args.source_artifact,
                args.condition_id,
                source_root=args.source_root,
            )
            operation = "full-source-and-result-replay-verified"
        else:
            artifact = load_sensory_dnp01_motor_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        output = artifact.summary()
        output["operation"] = operation
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, SensoryDnp01MotorArtifactError) as exc:
        print(f"Phase 8C adapter error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI smoke tests
    raise SystemExit(main())
