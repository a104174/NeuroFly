"""Minimal GET-only HTTP adapter for the Phase 4A application boundary.

This module is deliberately the only NeuroFly module that imports FastAPI.
It translates requests into calls to :class:`ExperimentArtifactStore` and
returns the already validated, JSON-safe Phase 4A DTOs.  It never executes an
experiment and contains no stimulus, encoder, neural, or comparison logic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from neurofly.experiment_api import (
    APPLICATION_API_SCHEMA_VERSION,
    ArtifactNotFoundError,
    ArtifactPathError,
    ArtifactStoreError,
    BodyTelemetryUnavailableError,
    ComparisonUnavailableError,
    CorruptedArtifactError,
    ExperimentApiError,
    ExperimentArtifactStore,
    InvalidArtifactIdError,
    InvalidRangeError,
    UnsupportedArtifactError,
)
from neurofly.morphology_api import (
    MORPHOLOGY_API_SCHEMA_VERSION,
    CorruptedMorphologyArtifactError,
    InvalidMorphologyArtifactIdError,
    MorphologyApiError,
    MorphologyArtifactNotFoundError,
    MorphologyArtifactStore,
    MorphologyBodyNotFoundError,
    MorphologyPathError,
    MorphologyStoreError,
    MorphologyStoreUnavailableError,
    UnsupportedMorphologyArtifactError,
)

HTTP_API_SCHEMA_VERSION = "experiment_http_v1"
HTTP_API_VERSION = "v1"
HTTP_ERROR_SCHEMA_VERSION = "experiment_http_error_v1"
ARTIFACT_ROOT_ENV = "NEUROFLY_EXPERIMENT_ARTIFACT_ROOT"
MORPHOLOGY_ARTIFACT_ROOT_ENV = "NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT"


def _error_payload(code: str, message: str) -> dict[str, str]:
    return {
        "schema": HTTP_ERROR_SCHEMA_VERSION,
        "code": code,
        "message": message,
    }


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=_error_payload(code, message),
    )


def _store(request: Request) -> ExperimentArtifactStore:
    try:
        return request.app.state.experiment_artifact_store
    except AttributeError as exc:  # pragma: no cover - app factory invariant
        raise RuntimeError("experiment artifact store is not configured") from exc


def _morphology_store(request: Request) -> MorphologyArtifactStore:
    store = getattr(request.app.state, "morphology_artifact_store", None)
    if store is None:
        raise MorphologyStoreUnavailableError(
            "morphology artifact root is not configured"
        )
    return store


async def _invalid_request_handler(
    _request: Request, _exc: RequestValidationError
) -> JSONResponse:
    return _error_response(400, "invalid_request", "request parameters are invalid")


async def _http_error_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    if exc.status_code == 405:
        return _error_response(405, "method_not_allowed", "only GET is supported")
    if exc.status_code == 404:
        return _error_response(404, "route_not_found", "requested route was not found")
    return _error_response(
        400, "http_request_error", "HTTP request could not be handled"
    )


async def _invalid_id_handler(
    _request: Request, _exc: InvalidArtifactIdError
) -> JSONResponse:
    return _error_response(400, "invalid_artifact_id", "artifact_id is malformed")


async def _range_handler(_request: Request, _exc: InvalidRangeError) -> JSONResponse:
    return _error_response(
        400,
        "invalid_time_range",
        "timeline range is invalid or not aligned to simulation samples",
    )


async def _not_found_handler(
    _request: Request, _exc: ArtifactNotFoundError
) -> JSONResponse:
    return _error_response(404, "artifact_not_found", "artifact was not found")


async def _body_unavailable_handler(
    _request: Request, _exc: BodyTelemetryUnavailableError
) -> JSONResponse:
    return _error_response(
        404,
        "body_telemetry_unavailable",
        "body telemetry is unavailable in this artifact",
    )


async def _path_error_handler(
    _request: Request, _exc: ArtifactPathError
) -> JSONResponse:
    return _error_response(409, "unsafe_artifact_path", "artifact path is unsafe")


async def _corrupt_handler(
    _request: Request, _exc: CorruptedArtifactError
) -> JSONResponse:
    return _error_response(
        409,
        "artifact_integrity_failure",
        "artifact failed integrity validation",
    )


async def _unsupported_handler(
    _request: Request, _exc: UnsupportedArtifactError
) -> JSONResponse:
    return _error_response(
        409,
        "unsupported_artifact_schema",
        "artifact schema is unsupported",
    )


async def _store_error_handler(
    _request: Request, _exc: ArtifactStoreError
) -> JSONResponse:
    return _error_response(
        500,
        "artifact_store_error",
        "artifact store could not be read",
    )


async def _comparison_error_handler(
    _request: Request, _exc: ComparisonUnavailableError
) -> JSONResponse:
    return _error_response(
        500,
        "comparison_unavailable",
        "comparison could not be constructed",
    )


async def _application_error_handler(
    _request: Request, _exc: ExperimentApiError
) -> JSONResponse:
    return _error_response(
        500,
        "application_error",
        "application request could not be completed",
    )


async def _unexpected_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    # Never serialize exception text: it may contain local paths or other
    # process details.  The server log remains the appropriate diagnostic
    # channel for deployment operators.
    return _error_response(
        500,
        "internal_error",
        "internal server error",
    )


async def _invalid_morphology_id_handler(
    _request: Request, _exc: InvalidMorphologyArtifactIdError
) -> JSONResponse:
    return _error_response(
        400, "invalid_morphology_artifact_id", "morphology artifact ID is malformed"
    )


async def _morphology_not_found_handler(
    _request: Request, _exc: MorphologyArtifactNotFoundError
) -> JSONResponse:
    return _error_response(
        404, "morphology_artifact_not_found", "morphology artifact was not found"
    )


async def _morphology_body_not_found_handler(
    _request: Request, _exc: MorphologyBodyNotFoundError
) -> JSONResponse:
    return _error_response(
        404, "morphology_body_not_found", "morphology body was not found"
    )


async def _morphology_path_handler(
    _request: Request, _exc: MorphologyPathError
) -> JSONResponse:
    return _error_response(
        409, "unsafe_morphology_path", "morphology artifact path is unsafe"
    )


async def _corrupt_morphology_handler(
    _request: Request, _exc: CorruptedMorphologyArtifactError
) -> JSONResponse:
    return _error_response(
        409,
        "morphology_integrity_failure",
        "morphology artifact failed integrity validation",
    )


async def _unsupported_morphology_handler(
    _request: Request, _exc: UnsupportedMorphologyArtifactError
) -> JSONResponse:
    return _error_response(
        409,
        "unsupported_morphology_schema",
        "morphology artifact schema is unsupported",
    )


async def _morphology_unavailable_handler(
    _request: Request, _exc: MorphologyStoreUnavailableError
) -> JSONResponse:
    return _error_response(
        503,
        "morphology_store_unavailable",
        "morphology artifact root is not configured",
    )


async def _morphology_store_handler(
    _request: Request, _exc: MorphologyStoreError
) -> JSONResponse:
    return _error_response(
        500, "morphology_store_error", "morphology artifact store could not be read"
    )


async def _morphology_api_handler(
    _request: Request, _exc: MorphologyApiError
) -> JSONResponse:
    return _error_response(
        500, "morphology_application_error", "morphology request could not be completed"
    )


def _register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _invalid_request_handler)
    app.add_exception_handler(StarletteHTTPException, _http_error_handler)
    app.add_exception_handler(InvalidArtifactIdError, _invalid_id_handler)
    app.add_exception_handler(InvalidRangeError, _range_handler)
    app.add_exception_handler(ArtifactNotFoundError, _not_found_handler)
    app.add_exception_handler(BodyTelemetryUnavailableError, _body_unavailable_handler)
    app.add_exception_handler(ArtifactPathError, _path_error_handler)
    app.add_exception_handler(CorruptedArtifactError, _corrupt_handler)
    app.add_exception_handler(UnsupportedArtifactError, _unsupported_handler)
    app.add_exception_handler(ComparisonUnavailableError, _comparison_error_handler)
    app.add_exception_handler(ArtifactStoreError, _store_error_handler)
    app.add_exception_handler(ExperimentApiError, _application_error_handler)
    app.add_exception_handler(
        InvalidMorphologyArtifactIdError, _invalid_morphology_id_handler
    )
    app.add_exception_handler(
        MorphologyArtifactNotFoundError, _morphology_not_found_handler
    )
    app.add_exception_handler(
        MorphologyBodyNotFoundError, _morphology_body_not_found_handler
    )
    app.add_exception_handler(MorphologyPathError, _morphology_path_handler)
    app.add_exception_handler(
        CorruptedMorphologyArtifactError, _corrupt_morphology_handler
    )
    app.add_exception_handler(
        UnsupportedMorphologyArtifactError, _unsupported_morphology_handler
    )
    app.add_exception_handler(
        MorphologyStoreUnavailableError, _morphology_unavailable_handler
    )
    app.add_exception_handler(MorphologyStoreError, _morphology_store_handler)
    app.add_exception_handler(MorphologyApiError, _morphology_api_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)


def create_app(
    artifact_root: str | Path,
    morphology_artifact_root: str | Path | None = None,
) -> FastAPI:
    """Create an isolated read-only API over one configured artifact root."""

    store = ExperimentArtifactStore(artifact_root)
    app = FastAPI(
        title="NeuroFly read-only experiment API",
        version=HTTP_API_VERSION,
        description=(
            "GET-only transport adapter for completed NeuroFly experiment "
            "artifacts. Requests never run the simulator."
        ),
    )
    app.state.experiment_artifact_store = store
    app.state.morphology_artifact_store = (
        None
        if morphology_artifact_root is None
        else MorphologyArtifactStore(morphology_artifact_root)
    )
    _register_error_handlers(app)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, Any]:
        return {
            "schema": HTTP_API_SCHEMA_VERSION,
            "status": "ok",
            "read_only": True,
        }

    @app.get("/api/v1", tags=["system"])
    def api_info() -> dict[str, Any]:
        return {
            "schema": HTTP_API_SCHEMA_VERSION,
            "api": "neurofly",
            "http_api_version": HTTP_API_VERSION,
            "application_contract": APPLICATION_API_SCHEMA_VERSION,
            "read_only": True,
        }

    @app.get("/api/v1/experiments", tags=["experiments"])
    def list_experiments(request: Request) -> dict[str, Any]:
        summaries = _store(request).list_experiment_summaries()
        return {
            "schema": HTTP_API_SCHEMA_VERSION,
            "kind": "experiment_list",
            "experiments": [summary.to_dict() for summary in summaries],
            "count": len(summaries),
        }

    @app.get("/api/v1/experiments/{artifact_id}", tags=["experiments"])
    def get_experiment(request: Request, artifact_id: str) -> dict[str, Any]:
        return _store(request).get_experiment(artifact_id).to_dict()

    @app.get("/api/v1/experiments/{artifact_id}/timeline", tags=["telemetry"])
    def get_timeline(
        request: Request,
        artifact_id: str,
        start_ms: float | None = Query(default=None),
        end_ms: float | None = Query(default=None),
    ) -> dict[str, Any]:
        return (
            _store(request)
            .get_timeline(
                artifact_id,
                start_ms=start_ms,
                end_ms=end_ms,
            )
            .to_dict()
        )

    @app.get("/api/v1/experiments/{artifact_id}/bodies/{body_id}", tags=["telemetry"])
    def get_body(
        request: Request,
        artifact_id: str,
        body_id: int,
    ) -> dict[str, Any]:
        return _store(request).get_body_telemetry(artifact_id, body_id).to_dict()

    @app.get("/api/v1/experiments/{artifact_id}/spikes", tags=["events"])
    def get_spikes(request: Request, artifact_id: str) -> dict[str, Any]:
        events = _store(request).get_spike_events(artifact_id)
        return {
            "schema": HTTP_API_SCHEMA_VERSION,
            "kind": "spike_events",
            "artifact_id": artifact_id,
            "spike_events": [event.to_dict() for event in events],
            "spike_event_count": len(events),
        }

    @app.get("/api/v1/experiments/{artifact_id}/events", tags=["events"])
    def get_events(request: Request, artifact_id: str) -> dict[str, Any]:
        events = _store(request).get_delivered_events(artifact_id)
        return {
            "schema": HTTP_API_SCHEMA_VERSION,
            "kind": "delivered_events",
            "artifact_id": artifact_id,
            "delivered_events": [event.to_dict() for event in events],
            "delivered_event_count": len(events),
        }

    @app.get("/api/v1/comparisons", tags=["comparisons"])
    def get_comparison(
        request: Request,
        artifact_a: str = Query(...),
        artifact_b: str = Query(...),
    ) -> dict[str, Any]:
        return _store(request).get_comparison(artifact_a, artifact_b).to_dict()

    @app.get("/api/v1/morphology", tags=["morphology"])
    def list_morphology(request: Request) -> dict[str, Any]:
        artifacts = _morphology_store(request).list_artifacts()
        return {
            "schema": MORPHOLOGY_API_SCHEMA_VERSION,
            "kind": "morphology_artifact_list",
            "artifacts": [artifact.to_dict() for artifact in artifacts],
            "count": len(artifacts),
        }

    @app.get("/api/v1/morphology/{artifact_id}", tags=["morphology"])
    def get_morphology(request: Request, artifact_id: str) -> dict[str, Any]:
        return _morphology_store(request).get_artifact(artifact_id).to_dict()

    @app.get(
        "/api/v1/morphology/{artifact_id}/bodies/{body_id}",
        tags=["morphology"],
    )
    def get_morphology_body(
        request: Request, artifact_id: str, body_id: int
    ) -> dict[str, Any]:
        return _morphology_store(request).get_body(artifact_id, body_id).to_dict()

    return app


def create_app_from_env() -> FastAPI:
    """Uvicorn-compatible zero-argument factory using one explicit env var."""

    configured = os.environ.get(ARTIFACT_ROOT_ENV)
    if not configured:
        raise RuntimeError(
            f"{ARTIFACT_ROOT_ENV} must identify an existing artifact directory"
        )
    morphology_root = os.environ.get(MORPHOLOGY_ARTIFACT_ROOT_ENV)
    return create_app(configured, morphology_root)


__all__ = [
    "ARTIFACT_ROOT_ENV",
    "HTTP_API_SCHEMA_VERSION",
    "HTTP_API_VERSION",
    "HTTP_ERROR_SCHEMA_VERSION",
    "MORPHOLOGY_ARTIFACT_ROOT_ENV",
    "create_app",
    "create_app_from_env",
]
