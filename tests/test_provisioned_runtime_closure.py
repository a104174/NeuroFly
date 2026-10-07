"""Full offline release gate: no developer data tree or runtime writes."""

import json
import subprocess
import sys
from pathlib import Path

from neurofly import runtime_bundle as bundle

ROOT = Path(__file__).resolve().parents[1]


def test_clean_bundle_provisioned_scientific_closure(tmp_path):
    archive, manifest, wrapper = bundle.build(
        ROOT,
        ROOT / "docs/deployment_runtime_inventory_v2.json",
        tmp_path,
        "f7baa1db24d2ff6c993894d4edafc33d736a58cd",
    )
    result = subprocess.run(
        [
            sys.executable,
            "tools/provisioned_runtime_validation.py",
            "--archive",
            str(archive),
            "--manifest",
            str(manifest),
            "--expected-manifest-id",
            wrapper["manifest_id"],
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(result.stdout)
    assert len(report["gates"]) == 14
    assert all(gate["status"] == "PASS" for gate in report["gates"])
    assert report["unauthorized_runtime_reads"] == []
    assert report["discovered_outside_candidate"] == []
    assert report["provisioned_http"] == "PASS"
    assert report["read_only"] == report["no_fallback"] == "VERIFIED"
    assert report["network_access"] == "DENIED"
    assert len(report["runtime_reads"]) == 74
