"""Generate, inspect, and replay the offline Phase 8O TTMn target dispatch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.model_derived_ttmn_target_dispatch import (
    DEFAULT_TARGET_CONTRACT_PATH,
    ModelDerivedTTMnDispatchError,
)
from neurofly.model_derived_ttmn_target_dispatch_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_PHASE8N_ARTIFACT,
    ModelDerivedTTMnTargetArtifactError,
    generate_model_derived_ttmn_target_artifact,
    load_model_derived_ttmn_target_artifact,
    replay_model_derived_ttmn_target_artifact,
)
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    DEFAULT_SOURCE_ARTIFACT as DEFAULT_PHASE8B_SOURCE_ARTIFACT,
)


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--source-ttmn-artifact", type=Path, default=DEFAULT_PHASE8N_ARTIFACT
    )
    parser.add_argument(
        "--source-phase8b-artifact", type=Path, default=DEFAULT_PHASE8B_SOURCE_ARTIFACT
    )
    parser.add_argument(
        "--target-contract", type=Path, default=DEFAULT_TARGET_CONTRACT_PATH
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    _add_source_arguments(generate)
    generate.add_argument("--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    for name in ("inspect", "replay"):
        command = commands.add_parser(name)
        command.add_argument("artifact", type=Path)
        if name == "replay":
            _add_source_arguments(command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_model_derived_ttmn_target_artifact(
                source_ttmn_artifact=args.source_ttmn_artifact,
                source_phase8b_artifact=args.source_phase8b_artifact,
                target_contract_path=args.target_contract,
                output_root=args.output_root,
            )
            operation = "generated-or-existing-8n-8k-full-replay-verified"
        elif args.command == "replay":
            artifact = replay_model_derived_ttmn_target_artifact(
                args.artifact,
                source_ttmn_artifact=args.source_ttmn_artifact,
                source_phase8b_artifact=args.source_phase8b_artifact,
                target_contract_path=args.target_contract,
            )
            operation = "phase8n-and-phase8k-source-replay-verified"
        else:
            artifact = load_model_derived_ttmn_target_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        summary = artifact.summary()
        summary["operation"] = operation
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (
        OSError,
        ValueError,
        ModelDerivedTTMnDispatchError,
        ModelDerivedTTMnTargetArtifactError,
    ) as exc:
        print(f"Phase 8O target-dispatch error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
