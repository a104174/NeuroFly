import manifestJson from "@/assets/fly_visual_v1.json";

export const FLY_VISUAL_ASSET_SCHEMA =
  "neurofly_visual_asset_manifest_v1" as const;
export const FLY_VISUAL_ASSET_ID = "neurofly_fly_visual_v1" as const;
export const FLY_VISUAL_ASSET_VERSION = 1 as const;

export type FlyAssetLoadStatus = "loading" | "ready" | "error";

export interface FlyVisualAssetManifest {
  schema: typeof FLY_VISUAL_ASSET_SCHEMA;
  asset_id: typeof FLY_VISUAL_ASSET_ID;
  asset_version: typeof FLY_VISUAL_ASSET_VERSION;
  role: "NEUROFLY_VISUAL_ASSET";
  runtime: {
    glb_path: string;
    public_url: string;
    sha256: string;
  };
  canonical_transform: {
    runtime_up_axis: "+Y";
    runtime_forward_axis: "+Z";
    runtime_left_axis: "-X";
    origin: string;
    normalized_scale: string;
    scene_position: [number, number, number];
    scene_rotation_euler_rad: [number, number, number];
    scene_uniform_scale: number;
  };
  measured: {
    triangle_count: number;
    material_count: number;
    animation_count: 0;
    camera_count: 0;
    light_count: 0;
    texture_image_count: 0;
  };
  scientific_status: {
    presentation_only: true;
    disclaimer: string;
  };
}

function isNumberTriplet(value: unknown): value is [number, number, number] {
  return (
    Array.isArray(value) &&
    value.length === 3 &&
    value.every((item) => typeof item === "number" && Number.isFinite(item))
  );
}

function validCount(value: unknown): value is number {
  return Number.isInteger(value) && Number(value) >= 0;
}

export function parseFlyVisualAssetManifest(
  value: unknown,
): FlyVisualAssetManifest {
  if (typeof value !== "object" || value === null) {
    throw new Error("Fly visual asset manifest must be an object.");
  }
  const manifest = value as Record<string, unknown>;
  if (
    manifest.schema !== FLY_VISUAL_ASSET_SCHEMA ||
    manifest.asset_id !== FLY_VISUAL_ASSET_ID ||
    manifest.asset_version !== FLY_VISUAL_ASSET_VERSION ||
    manifest.role !== "NEUROFLY_VISUAL_ASSET"
  ) {
    throw new Error("Fly visual asset identity is not supported.");
  }
  const runtime = manifest.runtime as Record<string, unknown> | undefined;
  if (
    runtime?.public_url !== "/assets/fly/fly_visual_v1.glb" ||
    runtime.glb_path !== "web/public/assets/fly/fly_visual_v1.glb" ||
    typeof runtime.sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(runtime.sha256)
  ) {
    throw new Error("Fly visual asset runtime reference is invalid.");
  }
  const transform = manifest.canonical_transform as
    | Record<string, unknown>
    | undefined;
  if (
    transform?.runtime_up_axis !== "+Y" ||
    transform.runtime_forward_axis !== "+Z" ||
    transform.runtime_left_axis !== "-X" ||
    typeof transform.origin !== "string" ||
    typeof transform.normalized_scale !== "string" ||
    !isNumberTriplet(transform.scene_position) ||
    !isNumberTriplet(transform.scene_rotation_euler_rad) ||
    typeof transform.scene_uniform_scale !== "number" ||
    !Number.isFinite(transform.scene_uniform_scale) ||
    transform.scene_uniform_scale <= 0
  ) {
    throw new Error("Fly visual asset transform contract is invalid.");
  }
  const measured = manifest.measured as Record<string, unknown> | undefined;
  if (
    !validCount(measured?.triangle_count) ||
    !validCount(measured.material_count) ||
    measured.animation_count !== 0 ||
    measured.camera_count !== 0 ||
    measured.light_count !== 0 ||
    measured.texture_image_count !== 0
  ) {
    throw new Error("Fly visual asset measured metadata is invalid.");
  }
  const status = manifest.scientific_status as
    | Record<string, unknown>
    | undefined;
  if (
    status?.presentation_only !== true ||
    typeof status.disclaimer !== "string"
  ) {
    throw new Error("Fly visual asset must be explicitly presentation-only.");
  }
  return value as FlyVisualAssetManifest;
}

export function flyAssetStatusMessage(status: FlyAssetLoadStatus): string {
  if (status === "loading") return "Loading 3D asset…";
  if (status === "error") return "Fly asset unavailable · procedural fallback";
  return `${FLY_VISUAL_ASSET_ID} · presentation only`;
}

export const FLY_VISUAL_ASSET = parseFlyVisualAssetManifest(manifestJson);
