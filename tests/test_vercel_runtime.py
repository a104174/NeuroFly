"""D3 build authentication, pinned provisioning, and runtime wiring."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from neurofly import runtime_bundle as bundle
from tools import vercel_runtime_build as build
from tools.vercel_runtime_entrypoint import application

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def preview_environment(monkeypatch):
    monkeypatch.setenv("VERCEL_ENV", "preview")


@pytest.mark.parametrize("environment", [None, "production", "development"])
def test_only_preview_can_retrieve(monkeypatch, tmp_path, environment):
    monkeypatch.setenv("VERCEL_OIDC_TOKEN", "synthetic-test-only")
    if environment is None:
        monkeypatch.delenv("VERCEL_ENV")
    else:
        monkeypatch.setenv("VERCEL_ENV", environment)
    monkeypatch.setattr(build.subprocess, "run", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(ValueError, match="Preview build environment is required"):
        build.retrieve(tmp_path / "archive")


@pytest.fixture
def build_root(tmp_path):
    source = ROOT / "docs/neurofly_runtime_bundle_manifest_v1.json"
    wrapper = bundle.manifest(
        source, build.MANIFEST_ID, ROOT / "docs/deployment_runtime_inventory_v2.json"
    )
    names = [
        "docs/neurofly_runtime_bundle_manifest_v1.json",
        "docs/deployment_runtime_inventory_v2.json",
    ] + [
        row["repository_relative_path"]
        for row in wrapper["manifest"]["tracked_build_dependencies"][
            "science_documents"
        ]
    ]
    for name in names:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    for name in ("src/neurofly", "data/reference"):
        shutil.copytree(ROOT / name, tmp_path / name)
    return tmp_path


@pytest.mark.parametrize("missing", ["VERCEL_OIDC_TOKEN", "BLOB_STORE_ID"])
def test_missing_build_auth_fails_before_retrieval(monkeypatch, tmp_path, missing):
    monkeypatch.setenv("VERCEL_OIDC_TOKEN", "test-only")
    monkeypatch.setenv("BLOB_STORE_ID", build.STORE_ID)
    monkeypatch.delenv(missing)
    monkeypatch.setattr(build.subprocess, "run", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(ValueError):
        build.retrieve(tmp_path / "archive")


@pytest.mark.parametrize("static", [False, True])
def test_wrong_store_or_static_auth_rejected(monkeypatch, tmp_path, static):
    monkeypatch.setenv("VERCEL_OIDC_TOKEN", "test-only")
    monkeypatch.setenv("BLOB_STORE_ID", build.STORE_ID if static else "wrong")
    if static:
        monkeypatch.setenv("BLOB_READ_WRITE_TOKEN", "test-only")
    monkeypatch.setattr(build.subprocess, "run", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(ValueError):
        build.retrieve(tmp_path / "archive")


def test_retrieval_failure_has_no_local_fallback(monkeypatch, build_root):
    def unavailable(_):
        raise RuntimeError("unavailable")

    monkeypatch.setattr(build, "retrieve", unavailable)
    monkeypatch.setattr(bundle, "provision", lambda *a: pytest.fail("extraction"))
    with pytest.raises(RuntimeError):
        build.build(build_root)
    assert not (build_root / ".neurofly-release").exists()


def test_sdk_subprocess_uses_pins_without_credentials_in_arguments(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("VERCEL_OIDC_TOKEN", "synthetic-test-only")
    monkeypatch.setenv("BLOB_STORE_ID", build.STORE_ID)
    monkeypatch.delenv("BLOB_READ_WRITE_TOKEN", raising=False)

    def child(args, **kwargs):
        assert args == [
            "node",
            str(ROOT / "tools/vercel_blob/retrieve.mjs"),
            str(tmp_path / "runtime.tar.gz"),
            build.PATHNAME,
            build.STORE_ID,
        ]
        assert "synthetic-test-only" not in args
        assert "env" not in kwargs and "cwd" not in kwargs
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(build.subprocess, "run", child)
    build.retrieve(tmp_path / "runtime.tar.gz")


@pytest.mark.parametrize("category", sorted(build.FAILURE_CATEGORIES))
def test_only_finite_child_failure_protocol_is_exposed(monkeypatch, tmp_path, category):
    monkeypatch.setenv("VERCEL_OIDC_TOKEN", "synthetic-test-only")
    monkeypatch.setenv("BLOB_STORE_ID", build.STORE_ID)
    monkeypatch.delenv("BLOB_READ_WRITE_TOKEN", raising=False)
    monkeypatch.setattr(
        build.subprocess,
        "run",
        lambda args, **kw: subprocess.CompletedProcess(
            args, 1, b"", f"NEUROFLY_BLOB_FAILURE {category}\n".encode()
        ),
    )
    with pytest.raises(RuntimeError, match=f"^{category}$"):
        build.retrieve(tmp_path / "runtime.tar.gz")


@pytest.mark.parametrize(
    "returncode,stdout,stderr",
    [
        (
            1,
            b"synthetic-private-output",
            b"NEUROFLY_BLOB_FAILURE BLOB_ACCESS_REJECTED\n",
        ),
        (1, b"", b"NEUROFLY_BLOB_FAILURE BLOB_ACCESS_REJECTED\nsynthetic-private-url"),
        (1, b"", b"NEUROFLY_BLOB_FAILURE UNRECOGNIZED\n"),
        (0, b"synthetic-private-output", b""),
        (2, b"", b"synthetic-private-url"),
    ],
)
def test_uncontrolled_child_output_is_never_forwarded(
    monkeypatch, tmp_path, capsys, returncode, stdout, stderr
):
    monkeypatch.setenv("VERCEL_OIDC_TOKEN", "synthetic-test-only")
    monkeypatch.setenv("BLOB_STORE_ID", build.STORE_ID)
    monkeypatch.delenv("BLOB_READ_WRITE_TOKEN", raising=False)
    monkeypatch.setattr(
        build.subprocess,
        "run",
        lambda args, **kw: subprocess.CompletedProcess(
            args, returncode, stdout, stderr
        ),
    )
    with pytest.raises(RuntimeError, match="^UNKNOWN_REDACTED_FAILURE$"):
        build.retrieve(tmp_path / "runtime.tar.gz")
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize(
    "error,category",
    [
        (FileNotFoundError("synthetic-private-error"), "SDK_DEPENDENCY_MISSING"),
        (
            subprocess.TimeoutExpired("synthetic-private-command", 180),
            "DOWNLOAD_TIMEOUT",
        ),
        (OSError("synthetic-private-error"), "UNKNOWN_REDACTED_FAILURE"),
    ],
)
def test_spawn_exceptions_are_sanitized(monkeypatch, tmp_path, error, category):
    monkeypatch.setenv("VERCEL_OIDC_TOKEN", "synthetic-test-only")
    monkeypatch.setenv("BLOB_STORE_ID", build.STORE_ID)
    monkeypatch.delenv("BLOB_READ_WRITE_TOKEN", raising=False)

    def failed(*args, **kwargs):
        raise error

    monkeypatch.setattr(build.subprocess, "run", failed)
    with pytest.raises(RuntimeError, match=f"^{category}$") as caught:
        build.retrieve(tmp_path / "runtime.tar.gz")
    assert caught.value.__suppress_context__


@pytest.mark.parametrize("same_size", [False, True])
def test_wrong_archive_bytes_or_hash_rejected(monkeypatch, build_root, same_size):
    monkeypatch.setattr(
        build,
        "retrieve",
        lambda path: path.write_bytes(bytes(3674299 if same_size else 1)),
    )
    with pytest.raises(ValueError, match="archive integrity failure"):
        build.build(build_root)
    assert not (build_root / ".neurofly-release").exists()


def test_pinned_build_and_runtime_readiness(monkeypatch, build_root, tmp_path):
    monkeypatch.setattr(sys, "path", sys.path.copy())
    # Reuse D2's deterministic fixture builder only for test input, never deployment.
    archive, _, _ = bundle.build(
        ROOT,
        ROOT / "docs/deployment_runtime_inventory_v2.json",
        tmp_path / "fixture",
        "f7baa1db24d2ff6c993894d4edafc33d736a58cd",
    )
    monkeypatch.setattr(build, "retrieve", lambda path: shutil.copyfile(archive, path))
    build.build(build_root)
    # A fresh process cannot use the editable checkout or installed neurofly.
    # This exercises the same module-relative paths as the native bundle.
    native = tmp_path / "native"
    native.mkdir()
    shutil.copytree(build_root / ".neurofly-release", native / ".neurofly-release")
    shutil.copytree(
        ROOT / "tools",
        native / "tools",
        ignore=shutil.ignore_patterns("__pycache__", "node_modules"),
    )
    script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from tools.vercel_runtime_entrypoint import application
assert 'neurofly' not in sys.modules
app = application(Path.cwd())
from neurofly import hs_dnp15_neural_validation as neural
from neurofly import looming_world_experiment as looming
from neurofly import orientation_to_horizontal_motion as orientation
from neurofly import dnp15_exploratory_yaw as yaw
from neurofly import exploratory_course_control as course
root = Path.cwd()
assert neural.SCIENCE_ROOT == root / 'docs/science'
assert (neural.SCIENCE_ROOT / 'hs_dnp15_network_context_audit.json').is_file()
neural.load_preregistration()
looming.load_preregistration()
orientation.load_contract()
yaw.load_preregistration()
course.load_preregistration()
from fastapi.testclient import TestClient
with TestClient(app) as client:
    assert client.get('/ready').status_code == 200
    for scenario in ['BASELINE_CONTROL', 'LOOMING_CIRCUIT_VALIDATION',
                     'LOOMING_WORLD_EXPERIMENT', 'HORIZONTAL_MOTION_NEURAL_VALIDATION',
                     'EXPLORATORY_COURSE_CONTROL']:
        response = client.get('/api/v1/scenarios/' + scenario + '/playback')
        assert response.status_code == 200
"""
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", script],
        cwd=native,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    monkeypatch.chdir(ROOT)
    for name in (
        "NEUROFLY_RUNTIME_MODE",
        "NEUROFLY_RUNTIME_RELEASE_ROOT",
        "NEUROFLY_RUNTIME_INVENTORY_ID",
        "NEUROFLY_RUNTIME_MANIFEST_ID",
        "NEUROFLY_EXPERIMENT_ARTIFACT_ROOT",
        "NEUROFLY_CIRCUIT_CONTRACT_ROOT",
    ):
        monkeypatch.delenv(name, raising=False)
    with TestClient(application(build_root)) as client:
        ready = client.get("/ready")
        assert ready.status_code == 200
        assert ready.json()["manifest_id"] == build.MANIFEST_ID
        assert ready.json()["inventory_id"] == bundle.INVENTORY_ID
    release = build_root / ".neurofly-release"
    assert Path.cwd() == release
    (release / bundle.RELEASE).write_text("{}")
    with TestClient(application(build_root)) as client:
        assert client.get("/ready").status_code == 503
        assert client.get("/health").status_code == 200
        assert (
            client.get("/api/v1/scenarios/BASELINE_CONTROL/playback").status_code == 503
        )


def test_missing_runtime_never_uses_checkout_data(monkeypatch, tmp_path):
    monkeypatch.chdir(ROOT)
    for name in (
        "NEUROFLY_RUNTIME_MODE",
        "NEUROFLY_RUNTIME_RELEASE_ROOT",
        "NEUROFLY_RUNTIME_INVENTORY_ID",
        "NEUROFLY_RUNTIME_MANIFEST_ID",
        "NEUROFLY_EXPERIMENT_ARTIFACT_ROOT",
        "NEUROFLY_CIRCUIT_CONTRACT_ROOT",
        "NEUROFLY_SCENARIO_ARTIFACT_PATH",
        "NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT",
        "NEUROFLY_MOTOR_EXPERIMENT_ARTIFACT_ROOT",
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(FileNotFoundError):
        application(tmp_path)


def test_services_route_api_before_frontend_and_bind_remote_backend():
    config = json.loads((ROOT / "vercel.json").read_text())
    assert config["git"]["deploymentEnabled"] == {
        "**": False,
        "d3r-preview": True,
    }
    assert config["services"]["backend"]["buildCommand"] == (
        "npm ci --prefix tools/vercel_blob --ignore-scripts --no-audit --no-fund"
        " && python tools/vercel_runtime_build.py"
    )
    package = json.loads((ROOT / "tools/vercel_blob/package.json").read_text())
    assert package["dependencies"] == {"@vercel/blob": "2.8.0"}
    lock = json.loads((ROOT / "tools/vercel_blob/package-lock.json").read_text())
    assert lock["packages"]["node_modules/@vercel/blob"]["version"] == "2.8.0"
    routes = config["rewrites"]
    assert [row["destination"]["service"] for row in routes] == [
        "backend",
        "backend",
        "backend",
        "frontend",
    ]
    assert routes[2]["source"] == "/api/v1/:path*"
    assert config["services"]["frontend"]["bindings"] == [
        {
            "type": "service",
            "service": "backend",
            "format": "url",
            "env": "NEUROFLY_API_BASE_URL",
        }
    ]
