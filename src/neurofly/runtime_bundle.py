"""Byte-only deployment packaging. No scientific execution or network access."""

import gzip
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

INVENTORY_ID = "cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b"
SCHEMA = "neurofly_runtime_bundle_manifest_v1"
RELEASE = ".neurofly-runtime-release.json"


def canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_path(value):
    path = PurePosixPath(value)
    if (
        not isinstance(value, str)
        or path.is_absolute()
        or "\\" in value
        or ".." in path.parts
        or str(path) != value
        or not value.startswith("data/")
    ):
        raise ValueError("unsafe runtime path")
    return value


def inventory(path):
    envelope = json.loads(Path(path).read_bytes())
    value = envelope["inventory"]
    if (
        envelope["schema"] != "neurofly_deployment_runtime_inventory_v2"
        or envelope["inventory_id"] != INVENTORY_ID
        or identity(value) != INVENTORY_ID
    ):
        raise ValueError("frozen inventory mismatch")
    return value


def check_files(root, rows, *, exact=True):
    root = Path(root).resolve()
    paths = [safe_path(row["repository_relative_path"]) for row in rows]
    if paths != sorted(set(paths)):
        raise ValueError("duplicate/unordered runtime paths")
    for row, name in zip(rows, paths, strict=True):
        path = root / name
        if (
            not path.is_file()
            or path.is_symlink()
            or not path.resolve().is_relative_to(root)
            or any(parent.is_symlink() for parent in path.parents if parent != root)
            or path.stat().st_size != row["bytes"]
            or file_hash(path) != row["sha256"]
        ):
            raise ValueError("runtime file integrity failure")
    if exact:
        actual = {
            str(p.relative_to(root))
            for p in (root / "data").rglob("*")
            if (p.is_file() or p.is_symlink())
            and not str(p.relative_to(root)).startswith("data/reference/")
        }
        if actual != set(paths):
            raise ValueError("unexpected/missing runtime file")
        allowed_directories = {
            str(parent) for name in paths for parent in PurePosixPath(name).parents
        }
        for path in (root / "data").rglob("*"):
            name = str(path.relative_to(root))
            if path.is_dir() and not name.startswith("data/reference"):
                if name not in allowed_directories:
                    raise ValueError("unexpected runtime directory")


def build(root, inventory_path, output, source_commit):
    value = inventory(inventory_path)
    rows = value["runtime_files"]
    check_files(root, rows, exact=False)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output) as temporary:
        archive = Path(temporary) / "bundle.tar.gz"
        with archive.open("wb") as stream:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=stream, mtime=0, compresslevel=9
            ) as compressed:
                with tarfile.open(
                    fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT
                ) as tar:
                    for row in rows:
                        name = row["repository_relative_path"]
                        entry = tarfile.TarInfo(name)
                        entry.size = row["bytes"]
                        entry.mode = 0o444
                        with (Path(root) / name).open("rb") as source:
                            tar.addfile(entry, source)
        archive_sha = file_hash(archive)
        contents = [
            {
                k: row[k]
                for k in ("repository_relative_path", "bytes", "sha256", "category")
            }
            for row in rows
        ]
        manifest = {
            "schema": SCHEMA,
            "inventory_id": INVENTORY_ID,
            "source_git_commit": source_commit,
            "bundle_format": "ustar+gzip",
            "creation_format_version": "ustar-gzip-mtime0-level9-v1",
            "content_id": identity(contents),
            "archive_sha256": archive_sha,
            "compressed_bytes": archive.stat().st_size,
            "uncompressed_bytes": value["total_bytes"],
            "file_count": value["file_count"],
            "files": contents,
            "required_roots": [
                "data/derived/experiments",
                "data/derived/malecns",
                "data/raw/malecns",
            ],
            "tracked_build_dependencies": value["tracked_build_dependencies"],
            "verification_policy": (
                "pinned manifest; archive and every file SHA256; "
                "exact entry set; regular files only; offline"
            ),
        }
        wrapper = {
            "schema": SCHEMA,
            "manifest_id": identity(manifest),
            "manifest": manifest,
        }
        verify_archive(archive, wrapper)
        target = output / f"neurofly-runtime-v2-{archive_sha}.tar.gz"
        if target.exists() and file_hash(target) != archive_sha:
            raise ValueError("content-addressed output conflict")
        if not target.exists():
            shutil.copyfile(archive, target)
        manifest_path = output / f"{target.name}.manifest.json"
        manifest_path.write_bytes(canonical(wrapper) + b"\n")
    return target, manifest_path, wrapper


def manifest(path, expected_id, inventory_path):
    wrapper = json.loads(Path(path).read_bytes())
    value = wrapper["manifest"]
    source = inventory(inventory_path)
    expected_files = [
        {k: row[k] for k in ("repository_relative_path", "bytes", "sha256", "category")}
        for row in source["runtime_files"]
    ]
    if (
        wrapper["schema"] != SCHEMA
        or value["schema"] != SCHEMA
        or wrapper["manifest_id"] != expected_id
        or identity(value) != expected_id
        or value["inventory_id"] != INVENTORY_ID
        or value["files"] != expected_files
        or value["content_id"] != identity(expected_files)
        or value["file_count"] != source["file_count"]
        or value["uncompressed_bytes"] != source["total_bytes"]
        or value["tracked_build_dependencies"] != source["tracked_build_dependencies"]
        or value["bundle_format"] != "ustar+gzip"
    ):
        raise ValueError("bundle manifest authority mismatch")
    return wrapper


def verify_archive(archive, wrapper, destination=None):
    if destination is not None:
        root = Path(destination)
        if root.is_symlink() or not root.is_dir() or any(root.iterdir()):
            raise ValueError("extraction requires an empty controlled directory")
    value = wrapper["manifest"]
    if (
        Path(archive).stat().st_size != value["compressed_bytes"]
        or file_hash(archive) != value["archive_sha256"]
    ):
        raise ValueError("archive integrity failure")
    seen = []
    rows = value["files"]
    canonical_tar = hashlib.sha256()
    tar_bytes = 0
    with tarfile.open(archive, "r|gz") as tar:
        for entry in tar:
            name = safe_path(entry.name)
            index = len(seen)
            if (
                index >= len(rows)
                or name != rows[index]["repository_relative_path"]
                or not entry.isreg()
                or entry.pax_headers
                or entry.linkname
                or entry.size != rows[index]["bytes"]
                or entry.uid != 0
                or entry.gid != 0
                or entry.mtime != 0
                or entry.mode != 0o444
                or entry.uname
                or entry.gname
            ):
                raise ValueError("unsafe/unauthorized archive entry")
            seen.append(name)
            canonical_tar.update(entry.tobuf(format=tarfile.USTAR_FORMAT))
            tar_bytes += 512 + ((entry.size + 511) // 512) * 512
            digest = hashlib.sha256()
            count = 0
            source = tar.extractfile(entry)
            target = None
            try:
                if destination is not None:
                    path = Path(destination) / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    target = path.open("xb")
                with source:
                    while block := source.read(1024 * 1024):
                        count += len(block)
                        digest.update(block)
                        canonical_tar.update(block)
                        if target:
                            target.write(block)
            finally:
                if target:
                    target.close()
            if (
                count != rows[index]["bytes"]
                or digest.hexdigest() != rows[index]["sha256"]
            ):
                raise ValueError("archive file integrity failure")
            canonical_tar.update(bytes((-entry.size) % 512))
    if len(seen) != value["file_count"]:
        raise ValueError("archive entry count mismatch")
    # Tar readers alone ignore appended content after EOF: validate all bytes.
    canonical_tar.update(bytes(1024 + (-(tar_bytes + 1024)) % tarfile.RECORDSIZE))
    with gzip.open(archive, "rb") as stream:
        if hashlib.file_digest(stream, "sha256").digest() != canonical_tar.digest():
            raise ValueError("noncanonical/trailing archive content")


def provision(archive, manifest_path, expected_id, inventory_path, destination):
    wrapper = manifest(manifest_path, expected_id, inventory_path)
    destination = Path(destination)
    if destination.exists():
        raise ValueError("provisioning requires a nonexistent clean destination")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        root = Path(temporary) / "release"
        root.mkdir()
        verify_archive(archive, wrapper, root)
        check_files(root, wrapper["manifest"]["files"])
        (root / RELEASE).write_bytes(canonical(wrapper) + b"\n")
        for path in sorted((root / "data").rglob("*"), reverse=True):
            path.chmod(0o555 if path.is_dir() else 0o444)
        (root / "data").chmod(0o555)
        os.rename(root, destination)
    return wrapper


def verify_release(root, expected_id, inventory_path):
    root = Path(root).resolve()
    wrapper = manifest(root / RELEASE, expected_id, inventory_path)
    check_files(root, wrapper["manifest"]["files"])
    for row in wrapper["manifest"]["tracked_build_dependencies"]["science_documents"]:
        path = root / row["repository_relative_path"]
        if (
            path.is_symlink()
            or not path.resolve().is_relative_to(root)
            or path.stat().st_size != row["bytes"]
            or file_hash(path) != row["sha256"]
        ):
            raise ValueError("tracked authority integrity failure")
    return wrapper
