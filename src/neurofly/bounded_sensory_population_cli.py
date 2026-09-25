"""Generate, inspect, replay, and summarize the offline Phase 7H sample/run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.bounded_sensory_population import (
    DEFAULT_EXPERIMENT_OUTPUT_ROOT,
    DEFAULT_SAMPLE_OUTPUT_ROOT,
    make_source_bundle,
    select_bounded_sample,
)
from neurofly.bounded_sensory_population_artifacts import (
    BoundedPopulationArtifactError,
    export_population_artifact,
    export_sample_artifact,
    load_population_artifact,
    load_sample_artifact,
    make_population_artifact_payload,
    population_artifact_id,
    replay_population_artifact,
    replay_sample_artifact,
    sample_artifact_id,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT, DEFAULT_WORKBOOK


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("sample-generate", "sample-replay"):
        command = commands.add_parser(name)
        if name == "sample-replay":
            command.add_argument("artifact", type=Path)
        command.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
        command.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
        if name == "sample-generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_SAMPLE_OUTPUT_ROOT
            )
    sample_inspect = commands.add_parser("sample-inspect")
    sample_inspect.add_argument("artifact", type=Path)

    for name in ("experiment-generate", "experiment-replay"):
        command = commands.add_parser(name)
        command.add_argument("sample_artifact", type=Path)
        if name == "experiment-replay":
            command.add_argument("artifact", type=Path)
        command.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
        command.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
        if name == "experiment-generate":
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_EXPERIMENT_OUTPUT_ROOT
            )
    for name in ("experiment-inspect", "summary"):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "sample-generate":
            source, _, circuit = make_source_bundle(
                str(args.source_root), str(args.workbook)
            )
            config, result = select_bounded_sample(source, circuit)
            destination = args.output_root / sample_artifact_id(config, result)
            if destination.exists():
                artifact = replay_sample_artifact(
                    destination,
                    source_root=args.source_root,
                    workbook_path=args.workbook,
                )
                operation = "existing-sample-replay-verified"
            else:
                artifact = export_sample_artifact(config, result, destination)
                operation = "sample-persisted-before-model-run"
            output = artifact.summary()
        elif args.command == "sample-replay":
            artifact = replay_sample_artifact(
                args.artifact, source_root=args.source_root, workbook_path=args.workbook
            )
            output = artifact.summary()
            operation = "source-selection-replay-verified"
        elif args.command == "sample-inspect":
            artifact = load_sample_artifact(args.artifact)
            output = artifact.summary()
            operation = "integrity-verified-no-source-replay"
        elif args.command == "experiment-generate":
            config, result = make_population_artifact_payload(
                args.sample_artifact,
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            destination = args.output_root / population_artifact_id(config, result)
            if destination.exists():
                artifact = replay_population_artifact(
                    destination,
                    args.sample_artifact,
                    source_root=args.source_root,
                    workbook_path=args.workbook,
                )
                operation = "existing-experiment-full-replay-verified"
            else:
                artifact = export_population_artifact(config, result, destination)
                operation = "created-after-sample-persistence"
            output = artifact.summary()
        elif args.command == "experiment-replay":
            artifact = replay_population_artifact(
                args.artifact,
                args.sample_artifact,
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            output = artifact.summary()
            operation = "full-source-pipeline-replay-verified"
        else:
            artifact = load_population_artifact(args.artifact)
            output = artifact.summary()
            operation = "integrity-verified-no-replay"
        output["operation"] = operation
        output["artifact_path"] = str(artifact.path)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (BoundedPopulationArtifactError, OSError, ValueError) as exc:
        print(f"Phase 7H error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI smoke-tested
    raise SystemExit(main())
