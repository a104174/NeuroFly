"""Generate, inspect, and replay the bounded Phase 7D assignment artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.relative_column_assignment import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    RelativeColumnAssignmentError,
)
from neurofly.relative_column_assignment_artifacts import (
    RelativeColumnArtifactError,
    export_relative_column_artifact,
    load_relative_column_artifact,
    make_fixed_assignment,
    relative_column_artifact_id,
    replay_relative_column_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate", help="create the fixed four-body offline assignment artifact"
    )
    generate.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    generate.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    generate.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)

    replay = subparsers.add_parser(
        "replay", help="recompute and verify a persisted assignment artifact"
    )
    replay.add_argument("artifact", type=Path)
    replay.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    replay.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)

    inspect = subparsers.add_parser(
        "inspect", help="inspect an artifact without executing a stimulus"
    )
    inspect.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            config, result = make_fixed_assignment(
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            artifact_id = relative_column_artifact_id(config, result)
            destination = args.output_root / artifact_id
            if destination.exists():
                artifact = replay_relative_column_artifact(
                    destination,
                    source_root=args.source_root,
                    workbook_path=args.workbook,
                )
                disposition = "existing-immutable-artifact-replayed"
            else:
                artifact = export_relative_column_artifact(config, result, destination)
                disposition = "created"
        elif args.command == "replay":
            artifact = replay_relative_column_artifact(
                args.artifact,
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            disposition = "replay-verified"
        else:
            artifact = load_relative_column_artifact(args.artifact)
            disposition = "integrity-verified-no-replay"
        summary = artifact.inspection_dict()
        summary["operation"] = disposition
        summary["artifact_path"] = str(artifact.path)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (RelativeColumnAssignmentError, RelativeColumnArtifactError, OSError) as exc:
        print(f"relative-column assignment failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - covered by CLI smoke tests
    raise SystemExit(main())
