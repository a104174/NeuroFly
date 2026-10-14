import { locomotionScene, type LocomotionReplay } from "./experimentalLocomotion";
import type { NeuralArtifact } from "./neuralLocomotion";

export const COMPARISON_CONDITIONS = [
  { key: "B", index: 1, id: "NEURAL_STEERING", label: "Steering neural ativo", color: "#67d3e0", symbol: "●", plane: .4 },
  { key: "C", index: 2, id: "NEURAL_OUTPUT_DISABLED", label: "Saída para steering desligada", color: "#f3c777", symbol: "■", plane: .4 },
  { key: "D", index: 3, id: "VISUAL_PLANE_INTERVENTION", label: "Ambiente visual alterado", color: "#c6a8f5", symbol: "◆", plane: -.4 },
] as const;
export type ComparisonKey = typeof COMPARISON_CONDITIONS[number]["key"];
export type ComparisonScene = ReturnType<typeof locomotionScene>;
export function wrappedAngle(delta: number) {
  if (!Number.isFinite(delta)) throw new Error("Invalid angular difference");
  return Math.atan2(Math.sin(delta), Math.cos(delta));
}
export function comparisonDelta(a: ComparisonScene, b: ComparisonScene) {
  return { signedHeading: wrappedAngle(a.pose.rotation - b.pose.rotation),
    separation: Math.hypot(a.pose.anchor[0]-b.pose.anchor[0], a.pose.anchor[2]-b.pose.anchor[2]),
    traveledDifference: a.distance-b.distance };
}
export function comparisonScenes(replay: LocomotionReplay, time: number) {
  if (!Number.isFinite(time) || time < 0 || time > replay.config.duration_s) throw new Error("Invalid comparison time");
  return COMPARISON_CONDITIONS.map(c => ({ ...c, scene: locomotionScene(replay, c.index, time) }));
}
// Built once per validated artifact. Maxima are over stored boundaries, not current-time deltas.
export function comparisonOverview(authority: NeuralArtifact) {
  if (authority.artifact_id !== "4d7c791224f21ecf677df81d2127a6f8b753974694b6b324afc1948da3fb9064") throw new Error("Unsupported comparison artifact");
  const tracks = COMPARISON_CONDITIONS.map(c => {
    const run = authority.result.runs[c.index];
    if (run.id !== c.id || run.condition?.plane_z !== c.plane || run.frames.length !== 401) throw new Error("Incompatible comparison condition");
    return { ...c, points: run.frames.map(f => f.position), contacts: run.contact_events };
  });
  const maxima = [2, 3].map(index => {
    const a = authority.result.runs[1], b = authority.result.runs[index];
    let heading = { value: -1, time: 0 }, separation = { value: -1, time: 0 };
    for (let i=0; i<a.frames.length; i++) {
      const x=a.frames[i], y=b.frames[i];
      if (x.time !== y.time) throw new Error("Unaligned comparison boundaries");
      const yaw=Math.abs(x.orientation-y.orientation), distance=Math.hypot(x.position[0]-y.position[0],x.position[2]-y.position[2]);
      if (yaw>heading.value) heading={value:yaw,time:x.time};
      if (distance>separation.value) separation={value:distance,time:x.time};
    }
    return { pair: index===2 ? "B−C" : "B−D", heading, separation };
  });
  return { tracks, maxima, landmarkX: authority.config.policy.landmark_x };
}
