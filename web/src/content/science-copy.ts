/**
 * Disclosure copy for the whole site, in one file so scientific review is one read.
 * Rules (redesign brief section 7, Phase 0 decisions):
 *  - The model is the subject: "the model's DNp01 state rises", never "the fly's neuron fires".
 *  - Model output carries "mV_eq" (model-equivalent, not measured), never a bare "mV".
 *  - "Dimensionless" is used only for values that really have no unit.
 *  - No green ticks, scores or "accuracy" near a result.
 *  - "Circuit check" instead of "Validation"; "Integrity-checked" instead of "verified".
 * Anything not supported by the repository is marked NEEDS OWNER INPUT instead of invented.
 */

export const MALECNS_RELEASE = "MaleCNS v1.0";

export const DATA_KINDS = [
  "structural",
  "model-assumption",
  "model-state",
  "not-evaluated",
  "unavailable",
] as const;
export type DataKind = (typeof DATA_KINDS)[number];

export interface KindCopy {
  /** Human label shown next to the glyph. */
  readonly label: string;
  /** Shape of the glyph, so the kind never depends on colour. */
  readonly glyph: "solid square" | "hollow diamond" | "half-filled circle" | "dashed circle" | "circle with slash";
  readonly tooltip: string;
}

export const KIND_COPY: Readonly<Record<DataKind, KindCopy>> = {
  structural: {
    label: "Structural",
    glyph: "solid square",
    tooltip: `From the ${MALECNS_RELEASE} connectome. Describes physical wiring, not signal strength.`,
  },
  "model-assumption": {
    label: "Model assumption",
    glyph: "hollow diamond",
    tooltip: "Chosen for the model; not validated here.",
  },
  "model-state": {
    label: "Model state",
    glyph: "half-filled circle",
    tooltip: "Simulation output in model units. Not a biological measurement.",
  },
  "not-evaluated": {
    label: "Not evaluated",
    glyph: "dashed circle",
    tooltip: "No comparison with real fly data has been made for this result. This is not a failure.",
  },
  unavailable: {
    label: "Not available yet",
    glyph: "circle with slash",
    tooltip: "Deliberately off or not built yet. The reason is on the Status and limits page.",
  },
};

/** Machine status codes from the API, shown by name outside the Raw layer. */
export const STATUS_COPY: Readonly<Record<string, string>> = {
  NOT_EVALUATED: "Not evaluated",
};
export function statusLabel(code: string): string {
  return STATUS_COPY[code] ?? code.replaceAll("_", " ").toLowerCase().replace(/^./, (c) => c.toUpperCase());
}

export const UNIT_COPY = {
  dimensionless: "dimensionless",
  /** Shown beside every unit ending in _eq. */
  modelEquivalentNote: "model-equivalent, not measured",
  modelEquivalentExplanation:
    "A model-equivalent unit. The simulation produces this number; it was not measured in a fly.",
} as const;

export const READOUT_COPY = {
  notRecorded: "Not recorded",
  loading: "Loading",
  notAvailable: "Not available yet",
} as const;

export const PROVENANCE_COPY = {
  details: "Details",
  detailsLabel: (what: string) => `Provenance details for ${what}`,
  copy: "Copy",
  copied: "Copied",
  copyFailed: "Could not copy. Select the text instead.",
  openJson: "Open JSON",
  fields: {
    kind: "Kind",
    source: "Source",
    modelVersion: "Model version",
    status: "Status",
    artifactId: "Artifact ID",
    api: "API link",
  },
} as const;

export const STATE_COPY = {
  loading3d: (what: string) => `Loading ${what}`,
  empty: { action: "Clear filters" },
  apiDown: {
    title: "The data service isn't responding.",
    body: "Nothing on this page has been lost.",
    retry: "Retry",
  },
  routeError: {
    title: "This page couldn't load.",
    retry: "Try again",
    home: "Go home",
    reference: "Reference",
  },
  integrityFailure: {
    title: "The stored results failed their integrity check.",
    body: "No results are shown, and none are substituted. Nothing on this page has been lost.",
  },
  notFound: { title: "We couldn't find that page.", body: "Try one of these sections." },
  /** The ID is rendered as code between the two parts. */
  unknownId: { before: (noun: string) => `There is no ${noun} with the ID`, after: "." },
  webglOff: {
    title: "3D isn't available on this device.",
    withData: "The data below is the same.",
  },
  contextLost: {
    title: "The 3D view stopped.",
    body: "The browser released the graphics context. Nothing on this page has been lost.",
    action: "Restart 3D view",
  },
  /** The API answered, and it says this deployment has no neuron shape data installed. */
  notOnDeployment: {
    title: "Neuron shape data is not available on this deployment.",
    body: "The rest of the site is not affected: scenarios, experiments, the Lab and the science pages work without it.",
  },
  lowPower: {
    title: "Showing simplified shapes for smoother playback.",
    action: "Use full detail",
  },
  missing: (what: string) => `${what} not included in this artifact.`,
} as const;

/**
 * Home page copy. The headline, statement and the four status facts are the owner's wording
 * (Phase 0 decision 5). Counts are not added together.
 */
export const HOME_COPY = {
  eyebrow: "Research project",
  headline: "Selected fruit fly circuits, modelled from the connectome.",
  statement:
    "NeuroFly is a research model of selected fruit fly neural circuits, built from the MaleCNS connectome and connected to a simplified simulated body.",
  primaryAction: "Watch the looming scenario",
  secondaryAction: "How much of this is real?",
  posterCaption: "The visible specimen is an artistic 3D asset, not anatomy reconstructed from MaleCNS.",
  strip: [
    { kind: "structural", text: "Two selected circuits: looming (313 bodies) and HS → DNp15 (8 bodies). Not a whole brain." },
    { kind: "structural", text: `Wiring from ${MALECNS_RELEASE}` },
    { kind: "model-assumption", text: "Kinematic body, no muscle or wing physics" },
    { kind: "not-evaluated", text: "Not yet evaluated against real flies" },
  ],
  layers: [
    { kind: "structural", title: "The connectome", text: `Which identified neurons connect, taken from the ${MALECNS_RELEASE} connectome. It describes wiring, not signal strength.` },
    { kind: "model-assumption", title: "The neuron model", text: "Explicit rules for how each neuron's state changes over time. They are chosen for the model, and some follow published models. They are not validated here." },
    { kind: "model-state", title: "The output", text: "What the simulation produces, in model units such as mV_eq. It is a model result, not a measurement from a fly." },
  ],
  lab: {
    title: "Explore the Lab",
    text: "Walking and flight modes in a 3D enclosure. Movement follows engineering rules with a neural steering influence, and there is no muscle or wing physics.",
    note: "Runs in your browser",
  },
} as const satisfies {
  eyebrow: string; headline: string; statement: string; primaryAction: string; secondaryAction: string; posterCaption: string;
  strip: readonly { kind: DataKind; text: string }[];
  layers: readonly { kind: DataKind; title: string; text: string }[];
  lab: { title: string; text: string; note: string };
};

/** Repository root, for evidence links. Every capability and glossary source must exist there. */
export const REPOSITORY_BLOB = "https://github.com/a104174/NeuroFly/blob/main/";

export type CapabilityGroup = "available" | "model-only" | "not-available";
export interface Capability {
  readonly id: string;
  readonly group: CapabilityGroup;
  /** What kind of thing this row is, shown with the kind glyph. */
  readonly kind: DataKind;
  readonly name: string;
  /** What it is, or why it is off. Taken from the cited report, not invented. */
  readonly reason: string;
  /** Path in the repository that supports the reason (a test checks that it exists). */
  readonly source: { readonly path: string; readonly label: string };
}

export const CAPABILITY_GROUPS: Readonly<Record<CapabilityGroup, { title: string; intro: string }>> = {
  available: {
    title: "Available",
    intro: "These work today. They show connectome structure and stored model results.",
  },
  "model-only": {
    title: "Model only",
    intro: "These run, but they are models. Their output is model state, not a biological measurement.",
  },
  "not-available": {
    title: "Not available yet",
    intro: "Deliberately off or not built yet. Each reason comes from the project's own reports.",
  },
};

export const CAPABILITIES: readonly Capability[] = [
  {
    id: "connectivity", group: "available", kind: "structural", name: "Selected MaleCNS connectivity",
    reason: `Identified neurons, their sides and the directed routes between them for the selected circuits, pinned to male-cns:v1.0. Contact counts are routing metadata, not signal strength.`,
    source: { path: "docs/science/neurofly_v1_scientific_status.json", label: "v1 scientific status" },
  },
  {
    id: "morphology", group: "available", kind: "structural", name: "Neuron shape samples",
    reason: "Raw skeletons for two DNp01 bodies and a fixed six-body sample, taken from the official MaleCNS release. They are shown as stored, not simulated.",
    source: { path: "docs/architecture/malecns_morphology_inspector.md", label: "Morphology inspector" },
  },
  {
    id: "replays", group: "available", kind: "model-state", name: "Canonical scenario replays",
    reason: "Five preset scenarios, recorded in advance and reconstructed offline with hash checks. The browser plays them back from stored data; it does not run them again.",
    source: { path: "docs/science/experiment_artifact_contract.md", label: "Experiment artifact contract" },
  },
  {
    id: "looming", group: "model-only", kind: "model-state", name: "Looming circuit (LC4 and LPLC2 to DNp01)",
    reason: "Runs deterministically. In the canonical presets the DNp01 model stays below its spike threshold and the body does not move. Zero model output is not evidence of a biological failure to respond.",
    source: { path: "docs/science/neurofly_v1_scientific_status.json", label: "v1 scientific status" },
  },
  {
    id: "steering", group: "model-only", kind: "model-state", name: "HS to DNp15 steering readout",
    reason: "Continuous, dimensionless proxy states from six HS sources to two DNp15 targets. They are not measured membrane voltages, and no spike or event model is defined.",
    source: { path: "docs/science/hs_dnp15_neural_validation.md", label: "HS to DNp15 model report" },
  },
  {
    id: "lab", group: "model-only", kind: "model-assumption", name: "Movement in the Lab",
    reason: "Runs in your browser. The walking neural update is a reimplementation of the pinned Python model; it agrees with the recorded Python run to within 1e-8 in each model-space quantity over eight seconds. Forward propulsion, boundary response and flight are engineering rules, not biology.",
    source: { path: "docs/science/interactive_neural_locomotion_v2.md", label: "Interactive neural locomotion report" },
  },
  {
    id: "level-c", group: "not-available", kind: "unavailable", name: "Level C visual-angle mapping",
    reason: "The column-space structure is kept but switched off. No validated mapping from a world object to MaleCNS columns exists, so it is not presented as calibrated vision.",
    source: { path: "docs/science/sensory_consumption_boundary.md", label: "Sensory consumption boundary" },
  },
  {
    id: "empirical", group: "not-available", kind: "not-evaluated", name: "Comparison with real fly data",
    reason: "Not done. A direct comparison with published calcium responses was refused because the published stimulus and observable are incompatible with what the model supports. No agreement or disagreement is claimed.",
    source: { path: "docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md", label: "Empirical benchmark v9.2" },
  },
  {
    id: "calibration", group: "not-available", kind: "unavailable", name: "Calibrated DNp01 voltage and transfer gain",
    reason: "The transfer magnitude cannot be identified numerically from current evidence, and calibration readiness is recorded as needing additional assay mapping.",
    source: { path: "docs/science/neurofly_v1_scientific_status.json", label: "v1 scientific status" },
  },
  {
    id: "biomechanics", group: "not-available", kind: "unavailable", name: "Muscle and wing physics",
    reason: "Not modelled. Body motion and leg animation are engineering rules. They do not establish biological muscle control or physiological flight, and validated biomechanics is listed as an open question.",
    source: { path: "docs/science/neurofly_v1_scientific_status.json", label: "v1 scientific status" },
  },
  {
    id: "dng100", group: "not-available", kind: "unavailable", name: "DNg100 and T1 as the movement controller",
    reason: "Kept as a shadow pathway. It is not the controller that drives movement in the Lab.",
    source: { path: "docs/science/dng100_t1_motor_response_shadow.md", label: "DNg100 and T1 shadow report" },
  },
  {
    id: "whole-brain", group: "not-available", kind: "unavailable", name: "Whole-brain simulation",
    reason: "Not attempted. Only the selected circuits run; the rest of the MaleCNS nervous system does not.",
    source: { path: "docs/science/neurofly_v1_scientific_status.json", label: "v1 scientific status" },
  },
];

/** Questions the project's own v1 status lists as unresolved. */
export const OPEN_QUESTIONS: readonly string[] = [
  "How a sensory state should be observed (the observation transform)",
  "The physiological size of the sensory-to-DNp01 transfer",
  "The relative per-body efficacy of LC4 and LPLC2",
  "Calibrated DNp01 electrophysiology",
  "Absolute retinal registration",
  "Physical world scale",
  "Validated biomechanics",
  "Broader behavioural circuits",
];

export type GlossaryGroup = "objects" | "kinds" | "science";
export interface GlossaryEntry {
  readonly id: string;
  readonly term: string;
  readonly group: GlossaryGroup;
  readonly meaning: string;
}
export const GLOSSARY_GROUPS: Readonly<Record<GlossaryGroup, { title: string; intro: string }>> = {
  objects: { title: "Core objects", intro: "One word for each thing, used everywhere on the site." },
  kinds: { title: "Kinds of data", intro: "Every number on the site says which of these it is." },
  science: { title: "Science terms", intro: "The words you need to read the model pages." },
};
export const GLOSSARY: readonly GlossaryEntry[] = [
  { id: "scenario", term: "Scenario", group: "objects", meaning: "A defined situation: which stimulus, which circuit, which settings. Like a recipe. NeuroFly offers five canonical scenarios, recorded in advance." },
  { id: "run", term: "Run", group: "objects", meaning: "One execution of the model. The model is deterministic, so the same inputs give the same run. A run is a model run, not a trial with a real fly." },
  { id: "experiment", term: "Experiment", group: "objects", meaning: "A completed run published here with its status and provenance. Publishing does not mean evaluated: today's recorded run is an engineering test, not a scientific experiment." },
  { id: "artifact", term: "Artifact", group: "objects", meaning: "The stored data package behind an experiment or a neuron. It appears only as an identifier and a link." },
  { id: "cockpit", term: "Cockpit", group: "objects", meaning: "The synchronised view of the world, the connectome and the telemetry for one experiment. It plays back a completed run; it does not control a live simulation." },
  { id: "structural", term: KIND_COPY.structural.label, group: "kinds", meaning: `Taken from the ${MALECNS_RELEASE} connectome, which maps the physical wiring. Examples: neuron shape, which neurons connect.` },
  { id: "contact-count", term: "Contact count", group: "kinds", meaning: "How many synaptic contacts were mapped between two neurons. It does not measure signal strength." },
  { id: "model-assumption", term: KIND_COPY["model-assumption"].label, group: "kinds", meaning: "A value or rule chosen for the model; not validated here. Some are starting values taken from published models and general fruit fly electrophysiology. Examples: the gain settings G_LC4 and G_LPLC2, and neuron-model parameters such as resting potential and threshold." },
  { id: "model-state", term: KIND_COPY["model-state"].label, group: "kinds", meaning: "A number the simulation produces, in model units such as mV_eq. It is not a biological measurement." },
  { id: "not-evaluated", term: KIND_COPY["not-evaluated"].label, group: "kinds", meaning: "No comparison with real fly data has been made for this result. It is not a failure. All current experiments have this status." },
  { id: "unavailable", term: KIND_COPY.unavailable.label, group: "kinds", meaning: "A capability that is deliberately off or not built yet. The Status and limits page gives the reason for each." },
  { id: "connectome", term: "Connectome", group: "science", meaning: "A map of a nervous system's neurons and their connections." },
  { id: "body", term: "Body", group: "science", meaning: "One reconstructed neuron in the connectome. The looming circuit has 313 bodies: 126 LC4, 185 LPLC2 and 2 DNp01." },
  { id: "morphology", term: "Morphology", group: "science", meaning: "The 3D shape of a neuron." },
  { id: "lc4-lplc2", term: "LC4 and LPLC2", group: "science", meaning: "Visual projection neurons. In the looming circuit there are 126 LC4 and 185 LPLC2." },
  { id: "dnp01", term: "DNp01", group: "science", meaning: "A descending neuron, which carries signals from the brain towards the body. The looming circuit has two, one on each side." },
  { id: "hs-dnp15", term: "HS and DNp15", group: "science", meaning: "The neurons selected for the horizontal-motion circuit: three HS neurons on each side feed the DNp15 neuron on that side, six HS and two DNp15 in all." },
  { id: "looming", term: "Looming", group: "science", meaning: "A visual stimulus in which an object appears to approach." },
  { id: "lif", term: "Leaky integrate-and-fire", group: "science", meaning: "A simple neuron model: input accumulates, leaks away over time, and triggers a spike at a threshold. NeuroFly uses it for the looming circuit. The HS to DNp15 path uses continuous proxy states and defines no spikes." },
  { id: "kinematic", term: "Kinematic", group: "science", meaning: "Movement is computed from rules, without simulating muscles or wing physics." },
  { id: "deterministic", term: "Deterministic", group: "science", meaning: "The same inputs always give the same output. NeuroFly's current runs use no random drive." },
];

/**
 * Words the interface retires (brief section 3 and Phase 0 decisions). A test scans the
 * UI components and this folder for them. Replacements are guidance for authors.
 */
export const RETIRED_TERMS: ReadonlyArray<{ readonly term: RegExp; readonly use: string }> = [
  { term: /\bverified\b/i, use: "Integrity-checked (data) or Reproducible (runs)" },
  // The one allowed use is the explanation itself: "not biological validation".
  { term: /(?<!not biological )\bvalidation\b/i, use: "Circuit check, with the note that it is not biological validation" },
  { term: /\bbio-?accurate\b|\brealistic\b|\blifelike\b/i, use: "remove" },
  { term: /\bdigital (organism|fly)\b/i, use: "selected circuit, model" },
  { term: /\bsimulated brain\b/i, use: "selected circuit, model" },
  { term: /\bfiring rate\b/i, use: "model activity, model spikes" },
];

/** Units that would present model output as a biological measurement. */
const BIOLOGICAL_SYMBOL = /^[mµunpk]?(V|A|S|Hz|F|Ω)$/; // case-sensitive: "ms" is time, "mS" is conductance
const BIOLOGICAL_WORDS = /spikes?\s*\/\s*s|firing rate/i;
export function isBiologicalUnit(unit: string): boolean {
  const trimmed = unit.trim();
  return BIOLOGICAL_SYMBOL.test(trimmed) || BIOLOGICAL_WORDS.test(trimmed);
}
