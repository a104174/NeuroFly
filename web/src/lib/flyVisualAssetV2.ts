import type { FlyVisualAssetManifestV1 } from "./flyVisualAsset";

export const VISUAL_SCHEMA_V2 = "neurofly_visual_asset_manifest_v2" as const;
export const REQUIRED_ANATOMY = ["Head", "Thorax", "Abdomen", "Eye.L", "Eye.R", "Wing.L", "Wing.R", "Leg.L.Front", "Leg.L.Middle", "Leg.L.Rear", "Leg.R.Front", "Leg.R.Middle", "Leg.R.Rear"] as const;
export type StaticBodyAnatomy = { body_topology: "separated" } | { body_topology: "combined"; body_node: string; limitation: string };
export const STATIC_ANATOMY = REQUIRED_ANATOMY.filter(name => name !== "Thorax" && name !== "Abdomen");
export type TextureRole = "base_color" | "emissive" | "normal" | "metallic_roughness" | "occlusion";
export interface FlyVisualAssetManifestV2 extends Omit<FlyVisualAssetManifestV1, "schema" | "asset_id" | "asset_version" | "measured"> {
  schema: typeof VISUAL_SCHEMA_V2;
  asset_id: string;
  asset_version: 2;
  canonical_transform: FlyVisualAssetManifestV1["canonical_transform"] & { source_up_axis: "+Z"; source_forward_axis: "-Y" };
  specimen: { species: "Drosophila melanogaster"; sex: "male" | "female" | "unspecified"; reference_basis: string };
  bounds: { min: [number, number, number]; max: [number, number, number] };
  anatomy?: StaticBodyAnatomy;
  nodes: { root: string; required: string[]; optional: string[] };
  materials: { strategy: "AUTHORED_PBR"; roles: { body: string[]; eyes: string[]; wings: string[] }; wings: { thin: true; double_sided: true; alpha_mode: "BLEND" | "MASK" }; textures: { role: TextureRole; color_space: "srgb" | "linear" }[] };
  capabilities: { static: true; skeletal_animation: false; morph_animation: false };
  measured: { triangle_count: number; material_count: number; animation_count: 0; camera_count: 0; light_count: 0; texture_image_count: number };
  provenance: { source_url: string; author: string; license: string; license_version: string; license_url: string; attribution: string; source_sha256: string; modifications: string; texture_rights: string; material_origins: string; exporter_version: string };
}
function object(v: unknown): Record<string, unknown> {
  if (!v || typeof v !== "object" || Array.isArray(v)) throw new Error("Invalid v2 visual metadata object.");
  return v as Record<string, unknown>;
}
function requireValue(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}
function text(v: unknown): v is string { return typeof v === "string" && v.trim().length > 0; }
function triplet(v: unknown): v is [number, number, number] { return Array.isArray(v) && v.length === 3 && v.every(n => typeof n === "number" && Number.isFinite(n)); }
function names(v: unknown): v is string[] { return Array.isArray(v) && v.every(text) && new Set(v).size === v.length; }
function hash(v: unknown) { return typeof v === "string" && /^[a-f0-9]{64}$/.test(v); }
function publicUrl(v: unknown) { return typeof v === "string" && /^https:\/\/[^\s]+$/.test(v) && !/[?#@]/.test(v); }

/** Metadata establishes visual provenance, never biological calibration or motion. */
export function parseVisualV2(value: unknown): FlyVisualAssetManifestV2 {
  const m = object(value);
  const allowed = ["schema", "asset_id", "asset_version", "role", "export", "runtime", "canonical_transform", "scientific_status", "anatomy", "specimen", "bounds", "nodes", "materials", "capabilities", "measured", "provenance"];
  requireValue(Object.keys(m).every(k => allowed.includes(k)), "Unknown v2 visual metadata field.");
  requireValue(m.schema === VISUAL_SCHEMA_V2 && m.asset_version === 2 && text(m.asset_id) && m.role === "NEUROFLY_VISUAL_ASSET", "Unsupported v2 visual identity.");
  const r = object(m.runtime), t = object(m.canonical_transform), s = object(m.specimen), b = object(m.bounds);
  requireValue(typeof r.public_url === "string" && /^\/assets\/fly\/[a-zA-Z0-9_-]+\.glb$/.test(r.public_url) && r.glb_path === "web/public" + r.public_url && hash(r.sha256), "Invalid v2 visual runtime reference.");
  requireValue(t.source_up_axis === "+Z" && t.source_forward_axis === "-Y" && t.runtime_up_axis === "+Y" && t.runtime_forward_axis === "+Z" && t.runtime_left_axis === "-X" && t.origin === "thorax center" && t.normalized_scale === "runtime long-axis (+Z) extent is 1.0 asset unit" && triplet(t.scene_position) && triplet(t.scene_rotation_euler_rad) && typeof t.scene_uniform_scale === "number" && Number.isFinite(t.scene_uniform_scale) && t.scene_uniform_scale > 0, "Invalid v2 axes, origin or presentation fitting.");
  requireValue(s.species === "Drosophila melanogaster" && ["male", "female", "unspecified"].includes(String(s.sex)) && text(s.reference_basis), "Invalid visual specimen designation.");
  requireValue(triplet(b.min) && triplet(b.max) && b.max.every((n, i) => n > (b.min as number[])[i]) && Math.abs(b.max[2] - b.min[2] - 1) < 1e-6, "Invalid normalized visual bounds.");
  const n = object(m.nodes);
  const root = n.root, required = n.required, optional = n.optional;
  requireValue(text(root) && names(required) && names(optional), "Invalid anatomical node names.");
  let requiredAnatomy: readonly string[] = REQUIRED_ANATOMY;
  if (m.anatomy !== undefined) {
    const anatomy = object(m.anatomy);
    requireValue(anatomy.body_topology === "separated" || anatomy.body_topology === "combined", "Unknown static body topology.");
    if (anatomy.body_topology === "combined") {
      requireValue(Object.keys(anatomy).every(k => ["body_topology", "body_node", "limitation"].includes(k)) && text(anatomy.body_node) && text(anatomy.limitation), "Combined body needs a real node and explicit limitation.");
      requireValue(![root, ...STATIC_ANATOMY, "Thorax", "Abdomen"].includes(anatomy.body_node) && ![...required, ...optional].some(k => k === "Thorax" || k === "Abdomen"), "Conflicting combined/separated anatomy.");
      requiredAnatomy = [...STATIC_ANATOMY, anatomy.body_node];
    } else {
      requireValue(Object.keys(anatomy).every(k => k === "body_topology"), "Conflicting separated anatomy declaration.");
    }
  }
  requireValue(requiredAnatomy.every(k => required.includes(k)) && !required.includes(root) && !optional.some(k => required.includes(k) || k === root), "Invalid required/optional anatomical nodes.");
  const c = object(m.capabilities), count = object(m.measured), scientific = object(m.scientific_status), exp = object(m.export);
  requireValue(c.static === true && c.skeletal_animation === false && c.morph_animation === false && count.animation_count === 0 && count.camera_count === 0 && count.light_count === 0, "Only static visual assets are supported.");
  requireValue([count.triangle_count, count.material_count, count.texture_image_count].every(v => Number.isInteger(v) && Number(v) >= 0) && Number(count.triangle_count) > 0 && Number(count.material_count) > 0, "Invalid visual asset counts.");
  requireValue(scientific.presentation_only === true && text(scientific.disclaimer) && exp.tool === "Blender" && text(exp.tool_version), "Missing visual limitations or export provenance.");
  const material = object(m.materials), roles = object(material.roles), wings = object(material.wings);
  requireValue(material.strategy === "AUTHORED_PBR" && [roles.body, roles.eyes, roles.wings].every(v => names(v) && v.length > 0), "Missing authored material roles.");
  const slots = [...roles.body as string[], ...roles.eyes as string[], ...roles.wings as string[]];
  requireValue(new Set(slots).size === slots.length, "Material roles must be disjoint.");
  requireValue(wings.thin === true && wings.double_sided === true && ["BLEND", "MASK"].includes(String(wings.alpha_mode)), "Invalid thin-wing transparency contract.");
  requireValue(Array.isArray(material.textures), "Missing texture declarations.");
  const seen = new Set<string>();
  for (const entry of material.textures) {
    const texture = object(entry); const role = String(texture.role);
    requireValue(["base_color", "emissive", "normal", "metallic_roughness", "occlusion"].includes(role) && !seen.has(role) && texture.color_space === (["base_color", "emissive"].includes(role) ? "srgb" : "linear"), "Invalid texture role/color space.");
    seen.add(role);
  }
  requireValue((count.texture_image_count === 0) === (material.textures.length === 0), "Texture count/declaration mismatch.");
  const p = object(m.provenance);
  requireValue(publicUrl(p.source_url) && publicUrl(p.license_url) && hash(p.source_sha256) && [p.author, p.license, p.license_version, p.attribution, p.modifications, p.texture_rights, p.material_origins, p.exporter_version].every(text), "Incomplete asset licensing or provenance.");
  return value as FlyVisualAssetManifestV2;
}
