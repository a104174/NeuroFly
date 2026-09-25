"""Generate, inspect, and fully replay the offline Phase 7I coverage run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.bounded_sensory_coverage import (
    DEFAULT_EXPERIMENT_OUTPUT_ROOT,
    DEFAULT_PLAN_OUTPUT_ROOT,
)
from neurofly.bounded_sensory_coverage_artifacts import (
    DEFAULT_PHASE7H_ARTIFACT_PATH,
    DEFAULT_SAMPLE_ARTIFACT_PATH,
    BoundedSensoryCoverageArtifactError,
    coverage_artifact_id,
    export_coverage_experiment,
    export_coverage_plan,
    load_coverage_experiment,
    load_coverage_plan,
    make_coverage_experiment_payload,
    make_coverage_plan_payload,
    plan_artifact_id,
    replay_coverage_experiment,
    replay_coverage_plan,
)


def _add_sources(command: argparse.ArgumentParser) -> None:
    command.add_argument("--sample", type=Path, default=DEFAULT_SAMPLE_ARTIFACT_PATH)
    command.add_argument("--phase7h", type=Path, default=DEFAULT_PHASE7H_ARTIFACT_PATH)
    command.add_argument("--source-root", type=Path)
    command.add_argument("--workbook", type=Path)


def _source_kwargs(args: argparse.Namespace) -> dict[str, object]:
    result: dict[str, object] = {}
    if args.source_root is not None:
        result["source_root"] = args.source_root
    if args.workbook is not None:
        result["workbook_path"] = args.workbook
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    plan_generate = commands.add_parser("plan-generate")
    _add_sources(plan_generate)
    plan_generate.add_argument(
        "--output-root", type=Path, default=DEFAULT_PLAN_OUTPUT_ROOT
    )

    plan_replay = commands.add_parser("plan-replay")
    plan_replay.add_argument("artifact", type=Path)
    _add_sources(plan_replay)

    plan_inspect = commands.add_parser("plan-inspect")
    plan_inspect.add_argument("artifact", type=Path)

    experiment_generate = commands.add_parser("experiment-generate")
    experiment_generate.add_argument("plan", type=Path)
    _add_sources(experiment_generate)
    experiment_generate.add_argument(
        "--output-root", type=Path, default=DEFAULT_EXPERIMENT_OUTPUT_ROOT
    )

    experiment_replay = commands.add_parser("experiment-replay")
    experiment_replay.add_argument("artifact", type=Path)
    experiment_replay.add_argument("plan", type=Path)
    _add_sources(experiment_replay)

    for name in ("experiment-inspect", "coverage-summary"):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "plan-generate":
            config, result = make_coverage_plan_payload(
                args.sample, args.phase7h, **_source_kwargs(args)
            )
            destination = args.output_root / plan_artifact_id(config, result)
            if destination.exists():
                artifact = replay_coverage_plan(
                    destination,
                    args.sample,
                    args.phase7h,
                    **_source_kwargs(args),
                )
                operation = "existing-anatomy-only-plan-replay-verified"
            else:
                artifact = export_coverage_plan(config, result, destination)
                operation = "coverage-plan-persisted-before-dynamics"
            output = artifact.summary()
        elif args.command == "plan-replay":
            artifact = replay_coverage_plan(
                args.artifact, args.sample, args.phase7h, **_source_kwargs(args)
            )
            output = artifact.summary()
            operation = "full-source-anatomical-plan-replay-verified"
        elif args.command == "plan-inspect":
            artifact = load_coverage_plan(args.artifact)
            output = artifact.summary()
            operation = "integrity-verified-no-source-replay"
        elif args.command == "experiment-generate":
            config, result = make_coverage_experiment_payload(
                args.plan, args.sample, args.phase7h, **_source_kwargs(args)
            )
            destination = args.output_root / coverage_artifact_id(config, result)
            if destination.exists():
                artifact = replay_coverage_experiment(
                    destination,
                    args.plan,
                    args.sample,
                    args.phase7h,
                    **_source_kwargs(args),
                )
                operation = "existing-coverage-experiment-full-replay-verified"
            else:
                artifact = export_coverage_experiment(config, result, destination)
                operation = "coverage-experiment-persisted"
            output = artifact.summary()
        elif args.command == "experiment-replay":
            artifact = replay_coverage_experiment(
                args.artifact,
                args.plan,
                args.sample,
                args.phase7h,
                **_source_kwargs(args),
            )
            output = artifact.summary()
            operation = "full-source-coverage-pipeline-replay-verified"
        else:
            artifact = load_coverage_experiment(args.artifact)
            output = artifact.summary()
            operation = "integrity-verified-no-source-replay"
        output["operation"] = operation
        output["artifact_path"] = str(artifact.path)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (BoundedSensoryCoverageArtifactError, OSError, ValueError) as exc:
        print(f"Phase 7I error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI smoke-tested
    raise SystemExit(main())
