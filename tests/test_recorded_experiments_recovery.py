"""Authentic Phase 3B data gate and isolated, fail-closed collection recovery.

Requires the explicit, pinned local source and D2.2 data. Missing data is a clear
failure, never a skip or a generated replacement. Negative cases copy the source
into pytest temporary directories and never touch the original.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from neurofly import runtime_bundle as bundle
from neurofly.experiment_api import ArtifactPathError, ArtifactStoreError
from neurofly.experiment_artifacts import (
    ArtifactIntegrityError,
    load_experiment_artifact,
)
from neurofly.http_api import create_app
from neurofly.recorded_experiments_runtime import (
    INVENTORY_PATH,
    REFERENCE_ARTIFACT_ID,
    REFERENCE_DIRECTORY,
    REQUIRED_ARTIFACT_IDS,
    build_candidate,
    provision_candidate,
    reference,
)

ROOT = Path(__file__).resolve().parents[1]
RESULT_ID = "8af5a3f50f0cd9fee65ce62e5421c873e95a48e32333de475545c1be7f133b45"
BASELINE = "a5aeea83722ea7fc8aa011b0d1e73065b99881c2"


@pytest.fixture(scope="module")
def authentic_source():
    try:
        return reference(ROOT, replay=True)[0]
    except (OSError, ValueError, RuntimeError) as exc:
        pytest.fail(f"Required authentic Phase 3B integration data unavailable: {exc}")


@pytest.fixture
def collection(tmp_path, authentic_source):
    root = tmp_path / "recorded"
    path = root / REFERENCE_DIRECTORY
    shutil.copytree(authentic_source, path)
    return root, path


def fingerprints(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


def test_real_reference_list_detail_timeline_and_no_mutation(collection, tmp_path):
    root, _ = collection
    # Adjacent legacy families and audit data are outside the dedicated root.
    for family in (
        "dnp15_exploratory_yaw_artifact_v1",
        "phase21_dataset_audit",
        "phase22_metadata_audit",
        "hs_dnp15_neural_validation_artifact_v1",
    ):
        (tmp_path / "legacy" / family).mkdir(parents=True)
    before = fingerprints(root)
    app = create_app(root, required_artifact_ids=REQUIRED_ARTIFACT_IDS)
    with TestClient(app) as client:
        listing = client.get("/api/v1/experiments")
        assert listing.status_code == 200
        assert listing.json()["count"] == 1
        summary = listing.json()["experiments"][0]
        assert summary["artifact_id"] == REFERENCE_ARTIFACT_ID
        assert summary["experiment_config_sha256"] == REFERENCE_DIRECTORY
        assert summary["experiment_config_id"] == "ui_smoke_phase2f_reference_v1"
        assert summary["result_id"] == RESULT_ID
        assert summary["duration_ms"] == 80.0
        assert summary["validation_status"] == "NOT_EVALUATED"
        assert (
            client.get(f"/api/v1/experiments/{REFERENCE_ARTIFACT_ID}").json() == summary
        )
        timeline = client.get(f"/api/v1/experiments/{REFERENCE_ARTIFACT_ID}/timeline")
        assert timeline.status_code == 200
        assert len(timeline.json()["times_ms"]) == 801
    assert fingerprints(root) == before


@pytest.mark.parametrize("fault", ["bytes", "missing", "extra", "manifest", "family"])
def test_invalid_phase3b_is_not_hidden(collection, fault):
    root, path = collection
    if fault == "bytes":
        with (path / "telemetry.json").open("ab") as f:
            f.write(b" ")
    elif fault == "missing":
        (path / "spikes.jsonl").unlink()
    elif fault == "extra":
        (path / "unrelated.txt").write_text("test-only extra file")
    elif fault == "manifest":
        (path / "manifest.json").write_text("{}")
    else:
        (root / "dnp15_exploratory_yaw_artifact_v1").mkdir()
    with TestClient(create_app(root, required_artifact_ids=REQUIRED_ARTIFACT_IDS)) as c:
        r = c.get("/api/v1/experiments")
        assert r.status_code == 409
        assert r.json()["code"] == "artifact_integrity_failure"
        assert str(path) not in r.text


def test_rehashed_config_mutation_remains_rejected(collection):
    _, path = collection
    p = path / "manifest.json"
    m = json.loads(p.read_bytes())
    m["config"]["duration_ms"] = 10.0
    m.pop("manifest_sha256")
    m["manifest_sha256"] = bundle.identity(m)
    p.write_bytes(bundle.canonical(m) + b"\n")
    with pytest.raises(ArtifactIntegrityError, match="config SHA-256"):
        load_experiment_artifact(path)


def test_required_empty_and_missing_are_distinct(tmp_path):
    empty = tmp_path / "intentionally-empty"
    empty.mkdir()
    with TestClient(create_app(empty)) as c:
        assert c.get("/api/v1/experiments").json()["count"] == 0
    with TestClient(
        create_app(empty, required_artifact_ids=REQUIRED_ARTIFACT_IDS)
    ) as c:
        r = c.get("/api/v1/experiments")
        assert r.status_code == 500
        assert r.json()["code"] == "artifact_store_error"
    with pytest.raises(ArtifactStoreError, match="not a directory"):
        create_app(tmp_path / "required-root-missing")


@pytest.mark.parametrize("fault", ["root-link", "payload-link", "fifo", "duplicate"])
def test_path_and_duplicate_policies(collection, tmp_path, fault):
    root, path = collection
    if fault == "root-link":
        link = tmp_path / "linked"
        link.symlink_to(root, target_is_directory=True)
        with pytest.raises(ArtifactPathError, match="symlink artifact root"):
            create_app(link)
        return
    if fault == "payload-link":
        p = path / "summary.json"
        p.unlink()
        p.symlink_to(tmp_path / "outside.json")
    elif fault == "fifo":
        p = path / "summary.json"
        p.unlink()
        os.mkfifo(p)
    else:
        shutil.copytree(path, root / "duplicate")
    with TestClient(create_app(root)) as c:
        r = c.get("/api/v1/experiments")
        assert r.status_code == (500 if fault == "duplicate" else 409)
        assert r.json()["code"] == (
            "artifact_store_error" if fault == "duplicate" else "unsafe_artifact_path"
        )


def test_deleting_required_run_after_startup_is_not_empty_success(collection):
    root, path = collection
    app = create_app(root, required_artifact_ids=REQUIRED_ARTIFACT_IDS)
    with TestClient(app) as c:
        assert c.get("/api/v1/experiments").status_code == 200
        shutil.rmtree(path)
        assert c.get("/api/v1/experiments").status_code == 500


def test_unverified_provisioned_runtime_does_not_serve_records(collection):
    root, _ = collection
    app = create_app(root, runtime_readiness={"mode": "provisioned", "ready": False})
    with TestClient(app) as c:
        assert c.get("/ready").status_code == 503
        assert c.get("/api/v1/experiments").status_code == 500


@pytest.fixture(scope="module")
def candidate(tmp_path_factory, authentic_source):
    return build_candidate(
        ROOT, tmp_path_factory.mktemp("recorded-candidate"), BASELINE
    )


def test_versioned_bundle_keeps_all_74_original_rows(candidate, tmp_path):
    archive, metadata, wrapper = candidate
    again, meta2, other = build_candidate(ROOT, tmp_path, BASELINE)
    assert archive.read_bytes() == again.read_bytes()
    assert metadata.read_bytes() == meta2.read_bytes()
    assert wrapper == other
    with pytest.raises(ValueError, match="content-addressed manifest conflict"):
        build_candidate(ROOT, tmp_path, "0" * 40)
    assert metadata.read_bytes() == meta2.read_bytes()
    assert wrapper["manifest"]["file_count"] == 79
    assert wrapper["manifest"]["inventory_id"] == bundle.RECORDED_INVENTORY_ID
    old = bundle.inventory(ROOT / "docs/deployment_runtime_inventory_v2.json")
    rows = {r["repository_relative_path"]: r for r in wrapper["manifest"]["files"]}
    for row in old["runtime_files"]:
        assert rows[row["repository_relative_path"]] == {
            k: row[k]
            for k in ("repository_relative_path", "bytes", "sha256", "category")
        }
    bundle.verify_archive(archive, wrapper)
    with pytest.raises(ValueError):
        bundle.manifest(
            metadata,
            wrapper["manifest_id"],
            ROOT / "docs/deployment_runtime_inventory_v2.json",
        )


def test_missing_authentic_data_has_no_generated_replacement(tmp_path):
    for name in (INVENTORY_PATH, "docs/recorded_experiments_reference_v1.json"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    with pytest.raises(ValueError, match="authentic Phase 3B source is missing"):
        reference(tmp_path, replay=True)


def test_clean_provisioned_api_and_five_canonical_replays(candidate, tmp_path):
    archive, metadata, wrapper = candidate
    container = tmp_path / "native"
    release = container / ".neurofly-release"
    provision_candidate(ROOT, archive, metadata, wrapper["manifest_id"], release)
    shutil.copytree(
        ROOT / "tools",
        container / "tools",
        ignore=shutil.ignore_patterns("__pycache__", "node_modules"),
    )
    script = r"""
import hashlib, json, os, sys
from pathlib import Path
container = Path.cwd()
sys.path.insert(0, str(container))
for name in tuple(os.environ):
    if name.startswith("NEUROFLY_"): os.environ.pop(name)
from tools.vercel_runtime_entrypoint import application
assert 'neurofly' not in sys.modules
app=application(container, manifest_id=sys.argv[1], inventory_id=(
    '75294376accee5f52261a8cdf922638e7cc17e2aa34963364d1f9b27e6fe4d46'))
root = Path.cwd()
from neurofly.http_api import create_app_from_env
import neurofly
assert Path(neurofly.__file__).is_relative_to(root)
from neurofly.recorded_experiments_runtime import COLLECTION_ROOT, REFERENCE_ARTIFACT_ID
from neurofly.experiment_artifacts import replay_experiment_artifact
from neurofly.malecns.contract import load_circuit_contract
from fastapi.testclient import TestClient
with TestClient(app) as c:
    assert c.get('/ready').json()['status'] == 'VERIFIED'
    r=c.get('/api/v1/experiments'); assert r.status_code == 200
    assert r.json()['count'] == 1
    assert r.json()['experiments'][0]['artifact_id'] == REFERENCE_ARTIFACT_ID
    assert c.get('/api/v1/experiments/'+REFERENCE_ARTIFACT_ID).status_code == 200
    hashes = {
      'BASELINE_CONTROL':'75d1f2856f0d896589a8b1f62fb61016d701045b760e216b7cb5fa70daa30668',
      'LOOMING_CIRCUIT_VALIDATION':'c3387396dcffa6372287df1a7d4680bb7ba605df319af4cf10f140cfc3a4d223',
      'LOOMING_WORLD_EXPERIMENT':'d06ef32aaf054b981464948916e5687951b40f571be5286513dad8ae440f26df',
      'HORIZONTAL_MOTION_NEURAL_VALIDATION':'52554962f3e9c85c6866b5e3ec56f8a12d24340db2236ec52c7809c6ece8d404',
      'EXPLORATORY_COURSE_CONTROL':'7fddc1109495023d8f64744237796d5d8e86852abef80b6979f1994088d46806'}
    for name, digest in hashes.items():
        r=c.get('/api/v1/scenarios/'+name+'/playback'); assert r.status_code == 200
        raw=json.dumps(r.json(),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        assert hashlib.sha256(raw).hexdigest() == digest
    run=next((root / COLLECTION_ROOT).iterdir())
    contract=load_circuit_contract(root/'data/derived/malecns/looming_giant_fiber_v1')
    result=replay_experiment_artifact(run,contract)
    assert result.result_sha256 == (
        '8af5a3f50f0cd9fee65ce62e5421c873e95a48e32333de475545c1be7f133b45')
    # Required collection files removed: readiness and API fail, no false empty list.
    run.chmod(0o755); (run/'summary.json').unlink()
    with TestClient(create_app_from_env()) as broken:
        assert broken.get('/ready').status_code == 503
        assert broken.get('/api/v1/experiments').status_code == 500
print('isolated v3 API, reference replay and five canonical hashes verified')
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script, wrapper["manifest_id"]],
        cwd=container,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_existing_native_family_validators_stay_authoritative():
    from neurofly.dnp15_exploratory_yaw_artifacts import replay_yaw_artifact
    from neurofly.exploratory_course_control_artifacts import (
        replay_closed_loop_artifact,
    )
    from neurofly.hs_dnp15_neural_validation_artifacts import replay_neural_artifact

    for family, replay in (
        ("dnp15_exploratory_yaw_artifact_v1", replay_yaw_artifact),
        ("hs_dnp15_neural_validation_artifact_v1", replay_neural_artifact),
        (
            "exploratory_course_control_closed_loop_artifact_v1",
            replay_closed_loop_artifact,
        ),
    ):
        root = ROOT / "data/derived/experiments" / family
        before = fingerprints(root)
        replay(next(root.iterdir()))
        assert fingerprints(root) == before
