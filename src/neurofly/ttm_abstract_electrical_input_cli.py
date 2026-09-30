"""Generate, inspect and offline-replay admission-only TTM abstract input tokens."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neurofly.ttm_abstract_electrical_input import DEFAULT_SOURCE_ARTIFACT
from neurofly.ttm_abstract_electrical_input_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    generate_abstract_input_artifact,
    replay_abstract_input_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument(
            "--source-receipt-artifact", type=Path, default=DEFAULT_SOURCE_ARTIFACT
        )
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
            )
        else:
            command.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_abstract_input_artifact(
                source_artifact=args.source_receipt_artifact,
                output_root=args.output_root,
            )
        else:
            artifact = replay_abstract_input_artifact(
                args.artifact, source_artifact=args.source_receipt_artifact
            )
        output = artifact.summary(include_tokens=args.command == "inspect")
        output["operation"] = "offline-phase8q-source-and-token-replay-verified"
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"TTM abstract input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
