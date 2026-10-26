"""Provision the pinned scientific runtime shipped with the Git source tree."""

import json
import os
import re
import shutil
import stat
from pathlib import Path

MANIFEST_ID = "4634950e8375b1d6adeb258c17e2c58a22059f9bee48663fc9fae56de68be194"
ARCHIVE_SHA = "c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf"
RUNTIME_INVENTORY_ID = (
    "75294376accee5f52261a8cdf922638e7cc17e2aa34963364d1f9b27e6fe4d46"
)
COMPRESSED_BYTES = 3795667
INVENTORY_PATH = "docs/deployment_runtime_inventory_v3.json"
MANIFEST_PATH = "docs/neurofly_runtime_bundle_manifest_v3.json"
ARCHIVE_PATH = (
    "runtime-distributions/v3/"
    "neurofly-runtime-v3-c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf.tar.gz"
)


def _source_file(root, relative_path):
    path = root / relative_path
    if path.is_symlink() or any(
        parent.is_symlink() for parent in path.parents if parent != root
    ):
        raise ValueError("runtime source path must not contain symlinks")
    if not path.resolve().is_relative_to(root):
        raise ValueError("runtime source path escapes the repository")
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        raise FileNotFoundError(
            f"required Git source file is missing: {relative_path}"
        ) from None
    if not stat.S_ISREG(mode):
        raise ValueError("runtime source must be a regular file")
    return path


def build(root):
    from neurofly import runtime_bundle as bundle

    root = Path(root).resolve()
    application_commit = os.environ.get("VERCEL_GIT_COMMIT_SHA", "")
    if not re.fullmatch(r"[a-f0-9]{40}", application_commit):
        raise ValueError("Vercel Git commit SHA is required for the runtime build")

    inventory = _source_file(root, INVENTORY_PATH)
    manifest = _source_file(root, MANIFEST_PATH)
    archive = _source_file(root, ARCHIVE_PATH)
    wrapper = bundle.manifest(manifest, MANIFEST_ID, inventory)
    if (
        wrapper["manifest"]["archive_sha256"] != ARCHIVE_SHA
        or wrapper["manifest"]["compressed_bytes"] != COMPRESSED_BYTES
        or wrapper["manifest"]["inventory_id"] != RUNTIME_INVENTORY_ID
    ):
        raise ValueError("pinned runtime v3 identity mismatch")
    if archive.stat().st_size != COMPRESSED_BYTES:
        raise ValueError("pinned runtime v3 archive size mismatch")

    release = root / ".neurofly-release"
    if release.exists():
        raise ValueError("build requires a fresh release destination")
    bundle.provision(archive, manifest, MANIFEST_ID, inventory, release)
    for row in wrapper["manifest"]["tracked_build_dependencies"]["science_documents"]:
        name = row["repository_relative_path"]
        source = _source_file(root, name)
        target = release / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o444)
    target = release / INVENTORY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inventory, target)
    target.chmod(0o444)
    bundle.verify_release(release, MANIFEST_ID, target)

    # Keep the established isolated application layout; runtime imports and
    # authority documents resolve only inside this verified release.
    for name in ("src/neurofly", "data/reference"):
        source = root / name
        if not source.is_dir() or source.is_symlink():
            raise ValueError("tracked application dependency is missing")
        if name == "data/reference":
            (release / "data").chmod(0o755)
        try:
            shutil.copytree(
                source,
                release / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        finally:
            if name == "data/reference":
                (release / "data").chmod(0o555)
        for path in (release / name).rglob("*"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        (release / name).chmod(0o555)

    print(
        "NEUROFLY RUNTIME VERIFIED "
        + json.dumps(
            {
                "application_commit_sha": application_commit,
                "data_source_commit_sha": wrapper["manifest"]["source_git_commit"],
                "manifest_id": MANIFEST_ID,
                "inventory_id": RUNTIME_INVENTORY_ID,
                "archive_sha256": ARCHIVE_SHA,
                "compressed_bytes": COMPRESSED_BYTES,
                "file_count": wrapper["manifest"]["file_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
