"""Generate, inspect, or replay the offline motor-neuron target contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from neurofly.motor_neuron_muscle_contract import (
    DEFAULT_OUTPUT_ROOT,
    MotorNeuronMuscleContractError,
    generate_motor_neuron_muscle_target_artifact,
    load_motor_neuron_muscle_target_artifact,
    replay_motor_neuron_muscle_target_artifact,
)
from neurofly.psi_dlmn_event_relay import DEFAULT_MOTOR_CONTRACT_PATH


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate")
    generate.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    generate.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("artifact", type=Path)
    replay = commands.add_parser("replay")
    replay.add_argument("artifact", type=Path)
    replay.add_argument(
        "--motor-contract", type=Path, default=DEFAULT_MOTOR_CONTRACT_PATH
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            artifact = generate_motor_neuron_muscle_target_artifact(
                motor_contract_path=args.motor_contract,
                output_root=args.output_root,
            )
            operation = "generated-or-existing-full-replay-verified"
        elif args.command == "replay":
            artifact = replay_motor_neuron_muscle_target_artifact(
                args.artifact,
                motor_contract_path=args.motor_contract,
            )
            operation = "offline-source-replay-verified"
        else:
            artifact = load_motor_neuron_muscle_target_artifact(args.artifact)
            operation = "artifact-integrity-verified"
        output = artifact.summary()
        output["operation"] = operation
        if args.command == "inspect":
            output["target_associations"] = artifact.contract["target_associations"]
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, MotorNeuronMuscleContractError) as exc:
        print(f"motor-neuron muscle contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
