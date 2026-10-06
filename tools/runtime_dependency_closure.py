"""Read-only dependency tracing and isolated deployment inventory validation.

This is deployment tooling, not a scientific model or archive builder.
Run from the repository: python tools/runtime_dependency_closure.py audit
Later: python tools/runtime_dependency_closure.py isolated --inventory <v2.json>
"""

import argparse
import contextlib
import hashlib
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

D1_PATH = "docs/deployment_gate_d1_runtime_inventory.json"
D1_ID = "edd7d36d4d4a9adcbc3df33a98dd5d474b8516f40074c8551faf8f4092ea82e2"
D1_BYTES_ID = "2e2719b09852164bdda97dac0f6ef3cd75f68670f6f531b1f70ae21bc1dc9b95"
CATEGORIES = {
    "CANONICAL_SCIENTIFIC_ARTIFACT",
    "CANONICAL_MANIFEST_OR_METADATA",
    "STRUCTURAL_CONTRACT",
    "SOURCE_VALIDATION_DEPENDENCY",
    "APPLICATION_STATIC_ASSET",
    "DEPLOYMENT_RUNTIME_METADATA",
    "NOT_REQUIRED_FOR_DEPLOYMENT",
    "UNEXPECTED_DEPENDENCY",
}
BASE = "data/derived/malecns/looming_giant_fiber_v1/"
SENSORY = (
    BASE
    + "sensory_population_experiment_311_v1/"
    + ("99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5")
)
PHASE16 = (
    BASE
    + "dnp01_subthreshold_diagnostic_artifact_v1/"
    + ("bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b")
)
SUPPLEMENT = {
    PHASE16 + "/diagnostic.json": (
        90631,
        "e24335e0d44486857222e1b76f4fb3dc7ca1e7e78862eaecf641db4a5839f208",
    ),
    PHASE16 + "/manifest.json": (
        439,
        "592dee368d13ea694a3a9c9e4bc72f0e47750be531d05c41b64c654ce7a1aded",
    ),
}
EXPERIMENTS = "data/derived/experiments/"
GATES = [
    ("7O", "sensory_population_execution_cli", [SENSORY]),
    (
        "8C",
        "sensory_dnp01_motor_adapter_cli",
        [
            BASE + "sensory_dnp01_ttmn_adapter_v1/"
            "5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf",
            SENSORY,
            "reference_bilateral",
        ],
    ),
    (
        "13B",
        "closed_loop_scenario_cli",
        [
            BASE + "closed_loop_scenario_artifact_v1/"
            "55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b"
        ],
    ),
    ("16_CORRECTED", "dnp01_subthreshold_diagnostic_cli", [PHASE16]),
    (
        "18",
        "looming_world_experiment_cli",
        [
            BASE + "looming_world_experiment_artifact_v1/"
            "ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c"
        ],
    ),
    (
        "25",
        "hs_dnp15_neural_validation_cli",
        [
            EXPERIMENTS + "hs_dnp15_neural_validation_artifact_v1/"
            "2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113"
        ],
    ),
    (
        "28",
        "dnp15_exploratory_yaw_cli",
        [
            EXPERIMENTS + "dnp15_exploratory_yaw_artifact_v1/"
            "243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d"
        ],
    ),
    (
        "30",
        "exploratory_course_control_cli",
        [
            EXPERIMENTS + "exploratory_course_control_closed_loop_artifact_v1/"
            "f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581"
        ],
    ),
]
PAYLOAD_IDS = {
    "BASELINE_CONTROL": (
        "475b550734133d6357fd5f8914549d9d1c5469ccfeaca8e1fb229311a9db5380"
    ),
    "LOOMING_CIRCUIT_VALIDATION": (
        "743e475ec7ad41e4cb80492688491607a19ef31ce3389ddddf6281ee9f8d8510"
    ),
    "LOOMING_WORLD_EXPERIMENT": (
        "cd9755131ecf6eb39ec26136f8d4bdadc1e65573ebfd387c4bbac25d3e53a060"
    ),
    "HORIZONTAL_MOTION_NEURAL_VALIDATION": (
        "2d61227727a0708ed5635a0054c729f9664db4e6b883edfac417573eddaafa6b"
    ),
    "EXPLORATORY_COURSE_CONTROL": (
        "ff1d4bfd9e0ba312155d1ddea76f15f0f4aba5048c4ffb3bcaf52f23e5a67e63"
    ),
}


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            ensure_ascii=True,
        ).encode()
    ).hexdigest()


def safe_path(value):
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or str(p) != value or "\\" in value:
        raise ValueError("unsafe inventory path")
    if not value.startswith("data/"):
        raise ValueError("runtime inventory must contain explicit data files")
    return value


def candidate(root):
    raw = (root / D1_PATH).read_bytes()
    d1 = json.loads(raw)
    if hashlib.sha256(raw).hexdigest() != D1_BYTES_ID or digest(d1) != D1_ID:
        raise ValueError("frozen D1 mismatch")
    rows = [dict(x) for x in d1["runtime_files"]]
    rows += [{"path": p, "bytes": n, "sha256": h} for p, (n, h) in SUPPLEMENT.items()]
    verify_files(root, rows)
    return rows


def verify_files(root, rows, *, exact=False):
    paths = [safe_path(x.get("path", x.get("repository_relative_path"))) for x in rows]
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate inventory path")
    for path, row in zip(paths, rows, strict=True):
        file = root / path
        if any(
            p.is_symlink() for p in (file, *file.parents)
        ) or not file.resolve().is_relative_to(root.resolve()):
            raise ValueError("runtime symlink/path escape")
        raw = file.read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("runtime byte/hash mismatch: " + path)
    if exact:
        actual = {
            str(p.relative_to(root))
            for p in (root / "data").rglob("*")
            if (p.is_file() or p.is_symlink())
            and not str(p.relative_to(root)).startswith("data/reference/")
        }
        if actual != set(paths):
            raise ValueError("extra/missing isolated runtime files")


def load_inventory(path):
    wrapper = json.loads(Path(path).read_bytes())
    inventory = wrapper["inventory"]
    if (
        wrapper["schema"] != "neurofly_deployment_runtime_inventory_v2"
        or digest(inventory) != wrapper["inventory_id"]
        or inventory["source_d1_inventory_id"] != D1_ID
    ):
        raise ValueError("inventory identity/schema mismatch")
    rows = inventory["runtime_files"]
    paths = [safe_path(x["repository_relative_path"]) for x in rows]
    if paths != sorted(set(paths)):
        raise ValueError("inventory paths must be unique and ordered")
    if (
        len(rows) != inventory["file_count"]
        or sum(x["bytes"] for x in rows) != inventory["total_bytes"]
    ):
        raise ValueError("inventory count/size mismatch")
    for row in rows:
        if (
            row["category"] not in CATEGORIES
            or not row["required_by"]
            or not set(row["required_by"]) <= set(inventory["required_gate_ids"])
            or not row["inclusion_reason"]
            or row["ignored_by_git"] is not True
        ):
            raise ValueError("invalid dependency classification")
    return inventory


def child(root, forbidden, rows, *, discovery=False):
    sys.path.insert(0, str(root / "src"))
    import neurofly

    if not Path(neurofly.__file__).resolve().is_relative_to(root / "src"):
        raise RuntimeError("application import fell back outside release")
    allowed = {x.get("path", x.get("repository_relative_path")) for x in rows}
    reads = {p: set() for p in allowed}
    tracked_reads = {}
    active = "STARTUP"

    def audit(event, args):
        if event in ("socket.connect", "socket.getaddrinfo"):
            raise PermissionError("network forbidden during offline closure")
        if event != "open" or not isinstance(args[0], (str, bytes)):
            return
        p = Path(os.fsdecode(args[0])).resolve()
        dependency_environment = p.is_relative_to(Path(sys.prefix).resolve())
        if forbidden and p.is_relative_to(forbidden) and not dependency_environment:
            raise PermissionError("developer checkout fallback forbidden")
        if not p.is_relative_to(root):
            if forbidden and "/data/" in str(p) and not dependency_environment:
                raise PermissionError("external runtime data read forbidden")
            return  # interpreter/third-party/system files, not release data
        relative = str(p.relative_to(root))
        if relative.startswith("data/reference/"):
            tracked_reads.setdefault(relative, set()).add(active)
        elif relative.startswith("data/"):
            if relative not in allowed and not discovery:
                raise PermissionError("unauthorized runtime read: " + relative)
            if args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
                raise PermissionError("runtime data writes forbidden")
            reads.setdefault(relative, set()).add(active)
        elif relative.startswith("docs/science/"):
            tracked_reads.setdefault(relative, set()).add(active)

    sys.addaudithook(audit)
    results = []
    for name, module, arguments in GATES:
        active = "REPLAY_" + name
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            code = importlib.import_module("neurofly." + module).main(
                ["replay", *arguments]
            )
        if code != 0:
            raise ValueError("historical replay failed: " + name)
        payload = json.loads(captured.getvalue())
        artifact = payload.get("artifact", payload)
        if artifact["artifact_id"] != Path(arguments[0]).name:
            raise ValueError("historical identity mismatch")
        results.append(
            {"gate": active, "artifact_id": artifact["artifact_id"], "status": "PASS"}
        )
        print(active + " PASS", file=sys.stderr, flush=True)
    active = "STARTUP"
    for key in list(os.environ):
        if key.startswith("NEUROFLY_"):
            del os.environ[key]
    os.environ["NEUROFLY_EXPERIMENT_ARTIFACT_ROOT"] = str(root / EXPERIMENTS)
    os.environ["NEUROFLY_SCENARIO_ARTIFACT_PATH"] = str(root / GATES[2][2][0])
    os.environ["NEUROFLY_CIRCUIT_CONTRACT_ROOT"] = str(root / BASE)
    from fastapi.testclient import TestClient

    from neurofly.http_api import create_app_from_env
    from neurofly.scenario_playback_api import load_scenario_playback

    with TestClient(create_app_from_env()) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert {r["id"] for r in client.get("/api/v1/scenarios").json()} == set(
            PAYLOAD_IDS
        )
        results.append({"gate": "STARTUP", "status": "PASS"})
        for scenario, expected in PAYLOAD_IDS.items():
            active = "PLAYBACK_" + scenario
            # Same public adapter invoked by the HTTP route; preserves exact bytes.
            payload = load_scenario_playback(scenario)
            raw = payload.model_dump_json(by_alias=True).encode()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("frozen transport mismatch: " + scenario)
            results.append(
                {
                    "gate": active,
                    "transport_sha256": expected,
                    "payload_id": digest(
                        payload.model_dump(mode="json", by_alias=True)
                    ),
                    "artifact_id": payload.artifact_id,
                    "bytes": len(raw),
                    "status": "PASS",
                }
            )
            print(active + " PASS", file=sys.stderr, flush=True)
    return {
        "gates": results,
        "runtime_reads": {p: sorted(v) for p, v in sorted(reads.items())},
        "tracked_science_reads": {
            p: sorted(v) for p, v in sorted(tracked_reads.items())
        },
        "unauthorized_runtime_reads": [],
        "discovered_outside_candidate": sorted(set(reads) - allowed),
        "network_access": "DENIED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("audit", "isolated", "child"))
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--forbid-root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    rows = (
        candidate(root)
        if args.inventory is None
        else load_inventory(args.inventory)["runtime_files"]
    )
    if args.mode == "child":
        os.chdir(root)
        print(json.dumps(child(root, args.forbid_root, rows), sort_keys=True))
        return
    verify_files(root, rows)
    if args.mode == "audit":
        # One complete read-only discovery pass. Discovered paths are evidence,
        # NOT automatically authorized or copied into an isolated release.
        print(json.dumps(child(root, None, rows, discovery=True), sort_keys=True))
        return
    with tempfile.TemporaryDirectory(prefix="neurofly-d21-closure-") as directory:
        isolated = Path(directory)
        tracked = (
            subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
            .decode()
            .split("\0")
        )
        for name in tracked:
            if name and (
                name.startswith(("src/", "docs/science/", "data/reference/"))
                or name in (D1_PATH, "pyproject.toml", "README.md")
            ):
                target = isolated / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / name, target)
        tool = isolated / "tools/runtime_dependency_closure.py"
        tool.parent.mkdir()
        shutil.copyfile(Path(__file__), tool)
        for row in rows:
            path = row.get("path", row.get("repository_relative_path"))
            target = isolated / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, target)
        verify_files(isolated, rows, exact=True)
        env = dict(
            os.environ, PYTHONPATH=str(isolated / "src"), PYTHONDONTWRITEBYTECODE="1"
        )
        # The child constructs the same reviewed D1+Phase16 candidate, unless a
        # final v2 inventory is explicitly supplied and independently verified.
        command = [
            sys.executable,
            "-B",
            str(tool),
            "child",
            "--root",
            str(isolated),
            "--forbid-root",
            str(root),
        ]
        if args.inventory:
            target_inventory = isolated / "inventory.json"
            shutil.copyfile(args.inventory, target_inventory)
            command += ["--inventory", str(target_inventory)]
        result = subprocess.run(
            command, cwd=isolated, env=env, capture_output=True, text=True
        )
        if result.returncode:
            print(result.stderr, file=sys.stderr, end="")
            raise RuntimeError("isolated closure failed; no inventory updated")
        verify_files(isolated, rows, exact=True)
        print(result.stderr, file=sys.stderr, end="")
        print(result.stdout, end="")


if __name__ == "__main__":
    main()
