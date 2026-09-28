"""Offline inspection/replay and explicit live refresh for motor source pins."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from neurofly.motor_neural_contract import (
    DEFAULT_ARTIFACT_ROOT,
    MotorNeuralContractError,
    load_pinned_artifact,
    pin_official_source,
    refresh_source,
)


def _summary(artifact: dict) -> dict:
    contract = artifact["contract"]
    counts: dict[str, int] = {}
    for row in contract["nodes"]:
        counts[row["type"]] = counts.get(row["type"], 0) + 1
    groups: dict[str, int] = {}
    for edge in contract["chemical_edges"]:
        query_id = edge["source_query_id"]
        groups[query_id] = groups.get(query_id, 0) + 1
    return {
        "status": "VALID",
        "schema_version": contract["schema_version"],
        "contract_id": contract["contract_id"],
        "query_response_sha256": contract["source_provenance"]["query_response_sha256"],
        "annotation_source_sha256": contract["source_provenance"][
            "annotation_source_sha256"
        ],
        "node_count": len(contract["nodes"]),
        "node_type_counts": counts,
        "chemical_edge_count": len(contract["chemical_edges"]),
        "edges_by_query": groups,
        "direct_dnp01_to_candidate_dlmn_edge_count": contract[
            "direct_dnp01_to_candidate_dlmn_audit"
        ]["returned_edge_count"],
        "no_dynamics": contract["scope"]["no_dynamics"],
        "path": str(artifact["path"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Pin or verify the no-dynamics MaleCNS motor structural contract. "
            "Only the explicit pin/refresh commands access the network."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    pin = subparsers.add_parser(
        "pin", help="query official sources and pin exact match"
    )
    pin.add_argument("--output-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    for name in ("inspect", "replay", "refresh"):
        command = subparsers.add_parser(
            name,
            help=(
                "inspect contract"
                if name == "inspect"
                else "offline deterministic validation"
                if name == "replay"
                else "live source comparison; never overwrites the pin"
            ),
        )
        command.add_argument("artifact", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "pin":
            path = pin_official_source(args.output_root)
            result = _summary(load_pinned_artifact(path))
            result["operation"] = "PINNED_OR_ALREADY_PRESENT"
        elif args.command == "refresh":
            result = refresh_source(args.artifact)
        else:
            artifact = load_pinned_artifact(args.artifact)
            result = _summary(artifact)
            result["operation"] = (
                "OFFLINE_REPLAY_OK" if args.command == "replay" else "INSPECT_OK"
            )
            if args.command == "inspect":
                result["nodes"] = artifact["contract"]["nodes"]
                result["chemical_edges"] = artifact["contract"]["chemical_edges"]
                result["literature_pathway_evidence"] = artifact["contract"][
                    "literature_pathway_evidence"
                ]
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.command == "refresh" and result["status"] != "MATCH":
            return 2
        return 0
    except (MotorNeuralContractError, OSError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
