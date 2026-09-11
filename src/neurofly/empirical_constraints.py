"""Provenance-controlled empirical-constraint metadata.

This module deliberately stores constraint metadata and references to possible
future source files, not experimental arrays.  It is an offline protocol
boundary: it does not download data, fit parameters, or transform numerical
traces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "empirical_constraint_registry_v1"
PROTOCOL_ID = "empirical_constraint_protocol_v1"
PROTOCOL_VERSION = "phase_2g_v1"
DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "reference"
    / "empirical_constraints"
    / "constraint_registry_v1.json"
)


class EmpiricalConstraintError(ValueError):
    """Base error for invalid empirical metadata or protocol state."""


class ConstraintRegistryError(EmpiricalConstraintError):
    """The metadata registry is malformed or fails its integrity checks."""


class ConstraintRole(StrEnum):
    FIT_CONSTRAINT = "FIT_CONSTRAINT"
    HELD_OUT_VALIDATION = "HELD_OUT_VALIDATION"
    QUALITATIVE_VALIDATION = "QUALITATIVE_VALIDATION"
    CONTEXT_ONLY = "CONTEXT_ONLY"
    NOT_DIRECTLY_COMPARABLE = "NOT_DIRECTLY_COMPARABLE"


class AvailabilityStatus(StrEnum):
    PENDING_SOURCE_DATA = "PENDING_SOURCE_DATA"
    PENDING_REVIEW = "PENDING_REVIEW"
    FIGURE_ONLY_NOT_EXTRACTED = "FIGURE_ONLY_NOT_EXTRACTED"
    AVAILABLE_VERIFIED = "AVAILABLE_VERIFIED"
    UNAVAILABLE = "UNAVAILABLE"
    WITHDRAWN_OR_UNUSABLE = "WITHDRAWN_OR_UNUSABLE"


class ReuseStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    PERMITTED = "PERMITTED"
    RESTRICTED = "RESTRICTED"
    PROHIBITED = "PROHIBITED"


class ComparabilityStatus(StrEnum):
    DIRECTLY_COMPARABLE = "DIRECTLY_COMPARABLE"
    COMPARABLE_AFTER_DECLARED_TRANSFORM = "COMPARABLE_AFTER_DECLARED_TRANSFORM"
    RELATIVE_OR_NORMALIZED_ONLY = "RELATIVE_OR_NORMALIZED_ONLY"
    QUALITATIVE_ONLY = "QUALITATIVE_ONLY"
    NOT_DIRECTLY_COMPARABLE = "NOT_DIRECTLY_COMPARABLE"


class MeasurementModality(StrEnum):
    GF_INTRACELLULAR_VOLTAGE = "GF_INTRACELLULAR_VOLTAGE"
    GF_SPIKE_TIMING = "GF_SPIKE_TIMING"
    GF_RESPONSE_LATENCY = "GF_RESPONSE_LATENCY"
    CALCIUM_DFF = "CALCIUM_DFF"
    BEHAVIORAL_LATENCY = "BEHAVIORAL_LATENCY"
    PHENOMENOLOGICAL_MODEL = "PHENOMENOLOGICAL_MODEL"
    QUALITATIVE_RESPONSE = "QUALITATIVE_RESPONSE"


class ObservationTransformKind(StrEnum):
    BASELINE_SUBTRACTION = "BASELINE_SUBTRACTION"
    SOURCE_MATCHED_NORMALIZATION = "SOURCE_MATCHED_NORMALIZATION"
    DECLARED_SMOOTHING = "DECLARED_SMOOTHING"
    TIME_REFERENCE_CONVERSION = "TIME_REFERENCE_CONVERSION"


_NUMERIC_TYPES = (int, float)
_FORBIDDEN_TRANSFORM_KEYS = frozenset(
    {
        "free_shift_ms",
        "alignment_offset_ms",
        "amplitude_scale",
        "free_amplitude_scale",
        "digitize_pixels",
        "calcium_to_voltage",
        "model_derived_maximum",
    }
)


def _required_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EmpiricalConstraintError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _finite_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, _NUMERIC_TYPES):
        raise EmpiricalConstraintError(f"{field_name} must be numeric.")
    converted = float(value)
    if not math.isfinite(converted):
        raise EmpiricalConstraintError(f"{field_name} must be finite.")
    return converted


def _enum(value: Any, enum_type: type[StrEnum], field_name: str) -> StrEnum:
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise EmpiricalConstraintError(
            f"{field_name} has unsupported value {value!r}; expected one of {allowed}."
        ) from exc


def _iso_datetime(value: str, field_name: str) -> str:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EmpiricalConstraintError(
            f"{field_name} must be an ISO-8601 timestamp."
        ) from exc
    return value


def _canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise EmpiricalConstraintError(
            "Value is not deterministically serializable."
        ) from exc


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _freeze_parameters(value: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    if not isinstance(value, Mapping):
        raise EmpiricalConstraintError("Transform parameters must be an object.")
    frozen: list[tuple[str, Any]] = []
    for raw_key, raw_value in value.items():
        key = _required_string(raw_key, "transform parameter name")
        if key in _FORBIDDEN_TRANSFORM_KEYS:
            raise EmpiricalConstraintError(
                f"Transform parameter {key!r} is forbidden by the protocol."
            )
        if (
            isinstance(raw_value, bool)
            or isinstance(raw_value, str)
            or raw_value is None
        ):
            value_for_storage = raw_value
        elif isinstance(raw_value, _NUMERIC_TYPES):
            value_for_storage = _finite_number(raw_value, f"transform parameter {key}")
            if isinstance(raw_value, int):
                value_for_storage = int(raw_value)
        else:
            raise EmpiricalConstraintError(
                f"Transform parameter {key!r} must be a scalar JSON value."
            )
        frozen.append((key, value_for_storage))
    return tuple(sorted(frozen))


@dataclass(frozen=True, slots=True)
class ObservationTransformSpec:
    """An allowed, declared observation transform.

    This is a declaration only.  Phase 2H-A intentionally does not execute
    numerical transforms because source-specific implementation semantics are
    not yet complete.
    """

    transform_id: str
    version: str
    kind: ObservationTransformKind
    parameters: tuple[tuple[str, Any], ...] = ()
    executable: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        transform_id = _required_string(self.transform_id, "transform_id")
        version = _required_string(self.version, "transform version")
        kind = _enum(self.kind, ObservationTransformKind, "transform kind")
        if not isinstance(self.parameters, tuple):
            parameters = _freeze_parameters(self.parameters)  # type: ignore[arg-type]
        else:
            parameters = _freeze_parameters(dict(self.parameters))
        notes = self.notes if isinstance(self.notes, str) else str(self.notes)
        if not isinstance(self.executable, bool):
            raise EmpiricalConstraintError("transform executable must be boolean.")

        values = dict(parameters)
        if kind is ObservationTransformKind.BASELINE_SUBTRACTION:
            start = _finite_number(values.get("baseline_start_ms"), "baseline_start_ms")
            end = _finite_number(values.get("baseline_end_ms"), "baseline_end_ms")
            if end <= start:
                raise EmpiricalConstraintError(
                    "Baseline interval must have positive width."
                )
        elif kind is ObservationTransformKind.SOURCE_MATCHED_NORMALIZATION:
            _required_string(values.get("rule"), "normalization rule")
        elif kind is ObservationTransformKind.DECLARED_SMOOTHING:
            window = _finite_number(values.get("window_ms"), "smoothing window_ms")
            if window <= 0:
                raise EmpiricalConstraintError("Smoothing window_ms must be positive.")
            _required_string(values.get("purpose"), "smoothing purpose")
        elif kind is ObservationTransformKind.TIME_REFERENCE_CONVERSION:
            _required_string(values.get("from_reference"), "from_reference")
            _required_string(values.get("to_reference"), "to_reference")
            if "offset_ms" in values:
                raise EmpiricalConstraintError(
                    "Time-reference declarations cannot contain a free offset_ms."
                )
        object.__setattr__(self, "transform_id", transform_id)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(self, "notes", notes)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ObservationTransformSpec:
        if not isinstance(value, Mapping):
            raise EmpiricalConstraintError("Transform declaration must be an object.")
        return cls(
            transform_id=value.get("transform_id"),
            version=value.get("version"),
            kind=value.get("kind"),
            parameters=value.get("parameters", {}),
            executable=value.get("executable", False),
            notes=value.get("notes", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "transform_id": self.transform_id,
            "version": self.version,
            "kind": self.kind.value,
            "parameters": {key: value for key, value in self.parameters},
            "executable": self.executable,
            "notes": self.notes,
        }

    @property
    def identity(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True, slots=True)
class PayloadReference:
    """A checked reference to a future external numerical payload.

    This object never embeds the numerical payload.  Paths are project-relative
    and are rejected when they can escape the supplied verification root.
    """

    artifact_id: str
    relative_path: str
    sha256: str
    received_at_utc: str
    original_filename: str
    format: str
    parser_schema_id: str
    source_contact_ref: str

    def __post_init__(self) -> None:
        values = {
            "artifact_id": self.artifact_id,
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "received_at_utc": self.received_at_utc,
            "original_filename": self.original_filename,
            "format": self.format,
            "parser_schema_id": self.parser_schema_id,
            "source_contact_ref": self.source_contact_ref,
        }
        for field_name, value in values.items():
            object.__setattr__(self, field_name, _required_string(value, field_name))
        path = Path(self.relative_path)
        if path.is_absolute() or ".." in path.parts:
            raise EmpiricalConstraintError(
                "Payload relative_path must not be absolute or traverse "
                "parent directories."
            )
        if len(self.sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.sha256.lower()
        ):
            raise EmpiricalConstraintError(
                "Payload sha256 must be a 64-character hex digest."
            )
        _iso_datetime(self.received_at_utc, "received_at_utc")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PayloadReference:
        if not isinstance(value, Mapping):
            raise EmpiricalConstraintError("payload_reference must be an object.")
        return cls(
            artifact_id=value.get("artifact_id"),
            relative_path=value.get("relative_path"),
            sha256=value.get("sha256"),
            received_at_utc=value.get("received_at_utc"),
            original_filename=value.get("original_filename"),
            format=value.get("format"),
            parser_schema_id=value.get("parser_schema_id"),
            source_contact_ref=value.get("source_contact_ref"),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "artifact_id": self.artifact_id,
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "received_at_utc": self.received_at_utc,
            "original_filename": self.original_filename,
            "format": self.format,
            "parser_schema_id": self.parser_schema_id,
            "source_contact_ref": self.source_contact_ref,
        }

    def verify(self, root: Path) -> bool:
        """Verify the referenced local file without downloading or mutating it."""
        root = Path(root).resolve()
        path = (root / self.relative_path).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise EmpiricalConstraintError(
                "Payload path escapes verification root."
            ) from exc
        if not path.is_file():
            raise EmpiricalConstraintError(
                f"Payload file does not exist: {self.relative_path}"
            )
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != self.sha256.lower():
            raise EmpiricalConstraintError(
                f"Payload SHA-256 mismatch for artifact {self.artifact_id!r}."
            )
        return True


@dataclass(frozen=True, slots=True)
class EmpiricalConstraint:
    """Immutable metadata for one pre-registered empirical constraint."""

    constraint_id: str
    protocol_version: str
    citation: str
    doi: str
    publication_year: int
    source_location: str
    experimental_population: str
    pathway_condition: str
    stimulus_description: str
    measurement_modality: MeasurementModality
    units: str
    source_time_reference: str
    source_normalization: str
    role: ConstraintRole
    availability: AvailabilityStatus
    comparability: ComparabilityStatus
    reuse_status: ReuseStatus
    uncertainty: str
    sample_size: str
    neurofly_observable: str
    limitations: str
    qualitative_relation: str | None = None
    payload_reference: PayloadReference | None = None
    observation_transforms: tuple[ObservationTransformSpec, ...] = ()

    def __post_init__(self) -> None:
        string_fields = (
            "constraint_id",
            "protocol_version",
            "citation",
            "doi",
            "source_location",
            "experimental_population",
            "pathway_condition",
            "stimulus_description",
            "units",
            "source_time_reference",
            "source_normalization",
            "uncertainty",
            "sample_size",
            "neurofly_observable",
            "limitations",
        )
        for field_name in string_fields:
            object.__setattr__(
                self,
                field_name,
                _required_string(getattr(self, field_name), field_name),
            )
        if not self.doi.startswith("10.") or any(
            character.isspace() for character in self.doi
        ):
            raise EmpiricalConstraintError(
                "doi must be a DOI string beginning with '10.'."
            )
        if not isinstance(self.publication_year, int) or isinstance(
            self.publication_year, bool
        ):
            raise EmpiricalConstraintError("publication_year must be an integer.")
        if self.publication_year < 1900 or self.publication_year > 2100:
            raise EmpiricalConstraintError(
                "publication_year is outside the supported range."
            )
        for field_name, enum_type in (
            ("measurement_modality", MeasurementModality),
            ("role", ConstraintRole),
            ("availability", AvailabilityStatus),
            ("comparability", ComparabilityStatus),
            ("reuse_status", ReuseStatus),
        ):
            object.__setattr__(
                self,
                field_name,
                _enum(getattr(self, field_name), enum_type, field_name),
            )
        if self.measurement_modality is MeasurementModality.QUALITATIVE_RESPONSE:
            if self.units != "qualitative":
                raise EmpiricalConstraintError(
                    "QUALITATIVE_RESPONSE records must use qualitative units."
                )
        if self.measurement_modality is MeasurementModality.CALCIUM_DFF:
            if self.units.lower() in {"mv", "mveq"}:
                raise EmpiricalConstraintError(
                    "CALCIUM_DFF cannot be represented with voltage units."
                )
        if self.qualitative_relation is not None:
            object.__setattr__(
                self,
                "qualitative_relation",
                _required_string(self.qualitative_relation, "qualitative_relation"),
            )
        if self.role is ConstraintRole.QUALITATIVE_VALIDATION:
            if self.comparability is not ComparabilityStatus.QUALITATIVE_ONLY:
                raise EmpiricalConstraintError(
                    "QUALITATIVE_VALIDATION must use QUALITATIVE_ONLY comparability."
                )
            if self.qualitative_relation is None:
                raise EmpiricalConstraintError(
                    "QUALITATIVE_VALIDATION requires qualitative_relation."
                )
        if self.role is ConstraintRole.NOT_DIRECTLY_COMPARABLE:
            if self.comparability is not ComparabilityStatus.NOT_DIRECTLY_COMPARABLE:
                raise EmpiricalConstraintError(
                    "NOT_DIRECTLY_COMPARABLE role requires matching comparability."
                )
        if self.availability is AvailabilityStatus.FIGURE_ONLY_NOT_EXTRACTED:
            if self.payload_reference is not None:
                raise EmpiricalConstraintError(
                    "Figure-only constraints cannot carry a numerical payload "
                    "reference."
                )
        if self.availability is AvailabilityStatus.PENDING_SOURCE_DATA:
            if self.payload_reference is not None:
                raise EmpiricalConstraintError(
                    "PENDING_SOURCE_DATA cannot carry a numerical payload reference."
                )
        if self.availability is AvailabilityStatus.PENDING_REVIEW:
            if self.payload_reference is None:
                raise EmpiricalConstraintError(
                    "PENDING_REVIEW requires a received payload reference."
                )
        if (
            self.availability
            in (
                AvailabilityStatus.UNAVAILABLE,
                AvailabilityStatus.WITHDRAWN_OR_UNUSABLE,
            )
            and self.payload_reference is not None
        ):
            raise EmpiricalConstraintError(
                "Unavailable or withdrawn constraints cannot carry a payload reference."
            )
        if (
            self.payload_reference is not None
            and self.reuse_status is ReuseStatus.PROHIBITED
        ):
            raise EmpiricalConstraintError(
                "Prohibited payloads cannot be registered for use."
            )
        if self.availability is AvailabilityStatus.AVAILABLE_VERIFIED:
            if self.role in (
                ConstraintRole.FIT_CONSTRAINT,
                ConstraintRole.HELD_OUT_VALIDATION,
            ):
                if self.payload_reference is None:
                    raise EmpiricalConstraintError(
                        "Verified numeric fit/held-out data require a payload "
                        "reference."
                    )
                if self.reuse_status not in (
                    ReuseStatus.PERMITTED,
                    ReuseStatus.RESTRICTED,
                ):
                    raise EmpiricalConstraintError(
                        "Verified numeric data require permitted or restricted "
                        "reuse status."
                    )
        if not isinstance(self.observation_transforms, tuple):
            transforms = tuple(self.observation_transforms)  # type: ignore[arg-type]
        else:
            transforms = self.observation_transforms
        normalized_transforms = tuple(
            transform
            if isinstance(transform, ObservationTransformSpec)
            else ObservationTransformSpec.from_mapping(transform)
            for transform in transforms
        )
        transform_ids = [transform.transform_id for transform in normalized_transforms]
        if len(transform_ids) != len(set(transform_ids)):
            raise EmpiricalConstraintError(
                f"Constraint {self.constraint_id!r} has duplicate transform IDs."
            )
        object.__setattr__(self, "observation_transforms", normalized_transforms)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> EmpiricalConstraint:
        if not isinstance(value, Mapping):
            raise EmpiricalConstraintError("Constraint record must be an object.")
        payload = value.get("payload_reference")
        transforms = value.get("observation_transforms", ())
        return cls(
            constraint_id=value.get("constraint_id"),
            protocol_version=value.get("protocol_version"),
            citation=value.get("citation"),
            doi=value.get("doi"),
            publication_year=value.get("publication_year"),
            source_location=value.get("source_location"),
            experimental_population=value.get("experimental_population"),
            pathway_condition=value.get("pathway_condition"),
            stimulus_description=value.get("stimulus_description"),
            measurement_modality=value.get("measurement_modality"),
            units=value.get("units"),
            source_time_reference=value.get("source_time_reference"),
            source_normalization=value.get("source_normalization"),
            role=value.get("role"),
            availability=value.get("availability"),
            comparability=value.get("comparability"),
            reuse_status=value.get("reuse_status"),
            uncertainty=value.get("uncertainty"),
            sample_size=value.get("sample_size"),
            neurofly_observable=value.get("neurofly_observable"),
            limitations=value.get("limitations"),
            qualitative_relation=value.get("qualitative_relation"),
            payload_reference=(
                None if payload is None else PayloadReference.from_mapping(payload)
            ),
            observation_transforms=tuple(
                ObservationTransformSpec.from_mapping(transform)
                for transform in transforms
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "protocol_version": self.protocol_version,
            "citation": self.citation,
            "doi": self.doi,
            "publication_year": self.publication_year,
            "source_location": self.source_location,
            "experimental_population": self.experimental_population,
            "pathway_condition": self.pathway_condition,
            "stimulus_description": self.stimulus_description,
            "measurement_modality": self.measurement_modality.value,
            "units": self.units,
            "source_time_reference": self.source_time_reference,
            "source_normalization": self.source_normalization,
            "role": self.role.value,
            "availability": self.availability.value,
            "comparability": self.comparability.value,
            "reuse_status": self.reuse_status.value,
            "uncertainty": self.uncertainty,
            "sample_size": self.sample_size,
            "neurofly_observable": self.neurofly_observable,
            "limitations": self.limitations,
            "qualitative_relation": self.qualitative_relation,
            "payload_reference": (
                None
                if self.payload_reference is None
                else self.payload_reference.to_dict()
            ),
            "observation_transforms": [
                transform.to_dict() for transform in self.observation_transforms
            ],
        }

    def is_comparison_ready(self, payload_root: Path | None = None) -> bool:
        """Return whether this record can enter its pre-registered comparison."""
        if self.role in (
            ConstraintRole.CONTEXT_ONLY,
            ConstraintRole.NOT_DIRECTLY_COMPARABLE,
        ):
            return False
        if self.role is ConstraintRole.QUALITATIVE_VALIDATION:
            return (
                self.comparability is ComparabilityStatus.QUALITATIVE_ONLY
                and self.qualitative_relation is not None
                and self.availability
                in (
                    AvailabilityStatus.FIGURE_ONLY_NOT_EXTRACTED,
                    AvailabilityStatus.AVAILABLE_VERIFIED,
                )
            )
        if self.availability is not AvailabilityStatus.AVAILABLE_VERIFIED:
            return False
        if self.payload_reference is None:
            return False
        if self.reuse_status not in (ReuseStatus.PERMITTED, ReuseStatus.RESTRICTED):
            return False
        if self.comparability in (
            ComparabilityStatus.NOT_DIRECTLY_COMPARABLE,
            ComparabilityStatus.QUALITATIVE_ONLY,
        ):
            return False
        if payload_root is None:
            return False
        try:
            self.payload_reference.verify(payload_root)
        except EmpiricalConstraintError:
            return False
        return True

    def is_redistribution_ready(self, payload_root: Path | None = None) -> bool:
        return (
            self.is_comparison_ready(payload_root)
            and self.reuse_status is ReuseStatus.PERMITTED
        )


@dataclass(frozen=True, slots=True)
class ValidationProtocol:
    """Locked fit/held-out partition and transform identity."""

    protocol_id: str
    protocol_version: str
    fit_constraint_ids: tuple[str, ...]
    held_out_validation_ids: tuple[str, ...]
    qualitative_validation_ids: tuple[str, ...]
    context_only_ids: tuple[str, ...]
    not_directly_comparable_ids: tuple[str, ...]
    constraint_roles: tuple[tuple[str, str], ...]
    transform_identities: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "protocol_id", _required_string(self.protocol_id, "protocol_id")
        )
        object.__setattr__(
            self,
            "protocol_version",
            _required_string(self.protocol_version, "protocol_version"),
        )
        groups = (
            self.fit_constraint_ids,
            self.held_out_validation_ids,
            self.qualitative_validation_ids,
            self.context_only_ids,
            self.not_directly_comparable_ids,
        )
        normalized_groups = tuple(
            tuple(sorted(_required_string(item, "constraint ID") for item in group))
            for group in groups
        )
        all_ids = [item for group in normalized_groups for item in group]
        if len(all_ids) != len(set(all_ids)):
            raise ConstraintRegistryError(
                "Validation protocol partition groups overlap."
            )
        object.__setattr__(self, "fit_constraint_ids", normalized_groups[0])
        object.__setattr__(self, "held_out_validation_ids", normalized_groups[1])
        object.__setattr__(self, "qualitative_validation_ids", normalized_groups[2])
        object.__setattr__(self, "context_only_ids", normalized_groups[3])
        object.__setattr__(self, "not_directly_comparable_ids", normalized_groups[4])
        roles = tuple(
            sorted(
                (
                    _required_string(identifier, "constraint role ID"),
                    _enum(role, ConstraintRole, "constraint role").value,
                )
                for identifier, role in self.constraint_roles
            )
        )
        if len({identifier for identifier, _ in roles}) != len(roles):
            raise ConstraintRegistryError("Validation protocol has duplicate role IDs.")
        transforms = tuple(
            sorted(
                (
                    _required_string(identifier, "transform constraint ID"),
                    _required_string(identity, "transform identity"),
                )
                for identifier, identity in self.transform_identities
            )
        )
        object.__setattr__(self, "constraint_roles", roles)
        object.__setattr__(self, "transform_identities", transforms)

    @classmethod
    def from_constraints(
        cls,
        constraints: Sequence[EmpiricalConstraint],
        *,
        protocol_id: str = PROTOCOL_ID,
        protocol_version: str = PROTOCOL_VERSION,
    ) -> ValidationProtocol:
        by_role: dict[ConstraintRole, list[str]] = {role: [] for role in ConstraintRole}
        roles: list[tuple[str, str]] = []
        transforms: list[tuple[str, str]] = []
        for constraint in constraints:
            by_role[constraint.role].append(constraint.constraint_id)
            roles.append((constraint.constraint_id, constraint.role.value))
            for transform in constraint.observation_transforms:
                transforms.append((constraint.constraint_id, transform.identity))
        return cls(
            protocol_id=protocol_id,
            protocol_version=protocol_version,
            fit_constraint_ids=tuple(by_role[ConstraintRole.FIT_CONSTRAINT]),
            held_out_validation_ids=tuple(by_role[ConstraintRole.HELD_OUT_VALIDATION]),
            qualitative_validation_ids=tuple(
                by_role[ConstraintRole.QUALITATIVE_VALIDATION]
            ),
            context_only_ids=tuple(by_role[ConstraintRole.CONTEXT_ONLY]),
            not_directly_comparable_ids=tuple(
                by_role[ConstraintRole.NOT_DIRECTLY_COMPARABLE]
            ),
            constraint_roles=tuple(roles),
            transform_identities=tuple(transforms),
        )

    @property
    def sha256(self) -> str:
        return _sha256_json(self.canonical_dict())

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "protocol_id": self.protocol_id,
            "protocol_version": self.protocol_version,
            "fit_constraint_ids": list(self.fit_constraint_ids),
            "held_out_validation_ids": list(self.held_out_validation_ids),
            "qualitative_validation_ids": list(self.qualitative_validation_ids),
            "context_only_ids": list(self.context_only_ids),
            "not_directly_comparable_ids": list(self.not_directly_comparable_ids),
            "constraint_roles": [list(item) for item in self.constraint_roles],
            "transform_identities": [list(item) for item in self.transform_identities],
        }

    def to_dict(self) -> dict[str, Any]:
        result = self.canonical_dict()
        result["protocol_sha256"] = self.sha256
        return result

    def validate_constraints(self, constraints: Sequence[EmpiricalConstraint]) -> None:
        expected = ValidationProtocol.from_constraints(
            constraints,
            protocol_id=self.protocol_id,
            protocol_version=self.protocol_version,
        )
        if expected.canonical_dict() != self.canonical_dict():
            raise ConstraintRegistryError(
                "Registry records do not match the locked validation protocol "
                "partition."
            )


@dataclass(frozen=True, slots=True)
class ConstraintRegistry:
    """Deterministically ordered immutable registry of constraint metadata."""

    schema_version: str
    protocol: ValidationProtocol
    constraints: tuple[EmpiricalConstraint, ...]
    strict_phase2g: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ConstraintRegistryError(
                f"Unsupported registry schema {self.schema_version!r}."
            )
        constraints = tuple(
            sorted(self.constraints, key=lambda item: item.constraint_id)
        )
        identifiers = [constraint.constraint_id for constraint in constraints]
        if not identifiers or len(identifiers) != len(set(identifiers)):
            raise ConstraintRegistryError(
                "Constraint IDs must be non-empty and unique."
            )
        if any(
            constraint.protocol_version != self.protocol.protocol_version
            for constraint in constraints
        ):
            raise ConstraintRegistryError(
                "Constraint protocol versions do not match registry."
            )
        self.protocol.validate_constraints(constraints)
        if self.strict_phase2g:
            _validate_phase2g_inventory(constraints, self.protocol)
        object.__setattr__(self, "constraints", constraints)

    @classmethod
    def from_constraints(
        cls,
        constraints: Sequence[EmpiricalConstraint],
        *,
        schema_version: str = SCHEMA_VERSION,
        protocol_id: str = PROTOCOL_ID,
        protocol_version: str = PROTOCOL_VERSION,
        strict_phase2g: bool = False,
    ) -> ConstraintRegistry:
        records = tuple(constraints)
        return cls(
            schema_version=schema_version,
            protocol=ValidationProtocol.from_constraints(
                records,
                protocol_id=protocol_id,
                protocol_version=protocol_version,
            ),
            constraints=records,
            strict_phase2g=strict_phase2g,
        )

    @classmethod
    def from_mapping(
        cls, value: Mapping[str, Any], *, strict_phase2g: bool = True
    ) -> ConstraintRegistry:
        if not isinstance(value, Mapping):
            raise ConstraintRegistryError("Registry root must be an object.")
        if value.get("schema_version") != SCHEMA_VERSION:
            raise ConstraintRegistryError("Registry schema_version is unsupported.")
        raw_protocol = value.get("protocol")
        raw_constraints = value.get("constraints")
        if not isinstance(raw_protocol, Mapping) or not isinstance(
            raw_constraints, list
        ):
            raise ConstraintRegistryError("Registry requires protocol and constraints.")
        records = tuple(
            EmpiricalConstraint.from_mapping(item) for item in raw_constraints
        )
        protocol = _protocol_from_mapping(raw_protocol)
        registry = cls(
            schema_version=SCHEMA_VERSION,
            protocol=protocol,
            constraints=records,
            strict_phase2g=strict_phase2g,
        )
        supplied_protocol_hash = raw_protocol.get("protocol_sha256")
        if supplied_protocol_hash != protocol.sha256:
            raise ConstraintRegistryError(
                "Protocol SHA-256 does not match canonical metadata."
            )
        supplied_registry_hash = value.get("registry_sha256")
        if supplied_registry_hash != registry.sha256:
            raise ConstraintRegistryError(
                "Registry SHA-256 does not match canonical metadata."
            )
        return registry

    @classmethod
    def load(cls, path: Path = DEFAULT_REGISTRY_PATH) -> ConstraintRegistry:
        path = Path(path)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ConstraintRegistryError(f"Unable to read registry {path}.") from exc
        except json.JSONDecodeError as exc:
            raise ConstraintRegistryError(f"Malformed registry JSON {path}.") from exc
        return cls.from_mapping(value, strict_phase2g=True)

    @property
    def sha256(self) -> str:
        return _sha256_json(self.canonical_dict())

    @property
    def protocol_sha256(self) -> str:
        return self.protocol.sha256

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "protocol": self.protocol.canonical_dict(),
            "constraints": [constraint.to_dict() for constraint in self.constraints],
        }

    def to_dict(self) -> dict[str, Any]:
        result = self.canonical_dict()
        protocol = dict(self.protocol.to_dict())
        result["protocol"] = protocol
        result["registry_sha256"] = self.sha256
        return result

    def get(self, constraint_id: str) -> EmpiricalConstraint:
        for constraint in self.constraints:
            if constraint.constraint_id == constraint_id:
                return constraint
        raise KeyError(constraint_id)

    def summary(self) -> dict[str, Any]:
        by_role = Counter(constraint.role.value for constraint in self.constraints)
        by_availability = Counter(
            constraint.availability.value for constraint in self.constraints
        )
        by_modality = Counter(
            constraint.measurement_modality.value for constraint in self.constraints
        )
        ready = [
            constraint.constraint_id
            for constraint in self.constraints
            if constraint.is_comparison_ready()
        ]
        return {
            "schema_version": self.schema_version,
            "protocol_id": self.protocol.protocol_id,
            "protocol_version": self.protocol.protocol_version,
            "protocol_sha256": self.protocol_sha256,
            "registry_sha256": self.sha256,
            "constraint_count": len(self.constraints),
            "by_role": dict(sorted(by_role.items())),
            "by_availability": dict(sorted(by_availability.items())),
            "by_modality": dict(sorted(by_modality.items())),
            "comparison_ready_count": len(ready),
            "comparison_ready_ids": ready,
            "pending_source_ids": [
                constraint.constraint_id
                for constraint in self.constraints
                if constraint.availability is AvailabilityStatus.PENDING_SOURCE_DATA
            ],
        }


def _protocol_from_mapping(value: Mapping[str, Any]) -> ValidationProtocol:
    required_groups = (
        "fit_constraint_ids",
        "held_out_validation_ids",
        "qualitative_validation_ids",
        "context_only_ids",
        "not_directly_comparable_ids",
        "constraint_roles",
        "transform_identities",
    )
    for key in required_groups:
        if key not in value or not isinstance(value[key], list):
            raise ConstraintRegistryError(f"Protocol field {key!r} must be a list.")
    try:
        protocol = ValidationProtocol(
            protocol_id=value.get("protocol_id"),
            protocol_version=value.get("protocol_version"),
            fit_constraint_ids=tuple(value["fit_constraint_ids"]),
            held_out_validation_ids=tuple(value["held_out_validation_ids"]),
            qualitative_validation_ids=tuple(value["qualitative_validation_ids"]),
            context_only_ids=tuple(value["context_only_ids"]),
            not_directly_comparable_ids=tuple(value["not_directly_comparable_ids"]),
            constraint_roles=tuple(tuple(item) for item in value["constraint_roles"]),
            transform_identities=tuple(
                tuple(item) for item in value["transform_identities"]
            ),
        )
    except (TypeError, ValueError) as exc:
        raise ConstraintRegistryError("Malformed validation protocol.") from exc
    return protocol


_PHASE2G_ROLE_BY_ID: dict[str, ConstraintRole] = {
    "ACHE19_LC4_GF_ISOLATED_WAVEFORM": ConstraintRole.FIT_CONSTRAINT,
    "ACHE19_LPLC2_GF_ISOLATED_WAVEFORM": ConstraintRole.FIT_CONSTRAINT,
    "ACHE19_ISOLATED_PEAK_TIMING": ConstraintRole.HELD_OUT_VALIDATION,
    "ACHE19_COMBINED_GF_WAVEFORM": ConstraintRole.HELD_OUT_VALIDATION,
    "ACHE19_WEIGHTED_COMPONENT_MODEL": ConstraintRole.CONTEXT_ONLY,
    "ACHE19_TRANSIENT_LATENCY_19MS": ConstraintRole.NOT_DIRECTLY_COMPARABLE,
    "KLAP17_LPLC2_DARK_LOOM_SPEED_SERIES": ConstraintRole.FIT_CONSTRAINT,
    "KLAP17_LPLC2_EARLY_EXPANSION": ConstraintRole.QUALITATIVE_VALIDATION,
    "KLAP17_LPLC2_RECEDING_NULL": ConstraintRole.QUALITATIVE_VALIDATION,
    "KLAP17_LPLC2_CONTRACTION_NULL": ConstraintRole.QUALITATIVE_VALIDATION,
    "KLAP17_LPLC2_DARKENING_NULL": ConstraintRole.NOT_DIRECTLY_COMPARABLE,
    "KLAP17_LPLC2_TRANSLATION_NULL": ConstraintRole.NOT_DIRECTLY_COMPARABLE,
    "VREYN14_GF_FIRST_SPIKE": ConstraintRole.HELD_OUT_VALIDATION,
    "VREYN14_GF_TO_MOTOR_LATENCY": ConstraintRole.CONTEXT_ONLY,
}


def _validate_phase2g_inventory(
    constraints: Sequence[EmpiricalConstraint], protocol: ValidationProtocol
) -> None:
    actual = {constraint.constraint_id: constraint.role for constraint in constraints}
    if actual != _PHASE2G_ROLE_BY_ID:
        missing = sorted(set(_PHASE2G_ROLE_BY_ID) - set(actual))
        extra = sorted(set(actual) - set(_PHASE2G_ROLE_BY_ID))
        raise ConstraintRegistryError(
            f"Phase 2G inventory mismatch; missing={missing}, extra={extra}."
        )
    for identifier, expected_role in _PHASE2G_ROLE_BY_ID.items():
        if actual[identifier] is not expected_role:
            raise ConstraintRegistryError(
                f"Phase 2G role changed for {identifier}: "
                f"expected {expected_role.value}, got {actual[identifier].value}."
            )
    expected_protocol = ValidationProtocol.from_constraints(
        constraints,
        protocol_id=PROTOCOL_ID,
        protocol_version=PROTOCOL_VERSION,
    )
    if protocol.canonical_dict() != expected_protocol.canonical_dict():
        raise ConstraintRegistryError(
            "Phase 2G protocol partition is not the locked partition."
        )


def is_comparison_ready(
    constraint: EmpiricalConstraint, payload_root: Path | None = None
) -> bool:
    """Small comparison gate; this is not a fitting API."""
    return constraint.is_comparison_ready(payload_root)


def inspect_registry(path: Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    """Load and summarize the metadata registry without network access."""
    return ConstraintRegistry.load(path).summary()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NeuroFly empirical metadata tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser(
        "inspect", help="inspect the metadata registry offline"
    )
    inspect.add_argument("path", type=Path, nargs="?", default=DEFAULT_REGISTRY_PATH)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect":
            summary = inspect_registry(args.path)
            print(
                f"schema={summary['schema_version']} "
                f"protocol={summary['protocol_id']}:{summary['protocol_version']}"
            )
            print(
                f"constraints={summary['constraint_count']} "
                f"comparison_ready={summary['comparison_ready_count']}"
            )
            print(f"protocol_sha256={summary['protocol_sha256']}")
            print(f"registry_sha256={summary['registry_sha256']}")
            print(f"by_role={summary['by_role']}")
            print(f"by_availability={summary['by_availability']}")
            print(f"by_modality={summary['by_modality']}")
            print(f"pending_source={summary['pending_source_ids']}")
            return 0
    except EmpiricalConstraintError as error:
        print(f"error: {error}")
        return 1
    raise RuntimeError(f"Unsupported command {args.command!r}.")


if __name__ == "__main__":
    raise SystemExit(main())
