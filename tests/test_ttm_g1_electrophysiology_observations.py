"""Phase 8S tests: protocol-specific observations, never model parameters."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observation_artifacts import (
    TTMG1ObservationArtifactError,
    export_ttm_g1_observation_artifact,
    load_ttm_g1_observation_artifact,
    replay_ttm_g1_observation_artifact,
    validate_and_replay_contract,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    ARTIFACT_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    build_observation_contract,
    canonical_json_bytes,
    canonical_sha256,
)

EXPECTED_QUANTITIES = [
    "G1_RESTING_MEMBRANE_POTENTIAL",
    "G1_EVOKED_JUNCTION_POTENTIAL",
    "G1_MINIATURE_JUNCTION_POTENTIAL",
    "G1_EQUILIBRIUM_POTENTIAL_ANALYSIS_INPUT",
    "G1_QUANTAL_CONTENT",
    "G1_SPONTANEOUS_MEJP_FREQUENCY",
    "G1_DEPRESSION_PROTOCOL_OUTCOME",
    "G1_VESICLE_RECYCLING_RATE",
    "TTMN_REGION_STIM_TO_TTM_POTENTIAL_ONSET_LATENCY",
]
FORBIDDEN_PARAMETER_KEYS = {
    "model_gain",
    "model_tau",
    "model_threshold",
    "model_v_rest",
    "nmj_delay_parameter",
    "activation_gain",
    "force_gain",
    "to_model_parameters",
    "build_ttm_model_config",
}


def _rows(contract: dict) -> dict[str, dict]:
    return {row["quantity_type"]: row for row in contract["result"]["observations"]}


def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key.lower()
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)


def test_canonical_contract_has_exact_nine_ordered_observation_records() -> None:
    contract = build_observation_contract()
    records = contract["result"]["observations"]

    assert contract["schema_version"] == CONTRACT_SCHEMA_VERSION
    assert contract["result"]["observation_count"] == 9
    assert [row["quantity_type"] for row in records] == EXPECTED_QUANTITIES
    assert len({row["observation_id"] for row in records}) == 9
    assert contract == build_observation_contract()
    assert contract["contract_id"] == canonical_sha256(
        {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "config_sha256": contract["config_sha256"],
            "result_sha256": contract["result_sha256"],
        }
    )


def test_values_keep_their_source_and_measurement_classifications() -> None:
    rows = _rows(build_observation_contract())
    assert rows["G1_RESTING_MEMBRANE_POTENTIAL"]["value"] == -95
    assert rows["G1_RESTING_MEMBRANE_POTENTIAL"]["value_qualifier"] == "APPROXIMATE"
    assert rows["G1_RESTING_MEMBRANE_POTENTIAL"]["record_classification"] == (
        "DESCRIPTIVE_MEASURED_VALUE"
    )

    assert rows["G1_EVOKED_JUNCTION_POTENTIAL"]["value"] == 45
    assert rows["G1_EVOKED_JUNCTION_POTENTIAL"]["record_classification"] == (
        "PRIOR_PRIMARY_RESULT_REUSED"
    )
    assert "koenig_ikeda_2005" in rows["G1_EVOKED_JUNCTION_POTENTIAL"]["evidence_refs"]
    prior_protocol = rows["G1_EVOKED_JUNCTION_POTENTIAL"]["protocol"]
    assert prior_protocol["dimensions"]["preparation"] is None
    assert prior_protocol["dimension_status"]["preparation"] == "NOT_VERIFIED"
    assert prior_protocol["dimensions"]["recording_method"] is None

    assert rows["G1_MINIATURE_JUNCTION_POTENTIAL"]["value"] == 0.5
    assert rows["G1_MINIATURE_JUNCTION_POTENTIAL"]["units"] == "mV"
    assert rows["G1_MINIATURE_JUNCTION_POTENTIAL"]["value_qualifier"] == (
        "APPROXIMATE_HISTOGRAM_SUPPORTED"
    )
    assert rows["G1_MINIATURE_JUNCTION_POTENTIAL"]["record_classification"] == (
        "DESCRIPTIVE_MEASURED_VALUE"
    )

    assert rows["G1_EQUILIBRIUM_POTENTIAL_ANALYSIS_INPUT"]["value"] == -10
    assert rows["G1_EQUILIBRIUM_POTENTIAL_ANALYSIS_INPUT"]["record_classification"] == (
        "ANALYSIS_INPUT_FROM_PRIOR_SOURCE"
    )

    derived = rows["G1_QUANTAL_CONTENT"]
    assert derived["value"] == 191
    assert derived["units"] == "quanta"
    assert derived["record_classification"] == "DERIVED_QUANTITY"
    assert len(derived["derived_from_observation_ids"]) == 3
    assert derived["derivation"]["notation"]["m"] == "derived quantal content"

    rate = rows["G1_VESICLE_RECYCLING_RATE"]
    assert rate["value"] == 0.24
    assert rate["record_classification"] == "DERIVED_QUANTITY"
    assert rate["derived_from_observation_ids"] == []
    assert "not separate records" in rate["derivation"]["note"]
    recycling_inputs = rate["derivation"]["comparison_inputs"]
    assert recycling_inputs["recycling_permitted_quanta"] == 286500
    assert recycling_inputs["recycling_permitted_uncertainty"] == 9680
    assert recycling_inputs["recycling_permitted_uncertainty_kind"] == (
        "UNKNOWN_NOT_ESTABLISHED"
    )
    assert recycling_inputs["recycling_permitted_sample_size"] == 5
    assert recycling_inputs["recycling_blocked_quanta"] == 31800
    assert recycling_inputs["active_zone_denominator_qualifier"] == "APPROXIMATE"


def test_unknown_uncertainty_and_protocol_details_are_not_imputed() -> None:
    rows = _rows(build_observation_contract())
    spontaneous = rows["G1_SPONTANEOUS_MEJP_FREQUENCY"]
    assert spontaneous["value"] == 7
    assert spontaneous["uncertainty_value"] == 3
    assert spontaneous["uncertainty_kind"] == "UNKNOWN_NOT_ESTABLISHED"
    assert spontaneous["sample_size"] == 5
    assert spontaneous["sample_size_unit"] == "flies"
    assert spontaneous["protocol"]["dimensions"]["temperature_c"] == 19

    one_hz = rows["G1_DEPRESSION_PROTOCOL_OUTCOME"]
    protocol = one_hz["protocol"]["dimensions"]
    assert one_hz["value"] == "NO_OBSERVED_DEPRESSION_UNDER_THIS_PROTOCOL"
    assert one_hz["record_classification"] == "CATEGORICAL_OBSERVATION"
    assert protocol["genotype"] == "temperature-sensitive shibire^ts1 (shi)"
    assert protocol["temperature_c"] == 19
    assert protocol["stimulation_frequency_hz"] == 1
    assert protocol["stimulus_count"] == 1500
    assert "permitted" in protocol["recycling_condition"]

    latency = rows["TTMN_REGION_STIM_TO_TTM_POTENTIAL_ONSET_LATENCY"]
    latency_protocol = latency["protocol"]["dimensions"]
    assert latency["value"] == 0.84
    assert latency["uncertainty_value"] == 0.02
    assert latency["uncertainty_kind"] == "MEAN_SEM"
    assert latency["sample_size"] == 8
    assert latency_protocol["developmental_age"] == "24 hours post-eclosion"
    assert latency_protocol["temperature_c"] is None
    assert latency["latency_semantics"]["is_isolated_nmj_delay"] is False
    assert latency["latency_semantics"]["latency_kind"] == (
        "DIRECT_MOTOR_NEURON_REGION_STIMULATION_TO_TTM_POTENTIAL_ONSET"
    )


def test_g1_scope_is_neither_whole_ttm_nor_exact_malecns_body_physiology() -> None:
    contract = build_observation_contract()
    for row in contract["result"]["observations"]:
        scope = row["biological_scope"]
        assert scope["whole_ttm_inference"] is False
        assert scope["malecns_body_id"] is None
        assert scope["identity_mapping_scope"] == "CLASS_LEVEL_EVIDENCE_ONLY"
        if row["biological_scope"]["structure_scope"] == "SINGLE_G1_FIBER":
            assert scope["structure_scope"] == "SINGLE_G1_FIBER"
            assert scope["recorded_fiber"] == "G1"
        assert row["model_comparability"]["status"] == "OBSERVATION_MODEL_REQUIRED"
        assert row["model_comparability"]["current_neurofly_observable"] is None


def test_manifest_keeps_2005_depression_qualitative_and_excludes_figures() -> None:
    config = build_observation_contract()["config"]
    sources = {
        row["evidence_id"]: row for row in config["evidence_manifest"]["sources"]
    }
    assert sources["koenig_ikeda_2005"]["verification_scope"] == (
        "PRIMARY_ABSTRACT_ONLY_FOR_CURRENT_CONTRACT"
    )
    qualitative = config["evidence_manifest"]["qualitative_context"]
    assert len(qualitative) == 1
    assert qualitative[0]["is_observation_record"] is False
    assert qualitative[0]["quantitative_depression_series_pinned"] is False
    assert (
        "QUANTITATIVE_KOENIG_IKEDA_2005_DEPRESSION_SERIES"
        in config["explicit_exclusions"]
    )
    assert "FIGURE_DIGITIZED_OR_OCR_DERIVED_VALUES" in config["explicit_exclusions"]


def test_observation_contract_contains_no_model_parameter_or_runtime_fields() -> None:
    contract = build_observation_contract()
    keys = set(_all_keys(contract))
    assert not (keys & FORBIDDEN_PARAMETER_KEYS)
    assert "model_comparability" in keys
    assert "activation" not in keys
    assert "force" not in keys
    assert "membrane_ode" not in keys


@pytest.mark.parametrize(
    ("quantity", "mutate"),
    [
        (
            "G1_RESTING_MEMBRANE_POTENTIAL",
            lambda row: row.update(record_classification="DIRECT_MEASUREMENT"),
        ),
        (
            "G1_EVOKED_JUNCTION_POTENTIAL",
            lambda row: row.update(evidence_refs=["kadas_etal_2019"]),
        ),
        (
            "G1_MINIATURE_JUNCTION_POTENTIAL",
            lambda row: row.update(units="events_per_s"),
        ),
        (
            "G1_EQUILIBRIUM_POTENTIAL_ANALYSIS_INPUT",
            lambda row: row.update(record_classification="DIRECT_MEASUREMENT"),
        ),
        (
            "G1_QUANTAL_CONTENT",
            lambda row: row.update(derivation={"method": "raw measurement"}),
        ),
        (
            "G1_SPONTANEOUS_MEJP_FREQUENCY",
            lambda row: row.update(uncertainty_kind="MEAN_SEM"),
        ),
        (
            "G1_DEPRESSION_PROTOCOL_OUTCOME",
            lambda row: row["protocol"]["dimensions"].update(stimulus_count=100),
        ),
        (
            "G1_VESICLE_RECYCLING_RATE",
            lambda row: row.update(record_classification="DIRECT_MEASUREMENT"),
        ),
        (
            "TTMN_REGION_STIM_TO_TTM_POTENTIAL_ONSET_LATENCY",
            lambda row: row["latency_semantics"].update(is_isolated_nmj_delay=True),
        ),
        (
            "TTMN_REGION_STIM_TO_TTM_POTENTIAL_ONSET_LATENCY",
            lambda row: row.update(uncertainty_kind="SD"),
        ),
        (
            "TTMN_REGION_STIM_TO_TTM_POTENTIAL_ONSET_LATENCY",
            lambda row: row.update(sample_size=5),
        ),
    ],
)
def test_semantic_observation_mutations_fail_offline_replay(quantity, mutate) -> None:
    contract = build_observation_contract()
    changed = copy.deepcopy(contract)
    record = next(
        row
        for row in changed["result"]["observations"]
        if row["quantity_type"] == quantity
    )
    mutate(record)
    with pytest.raises(TTMG1ObservationArtifactError):
        validate_and_replay_contract(changed)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda c: c["config"]["explicit_exclusions"].pop(),
        lambda c: c["result"]["observations"][0]["biological_scope"].update(
            whole_ttm_inference=True
        ),
        lambda c: c["result"]["observations"][0]["biological_scope"].update(
            malecns_body_id=800146
        ),
        lambda c: c["result"]["observations"][0].update(applicability="UNRESOLVED"),
        lambda c: c["result"]["observations"][0]["protocol"]["dimensions"].update(
            temperature_c=float("nan")
        ),
    ],
)
def test_contract_level_mutations_fail_offline_replay(mutate) -> None:
    changed = copy.deepcopy(build_observation_contract())
    mutate(changed)
    with pytest.raises(TTMG1ObservationArtifactError):
        validate_and_replay_contract(changed)


def test_content_addressed_artifact_generation_and_full_replay(tmp_path: Path) -> None:
    contract = build_observation_contract()
    path = tmp_path / contract["contract_id"]
    artifact = export_ttm_g1_observation_artifact(contract, path)
    loaded = load_ttm_g1_observation_artifact(path)
    replayed = replay_ttm_g1_observation_artifact(path)

    assert artifact.artifact_id == contract["contract_id"]
    assert loaded.artifact_id == replayed.artifact_id
    assert dict(loaded.contract) == contract
    assert replayed.summary()["observation_count"] == 9
    assert set(item.name for item in path.iterdir()) == {
        "observation_contract.json",
        "manifest.json",
    }

    duplicate = tmp_path / "second" / contract["contract_id"]
    export_ttm_g1_observation_artifact(contract, duplicate)
    for filename in ("observation_contract.json", "manifest.json"):
        assert (path / filename).read_bytes() == (duplicate / filename).read_bytes()


def test_artifact_file_tampering_fails_integrity_check(tmp_path: Path) -> None:
    contract = build_observation_contract()
    path = tmp_path / contract["contract_id"]
    export_ttm_g1_observation_artifact(contract, path)
    contract_path = path / "observation_contract.json"
    tampered = json.loads(contract_path.read_text(encoding="utf-8"))
    tampered["result"]["observations"][0]["value"] = -94
    contract_path.write_bytes(canonical_json_bytes(tampered, newline=True))
    with pytest.raises(TTMG1ObservationArtifactError):
        load_ttm_g1_observation_artifact(path)


def test_observation_identity_changes_with_semantic_value() -> None:
    contract = build_observation_contract()
    row = contract["result"]["observations"][0]
    identity_without_id = {
        key: value for key, value in row.items() if key != "observation_id"
    }
    original = canonical_sha256(identity_without_id)
    changed = copy.deepcopy(identity_without_id)
    changed["value"] = -94
    assert canonical_sha256(changed) != original


def test_contract_identity_changes_when_observation_semantics_change() -> None:
    contract = build_observation_contract()
    changed = copy.deepcopy(contract)
    changed["result"]["observations"][0]["value"] = -94
    changed["result_sha256"] = canonical_sha256(changed["result"])
    changed["contract_id"] = canonical_sha256(
        {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "config_sha256": changed["config_sha256"],
            "result_sha256": changed["result_sha256"],
        }
    )
    assert changed["contract_id"] != contract["contract_id"]
