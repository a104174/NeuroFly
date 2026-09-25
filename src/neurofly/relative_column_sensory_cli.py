"""Generate, inspect, replay, and summarize the offline Phase 7E state artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT, DEFAULT_WORKBOOK
from neurofly.relative_column_sensory_artifacts import (
    DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    DEFAULT_OUTPUT_ROOT,
    RelativeColumnSensoryArtifactError,
    export_relative_column_sensory_artifact,
    load_relative_column_sensory_artifact,
    make_relative_column_sensory_artifact,
    relative_column_sensory_artifact_id,
    replay_relative_column_sensory_artifact,
)
from neurofly.relative_column_sensory_dynamics import sensitivity_summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate", help="create the fixed four-body Phase 7E artifact"
    )
    generate.add_argument(
        "--assignment-artifact", type=Path, default=DEFAULT_ASSIGNMENT_ARTIFACT_PATH
    )
    generate.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    generate.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    generate.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)

    replay = subparsers.add_parser(
        "replay", help="replay Phase 7D and verify the Phase 7E artifact"
    )
    replay.add_argument("artifact", type=Path)
    replay.add_argument(
        "--assignment-artifact", type=Path, default=DEFAULT_ASSIGNMENT_ARTIFACT_PATH
    )
    replay.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    replay.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)

    for name, help_text in (
        ("inspect", "check integrity and summarize the artifact without replay"),
        ("sensitivity", "print the stored assumption-grid sensitivity summary"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            config, result = make_relative_column_sensory_artifact(
                assignment_artifact_path=args.assignment_artifact,
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            artifact_id = relative_column_sensory_artifact_id(config, result)
            destination = args.output_root / artifact_id
            if destination.exists():
                artifact = replay_relative_column_sensory_artifact(
                    destination,
                    assignment_artifact_path=args.assignment_artifact,
                    source_root=args.source_root,
                    workbook_path=args.workbook,
                )
                operation = "existing-immutable-artifact-replayed"
            else:
                artifact = export_relative_column_sensory_artifact(
                    config, result, destination
                )
                operation = "created"
            output = artifact.inspection_dict()
        elif args.command == "replay":
            artifact = replay_relative_column_sensory_artifact(
                args.artifact,
                assignment_artifact_path=args.assignment_artifact,
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            output = artifact.inspection_dict()
            operation = "replay-verified"
        else:
            artifact = load_relative_column_sensory_artifact(args.artifact)
            if args.command == "sensitivity":
                output = sensitivity_summary(artifact.result)
            else:
                output = artifact.inspection_dict()
            operation = "integrity-verified-no-replay"
        output["operation"] = operation
        output["artifact_path"] = str(artifact.path)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (RelativeColumnSensoryArtifactError, OSError, ValueError) as exc:
        print(f"relative-column sensory state failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - smoke-tested as a module
    raise SystemExit(main())
