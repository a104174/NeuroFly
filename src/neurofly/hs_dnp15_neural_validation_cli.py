"""Generate, inspect or replay the frozen HS→DNp15 neural validation artifact."""

import argparse
import json
import sys
import time

from neurofly.hs_dnp15_neural_validation_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    _load,
    artifact_summary,
    generate_neural_artifact,
    replay_neural_artifact,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        if name == "generate":
            command.add_argument("--output-root", default=DEFAULT_ARTIFACT_ROOT)
        else:
            command.add_argument("artifact")
    args = parser.parse_args(argv)
    try:
        start = time.perf_counter()
        if args.command == "generate":
            path = generate_neural_artifact(output_root=args.output_root)
            response = _load(path)
        else:
            path = args.artifact
            response = replay_neural_artifact(path)
        summary = artifact_summary(path, response)
        summary["diagnostic_wall_seconds_not_hashed"] = time.perf_counter() - start
        print(json.dumps(summary, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(f"HS/DNp15 validation error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
