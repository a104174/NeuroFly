"""Offline v9.2b declarative contract. Gate A is closed; no neural execution.

Source verification authenticates an artifact, not the scientific meaning of
caller-supplied fields. No input conversion or experimental solver path exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path

from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

SCHEMA = "horizontal_visual_motion_stimulus_v9_2b"
ADAPTER = "horizontal_visual_motion_contract_v9_2b"
DOI = "10.1038/s41593-025-01948-9"
FRAME = "ANATOMICAL_AZIMUTH_ZERO_FORWARD_POSITIVE_RIGHT_RAD"
# Artifact identities independently recovered in v9.2/v9.2a. None contains the
# study-specific compiled visual pattern or controller polarity definition.
SOURCES = {
    "FIGURE_1H": "b5a36e2363279a1bf908bcdcc9da7dda93ce6710487ceb31add0a284d9db9488",
    "HS_HORIZONTAL_RECORD": (
        "a50a3c5db2ba993ea9cce8167f646b3189714d8f0b27945aa4991a442a11ef2c"
    ),
}
CONDITIONS = {"ZERO", "YAW_CW", "YAW_CCW", "BFTOB", "LEFT", "RIGHT"}
FIELDS = {"coordinates", "hemisphere", "polarity", "velocity", "timing", "visibility"}


class Grounding(StrEnum):
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    DERIVED = "DERIVED_FROM_VERIFIED_GEOMETRY"
    ASSUMPTION = "ENGINEERING_ASSUMPTION"
    UNRESOLVED = "UNRESOLVED"
    UNAVAILABLE = "UNAVAILABLE"


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True, slots=True)
class Evidence:
    field: str
    status: Grounding
    reference: str

    def __post_init__(self):
        if (
            self.field not in FIELDS
            or type(self.status) is not Grounding
            or type(self.reference) is not str
            or not self.reference.strip()
        ):
            raise ValueError("invalid field evidence")


@dataclass(frozen=True, slots=True)
class Sector:
    """Optional documented sector, not a default full-field visibility mask.

    Endpoints are radians in [-pi,pi], increasing without wrap. Split a wrapping
    sector explicitly. Right is positive azimuth, left negative. Unknown geometry
    belongs in a null mask, never in invented sector coordinates.
    """

    hemisphere: str
    start_rad: float
    end_rad: float
    visible: bool

    def __post_init__(self):
        if (
            self.hemisphere not in ("L", "R")
            or not number(self.start_rad)
            or not number(self.end_rad)
            or not -math.pi <= self.start_rad < self.end_rad <= math.pi
            or type(self.visible) is not bool
            or (self.hemisphere == "R" and self.start_rad < 0)
            or (self.hemisphere == "L" and self.end_rad > 0)
        ):
            raise ValueError("invalid anatomical sector; wrapping is not implicit")


@dataclass(frozen=True, slots=True)
class Stimulus:
    schema: str
    adapter: str
    source_id: str
    source_doi: str
    source_sha256: str
    condition: str
    original_label: str
    coordinates: str
    hemisphere: str | None
    angular_velocity: float | None
    units: str
    start_ms: float | None
    end_ms: float | None
    timing_rule: str
    mask: tuple[Sector, ...] | None
    aggregation: str
    evidence: tuple[Evidence, ...]

    def __post_init__(self):
        if self.schema != SCHEMA or self.adapter != ADAPTER:
            raise ValueError("unsupported schema/adapter version")
        if (
            self.source_doi != DOI
            or self.source_id not in SOURCES
            or self.source_sha256 != SOURCES[self.source_id]
        ):
            raise ValueError("unsupported source identity")
        if self.condition not in CONDITIONS or not self.original_label.strip():
            raise ValueError("invalid condition/label")
        if self.coordinates != FRAME or self.hemisphere not in ("L", "R", "B", None):
            raise ValueError("unsupported coordinates/hemisphere")
        if self.units not in ("rad/s", "deg/s"):
            raise ValueError("unsupported angular units")
        if self.angular_velocity is not None and not number(self.angular_velocity):
            raise ValueError("non-finite angular velocity")
        if self.condition == "ZERO" and self.angular_velocity not in (None, 0):
            raise ValueError("contradictory zero-motion descriptor")
        if (self.start_ms is None) != (self.end_ms is None):
            raise ValueError("partial interval")
        if self.start_ms is not None and (
            not number(self.start_ms)
            or not number(self.end_ms)
            or not 0 <= self.start_ms < self.end_ms
            or any(
                not math.isclose(t * 10, round(t * 10), abs_tol=1e-8, rel_tol=0)
                for t in (self.start_ms, self.end_ms)
            )
        ):
            raise ValueError("require ordered 0.1-ms-aligned boundaries")
        if self.timing_rule != "HALF_OPEN_CONSTANT_HOLD_NO_INTERPOLATION":
            raise ValueError("unsupported timing rule")
        if self.aggregation != "UNRESOLVED_NO_REDUCTION":
            raise ValueError("no spatial aggregation authorized by Gate A")
        if self.mask is not None:
            if type(self.mask) is not tuple or not self.mask:
                raise ValueError("mask must be null or nonempty tuple")
            if any(type(s) is not Sector for s in self.mask):
                raise ValueError("invalid mask")
            ordered = sorted(self.mask, key=lambda s: s.start_rad)
            if any(a.end_rad > b.start_rad for a, b in zip(ordered, ordered[1:])):
                raise ValueError("overlapping mask sectors")
            if self.hemisphere is None or any(
                self.hemisphere != "B" and s.hemisphere != self.hemisphere
                for s in self.mask
            ):
                raise ValueError("contradictory hemisphere/mask")
        if (
            type(self.evidence) is not tuple
            or any(type(e) is not Evidence for e in self.evidence)
            or len(self.evidence) != len(FIELDS)
            or {e.field for e in self.evidence} != FIELDS
        ):
            raise ValueError("require exactly one evidence record per essential field")


def parse_descriptor(value: dict) -> Stimulus:
    """Strict JSON shape; no defaults that invent missing stimulus evidence."""
    if type(value) is not dict:
        raise ValueError("descriptor must be an object")
    try:
        data = value.copy()
        if data["mask"] is not None:
            data["mask"] = tuple(Sector(**s) for s in data["mask"])
        if any(
            type(e) is not dict or set(e) != {"field", "status", "reference"}
            for e in data["evidence"]
        ):
            raise ValueError("invalid evidence shape")
        data["evidence"] = tuple(
            Evidence(e["field"], Grounding(e["status"]), e["reference"])
            for e in data["evidence"]
        )
        return Stimulus(**data)
    except (TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise ValueError("invalid descriptor shape") from exc


def assess(stimulus: Stimulus, artifact: Path) -> dict:
    """Authenticate bytes and report a scientific refusal, never model activity."""
    if type(stimulus) is not Stimulus:
        raise ValueError("require validated stimulus")
    expected_size = {"FIGURE_1H": 9402, "HS_HORIZONTAL_RECORD": 4452855}
    if artifact.stat().st_size != expected_size[stimulus.source_id]:
        raise ValueError("source artifact SHA-256/size mismatch")
    if hashlib.sha256(artifact.read_bytes()).hexdigest() != stimulus.source_sha256:
        raise ValueError("source artifact SHA-256 mismatch")
    missing = sorted(
        e.field
        for e in stimulus.evidence
        if e.status not in (Grounding.SOURCE_VERIFIED, Grounding.DERIVED)
    )
    content = {
        "schema": "horizontal_visual_motion_validation_v9_2b",
        "stimulus": asdict(stimulus),
        "scientific_status": "SOURCE_METADATA_INCOMPLETE",
        "gate_a": "CLOSED",
        "blocking_findings": [
            "Study-specific controller polarity not verified in approved artifacts",
            "Exact spatiotemporal visibility masks not verified in approved artifacts",
            "No source-grounded spatial aggregation or velocity normalization approved",
        ],
        "caller_unresolved_fields": missing,
        "caller_evidence_is_not_independent_verification": True,
        "normalized_neural_input": None,
        "model_output": None,
        "neural_substeps": 0,
        "clipped_intervals": None,
        "calcium_equivalence": False,
    }
    return {"result": content, "result_sha256": canonical_sha256(content)}


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stimulus", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        output = args.output.resolve()
        root = Path(__file__).resolve().parents[2]
        if output.is_relative_to(root):
            raise ValueError("analysis output must remain outside the repository")
        if args.stimulus.stat().st_size > 100_000:
            raise ValueError("oversized stimulus descriptor")
        descriptor = parse_descriptor(
            json.loads(args.stimulus.read_text(), object_pairs_hook=_unique)
        )
        report = assess(descriptor, args.source)
        with output.open("x") as stream:
            stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"scientific_status": report["result"]["scientific_status"]}))
        return 0
    except (ValueError, OSError) as exc:
        print(
            json.dumps({"error": str(exc), "status": "EXECUTION_FAILED"}),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
