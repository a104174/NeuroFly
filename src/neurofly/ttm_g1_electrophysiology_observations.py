"""Curated, observation-only adult Drosophila TTM G1 evidence.

The records in this module pin literature observations and protocol metadata.
They are not NeuroFly model parameters and cannot be exported as such.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

CONTRACT_SCHEMA_VERSION = "ttm_g1_electrophysiology_observation_contract_v1"
CONFIG_SCHEMA_VERSION = "ttm_g1_electrophysiology_observation_config_v1"
RESULT_SCHEMA_VERSION = "ttm_g1_electrophysiology_observation_result_v1"
ARTIFACT_SCHEMA_VERSION = "ttm_g1_electrophysiology_observation_artifact_v1"

RECORD_CLASSIFICATIONS = frozenset(
    {
        "DIRECT_MEASUREMENT",
        "DESCRIPTIVE_MEASURED_VALUE",
        "SUMMARY_STATISTIC",
        "DERIVED_QUANTITY",
        "PRIOR_PRIMARY_RESULT_REUSED",
        "ANALYSIS_INPUT_FROM_PRIOR_SOURCE",
        "CATEGORICAL_OBSERVATION",
    }
)
APPLICABILITY_VALUES = frozenset(
    {
        "G1_FIBER_VALIDATION_TARGET",
        "TTM_CLASS_CONTEXT",
        "COMPOSITE_LATENCY_VALIDATION_TARGET",
        "ANALYSIS_CONTEXT_ONLY",
        "NOT_DIRECTLY_MAPPABLE_TO_CURRENT_MODEL",
    }
)
UNCERTAINTY_KINDS = frozenset(
    {"MEAN_SEM", "SD", "UNKNOWN_NOT_ESTABLISHED", "NOT_REPORTED", "NOT_APPLICABLE"}
)
MODEL_COMPARABILITY_STATUS = "OBSERVATION_MODEL_REQUIRED"


class TTMG1ObservationContractError(ValueError):
    """Invalid, mutated, or non-replayable TTM G1 observation contract."""


def canonical_json_bytes(value: Any, *, newline: bool = False) -> bytes:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise TTMG1ObservationContractError(
            "observation contract must be deterministic JSON"
        ) from exc
    return payload + (b"\n" if newline else b"")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _source_manifest() -> dict[str, Any]:
    return {
        "schema_version": "ttm_g1_electrophysiology_evidence_manifest_v1",
        "sources": [
            {
                "evidence_id": "koenig_ikeda_2007",
                "authors": ["Koenig JH", "Ikeda K"],
                "year": 2007,
                "title": (
                    "Release and Recycling of the Readily Releasable Vesicle "
                    "Population in a Synapse Possessing No Reserve Population"
                ),
                "journal": "Journal of Neurophysiology",
                "volume": "97",
                "pages": "4048-4057",
                "doi": "10.1152/jn.01258.2006",
                "source_role": "PRIMARY_G1_OBSERVATION_AND_ANALYSIS_SOURCE",
                "verification_scope": (
                    "PUBLISHER_INDEXED_FULL_TEXT_METHODS_RESULTS_DISCUSSION_CAPTIONS"
                ),
                "source_url": (
                    "https://journals.physiology.org/doi/full/10.1152/jn.01258.2006"
                ),
                "limitations": [
                    (
                        "Direct publisher-page retrieval returned HTTP 403 during "
                        "Phase 8R; inspected publisher-indexed primary-text passages "
                        "were used."
                    ),
                    "No values were digitized from figures.",
                    "The experimental G1 fiber is not mapped to a MaleCNS body ID.",
                ],
            },
            {
                "evidence_id": "koenig_ikeda_2005",
                "authors": ["Koenig JH", "Ikeda K"],
                "year": 2005,
                "title": (
                    "Relationship of the Reserve Vesicle Population to Synaptic "
                    "Depression in the Tergotrochanteral and Dorsal Longitudinal "
                    "Muscles of Drosophila"
                ),
                "journal": "Journal of Neurophysiology",
                "volume": "94",
                "pages": "2111-2119",
                "doi": "10.1152/jn.00323.2005",
                "source_role": "PRIOR_RESULT_AND_QUALITATIVE_DEPRESSION_CONTEXT",
                "verification_scope": "PRIMARY_ABSTRACT_ONLY_FOR_CURRENT_CONTRACT",
                "source_url": "https://pubmed.ncbi.nlm.nih.gov/15958601/",
                "limitations": [
                    "Full methods, results, and figures were not verified here.",
                    "No quantitative depression series or figure value is pinned.",
                    (
                        "The 45 mV value is identified as a prior result reused by "
                        "the 2007 analysis; its 2005 protocol details remain "
                        "unverified here."
                    ),
                ],
            },
            {
                "evidence_id": "kadas_etal_2019",
                "authors": ["Kadas D", "Duch C", "Consoulas C"],
                "year": 2019,
                "title": (
                    "Postnatal Increases in Axonal Conduction Velocity of an "
                    "Identified Drosophila Interneuron Require Fast Sodium, "
                    "L-Type Calcium and Shaker Potassium Channels"
                ),
                "journal": "eNeuro",
                "volume": "6",
                "pages": "ENEURO.0181-19.2019",
                "doi": "10.1523/ENEURO.0181-19.2019",
                "source_role": "PRIMARY_PROTOCOL_SPECIFIC_COMPOSITE_TTM_LATENCY",
                "verification_scope": "OPEN_ARTICLE_METHODS_FIG1_TABLE1",
                "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6709211/",
                "limitations": [
                    (
                        "The TTMn-to-TTM interval combines motor-neuron-region "
                        "stimulation, axonal conduction, neuromuscular transmission, "
                        "and muscle-potential onset."
                    ),
                    "The recorded TTM response is not intracellular G1 physiology.",
                    (
                        "The paper reports rearing temperature; the cited latency "
                        "protocol does not establish electrophysiology test "
                        "temperature."
                    ),
                ],
            },
        ],
        "qualitative_context": [
            {
                "evidence_id": "koenig_ikeda_2005",
                "classification": "QUALITATIVE_PRIMARY_ABSTRACT_ONLY",
                "statement_scope": (
                    "The primary abstract reports faster TTM than DLM response "
                    "depression under repetitive stimulation and a reserve-"
                    "population contribution in the DLM comparison."
                ),
                "is_observation_record": False,
                "quantitative_depression_series_pinned": False,
            }
        ],
        "prior_source_attributions": [
            {
                "attribution": "Ikeda 1980",
                "reported_by_evidence_id": "koenig_ikeda_2007",
                "role": "PRIOR_SOURCE_FOR_EQUILIBRIUM_POTENTIAL_INPUT",
                "independently_reviewed_in_phase8s": False,
            }
        ],
    }


_PROTOCOL_KEYS = (
    "species",
    "developmental_age",
    "sex",
    "genotype",
    "temperature_c",
    "temperature_role",
    "preparation",
    "stimulation_site",
    "stimulation_pulse_ms",
    "stimulation_frequency_hz",
    "stimulus_count",
    "recycling_condition",
    "recording_site",
    "recording_method",
    "recording_fiber",
    "recording_mode",
    "bath_or_medium",
    "normalization",
    "correction_method",
    "stimulus_history",
)


def _protocol(
    values: dict[str, Any],
    *,
    source_not_verified: tuple[str, ...] = (),
    not_applicable: tuple[str, ...] = (),
) -> dict[str, Any]:
    protocol = {key: values.get(key) for key in _PROTOCOL_KEYS}
    status: dict[str, str] = {}
    reasons: dict[str, str] = {}
    for key, value in protocol.items():
        if value is not None:
            status[key] = "REPORTED"
            continue
        if key in not_applicable:
            status[key] = "NOT_APPLICABLE"
            reasons[key] = "This protocol dimension does not apply to this observation."
        elif key in source_not_verified:
            status[key] = "NOT_VERIFIED"
            reasons[key] = (
                "The 2005 primary full text was not verified for this contract."
            )
        else:
            status[key] = "NOT_REPORTED"
            reasons[key] = (
                "Not stated for this observation in the verified source scope."
            )
    return {
        "dimensions": protocol,
        "dimension_status": status,
        "unknown_reasons": reasons,
    }


def _common_g1_protocol(**overrides: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "species": "Drosophila melanogaster",
        "developmental_age": "4-day-old adult",
        "sex": "female",
        "genotype": None,
        "temperature_c": None,
        "temperature_role": None,
        "preparation": (
            "Fly fixed in Tackiwax; exposed TTM preparation for intracellular "
            "G1 recording."
        ),
        "stimulation_site": None,
        "stimulation_pulse_ms": None,
        "stimulation_frequency_hz": None,
        "stimulus_count": None,
        "recycling_condition": None,
        "recording_site": "G1 near its tergal attachment",
        "recording_method": "Intracellular glass-micropipette recording",
        "recording_fiber": "G1",
        "recording_mode": "intracellular",
        "bath_or_medium": None,
        "normalization": None,
        "correction_method": None,
        "stimulus_history": None,
    }
    values.update(overrides)
    return _protocol(values)


def _record(
    *,
    key: str,
    quantity_type: str,
    quantity: str,
    value: float | int | str,
    units: str | None,
    classification: str,
    applicability: str,
    scope_kind: str,
    protocol: dict[str, Any],
    evidence_refs: tuple[str, ...],
    source_locations: tuple[str, ...],
    limitations: tuple[str, ...],
    value_qualifier: str = "REPORTED_VALUE",
    uncertainty_value: float | None = None,
    uncertainty_kind: str = "NOT_REPORTED",
    sample_size: int | None = None,
    sample_size_unit: str | None = None,
    derivation_input_quantities: tuple[str, ...] = (),
    derivation: dict[str, Any] | None = None,
    source_lineage: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "quantity_type": quantity_type,
        "quantity": quantity,
        "value": value,
        "units": units,
        "value_qualifier": value_qualifier,
        "uncertainty_value": uncertainty_value,
        "uncertainty_kind": uncertainty_kind,
        "sample_size": sample_size,
        "sample_size_unit": sample_size_unit,
        "record_classification": classification,
        "applicability": applicability,
        "biological_scope": {
            "species": "Drosophila melanogaster",
            "structure": "TTM",
            "structure_scope": scope_kind,
            "recorded_fiber": "G1" if scope_kind == "SINGLE_G1_FIBER" else None,
            "whole_ttm_inference": False,
            "laterality": "NOT_RESOLVED_FOR_MALECNS_CROSSWALK",
            "malecns_body_id": None,
            "identity_mapping_scope": "CLASS_LEVEL_EVIDENCE_ONLY",
        },
        "protocol": protocol,
        "evidence_refs": list(evidence_refs),
        "source_locations": list(source_locations),
        "source_lineage": list(source_lineage),
        "derivation_input_quantities": list(derivation_input_quantities),
        "derivation": derivation,
        "latency_semantics": None,
        "model_comparability": {
            "status": MODEL_COMPARABILITY_STATUS,
            "current_neurofly_observable": None,
            "reason": (
                "Current NeuroFly motor/NMJ layers do not produce this measured "
                "quantity; a separately specified observation model is required."
            ),
        },
        "limitations": list(limitations),
        "_key": key,
    }


def _curated_observations() -> list[dict[str, Any]]:
    g1_base = _common_g1_protocol()
    resting_protocol = _common_g1_protocol(
        genotype=None,
        temperature_c=None,
        temperature_role=None,
        recording_site=(
            "G1 fiber; exact electrode position for this descriptive value "
            "not separately stated"
        ),
    )
    prior45_protocol = _protocol(
        {
            **{key: value for key, value in g1_base["dimensions"].items()},
            "developmental_age": None,
            "sex": None,
            "genotype": None,
            "temperature_c": None,
            "temperature_role": None,
            "preparation": None,
            "stimulation_site": None,
            "stimulation_pulse_ms": None,
            "stimulation_frequency_hz": None,
            "stimulus_count": None,
            "recycling_condition": None,
            "recording_site": None,
            "recording_method": None,
            "recording_mode": None,
            "bath_or_medium": (
                "4 mM Na-L-glutamate, reported to suppress the electrogenic response"
            ),
            "correction_method": None,
        },
        source_not_verified=(
            "developmental_age",
            "sex",
            "genotype",
            "temperature_c",
            "temperature_role",
            "preparation",
            "stimulation_site",
            "stimulation_pulse_ms",
            "stimulation_frequency_hz",
            "stimulus_count",
            "recycling_condition",
            "recording_site",
            "recording_method",
            "recording_mode",
            "correction_method",
            "normalization",
        ),
    )
    shi19_protocol = _common_g1_protocol(
        genotype="temperature-sensitive shibire^ts1 (shi)",
        temperature_c=19,
        temperature_role="electrophysiology test temperature",
        stimulation_site=None,
        stimulation_pulse_ms=None,
        stimulation_frequency_hz=None,
        stimulus_count=None,
        recycling_condition="recycling functions at 19 °C",
        bath_or_medium=None,
    )
    one_hz_protocol = _common_g1_protocol(
        genotype="temperature-sensitive shibire^ts1 (shi)",
        temperature_c=19,
        temperature_role="electrophysiology test temperature",
        stimulation_site="neck stimulating electrode",
        stimulation_pulse_ms=0.1,
        stimulation_frequency_hz=1,
        stimulus_count=1500,
        recycling_condition="permitted; shi recycling machinery functions at 19 °C",
        bath_or_medium=None,
        correction_method=None,
        stimulus_history="1500 repeated stimuli at 1 Hz",
    )
    latency_protocol = _protocol(
        {
            "species": "Drosophila melanogaster",
            "developmental_age": "24 hours post-eclosion",
            "sex": "both sexes",
            "genotype": "control condition in the Kadas et al. study",
            "temperature_c": None,
            "temperature_role": None,
            "preparation": (
                "Adult fly electrophysiology; reared at 24 °C. Test temperature "
                "for this latency is not specified in the cited protocol."
            ),
            "stimulation_site": (
                "Thoracic motor-neuron region; tungsten stimulation electrode"
            ),
            "stimulation_pulse_ms": None,
            "stimulation_frequency_hz": None,
            "stimulus_count": None,
            "recycling_condition": None,
            "recording_site": "TTM muscle; onset of the initial evoked potential phase",
            "recording_method": "Tungsten electrode muscle-potential recording",
            "recording_fiber": None,
            "recording_mode": "extracellular muscle-potential onset",
            "bath_or_medium": None,
            "normalization": None,
            "correction_method": None,
            "stimulus_history": None,
        }
    )

    observations = [
        _record(
            key="resting_potential",
            quantity_type="G1_RESTING_MEMBRANE_POTENTIAL",
            quantity="G1 resting membrane potential",
            value=-95,
            units="mV",
            value_qualifier="APPROXIMATE",
            classification="DESCRIPTIVE_MEASURED_VALUE",
            applicability="TTM_CLASS_CONTEXT",
            scope_kind="SINGLE_G1_FIBER",
            protocol=resting_protocol,
            evidence_refs=("koenig_ikeda_2007",),
            source_locations=(
                "Methods: Martin correction paragraph describing G1 membrane potential",
            ),
            limitations=(
                (
                    "Approximate descriptive value; no distribution, uncertainty, "
                    "or n is given with this statement."
                ),
                "Not a NeuroFly resting-potential parameter.",
                (
                    "The verified passage does not separately attach experiment-"
                    "level genotype or temperature to this value."
                ),
            ),
        ),
        _record(
            key="evoked_potential_prior",
            quantity_type="G1_EVOKED_JUNCTION_POTENTIAL",
            quantity=(
                "G1 evoked synaptic/junction potential at the reported "
                "threshold-level response"
            ),
            value=45,
            units="mV",
            classification="PRIOR_PRIMARY_RESULT_REUSED",
            applicability="G1_FIBER_VALIDATION_TARGET",
            scope_kind="SINGLE_G1_FIBER",
            protocol=prior45_protocol,
            evidence_refs=("koenig_ikeda_2007", "koenig_ikeda_2005"),
            source_locations=(
                "Koenig & Ikeda 2007 Methods: Martin correction paragraph",
                "Koenig & Ikeda 2007 Results: docked-vesicle/quantal-content analysis",
            ),
            source_lineage=(
                "45 mV value attributed by the 2007 paper to Koenig & Ikeda 2005",
            ),
            limitations=(
                (
                    "Prior primary result reused by the 2007 analysis, not a new "
                    "2007 measurement."
                ),
                (
                    "The verified 2005 source scope is abstract-only; exact 2005 "
                    "protocol details are not pinned."
                ),
                "Not whole-TTM voltage, muscle activation, or a NeuroFly gain.",
            ),
        ),
        _record(
            key="mejp_size",
            quantity_type="G1_MINIATURE_JUNCTION_POTENTIAL",
            quantity=(
                "G1 miniature excitatory junction-potential amplitude "
                "(MEJP peak estimate)"
            ),
            value=0.5,
            units="mV",
            value_qualifier="APPROXIMATE_HISTOGRAM_SUPPORTED",
            classification="DESCRIPTIVE_MEASURED_VALUE",
            applicability="G1_FIBER_VALIDATION_TARGET",
            scope_kind="SINGLE_G1_FIBER",
            protocol=shi19_protocol,
            evidence_refs=("koenig_ikeda_2007",),
            source_locations=("Results and Figure 6: G1 MEJP amplitude histogram",),
            limitations=(
                (
                    "Approximate histogram-supported G1 miniature-potential "
                    "estimate; no uncertainty or sample size is pinned."
                ),
                "Not an evoked response, event_gain, or force proxy.",
            ),
        ),
        _record(
            key="equilibrium_input",
            quantity_type="G1_EQUILIBRIUM_POTENTIAL_ANALYSIS_INPUT",
            quantity="Equilibrium potential V0 used by the Martin RC correction",
            value=-10,
            units="mV",
            classification="ANALYSIS_INPUT_FROM_PRIOR_SOURCE",
            applicability="ANALYSIS_CONTEXT_ONLY",
            scope_kind="ANALYSIS_INPUT",
            protocol=_protocol(
                {
                    "species": "Drosophila melanogaster (2007 analysis context)",
                    "developmental_age": None,
                    "sex": None,
                    "genotype": None,
                    "temperature_c": None,
                    "temperature_role": None,
                    "preparation": None,
                    "stimulation_site": None,
                    "stimulation_pulse_ms": None,
                    "stimulation_frequency_hz": None,
                    "stimulus_count": None,
                    "recycling_condition": None,
                    "recording_site": None,
                    "recording_method": None,
                    "recording_fiber": "G1 correction analysis",
                    "recording_mode": None,
                    "bath_or_medium": None,
                    "normalization": None,
                    "correction_method": "Martin RC nonlinear-summation correction",
                    "stimulus_history": None,
                }
            ),
            evidence_refs=("koenig_ikeda_2007",),
            source_locations=(
                (
                    "Methods: Martin correction paragraph; prior value attributed "
                    "to Ikeda 1980"
                ),
            ),
            source_lineage=("Ikeda 1980, as attributed by Koenig & Ikeda 2007",),
            limitations=(
                ("Prior-source analysis input, not measured in the 2007 preparation."),
                "Not automatically a NeuroFly reversal-potential parameter.",
            ),
        ),
        _record(
            key="quantal_content",
            quantity_type="G1_QUANTAL_CONTENT",
            quantity=(
                "Estimated quantal content for the reported single-stimulus G1 response"
            ),
            value=191,
            units="quanta",
            value_qualifier="APPROXIMATE_DERIVED_ESTIMATE",
            classification="DERIVED_QUANTITY",
            applicability="ANALYSIS_CONTEXT_ONLY",
            scope_kind="SINGLE_G1_FIBER",
            protocol=_common_g1_protocol(
                stimulation_site=(
                    "Neck stimulating electrode (paper's general arrangement)"
                ),
                stimulation_pulse_ms=0.1,
                stimulus_count=1,
                correction_method="Martin RC nonlinear-summation correction",
                stimulus_history="single stimulus; no prior activity",
            ),
            evidence_refs=("koenig_ikeda_2007", "koenig_ikeda_2005"),
            source_locations=(
                "Results: single-stimulus/docked-vesicle quantal-content estimate",
            ),
            derivation_input_quantities=(
                "G1_EVOKED_JUNCTION_POTENTIAL",
                "G1_MINIATURE_JUNCTION_POTENTIAL",
                "G1_EQUILIBRIUM_POTENTIAL_ANALYSIS_INPUT",
            ),
            derivation={
                "method": "Martin RC nonlinear-summation correction",
                "notation": {
                    "v": "recorded evoked synaptic potential",
                    "v1": "miniature/quantal potential",
                    "V0": "equilibrium-potential analysis input",
                    "m": "derived quantal content",
                },
                "interpretation": (
                    "The paper reports approximately 191 quanta after applying "
                    "the correction to the cited G1 inputs. This contract records "
                    "the derived result and does not recompute the physiology."
                ),
            },
            limitations=(
                (
                    "Derived corrected quantal content, not a raw voltage or "
                    "191 NeuroFly events."
                ),
                "No uncertainty is supplied for this approximate derived value.",
                "Correction assumptions are source-specific, not a NeuroFly model.",
            ),
        ),
        _record(
            key="spontaneous_rate",
            quantity_type="G1_SPONTANEOUS_MEJP_FREQUENCY",
            quantity="Spontaneous G1 miniature-event frequency",
            value=7,
            units="events_per_s",
            classification="SUMMARY_STATISTIC",
            applicability="G1_FIBER_VALIDATION_TARGET",
            scope_kind="SINGLE_G1_FIBER",
            protocol=_common_g1_protocol(
                genotype="wild-type Oregon-R",
                temperature_c=19,
                temperature_role="electrophysiology test temperature",
                stimulation_site=None,
                stimulation_pulse_ms=None,
                stimulation_frequency_hz=None,
                stimulus_count=None,
                recycling_condition=(
                    "Not pharmacologically blocked for this WT observation"
                ),
                stimulus_history="spontaneous recording; no evoked stimulus train",
            ),
            evidence_refs=("koenig_ikeda_2007",),
            source_locations=("Results: spontaneous MEJP frequency at 19 °C",),
            uncertainty_value=3,
            uncertainty_kind="UNKNOWN_NOT_ESTABLISHED",
            sample_size=5,
            sample_size_unit="flies",
            limitations=(
                (
                    "Reported as 7 ± 3 events/s for five wild-type flies. The "
                    "verified passage does not establish the uncertainty type."
                ),
                (
                    "Temperature-specific spontaneous miniature activity, not "
                    "evoked-response probability."
                ),
            ),
        ),
        _record(
            key="one_hz_no_depression",
            quantity_type="G1_DEPRESSION_PROTOCOL_OUTCOME",
            quantity="Observed depression outcome during the specified 1-Hz train",
            value="NO_OBSERVED_DEPRESSION_UNDER_THIS_PROTOCOL",
            units=None,
            value_qualifier="CATEGORICAL_PROTOCOL_OUTCOME",
            classification="CATEGORICAL_OBSERVATION",
            applicability="G1_FIBER_VALIDATION_TARGET",
            scope_kind="SINGLE_G1_FIBER",
            protocol=one_hz_protocol,
            evidence_refs=("koenig_ikeda_2007",),
            source_locations=(
                "Results: recycling-permitted 1-Hz train; Figure 5 protocol/results",
            ),
            uncertainty_kind="NOT_APPLICABLE",
            limitations=(
                (
                    "No depression was observed for this shi G1 protocol only: "
                    "19 °C, recycling permitted, 1 Hz, 1,500 stimuli."
                ),
                (
                    "This does not mean TTM never depresses at 1 Hz; blocked "
                    "recycling at 29 °C is distinct."
                ),
            ),
        ),
        _record(
            key="recycling_rate",
            quantity_type="G1_VESICLE_RECYCLING_RATE",
            quantity="Reported vesicle recycling rate per G1 active zone",
            value=0.24,
            units="vesicle_per_active_zone_per_s",
            value_qualifier="REPORTED_ROUNDED_DERIVED_VALUE",
            classification="DERIVED_QUANTITY",
            applicability="ANALYSIS_CONTEXT_ONLY",
            scope_kind="SINGLE_G1_FIBER",
            protocol=one_hz_protocol,
            evidence_refs=("koenig_ikeda_2007",),
            source_locations=(
                "Results: recycling-permitted versus recycling-blocked 1-Hz comparison",
            ),
            derivation={
                "method": (
                    "The paper derives the rate from recycling-permitted versus "
                    "blocked quanta, divided by the 1,500 s train and about "
                    "720 G1 active zones."
                ),
                "classification": "DERIVED_QUANTITY_REPORTED_BY_PRIMARY_SOURCE",
                "source_reported_value": 0.24,
                "comparison_inputs": {
                    "recycling_permitted_quanta": 286500,
                    "recycling_permitted_uncertainty": 9680,
                    "recycling_permitted_uncertainty_kind": "UNKNOWN_NOT_ESTABLISHED",
                    "recycling_permitted_sample_size": 5,
                    "recycling_blocked_quanta": 31800,
                    "train_duration_s": 1500,
                    "active_zone_denominator": 720,
                    "active_zone_denominator_qualifier": "APPROXIMATE",
                },
                "input_observations_in_contract": [],
                "note": (
                    "Comparison totals are source-level derivation inputs, not "
                    "separate records in this nine-observation set."
                ),
            },
            limitations=(
                (
                    "Source-derived rate tied to this 1-Hz recycling comparison "
                    "and active-zone denominator."
                ),
                (
                    "Not a NeuroFly recovery time constant, vesicle-state "
                    "coefficient, or generalized physiological rate."
                ),
            ),
        ),
        _record(
            key="ttmn_region_latency_24hpe",
            quantity_type="TTMN_REGION_STIM_TO_TTM_POTENTIAL_ONSET_LATENCY",
            quantity="TTMn-region stimulation to initial TTM potential onset latency",
            value=0.84,
            units="ms",
            uncertainty_value=0.02,
            uncertainty_kind="MEAN_SEM",
            sample_size=8,
            sample_size_unit="animals",
            classification="SUMMARY_STATISTIC",
            applicability="COMPOSITE_LATENCY_VALIDATION_TARGET",
            scope_kind="TTM_CLASS",
            protocol=latency_protocol,
            evidence_refs=("kadas_etal_2019",),
            source_locations=(
                (
                    "Methods; Figure 1 stimulation/recording schematic; Table 1, "
                    "24 h post-eclosion control"
                ),
            ),
            limitations=(
                (
                    "Composite motor-neuron-region stimulation-to-muscle-"
                    "potential-onset interval, not isolated NMJ delay."
                ),
                (
                    "Includes axonal conduction, neuromuscular transmission, and "
                    "muscle electrical-response onset."
                ),
                (
                    "Not an intracellular G1 measurement; the recorded fiber is "
                    "not identified as G1."
                ),
                (
                    "Test temperature is not reported in the latency protocol. "
                    "24 °C is rearing temperature, not a substitute test value."
                ),
            ),
        ),
    ]
    observations[-1]["latency_semantics"] = {
        "latency_kind": "DIRECT_MOTOR_NEURON_REGION_STIMULATION_TO_TTM_POTENTIAL_ONSET",
        "is_isolated_nmj_delay": False,
        "included_processes": [
            "motor-neuron axonal conduction",
            "neuromuscular transmission",
            "onset of the TTM muscle electrical potential",
        ],
    }

    # Protocol field statuses and omissions are explicit, even when a field is
    # inapplicable (for example, stimulation frequency during spontaneous activity).
    return observations


def _observation_id(record: dict[str, Any]) -> str:
    identity = {
        key: value
        for key, value in record.items()
        if key not in {"_key", "observation_id"}
    }
    digest = canonical_sha256(identity)
    return f"ttm-g1-obs-{digest[:20]}"


def build_observation_contract() -> dict[str, Any]:
    """Build the exact curated nine-record contract without external sources."""

    observations = _curated_observations()
    by_quantity = {row["quantity_type"]: row for row in observations}
    for row in observations:
        dependencies = [
            by_quantity[quantity] for quantity in row["derivation_input_quantities"]
        ]
        if any("observation_id" not in dependency for dependency in dependencies):
            raise TTMG1ObservationContractError(
                "derived records must follow their source records in canonical order"
            )
        row["derived_from_observation_ids"] = [
            dependency["observation_id"] for dependency in dependencies
        ]
        row["observation_id"] = _observation_id(row)
        row.pop("_key")

    # Canonical order is intentionally curated and pinned, rather than dependent
    # on dict/set order or a run-time query.
    config = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "evidence_manifest": _source_manifest(),
        "scientific_boundary": [
            "OBSERVATION_ONLY",
            "NO_MODEL_PARAMETERIZATION",
            "NO_EXACT_MALECNS_BODY_PHYSIOLOGY",
            "NO_WHOLE_TTM_INFERENCE_FROM_G1",
            "NO_MUSCLE_DYNAMICS",
            "NO_FIGURE_DIGITIZATION",
            "NO_CALIBRATION_OR_FITTING",
            "NO_FORCE_MECHANICS_OR_BEHAVIOR",
        ],
        "explicit_exclusions": [
            "QUANTITATIVE_KOENIG_IKEDA_2005_DEPRESSION_SERIES",
            "FIGURE_DIGITIZED_OR_OCR_DERIVED_VALUES",
            "EXACT_MALECNS_BODY_PHYSIOLOGY",
            "SIDE_RESOLVED_G1_PHYSIOLOGY",
            "WHOLE_TTM_INTERPRETATION_OF_G1_VALUES",
            "MODEL_CALIBRATION_OR_FITTING",
            "MODEL_PARAMETER_EXPORT",
            "MUSCLE_ACTIVATION_OR_ELECTRICAL_DYNAMICS",
            "FORCE_CONTRACTION_MECHANICS_OR_BEHAVIOR",
        ],
        "record_classifications": sorted(RECORD_CLASSIFICATIONS),
        "applicability_vocabulary": sorted(APPLICABILITY_VALUES),
        "uncertainty_vocabulary": sorted(UNCERTAINTY_KINDS),
        "model_comparability_default": MODEL_COMPARABILITY_STATUS,
        "record_count": 9,
        "ordering": "CURATED_PHASE8R_ORDER",
    }
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "observation_count": len(observations),
        "observations": observations,
    }
    validate_observation_payload(config, result)
    config_sha256 = canonical_sha256(config)
    result_sha256 = canonical_sha256(result)
    contract_id = canonical_sha256(
        {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "config_sha256": config_sha256,
            "result_sha256": result_sha256,
        }
    )
    return {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "contract_id": contract_id,
        "config_sha256": config_sha256,
        "result_sha256": result_sha256,
        "config": config,
        "result": result,
    }


def validate_observation_payload(
    config: dict[str, Any], result: dict[str, Any]
) -> None:
    """Fail closed on scope, provenance, protocol, or classification drift."""

    if config.get("schema_version") != CONFIG_SCHEMA_VERSION:
        raise TTMG1ObservationContractError("unsupported observation config schema")
    if result.get("schema_version") != RESULT_SCHEMA_VERSION:
        raise TTMG1ObservationContractError("unsupported observation result schema")
    rows = result.get("observations")
    if (
        not isinstance(rows, list)
        or len(rows) != 9
        or result.get("observation_count") != 9
    ):
        raise TTMG1ObservationContractError(
            "canonical contract must contain nine observations"
        )
    sources = config.get("evidence_manifest", {}).get("sources", [])
    source_ids = {row.get("evidence_id") for row in sources if isinstance(row, dict)}
    ids: set[str] = set()
    quantities: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise TTMG1ObservationContractError("observation record must be an object")
        record_id = row.get("observation_id")
        if not isinstance(record_id, str) or record_id in ids:
            raise TTMG1ObservationContractError("missing or duplicate observation ID")
        ids.add(record_id)
        quantity = row.get("quantity_type")
        if not isinstance(quantity, str) or quantity in quantities:
            raise TTMG1ObservationContractError("missing or duplicate quantity type")
        quantities.add(quantity)
        if row.get("record_classification") not in RECORD_CLASSIFICATIONS:
            raise TTMG1ObservationContractError("unknown observation classification")
        if row.get("applicability") not in APPLICABILITY_VALUES:
            raise TTMG1ObservationContractError("unknown observation applicability")
        if (
            row.get("model_comparability", {}).get("status")
            != MODEL_COMPARABILITY_STATUS
        ):
            raise TTMG1ObservationContractError("unsupported model-comparability claim")
        if (
            row.get("model_comparability", {}).get("current_neurofly_observable")
            is not None
        ):
            raise TTMG1ObservationContractError(
                "current model observable was fabricated"
            )
        if row.get("uncertainty_kind") not in UNCERTAINTY_KINDS:
            raise TTMG1ObservationContractError("unknown uncertainty kind")
        value = row.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise TTMG1ObservationContractError("observation value has invalid type")
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            raise TTMG1ObservationContractError("numeric observation must be finite")
        if row.get("units") not in {
            None,
            "mV",
            "ms",
            "events_per_s",
            "vesicle_per_active_zone_per_s",
            "quanta",
        }:
            raise TTMG1ObservationContractError("unsupported observation unit")
        if (
            row.get("record_classification") == "CATEGORICAL_OBSERVATION"
            and row.get("units") is not None
        ):
            raise TTMG1ObservationContractError(
                "categorical observations cannot carry numeric units"
            )
        uncertainty = row.get("uncertainty_value")
        if uncertainty is not None and (
            isinstance(uncertainty, bool)
            or not isinstance(uncertainty, (int, float))
            or not math.isfinite(float(uncertainty))
            or uncertainty < 0
        ):
            raise TTMG1ObservationContractError("invalid observation uncertainty")
        sample_size = row.get("sample_size")
        if sample_size is not None and (
            isinstance(sample_size, bool)
            or not isinstance(sample_size, int)
            or sample_size < 0
        ):
            raise TTMG1ObservationContractError("invalid observation sample size")
        if row.get("uncertainty_kind") in {"MEAN_SEM", "SD"} and uncertainty is None:
            raise TTMG1ObservationContractError(
                "reported uncertainty kind requires a value"
            )
        if (
            row.get("uncertainty_kind") == "UNKNOWN_NOT_ESTABLISHED"
            and uncertainty is None
        ):
            raise TTMG1ObservationContractError(
                "unknown uncertainty must retain its reported magnitude"
            )
        if row.get("record_classification") == "DERIVED_QUANTITY" and not isinstance(
            row.get("derivation"), dict
        ):
            raise TTMG1ObservationContractError(
                "derived observation requires derivation metadata"
            )
        refs = row.get("evidence_refs")
        if (
            not isinstance(refs, list)
            or not refs
            or any(ref not in source_ids for ref in refs)
        ):
            raise TTMG1ObservationContractError(
                "observation evidence reference is missing"
            )
        if (
            not isinstance(row.get("source_locations"), list)
            or not row["source_locations"]
        ):
            raise TTMG1ObservationContractError(
                "observation source location is required"
            )
        scope = row.get("biological_scope")
        if (
            not isinstance(scope, dict)
            or scope.get("whole_ttm_inference") is not False
            or scope.get("malecns_body_id") is not None
            or scope.get("identity_mapping_scope") != "CLASS_LEVEL_EVIDENCE_ONLY"
        ):
            raise TTMG1ObservationContractError(
                "unsupported whole-TTM or exact-body scope"
            )
        if (
            scope.get("structure_scope") == "SINGLE_G1_FIBER"
            and scope.get("recorded_fiber") != "G1"
        ):
            raise TTMG1ObservationContractError("G1 scope and recorded fiber disagree")
        protocol = row.get("protocol")
        if not isinstance(protocol, dict):
            raise TTMG1ObservationContractError("protocol metadata is required")
        dimensions = protocol.get("dimensions")
        statuses = protocol.get("dimension_status")
        reasons = protocol.get("unknown_reasons")
        if (
            not isinstance(dimensions, dict)
            or set(dimensions) != set(_PROTOCOL_KEYS)
            or not isinstance(statuses, dict)
            or set(statuses) != set(_PROTOCOL_KEYS)
            or not isinstance(reasons, dict)
        ):
            raise TTMG1ObservationContractError(
                "protocol dimensions/statuses are incomplete"
            )
        for key, protocol_value in dimensions.items():
            status = statuses[key]
            if protocol_value is None:
                if status not in {"NOT_REPORTED", "NOT_VERIFIED", "NOT_APPLICABLE"}:
                    raise TTMG1ObservationContractError(
                        "unknown protocol value lacks explicit status"
                    )
                if not isinstance(reasons.get(key), str) or not reasons[key]:
                    raise TTMG1ObservationContractError(
                        "unknown protocol value lacks reason"
                    )
            elif status != "REPORTED":
                raise TTMG1ObservationContractError(
                    "reported protocol value has unknown status"
                )
            if (
                key
                in {"temperature_c", "stimulation_frequency_hz", "stimulation_pulse_ms"}
                and protocol_value is not None
            ):
                if (
                    isinstance(protocol_value, bool)
                    or not isinstance(protocol_value, (int, float))
                    or not math.isfinite(float(protocol_value))
                ):
                    raise TTMG1ObservationContractError(
                        f"invalid protocol number: {key}"
                    )
                if key != "temperature_c" and protocol_value < 0:
                    raise TTMG1ObservationContractError(
                        f"negative protocol number: {key}"
                    )
        if dimensions.get("stimulus_count") is not None and (
            isinstance(dimensions["stimulus_count"], bool)
            or not isinstance(dimensions["stimulus_count"], int)
            or dimensions["stimulus_count"] < 0
        ):
            raise TTMG1ObservationContractError("invalid protocol stimulus count")
    if len({row.get("observation_id") for row in rows}) != len(rows):
        raise TTMG1ObservationContractError("duplicate observation IDs")


def validate_contract_against_curated(contract: dict[str, Any]) -> dict[str, Any]:
    """Validate hashes, semantic identities, and exact offline curated replay."""

    expected = build_observation_contract()
    if contract != expected:
        raise TTMG1ObservationContractError(
            "observation contract differs from the pinned curated definition"
        )
    return expected


__all__ = [
    "APPLICABILITY_VALUES",
    "ARTIFACT_SCHEMA_VERSION",
    "CONFIG_SCHEMA_VERSION",
    "CONTRACT_SCHEMA_VERSION",
    "MODEL_COMPARABILITY_STATUS",
    "RECORD_CLASSIFICATIONS",
    "RESULT_SCHEMA_VERSION",
    "TTMG1ObservationContractError",
    "build_observation_contract",
    "canonical_json_bytes",
    "canonical_sha256",
    "validate_contract_against_curated",
    "validate_observation_payload",
]
