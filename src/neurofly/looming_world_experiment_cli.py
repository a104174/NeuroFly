"""Generate, inspect and replay the frozen longer looming world experiment."""

import argparse
import json
import sys
import time
from pathlib import Path

from neurofly.looming_world_experiment_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    artifact_summary,
    generate_world_artifact,
    replay_world_artifact,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
            )
        else:
            command.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    try:
        start = time.perf_counter()
        path = (
            generate_world_artifact(output_root=args.output_root)
            if args.command == "generate"
            else args.artifact
        )
        response = replay_world_artifact(path)
        summary = artifact_summary(path, response)
        summary["diagnostic_wall_seconds_not_hashed"] = time.perf_counter() - start
        print(json.dumps(summary, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"World experiment error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
