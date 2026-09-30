"""Generate, inspect or replay exploratory functional TTM actuator commands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neurofly.ttm_actuator import DEFAULT_SOURCE_ARTIFACT
from neurofly.ttm_actuator_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    artifact_summary,
    generate_command_artifact,
    replay_command_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument(
            "--source-artifact", type=Path, default=DEFAULT_SOURCE_ARTIFACT
        )
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
            )
        else:
            command.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    try:
        sources = {"source_artifact": args.source_artifact}
        path = (
            generate_command_artifact(output_root=args.output_root, **sources)
            if args.command == "generate"
            else args.artifact
        )
        response = replay_command_artifact(path, **sources)
        print(json.dumps(artifact_summary(path, response), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Actuator artifact error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
