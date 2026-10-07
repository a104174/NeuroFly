"""Deployment byte authority and extraction attack regressions."""

import copy
import io
import json
import tarfile
from pathlib import Path

import pytest

from neurofly import runtime_bundle as bundle
from neurofly.runtime_readiness import startup_readiness

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/deployment_runtime_inventory_v2.json"
COMMIT = "f7baa1db24d2ff6c993894d4edafc33d736a58cd"


@pytest.fixture(scope="module")
def release(tmp_path_factory):
    root = tmp_path_factory.mktemp("bundle")
    return bundle.build(ROOT, INVENTORY, root, COMMIT)


def test_exact_inventory_and_repeat_determinism(release, tmp_path):
    archive, path, wrapper = release
    other, metadata, repeated = bundle.build(ROOT, INVENTORY, tmp_path, COMMIT)
    assert archive.read_bytes() == other.read_bytes()
    assert path.read_bytes() == metadata.read_bytes()
    assert wrapper == repeated
    assert wrapper["manifest"]["file_count"] == 74
    assert wrapper["manifest"]["uncompressed_bytes"] == 116239303
    with tarfile.open(archive) as tar:
        assert [e.name for e in tar] == [
            r["repository_relative_path"]
            for r in bundle.inventory(INVENTORY)["runtime_files"]
        ]


def test_manifest_pin_and_inventory_mutation(release, tmp_path):
    _, path, wrapper = release
    for field in ("inventory_id", "archive_sha256", "content_id", "file_count"):
        altered = copy.deepcopy(wrapper)
        altered["manifest"][field] = "invalid"
        altered["manifest_id"] = bundle.identity(altered["manifest"])
        target = tmp_path / "manifest.json"
        target.write_bytes(bundle.canonical(altered))
        with pytest.raises(ValueError):
            bundle.manifest(target, wrapper["manifest_id"], INVENTORY)
    modified = json.loads(INVENTORY.read_bytes())
    modified["inventory"]["runtime_files"][0]["bytes"] += 1
    modified["inventory_id"] = bundle.identity(modified["inventory"])
    target = tmp_path / "inventory.json"
    target.write_bytes(bundle.canonical(modified))
    with pytest.raises(ValueError):
        bundle.inventory(target)


def test_corrupted_archive_rejected(release, tmp_path):
    archive, _, wrapper = release
    bad = tmp_path / "bad.tar.gz"
    bad.write_bytes(archive.read_bytes()[:-1] + b"!")
    with pytest.raises(ValueError):
        bundle.verify_archive(bad, wrapper)


@pytest.mark.parametrize(
    "attack",
    [
        "traversal",
        "absolute",
        "duplicate",
        "symlink",
        "hardlink",
        "device",
        "extra",
        "missing",
        "file_mutation",
        "trailing",
    ],
)
def test_rehashed_unsafe_archives_rejected(attack, tmp_path):
    data = b"frozen"
    row = {
        "repository_relative_path": "data/a.json",
        "bytes": len(data),
        "sha256": __import__("hashlib").sha256(data).hexdigest(),
    }
    path = tmp_path / "unsafe.tar.gz"
    with tarfile.open(path, "w:gz", format=tarfile.USTAR_FORMAT) as tar:
        names = {
            "traversal": ["data/../escape"],
            "absolute": ["/data/a.json"],
            "duplicate": ["data/a.json", "data/a.json"],
            "extra": ["data/a.json", "data/extra"],
            "missing": [],
        }.get(attack, ["data/a.json"])
        for name in names:
            entry = tarfile.TarInfo(name)
            entry.mode = 0o444
            entry.size = len(data)
            if attack in ("symlink", "hardlink", "device"):
                entry.type = {
                    "symlink": tarfile.SYMTYPE,
                    "hardlink": tarfile.LNKTYPE,
                    "device": tarfile.CHRTYPE,
                }[attack]
                entry.linkname = "../../escape"
                entry.size = 0
            tar.addfile(
                entry, io.BytesIO(b"mutate" if attack == "file_mutation" else data)
            )
    if attack == "trailing":
        import gzip

        with path.open("ab") as stream:
            stream.write(gzip.compress(b"hidden content"))
    wrapper = {
        "manifest": {
            "files": [row],
            "file_count": 1,
            "archive_sha256": bundle.file_hash(path),
            "compressed_bytes": path.stat().st_size,
        }
    }
    with pytest.raises((ValueError, tarfile.TarError, OSError)):
        bundle.verify_archive(path, wrapper)


def test_provision_exact_read_only_and_failed_release(release, tmp_path):
    archive, path, wrapper = release
    destination = tmp_path / "release"
    bundle.provision(archive, path, wrapper["manifest_id"], INVENTORY, destination)
    bundle.check_files(destination, wrapper["manifest"]["files"])
    for row in wrapper["manifest"]["files"]:
        target = destination / row["repository_relative_path"]
        assert target.stat().st_mode & 0o222 == 0
    with pytest.raises(ValueError):
        bundle.provision(archive, path, wrapper["manifest_id"], INVENTORY, destination)
    target = destination / wrapper["manifest"]["files"][0]["repository_relative_path"]
    target.chmod(0o644)
    target.write_bytes(b"mutated")
    with pytest.raises(ValueError):
        bundle.check_files(destination, wrapper["manifest"]["files"])


def test_readiness_local_and_incomplete_fail_closed(monkeypatch):
    monkeypatch.setenv("NEUROFLY_RUNTIME_MODE", "local")
    assert startup_readiness()["status"] == "LOCAL_UNVERIFIED"
    monkeypatch.setenv("NEUROFLY_RUNTIME_MODE", "provisioned")
    monkeypatch.delenv("NEUROFLY_RUNTIME_RELEASE_ROOT", raising=False)
    assert startup_readiness()["ready"] is False


def test_liveness_and_blocked_provisioned_playback():
    from fastapi.testclient import TestClient

    from neurofly.http_api import create_app

    with TestClient(
        create_app(
            ROOT / "data/derived/experiments",
            runtime_readiness={
                "mode": "provisioned",
                "ready": False,
                "status": "RUNTIME_NOT_VERIFIED",
            },
        )
    ) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 503
        assert (
            client.get("/api/v1/scenarios/BASELINE_CONTROL/playback").status_code == 503
        )


@pytest.mark.parametrize(
    "fault", ["none", "missing", "hash", "inventory", "manifest", "root"]
)
def test_startup_readiness_integrity(release, tmp_path, monkeypatch, fault):
    import shutil

    archive, path, wrapper = release
    root = tmp_path / "release"
    bundle.provision(archive, path, wrapper["manifest_id"], INVENTORY, root)
    for row in wrapper["manifest"]["tracked_build_dependencies"]["science_documents"]:
        target = root / row["repository_relative_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / row["repository_relative_path"], target)
    shutil.copyfile(INVENTORY, root / "docs/deployment_runtime_inventory_v2.json")
    monkeypatch.chdir(root)
    for key, value in {
        "NEUROFLY_RUNTIME_MODE": "provisioned",
        "NEUROFLY_RUNTIME_RELEASE_ROOT": str(root),
        "NEUROFLY_RUNTIME_INVENTORY_ID": bundle.INVENTORY_ID,
        "NEUROFLY_RUNTIME_MANIFEST_ID": wrapper["manifest_id"],
        "NEUROFLY_EXPERIMENT_ARTIFACT_ROOT": str(root / "data/derived/experiments"),
        "NEUROFLY_CIRCUIT_CONTRACT_ROOT": str(
            root / "data/derived/malecns/looming_giant_fiber_v1"
        ),
    }.items():
        monkeypatch.setenv(key, value)
    for key in (
        "NEUROFLY_SCENARIO_ARTIFACT_PATH",
        "NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT",
        "NEUROFLY_MOTOR_EXPERIMENT_ARTIFACT_ROOT",
    ):
        monkeypatch.delenv(key, raising=False)
    target = root / wrapper["manifest"]["files"][0]["repository_relative_path"]
    if fault == "missing":
        target.parent.chmod(0o755)
        target.unlink()
    elif fault == "hash":
        target.chmod(0o644)
        target.write_bytes(b"corrupt")
    elif fault in ("inventory", "manifest"):
        monkeypatch.setenv(f"NEUROFLY_RUNTIME_{fault.upper()}_ID", "0" * 64)
    elif fault == "root":
        monkeypatch.setenv(
            "NEUROFLY_EXPERIMENT_ARTIFACT_ROOT", str(ROOT / "data/derived/experiments")
        )
    state = startup_readiness()
    assert state["ready"] is (fault == "none")
    assert str(root) not in json.dumps(state)


def test_manifest_committed_release_identity(release):
    _, _, wrapper = release
    stored = json.loads(
        (ROOT / "docs/neurofly_runtime_bundle_manifest_v1.json").read_bytes()
    )
    assert stored == wrapper


def test_extraction_destination_cannot_contain_links(release, tmp_path):
    archive, _, wrapper = release
    destination = tmp_path / "destination"
    destination.mkdir()
    (destination / "data").symlink_to(ROOT / "data", target_is_directory=True)
    with pytest.raises(ValueError):
        bundle.verify_archive(archive, wrapper, destination)


def test_build_rejects_missing_input_and_extra_directories(release, tmp_path):
    archive, path, wrapper = release
    root = tmp_path / "release"
    bundle.provision(archive, path, wrapper["manifest_id"], INVENTORY, root)
    (root / "data").chmod(0o755)
    (root / "data/unauthorized").mkdir()
    with pytest.raises(ValueError):
        bundle.check_files(root, wrapper["manifest"]["files"])
    target = root / wrapper["manifest"]["files"][0]["repository_relative_path"]
    target.parent.chmod(0o755)
    target.unlink()
    with pytest.raises(ValueError):
        bundle.build(root, INVENTORY, tmp_path / "output", COMMIT)
