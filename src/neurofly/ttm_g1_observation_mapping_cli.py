"""Generate, inspect, and replay Phase 8U observation-mapping metadata offline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neurofly.ttm_g1_observation_mapping import DEFAULT_SOURCE_ARTIFACT
from neurofly.ttm_g1_observation_mapping_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    generate_ttm_g1_mapping_artifact,
    replay_ttm_g1_mapping_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument(
            "--source-observation-artifact", type=Path, default=DEFAULT_SOURCE_ARTIFACT
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
            artifact = generate_ttm_g1_mapping_artifact(
                source_artifact=args.source_observation_artifact,
                output_root=args.output_root,
            )
        else:
            artifact = replay_ttm_g1_mapping_artifact(
                args.artifact, source_artifact=args.source_observation_artifact
            )
        output = artifact.summary(
            include_mappings=args.command == "inspect",
            source_artifact=args.source_observation_artifact,
        )
        output["operation"] = "offline-source-and-curated-mapping-replay-verified"
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"TTM G1 mapping contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
