"""Build-only private release retrieval; all byte validation belongs to D2."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

MANIFEST_ID = "e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882"
ARCHIVE_SHA = "12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5"
STORE_ID = "store_S3zkyGCIjHi3p79M"
PATHNAME = f"neurofly/runtime/v2/{ARCHIVE_SHA}/neurofly-runtime-v2-{ARCHIVE_SHA}.tar.gz"


def retrieve(archive):
    if not os.environ.get("VERCEL_OIDC_TOKEN"):
        raise ValueError("build OIDC authentication is required")
    if os.environ.get("BLOB_STORE_ID") != STORE_ID:
        raise ValueError("build store metadata does not match the pinned store")
    if os.environ.get("BLOB_READ_WRITE_TOKEN"):
        raise ValueError("static Blob credentials are prohibited")
    result = subprocess.run(
        [
            "npx",
            "--yes",
            "vercel@62.7.0",
            "blob",
            "get",
            PATHNAME,
            "--access",
            "private",
            "--output",
            str(archive),
            "--non-interactive",
        ],
        capture_output=True,
        timeout=180,
        check=False,
    )
    if result.returncode:
        # Provider error output can contain URLs; never forward it to build logs.
        raise RuntimeError("pinned private release retrieval failed")


def build(root):
    from neurofly import runtime_bundle as bundle

    root = Path(root).resolve()
    inventory = root / "docs/deployment_runtime_inventory_v2.json"
    manifest = root / "docs/neurofly_runtime_bundle_manifest_v1.json"
    wrapper = bundle.manifest(manifest, MANIFEST_ID, inventory)
    if (
        wrapper["manifest"]["archive_sha256"] != ARCHIVE_SHA
        or wrapper["manifest"]["compressed_bytes"] != 3674299
    ):
        raise ValueError("pinned release identity mismatch")
    release = root / ".neurofly-release"
    if release.exists():
        raise ValueError("build requires a fresh release destination")
    with tempfile.TemporaryDirectory(prefix="neurofly-build-") as temporary:
        archive = Path(temporary) / "runtime.tar.gz"
        retrieve(archive)
        bundle.provision(archive, manifest, MANIFEST_ID, inventory, release)
    for row in wrapper["manifest"]["tracked_build_dependencies"]["science_documents"]:
        name = row["repository_relative_path"]
        target = release / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
        target.chmod(0o444)
    target = release / "docs/deployment_runtime_inventory_v2.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inventory, target)
    target.chmod(0o444)
    bundle.verify_release(release, MANIFEST_ID, target)
    # Preserve the existing isolated D2 application layout. Module-relative
    # authority paths then resolve inside this release, independent of _vendor.
    for name in ("src/neurofly", "data/reference"):
        source = root / name
        if not source.is_dir():
            raise ValueError("tracked application dependency is missing")
        # D2 has already sealed data/. Open only its parent during assembly,
        # then restore the same read-only mode before the build can succeed.
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
    print(f"D3 RELEASE VERIFIED {MANIFEST_ID} {ARCHIVE_SHA} 3674299 bytes")


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
