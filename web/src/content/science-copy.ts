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
    tooltip: "Chosen for the model, not measured from the fly.",
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
  notFound: { title: "We couldn't find that page.", body: "Try one of these sections." },
  /** The ID is rendered as code between the two parts. */
  unknownId: { before: (noun: string) => `There is no ${noun} with the ID`, after: "." },
  webglOff: {
    title: "3D isn't available on this device.",
    withData: "The data below is the same.",
  },
  lowPower: {
    title: "Showing simplified shapes for smoother playback.",
    action: "Use full detail",
  },
  missing: (what: string) => `${what} not included in this artifact.`,
} as const;

/**
 * Words the interface retires (brief section 3 and Phase 0 decisions). A test scans the
 * UI components and this folder for them. Replacements are guidance for authors.
 */
export const RETIRED_TERMS: ReadonlyArray<{ readonly term: RegExp; readonly use: string }> = [
  { term: /\bverified\b/i, use: "Integrity-checked (data) or Reproducible (runs)" },
  { term: /\bvalidation\b/i, use: "Circuit check, with the note that it is not biological validation" },
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
