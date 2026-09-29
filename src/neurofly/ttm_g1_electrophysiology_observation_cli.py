"""Generate, inspect, and replay the offline TTM G1 observation contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.ttm_g1_electrophysiology_observation_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    TTMG1ObservationArtifactError,
    generate_ttm_g1_observation_artifact,
    load_ttm_g1_observation_artifact,
    replay_ttm_g1_observation_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument("--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("artifact", type=Path)
    replay = commands.add_parser("replay")
    replay.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_ttm_g1_observation_artifact(
                output_root=args.output_root
            )
            operation = "generated-or-existing-offline-curated-replay-verified"
        elif args.command == "replay":
            artifact = replay_ttm_g1_observation_artifact(args.artifact)
            operation = "offline-curated-definition-replay-verified"
        else:
            artifact = load_ttm_g1_observation_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        output = artifact.summary(include_observations=args.command == "inspect")
        output["operation"] = operation
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, TTMG1ObservationArtifactError) as exc:
        print(f"TTM G1 observation contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
