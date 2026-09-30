"""EXPLORATORY PARAMETER SENSITIVITY: generate/inspect/replay, NO EMPIRICAL FITTING."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neurofly.g1_proxy_electrical_sensitivity import DEFAULT_MODEL_ARTIFACT
from neurofly.g1_proxy_electrical_sensitivity_artifacts import (
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
            "--model-artifact", type=Path, default=DEFAULT_MODEL_ARTIFACT
        )
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
            )
        else:
            command.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    try:
        path = (
            generate_sensitivity_artifact(
                output_root=args.output_root, model_artifact=args.model_artifact
            )
            if args.command == "generate"
            else args.artifact
        )
        experiment = replay_sensitivity_artifact(
            path, model_artifact=args.model_artifact
        )
        print(
            json.dumps(
                sensitivity_summary(
                    path, experiment, include_cells=args.command == "inspect"
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"G1-proxy sensitivity error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
