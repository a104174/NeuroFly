"""Explicit deployment-data closure; no model/artifact generation."""

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import runtime_dependency_closure as closure

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/deployment_runtime_inventory_v2.json"


@pytest.fixture(scope="module")
def inventory():
    return closure.load_inventory(INVENTORY)


def test_frozen_d1_and_version_relationship(inventory):
    raw = (ROOT / closure.D1_PATH).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == closure.D1_BYTES_ID
    assert closure.digest(json.loads(raw)) == closure.D1_ID
    assert inventory["source_d1_inventory_id"] == closure.D1_ID
    assert inventory["source_git_commit"] == (
        "735015182ac6f5abac1b7fc90cecc642b474ae3c"
    )
    assert "D1 remains" in inventory["closure_policy"]["version_relationship"]


def test_exact_files_totals_categories_and_authorization(inventory):
    rows = inventory["runtime_files"]
    assert len(rows) == inventory["file_count"] == 74
    assert sum(r["bytes"] for r in rows) == inventory["total_bytes"] == 116239303
    closure.verify_files(ROOT, rows)
    paths = [r["repository_relative_path"] for r in rows]
    assert paths == sorted(set(paths))
    ignored = subprocess.check_output(
        ["git", "check-ignore", "--stdin"],
        input="\n".join(paths) + "\n",
        text=True,
        cwd=ROOT,
    ).splitlines()
    assert ignored == paths
    for row in rows:
        assert row["category"] in closure.CATEGORIES
        assert row["required_by"] and row["inclusion_reason"]
        assert row["ignored_by_git"]
    for category, totals in inventory["category_totals"].items():
        subset = [r for r in rows if r["category"] == category]
        assert totals == {
            "files": len(subset),
            "bytes": sum(r["bytes"] for r in subset),
        }
    assert not inventory["minimality_review"]["unused_inherited_d1_files"]


def test_phase16_gap_history_and_canonical_metadata(inventory):
    d1 = json.loads((ROOT / closure.D1_PATH).read_bytes())
    d1_paths = {r["path"] for r in d1["runtime_files"]}
    rows = {r["repository_relative_path"]: r for r in inventory["runtime_files"]}
    for path, (size, digest) in closure.SUPPLEMENT.items():
        assert path not in d1_paths and path in rows
        assert rows[path]["bytes"] == size and rows[path]["sha256"] == digest
        assert rows[path]["required_by"] == ["REPLAY_16_CORRECTED"]
    from neurofly.dnp01_subthreshold_diagnostic_artifacts import _manifest
    from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

    path = ROOT / closure.PHASE16
    raw = (path / "diagnostic.json").read_bytes()
    result = json.loads(raw)
    assert raw == canonical_json_bytes(result, newline=True)
    assert json.loads((path / "manifest.json").read_bytes()) == _manifest(result)
    assert closure.digest(result["config"]) == result["config_sha256"]
    assert closure.digest(result["result"]) == result["result_sha256"]
    assert result["artifact_id"] == path.name


def test_raw_xlsx_and_git_delivered_documents(inventory):
    rows = inventory["runtime_files"]
    raw = [r for r in rows if r["repository_relative_path"].startswith("data/raw/")]
    assert len(raw) == 1 and raw[0]["bytes"] == 111565
    assert raw[0]["category"] == "SOURCE_VALIDATION_DEPENDENCY"
    for doc in inventory["tracked_build_dependencies"]["science_documents"]:
        file = ROOT / doc["repository_relative_path"]
        assert hashlib.sha256(file.read_bytes()).hexdigest() == doc["sha256"]
        assert len(file.read_bytes()) == doc["bytes"]
        assert doc["repository_relative_path"] not in {
            r["repository_relative_path"] for r in rows
        }


@pytest.mark.parametrize(
    "field",
    [
        "repository_relative_path",
        "sha256",
        "bytes",
        "category",
        "required_by",
        "inclusion_reason",
    ],
)
def test_semantic_mutations_change_identity(inventory, field):
    changed = copy.deepcopy(inventory)
    row = changed["runtime_files"][0]
    row[field] = row[field] + 1 if field == "bytes" else "mutated semantic field"
    assert closure.digest(changed) != closure.digest(inventory)
    assert closure.digest(dict(reversed(list(inventory.items())))) == (
        closure.digest(inventory)
    )


@pytest.mark.parametrize(
    "path",
    [
        "/tmp/data/file",
        "data/../file",
        "data//file",
        "data/./file",
        "data\\file",
        "src/neurofly/file",
    ],
)
def test_unsafe_paths_rejected(path):
    with pytest.raises(ValueError):
        closure.safe_path(path)


def sample(root):
    file = root / "data/raw/sample"
    file.parent.mkdir(parents=True)
    file.write_bytes(b"explicit authorized bytes")
    return [
        {
            "path": "data/raw/sample",
            "bytes": file.stat().st_size,
            "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
        }
    ]


def test_missing_mutated_extra_and_duplicate_rejected(tmp_path):
    rows = sample(tmp_path)
    closure.verify_files(tmp_path, rows, exact=True)
    with pytest.raises(ValueError, match="duplicate"):
        closure.verify_files(tmp_path, rows * 2)
    with pytest.raises(ValueError, match="extra/missing"):
        closure.verify_files(tmp_path, [], exact=True)
    (tmp_path / rows[0]["path"]).write_bytes(b"mutated")
    with pytest.raises(ValueError, match="byte/hash"):
        closure.verify_files(tmp_path, rows)
    (tmp_path / rows[0]["path"]).unlink()
    with pytest.raises(FileNotFoundError):
        closure.verify_files(tmp_path, rows)


def test_runtime_symlinks_rejected(tmp_path):
    rows = sample(tmp_path)
    file = tmp_path / rows[0]["path"]
    other = tmp_path / "original"
    file.rename(other)
    file.symlink_to(other)
    with pytest.raises(ValueError, match="symlink"):
        closure.verify_files(tmp_path, rows)


def test_rehashed_missing_gate_dependency_cannot_be_complete(inventory):
    row_paths = {r["repository_relative_path"] for r in inventory["runtime_files"]}
    assert closure.PHASE16 + "/diagnostic.json" in row_paths
    assert inventory["closure_validation"]["isolated_validation"] == "PASS"
    assert len(inventory["closure_validation"]["gates"]) == 14
    assert all(g["status"] == "PASS" for g in inventory["closure_validation"]["gates"])


def test_full_isolated_runtime_closure(inventory):
    result = subprocess.run(
        [
            sys.executable,
            "tools/runtime_dependency_closure.py",
            "isolated",
            "--inventory",
            str(INVENTORY),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(result.stdout)
    assert report["network_access"] == "DENIED"
    assert report["unauthorized_runtime_reads"] == []
    assert report["discovered_outside_candidate"] == []
    assert all(g["status"] == "PASS" for g in report["gates"])
    assert {g["gate"] for g in report["gates"]} == set(inventory["required_gate_ids"])
    for row in inventory["runtime_files"]:
        assert (
            report["runtime_reads"][row["repository_relative_path"]]
            == row["required_by"]
        )
