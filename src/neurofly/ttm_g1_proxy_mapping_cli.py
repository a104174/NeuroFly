"""Generate, inspect or replay metadata-only G1 proxy domains offline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS
from neurofly.ttm_g1_proxy_mapping_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    generate_proxy_artifact,
    replay_proxy_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        for phase, path in DEFAULT_SOURCE_PATHS.items():
            command.add_argument(f"--{phase}-artifact", type=Path, default=path)
        if name == "generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT
            )
        else:
            command.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    paths = {
        phase: getattr(args, f"{phase}_artifact") for phase in DEFAULT_SOURCE_PATHS
    }
    try:
        if args.command == "generate":
            artifact = generate_proxy_artifact(
                source_paths=paths, output_root=args.output_root
            )
        else:
            artifact = replay_proxy_artifact(args.artifact, source_paths=paths)
        output = artifact.summary(include_mappings=args.command == "inspect")
        output["operation"] = "offline-source-and-proxy-metadata-replay-verified"
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"TTM G1 proxy contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
