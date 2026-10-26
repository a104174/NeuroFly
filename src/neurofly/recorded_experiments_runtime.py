"""Local-only v3 packaging of an existing Phase 3B engineering reference.

No scientific output is generated. The cloud v2 retrieval and Production policy
remain in tools/vercel_runtime_build.py. All candidate outputs require an explicit
external destination; the original data directories are only read.
"""

import json
import shutil
import tempfile
from pathlib import Path

from neurofly import runtime_bundle as bundle

COLLECTION_ROOT = "data/derived/recorded_experiments_v1"
REFERENCE_DIRECTORY = "4481c8c202c06c5d45ce8808beec28f4e9fadb2f4ae29f39c1301a8f1aaedcf1"
REFERENCE_ARTIFACT_ID = (
    "63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656"
)
REQUIRED_ARTIFACT_IDS = (REFERENCE_ARTIFACT_ID,)
INVENTORY_PATH = "docs/deployment_runtime_inventory_v3.json"
REFERENCE_PATH = "docs/recorded_experiments_reference_v1.json"


def reference(root, *, replay=False):
    """Verify explicit local dependencies; never create a substitute fixture."""
    from neurofly.experiment_artifacts import (
        load_experiment_artifact,
        replay_experiment_artifact,
    )
    from neurofly.malecns.contract import load_circuit_contract

    root = Path(root).resolve()
    inventory = bundle.inventory(root / INVENTORY_PATH)
    row = next(
        r
        for r in inventory["tracked_build_dependencies"]["science_documents"]
        if r["repository_relative_path"] == REFERENCE_PATH
    )
    document = root / REFERENCE_PATH
    if document.is_symlink() or bundle.file_hash(document) != row["sha256"]:
        raise ValueError("recorded reference authority mismatch")
    spec = json.loads(document.read_bytes())
    source = root / spec["source_directory"]
    for path in (source, *source.parents):
        if path == root:
            break
        if path.is_symlink():
            raise ValueError("symlink recorded source is prohibited")
    if not source.is_dir():
        raise ValueError("required authentic Phase 3B source is missing")
    for row in spec["files"]:
        p = source / row["filename"]
        if (
            p.is_symlink()
            or not p.is_file()
            or p.stat().st_size != row["bytes"]
            or bundle.file_hash(p) != row["sha256"]
        ):
            raise ValueError("authentic Phase 3B source bytes differ")
    artifact = load_experiment_artifact(source)
    actual = artifact.inspection_dict()
    for key in (
        "artifact_id",
        "config_sha256",
        "result_sha256",
        "experiment_id",
        "duration_ms",
        "validation_status",
    ):
        if actual[key] != spec[key]:
            raise ValueError("recorded reference identity mismatch")
    if replay:
        replay_experiment_artifact(
            source,
            load_circuit_contract(root / "data/derived/malecns/looming_giant_fiber_v1"),
        )
    return source, spec


def build_candidate(root, output, source_commit):
    """Use the existing deterministic tar/manifest verifier for 74+5 files."""
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.is_relative_to(root):
        raise ValueError("candidate destination must be outside the source checkout")
    inventory_path = root / INVENTORY_PATH
    inventory = bundle.inventory(inventory_path)
    reference(root, replay=True)
    parent = bundle.inventory(root / "docs/deployment_runtime_inventory_v2.json")
    bundle.check_files(root, parent["runtime_files"], exact=False)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="recorded-input-", dir=output) as tmp:
        stage = Path(tmp)
        for row in inventory["runtime_files"]:
            name = row["repository_relative_path"]
            original = root / bundle.safe_path(
                row.get("source_repository_relative_path", name)
            )
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
        return bundle.build(stage, inventory_path, output, source_commit)


def provision_candidate(root, archive, manifest_path, expected_id, destination):
    """Assemble an isolated native application, with no editable-install reads."""
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if destination.is_relative_to(root):
        raise ValueError("candidate destination must be outside the source checkout")
    inventory_path = root / INVENTORY_PATH
    wrapper = bundle.manifest(manifest_path, expected_id, inventory_path)
    if wrapper["manifest"]["inventory_id"] != bundle.RECORDED_INVENTORY_ID:
        raise ValueError("recorded provisioning requires the v3 inventory")
    bundle.provision(archive, manifest_path, expected_id, inventory_path, destination)
    for row in wrapper["manifest"]["tracked_build_dependencies"]["science_documents"]:
        name = row["repository_relative_path"]
        source, target = root / name, destination / name
        if (
            source.is_symlink()
            or bundle.file_hash(source) != row["sha256"]
            or source.stat().st_size != row["bytes"]
        ):
            raise ValueError("tracked authority changed before assembly")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o444)
    target = destination / INVENTORY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inventory_path, target)
    target.chmod(0o444)
    for name in ("src/neurofly", "data/reference"):
        if name == "data/reference":
            (destination / "data").chmod(0o755)
        try:
            shutil.copytree(
                root / name,
                destination / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        finally:
            if name == "data/reference":
                (destination / "data").chmod(0o555)
        for path in (destination / name).rglob("*"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        (destination / name).chmod(0o555)
    bundle.verify_release(destination, expected_id, destination / INVENTORY_PATH)
    return wrapper


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    archive, manifest_path, wrapper = build_candidate(
        args.source_root, args.output, args.source_commit
    )
    print(
        json.dumps(
            {
                "archive": str(archive),
                "manifest": str(manifest_path),
                "manifest_id": wrapper["manifest_id"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
