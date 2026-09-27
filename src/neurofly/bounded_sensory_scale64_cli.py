"""Offline generate, inspect, and replay the Phase 7L 64-body experiment."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Sequence

from neurofly.bounded_sensory_scale64 import (
    CANONICAL_BATTERY_IDS,
    SAMPLE_C_ID,
    SAMPLE_D_ID,
    BoundedSensoryScale64Error,
    canonical_phase7l_context,
    compose_four_samples,
    compute_population64_experiment,
    make_coverage_plan64,
    scale64_artifact_id,
    select_disjoint_sample,
)
from neurofly.bounded_sensory_scale64_artifacts import (
    BoundedSensoryScale64ArtifactError,
    export_scale64_artifact,
    load_scale64_artifact,
    scale64_artifact_path,
)


def _sample_path(label: str, artifact_id: str) -> Path:
    return scale64_artifact_path("sample", artifact_id, sample_label=label)


def _input(artifact):
    return artifact.as_input() if hasattr(artifact, "as_input") else artifact


def _replay_sample(label: str, path: Path, context):
    artifact = load_scale64_artifact(path, "sample")
    parents = [context["sample_a"].as_input(), context["sample_b"].as_input()]
    expected_sample_id = SAMPLE_C_ID if label == "C" else SAMPLE_D_ID
    if label == "D":
        c_id = artifact.config["exclusion_parent_artifacts"][2]["artifact_id"]
        c_path = _sample_path("C", c_id)
        sample_c = load_scale64_artifact(c_path, "sample")
        parents.append(sample_c.as_input())
    config, result = select_disjoint_sample(
        expected_sample_id,
        parents,
        context["source"],
        context["circuit"],
    )
    expected_id = scale64_artifact_id("sample", config, result)
    if (
        artifact.artifact_id != expected_id
        or artifact.config != config
        or artifact.result != result
    ):
        raise BoundedSensoryScale64Error(f"Sample {label} failed deterministic replay.")
    return artifact


def _replay_samples(path_c: Path, path_d: Path, context):
    sample_c = _replay_sample("C", path_c, context)
    sample_d = _replay_sample("D", path_d, context)
    if set(sample_c.result["body_ids"]) & set(sample_d.result["body_ids"]):
        raise BoundedSensoryScale64Error("Sample C/D overlap after replay.")
    return sample_c, sample_d


def _composition_payload(path_c: Path, path_d: Path, context):
    sample_c, sample_d = _replay_samples(path_c, path_d, context)
    samples = [
        context["sample_a"].as_input(),
        context["sample_b"].as_input(),
        sample_c.as_input(),
        sample_d.as_input(),
    ]
    config, result = compose_four_samples(
        samples, context["source"], context["circuit"]
    )
    return config, result


def _replay_composition(path: Path, path_c: Path, path_d: Path, context):
    artifact = load_scale64_artifact(path, "composition")
    config, result = _composition_payload(path_c, path_d, context)
    if artifact.config != config or artifact.result != result:
        raise BoundedSensoryScale64Error(
            "64-body composition failed full source replay."
        )
    return artifact


def _plan_payload(path_composition: Path, path_c: Path, path_d: Path, context):
    composition = _replay_composition(path_composition, path_c, path_d, context)
    config, result = make_coverage_plan64(
        composition.as_input(),
        context["phase7k"],
        context["source"],
        context["grid"],
    )
    return config, result


def _experiment_payload(
    path_composition: Path,
    path_plan: Path,
    path_c: Path,
    path_d: Path,
    context,
):
    composition = _replay_composition(path_composition, path_c, path_d, context)
    plan = load_scale64_artifact(path_plan, "plan")
    expected_plan_config, expected_plan_result = make_coverage_plan64(
        composition.as_input(),
        context["phase7k"],
        context["source"],
        context["grid"],
    )
    if plan.config != expected_plan_config or plan.result != expected_plan_result:
        raise BoundedSensoryScale64Error("64-body coverage plan failed replay.")
    return compute_population64_experiment(
        composition.as_input(),
        plan.as_input(),
        context["phase7k"],
        context["phase7h"],
        context["phase7i"],
        context["phase7j"],
        context["source"],
        context["grid"],
        context["circuit"],
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "samples-generate", help="replay parents, select/persist C then D"
    )
    sample_replay = commands.add_parser("sample-replay")
    sample_replay.add_argument("label", choices=("C", "D"))
    sample_replay.add_argument("artifact", type=Path)
    composition_generate = commands.add_parser("composition-generate")
    composition_generate.add_argument("sample_c", type=Path)
    composition_generate.add_argument("sample_d", type=Path)
    composition_replay = commands.add_parser("composition-replay")
    composition_replay.add_argument("sample_c", type=Path)
    composition_replay.add_argument("sample_d", type=Path)
    composition_replay.add_argument("artifact", type=Path)
    plan_generate = commands.add_parser("coverage-plan-generate")
    plan_generate.add_argument("composition", type=Path)
    plan_generate.add_argument("sample_c", type=Path)
    plan_generate.add_argument("sample_d", type=Path)
    plan_replay = commands.add_parser("coverage-plan-replay")
    plan_replay.add_argument("composition", type=Path)
    plan_replay.add_argument("sample_c", type=Path)
    plan_replay.add_argument("sample_d", type=Path)
    plan_replay.add_argument("artifact", type=Path)
    experiment_generate = commands.add_parser("experiment-generate")
    experiment_generate.add_argument("composition", type=Path)
    experiment_generate.add_argument("plan", type=Path)
    experiment_generate.add_argument("sample_c", type=Path)
    experiment_generate.add_argument("sample_d", type=Path)
    experiment_replay = commands.add_parser("experiment-replay")
    experiment_replay.add_argument("composition", type=Path)
    experiment_replay.add_argument("plan", type=Path)
    experiment_replay.add_argument("sample_c", type=Path)
    experiment_replay.add_argument("sample_d", type=Path)
    experiment_replay.add_argument("artifact", type=Path)
    for name, kind in (
        ("sample-inspect", "sample"),
        ("composition-inspect", "composition"),
        ("coverage-plan-inspect", "plan"),
        ("experiment-inspect", "experiment"),
    ):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)
        command.set_defaults(artifact_kind=kind)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    start = time.perf_counter()
    try:
        if args.command == "samples-generate":
            parent_start = time.perf_counter()
            context = canonical_phase7l_context()
            parent_elapsed = time.perf_counter() - parent_start
            sample_a = context["sample_a"].as_input()
            sample_b = context["sample_b"].as_input()
            c_selection_start = time.perf_counter()
            config_c, result_c = select_disjoint_sample(
                SAMPLE_C_ID,
                [sample_a, sample_b],
                context["source"],
                context["circuit"],
            )
            artifact_c = export_scale64_artifact(
                "sample",
                config_c,
                result_c,
                output_root=scale64_artifact_path(
                    "sample", "unused", sample_label="C"
                ).parent,
            )
            c_selection_elapsed = time.perf_counter() - c_selection_start
            replay_c_start = time.perf_counter()
            replayed_c = _replay_sample("C", artifact_c.path, context)
            replay_c_elapsed = time.perf_counter() - replay_c_start
            d_selection_start = time.perf_counter()
            config_d, result_d = select_disjoint_sample(
                SAMPLE_D_ID,
                [sample_a, sample_b, replayed_c.as_input()],
                context["source"],
                context["circuit"],
            )
            artifact_d = export_scale64_artifact(
                "sample",
                config_d,
                result_d,
                output_root=scale64_artifact_path(
                    "sample", "unused", sample_label="D"
                ).parent,
            )
            d_selection_elapsed = time.perf_counter() - d_selection_start
            replay_d_start = time.perf_counter()
            replayed_d = _replay_sample("D", artifact_d.path, context)
            replay_d_elapsed = time.perf_counter() - replay_d_start
            output = {
                "sample_c": artifact_c.summary(),
                "sample_d": artifact_d.summary(),
                "pairwise_new_sample_overlap": len(
                    set(replayed_c.result["body_ids"])
                    & set(replayed_d.result["body_ids"])
                ),
                "model_outcomes_used": False,
                "phase_timings_seconds": {
                    "canonical_A_B_7K_parent_replay": round(parent_elapsed, 3),
                    "sample_c_selection_and_persist": round(c_selection_elapsed, 3),
                    "sample_c_replay": round(replay_c_elapsed, 3),
                    "sample_d_selection_and_persist": round(d_selection_elapsed, 3),
                    "sample_d_replay": round(replay_d_elapsed, 3),
                },
            }
        elif args.command == "sample-replay":
            context = canonical_phase7l_context()
            output = _replay_sample(args.label, args.artifact, context).summary()
        elif args.command in {"composition-generate", "composition-replay"}:
            context = canonical_phase7l_context()
            if args.command == "composition-generate":
                config, result = _composition_payload(
                    args.sample_c, args.sample_d, context
                )
                artifact = export_scale64_artifact("composition", config, result)
            else:
                artifact = _replay_composition(
                    args.artifact, args.sample_c, args.sample_d, context
                )
            output = artifact.summary()
        elif args.command in {"coverage-plan-generate", "coverage-plan-replay"}:
            context = canonical_phase7l_context()
            if args.command == "coverage-plan-generate":
                config, result = _plan_payload(
                    args.composition, args.sample_c, args.sample_d, context
                )
                artifact = export_scale64_artifact("plan", config, result)
            else:
                artifact = load_scale64_artifact(args.artifact, "plan")
                config, result = _plan_payload(
                    args.composition, args.sample_c, args.sample_d, context
                )
                if artifact.config != config or artifact.result != result:
                    raise BoundedSensoryScale64Error(
                        "64-body plan failed deterministic replay."
                    )
            output = artifact.summary()
            output.update(
                {
                    "initial_coverage_count": sum(
                        row["body_stimulus_covered"]
                        for row in artifact.result["initial_coverage"]
                    ),
                    "initial_uncovered_body_ids": artifact.result[
                        "initial_uncovered_body_ids"
                    ],
                    "added_stimuli": artifact.result["coverage_extension_stimuli"],
                    "final_coverage_count": len(
                        artifact.result["final_covered_body_ids"]
                    ),
                    "retained_stimulus_ids": list(CANONICAL_BATTERY_IDS),
                }
            )
        elif args.command in {"experiment-generate", "experiment-replay"}:
            context = canonical_phase7l_context()
            if args.command == "experiment-generate":
                config, result = _experiment_payload(
                    args.composition,
                    args.plan,
                    args.sample_c,
                    args.sample_d,
                    context,
                )
                artifact = export_scale64_artifact("experiment", config, result)
            else:
                artifact = load_scale64_artifact(args.artifact, "experiment")
                config, result = _experiment_payload(
                    args.composition,
                    args.plan,
                    args.sample_c,
                    args.sample_d,
                    context,
                )
                if artifact.config != config or artifact.result != result:
                    raise BoundedSensoryScale64Error(
                        "64-body experiment failed full deterministic replay."
                    )
            output = artifact.summary()
            output.update(
                {
                    "target_summary": artifact.result["target_summary"],
                    "nested_32_comparison_count": len(
                        artifact.result["phase7k_A_B_only_nested_regression"]
                    ),
                    "additivity_comparisons": artifact.result[
                        "per_step_A_B_C_D_additivity_comparisons"
                    ],
                    "source_accounting_comparisons": artifact.result[
                        "per_step_source_accounting_comparisons"
                    ],
                }
            )
        else:
            artifact = load_scale64_artifact(args.artifact, args.artifact_kind)
            output = artifact.summary()
        output["elapsed_seconds_this_command"] = round(time.perf_counter() - start, 3)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (
        BoundedSensoryScale64ArtifactError,
        BoundedSensoryScale64Error,
        OSError,
        ValueError,
    ) as exc:
        print(f"Phase 7L error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI smoke-tested
    raise SystemExit(main())
