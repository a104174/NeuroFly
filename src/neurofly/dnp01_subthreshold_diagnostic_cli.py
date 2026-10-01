"""Generate, inspect or replay canonical subthreshold response accounting."""

import argparse
import json
import sys
from pathlib import Path

from neurofly.dnp01_subthreshold_diagnostic_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    diagnostic_summary,
    generate_diagnostic_artifact,
    replay_diagnostic_artifact,
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
        path = (
            generate_diagnostic_artifact(output_root=args.output_root)
            if args.command == "generate"
            else args.artifact
        )
        payload = replay_diagnostic_artifact(path)
        print(json.dumps(diagnostic_summary(path, payload), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Subthreshold diagnostic error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
