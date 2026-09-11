"""Offline tests for the Phase 2H-A empirical metadata boundary."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.empirical_constraints import (
    AvailabilityStatus,
    ComparabilityStatus,
    ConstraintRegistry,
    ConstraintRegistryError,
    ConstraintRole,
    EmpiricalConstraint,
    EmpiricalConstraintError,
    MeasurementModality,
    ObservationTransformKind,
    ObservationTransformSpec,
    PayloadReference,
    ReuseStatus,
    ValidationProtocol,
    inspect_registry,
)

REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "reference"
    / "empirical_constraints"
    / "constraint_registry_v1.json"
)


def test_phase2g_registry_loads_and_reports_expected_summary() -> None:
    summary = inspect_registry(REGISTRY_PATH)
    assert summary["constraint_count"] == 14
    assert summary["comparison_ready_count"] == 3
    assert summary["by_role"] == {
        "CONTEXT_ONLY": 2,
        "FIT_CONSTRAINT": 3,
        "HELD_OUT_VALIDATION": 3,
        "NOT_DIRECTLY_COMPARABLE": 3,
        "QUALITATIVE_VALIDATION": 3,
    }
    assert len(summary["pending_source_ids"]) == 3


def test_registry_preserves_every_preregistered_id_and_role() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    assert [record.constraint_id for record in registry.constraints] == sorted(
        record.constraint_id for record in registry.constraints
    )
    assert registry.protocol.fit_constraint_ids == (
        "ACHE19_LC4_GF_ISOLATED_WAVEFORM",
        "ACHE19_LPLC2_GF_ISOLATED_WAVEFORM",
        "KLAP17_LPLC2_DARK_LOOM_SPEED_SERIES",
    )
    assert (
        registry.get("ACHE19_TRANSIENT_LATENCY_19MS").role
        is ConstraintRole.NOT_DIRECTLY_COMPARABLE
    )


def test_registry_order_does_not_change_identity() -> None:
    raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    reversed_raw = copy.deepcopy(raw)
    reversed_raw["constraints"] = list(reversed(reversed_raw["constraints"]))
    reversed_registry = ConstraintRegistry.from_mapping(reversed_raw)
    original = ConstraintRegistry.load(REGISTRY_PATH)
    assert reversed_registry.sha256 == original.sha256
    assert reversed_registry.protocol_sha256 == original.protocol_sha256


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("role", "UNKNOWN_ROLE"),
        ("measurement_modality", "UNKNOWN_MODALITY"),
        ("availability", "UNKNOWN_AVAILABILITY"),
        ("comparability", "UNKNOWN_COMPARABILITY"),
    ],
)
def test_unknown_closed_enum_is_rejected(field: str, value: str) -> None:
    raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    raw["constraints"][0][field] = value
    with pytest.raises(EmpiricalConstraintError):
        ConstraintRegistry.from_mapping(raw, strict_phase2g=False)


@pytest.mark.parametrize("field", ["citation", "doi", "source_location"])
def test_required_source_metadata_is_rejected_when_missing(field: str) -> None:
    raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    raw["constraints"][0][field] = ""
    with pytest.raises(EmpiricalConstraintError):
        ConstraintRegistry.from_mapping(raw, strict_phase2g=False)


def test_measurement_modality_and_units_cannot_be_collapsed() -> None:
    raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    raw["constraints"][6]["units"] = "mV"
    with pytest.raises(EmpiricalConstraintError, match="voltage units"):
        ConstraintRegistry.from_mapping(raw, strict_phase2g=False)


def test_pending_source_data_has_no_payload_and_is_not_ready() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    record = registry.get("ACHE19_LC4_GF_ISOLATED_WAVEFORM")
    assert record.availability is AvailabilityStatus.PENDING_SOURCE_DATA
    assert record.payload_reference is None
    assert not record.is_comparison_ready()


def test_pending_review_requires_received_payload_reference() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    record = registry.get("ACHE19_LC4_GF_ISOLATED_WAVEFORM")
    with pytest.raises(EmpiricalConstraintError, match="PENDING_REVIEW"):
        replace(record, availability=AvailabilityStatus.PENDING_REVIEW)


def test_figure_only_record_cannot_gain_payload_reference() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    record = registry.get("KLAP17_LPLC2_RECEDING_NULL")
    reference = PayloadReference(
        artifact_id="synthetic-test",
        relative_path="payload.csv",
        sha256="0" * 64,
        received_at_utc="2026-09-11T00:00:00+00:00",
        original_filename="payload.csv",
        format="csv",
        parser_schema_id="test_v1",
        source_contact_ref="test_source",
    )
    with pytest.raises(EmpiricalConstraintError, match="Figure-only"):
        replace(record, payload_reference=reference)


def test_available_verified_numeric_data_requires_checksum_and_reuse() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    record = registry.get("ACHE19_LC4_GF_ISOLATED_WAVEFORM")
    with pytest.raises(EmpiricalConstraintError, match="payload reference"):
        replace(record, availability=AvailabilityStatus.AVAILABLE_VERIFIED)

    with pytest.raises(EmpiricalConstraintError, match="64-character"):
        PayloadReference(
            artifact_id="bad",
            relative_path="payload.csv",
            sha256="not-a-hash",
            received_at_utc="2026-09-11T00:00:00+00:00",
            original_filename="payload.csv",
            format="csv",
            parser_schema_id="test_v1",
            source_contact_ref="test_source",
        )


def _synthetic_constraint(
    *,
    availability: AvailabilityStatus,
    payload_reference: PayloadReference | None = None,
) -> EmpiricalConstraint:
    return EmpiricalConstraint(
        constraint_id="SYNTHETIC_FIT",
        protocol_version="test_protocol_v1",
        citation="Synthetic test metadata",
        doi="10.0000/test",
        publication_year=2026,
        source_location="test fixture",
        experimental_population="test population",
        pathway_condition="test condition",
        stimulus_description="test stimulus",
        measurement_modality=MeasurementModality.GF_INTRACELLULAR_VOLTAGE,
        units="mV",
        source_time_reference="stimulus onset",
        source_normalization="none",
        role=ConstraintRole.FIT_CONSTRAINT,
        availability=availability,
        comparability=ComparabilityStatus.DIRECTLY_COMPARABLE,
        reuse_status=(
            ReuseStatus.PERMITTED
            if availability is AvailabilityStatus.AVAILABLE_VERIFIED
            else ReuseStatus.PENDING_CONFIRMATION
        ),
        uncertainty="synthetic fixture uncertainty",
        sample_size="synthetic fixture",
        neurofly_observable="test observable",
        limitations="test only",
        payload_reference=payload_reference,
    )


def test_future_receipt_state_machine_requires_review_then_verification(
    tmp_path: Path,
) -> None:
    pending = _synthetic_constraint(availability=AvailabilityStatus.PENDING_SOURCE_DATA)
    assert not pending.is_comparison_ready()

    payload = b"synthetic test payload\n"
    payload_path = tmp_path / "payload.csv"
    payload_path.write_bytes(payload)
    reference = PayloadReference(
        artifact_id="synthetic-test",
        relative_path="payload.csv",
        sha256=hashlib.sha256(payload).hexdigest(),
        received_at_utc="2026-09-11T00:00:00+00:00",
        original_filename="payload.csv",
        format="csv",
        parser_schema_id="test_v1",
        source_contact_ref="test_source",
    )
    pending_review = _synthetic_constraint(
        availability=AvailabilityStatus.PENDING_REVIEW,
        payload_reference=reference,
    )
    assert not pending_review.is_comparison_ready(tmp_path)

    verified = _synthetic_constraint(
        availability=AvailabilityStatus.AVAILABLE_VERIFIED,
        payload_reference=reference,
    )
    assert not verified.is_comparison_ready()
    assert verified.is_comparison_ready(tmp_path)
    assert verified.is_redistribution_ready(tmp_path)
    payload_path.write_bytes(b"corrupted\n")
    assert not verified.is_comparison_ready(tmp_path)


def test_qualitative_constraint_is_ready_without_fake_numeric_payload() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    record = registry.get("KLAP17_LPLC2_RECEDING_NULL")
    assert record.payload_reference is None
    assert record.qualitative_relation
    assert record.is_comparison_ready()


def test_role_change_changes_protocol_identity() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    changed = tuple(
        replace(
            record,
            role=(
                ConstraintRole.CONTEXT_ONLY
                if record.constraint_id == "ACHE19_LC4_GF_ISOLATED_WAVEFORM"
                else record.role
            ),
        )
        for record in registry.constraints
    )
    changed_protocol = ValidationProtocol.from_constraints(
        changed,
        protocol_id=registry.protocol.protocol_id,
        protocol_version=registry.protocol.protocol_version,
    )
    assert changed_protocol.sha256 != registry.protocol_sha256
    with pytest.raises(ConstraintRegistryError):
        ConstraintRegistry.from_constraints(changed, strict_phase2g=True)


def test_transform_declarations_are_narrow_and_forbid_free_shift() -> None:
    transform = ObservationTransformSpec(
        transform_id="baseline_test",
        version="v1",
        kind=ObservationTransformKind.BASELINE_SUBTRACTION,
        parameters=(
            ("baseline_end_ms", 0.0),
            ("baseline_start_ms", -100.0),
        ),
    )
    assert transform.identity
    with pytest.raises(EmpiricalConstraintError, match="forbidden"):
        ObservationTransformSpec(
            transform_id="free_shift",
            version="v1",
            kind=ObservationTransformKind.TIME_REFERENCE_CONVERSION,
            parameters={
                "from_reference": "stimulus",
                "to_reference": "model",
                "free_shift_ms": 19.0,
            },
        )


def test_19_ms_record_cannot_become_model_latency() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    record = registry.get("ACHE19_TRANSIENT_LATENCY_19MS")
    assert record.comparability is ComparabilityStatus.NOT_DIRECTLY_COMPARABLE
    assert record.measurement_modality.value == "GF_RESPONSE_LATENCY"
    assert record.neurofly_observable == "none"
    assert not record.is_comparison_ready()


def test_serialization_contains_no_credentials() -> None:
    registry = ConstraintRegistry.load(REGISTRY_PATH)
    serialized = json.dumps(registry.to_dict(), sort_keys=True)
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in serialized
    assert "credential" not in serialized.lower()
