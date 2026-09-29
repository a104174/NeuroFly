"""Generate, inspect, and replay the offline Phase 8N TTMn output rule."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_ttmn_output_rule import REFERENCE_THRESHOLD_DIMENSIONLESS
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SOURCE_ARTIFACT,
    SyntheticTTMnOutputArtifactError,
    generate_synthetic_ttmn_output_artifact,
    load_synthetic_ttmn_output_artifact,
    replay_synthetic_ttmn_output_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    generate.add_argument(
        "--source-artifact", type=Path, default=DEFAULT_SOURCE_ARTIFACT
    )
    generate.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    generate.add_argument(
        "--threshold-dimensionless",
        type=float,
        default=REFERENCE_THRESHOLD_DIMENSIONLESS,
        help="explicit MODEL_ASSUMPTION override; default is the pinned 0.25 reference",
    )
    for name in ("inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)
        if name == "replay":
            command.add_argument(
                "--source-root", type=Path, default=DEFAULT_SOURCE_ROOT
            )
            command.add_argument(
                "--source-artifact", type=Path, default=DEFAULT_SOURCE_ARTIFACT
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_synthetic_ttmn_output_artifact(
                source_artifact=args.source_artifact,
                source_root=args.source_root,
                output_root=args.output_root,
                threshold_dimensionless=args.threshold_dimensionless,
            )
            operation = "generated-or-existing-full-replay-verified"
        elif args.command == "replay":
            artifact = replay_synthetic_ttmn_output_artifact(
                args.artifact,
                source_artifact=args.source_artifact,
                source_root=args.source_root,
            )
            operation = "phase8b-source-and-threshold-result-replay-verified"
        else:
            artifact = load_synthetic_ttmn_output_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        summary = artifact.summary()
        summary["operation"] = operation
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, SyntheticTTMnOutputArtifactError) as exc:
        print(f"Phase 8N error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI smoke tested
    raise SystemExit(main())
