"""Read-only bridge extraction from the genuine pinned scientific response."""

import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "motor_gait_export", ROOT / "tools/exports/build_motor_gait_reference.py"
)
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


def test_selected_reference_exact_semantic_replay_and_projection():
    expected = export.reference()
    actual = json.loads(export.OUTPUT.read_bytes())
    assert actual == expected
    assert actual["source"]["edge"] == {
        "pre": 903216,
        "post": 804257,
        "synapse_count": 23,
    }
    assert actual["timebase"] == {"dt_s": 0.001, "duration_s": 2, "samples": 2001}
    rows = actual["samples"]
    for n in (20, 42, 100, 500, 1000, 2000):
        independently_summed = math.fsum(
            rows[k][0]
            * (
                math.exp(-(n - k - 1) * 0.001 / 0.01)
                - math.exp(-(n - k) * 0.001 / 0.01)
            )
            for k in range(n)
        )
        assert abs(independently_summed - rows[n][1]) < 1e-10
    assert rows[42][1] == 48.51900174689791
    assert 0.012 + 0.004 * (rows[42][1] / 100) == 0.013940760069875916
    assert all(0.012 <= r[2] <= 0.016 for r in actual["projection_reference"])
