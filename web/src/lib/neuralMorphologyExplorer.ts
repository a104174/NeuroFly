import type { neuralActivityTrace } from "./neuralActivityTrace";

export const NEURAL_MORPHOLOGY_MANIFEST_URL =
  "/assets/neural/malecns-v1.0/hs-dnp15/manifest.json";
export const NEURAL_MORPHOLOGY_MANIFEST_SHA256 =
  "c538f94a6a3ea02390bfcb09ee77226fe6f0418455c0794cdfedd64593070697";
export const NEURAL_MORPHOLOGY_VIEW_ID = "hs_dnp15_native_malecns_view_v1";
export const NEURAL_MORPHOLOGY_TARGET_EXTENT = 10;

export const NEURAL_MORPHOLOGY_IDENTITIES = [
  { body_id: 10015, cell_type: "HSN", side: "R", model: "HS", index: 0, field: "hs_states[0]", role: "SOURCE" },
  { body_id: 10016, cell_type: "HSE", side: "R", model: "HS", index: 1, field: "hs_states[1]", role: "SOURCE" },
  { body_id: 10023, cell_type: "HSS", side: "R", model: "HS", index: 2, field: "hs_states[2]", role: "SOURCE" },
  { body_id: 10034, cell_type: "HSE", side: "L", model: "HS", index: 3, field: "hs_states[3]", role: "SOURCE" },
  { body_id: 10181, cell_type: "HSN", side: "L", model: "HS", index: 4, field: "hs_states[4]", role: "SOURCE" },
  { body_id: 10419, cell_type: "HSS", side: "L", model: "HS", index: 5, field: "hs_states[5]", role: "SOURCE" },
  { body_id: 11215, cell_type: "DNp15", side: "R", model: "DNp15", index: 0, field: "dnp15_states[0]", role: "TARGET" },
  { body_id: 12069, cell_type: "DNp15", side: "L", model: "DNp15", index: 1, field: "dnp15_states[1]", role: "TARGET" },
] as const;

export type NeuralMorphologyIdentity = (typeof NEURAL_MORPHOLOGY_IDENTITIES)[number];

export type NeuralMorphologyManifestBody = NeuralMorphologyIdentity & {
  readonly mapping_status: "IDENTITY_RESOLVED_MODEL_PROXY";
  readonly model_state: {
    readonly model: "HS" | "DNp15";
    readonly role: "SOURCE" | "TARGET";
    readonly index: number;
    readonly field: string;
    readonly semantics: "DIMENSIONLESS_SIGNED_COMPUTED_PROXY";
  };
  readonly morphology: {
    readonly path: string;
    readonly source_url: string;
    readonly source_sha256: string;
    readonly node_count: number;
    readonly component_count: number;
    readonly source_sampling: {
      readonly downres_level: string;
      readonly ds_intv: readonly [number, number, number];
    };
    readonly transform: "NONE_RAW_NATIVE_SWC";
    readonly healing: "NONE";
    readonly smoothing: "NONE";
    readonly repair: "NONE";
  };
};

export interface NeuralMorphologyManifest {
  readonly schema: "neurofly_malecns_neural_morphology_bundle_v1";
  readonly dataset: "male-cns:v1.0";
  readonly dataset_release: "2026-06-08";
  readonly license: "CC-BY";
  readonly attribution: string;
  readonly source_base_url: string;
  readonly coordinate_frame_id: "male_cns_v1_em_native_voxels";
  readonly coordinate_unit: "8_nm_voxel";
  readonly axis_semantics: string;
  readonly display_transform: string;
  readonly structural_authority: {
    readonly dataset: "male-cns:v1.0";
    readonly selection_record_id: string;
    readonly v1_status_id: string;
    readonly authority: string;
  };
  readonly selected_routes: readonly {
    readonly source_body_id: number;
    readonly target_body_id: number;
    readonly structural_contact_count: number;
  }[];
  readonly identity_interpretation: string;
  readonly bodies: readonly NeuralMorphologyManifestBody[];
}

export interface MorphologySourceBounds {
  readonly minimum: readonly [number, number, number];
  readonly maximum: readonly [number, number, number];
}

export interface ParsedNeuralMorphology {
  readonly identity: NeuralMorphologyManifestBody;
  readonly node_count: number;
  readonly component_count: number;
  readonly source_positions: Float32Array;
  readonly source_bounds: MorphologySourceBounds;
}

export interface DisplayNeuralMorphology extends ParsedNeuralMorphology {
  readonly view_positions: Float32Array;
}

export interface NeuralMorphologyView {
  readonly view_id: typeof NEURAL_MORPHOLOGY_VIEW_ID;
  readonly source_frame: "male_cns_v1_em_native_voxels";
  readonly source_unit: "8_nm_voxel";
  readonly axis_mapping: "IDENTITY_NATIVE_XYZ";
  readonly center_source: readonly [number, number, number];
  readonly uniform_scale: number;
  readonly source_bounds: MorphologySourceBounds;
  readonly bodies: readonly DisplayNeuralMorphology[];
}

export interface NeuralActivityViewSnapshot {
  readonly schema: "neural_activity_view_snapshot_v1";
  readonly session_id: string;
  readonly interval_tick: number;
  readonly accepted_tick: number;
  readonly simulation_time_s: number;
  readonly values: readonly {
    readonly body_id: number;
    readonly value: number;
    readonly semantics: "DIMENSIONLESS_SIGNED_COMPUTED_PROXY";
  }[];
  readonly neural_enabled: boolean;
  readonly neural_yaw_rad_s: number;
  readonly boundary_yaw_rad_s: number;
  readonly validity: "VALID";
}

export type NeuralActivityTrace = ReturnType<typeof neuralActivityTrace>;

const BASE_URL = "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/";
const EXPECTED_ROUTES = [
  [10015, 11215, 138],
  [10016, 11215, 122],
  [10023, 11215, 23],
  [10034, 12069, 78],
  [10181, 12069, 126],
  [10419, 12069, 14],
] as const;

function record(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${label} must be an object`);
  }
  return value as Record<string, unknown>;
}

function isSha256(value: unknown): value is string {
  return typeof value === "string" && /^[0-9a-f]{64}$/.test(value);
}

function exactIdentity(value: unknown, index: number): NeuralMorphologyIdentity {
  const row = record(value, `bodies[${index}]`);
  const modelState = record(row.model_state, `bodies[${index}].model_state`);
  const expected = NEURAL_MORPHOLOGY_IDENTITIES[index];
  if (!expected ||
      row.body_id !== expected.body_id || row.cell_type !== expected.cell_type ||
      row.side !== expected.side || modelState.model !== expected.model ||
      modelState.index !== expected.index || modelState.field !== expected.field ||
      modelState.role !== expected.role ||
      modelState.semantics !== "DIMENSIONLESS_SIGNED_COMPUTED_PROXY") {
    throw new Error(`Neural morphology identity mismatch at body index ${index}`);
  }
  return expected;
}

export function parseNeuralMorphologyManifest(value: unknown): NeuralMorphologyManifest {
  const manifest = record(value, "Neural morphology manifest");
  if (manifest.schema !== "neurofly_malecns_neural_morphology_bundle_v1" ||
      manifest.dataset !== "male-cns:v1.0" ||
      manifest.dataset_release !== "2026-06-08" ||
      manifest.license !== "CC-BY" ||
      manifest.coordinate_frame_id !== "male_cns_v1_em_native_voxels" ||
      manifest.coordinate_unit !== "8_nm_voxel" ||
      manifest.source_base_url !== BASE_URL ||
      typeof manifest.attribution !== "string" ||
      typeof manifest.axis_semantics !== "string" ||
      typeof manifest.display_transform !== "string" ||
      typeof manifest.identity_interpretation !== "string") {
    throw new Error("Unsupported neural morphology manifest provenance or coordinates");
  }
  const authority = record(manifest.structural_authority, "structural_authority");
  if (authority.dataset !== "male-cns:v1.0" ||
      authority.selection_record_id !== "435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41" ||
      authority.v1_status_id !== "1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6") {
    throw new Error("Neural morphology structural authority identity mismatch");
  }
  if (!Array.isArray(manifest.bodies) || manifest.bodies.length !== NEURAL_MORPHOLOGY_IDENTITIES.length) {
    throw new Error("Neural morphology bundle must contain the exact eight-body model sample");
  }
  const bodies = manifest.bodies.map((raw, index) => {
    const identity = exactIdentity(raw, index);
    const body = record(raw, `bodies[${index}]`);
    if (body.mapping_status !== "IDENTITY_RESOLVED_MODEL_PROXY") {
      throw new Error(`Body ${identity.body_id} has an unsupported model mapping status`);
    }
    const morphology = record(body.morphology, `body ${identity.body_id} morphology`);
    const id = identity.body_id;
    if (morphology.path !== `${id}.swc` ||
        morphology.source_url !== `${BASE_URL}${id}.swc` ||
        !isSha256(morphology.source_sha256) ||
        !Number.isInteger(morphology.node_count) || (morphology.node_count as number) <= 1 ||
        morphology.component_count !== 1 ||
        morphology.transform !== "NONE_RAW_NATIVE_SWC" ||
        morphology.healing !== "NONE" || morphology.smoothing !== "NONE" || morphology.repair !== "NONE") {
      throw new Error(`Body ${id} morphology source contract is invalid`);
    }
    const sampling = record(morphology.source_sampling, `body ${id} sampling`);
    if (typeof sampling.downres_level !== "string" || !Array.isArray(sampling.ds_intv) ||
        sampling.ds_intv.length !== 3 || sampling.ds_intv.some((part) => !Number.isInteger(part) || part <= 0)) {
      throw new Error(`Body ${id} sampling metadata is invalid`);
    }
    return {
      ...identity,
      mapping_status: "IDENTITY_RESOLVED_MODEL_PROXY" as const,
      model_state: {
        model: identity.model,
        role: identity.role,
        index: identity.index,
        field: identity.field,
        semantics: "DIMENSIONLESS_SIGNED_COMPUTED_PROXY" as const,
      },
      morphology: {
        path: morphology.path as string,
        source_url: morphology.source_url as string,
        source_sha256: morphology.source_sha256,
        node_count: morphology.node_count as number,
        component_count: 1 as const,
        source_sampling: {
          downres_level: sampling.downres_level,
          ds_intv: sampling.ds_intv as [number, number, number],
        },
        transform: "NONE_RAW_NATIVE_SWC" as const,
        healing: "NONE" as const,
        smoothing: "NONE" as const,
        repair: "NONE" as const,
      },
    };
  });
  if (!Array.isArray(manifest.selected_routes) || manifest.selected_routes.length !== EXPECTED_ROUTES.length) {
    throw new Error("Neural morphology selected-route set is invalid");
  }
  manifest.selected_routes.forEach((raw, index) => {
    const route = record(raw, `selected_routes[${index}]`);
    const [source, target, contacts] = EXPECTED_ROUTES[index];
    if (route.source_body_id !== source || route.target_body_id !== target ||
        route.structural_contact_count !== contacts) {
      throw new Error(`Neural morphology route identity mismatch at route ${index}`);
    }
  });
  return {
    schema: "neurofly_malecns_neural_morphology_bundle_v1",
    dataset: "male-cns:v1.0",
    dataset_release: "2026-06-08",
    license: "CC-BY",
    attribution: manifest.attribution,
    source_base_url: BASE_URL,
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    axis_semantics: manifest.axis_semantics,
    display_transform: manifest.display_transform,
    structural_authority: manifest.structural_authority as NeuralMorphologyManifest["structural_authority"],
    selected_routes: EXPECTED_ROUTES.map(([source_body_id, target_body_id, structural_contact_count]) => ({
      source_body_id, target_body_id, structural_contact_count,
    })),
    identity_interpretation: manifest.identity_interpretation,
    bodies,
  };
}

function finiteNumber(token: string, label: string): number {
  const value = Number(token);
  if (!Number.isFinite(value)) throw new Error(`${label} must be finite`);
  return value;
}

export function parseMaleCnsSwc(source: string, identity: NeuralMorphologyManifestBody): ParsedNeuralMorphology {
  const nodes: { id: number; x: number; y: number; z: number; parent: number }[] = [];
  const byId = new Map<number, (typeof nodes)[number]>();
  for (const [lineIndex, line] of source.split(/\r?\n/).entries()) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const fields = trimmed.split(/\s+/);
    if (fields.length !== 7) throw new Error(`SWC ${identity.body_id} line ${lineIndex + 1} must contain seven fields`);
    const id = Number(fields[0]);
    const type = Number(fields[1]);
    const x = finiteNumber(fields[2], "SWC x coordinate");
    const y = finiteNumber(fields[3], "SWC y coordinate");
    const z = finiteNumber(fields[4], "SWC z coordinate");
    const radius = finiteNumber(fields[5], "SWC radius");
    const parent = Number(fields[6]);
    if (!Number.isSafeInteger(id) || id <= 0 || !Number.isSafeInteger(type) ||
        !Number.isSafeInteger(parent) || parent < -1 || parent === id || radius < 0 || byId.has(id)) {
      throw new Error(`SWC ${identity.body_id} line ${lineIndex + 1} has invalid node identity or radius`);
    }
    const node = { id, x, y, z, parent };
    nodes.push(node);
    byId.set(id, node);
  }
  if (nodes.length !== identity.morphology.node_count) {
    throw new Error(`SWC ${identity.body_id} node count differs from its pinned manifest`);
  }
  const roots = nodes.filter((node) => node.parent === -1);
  if (roots.length !== identity.morphology.component_count) {
    throw new Error(`SWC ${identity.body_id} component count differs from its pinned manifest`);
  }
  const resolved = new Set(roots.map((node) => node.id));
  for (const node of nodes) {
    let current = node;
    const path: number[] = [];
    const visiting = new Set<number>();
    while (!resolved.has(current.id)) {
      if (visiting.has(current.id)) throw new Error(`SWC ${identity.body_id} contains a parent cycle`);
      visiting.add(current.id);
      path.push(current.id);
      const parent = byId.get(current.parent);
      if (!parent) throw new Error(`SWC ${identity.body_id} references a missing parent`);
      current = parent;
    }
    for (const id of path) resolved.add(id);
  }
  const minimum: [number, number, number] = [Infinity, Infinity, Infinity];
  const maximum: [number, number, number] = [-Infinity, -Infinity, -Infinity];
  const positions = new Float32Array((nodes.length - roots.length) * 6);
  let offset = 0;
  for (const node of nodes) {
    for (const [axis, value] of [node.x, node.y, node.z].entries()) {
      minimum[axis] = Math.min(minimum[axis], value);
      maximum[axis] = Math.max(maximum[axis], value);
    }
    if (node.parent === -1) continue;
    const parent = byId.get(node.parent)!;
    positions.set([node.x, node.y, node.z, parent.x, parent.y, parent.z], offset);
    offset += 6;
  }
  if (!positions.length || ![...minimum, ...maximum].every(Number.isFinite)) {
    throw new Error(`SWC ${identity.body_id} contains no finite drawable geometry`);
  }
  return {
    identity,
    node_count: nodes.length,
    component_count: roots.length,
    source_positions: positions,
    source_bounds: { minimum, maximum },
  };
}

export function deriveNeuralMorphologyView(bodies: readonly ParsedNeuralMorphology[]): NeuralMorphologyView {
  if (bodies.length !== NEURAL_MORPHOLOGY_IDENTITIES.length ||
      bodies.some((body, index) => body.identity.body_id !== NEURAL_MORPHOLOGY_IDENTITIES[index].body_id)) {
    throw new Error("Neural morphology view requires the complete pinned eight-body sample in canonical order");
  }
  const minimum: [number, number, number] = [Infinity, Infinity, Infinity];
  const maximum: [number, number, number] = [-Infinity, -Infinity, -Infinity];
  for (const body of bodies) {
    for (let axis = 0; axis < 3; axis += 1) {
      minimum[axis] = Math.min(minimum[axis], body.source_bounds.minimum[axis]);
      maximum[axis] = Math.max(maximum[axis], body.source_bounds.maximum[axis]);
    }
  }
  const center: [number, number, number] = [
    (minimum[0] + maximum[0]) / 2,
    (minimum[1] + maximum[1]) / 2,
    (minimum[2] + maximum[2]) / 2,
  ];
  const extent = Math.max(maximum[0] - minimum[0], maximum[1] - minimum[1], maximum[2] - minimum[2]);
  if (!(extent > 0) || !Number.isFinite(extent)) throw new Error("Neural morphology source bounds are invalid");
  const uniformScale = NEURAL_MORPHOLOGY_TARGET_EXTENT / extent;
  const viewBodies = bodies.map((body) => {
    const positions = new Float32Array(body.source_positions.length);
    for (let index = 0; index < positions.length; index += 3) {
      positions[index] = (body.source_positions[index] - center[0]) * uniformScale;
      positions[index + 1] = (body.source_positions[index + 1] - center[1]) * uniformScale;
      positions[index + 2] = (body.source_positions[index + 2] - center[2]) * uniformScale;
    }
    if (!Array.from(positions).every(Number.isFinite)) throw new Error(`Display coordinates for ${body.identity.body_id} are invalid`);
    return { ...body, view_positions: positions };
  });
  return {
    view_id: NEURAL_MORPHOLOGY_VIEW_ID,
    source_frame: "male_cns_v1_em_native_voxels",
    source_unit: "8_nm_voxel",
    axis_mapping: "IDENTITY_NATIVE_XYZ",
    center_source: center,
    uniform_scale: uniformScale,
    source_bounds: { minimum, maximum },
    bodies: viewBodies,
  };
}

async function sha256(bytes: ArrayBuffer): Promise<string> {
  if (!globalThis.crypto?.subtle) throw new Error("Secure SHA-256 verification is unavailable in this browser context");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function loadVerifiedNeuralMorphology(fetcher: typeof fetch = fetch): Promise<{
  readonly manifest: NeuralMorphologyManifest;
  readonly view: NeuralMorphologyView;
}> {
  const manifestResponse = await fetcher(NEURAL_MORPHOLOGY_MANIFEST_URL, { cache: "force-cache" });
  if (!manifestResponse.ok) throw new Error(`Neural morphology manifest request failed (${manifestResponse.status})`);
  const manifestBytes = await manifestResponse.arrayBuffer();
  if (await sha256(manifestBytes) !== NEURAL_MORPHOLOGY_MANIFEST_SHA256) {
    throw new Error("Neural morphology manifest SHA-256 mismatch");
  }
  const manifestText = new TextDecoder("utf-8", { fatal: true }).decode(manifestBytes);
  const manifest = parseNeuralMorphologyManifest(JSON.parse(manifestText) as unknown);
  const parsed = await Promise.all(manifest.bodies.map(async (identity) => {
    const url = `${NEURAL_MORPHOLOGY_MANIFEST_URL.slice(0, NEURAL_MORPHOLOGY_MANIFEST_URL.lastIndexOf("/"))}/${identity.morphology.path}`;
    const response = await fetcher(url, { cache: "force-cache" });
    if (!response.ok) throw new Error(`MaleCNS skeleton ${identity.body_id} request failed (${response.status})`);
    const bytes = await response.arrayBuffer();
    if (await sha256(bytes) !== identity.morphology.source_sha256) {
      throw new Error(`MaleCNS skeleton ${identity.body_id} SHA-256 mismatch`);
    }
    const source = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    return parseMaleCnsSwc(source, identity);
  }));
  return { manifest, view: deriveNeuralMorphologyView(parsed) };
}

export function neuralActivityViewSnapshot(sessionId: string, trace: NeuralActivityTrace): NeuralActivityViewSnapshot {
  if (!sessionId || !Number.isSafeInteger(trace.tick) || trace.tick < 0 ||
      trace.accepted_tick !== trace.tick + 1 || !Number.isFinite(trace.time_s) ||
      !Number.isFinite(trace.neural_yaw_rad_s) || !Number.isFinite(trace.boundary_yaw_rad_s) ||
      trace.states.length !== NEURAL_MORPHOLOGY_IDENTITIES.length ||
      trace.states.some((state, index) => state.id !== NEURAL_MORPHOLOGY_IDENTITIES[index].body_id ||
        state.model !== NEURAL_MORPHOLOGY_IDENTITIES[index].model ||
        state.semantics !== "COMPUTED_MODEL_STATE" || !Number.isFinite(state.value))) {
    throw new Error("Live neural activity is unavailable or does not match the pinned morphology identities");
  }
  return {
    schema: "neural_activity_view_snapshot_v1",
    session_id: sessionId,
    interval_tick: trace.tick,
    accepted_tick: trace.accepted_tick,
    simulation_time_s: trace.time_s,
    values: trace.states.map((state) => ({
      body_id: state.id,
      value: state.value,
      semantics: "DIMENSIONLESS_SIGNED_COMPUTED_PROXY",
    })),
    neural_enabled: trace.neural_enabled,
    neural_yaw_rad_s: trace.neural_yaw_rad_s,
    boundary_yaw_rad_s: trace.boundary_yaw_rad_s,
    validity: "VALID",
  };
}
