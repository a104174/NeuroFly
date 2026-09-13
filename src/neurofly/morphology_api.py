"""Read-only application boundary for validated MaleCNS morphology artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.malecns.errors import (
    MorphologyArtifactError,
    MorphologyArtifactIntegrityError,
    MorphologyArtifactSchemaError,
)
from neurofly.malecns.morphology_artifacts import (
    MORPHOLOGY_ARTIFACT_SCHEMA_VERSION,
    LoadedMorphologyArtifact,
    MorphologyBodyRecord,
    load_morphology_artifact,
)

MORPHOLOGY_API_SCHEMA_VERSION = "morphology_api_v1"
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class MorphologyApiError(RuntimeError):
    """Base error for the morphology application boundary."""


class MorphologyStoreUnavailableError(MorphologyApiError):
    """No explicit morphology artifact root was configured."""


class MorphologyStoreError(MorphologyApiError):
    """The configured morphology store could not be read."""


class InvalidMorphologyArtifactIdError(MorphologyApiError):
    """A caller supplied a non-canonical morphology identity."""


class MorphologyArtifactNotFoundError(MorphologyApiError):
    """No requested morphology artifact exists under the configured root."""


class MorphologyBodyNotFoundError(MorphologyApiError):
    """The requested body is absent from a morphology artifact."""


class MorphologyPathError(MorphologyApiError):
    """A morphology store entry violates path-containment policy."""


class CorruptedMorphologyArtifactError(MorphologyApiError):
    """A morphology artifact failed integrity validation."""


class UnsupportedMorphologyArtifactError(MorphologyApiError):
    """A morphology artifact uses an unsupported schema."""


def _bounds(body: MorphologyBodyRecord) -> dict[str, list[float]]:
    nodes = [
        node for component in body.spatial_record.components for node in component.nodes
    ]
    return {
        "minimum": [
            min(node.location.x for node in nodes),
            min(node.location.y for node in nodes),
            min(node.location.z for node in nodes),
        ],
        "maximum": [
            max(node.location.x for node in nodes),
            max(node.location.y for node in nodes),
            max(node.location.z for node in nodes),
        ],
    }


def _body_summary(body: MorphologyBodyRecord) -> dict[str, Any]:
    record = body.spatial_record
    return {
        "body_id": record.body_id,
        "node_index": record.node_index,
        "neuron_type": record.neuron_type,
        "source_side": record.side,
        "source_status": body.source_status,
        "morphology_mode": record.morphology_mode.value,
        "node_count": sum(len(component.nodes) for component in record.components),
        "link_count": sum(len(component.links) for component in record.components),
        "component_count": record.component_count,
        "source_bounds": _bounds(body),
        "source_swc_sha256": record.source_swc_sha256,
        "spatial_record_id": record.spatial_record_id,
    }


@dataclass(frozen=True, slots=True)
class MorphologyArtifactSummary:
    """Small JSON-safe metadata view without dense skeleton payloads."""

    artifact: LoadedMorphologyArtifact

    def to_dict(self) -> dict[str, Any]:
        first = self.artifact.bodies[0].spatial_record
        return {
            "schema": MORPHOLOGY_API_SCHEMA_VERSION,
            "kind": "morphology_artifact_summary",
            "artifact_id": self.artifact.artifact_id,
            "artifact_schema_version": MORPHOLOGY_ARTIFACT_SCHEMA_VERSION,
            "dataset": first.dataset_id,
            "candidate": {
                "identifier": first.candidate_id,
                "version": first.candidate_version,
            },
            "coordinate_frame_id": first.coordinate_frame_id,
            "coordinate_unit": first.coordinate_unit,
            "morphology_mode": first.morphology_mode.value,
            "body_ids": [body.spatial_record.body_id for body in self.artifact.bodies],
            "bodies": [_body_summary(body) for body in self.artifact.bodies],
            "generation": {
                "generated_at_utc": self.artifact.generated_at_utc,
                "neuprint_python_version": self.artifact.neuprint_python_version,
                "source_endpoint": self.artifact.source_endpoint,
                "source_mode": self.artifact.source_mode,
                "source_urls": {
                    str(body_id): url for body_id, url in self.artifact.source_urls
                },
                "retrieval": self.artifact.retrieval,
            },
        }


@dataclass(frozen=True, slots=True)
class MorphologyBodyView:
    """One full raw skeleton body as JSON-native source coordinates."""

    artifact_id: str
    body: MorphologyBodyRecord

    def to_dict(self) -> dict[str, Any]:
        record = self.body.spatial_record
        summary = _body_summary(self.body)
        return {
            "schema": MORPHOLOGY_API_SCHEMA_VERSION,
            "kind": "morphology_body",
            "artifact_id": self.artifact_id,
            "artifact_schema_version": MORPHOLOGY_ARTIFACT_SCHEMA_VERSION,
            "dataset": record.dataset_id,
            "candidate": {
                "identifier": record.candidate_id,
                "version": record.candidate_version,
            },
            **summary,
            "source_category": record.source_category.value,
            "morphology_source": record.morphology_source,
            "coordinate_frame_id": record.coordinate_frame_id,
            "coordinate_unit": record.coordinate_unit,
            "soma_location": (
                None if record.soma_location is None else record.soma_location.to_dict()
            ),
            "components": [component.to_dict() for component in record.components],
        }


def _load_error(error: MorphologyArtifactError) -> MorphologyApiError:
    if (
        isinstance(error, MorphologyArtifactSchemaError)
        and "unsupported" in str(error).lower()
    ):
        return UnsupportedMorphologyArtifactError(str(error))
    if isinstance(
        error, (MorphologyArtifactIntegrityError, MorphologyArtifactSchemaError)
    ):
        return CorruptedMorphologyArtifactError(str(error))
    return CorruptedMorphologyArtifactError(str(error))


class MorphologyArtifactStore:
    """Strict read-only discovery below one explicit morphology root."""

    def __init__(self, root: str | Path) -> None:
        configured = Path(root)
        if not configured.exists() or not configured.is_dir():
            raise MorphologyStoreError("morphology root is not a directory")
        self._root = configured.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def _children(self) -> tuple[Path, ...]:
        try:
            entries = tuple(sorted(self._root.iterdir(), key=lambda item: item.name))
        except OSError as exc:
            raise MorphologyStoreError("could not enumerate morphology root") from exc
        children = []
        for entry in entries:
            if entry.is_symlink():
                raise MorphologyPathError("symlink morphology entries are forbidden")
            if not entry.is_dir() or entry.name.startswith("."):
                continue
            try:
                entry.resolve().relative_to(self._root)
            except ValueError:
                raise MorphologyPathError("morphology entry escapes configured root")
            children.append(entry)
        return tuple(children)

    def _load(self, path: Path) -> LoadedMorphologyArtifact:
        try:
            if any(entry.is_symlink() for entry in path.rglob("*")):
                raise MorphologyPathError(
                    "symlinks inside morphology artifacts are forbidden"
                )
            return load_morphology_artifact(path)
        except MorphologyApiError:
            raise
        except MorphologyArtifactError as exc:
            raise _load_error(exc) from exc
        except OSError as exc:
            raise MorphologyStoreError("could not inspect morphology artifact") from exc

    def _all_loaded(self) -> tuple[LoadedMorphologyArtifact, ...]:
        loaded = tuple(self._load(path) for path in self._children())
        identities = [item.artifact_id for item in loaded]
        if len(identities) != len(set(identities)):
            raise MorphologyStoreError("duplicate morphology artifact identity")
        return tuple(sorted(loaded, key=lambda item: item.artifact_id))

    @staticmethod
    def _validate_id(artifact_id: str) -> str:
        if (
            not isinstance(artifact_id, str)
            or _SHA256_RE.fullmatch(artifact_id) is None
        ):
            raise InvalidMorphologyArtifactIdError(
                "morphology artifact ID must be a lowercase SHA-256"
            )
        return artifact_id

    def list_artifacts(self) -> tuple[MorphologyArtifactSummary, ...]:
        return tuple(MorphologyArtifactSummary(item) for item in self._all_loaded())

    def get_artifact(self, artifact_id: str) -> MorphologyArtifactSummary:
        identity = self._validate_id(artifact_id)
        for artifact in self._all_loaded():
            if artifact.artifact_id == identity:
                return MorphologyArtifactSummary(artifact)
        raise MorphologyArtifactNotFoundError("morphology artifact not found")

    def get_body(self, artifact_id: str, body_id: int) -> MorphologyBodyView:
        identity = self._validate_id(artifact_id)
        if isinstance(body_id, bool) or not isinstance(body_id, int):
            raise MorphologyBodyNotFoundError("morphology body ID must be an integer")
        for artifact in self._all_loaded():
            if artifact.artifact_id == identity:
                body = artifact.bodies_by_id.get(body_id)
                if body is None:
                    raise MorphologyBodyNotFoundError("morphology body not found")
                return MorphologyBodyView(identity, body)
        raise MorphologyArtifactNotFoundError("morphology artifact not found")


__all__ = [
    "MORPHOLOGY_API_SCHEMA_VERSION",
    "CorruptedMorphologyArtifactError",
    "InvalidMorphologyArtifactIdError",
    "MorphologyApiError",
    "MorphologyArtifactNotFoundError",
    "MorphologyArtifactStore",
    "MorphologyArtifactSummary",
    "MorphologyBodyNotFoundError",
    "MorphologyBodyView",
    "MorphologyPathError",
    "MorphologyStoreError",
    "MorphologyStoreUnavailableError",
    "UnsupportedMorphologyArtifactError",
]
