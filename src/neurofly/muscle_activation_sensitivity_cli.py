"""Generate, inspect or replay activation-scale sensitivity; no fitting."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neurofly.muscle_activation import DEFAULT_MODEL_ARTIFACT
from neurofly.muscle_activation_sensitivity import DEFAULT_ACTIVATION_ARTIFACT
from neurofly.muscle_activation_sensitivity_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    generate_sensitivity_artifact,
    replay_sensitivity_artifact,
    sensitivity_summary,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument(
            "--activation-artifact", type=Path, default=DEFAULT_ACTIVATION_ARTIFACT
        )
        command.add_argument(
            "--electrical-artifact", type=Path, default=DEFAULT_MODEL_ARTIFACT
        )
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
            )
        else:
            command.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    try:
        sources = {
            "activation_artifact": args.activation_artifact,
            "electrical_artifact": args.electrical_artifact,
        }
        path = (
            generate_sensitivity_artifact(output_root=args.output_root, **sources)
            if args.command == "generate"
            else args.artifact
        )
        experiment = replay_sensitivity_artifact(path, **sources)
        print(
            json.dumps(sensitivity_summary(path, experiment), indent=2, sort_keys=True)
        )
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Activation sensitivity artifact error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
