"""Generate, inspect or replay the exploratory UNCALIBRATED G1-proxy response."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neurofly.g1_proxy_passive_electrical import (
    DEFAULT_PROXY_ARTIFACT,
    reference_config,
)
from neurofly.g1_proxy_passive_electrical_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    artifact_summary,
    generate_response_artifact,
    replay_response_artifact,
)
from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument(
            "--input-artifact", type=Path, default=DEFAULT_SOURCE_PATHS["phase8w"]
        )
        command.add_argument(
            "--proxy-artifact", type=Path, default=DEFAULT_PROXY_ARTIFACT
        )
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
            )
        else:
            command.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    sources = {
        "input_artifact": args.input_artifact,
        "proxy_artifact": args.proxy_artifact,
    }
    try:
        path = (
            generate_response_artifact(
                reference_config(), output_root=args.output_root, **sources
            )
            if args.command == "generate"
            else args.artifact
        )
        response = replay_response_artifact(path, **sources)
        print(json.dumps(artifact_summary(path, response), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"G1-proxy model artifact error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
