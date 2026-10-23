import { Vector3 } from "three";
import { arenaCamera, type ArenaCameraView } from "@/lib/experimentalArena";

export type ViewerCameraView = ArenaCameraView | "explore";

/** Presentation only. No observer, body, solver or scientific configuration. */
export const EXPLORE_STYLE = Object.freeze({
  background: "#081722", floor: "#173444", frame: "#7babb5",
  panel: "#c9e6e9", panelOpacity: .035, backdrop: "#102733",
});

export const EXPLORE_CAMERA_LIMITS = Object.freeze({ minDistance: 1, maxDistance: 6, maxPolarAngle: 1.35 });

export const EXPLORE_TARGET_LIFT = .2;

/** Fixed framing above the visual anchor reveals the enclosure behind the fly. */
export function exploreCamera(aspect: number) {
  if (!Number.isFinite(aspect) || aspect <= 0) throw new Error("Invalid Explore camera aspect ratio");
  const { target } = arenaCamera(aspect, "inspect");
  target[1] += EXPLORE_TARGET_LIFT;
  const direction = new Vector3(-.5, .35, 1).normalize();
  const distance = Math.max(1.15, .9 / Math.max(.05, aspect));
  return { target: [...target], position: new Vector3(...target).addScaledVector(direction, distance).toArray(), distance, fov: 50 };
}
