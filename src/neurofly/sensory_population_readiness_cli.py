"""Prepare, inspect, or replay the Phase 7N all-311 dry-run artifacts."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Sequence

from neurofly.bounded_sensory_scale128 import (
    CANONICAL_PLAN128_ID,
    scale128_artifact_path,
)
from neurofly.bounded_sensory_scale128_artifacts import load_scale128_artifact
from neurofly.sensory_population_readiness import (
    SensoryPopulationReadinessError,
    build_execution_dry_run,
    build_full_coverage_plan,
    build_full_population_plan,
    export_readiness_artifact,
    load_phase7n_sources,
    load_readiness_artifact,
    replay_full_coverage_plan,
)


def _load_baseline_inputs():
    plan = load_scale128_artifact(
        scale128_artifact_path("plan", CANONICAL_PLAN128_ID), "plan"
    )
    return plan


def _compute_bundle():
    started = time.perf_counter()
    source, circuit, grid = load_phase7n_sources()
    phase_timings = {"source_load_validation": round(time.perf_counter() - started, 3)}
    phase7m_plan = _load_baseline_inputs()
    phase_started = time.perf_counter()
    population_config, population_result = build_full_population_plan(
        source, circuit, grid
    )
    population_saved = export_readiness_artifact(
        "population", population_config, population_result
    )
    phase_timings["population_plan_build_and_persist"] = round(
        time.perf_counter() - phase_started, 3
    )
    population = population_saved.as_input()

    phase_started = time.perf_counter()
    coverage_config, coverage_result = build_full_coverage_plan(
        population, phase7m_plan, source, circuit, grid
    )
    coverage_saved = export_readiness_artifact(
        "coverage", coverage_config, coverage_result
    )
    phase_timings["coverage_plan_build_and_persist"] = round(
        time.perf_counter() - phase_started, 3
    )
    coverage = coverage_saved.as_input()

    phase_started = time.perf_counter()
    execution_config, execution_result = build_execution_dry_run(
        population, coverage, source, circuit
    )
    execution_saved = export_readiness_artifact(
        "execution", execution_config, execution_result
    )
    phase_timings["execution_manifest_build_and_persist"] = round(
        time.perf_counter() - phase_started, 3
    )
    phase_timings["all_including_persist"] = round(time.perf_counter() - started, 3)
    return {
        "population": population_saved,
        "coverage": coverage_saved,
        "execution": execution_saved,
        "phase_timings_seconds": phase_timings,
    }


def _replay(population_path: Path, coverage_path: Path, execution_path: Path):
    started = time.perf_counter()
    phase_timings = {}
    phase_started = time.perf_counter()
    source, circuit, grid = load_phase7n_sources()
    phase_timings["source_load_validation"] = round(
        time.perf_counter() - phase_started, 3
    )
    population = load_readiness_artifact(population_path, "population")
    coverage = load_readiness_artifact(coverage_path, "coverage")
    execution = load_readiness_artifact(execution_path, "execution")
    phase_started = time.perf_counter()
    expected_population = build_full_population_plan(source, circuit, grid)
    if (population.config, population.result) != expected_population:
        raise SensoryPopulationReadinessError(
            "full-population plan failed deterministic source replay."
        )
    phase_timings["population_plan_replay"] = round(
        time.perf_counter() - phase_started, 3
    )
    phase_started = time.perf_counter()
    expected_coverage = replay_full_coverage_plan(
        population.as_input(), coverage.as_input(), source, circuit, grid
    )
    if (coverage.config, coverage.result) != expected_coverage:
        raise SensoryPopulationReadinessError(
            "full-population anatomy-only coverage plan failed replay."
        )
    phase_timings["coverage_plan_replay"] = round(
        time.perf_counter() - phase_started, 3
    )
    phase_started = time.perf_counter()
    expected_execution = build_execution_dry_run(
        population.as_input(), coverage.as_input(), source, circuit
    )
    if (execution.config, execution.result) != expected_execution:
        raise SensoryPopulationReadinessError(
            "all-311 execution manifest failed deterministic replay."
        )
    phase_timings["execution_manifest_replay"] = round(
        time.perf_counter() - phase_started, 3
    )
    phase_timings["all_replay"] = round(time.perf_counter() - started, 3)
    return {
        "population": population.summary(),
        "coverage": coverage.summary(),
        "execution": execution.summary(),
        "replay_identity_match": True,
        "dynamics_executed": False,
        "elapsed_seconds": phase_timings["all_replay"],
        "phase_timings_seconds": phase_timings,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "prepare", help="generate and persist all three dry-run artifacts"
    )
    for name in ("replay", "validate"):
        command = commands.add_parser(
            name, help="recompute and verify the dry-run chain"
        )
        command.add_argument("population", type=Path)
        command.add_argument("coverage", type=Path)
        command.add_argument("execution", type=Path)
    inspect = commands.add_parser("inspect", help="inspect one immutable artifact")
    inspect.add_argument("kind", choices=("population", "coverage", "execution"))
    inspect.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect":
            artifact = load_readiness_artifact(args.artifact, args.kind)
            output = artifact.summary()
        elif args.command in {"replay", "validate"}:
            output = _replay(args.population, args.coverage, args.execution)
        else:
            bundle = _compute_bundle()
            output = {
                "population": bundle["population"].summary(),
                "coverage": bundle["coverage"].summary(),
                "execution": bundle["execution"].summary(),
                "phase_timings_seconds": bundle["phase_timings_seconds"],
                "dynamics_executed": False,
            }
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (
        SensoryPopulationReadinessError,
        OSError,
        ValueError,
    ) as exc:
        print(f"Phase 7N dry-run failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
