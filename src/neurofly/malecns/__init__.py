"""Reproducible access to the pinned MaleCNS candidate circuit."""

from neurofly.malecns.acquire import acquire_candidate
from neurofly.malecns.benchmarks import BENCHMARKS, SENSORY_BOUNDARY
from neurofly.malecns.client import create_client
from neurofly.malecns.column_snapshot import (
    export_column_contract,
    load_column_contract,
)
from neurofly.malecns.columns import (
    BodyColumnInputContract,
    BodyColumnSummary,
    ColumnInputRecord,
    acquire_body_columns,
    validate_column_contract,
)
from neurofly.malecns.contract import CircuitContract, load_circuit_contract
from neurofly.malecns.models import CANDIDATE, CandidateSnapshot
from neurofly.malecns.morphology_artifacts import (
    DNP01_MORPHOLOGY_BODY_IDS,
    MORPHOLOGY_ARTIFACT_SCHEMA_VERSION,
    PHASE5G_MORPHOLOGY_BODY_IDS,
    PHASE5G_MORPHOLOGY_SAMPLE,
    LoadedMorphologyArtifact,
    MorphologyBodyRecord,
    acquire_dnp01_morphology,
    acquire_dnp01_morphology_from_official_bulk_swc,
    acquire_phase5g_morphology_from_official_bulk_swc,
    export_morphology_artifact,
    generate_dnp01_morphology_artifact,
    generate_dnp01_morphology_artifact_from_official_bulk_swc,
    generate_phase5g_morphology_artifact_from_official_bulk_swc,
    load_morphology_artifact,
)
from neurofly.malecns.sensory import LoomingSample, LoomingStimulus, VisualPoint
from neurofly.malecns.snapshot import export_snapshot
from neurofly.malecns.spatial import (
    MALECNS_EM_COORDINATE_FRAME,
    MALECNS_EM_COORDINATE_UNIT,
    MALECNS_NEUPRINT_SKELETON_SOURCE,
    MALECNS_OFFICIAL_BULK_SWC_SOURCE,
    SPATIAL_SCHEMA_VERSION,
    MorphologyMode,
    NeuronSpatialRecord,
    SkeletonComponent,
    SkeletonLink,
    SkeletonLinkProvenance,
    SkeletonNode,
    SpatialEvidenceCategory,
    SpatialPoint,
    current_raw_spatial_record,
    validate_spatial_record_against_circuit,
)
from neurofly.malecns.validation import validate_snapshot

__all__ = [
    "CANDIDATE",
    "BENCHMARKS",
    "BodyColumnInputContract",
    "BodyColumnSummary",
    "SENSORY_BOUNDARY",
    "ColumnInputRecord",
    "CircuitContract",
    "CandidateSnapshot",
    "DNP01_MORPHOLOGY_BODY_IDS",
    "PHASE5G_MORPHOLOGY_BODY_IDS",
    "PHASE5G_MORPHOLOGY_SAMPLE",
    "LoadedMorphologyArtifact",
    "LoomingSample",
    "LoomingStimulus",
    "MALECNS_EM_COORDINATE_FRAME",
    "MALECNS_EM_COORDINATE_UNIT",
    "MALECNS_OFFICIAL_BULK_SWC_SOURCE",
    "MALECNS_NEUPRINT_SKELETON_SOURCE",
    "MorphologyMode",
    "MorphologyBodyRecord",
    "MORPHOLOGY_ARTIFACT_SCHEMA_VERSION",
    "NeuronSpatialRecord",
    "SPATIAL_SCHEMA_VERSION",
    "SkeletonComponent",
    "SkeletonLink",
    "SkeletonLinkProvenance",
    "SkeletonNode",
    "SpatialEvidenceCategory",
    "SpatialPoint",
    "VisualPoint",
    "acquire_candidate",
    "acquire_body_columns",
    "acquire_dnp01_morphology",
    "acquire_dnp01_morphology_from_official_bulk_swc",
    "acquire_phase5g_morphology_from_official_bulk_swc",
    "create_client",
    "current_raw_spatial_record",
    "export_column_contract",
    "export_morphology_artifact",
    "export_snapshot",
    "load_column_contract",
    "load_circuit_contract",
    "load_morphology_artifact",
    "validate_column_contract",
    "validate_spatial_record_against_circuit",
    "validate_snapshot",
    "generate_dnp01_morphology_artifact",
    "generate_dnp01_morphology_artifact_from_official_bulk_swc",
    "generate_phase5g_morphology_artifact_from_official_bulk_swc",
]
