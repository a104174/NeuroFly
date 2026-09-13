"""Model-neutral contracts for preserving MaleCNS skeleton coordinates.

This module defines a future morphology boundary.  It does not fetch, heal,
transform, or render skeletons.
"""

import hashlib
import json
import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Integral, Real
from typing import TYPE_CHECKING, Any

from neurofly.malecns.errors import MaleCNSValidationError
from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET

if TYPE_CHECKING:
    from neurofly.malecns.contract import CircuitContract

SPATIAL_SCHEMA_VERSION = "malecns_neuron_spatial_v1"
MALECNS_EM_COORDINATE_FRAME = "male_cns_v1_em_native_voxels"
MALECNS_EM_COORDINATE_UNIT = "8_nm_voxel"
MALECNS_NEUPRINT_SKELETON_SOURCE = "JANELIA_NEUPRINT_MALECNS_SKELETON"


class SpatialEvidenceCategory(StrEnum):
    """Provenance category; categories must never be silently promoted."""

    MALECNS_DIRECT_DATA = "MALECNS_DIRECT_DATA"
    PUBLISHED_DERIVED_EVIDENCE = "PUBLISHED_DERIVED_EVIDENCE"
    NEUROFLY_PRESENTATION_MAPPING = "NEUROFLY_PRESENTATION_MAPPING"
    NEUROFLY_MODELLING_ASSUMPTION = "NEUROFLY_MODELLING_ASSUMPTION"


class MorphologyMode(StrEnum):
    """Whether component linkage is raw or may contain explicit repairs."""

    RAW = "RAW"
    HEALED = "HEALED"


class SkeletonLinkProvenance(StrEnum):
    """Provenance of a tree edge, never biological signal direction."""

    RAW = "MALECNS_RAW_SKELETON_LINK"
    ARTIFICIAL_REPAIR = "NEUROFLY_ARTIFICIAL_REPAIR_LINK"


@dataclass(frozen=True)
class SpatialPoint:
    """An untransformed point in a declared source coordinate frame."""

    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        values = (self.x, self.y, self.z)
        if not all(
            isinstance(value, Real)
            and not isinstance(value, bool)
            and math.isfinite(value)
            for value in values
        ):
            raise MaleCNSValidationError("Spatial coordinates must be finite.")
        object.__setattr__(self, "x", float(self.x))
        object.__setattr__(self, "y", float(self.y))
        object.__setattr__(self, "z", float(self.z))

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass(frozen=True)
class SkeletonNode:
    """One source skeleton sample; coordinates remain in the source frame."""

    node_id: int
    location: SpatialPoint
    radius: float | None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.node_id, Integral)
            or isinstance(self.node_id, bool)
            or self.node_id <= 0
        ):
            raise MaleCNSValidationError("Skeleton node_id must be positive.")
        if not isinstance(self.location, SpatialPoint):
            raise MaleCNSValidationError(
                "Skeleton location must be a source SpatialPoint."
            )
        if self.radius is not None and (
            not isinstance(self.radius, Real)
            or isinstance(self.radius, bool)
            or not math.isfinite(self.radius)
            or self.radius < 0
        ):
            raise MaleCNSValidationError(
                "Skeleton radius must be finite and non-negative or null."
            )
        object.__setattr__(self, "node_id", int(self.node_id))
        if self.radius is not None:
            object.__setattr__(self, "radius", float(self.radius))

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "x": self.location.x,
            "y": self.location.y,
            "z": self.location.z,
            "radius": self.radius,
        }


@dataclass(frozen=True)
class SkeletonLink:
    """Child-to-parent serialization linkage, not neural signal direction."""

    child_node_id: int
    parent_node_id: int
    provenance: SkeletonLinkProvenance

    def __post_init__(self) -> None:
        if (
            not isinstance(self.child_node_id, Integral)
            or not isinstance(self.parent_node_id, Integral)
            or isinstance(self.child_node_id, bool)
            or isinstance(self.parent_node_id, bool)
            or self.child_node_id <= 0
            or self.parent_node_id <= 0
            or self.child_node_id == self.parent_node_id
        ):
            raise MaleCNSValidationError(
                "Skeleton links require distinct positive node IDs."
            )
        if not isinstance(self.provenance, SkeletonLinkProvenance):
            raise MaleCNSValidationError("Skeleton link provenance is invalid.")
        object.__setattr__(self, "child_node_id", int(self.child_node_id))
        object.__setattr__(self, "parent_node_id", int(self.parent_node_id))

    def to_dict(self) -> dict[str, Any]:
        return {
            "child_node_id": self.child_node_id,
            "parent_node_id": self.parent_node_id,
            "provenance": self.provenance.value,
        }


@dataclass(frozen=True)
class SkeletonComponent:
    """One disconnected source component; components are never auto-joined."""

    component_id: int
    nodes: tuple[SkeletonNode, ...]
    links: tuple[SkeletonLink, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.component_id, Integral)
            or isinstance(self.component_id, bool)
            or self.component_id < 0
        ):
            raise MaleCNSValidationError(
                "Skeleton component_id must be a non-negative integer."
            )
        object.__setattr__(self, "component_id", int(self.component_id))
        if not isinstance(self.nodes, tuple) or not all(
            isinstance(node, SkeletonNode) for node in self.nodes
        ):
            raise MaleCNSValidationError(
                "Skeleton component nodes must be an immutable node tuple."
            )
        if not isinstance(self.links, tuple) or not all(
            isinstance(link, SkeletonLink) for link in self.links
        ):
            raise MaleCNSValidationError(
                "Skeleton component links must be an immutable link tuple."
            )
        if not self.nodes:
            raise MaleCNSValidationError("Skeleton components must contain nodes.")
        node_ids = tuple(node.node_id for node in self.nodes)
        if len(set(node_ids)) != len(node_ids):
            raise MaleCNSValidationError(
                "Skeleton node IDs must be unique within a component."
            )
        if node_ids != tuple(sorted(node_ids)):
            raise MaleCNSValidationError("Skeleton nodes must be ordered by node_id.")
        node_id_set = set(node_ids)
        edge_keys = []
        for link in self.links:
            if (
                link.child_node_id not in node_id_set
                or link.parent_node_id not in node_id_set
            ):
                raise MaleCNSValidationError(
                    "Skeleton links must remain within their component."
                )
            edge_keys.append(
                (
                    min(link.child_node_id, link.parent_node_id),
                    max(link.child_node_id, link.parent_node_id),
                )
            )
        if len(set(edge_keys)) != len(edge_keys):
            raise MaleCNSValidationError("Duplicate skeleton links are forbidden.")
        link_order = tuple(
            (link.child_node_id, link.parent_node_id, link.provenance.value)
            for link in self.links
        )
        if link_order != tuple(sorted(link_order)):
            raise MaleCNSValidationError(
                "Skeleton links must use deterministic child/parent ordering."
            )
        if len(self.links) != len(self.nodes) - 1:
            raise MaleCNSValidationError(
                "Each skeleton component must preserve one tree without invented joins."
            )
        neighbors = {node_id: set() for node_id in node_ids}
        for left, right in edge_keys:
            neighbors[left].add(right)
            neighbors[right].add(left)
        visited: set[int] = set()
        pending = [node_ids[0]]
        while pending:
            node_id = pending.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            pending.extend(neighbors[node_id] - visited)
        if visited != node_id_set:
            raise MaleCNSValidationError(
                "Skeleton component links must form one connected tree."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "links": [link.to_dict() for link in self.links],
        }


@dataclass(frozen=True)
class NeuronSpatialRecord:
    """Immutable, body-keyed morphology in unmodified source coordinates."""

    dataset_id: str
    candidate_id: str
    candidate_version: int
    body_id: int
    node_index: int
    neuron_type: str
    side: str | None
    source_category: SpatialEvidenceCategory
    morphology_source: str
    morphology_mode: MorphologyMode
    coordinate_unit: str
    coordinate_frame_id: str
    components: tuple[SkeletonComponent, ...]
    source_swc_sha256: str
    soma_location: SpatialPoint | None = None
    schema_version: str = SPATIAL_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SPATIAL_SCHEMA_VERSION:
            raise MaleCNSValidationError(
                f"Unsupported spatial schema {self.schema_version!r}."
            )
        if (
            not isinstance(self.dataset_id, str)
            or not self.dataset_id
            or not isinstance(self.candidate_id, str)
            or not self.candidate_id
        ):
            raise MaleCNSValidationError(
                "Spatial dataset and candidate identities must not be empty."
            )
        if (
            not isinstance(self.candidate_version, Integral)
            or isinstance(self.candidate_version, bool)
            or self.candidate_version <= 0
            or not isinstance(self.body_id, Integral)
            or isinstance(self.body_id, bool)
            or self.body_id <= 0
            or not isinstance(self.node_index, Integral)
            or isinstance(self.node_index, bool)
            or self.node_index < 0
        ):
            raise MaleCNSValidationError(
                "Spatial body_id must be positive and node_index non-negative."
            )
        object.__setattr__(self, "candidate_version", int(self.candidate_version))
        object.__setattr__(self, "body_id", int(self.body_id))
        object.__setattr__(self, "node_index", int(self.node_index))
        if not isinstance(self.source_category, SpatialEvidenceCategory):
            raise MaleCNSValidationError("Spatial source category is invalid.")
        if not isinstance(self.morphology_mode, MorphologyMode):
            raise MaleCNSValidationError("Spatial morphology mode is invalid.")
        if (
            not isinstance(self.neuron_type, str)
            or not self.neuron_type
            or not isinstance(self.morphology_source, str)
            or not self.morphology_source
            or not isinstance(self.coordinate_unit, str)
            or not self.coordinate_unit
            or not isinstance(self.coordinate_frame_id, str)
            or not self.coordinate_frame_id
        ):
            raise MaleCNSValidationError(
                "Neuron type, coordinate unit, and coordinate frame are required."
            )
        if self.side is not None and not isinstance(self.side, str):
            raise MaleCNSValidationError(
                "Spatial side must be a source string or null."
            )
        if not isinstance(self.components, tuple) or not all(
            isinstance(component, SkeletonComponent) for component in self.components
        ):
            raise MaleCNSValidationError(
                "Spatial components must be an immutable component tuple."
            )
        if self.soma_location is not None and not isinstance(
            self.soma_location, SpatialPoint
        ):
            raise MaleCNSValidationError(
                "Soma location must be a source SpatialPoint or null."
            )
        component_ids = tuple(component.component_id for component in self.components)
        if not component_ids or component_ids != tuple(sorted(component_ids)):
            raise MaleCNSValidationError(
                "Spatial components must be present and ordered by component_id."
            )
        if len(set(component_ids)) != len(component_ids):
            raise MaleCNSValidationError("Spatial component IDs must be unique.")
        all_node_ids = [
            node.node_id for component in self.components for node in component.nodes
        ]
        if len(all_node_ids) != len(set(all_node_ids)):
            raise MaleCNSValidationError(
                "Skeleton node IDs must be unique across all components."
            )
        if self.morphology_mode is MorphologyMode.RAW and any(
            link.provenance is SkeletonLinkProvenance.ARTIFICIAL_REPAIR
            for component in self.components
            for link in component.links
        ):
            raise MaleCNSValidationError(
                "RAW morphology cannot contain artificial repair links."
            )
        if (
            self.morphology_mode is MorphologyMode.HEALED
            and self.source_category
            is not SpatialEvidenceCategory.NEUROFLY_MODELLING_ASSUMPTION
        ):
            raise MaleCNSValidationError(
                "HEALED morphology must remain a NeuroFly modelling assumption."
            )
        if len(self.source_swc_sha256) != 64 or any(
            char not in "0123456789abcdef" for char in self.source_swc_sha256
        ):
            raise MaleCNSValidationError(
                "source_swc_sha256 must be a lowercase SHA-256 digest."
            )

    @property
    def component_count(self) -> int:
        return len(self.components)

    @property
    def spatial_record_id(self) -> str:
        encoded = json.dumps(
            self.to_dict(include_record_id=False),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"

    def to_dict(self, *, include_record_id: bool = True) -> dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "dataset_id": self.dataset_id,
            "candidate_id": self.candidate_id,
            "candidate_version": self.candidate_version,
            "body_id": self.body_id,
            "node_index": self.node_index,
            "neuron_type": self.neuron_type,
            "side": self.side,
            "source_category": self.source_category.value,
            "morphology_source": self.morphology_source,
            "morphology_mode": self.morphology_mode.value,
            "coordinate_unit": self.coordinate_unit,
            "coordinate_frame_id": self.coordinate_frame_id,
            "component_count": self.component_count,
            "components": [component.to_dict() for component in self.components],
            "source_swc_sha256": self.source_swc_sha256,
            "soma_location": (
                None if self.soma_location is None else self.soma_location.to_dict()
            ),
        }
        if include_record_id:
            result["spatial_record_id"] = self.spatial_record_id
        return result


def validate_spatial_record_against_circuit(
    record: NeuronSpatialRecord, circuit: "CircuitContract"
) -> None:
    """Require exact dataset/body/node/type/side linkage to a circuit contract."""

    if record.dataset_id != circuit.provenance.dataset:
        raise MaleCNSValidationError("Spatial record dataset does not match circuit.")
    if (
        record.candidate_id != circuit.candidate.identifier
        or record.candidate_version != circuit.candidate.version
    ):
        raise MaleCNSValidationError("Spatial record candidate does not match circuit.")
    if record.body_id not in circuit.neurons_by_body_id:
        raise MaleCNSValidationError("Spatial body_id is absent from circuit.")
    neuron = circuit.neurons_by_body_id[record.body_id]
    if circuit.node_index_by_body_id[record.body_id] != record.node_index:
        raise MaleCNSValidationError("Spatial node_index does not match body_id.")
    if neuron.type != record.neuron_type or neuron.soma_side != record.side:
        raise MaleCNSValidationError(
            "Spatial neuron type/side metadata does not match circuit."
        )


def current_raw_spatial_record(
    *,
    body_id: int,
    node_index: int,
    neuron_type: str,
    side: str | None,
    components: tuple[SkeletonComponent, ...],
    source_swc_sha256: str,
    soma_location: SpatialPoint | None = None,
) -> NeuronSpatialRecord:
    """Construct the pinned raw MaleCNS v1.0 contract without transforming it."""

    return NeuronSpatialRecord(
        dataset_id=MALECNS_DATASET,
        candidate_id=CANDIDATE.identifier,
        candidate_version=CANDIDATE.version,
        body_id=body_id,
        node_index=node_index,
        neuron_type=neuron_type,
        side=side,
        source_category=SpatialEvidenceCategory.MALECNS_DIRECT_DATA,
        morphology_source=MALECNS_NEUPRINT_SKELETON_SOURCE,
        morphology_mode=MorphologyMode.RAW,
        coordinate_unit=MALECNS_EM_COORDINATE_UNIT,
        coordinate_frame_id=MALECNS_EM_COORDINATE_FRAME,
        components=components,
        source_swc_sha256=source_swc_sha256,
        soma_location=soma_location,
    )
