"""Generate, inspect, replay, and summarize the offline Phase 7F artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT, DEFAULT_WORKBOOK
from neurofly.relative_column_dnp01_artifacts import (
    DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SENSORY_ARTIFACT_PATH,
    TransferArtifactError,
    artifact_id,
    export_artifact,
    load_artifact,
    make_artifact_payload,
    replay_artifact,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "replay", "inspect", "sensitivity"):
        command = commands.add_parser(name)
        if name != "generate":
            command.add_argument("artifact", type=Path)
        if name in {"generate", "replay"}:
            command.add_argument(
                "--sensory-artifact", type=Path, default=DEFAULT_SENSORY_ARTIFACT_PATH
            )
            command.add_argument(
                "--assignment-artifact",
                type=Path,
                default=DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
            )
            command.add_argument(
                "--source-root", type=Path, default=DEFAULT_SOURCE_ROOT
            )
            command.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT
            )
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            kwargs = {
                "sensory_artifact_path": args.sensory_artifact,
                "assignment_artifact_path": args.assignment_artifact,
                "source_root": args.source_root,
                "workbook_path": args.workbook,
            }
            config, result = make_artifact_payload(**kwargs)
            path = args.output_root / artifact_id(config, result)
            if path.exists():
                artifact = replay_artifact(path, **kwargs)
                operation = "existing_immutable_artifact_replayed"
            else:
                artifact = export_artifact(config, result, path)
                operation = "created"
        elif args.command == "replay":
            artifact = replay_artifact(
                args.artifact,
                sensory_artifact_path=args.sensory_artifact,
                assignment_artifact_path=args.assignment_artifact,
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            operation = "full_source_replay_verified"
        else:
            artifact = load_artifact(args.artifact)
            operation = "integrity_verified_without_replay"
        output = artifact.summary()
        if args.command == "sensitivity":
            output["conditions"] = [
                item
                for item in output["conditions"]
                if item["condition_id"].startswith("sensitivity")
                or item["condition_id"] in {"reference_bilateral_expansion", "k_zero"}
            ]
        output["operation"] = operation
        output["artifact_path"] = str(artifact.path)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (TransferArtifactError, OSError, ValueError) as exc:
        print(f"Phase 7F error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
