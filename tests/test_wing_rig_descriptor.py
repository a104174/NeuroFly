"""Read-only regeneration of presentation hinges, not scientific model processing."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "wing_export", ROOT / "tools/exports/build_wing_rig.py"
)
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


def test_descriptor_reproduced_from_immutable_deployed_glb():
    raw = export.OUTPUT.read_bytes()
    assert export.derive() == json.loads(raw)
    assert hashlib.sha256(raw).hexdigest() == (
        "f175ede40fd15892d6089d446146b371a4534be048ffa45447a7cb5a740a51ff"
    )
    wings = json.loads(raw)["wings"]
    assert [w["id"] for w in wings] == ["Wing.L", "Wing.R"]
    assert wings[0]["pivot"][0] < 0 < wings[1]["pivot"][0]
    assert all(w["vertices"] == 1252 for w in wings)
