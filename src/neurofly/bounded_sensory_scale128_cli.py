"""Generate, inspect, and fully replay Phase 7M's deterministic 128-body run."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Sequence

from neurofly.bounded_sensory_scale128 import (
    NEW_SAMPLE_LABELS,
    SAMPLE_LABELS,
    BoundedSensoryScale128Error,
    canonical_phase7m_context,
    compose_eight_samples,
    compute_population128_experiment,
    make_coverage_plan128,
    scale128_artifact_path,
    select_sample128,
)
from neurofly.bounded_sensory_scale128_artifacts import (
    BoundedSensoryScale128ArtifactError,
    export_scale128_artifact,
    load_scale128_artifact,
)


def _parents(context, earlier):
    canonical = [context[f"sample_{label.lower()}"].as_input() for label in "AB"]
    canonical.extend(context[f"sample_{label.lower()}"].as_input() for label in "CD")
    return [
        *canonical,
        *(earlier[label].as_input() for label in "EFGH" if label in earlier),
    ]


def _replay_sample(label: str, path: Path, context, earlier):
    if label not in NEW_SAMPLE_LABELS:
        raise BoundedSensoryScale128Error("sample label must be E, F, G, or H.")
    artifact = load_scale128_artifact(path, "sample")
    parents = _parents(context, earlier)
    if len(parents) != SAMPLE_LABELS.index(label):
        raise BoundedSensoryScale128Error(f"missing earlier parent sample for {label}.")
    config, result = select_sample128(
        label, parents, context["source"], context["circuit"]
    )
    if artifact.config != config or artifact.result != result:
        raise BoundedSensoryScale128Error(
            f"Sample {label} failed deterministic replay."
        )
    return artifact


def _sample_chain(context, paths=None):
    earlier = {}
    outputs = {}
    paths = paths or {}
    for label in NEW_SAMPLE_LABELS:
        path = Path(paths[label]) if label in paths else _find_sample_path(label)
        artifact = _replay_sample(label, path, context, earlier)
        earlier[label] = outputs[label] = artifact
    return outputs


def _find_sample_path(label: str) -> Path:
    root = scale128_artifact_path("sample", "unused", label=label).parent
    if not root.is_dir():
        raise BoundedSensoryScale128Error(f"Sample {label} has not been persisted.")
    candidates = [path for path in root.iterdir() if path.is_dir()]
    if len(candidates) != 1:
        raise BoundedSensoryScale128Error(
            f"expected exactly one persisted Sample {label}."
        )
    return candidates[0]


def _replay_composition(path: Path, context, samples):
    artifact = load_scale128_artifact(path, "composition")
    all_samples = [
        context["sample_a"].as_input(),
        context["sample_b"].as_input(),
        context["sample_c"].as_input(),
        context["sample_d"].as_input(),
        *(samples[label].as_input() for label in NEW_SAMPLE_LABELS),
    ]
    config, result = compose_eight_samples(
        all_samples, context["source"], context["circuit"]
    )
    if artifact.config != config or artifact.result != result:
        raise BoundedSensoryScale128Error(
            "128-body composition failed deterministic replay."
        )
    return artifact


def _replay_plan(path: Path, composition, context):
    artifact = load_scale128_artifact(path, "plan")
    config, result = make_coverage_plan128(
        composition.as_input(),
        context["plan64"],
        context["experiment64"],
        context["source"],
        context["grid"],
    )
    if artifact.config != config or artifact.result != result:
        raise BoundedSensoryScale128Error("128-body anatomy-only plan replay failed.")
    return artifact


def _replay_experiment(path: Path, plan, composition, context):
    artifact = load_scale128_artifact(path, "experiment")
    config, result = compute_population128_experiment(
        composition.as_input(),
        plan.as_input(),
        context["plan64"],
        context["experiment64"],
        context,
    )
    if artifact.config != config or artifact.result != result:
        raise BoundedSensoryScale128Error("128-body experiment failed full replay.")
    return artifact


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "samples-generate", help="select and persist E, F, G, H in order"
    )
    sample_replay = commands.add_parser("sample-replay")
    sample_replay.add_argument("label", choices=NEW_SAMPLE_LABELS)
    sample_replay.add_argument("artifact", type=Path)
    commands.add_parser("composition-generate")
    composition_replay = commands.add_parser("composition-replay")
    composition_replay.add_argument("artifact", type=Path)
    plan_generate = commands.add_parser("coverage-plan-generate")
    plan_generate.add_argument("composition", type=Path)
    plan_replay = commands.add_parser("coverage-plan-replay")
    plan_replay.add_argument("composition", type=Path)
    plan_replay.add_argument("artifact", type=Path)
    experiment_generate = commands.add_parser("experiment-generate")
    experiment_generate.add_argument("composition", type=Path)
    experiment_generate.add_argument("plan", type=Path)
    experiment_replay = commands.add_parser("experiment-replay")
    experiment_replay.add_argument("composition", type=Path)
    experiment_replay.add_argument("plan", type=Path)
    experiment_replay.add_argument("artifact", type=Path)
    inspect = commands.add_parser("inspect")
    inspect.add_argument(
        "kind", choices=("sample", "composition", "plan", "experiment")
    )
    inspect.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    started = time.perf_counter()
    try:
        if args.command == "inspect":
            artifact = load_scale128_artifact(args.artifact, args.kind)
            output = artifact.summary()
        else:
            context_started = time.perf_counter()
            context = canonical_phase7m_context()
            context_elapsed = time.perf_counter() - context_started
            output: dict
            if args.command == "samples-generate":
                earlier = {}
                samples = {}
                timings = {"phase7l_replay": round(context_elapsed, 3)}
                for label in NEW_SAMPLE_LABELS:
                    parents = _parents(context, earlier)
                    selection_start = time.perf_counter()
                    config, result = select_sample128(
                        label, parents, context["source"], context["circuit"]
                    )
                    artifact = export_scale128_artifact(
                        "sample", config, result, label=label
                    )
                    timings[f"sample_{label.lower()}_selection_persist"] = round(
                        time.perf_counter() - selection_start, 3
                    )
                    replay_start = time.perf_counter()
                    replayed = _replay_sample(label, artifact.path, context, earlier)
                    timings[f"sample_{label.lower()}_replay"] = round(
                        time.perf_counter() - replay_start, 3
                    )
                    earlier[label] = samples[label] = replayed
                output = {
                    "samples": {
                        label: artifact.summary() for label, artifact in samples.items()
                    },
                    "pairwise_new_sample_overlap": {
                        f"{left}{right}": len(
                            set(samples[left].result["body_ids"])
                            & set(samples[right].result["body_ids"])
                        )
                        for i, left in enumerate(NEW_SAMPLE_LABELS)
                        for right in NEW_SAMPLE_LABELS[i + 1 :]
                    },
                    "model_outcomes_used": False,
                    "phase_timings_seconds": timings,
                }
            elif args.command == "sample-replay":
                earlier = {}
                for label in NEW_SAMPLE_LABELS[: NEW_SAMPLE_LABELS.index(args.label)]:
                    path = _find_sample_path(label)
                    earlier[label] = _replay_sample(label, path, context, earlier)
                output = _replay_sample(
                    args.label, args.artifact, context, earlier
                ).summary()
            elif args.command in {"composition-generate", "composition-replay"}:
                samples = _sample_chain(context)
                parents = [
                    context[f"sample_{label.lower()}"].as_input() for label in "ABCD"
                ]
                parents.extend(samples[label].as_input() for label in NEW_SAMPLE_LABELS)
                config, result = compose_eight_samples(
                    parents, context["source"], context["circuit"]
                )
                if args.command == "composition-generate":
                    artifact = export_scale128_artifact("composition", config, result)
                else:
                    artifact = _replay_composition(args.artifact, context, samples)
                output = artifact.summary()
            elif args.command in {"coverage-plan-generate", "coverage-plan-replay"}:
                samples = _sample_chain(context)
                composition = _replay_composition(args.composition, context, samples)
                config, result = make_coverage_plan128(
                    composition.as_input(),
                    context["plan64"],
                    context["experiment64"],
                    context["source"],
                    context["grid"],
                )
                if args.command == "coverage-plan-generate":
                    artifact = export_scale128_artifact("plan", config, result)
                else:
                    artifact = _replay_plan(args.artifact, composition, context)
                output = artifact.summary()
                output.update(
                    {
                        "initial_coverage_count": sum(
                            row["body_stimulus_covered"]
                            for row in artifact.result["initial_coverage"]
                        ),
                        "initial_uncovered_body_count": len(
                            artifact.result["initial_uncovered_body_ids"]
                        ),
                        "initial_uncovered_body_ids": artifact.result[
                            "initial_uncovered_body_ids"
                        ],
                        "added_stimuli": artifact.result["coverage_extension_stimuli"],
                        "final_coverage_count": len(
                            artifact.result["final_covered_body_ids"]
                        ),
                        "model_outcomes_used": False,
                        "neural_dynamics_computed": False,
                    }
                )
            elif args.command in {"experiment-generate", "experiment-replay"}:
                samples = _sample_chain(context)
                composition = _replay_composition(args.composition, context, samples)
                plan = _replay_plan(args.plan, composition, context)
                if args.command == "experiment-generate":
                    config, result = compute_population128_experiment(
                        composition.as_input(),
                        plan.as_input(),
                        context["plan64"],
                        context["experiment64"],
                        context,
                    )
                    artifact = export_scale128_artifact("experiment", config, result)
                else:
                    artifact = _replay_experiment(
                        args.artifact, plan, composition, context
                    )
                output = artifact.summary()
                output.update(
                    {
                        "coverage_totals": artifact.result["coverage_totals"],
                        "assignment_sample_count": artifact.result["assignment"][
                            "sample_count"
                        ],
                        "ledger_rows": sum(
                            len(item["contributions"])
                            for condition in artifact.result["conditions"]
                            for item in condition["source_contributions_by_interval"]
                        ),
                        "condition_count": artifact.result["condition_count"],
                        "per_step_source_accounting_comparisons": artifact.result[
                            "per_step_source_accounting_comparisons"
                        ],
                        "per_step_A_H_additivity_comparisons": artifact.result[
                            "per_step_A_H_additivity_comparisons"
                        ],
                        "target_summary": artifact.result["target_summary"],
                    }
                )
            else:
                raise BoundedSensoryScale128Error("unknown Phase 7M command.")
            output.setdefault("phase7l_full_replay_seconds", round(context_elapsed, 3))
        output["elapsed_seconds_this_command"] = round(time.perf_counter() - started, 3)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (
        BoundedSensoryScale128Error,
        BoundedSensoryScale128ArtifactError,
        ValueError,
        OSError,
    ) as exc:
        print(f"Phase 7M validation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
