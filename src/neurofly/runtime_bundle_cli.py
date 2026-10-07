"""Offline scientific runtime release commands."""

import argparse
import json
import subprocess
import time
from pathlib import Path

from neurofly import runtime_bundle as bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["build", "verify", "provision", "verify-release"]
    )
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expected-manifest-id")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    if args.command == "build":
        if args.output is None:
            parser.error("build requires --output")
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=args.root, text=True
        ).strip()
        archive, manifest, wrapper = bundle.build(
            args.root, args.inventory, args.output, commit
        )
        result = {"archive": str(archive), "manifest": str(manifest)}
        if args.manifest:
            args.manifest.write_bytes(bundle.canonical(wrapper) + b"\n")
    else:
        if not args.expected_manifest_id:
            parser.error(
                "verification requires an externally pinned --expected-manifest-id"
            )
        if args.command == "verify-release":
            wrapper = bundle.verify_release(
                args.root, args.expected_manifest_id, args.inventory
            )
        else:
            if args.archive is None or args.manifest is None:
                parser.error("archive verification requires --archive and --manifest")
            wrapper = bundle.manifest(
                args.manifest, args.expected_manifest_id, args.inventory
            )
            if args.command == "provision":
                if args.destination is None:
                    parser.error("provision requires --destination")
                bundle.provision(
                    args.archive,
                    args.manifest,
                    args.expected_manifest_id,
                    args.inventory,
                    args.destination,
                )
            else:
                bundle.verify_archive(args.archive, wrapper)
                if args.destination:
                    bundle.check_files(args.destination, wrapper["manifest"]["files"])
        result = {"status": "VERIFIED"}
    result.update(
        {
            "manifest_id": wrapper["manifest_id"],
            "archive_sha256": wrapper["manifest"]["archive_sha256"],
            "seconds": time.perf_counter() - started,
        }
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
