"""Literature-grounded, model-neutral looming benchmark definitions."""

from dataclasses import dataclass

from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET


@dataclass(frozen=True)
class BenchmarkCondition:
    identifier: str
    description: str
    role: str


@dataclass(frozen=True)
class LoomingBenchmark:
    identifier: str
    target: str
    phenomenon: str
    conditions: tuple[BenchmarkCondition, ...]
    quantitative_requirement: str
    evidence_reference: str


@dataclass(frozen=True)
class FeatureAssociation:
    """Published population evidence, explicitly not a per-body mapping."""

    source_feature: str
    target_population: str
    classification: str
    provenance: str


@dataclass(frozen=True)
class SensoryBoundarySpecification:
    """The model-neutral variables available before a future encoder exists."""

    candidate_identifier: str
    dataset: str
    stimulus_fields: tuple[str, ...]
    feature_associations: tuple[FeatureAssociation, ...]
    mapping_status: str


SENSORY_BOUNDARY = SensoryBoundarySpecification(
    candidate_identifier=CANDIDATE.identifier,
    dataset=MALECNS_DATASET,
    stimulus_fields=(
        "center.azimuth_rad",
        "center.elevation_rad",
        "angular_size_rad",
        "angular_expansion_velocity_rad_s",
    ),
    feature_associations=(
        FeatureAssociation(
            source_feature="angular_expansion_velocity_rad",
            target_population="LC4",
            classification=(
                "published population association; not a MaleCNS per-body map"
            ),
            provenance="Ache et al. 2019, doi:10.1016/j.cub.2019.01.079",
        ),
        FeatureAssociation(
            source_feature="angular_size_rad",
            target_population="LPLC2",
            classification=(
                "published population association; not a MaleCNS per-body map"
            ),
            provenance="Ache et al. 2019, doi:10.1016/j.cub.2019.01.079",
        ),
    ),
    mapping_status="MaleCNS per-neuron visual mapping not established",
)


BENCHMARKS = (
    LoomingBenchmark(
        identifier="lplc2_localized_outward_selectivity",
        target="LPLC2",
        phenomenon=(
            "localized receptive fields with preference for focal outward/radial motion"
        ),
        conditions=(
            BenchmarkCondition(
                "dark_loom", "dark disk expands from a focal center", "looming"
            ),
            BenchmarkCondition(
                "dark_recede", "dark disk recedes from the observer", "control"
            ),
            BenchmarkCondition(
                "motion_free_darkening",
                "luminance changes without edge motion",
                "control",
            ),
            BenchmarkCondition(
                "wide_field_translation",
                "wide-field motion without focal expansion",
                "control",
            ),
            BenchmarkCondition(
                "contraction", "motion directed toward a focal center", "control"
            ),
        ),
        quantitative_requirement=(
            "Compare selectivity qualitatively; do not invent a response amplitude "
            "or threshold."
        ),
        evidence_reference="Klapoetke et al. 2017, doi:10.1038/nature24626",
    ),
    LoomingBenchmark(
        identifier="lc4_lplc2_feature_separation",
        target="LC4 + LPLC2 -> DNp01/GF",
        phenomenon=(
            "distinct looming feature contributions: angular velocity associated "
            "with LC4 and angular size associated with LPLC2"
        ),
        conditions=(
            BenchmarkCondition(
                "vary_angular_velocity",
                "hold geometry comparable while varying expansion speed",
                "feature comparison",
            ),
            BenchmarkCondition(
                "vary_angular_size",
                "vary retinal/angular coverage across looming trajectories",
                "feature comparison",
            ),
            BenchmarkCondition(
                "pathway_silencing_controls",
                "compare pathway-isolated and combined conditions",
                "control",
            ),
        ),
        quantitative_requirement=(
            "Evaluate feature separation and timing against the paper's observations; "
            "do not convert them into per-cell input amplitudes."
        ),
        evidence_reference="Ache et al. 2019, doi:10.1016/j.cub.2019.01.079",
    ),
    LoomingBenchmark(
        identifier="dnp01_combined_integration",
        target="DNp01/Giant Fiber",
        phenomenon=(
            "combined LC4 and LPLC2 drive should be evaluated as a joint GF response, "
            "including the reported supralinear integration target"
        ),
        conditions=(
            BenchmarkCondition(
                "lc4_only",
                "LC4-associated feature pathway condition",
                "ablation comparison",
            ),
            BenchmarkCondition(
                "lplc2_only",
                "LPLC2-associated feature pathway condition",
                "ablation comparison",
            ),
            BenchmarkCondition(
                "combined",
                "both feature pathways presented together",
                "integration target",
            ),
        ),
        quantitative_requirement=(
            "Compare the combined response with isolated responses; do not implement "
            "supralinearity or a DNp01 activation rule in Phase 1C."
        ),
        evidence_reference="Ache et al. 2019, doi:10.1016/j.cub.2019.01.079",
    ),
)
