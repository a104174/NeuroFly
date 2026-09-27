"""Generate, inspect, and replay the offline Phase 7J Sample B experiment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.bounded_sensory_robustness import (
    DEFAULT_EXPERIMENT_B_ROOT,
    DEFAULT_PHASE7H_PATH,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_PHASE7I_PLAN_PATH,
    DEFAULT_PLAN_B_ROOT,
    DEFAULT_SAMPLE_A_PATH,
    DEFAULT_SAMPLE_B_ROOT,
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    make_sample_b_payload,
)
from neurofly.bounded_sensory_robustness_artifacts import (
    BoundedSensoryRobustnessArtifactError,
    export_sample_b_artifact,
    export_sample_b_experiment_artifact,
    export_sample_b_plan_artifact,
    load_sample_b_artifact,
    load_sample_b_experiment_artifact,
    load_sample_b_plan_artifact,
    make_sample_b_experiment_payload,
    make_sample_b_plan_payload,
    replay_sample_b_artifact,
    replay_sample_b_experiment_artifact,
    replay_sample_b_plan_artifact,
    sample_b_artifact_id,
    sample_b_experiment_artifact_id,
    sample_b_plan_artifact_id,
)


def _add_source_args(command: argparse.ArgumentParser) -> None:
    command.add_argument("--sample-a", type=Path, default=DEFAULT_SAMPLE_A_PATH)
    command.add_argument("--phase7h", type=Path, default=DEFAULT_PHASE7H_PATH)
    command.add_argument("--phase7i-plan", type=Path, default=DEFAULT_PHASE7I_PLAN_PATH)
    command.add_argument(
        "--phase7i-experiment", type=Path, default=DEFAULT_PHASE7I_EXPERIMENT_PATH
    )
    command.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    command.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)


def _source_kwargs(args: argparse.Namespace) -> dict[str, object]:
    return {
        "sample_a_path": args.sample_a,
        "phase7h_path": args.phase7h,
        "phase7i_plan_path": args.phase7i_plan,
        "phase7i_experiment_path": args.phase7i_experiment,
        "source_root": args.source_root,
        "workbook_path": args.workbook,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    sample_generate = commands.add_parser("sample-generate")
    sample_generate.add_argument("--sample-a", type=Path, default=DEFAULT_SAMPLE_A_PATH)
    sample_generate.add_argument(
        "--source-root", type=Path, default=DEFAULT_SOURCE_ROOT
    )
    sample_generate.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    sample_generate.add_argument(
        "--output-root", type=Path, default=DEFAULT_SAMPLE_B_ROOT
    )

    sample_replay = commands.add_parser("sample-replay")
    sample_replay.add_argument("artifact", type=Path)
    sample_replay.add_argument("--sample-a", type=Path, default=DEFAULT_SAMPLE_A_PATH)
    sample_replay.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    sample_replay.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)

    for name in ("sample-inspect", "plan-inspect", "experiment-inspect"):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)

    plan_generate = commands.add_parser("plan-generate")
    plan_generate.add_argument("sample_b", type=Path)
    _add_source_args(plan_generate)
    plan_generate.add_argument("--output-root", type=Path, default=DEFAULT_PLAN_B_ROOT)

    plan_replay = commands.add_parser("plan-replay")
    plan_replay.add_argument("artifact", type=Path)
    plan_replay.add_argument("sample_b", type=Path)
    _add_source_args(plan_replay)

    experiment_generate = commands.add_parser("experiment-generate")
    experiment_generate.add_argument("sample_b", type=Path)
    experiment_generate.add_argument("plan_b", type=Path)
    _add_source_args(experiment_generate)
    experiment_generate.add_argument(
        "--output-root", type=Path, default=DEFAULT_EXPERIMENT_B_ROOT
    )

    experiment_replay = commands.add_parser("experiment-replay")
    experiment_replay.add_argument("artifact", type=Path)
    experiment_replay.add_argument("sample_b", type=Path)
    experiment_replay.add_argument("plan_b", type=Path)
    _add_source_args(experiment_replay)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "sample-generate":
            config, result = make_sample_b_payload(
                args.sample_a,
                source_root=str(args.source_root),
                workbook_path=str(args.workbook),
            )
            destination = args.output_root / sample_b_artifact_id(config, result)
            if destination.exists():
                artifact = replay_sample_b_artifact(
                    destination,
                    args.sample_a,
                    source_root=args.source_root,
                    workbook_path=args.workbook,
                )
                operation = "existing-outcome-blind-sample-replay-verified"
            else:
                artifact = export_sample_b_artifact(config, result, destination)
                operation = "sample-b-persisted-before-coverage-or-dynamics"
            output = artifact.summary()
        elif args.command == "sample-replay":
            artifact = replay_sample_b_artifact(
                args.artifact,
                args.sample_a,
                source_root=args.source_root,
                workbook_path=args.workbook,
            )
            output = artifact.summary()
            operation = "source-only-sample-selection-replay-verified"
        elif args.command == "sample-inspect":
            artifact = load_sample_b_artifact(args.artifact)
            output = artifact.summary()
            operation = "integrity-verified-no-source-replay"
        elif args.command == "plan-generate":
            config, result = make_sample_b_plan_payload(
                args.sample_b, **_source_kwargs(args)
            )
            destination = args.output_root / sample_b_plan_artifact_id(config, result)
            if destination.exists():
                artifact = replay_sample_b_plan_artifact(
                    destination, args.sample_b, **_source_kwargs(args)
                )
                operation = "existing-anatomy-only-plan-replay-verified"
            else:
                artifact = export_sample_b_plan_artifact(config, result, destination)
                operation = "sample-b-coverage-plan-persisted-before-dynamics"
            output = artifact.summary()
        elif args.command == "plan-replay":
            artifact = replay_sample_b_plan_artifact(
                args.artifact, args.sample_b, **_source_kwargs(args)
            )
            output = artifact.summary()
            operation = "full-source-anatomical-plan-replay-verified"
        elif args.command == "plan-inspect":
            artifact = load_sample_b_plan_artifact(args.artifact)
            output = artifact.summary()
            operation = "integrity-verified-no-source-replay"
        elif args.command == "experiment-generate":
            config, result = make_sample_b_experiment_payload(
                args.sample_b, args.plan_b, **_source_kwargs(args)
            )
            destination = args.output_root / sample_b_experiment_artifact_id(
                config, result
            )
            if destination.exists():
                artifact = replay_sample_b_experiment_artifact(
                    destination,
                    args.sample_b,
                    args.plan_b,
                    **_source_kwargs(args),
                )
                operation = "existing-experiment-full-replay-verified"
            else:
                artifact = export_sample_b_experiment_artifact(
                    config, result, destination
                )
                operation = "created-from-persisted-sample-and-plan"
            output = artifact.summary()
        elif args.command == "experiment-replay":
            artifact = replay_sample_b_experiment_artifact(
                args.artifact,
                args.sample_b,
                args.plan_b,
                **_source_kwargs(args),
            )
            output = artifact.summary()
            operation = "full-source-sample-b-pipeline-replay-verified"
        else:
            artifact = load_sample_b_experiment_artifact(args.artifact)
            output = artifact.summary()
            operation = "integrity-verified-no-source-replay"
        output["operation"] = operation
        output["artifact_path"] = str(artifact.path)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (BoundedSensoryRobustnessArtifactError, OSError, ValueError) as exc:
        print(f"Phase 7J error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI smoke-tested
    raise SystemExit(main())
