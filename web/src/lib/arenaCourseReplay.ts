import { Vector3 } from "three";
import { courseScene, parseCoursePlayback, type CoursePlaybackResult } from "./courseControlPlayback";
import { ARENA } from "./experimentalArena";
import { FLY_VIEWER_ASSET } from "./flyViewer";
import { flyPresentationAnchor } from "./flyVisualInstance";

export const ARENA_COURSE_ID = "EXPLORATORY_COURSE_CONTROL" as const;
export const ARENA_COURSE_PAYLOAD_SHA256 = "7fddc1109495023d8f64744237796d5d8e86852abef80b6979f1994088d46806";
export type ArenaCoursePose = { anchor: [number, number, number]; assetOffset: [number, number, number]; rotation: number };

/** Recorded abstract orientation only. Position is an unchanged presentation convention. */
export function arenaCoursePose(replay: CoursePlaybackResult, cursor: number): ArenaCoursePose {
  if (!Number.isFinite(cursor) || cursor < 0 || cursor > replay.frames.length - 1) throw new Error("Boundary de replay inválido.");
  if (replay.scenario.id !== ARENA_COURSE_ID || replay.world_reference.period_eq !== 1 || ARENA.flyScale !== .30) throw new Error("Replay incompatível com a arena.");
  const a = new Vector3(...flyPresentationAnchor(FLY_VIEWER_ASSET, "historical"));
  const anchor = a.clone().multiplyScalar(ARENA.flyScale).add(new Vector3(...ARENA.flyOffset)).toArray();
  const { renderRotation } = courseScene(replay, cursor);
  if (!Number.isFinite(renderRotation)) throw new Error("Orientação inválida.");
  return { anchor, assetOffset: a.negate().toArray(), rotation: renderRotation };
}

/** Fail before starting playback; never clamp scientific poses or resize the specimen. */
export function validateArenaCourseReplay(value: unknown): CoursePlaybackResult {
  const replay = parseCoursePlayback(value);
  if (replay.artifact_id !== "f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581") throw new Error("A autoridade canónica Course não corresponde à esperada.");
  const transform = FLY_VIEWER_ASSET.canonical_transform;
  if (transform.scene_uniform_scale !== 1 || [...transform.scene_position, ...transform.scene_rotation_euler_rad].some(n => n !== 0)) throw new Error("O fitting do asset não corresponde ao mapping auditado.");
  const { width, depth, height, wall } = ARENA.chamber;
  // A bounding sphere in X/Z about the anchor covers every angle, including interpolation.
  const pose = arenaCoursePose(replay, 0);
  let radius = 0;
  for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]])
    for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) {
      radius = Math.max(radius, Math.hypot(x + pose.assetOffset[0], z + pose.assetOffset[2]) * ARENA.flyScale);
    }
  const lowY = ARENA.flyOffset[1] + FLY_VIEWER_ASSET.bounds.min[1] * ARENA.flyScale;
  const highY = ARENA.flyOffset[1] + FLY_VIEWER_ASSET.bounds.max[1] * ARENA.flyScale;
  if (Math.abs(pose.anchor[0]) + radius >= (width - wall) / 2 || Math.abs(pose.anchor[2]) + radius >= (depth - wall) / 2 || lowY <= 0 || highY >= height - wall / 2) throw new Error("O espécime ultrapassa os limites visuais da câmara. Replay não iniciado.");
  replay.frames.forEach((_, i) => arenaCoursePose(replay, i));
  return replay;
}
