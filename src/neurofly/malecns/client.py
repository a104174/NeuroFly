"""Credential-safe construction of an authenticated MaleCNS client."""

import os
from typing import Any

from neurofly.malecns.errors import MaleCNSAccessError
from neurofly.malecns.models import (
    CREDENTIAL_ENV_VAR,
    MALECNS_DATASET,
    NEUPRINT_ENDPOINT,
)


def create_client() -> Any:
    """Create a neuPrint client pinned to the official MaleCNS v1.0 dataset."""
    if not os.environ.get(CREDENTIAL_ENV_VAR):
        raise MaleCNSAccessError(
            f"Missing {CREDENTIAL_ENV_VAR}; set it to your neuPrint application "
            "credentials before accessing MaleCNS."
        )

    try:
        from neuprint import Client

        client = Client(
            NEUPRINT_ENDPOINT,
            dataset=MALECNS_DATASET,
            progress=False,
        )
    except Exception:
        # Do not propagate third-party request details that might expose headers.
        raise MaleCNSAccessError(
            "Could not authenticate or connect to the official neuPrint MaleCNS "
            "dataset. Check the credential, network, and service availability."
        ) from None

    if client.dataset != MALECNS_DATASET:
        raise MaleCNSAccessError(
            f"Unexpected neuPrint dataset {client.dataset!r}; expected "
            f"{MALECNS_DATASET!r}."
        )
    return client
