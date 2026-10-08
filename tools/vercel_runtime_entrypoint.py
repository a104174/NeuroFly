"""Wire the immutable built release into the existing FastAPI factory."""

import os
import sys
from pathlib import Path

from tools.vercel_runtime_build import MANIFEST_ID


def application(root):
    release = Path(root).resolve() / ".neurofly-release"
    source = release / "src"
    if not (source / "neurofly/http_api.py").is_file():
        raise FileNotFoundError("provisioned application source is missing")
    sys.path.insert(0, str(source))
    from neurofly.http_api import create_app_from_env
    from neurofly.runtime_bundle import INVENTORY_ID

    os.environ.update(
        NEUROFLY_RUNTIME_MODE="provisioned",
        NEUROFLY_RUNTIME_RELEASE_ROOT=str(release),
        NEUROFLY_RUNTIME_INVENTORY_ID=INVENTORY_ID,
        NEUROFLY_RUNTIME_MANIFEST_ID=MANIFEST_ID,
        NEUROFLY_EXPERIMENT_ARTIFACT_ROOT=str(release / "data/derived/experiments"),
        NEUROFLY_CIRCUIT_CONTRACT_ROOT=str(
            release / "data/derived/malecns/looming_giant_fiber_v1"
        ),
    )
    # These optional local overrides must never redirect a deployment to local data.
    for name in (
        "NEUROFLY_SCENARIO_ARTIFACT_PATH",
        "NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT",
        "NEUROFLY_MOTOR_EXPERIMENT_ARTIFACT_ROOT",
    ):
        os.environ.pop(name, None)
    os.chdir(release)
    return create_app_from_env()
