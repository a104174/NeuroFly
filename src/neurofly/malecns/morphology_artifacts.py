"""Raw, fixed-scope MaleCNS morphology acquisition and portable artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from neurofly.malecns.contract import CircuitContract
from neurofly.malecns.errors import (
    MaleCNSAccessError,
    MaleCNSValidationError,
    MorphologyArtifactError,
    MorphologyArtifactExportError,
    MorphologyArtifactIntegrityError,
    MorphologyArtifactSchemaError,
)
from neurofly.malecns.models import NEUPRINT_ENDPOINT
from neurofly.malecns.spatial import (
    MALECNS_EM_COORDINATE_FRAME,
    MALECNS_EM_COORDINATE_UNIT,
    MALECNS_NEUPRINT_SKELETON_SOURCE,
    MALECNS_OFFICIAL_BULK_SWC_SOURCE,
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

MORPHOLOGY_ARTIFACT_SCHEMA_VERSION = "malecns_morphology_artifact_v1"
MORPHOLOGY_BODY_SCHEMA_VERSION = "malecns_morphology_body_v1"
MORPHOLOGY_MANIFEST_FILENAME = "manifest.json"
MORPHOLOGY_BODY_DIRECTORY = "bodies"
DNP01_MORPHOLOGY_BODY_IDS = (10001, 10010)
EXPECTED_DNP01_MAPPING = (
    (10001, 0, "DNp01", "R"),
    (10010, 1, "DNp01", "L"),
)
PHASE5G_MORPHOLOGY_SAMPLE = "phase5g-six-body"
PHASE5G_MORPHOLOGY_BODY_IDS = (10001, 10010, 11498, 12032, 14465, 16128)
EXPECTED_PHASE5G_MAPPING = (
    (10001, 0, "DNp01", "R"),
    (10010, 1, "DNp01", "L"),
    (11498, 2, "LPLC2", "L"),
    (12032, 3, "LC4", "L"),
    (14465, 12, "LPLC2", "R"),
    (16128, 16, "LC4", "R"),
)
EXPECTED_PHASE5G_SOURCE = MappingProxyType(
    {
        10001: (
            2975,
            (2975,),
            "838c60b0e4724d8ca163be994012ebdc23e7ccbdcb9cde92f25e541bc4696511",
        ),
        10010: (
            3312,
            (3312,),
            "97e1c587397bd6ec1d6489c1ff129c13b3794745f1ada4376313fdf50363d336",
        ),
        11498: (
            2121,
            (9, 2112),
            "172ed22b0ec942974d211a91d064d77a52ac49ffc3757d4fffee92d0ffa71d74",
        ),
        12032: (
            1251,
            (1251,),
            "cd6893e4adf7eb5b8070d40e2ec5644fbfde09f98e8b231ccd56bf6e63711c3d",
        ),
        14465: (
            2467,
            (2467,),
            "f7171d38867895e4bdd62ad13996573e30121a2bd2e852047417d4fb17e3467d",
        ),
        16128: (
            1773,
            (1773,),
            "ffe661f5c0669fe54b253a2101940bd2b36d098a1c0af8caf3edee7c857354a0",
        ),
    }
)
OFFICIAL_MALECNS_BULK_SWC_BASE_URL = (
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/"
    "skeletons-malecns/skeletons-swc/"
)
OFFICIAL_MALECNS_BULK_SWC_URLS = MappingProxyType(
    {
        body_id: f"{OFFICIAL_MALECNS_BULK_SWC_BASE_URL}{body_id}.swc"
        for body_id in DNP01_MORPHOLOGY_BODY_IDS
    }
)
OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS = MappingProxyType(
    {
        body_id: f"{OFFICIAL_MALECNS_BULK_SWC_BASE_URL}{body_id}.swc"
        for body_id in PHASE5G_MORPHOLOGY_BODY_IDS
    }
)
MORPHOLOGY_RETRIEVAL_NEUPRINT = "fetch_skeleton(heal=False, format=swc)"
MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC = (
    "official_malecns_bulk_swc(raw, heal=False, smoothing=False, repair=False)"
)


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value}")


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise MorphologyArtifactIntegrityError(
            f"could not hash morphology file {path.name!r}"
        ) from exc
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> str:
    payload = _json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return _sha256_bytes(payload)


def _read_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_json_constant
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise MorphologyArtifactSchemaError(f"malformed {label}: {exc}") from None
    if not isinstance(value, Mapping):
        raise MorphologyArtifactSchemaError(f"{label} must be a JSON object")
    return value


def _require_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    if missing or extra:
        raise MorphologyArtifactSchemaError(
            f"invalid {label} fields: missing={missing!r}, unexpected={extra!r}"
        )


def _string(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value:
        raise MorphologyArtifactSchemaError(f"{label} must be a non-empty string")
    return value


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MorphologyArtifactSchemaError(f"{label} must be an integer")
    return value


def _number(value: Any, label: str, *, nullable: bool = False) -> float | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MorphologyArtifactSchemaError(f"{label} must be numeric")
    return float(value)


def _sha256(value: Any, label: str) -> str:
    result = _string(value, label)
    if len(result) != 64 or any(char not in "0123456789abcdef" for char in result):
        raise MorphologyArtifactSchemaError(f"{label} must be a lowercase SHA-256")
    return result


def _source_provenance(
    source_mode: str,
    source_urls: Mapping[int | str, str] | None,
) -> tuple[str, tuple[tuple[int, str], ...]]:
    """Normalize and validate the explicit morphology acquisition source."""

    if source_mode not in {
        MALECNS_NEUPRINT_SKELETON_SOURCE,
        MALECNS_OFFICIAL_BULK_SWC_SOURCE,
    }:
        raise MorphologyArtifactSchemaError(
            f"unsupported morphology source mode {source_mode!r}"
        )
    supplied = {} if source_urls is None else dict(source_urls)
    normalized: dict[int, str] = {}
    for body_id, url in supplied.items():
        try:
            body_key = int(body_id)
        except (TypeError, ValueError):
            raise MorphologyArtifactSchemaError(
                "morphology source URL body IDs must be integers"
            ) from None
        if body_key in normalized or not isinstance(url, str) or not url:
            raise MorphologyArtifactSchemaError("morphology source URLs are invalid")
        normalized[body_key] = url
    if source_mode == MALECNS_OFFICIAL_BULK_SWC_SOURCE:
        expected_sets = (
            dict(OFFICIAL_MALECNS_BULK_SWC_URLS),
            dict(OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS),
        )
        if normalized not in expected_sets:
            raise MorphologyArtifactSchemaError(
                "official bulk SWC provenance must name one canonical fixed sample"
            )
    elif normalized:
        raise MorphologyArtifactSchemaError(
            "neuPrint morphology provenance must not contain bulk source URLs"
        )
    return source_mode, tuple(sorted(normalized.items()))


def _source_urls_dict(source_urls: tuple[tuple[int, str], ...]) -> dict[str, str]:
    return {str(body_id): url for body_id, url in source_urls}


@dataclass(frozen=True, slots=True)
class MorphologyBodyRecord:
    """One raw body record plus source reconstruction status."""

    spatial_record: NeuronSpatialRecord
    source_status: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": MORPHOLOGY_BODY_SCHEMA_VERSION,
            "source_status": self.source_status,
            "spatial_record": self.spatial_record.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class LoadedMorphologyArtifact:
    """Integrity-validated fixed-sample raw morphology artifact."""

    path: Path
    artifact_id: str
    generated_at_utc: str
    neuprint_python_version: str
    source_endpoint: str
    source_mode: str
    source_urls: tuple[tuple[int, str], ...]
    retrieval: str
    bodies: tuple[MorphologyBodyRecord, ...]
    file_sha256: tuple[tuple[str, str], ...]
    manifest: Mapping[str, Any]

    @property
    def bodies_by_id(self) -> Mapping[int, MorphologyBodyRecord]:
        return MappingProxyType(
            {item.spatial_record.body_id: item for item in self.bodies}
        )

    def inspection_dict(self) -> dict[str, Any]:
        return {
            "artifact_schema_version": MORPHOLOGY_ARTIFACT_SCHEMA_VERSION,
            "artifact_id": self.artifact_id,
            "dataset": self.bodies[0].spatial_record.dataset_id,
            "candidate": {
                "identifier": self.bodies[0].spatial_record.candidate_id,
                "version": self.bodies[0].spatial_record.candidate_version,
            },
            "morphology_mode": MorphologyMode.RAW.value,
            "coordinate_frame_id": MALECNS_EM_COORDINATE_FRAME,
            "coordinate_unit": MALECNS_EM_COORDINATE_UNIT,
            "body_ids": [item.spatial_record.body_id for item in self.bodies],
            "bodies": [
                {
                    "body_id": item.spatial_record.body_id,
                    "node_index": item.spatial_record.node_index,
                    "source_side": item.spatial_record.side,
                    "source_status": item.source_status,
                    "node_count": sum(
                        len(component.nodes)
                        for component in item.spatial_record.components
                    ),
                    "component_count": item.spatial_record.component_count,
                    "spatial_record_id": item.spatial_record.spatial_record_id,
                    "source_swc_sha256": item.spatial_record.source_swc_sha256,
                }
                for item in self.bodies
            ],
            "generated_at_utc": self.generated_at_utc,
            "neuprint_python_version": self.neuprint_python_version,
            "source_endpoint": self.source_endpoint,
            "source_mode": self.source_mode,
            "source_urls": {str(body_id): url for body_id, url in self.source_urls},
            "retrieval": self.retrieval,
            "file_sha256": [list(item) for item in self.file_sha256],
        }


def validate_fixed_dnp01_mapping(circuit: CircuitContract) -> None:
    """Verify the exact Phase 5F body/index/type/side boundary."""

    for body_id, node_index, neuron_type, side in EXPECTED_DNP01_MAPPING:
        neuron = circuit.neurons_by_body_id.get(body_id)
        if neuron is None:
            raise MaleCNSValidationError(f"DNp01 body {body_id} is absent")
        actual = (
            circuit.node_index_by_body_id[body_id],
            neuron.type,
            neuron.soma_side,
        )
        if actual != (node_index, neuron_type, side):
            raise MaleCNSValidationError(
                f"DNp01 body {body_id} mapping mismatch: {actual!r}"
            )


def validate_fixed_phase5g_mapping(circuit: CircuitContract) -> None:
    """Verify the exact Phase 5G body/index/type/side boundary."""

    for body_id, node_index, neuron_type, side in EXPECTED_PHASE5G_MAPPING:
        neuron = circuit.neurons_by_body_id.get(body_id)
        if neuron is None:
            raise MaleCNSValidationError(f"Phase 5G body {body_id} is absent")
        actual = (
            circuit.node_index_by_body_id[body_id],
            neuron.type,
            neuron.soma_side,
        )
        if actual != (node_index, neuron_type, side):
            raise MaleCNSValidationError(
                f"Phase 5G body {body_id} mapping mismatch: {actual!r}"
            )


def _components_from_swc_frame(frame: Any) -> tuple[SkeletonComponent, ...]:
    required = {"rowId", "x", "y", "z", "radius", "link"}
    if not required.issubset(frame.columns):
        raise MaleCNSValidationError("raw skeleton is missing required SWC fields")
    rows = {int(row.rowId): row for row in frame.itertuples(index=False)}
    if not rows:
        raise MaleCNSValidationError("raw skeleton must not be empty")
    parent_by_id = {node_id: int(row.link) for node_id, row in rows.items()}
    roots = sorted(node_id for node_id, parent in parent_by_id.items() if parent == -1)
    if not roots:
        raise MaleCNSValidationError("raw skeleton has no component root")
    root_by_id: dict[int, int] = {}
    for node_id in sorted(rows):
        trail: list[int] = []
        visiting: set[int] = set()
        current = node_id
        while current not in root_by_id and parent_by_id[current] != -1:
            if current in visiting:
                raise MaleCNSValidationError("raw skeleton contains a parent cycle")
            visiting.add(current)
            trail.append(current)
            parent = parent_by_id[current]
            if parent not in rows:
                raise MaleCNSValidationError(
                    "raw skeleton parent references a missing node"
                )
            current = parent
        root = root_by_id.get(current, current)
        root_by_id[current] = root
        for item in trail:
            root_by_id[item] = root
    grouped: dict[int, list[int]] = {root: [] for root in roots}
    for node_id, root in root_by_id.items():
        grouped.setdefault(root, []).append(node_id)
    components = []
    for component_id, root in enumerate(sorted(grouped)):
        node_ids = sorted(grouped[root])
        nodes = tuple(
            SkeletonNode(
                node_id=node_id,
                location=SpatialPoint(
                    float(rows[node_id].x),
                    float(rows[node_id].y),
                    float(rows[node_id].z),
                ),
                radius=float(rows[node_id].radius),
            )
            for node_id in node_ids
        )
        links = tuple(
            SkeletonLink(
                child_node_id=node_id,
                parent_node_id=parent_by_id[node_id],
                provenance=SkeletonLinkProvenance.RAW,
            )
            for node_id in node_ids
            if parent_by_id[node_id] != -1
        )
        components.append(SkeletonComponent(component_id, nodes, links))
    return tuple(components)


def _soma_coordinates(value: Any) -> SpatialPoint | None:
    if value is None:
        return None
    coordinates = getattr(value, "coordinates", None)
    if coordinates is None and isinstance(value, Mapping):
        coordinates = value.get("coordinates")
    if not isinstance(coordinates, (tuple, list)) or len(coordinates) != 3:
        raise MaleCNSValidationError("somaLocation is not a three-coordinate point")
    return SpatialPoint(*(float(item) for item in coordinates))


def _fetch_soma_rows(client: Any) -> Any:
    from neuprint import fetch_custom

    ids = ", ".join(str(body_id) for body_id in DNP01_MORPHOLOGY_BODY_IDS)
    return fetch_custom(
        f"""MATCH (n:Neuron) WHERE n.bodyId IN [{ids}]
RETURN n.bodyId AS bodyId, n.somaLocation AS somaLocation
ORDER BY n.bodyId""",
        client=client,
    )


def _components_from_swc_text(swc: str) -> tuple[SkeletonComponent, ...]:
    from neuprint.skeleton import skeleton_swc_to_df

    return _components_from_swc_frame(skeleton_swc_to_df(swc))


def acquire_dnp01_morphology(
    client: Any,
    circuit: CircuitContract,
    *,
    soma_fetcher: Callable[[Any], Any] = _fetch_soma_rows,
    skeleton_fetcher: Callable[[int, Any], str] | None = None,
) -> tuple[MorphologyBodyRecord, ...]:
    """Fetch exactly two raw DNp01 skeletons; never heal or write data."""

    validate_fixed_dnp01_mapping(circuit)
    if client.dataset != circuit.provenance.dataset:
        raise MaleCNSAccessError("neuPrint dataset does not match CircuitContract")
    try:
        soma_table = soma_fetcher(client)
        soma_by_body = {
            int(row.bodyId): _soma_coordinates(row.somaLocation)
            for row in soma_table.itertuples(index=False)
        }
        if set(soma_by_body) != set(DNP01_MORPHOLOGY_BODY_IDS):
            raise MaleCNSValidationError("soma query did not return the fixed body set")
        records = []
        for body_id in DNP01_MORPHOLOGY_BODY_IDS:
            if skeleton_fetcher is None:
                swc = client.fetch_skeleton(body_id, heal=False, format="swc")
            else:
                swc = skeleton_fetcher(body_id, client)
            if not isinstance(swc, str) or not swc.strip():
                raise MaleCNSValidationError(
                    f"raw skeleton for body {body_id} is unavailable"
                )
            neuron = circuit.neurons_by_body_id[body_id]
            spatial = current_raw_spatial_record(
                body_id=body_id,
                node_index=circuit.node_index_by_body_id[body_id],
                neuron_type=neuron.type,
                side=neuron.soma_side,
                components=_components_from_swc_text(swc),
                source_swc_sha256=_sha256_bytes(swc.encode("utf-8")),
                soma_location=soma_by_body[body_id],
            )
            validate_spatial_record_against_circuit(spatial, circuit)
            records.append(MorphologyBodyRecord(spatial, neuron.status))
        return tuple(records)
    except (MaleCNSAccessError, MaleCNSValidationError):
        raise
    except Exception:
        raise MaleCNSAccessError(
            "Raw DNp01 morphology acquisition failed; check access and availability."
        ) from None


def _download_official_bulk_swc(body_id: int, url: str) -> bytes:
    request = Request(url, headers={"Accept": "text/plain"})
    try:
        with urlopen(request, timeout=120) as response:
            payload = response.read()
    except (HTTPError, URLError, TimeoutError, OSError):
        raise MaleCNSAccessError(
            f"Official MaleCNS bulk SWC download failed for body {body_id}."
        ) from None
    if not payload:
        raise MaleCNSValidationError(
            f"Official MaleCNS bulk SWC is empty for body {body_id}."
        )
    return payload


def acquire_dnp01_morphology_from_official_bulk_swc(
    circuit: CircuitContract,
    *,
    fetcher: Callable[[int, str], bytes] | None = None,
) -> tuple[tuple[MorphologyBodyRecord, ...], tuple[tuple[int, str], ...]]:
    """Fetch exactly two raw skeletons from the official bulk SWC source."""

    validate_fixed_dnp01_mapping(circuit)
    if circuit.provenance.dataset != "male-cns:v1.0":
        raise MaleCNSValidationError("CircuitContract dataset is not male-cns:v1.0")
    source_urls = tuple(sorted(OFFICIAL_MALECNS_BULK_SWC_URLS.items()))
    records = []
    try:
        for body_id, url in source_urls:
            payload = (
                _download_official_bulk_swc(body_id, url)
                if fetcher is None
                else fetcher(body_id, url)
            )
            if not isinstance(payload, bytes) or not payload:
                raise MaleCNSValidationError(
                    f"Official MaleCNS bulk SWC is empty for body {body_id}."
                )
            try:
                swc = payload.decode("utf-8")
            except UnicodeDecodeError:
                raise MaleCNSValidationError(
                    f"Official MaleCNS bulk SWC is not UTF-8 for body {body_id}."
                ) from None
            if not swc.strip():
                raise MaleCNSValidationError(
                    f"Official MaleCNS bulk SWC is empty for body {body_id}."
                )
            neuron = circuit.neurons_by_body_id[body_id]
            spatial = current_raw_spatial_record(
                body_id=body_id,
                node_index=circuit.node_index_by_body_id[body_id],
                neuron_type=neuron.type,
                side=neuron.soma_side,
                components=_components_from_swc_text(swc),
                source_swc_sha256=_sha256_bytes(payload),
                soma_location=None,
                morphology_source=MALECNS_OFFICIAL_BULK_SWC_SOURCE,
            )
            validate_spatial_record_against_circuit(spatial, circuit)
            records.append(MorphologyBodyRecord(spatial, neuron.status))
    except (MaleCNSAccessError, MaleCNSValidationError):
        raise
    except Exception:
        raise MaleCNSValidationError(
            "Official MaleCNS bulk SWC parsing failed; source data are invalid."
        ) from None
    return tuple(records), source_urls


def acquire_phase5g_morphology_from_official_bulk_swc(
    circuit: CircuitContract,
    *,
    fetcher: Callable[[int, str], bytes] | None = None,
) -> tuple[tuple[MorphologyBodyRecord, ...], tuple[tuple[int, str], ...]]:
    """Fetch exactly the six audited Phase 5G raw official SWC skeletons."""

    validate_fixed_phase5g_mapping(circuit)
    if circuit.provenance.dataset != "male-cns:v1.0":
        raise MaleCNSValidationError("CircuitContract dataset is not male-cns:v1.0")
    source_urls = tuple(sorted(OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS.items()))
    records = []
    try:
        for body_id, url in source_urls:
            payload = (
                _download_official_bulk_swc(body_id, url)
                if fetcher is None
                else fetcher(body_id, url)
            )
            if not isinstance(payload, bytes) or not payload:
                raise MaleCNSValidationError(
                    f"Official MaleCNS bulk SWC is empty for body {body_id}."
                )
            try:
                swc = payload.decode("utf-8")
            except UnicodeDecodeError:
                raise MaleCNSValidationError(
                    f"Official MaleCNS bulk SWC is not UTF-8 for body {body_id}."
                ) from None
            if not swc.strip():
                raise MaleCNSValidationError(
                    f"Official MaleCNS bulk SWC is empty for body {body_id}."
                )
            neuron = circuit.neurons_by_body_id[body_id]
            spatial = current_raw_spatial_record(
                body_id=body_id,
                node_index=circuit.node_index_by_body_id[body_id],
                neuron_type=neuron.type,
                side=neuron.soma_side,
                components=_components_from_swc_text(swc),
                source_swc_sha256=_sha256_bytes(payload),
                soma_location=None,
                morphology_source=MALECNS_OFFICIAL_BULK_SWC_SOURCE,
            )
            validate_spatial_record_against_circuit(spatial, circuit)
            records.append(MorphologyBodyRecord(spatial, neuron.status))
    except (MaleCNSAccessError, MaleCNSValidationError):
        raise
    except Exception:
        raise MaleCNSValidationError(
            "Official MaleCNS bulk SWC parsing failed; source data are invalid."
        ) from None
    if fetcher is None:
        for item in records:
            record = item.spatial_record
            expected_nodes, expected_component_sizes, expected_hash = (
                EXPECTED_PHASE5G_SOURCE[record.body_id]
            )
            component_sizes = tuple(
                len(component.nodes) for component in record.components
            )
            if (
                sum(component_sizes) != expected_nodes
                or component_sizes != expected_component_sizes
                or record.source_swc_sha256 != expected_hash
            ):
                raise MaleCNSValidationError(
                    "Official Phase 5G source differs from the audited record "
                    f"for body {record.body_id}."
                )
    return tuple(records), source_urls


def _artifact_identity(
    bodies: tuple[MorphologyBodyRecord, ...],
    *,
    source_mode: str,
    source_urls: tuple[tuple[int, str], ...],
) -> dict[str, Any]:
    first = bodies[0].spatial_record
    return {
        "artifact_schema_version": MORPHOLOGY_ARTIFACT_SCHEMA_VERSION,
        "dataset": first.dataset_id,
        "candidate": {
            "identifier": first.candidate_id,
            "version": first.candidate_version,
        },
        "morphology_mode": MorphologyMode.RAW.value,
        "coordinate_frame_id": first.coordinate_frame_id,
        "coordinate_unit": first.coordinate_unit,
        "source_mode": source_mode,
        "source_urls": _source_urls_dict(source_urls),
        "body_ids": [item.spatial_record.body_id for item in bodies],
        "spatial_record_ids": [
            [item.spatial_record.body_id, item.spatial_record.spatial_record_id]
            for item in bodies
        ],
        "source_swc_sha256": [
            [item.spatial_record.body_id, item.spatial_record.source_swc_sha256]
            for item in bodies
        ],
    }


def _validate_body_set(bodies: tuple[MorphologyBodyRecord, ...]) -> None:
    if not isinstance(bodies, tuple):
        raise MorphologyArtifactIntegrityError("morphology bodies must be a tuple")
    body_ids = tuple(item.spatial_record.body_id for item in bodies)
    expected_by_set = {
        DNP01_MORPHOLOGY_BODY_IDS: EXPECTED_DNP01_MAPPING,
        PHASE5G_MORPHOLOGY_BODY_IDS: EXPECTED_PHASE5G_MAPPING,
    }
    expected_mapping = expected_by_set.get(body_ids)
    if expected_mapping is None:
        raise MorphologyArtifactIntegrityError(
            "morphology artifact requires one supported fixed body sample"
        )
    for item, expected in zip(bodies, expected_mapping, strict=True):
        record = item.spatial_record
        if (
            record.body_id,
            record.node_index,
            record.neuron_type,
            record.side,
        ) != expected:
            raise MorphologyArtifactIntegrityError(
                f"invalid fixed mapping for body {record.body_id}"
            )
        if (
            record.morphology_mode is not MorphologyMode.RAW
            or record.coordinate_frame_id != MALECNS_EM_COORDINATE_FRAME
            or record.coordinate_unit != MALECNS_EM_COORDINATE_UNIT
            or record.source_category is not SpatialEvidenceCategory.MALECNS_DIRECT_DATA
        ):
            raise MorphologyArtifactIntegrityError(
                f"body {record.body_id} is not raw native-frame MaleCNS data"
            )


def export_morphology_artifact(
    bodies: tuple[MorphologyBodyRecord, ...],
    output_root: str | Path,
    *,
    generated_at_utc: str | None = None,
    neuprint_python_version: str = "unknown",
    source_endpoint: str = NEUPRINT_ENDPOINT,
    source_mode: str = MALECNS_NEUPRINT_SKELETON_SOURCE,
    source_urls: Mapping[int | str, str] | None = None,
    retrieval: str | None = None,
) -> Path:
    """Write canonical payloads atomically below a root; never overwrite."""

    _validate_body_set(bodies)
    normalized_source_mode, normalized_source_urls = _source_provenance(
        source_mode, source_urls
    )
    if any(
        item.spatial_record.morphology_source != normalized_source_mode
        for item in bodies
    ):
        raise MorphologyArtifactIntegrityError(
            "body morphology source does not match artifact source mode"
        )
    expected_retrieval = (
        MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC
        if normalized_source_mode == MALECNS_OFFICIAL_BULK_SWC_SOURCE
        else MORPHOLOGY_RETRIEVAL_NEUPRINT
    )
    if retrieval is not None and retrieval != expected_retrieval:
        raise MorphologyArtifactSchemaError(
            f"retrieval does not match source mode {normalized_source_mode!r}"
        )
    retrieval = expected_retrieval
    identity = _artifact_identity(
        bodies,
        source_mode=normalized_source_mode,
        source_urls=normalized_source_urls,
    )
    artifact_id = _sha256_bytes(_json_bytes(identity))
    root = Path(output_root)
    output = root / artifact_id
    if output.exists():
        raise MorphologyArtifactExportError(
            f"morphology artifact already exists: {artifact_id}"
        )
    staging: Path | None = None
    try:
        root.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".morphology.", dir=root))
        file_records = {}
        for body in bodies:
            relative = f"{MORPHOLOGY_BODY_DIRECTORY}/{body.spatial_record.body_id}.json"
            digest = _write_json(staging / relative, body.to_dict())
            file_records[relative] = {
                "schema": MORPHOLOGY_BODY_SCHEMA_VERSION,
                "sha256": digest,
                "bytes": (staging / relative).stat().st_size,
            }
        manifest = {
            **identity,
            "artifact_id": artifact_id,
            "generation": {
                "generated_at_utc": generated_at_utc or datetime.now(UTC).isoformat(),
                "neuprint_python_version": neuprint_python_version,
                "source_endpoint": source_endpoint,
                "source_mode": normalized_source_mode,
                "source_urls": _source_urls_dict(normalized_source_urls),
                "retrieval": retrieval,
            },
            "files": file_records,
        }
        manifest["manifest_sha256"] = _sha256_bytes(_json_bytes(manifest))
        _write_json(staging / MORPHOLOGY_MANIFEST_FILENAME, manifest)
        load_morphology_artifact(staging)
        os.replace(staging, output)
    except MorphologyArtifactError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise MorphologyArtifactExportError(
            f"could not export morphology artifact: {exc}"
        ) from None
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
    return output


def _parse_spatial_record(value: Any, label: str) -> NeuronSpatialRecord:
    record = value if isinstance(value, Mapping) else {}
    expected = {
        "schema_version",
        "dataset_id",
        "candidate_id",
        "candidate_version",
        "body_id",
        "node_index",
        "neuron_type",
        "side",
        "source_category",
        "morphology_source",
        "morphology_mode",
        "coordinate_unit",
        "coordinate_frame_id",
        "component_count",
        "components",
        "source_swc_sha256",
        "soma_location",
        "spatial_record_id",
    }
    _require_keys(record, expected, label)
    components_value = record["components"]
    if not isinstance(components_value, list):
        raise MorphologyArtifactSchemaError(f"{label}.components must be an array")
    components = []
    for component_index, component_value in enumerate(components_value):
        component = component_value if isinstance(component_value, Mapping) else {}
        component_label = f"{label}.components[{component_index}]"
        _require_keys(component, {"component_id", "nodes", "links"}, component_label)
        if not isinstance(component["nodes"], list) or not isinstance(
            component["links"], list
        ):
            raise MorphologyArtifactSchemaError(
                f"{component_label} nodes/links must be arrays"
            )
        nodes = []
        for node_index, node_value in enumerate(component["nodes"]):
            node = node_value if isinstance(node_value, Mapping) else {}
            node_label = f"{component_label}.nodes[{node_index}]"
            _require_keys(node, {"node_id", "x", "y", "z", "radius"}, node_label)
            nodes.append(
                SkeletonNode(
                    _integer(node["node_id"], f"{node_label}.node_id"),
                    SpatialPoint(
                        _number(node["x"], f"{node_label}.x"),
                        _number(node["y"], f"{node_label}.y"),
                        _number(node["z"], f"{node_label}.z"),
                    ),
                    _number(node["radius"], f"{node_label}.radius", nullable=True),
                )
            )
        links = []
        for link_index, link_value in enumerate(component["links"]):
            link = link_value if isinstance(link_value, Mapping) else {}
            link_label = f"{component_label}.links[{link_index}]"
            _require_keys(
                link,
                {"child_node_id", "parent_node_id", "provenance"},
                link_label,
            )
            try:
                provenance = SkeletonLinkProvenance(
                    _string(link["provenance"], f"{link_label}.provenance")
                )
            except ValueError:
                raise MorphologyArtifactSchemaError(
                    f"{link_label}.provenance is unsupported"
                ) from None
            links.append(
                SkeletonLink(
                    _integer(link["child_node_id"], f"{link_label}.child_node_id"),
                    _integer(link["parent_node_id"], f"{link_label}.parent_node_id"),
                    provenance,
                )
            )
        components.append(
            SkeletonComponent(
                _integer(component["component_id"], f"{component_label}.component_id"),
                tuple(nodes),
                tuple(links),
            )
        )
    soma_value = record["soma_location"]
    soma = None
    if soma_value is not None:
        soma_mapping = soma_value if isinstance(soma_value, Mapping) else {}
        _require_keys(soma_mapping, {"x", "y", "z"}, f"{label}.soma_location")
        soma = SpatialPoint(
            _number(soma_mapping["x"], f"{label}.soma_location.x"),
            _number(soma_mapping["y"], f"{label}.soma_location.y"),
            _number(soma_mapping["z"], f"{label}.soma_location.z"),
        )
    try:
        result = NeuronSpatialRecord(
            schema_version=_string(record["schema_version"], f"{label}.schema_version"),
            dataset_id=_string(record["dataset_id"], f"{label}.dataset_id"),
            candidate_id=_string(record["candidate_id"], f"{label}.candidate_id"),
            candidate_version=_integer(
                record["candidate_version"], f"{label}.candidate_version"
            ),
            body_id=_integer(record["body_id"], f"{label}.body_id"),
            node_index=_integer(record["node_index"], f"{label}.node_index"),
            neuron_type=_string(record["neuron_type"], f"{label}.neuron_type"),
            side=_string(record["side"], f"{label}.side", nullable=True),
            source_category=SpatialEvidenceCategory(
                _string(record["source_category"], f"{label}.source_category")
            ),
            morphology_source=_string(
                record["morphology_source"], f"{label}.morphology_source"
            ),
            morphology_mode=MorphologyMode(
                _string(record["morphology_mode"], f"{label}.morphology_mode")
            ),
            coordinate_unit=_string(
                record["coordinate_unit"], f"{label}.coordinate_unit"
            ),
            coordinate_frame_id=_string(
                record["coordinate_frame_id"], f"{label}.coordinate_frame_id"
            ),
            components=tuple(components),
            source_swc_sha256=_sha256(
                record["source_swc_sha256"], f"{label}.source_swc_sha256"
            ),
            soma_location=soma,
        )
    except (ValueError, MaleCNSValidationError) as exc:
        raise MorphologyArtifactSchemaError(f"invalid {label}: {exc}") from None
    if _integer(record["component_count"], f"{label}.component_count") != len(
        result.components
    ):
        raise MorphologyArtifactIntegrityError(f"{label} component count mismatch")
    if record["spatial_record_id"] != result.spatial_record_id:
        raise MorphologyArtifactIntegrityError(f"{label} spatial identity mismatch")
    return result


def _parse_body(value: Mapping[str, Any], filename: str) -> MorphologyBodyRecord:
    _require_keys(value, {"schema", "source_status", "spatial_record"}, filename)
    if value["schema"] != MORPHOLOGY_BODY_SCHEMA_VERSION:
        raise MorphologyArtifactSchemaError(f"unsupported body schema in {filename}")
    return MorphologyBodyRecord(
        _parse_spatial_record(value["spatial_record"], f"{filename}.spatial_record"),
        _string(value["source_status"], f"{filename}.source_status", nullable=True),
    )


def load_morphology_artifact(
    path: str | Path, *, circuit: CircuitContract | None = None
) -> LoadedMorphologyArtifact:
    """Load and strictly validate a portable raw morphology artifact offline."""

    root = Path(path)
    manifest = _read_json(root / MORPHOLOGY_MANIFEST_FILENAME, "manifest")
    if manifest.get("artifact_schema_version") != MORPHOLOGY_ARTIFACT_SCHEMA_VERSION:
        raise MorphologyArtifactSchemaError("unsupported morphology artifact schema")
    expected_manifest = {
        "artifact_schema_version",
        "artifact_id",
        "dataset",
        "candidate",
        "morphology_mode",
        "coordinate_frame_id",
        "coordinate_unit",
        "source_mode",
        "source_urls",
        "body_ids",
        "spatial_record_ids",
        "source_swc_sha256",
        "generation",
        "files",
        "manifest_sha256",
    }
    _require_keys(manifest, expected_manifest, "manifest")
    manifest_without_hash = dict(manifest)
    supplied_manifest_hash = _sha256(
        manifest_without_hash.pop("manifest_sha256"), "manifest.manifest_sha256"
    )
    if _sha256_bytes(_json_bytes(manifest_without_hash)) != supplied_manifest_hash:
        raise MorphologyArtifactIntegrityError("manifest SHA-256 mismatch")
    files = manifest["files"]
    if not isinstance(files, Mapping):
        raise MorphologyArtifactSchemaError("manifest.files must be an object")
    manifest_body_ids = manifest.get("body_ids")
    if not isinstance(manifest_body_ids, list):
        raise MorphologyArtifactSchemaError("manifest.body_ids must be an array")
    expected_files = {
        f"{MORPHOLOGY_BODY_DIRECTORY}/{body_id}.json"
        for body_id in manifest_body_ids
        if isinstance(body_id, int) and not isinstance(body_id, bool)
    }
    if len(expected_files) != len(manifest_body_ids):
        raise MorphologyArtifactSchemaError("manifest.body_ids are invalid")
    if set(files) != expected_files:
        raise MorphologyArtifactSchemaError("manifest body files do not match body_ids")
    bodies = []
    file_hashes = []
    for relative in sorted(expected_files):
        file_entry = files[relative]
        if not isinstance(file_entry, Mapping):
            raise MorphologyArtifactSchemaError(f"manifest file {relative} is invalid")
        _require_keys(file_entry, {"schema", "sha256", "bytes"}, f"files.{relative}")
        payload_path = root / relative
        if payload_path.is_symlink():
            raise MorphologyArtifactIntegrityError("symlink payloads are forbidden")
        expected_hash = _sha256(file_entry["sha256"], f"files.{relative}.sha256")
        actual_hash = _sha256_file(payload_path)
        if actual_hash != expected_hash:
            raise MorphologyArtifactIntegrityError(f"SHA-256 mismatch for {relative}")
        if payload_path.stat().st_size != _integer(
            file_entry["bytes"], f"files.{relative}.bytes"
        ):
            raise MorphologyArtifactIntegrityError(
                f"byte count mismatch for {relative}"
            )
        bodies.append(_parse_body(_read_json(payload_path, relative), relative))
        file_hashes.append((relative, actual_hash))
    bodies_tuple = tuple(sorted(bodies, key=lambda item: item.spatial_record.body_id))
    _validate_body_set(bodies_tuple)
    generation = manifest["generation"]
    if not isinstance(generation, Mapping):
        raise MorphologyArtifactSchemaError("manifest.generation must be an object")
    _require_keys(
        generation,
        {
            "generated_at_utc",
            "neuprint_python_version",
            "source_endpoint",
            "source_mode",
            "source_urls",
            "retrieval",
        },
        "manifest.generation",
    )
    source_urls_value = generation["source_urls"]
    if not isinstance(source_urls_value, Mapping):
        raise MorphologyArtifactSchemaError(
            "manifest.generation.source_urls must be an object"
        )
    try:
        source_mode, source_urls = _source_provenance(
            _string(generation["source_mode"], "generation.source_mode"),
            source_urls_value,
        )
    except MorphologyArtifactSchemaError:
        raise
    expected_retrieval = (
        MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC
        if source_mode == MALECNS_OFFICIAL_BULK_SWC_SOURCE
        else MORPHOLOGY_RETRIEVAL_NEUPRINT
    )
    if generation["retrieval"] != expected_retrieval:
        raise MorphologyArtifactIntegrityError("artifact retrieval provenance mismatch")
    if any(
        item.spatial_record.morphology_source != source_mode for item in bodies_tuple
    ):
        raise MorphologyArtifactIntegrityError(
            "body morphology source does not match artifact source mode"
        )
    identity = _artifact_identity(
        bodies_tuple,
        source_mode=source_mode,
        source_urls=source_urls,
    )
    artifact_id = _sha256_bytes(_json_bytes(identity))
    if manifest["artifact_id"] != artifact_id:
        raise MorphologyArtifactIntegrityError("artifact identity mismatch")
    for key, value in identity.items():
        if manifest[key] != value:
            raise MorphologyArtifactIntegrityError(f"manifest {key} mismatch")
    if circuit is not None:
        if tuple(item.spatial_record.body_id for item in bodies_tuple) == (
            DNP01_MORPHOLOGY_BODY_IDS
        ):
            validate_fixed_dnp01_mapping(circuit)
        else:
            validate_fixed_phase5g_mapping(circuit)
        for body in bodies_tuple:
            validate_spatial_record_against_circuit(body.spatial_record, circuit)
    return LoadedMorphologyArtifact(
        path=root,
        artifact_id=artifact_id,
        generated_at_utc=_string(
            generation["generated_at_utc"], "generation.generated_at_utc"
        ),
        neuprint_python_version=_string(
            generation["neuprint_python_version"], "generation.neuprint_python_version"
        ),
        source_endpoint=_string(
            generation["source_endpoint"], "generation.source_endpoint"
        ),
        source_mode=source_mode,
        source_urls=source_urls,
        retrieval=_string(generation["retrieval"], "generation.retrieval"),
        bodies=bodies_tuple,
        file_sha256=tuple(file_hashes),
        manifest=MappingProxyType(dict(manifest)),
    )


def generate_dnp01_morphology_artifact(
    client: Any,
    circuit: CircuitContract,
    output_root: str | Path,
) -> Path:
    """Acquire the fixed raw body set and export one validated artifact."""

    try:
        from importlib.metadata import version

        client_version = version("neuprint-python")
    except Exception:  # pragma: no cover - installed production dependency
        client_version = "unknown"
    bodies = acquire_dnp01_morphology(client, circuit)
    return export_morphology_artifact(
        bodies,
        output_root,
        neuprint_python_version=client_version,
    )


def generate_dnp01_morphology_artifact_from_official_bulk_swc(
    circuit: CircuitContract,
    output_root: str | Path,
    *,
    fetcher: Callable[[int, str], bytes] | None = None,
) -> Path:
    """Generate the fixed artifact from official MaleCNS bulk SWC files."""

    bodies, source_urls = acquire_dnp01_morphology_from_official_bulk_swc(
        circuit, fetcher=fetcher
    )
    return export_morphology_artifact(
        bodies,
        output_root,
        neuprint_python_version="not_used_for_official_bulk_swc",
        source_endpoint=OFFICIAL_MALECNS_BULK_SWC_BASE_URL,
        source_mode=MALECNS_OFFICIAL_BULK_SWC_SOURCE,
        source_urls=dict(source_urls),
        retrieval=MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC,
    )


def generate_phase5g_morphology_artifact_from_official_bulk_swc(
    circuit: CircuitContract,
    output_root: str | Path,
    *,
    fetcher: Callable[[int, str], bytes] | None = None,
) -> Path:
    """Generate the fixed six-body Phase 5G artifact from official raw SWCs."""

    bodies, source_urls = acquire_phase5g_morphology_from_official_bulk_swc(
        circuit, fetcher=fetcher
    )
    return export_morphology_artifact(
        bodies,
        output_root,
        neuprint_python_version="not_used_for_official_bulk_swc",
        source_endpoint=OFFICIAL_MALECNS_BULK_SWC_BASE_URL,
        source_mode=MALECNS_OFFICIAL_BULK_SWC_SOURCE,
        source_urls=dict(source_urls),
        retrieval=MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC,
    )


__all__ = [
    "DNP01_MORPHOLOGY_BODY_IDS",
    "EXPECTED_DNP01_MAPPING",
    "MORPHOLOGY_ARTIFACT_SCHEMA_VERSION",
    "MORPHOLOGY_BODY_SCHEMA_VERSION",
    "MORPHOLOGY_RETRIEVAL_NEUPRINT",
    "MORPHOLOGY_RETRIEVAL_OFFICIAL_BULK_SWC",
    "OFFICIAL_MALECNS_BULK_SWC_BASE_URL",
    "OFFICIAL_MALECNS_BULK_SWC_URLS",
    "OFFICIAL_MALECNS_PHASE5G_BULK_SWC_URLS",
    "EXPECTED_PHASE5G_MAPPING",
    "EXPECTED_PHASE5G_SOURCE",
    "PHASE5G_MORPHOLOGY_BODY_IDS",
    "PHASE5G_MORPHOLOGY_SAMPLE",
    "LoadedMorphologyArtifact",
    "MorphologyBodyRecord",
    "acquire_dnp01_morphology",
    "acquire_dnp01_morphology_from_official_bulk_swc",
    "acquire_phase5g_morphology_from_official_bulk_swc",
    "export_morphology_artifact",
    "generate_dnp01_morphology_artifact",
    "generate_dnp01_morphology_artifact_from_official_bulk_swc",
    "generate_phase5g_morphology_artifact_from_official_bulk_swc",
    "load_morphology_artifact",
    "validate_fixed_dnp01_mapping",
    "validate_fixed_phase5g_mapping",
]
