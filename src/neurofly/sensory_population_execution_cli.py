"""Generate, inspect, and replay the Phase 7O all-311 offline experiment."""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path
from typing import Sequence

from neurofly.relative_column_assignment import canonical_json_bytes
from neurofly.sensory_population_execution import (
    SensoryPopulationExecutionError,
    execute_311,
)
from neurofly.sensory_population_execution_artifacts import (
    DEFAULT_ROOT,
    SensoryPopulationExecutionArtifactError,
    export_execution_artifact,
    load_execution_artifact,
)
from neurofly.sensory_population_readiness import (
    DEFAULT_COVERAGE_ROOT,
    DEFAULT_EXECUTION_ROOT,
    DEFAULT_POPULATION_ROOT,
    load_phase7n_sources,
    load_readiness_artifact,
)

POPULATION_ID = "0db2b29f168039e23858db9831e345cc25fdec8c06775e2f23a7d8d681544356"
COVERAGE_ID = "0331ff3d309892ac5284e0da3898683df7b5fb8fd06055090b6100dcea4a6e56"
EXECUTION_ID = "a7d828993674634875b8b8862d40083690e77bb8aa748ad7079135cc8e10725f"


def _rss_kib() -> int:
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def _inputs():
    started = time.perf_counter()
    source, circuit, grid = load_phase7n_sources()
    population = load_readiness_artifact(
        DEFAULT_POPULATION_ROOT / POPULATION_ID, "population"
    )
    coverage = load_readiness_artifact(DEFAULT_COVERAGE_ROOT / COVERAGE_ID, "coverage")
    execution = load_readiness_artifact(
        DEFAULT_EXECUTION_ROOT / EXECUTION_ID, "execution"
    )
    if (population.artifact_id, coverage.artifact_id, execution.artifact_id) != (
        POPULATION_ID,
        COVERAGE_ID,
        EXECUTION_ID,
    ):
        raise SensoryPopulationExecutionError(
            "Phase 7N canonical planning identities changed"
        )
    return (
        population,
        coverage,
        execution,
        source,
        circuit,
        grid,
    ), time.perf_counter() - started


def _generate() -> dict[str, object]:
    started = time.perf_counter()
    baseline_rss = _rss_kib()
    inputs, load_seconds = _inputs()
    config, result, timings = execute_311(*inputs)
    persist_started = time.perf_counter()
    saved = export_execution_artifact(config, result)
    persist_seconds = time.perf_counter() - persist_started
    metrics = {
        "measurement_method": (
            "time.perf_counter; Linux /proc/self/status VmRSS baseline; "
            "resource.ru_maxrss peak (KiB)"
        ),
        "population_config_load_seconds": load_seconds,
        **timings,
        "serialization_write_and_integrity_load_seconds": persist_seconds,
        "total_generation_seconds": time.perf_counter() - started,
        "baseline_rss_kib": baseline_rss,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "artifact_bytes": saved.summary()["bytes_including_manifest"],
    }
    metrics["delta_peak_rss_kib"] = metrics["peak_rss_kib"] - baseline_rss
    metrics_path = DEFAULT_ROOT / f"{saved.artifact_id}.generation_metrics.json"
    metrics_path.write_bytes(canonical_json_bytes(metrics) + b"\n")
    return {
        "artifact": saved.summary(),
        "performance": metrics,
        "performance_path": str(metrics_path),
    }


def _replay(path: Path) -> dict[str, object]:
    started = time.perf_counter()
    artifact = load_execution_artifact(path)
    inputs, load_seconds = _inputs()
    config, result, timings = execute_311(*inputs)
    if (artifact.config, artifact.result) != (config, result):
        raise SensoryPopulationExecutionError(
            "Phase 7O full replay differs from stored result"
        )
    replayed = export_execution_artifact(config, result)
    if replayed.artifact_id != artifact.artifact_id:
        raise SensoryPopulationExecutionError(
            "Phase 7O replay artifact identity changed"
        )
    return {
        "artifact": artifact.summary(),
        "replay_identity_match": True,
        "config_and_result_equal": True,
        "source_load_seconds": load_seconds,
        "compute_timings_seconds": timings,
        "full_replay_seconds": time.perf_counter() - started,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("generate")
    for command in ("inspect", "replay"):
        commands.add_parser(command).add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            output = _generate()
        elif args.command == "inspect":
            output = load_execution_artifact(args.artifact).summary()
        else:
            output = _replay(args.artifact)
        print(json.dumps(output, sort_keys=True, indent=2))
        return 0
    except (
        SensoryPopulationExecutionError,
        SensoryPopulationExecutionArtifactError,
        OSError,
        ValueError,
    ) as exc:
        print(f"Phase 7O execution failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
