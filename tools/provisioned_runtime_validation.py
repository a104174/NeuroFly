"""Validate only bundle-provisioned data using D2.1's offline read/write guard."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def child(root, forbidden, manifest_id):
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root))
    from neurofly import runtime_bundle as bundle
    from tools import runtime_dependency_closure as closure

    inventory = root / "docs/deployment_runtime_inventory_v2.json"
    rows = closure.load_inventory(inventory)["runtime_files"]
    # This installs the deny-network, deny-original-checkout, whitelist-runtime,
    # deny-runtime-writes audit hook and executes all eight historical gates.
    report = closure.child(root, forbidden, rows)
    from fastapi.testclient import TestClient

    from neurofly.http_api import create_app_from_env

    os.environ.update(
        NEUROFLY_RUNTIME_MODE="provisioned",
        NEUROFLY_RUNTIME_RELEASE_ROOT=str(root),
        NEUROFLY_RUNTIME_INVENTORY_ID=bundle.INVENTORY_ID,
        NEUROFLY_RUNTIME_MANIFEST_ID=manifest_id,
    )
    start = time.perf_counter()
    app = create_app_from_env()
    report["startup_verification_seconds"] = time.perf_counter() - start
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        start = time.perf_counter()
        ready = client.get("/ready")
        assert ready.status_code == 200 and ready.json()["ready"] is True
        report["readiness_probe_seconds"] = time.perf_counter() - start
        assert len(client.get("/api/v1/scenarios").json()) == 5
        for result in report["gates"]:
            if not result["gate"].startswith("PLAYBACK_"):
                continue
            scenario = result["gate"].removeprefix("PLAYBACK_")
            response = client.get(f"/api/v1/scenarios/{scenario}/playback")
            assert response.status_code == 200
            assert bundle.identity(response.json()) == result["payload_id"]
            print("HTTP " + scenario + " PASS", file=sys.stderr, flush=True)
        # Wrong pin fails closed, liveness remains unchanged, no playback fallback.
        os.environ["NEUROFLY_RUNTIME_MANIFEST_ID"] = "0" * 64
        with TestClient(create_app_from_env()) as invalid:
            assert invalid.get("/health").status_code == 200
            assert invalid.get("/ready").status_code == 503
            assert (
                invalid.get("/api/v1/scenarios/BASELINE_CONTROL/playback").status_code
                == 503
            )
    bundle.verify_release(root, manifest_id, inventory)
    report.update(read_only="VERIFIED", provisioned_http="PASS", no_fallback="VERIFIED")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expected-manifest-id", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--forbid-root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.child:
        os.chdir(root)
        print(
            json.dumps(
                child(root, args.forbid_root, args.expected_manifest_id), sort_keys=True
            )
        )
        return
    from neurofly import runtime_bundle as bundle

    with tempfile.TemporaryDirectory(prefix="neurofly-d2-provisioned-") as temporary:
        isolated = Path(temporary) / "release"
        start = time.perf_counter()
        bundle.provision(
            args.archive,
            args.manifest,
            args.expected_manifest_id,
            root / "docs/deployment_runtime_inventory_v2.json",
            isolated,
        )
        extraction = time.perf_counter() - start
        (isolated / "data").chmod(0o755)
        tracked = (
            subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
            .decode()
            .split("\0")
        )
        for name in tracked:
            if name and (
                name.startswith(("src/", "docs/science/", "data/reference/"))
                or name
                in (
                    "docs/deployment_runtime_inventory_v2.json",
                    "pyproject.toml",
                    "README.md",
                )
            ):
                target = isolated / name
                # Reference metadata is Git-delivered, outside the bundle set.
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / name, target)
        (isolated / "data").chmod(0o555)
        for name in (
            "tools/runtime_dependency_closure.py",
            "tools/provisioned_runtime_validation.py",
            "src/neurofly/runtime_bundle.py",
            "src/neurofly/runtime_readiness.py",
            "src/neurofly/http_api.py",
        ):
            target = isolated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, target)
        env = dict(
            os.environ, PYTHONPATH=str(isolated / "src"), PYTHONDONTWRITEBYTECODE="1"
        )
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(isolated / "tools/provisioned_runtime_validation.py"),
                "--child",
                "--root",
                str(isolated),
                "--forbid-root",
                str(root),
                "--expected-manifest-id",
                args.expected_manifest_id,
            ],
            cwd=isolated,
            env=env,
            capture_output=True,
            text=True,
        )
        print(result.stderr, file=sys.stderr, end="")
        if result.returncode:
            raise RuntimeError("provisioned closure failed")
        report = json.loads(result.stdout)
        report["provision_seconds"] = extraction
        print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
