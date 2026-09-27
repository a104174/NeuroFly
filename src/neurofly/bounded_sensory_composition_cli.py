"""Generate, inspect, and replay the offline Phase 7K 32-body union experiment."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Sequence

from neurofly.bounded_sensory_composition import (
    DEFAULT_COMPOSITION_ROOT,
    DEFAULT_COVERAGE_B_ARTIFACT,
    DEFAULT_PHASE7H_ARTIFACT,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_PHASE7I_PLAN_PATH,
    DEFAULT_PHASE7J_ARTIFACT,
    DEFAULT_POPULATION32_ROOT,
    DEFAULT_SAMPLE_A_ARTIFACT,
    DEFAULT_SAMPLE_B_ARTIFACT,
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
)
from neurofly.bounded_sensory_composition_artifacts import (
    BoundedSensoryCompositionArtifactError,
    export_composition_artifact,
    export_population32_artifact,
    load_composition_artifact,
    load_population32_artifact,
    make_composition_artifact_payload,
    make_population32_artifact_payload,
    replay_composition_artifact,
    replay_population32_artifact,
)


def _add_source_args(command: argparse.ArgumentParser) -> None:
    command.add_argument("--sample-a", type=Path, default=DEFAULT_SAMPLE_A_ARTIFACT)
    command.add_argument("--phase7h", type=Path, default=DEFAULT_PHASE7H_ARTIFACT)
    command.add_argument("--phase7i-plan", type=Path, default=DEFAULT_PHASE7I_PLAN_PATH)
    command.add_argument(
        "--phase7i-experiment", type=Path, default=DEFAULT_PHASE7I_EXPERIMENT_PATH
    )
    command.add_argument("--sample-b", type=Path, default=DEFAULT_SAMPLE_B_ARTIFACT)
    command.add_argument("--coverage-b", type=Path, default=DEFAULT_COVERAGE_B_ARTIFACT)
    command.add_argument("--experiment-b", type=Path, default=DEFAULT_PHASE7J_ARTIFACT)
    command.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    command.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)


def _source_kwargs(args: argparse.Namespace) -> dict[str, object]:
    return {
        "sample_a_path": args.sample_a,
        "phase7h_path": args.phase7h,
        "phase7i_plan_path": args.phase7i_plan,
        "phase7i_experiment_path": args.phase7i_experiment,
        "sample_b_path": args.sample_b,
        "coverage_b_path": args.coverage_b,
        "experiment_b_path": args.experiment_b,
        "source_root": args.source_root,
        "workbook_path": args.workbook,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    for name in ("composition-generate", "composition-replay"):
        command = commands.add_parser(name)
        _add_source_args(command)
        if name == "composition-replay":
            command.add_argument("artifact", type=Path)
        else:
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_COMPOSITION_ROOT
            )

    composition_inspect = commands.add_parser("composition-inspect")
    composition_inspect.add_argument("artifact", type=Path)

    for name in ("experiment-generate", "experiment-replay"):
        command = commands.add_parser(name)
        command.add_argument("composition", type=Path)
        _add_source_args(command)
        if name == "experiment-replay":
            command.add_argument("artifact", type=Path)
        else:
            command.add_argument(
                "--output-root", type=Path, default=DEFAULT_POPULATION32_ROOT
            )

    experiment_inspect = commands.add_parser("experiment-inspect")
    experiment_inspect.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    start = time.perf_counter()
    try:
        if args.command == "composition-generate":
            config, result, destination = make_composition_artifact_payload(
                output_root=args.output_root, **_source_kwargs(args)
            )
            if destination.exists():
                artifact = replay_composition_artifact(
                    destination, **_source_kwargs(args)
                )
                operation = "existing-composition-full-source-replay-verified"
            else:
                artifact = export_composition_artifact(config, result, destination)
                operation = "persisted-disjoint-union-before-dynamics"
        elif args.command == "composition-replay":
            artifact = replay_composition_artifact(
                args.artifact, **_source_kwargs(args)
            )
            operation = "sample-a-and-b-union-source-replay-verified"
        elif args.command == "composition-inspect":
            artifact = load_composition_artifact(args.artifact)
            operation = "integrity-verified-no-source-replay"
        elif args.command == "experiment-generate":
            config, result, destination = make_population32_artifact_payload(
                args.composition,
                output_root=args.output_root,
                **_source_kwargs(args),
            )
            if destination.exists():
                artifact = replay_population32_artifact(
                    destination, args.composition, **_source_kwargs(args)
                )
                operation = "existing-32-body-experiment-full-replay-verified"
            else:
                artifact = export_population32_artifact(config, result, destination)
                operation = (
                    "32-body-experiment-persisted-after-composition-and-coverage"
                )
        elif args.command == "experiment-replay":
            artifact = replay_population32_artifact(
                args.artifact, args.composition, **_source_kwargs(args)
            )
            operation = "full-source-a-b-union-experiment-replay-verified"
        else:
            artifact = load_population32_artifact(args.artifact)
            operation = "integrity-verified-no-source-replay"
        output = artifact.summary()
        output["operation"] = operation
        output["artifact_path"] = str(artifact.path)
        output["elapsed_seconds_this_command"] = round(time.perf_counter() - start, 3)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (BoundedSensoryCompositionArtifactError, OSError, ValueError) as exc:
        print(f"Phase 7K error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI smoke-tested
    raise SystemExit(main())
