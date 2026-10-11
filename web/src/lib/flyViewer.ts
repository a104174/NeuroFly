import { Box3, Vector3 } from "three";
import manifestJson from "@/assets/fly_visual_v2f.json";
import { parseVisualV2 } from "./flyVisualAssetV2";
import { flyPresentationAnchor } from "./flyVisualInstance";

export const FLY_VIEWER_ASSET = parseVisualV2(manifestJson);
export type FlyViewerView = "three-quarter" | "lateral" | "head" | "dorsal";

/** Fit all asset-bound corners into the chosen view, preserving the thoracic target. */
export function flyViewerCamera(aspect: number, view: FlyViewerView = "three-quarter") {
  const target = new Vector3(...flyPresentationAnchor(FLY_VIEWER_ASSET, "historical"));
  const bounds = new Box3(new Vector3(...FLY_VIEWER_ASSET.bounds.min), new Vector3(...FLY_VIEWER_ASSET.bounds.max));
  const fov = 35;
  const tanVertical = Math.tan(fov * Math.PI / 360);
  const tanHorizontal = tanVertical * Math.max(aspect, .1);
  const directions = { "three-quarter": [-1.3, .85, 1.7], lateral: [-1, .12, 0], head: [0, .08, 1], dorsal: [0, 1, .001] };
  const direction = new Vector3(...directions[view]).normalize();
  const right = new Vector3().crossVectors(new Vector3(0, 1, 0), direction).normalize();
  const up = new Vector3().crossVectors(direction, right).normalize();
  let distance = 0;
  for (const x of [bounds.min.x, bounds.max.x]) for (const y of [bounds.min.y, bounds.max.y]) for (const z of [bounds.min.z, bounds.max.z]) {
    const corner = new Vector3(x, y, z).sub(target);
    distance = Math.max(distance, corner.dot(direction) + 1.18 * Math.max(Math.abs(corner.dot(right)) / tanHorizontal, Math.abs(corner.dot(up)) / tanVertical));
  }
  return { target: target.toArray(), position: target.clone().addScaledVector(direction, distance).toArray(), fov, distance };
}

export async function verifyFlyViewerBytes(bytes: ArrayBuffer, expected = FLY_VIEWER_ASSET.runtime.sha256) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  const actual = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, "0")).join("");
  if (actual !== expected) throw new Error("The fly asset checksum does not match its approved manifest.");
}
