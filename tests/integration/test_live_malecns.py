"""Opt-in authenticated smoke test against the official MaleCNS dataset."""

import os

import pytest

from neurofly.malecns import acquire_candidate, create_client, validate_snapshot


@pytest.mark.integration
def test_live_candidate_invariants() -> None:
    if not os.environ.get("NEUPRINT_APPLICATION_CREDENTIALS"):
        pytest.skip("NEUPRINT_APPLICATION_CREDENTIALS is not set")
    snapshot = acquire_candidate(create_client())
    report = validate_snapshot(snapshot)
    assert report.total_neuron_count == 313
    assert report.induced_connection_count > 0
