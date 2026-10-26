"""Git-source runtime provisioning and deployed application wiring."""

import json
import os
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
def git_environment(monkeypatch):
    monkeypatch.setenv("VERCEL_GIT_COMMIT_SHA", "a" * 40)
    for name in ("VERCEL_OIDC_TOKEN", "BLOB_STORE_ID", "BLOB_READ_WRITE_TOKEN"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def build_root(tmp_path):
    source = ROOT / build.MANIFEST_PATH
    wrapper = bundle.manifest(source, build.MANIFEST_ID, ROOT / build.INVENTORY_PATH)
    names = [build.MANIFEST_PATH, build.INVENTORY_PATH, build.ARCHIVE_PATH] + [
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
    for name in ("tools/vercel_runtime_build.py", "tools/vercel_runtime_entrypoint.py"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return tmp_path


def test_missing_committed_archive_fails_closed(build_root):
    (build_root / build.ARCHIVE_PATH).unlink()
    with pytest.raises(FileNotFoundError, match="required Git source file"):
        build.build(build_root)
    assert not (build_root / ".neurofly-release").exists()


@pytest.mark.parametrize("same_size", [False, True])
def test_wrong_committed_archive_bytes_or_hash_rejected(build_root, same_size):
    archive = build_root / build.ARCHIVE_PATH
    archive.write_bytes(bytes(build.COMPRESSED_BYTES if same_size else 1))
    expected = (
        "archive integrity failure"
        if same_size
        else "pinned runtime v3 archive size mismatch"
    )
    with pytest.raises(ValueError, match=expected):
        build.build(build_root)
    assert not (build_root / ".neurofly-release").exists()


def test_committed_runtime_builds_without_blob_access(
    monkeypatch, build_root, tmp_path, capsys
):
    monkeypatch.setattr(sys, "path", sys.path.copy())
    assert not hasattr(build, "retrieve")
    for name in ("VERCEL_OIDC_TOKEN", "BLOB_STORE_ID", "BLOB_READ_WRITE_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    build.build(build_root)
    logged = json.loads(
        capsys.readouterr().out.removeprefix("NEUROFLY RUNTIME VERIFIED ")
    )
    assert logged["application_commit_sha"] == "a" * 40
    assert logged["data_source_commit_sha"] != logged["application_commit_sha"]
    assert logged["archive_sha256"] == build.ARCHIVE_SHA
    # A fresh process cannot use the editable checkout or installed neurofly.
    # This exercises the same module-relative paths as the native bundle.
    native = tmp_path / "native"
    native.mkdir()
    shutil.copytree(build_root / ".neurofly-release", native / ".neurofly-release")
    shutil.copytree(build_root / "tools", native / "tools")
    script = """
import hashlib
import importlib.abc
import json
import sys
from pathlib import Path
class RejectAcquisition(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'neuprint', 'scipy', 'pyarrow', 'pandas'}:
            raise AssertionError('serving attempted acquisition import')
sys.meta_path.insert(0, RejectAcquisition())
sys.path.insert(0, str(Path.cwd()))
from tools.vercel_runtime_entrypoint import application
assert 'neurofly' not in sys.modules
app = application(Path.cwd(), manifest_id=sys.argv[1], inventory_id=sys.argv[2])
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
    assert client.get('/health').json()['read_only'] is True
    assert client.get('/ready').status_code == 200
    assert len(client.get('/api/v1/scenarios').json()) == 5
    experiments = client.get('/api/v1/experiments')
    assert experiments.status_code == 200
    assert experiments.json()['count'] == 1
    run = experiments.json()['experiments'][0]
    assert run['artifact_id'] == (
        '63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656')
    assert run['result_id'] == (
        '8af5a3f50f0cd9fee65ce62e5421c873e95a48e32333de475545c1be7f133b45')
    assert run['validation_status'] == 'NOT_EVALUATED'
    assert client.get('/ready').json()['file_count'] == 79
    assert client.get('/api/v1/experiments/'+run['artifact_id']).json() == run
    timeline = client.get('/api/v1/experiments/'+run['artifact_id']+'/timeline')
    assert len(timeline.json()['times_ms']) == 801
    hashes = {
        'BASELINE_CONTROL':
            '75d1f2856f0d896589a8b1f62fb61016d701045b760e216b7cb5fa70daa30668',
        'LOOMING_CIRCUIT_VALIDATION':
            'c3387396dcffa6372287df1a7d4680bb7ba605df319af4cf10f140cfc3a4d223',
        'LOOMING_WORLD_EXPERIMENT':
            'd06ef32aaf054b981464948916e5687951b40f571be5286513dad8ae440f26df',
        'HORIZONTAL_MOTION_NEURAL_VALIDATION':
            '52554962f3e9c85c6866b5e3ec56f8a12d24340db2236ec52c7809c6ece8d404',
        'EXPLORATORY_COURSE_CONTROL':
            '7fddc1109495023d8f64744237796d5d8e86852abef80b6979f1994088d46806',
    }
    for scenario in ['BASELINE_CONTROL', 'LOOMING_CIRCUIT_VALIDATION',
                     'LOOMING_WORLD_EXPERIMENT', 'HORIZONTAL_MOTION_NEURAL_VALIDATION',
                     'EXPLORATORY_COURSE_CONTROL']:
        response = client.get('/api/v1/scenarios/' + scenario + '/playback')
        assert response.status_code == 200
        canonical = json.dumps(response.json(), sort_keys=True,
                               separators=(',', ':'), allow_nan=False).encode()
        assert hashlib.sha256(canonical).hexdigest() == hashes[scenario]
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            script,
            build.MANIFEST_ID,
            build.RUNTIME_INVENTORY_ID,
        ],
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
    with TestClient(
        application(
            build_root,
            manifest_id=build.MANIFEST_ID,
            inventory_id=build.RUNTIME_INVENTORY_ID,
        )
    ) as client:
        ready = client.get("/ready")
        assert ready.status_code == 200
        assert ready.json()["manifest_id"] == build.MANIFEST_ID
        assert ready.json()["inventory_id"] == build.RUNTIME_INVENTORY_ID
    release = build_root / ".neurofly-release"
    assert Path.cwd() == release
    (release / bundle.RELEASE).write_text("{}")
    with TestClient(
        application(
            build_root,
            manifest_id=build.MANIFEST_ID,
            inventory_id=build.RUNTIME_INVENTORY_ID,
        )
    ) as client:
        assert client.get("/ready").status_code == 503
        assert client.get("/health").status_code == 200
        assert (
            client.get("/api/v1/scenarios/BASELINE_CONTROL/playback").status_code == 503
        )


@pytest.mark.parametrize("commit", [None, "", "main", "a" * 39, "A" * 40])
def test_missing_or_invalid_vercel_commit_fails_before_provision(
    monkeypatch, tmp_path, commit
):
    if commit is None:
        monkeypatch.delenv("VERCEL_GIT_COMMIT_SHA", raising=False)
    else:
        monkeypatch.setenv("VERCEL_GIT_COMMIT_SHA", commit)
    monkeypatch.setattr(bundle, "provision", lambda *a: pytest.fail("provision"))
    with pytest.raises(ValueError, match="Vercel Git commit SHA is required"):
        build.build(tmp_path)


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
    assert config["git"]["deploymentEnabled"]["main"] is True
    assert config["services"]["backend"]["buildCommand"] == (
        "python tools/vercel_runtime_build.py"
    )
    assert "npm ci" not in config["services"]["backend"]["buildCommand"]
    assert build.ARCHIVE_PATH == (
        "runtime-distributions/v3/"
        "neurofly-runtime-v3-c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf.tar.gz"
    )
    routes = config["rewrites"]
    assert [row["destination"]["service"] for row in routes] == [
        "backend",
        "backend",
        "backend",
        "frontend",
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


def test_pinned_compiler_root_and_service_precedence():
    """Use installed CLI 62.7.0 routing-utils, with no network or deployment.

    CI can supply NEUROFLY_VERCEL_ROUTING_MODULE instead of an npm cache.
    This small bundle adapter is confined to the compiler regression gate.
    """
    explicit = os.environ.get("NEUROFLY_VERCEL_ROUTING_MODULE")
    modules = [Path(explicit)] if explicit else []
    if not explicit:
        cache = Path(os.environ.get("NPM_CONFIG_CACHE", Path.home() / ".npm"))
        for package in sorted((cache / "_npx").glob("*/node_modules/vercel")):
            if (
                json.loads((package / "package.json").read_text())["version"]
                != "62.7.0"
            ):
                continue
            modules.extend(
                path
                for path in sorted((package / "dist/chunks").glob("*.js"))
                if "getTransformedRoutes" in path.read_text()
                and "require_dist" in path.read_text()
            )
    assert modules, "Compiler gate requires installed Vercel 62.7.0 routing-utils"
    script = """
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
let compiler;
for (const file of JSON.parse(process.argv[1])) {
    const module = await import(pathToFileURL(file));
    if (typeof module.require_dist !== 'function') continue;
    const api = module.require_dist();
    if (typeof api.getTransformedRoutes === 'function') {compiler = api; break;}
}
if (!compiler) throw new Error('Pinned routing-utils export not found');
const config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const old = {...config, rewrites: config.rewrites.filter(row => row.source !== '/')};
function select(config, path) {
    const {routes, error} = compiler.getTransformedRoutes(config);
    if (error) throw new Error('Routing configuration rejected');
    return routes.find(row => row.src && new RegExp(row.src).test(path)
        && row.destination?.service)?.destination.service ?? null;
}
console.log(JSON.stringify(JSON.parse(process.argv[3]).map(path =>
    ({path, previous: select(old, path), current: select(config, path)}))));
"""
    frontend = [
        "/scenarios",
        "/scenarios/BASELINE_CONTROL",
        "/experiments",
        "/experiments/" + "a" * 64 + "/cockpit",
        "/morphology/example",
        "/_next/static/chunks/example.js",
        "/api/unknown",
    ]
    backend = [
        "/health",
        "/ready",
        "/api/v1/scenarios",
        "/api/v1/experiments",
        "/api/v1/unknown",
        *[
            f"/api/v1/scenarios/{name}/playback"
            for name in (
                "BASELINE_CONTROL",
                "LOOMING_CIRCUIT_VALIDATION",
                "LOOMING_WORLD_EXPERIMENT",
                "HORIZONTAL_MOTION_NEURAL_VALIDATION",
                "EXPLORATORY_COURSE_CONTROL",
            )
        ],
    ]
    result = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            script,
            json.dumps([str(path) for path in modules]),
            str(ROOT / "vercel.json"),
            json.dumps(["/", *frontend, *backend]),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    rows = json.loads(result.stdout)
    assert rows[0] == {"path": "/", "previous": None, "current": "frontend"}
    for row in rows[1:]:
        expected = "backend" if row["path"] in backend else "frontend"
        assert row["current"] == row["previous"] == expected
    routes = json.loads((ROOT / "vercel.json").read_text())["rewrites"]
    assert [row["source"] for row in routes] == [
        "/health",
        "/ready",
        "/api/v1/:path*",
        "/",
        "/:path*",
    ]


def test_unknown_scientific_api_does_not_become_frontend_success(tmp_path):
    from neurofly.http_api import create_app

    with TestClient(create_app(tmp_path)) as client:
        response = client.get("/api/v1/unknown")
        assert response.status_code == 404
        assert response.headers["content-type"] == "application/json"
    # Other /api paths remain Next-owned; no frontend API fallback exists.
    assert not list((ROOT / "web/src/app").glob("api/**/route.*"))
