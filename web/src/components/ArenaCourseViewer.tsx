"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { advanceScenarioCursor } from "@/lib/scenarioPlayback";
import { courseScene, type CoursePlaybackResult } from "@/lib/courseControlPlayback";
import { ARENA_COURSE_ID, arenaCoursePose, validateArenaCourseReplay } from "@/lib/arenaCourseReplay";
import { advanceLocomotion, loadLocomotion, locomotionScene, type LocomotionReplay } from "@/lib/experimentalLocomotion";
import { loadNeuralLocomotion, type NeuralArtifact } from "@/lib/neuralLocomotion";
import { displayText } from "@/lib/frozenText";
import { comparisonOverview, comparisonScenes } from "@/lib/neuralSteeringComparison";
import { NeuralComparisonInspector } from "./NeuralComparisonInspector";
import {ContinuousNavigationArena} from "./ContinuousNavigationArena";
import { InteractiveNeuralArena } from "./InteractiveNeuralArena";
import { MotorGaitBridgeArena } from "./MotorGaitBridgeArena";
import { FlightVisualPreview } from "./FlightVisualPreview";
import { NeuralFlightArena } from "./NeuralFlightArena";
import { EngineeringFlightArena } from "./EngineeringFlightArena";
import { FlyViewer } from "./FlyViewer";

export function ArenaCourseViewer() {
  const [mode, setMode] = useState<"static" | "course" | "locomotion" | "neural" | "comparison" | "interactive" | "navigation" | "moving" | "independent" | "visual-programs" | "scheduler" | "motor-bridge" | "flight-preview" | "flight-v8" | "neural-flight">("static");
  const [loadedProtocol,setLoadedProtocol]=useState(false);
  const [loadedVisual,setLoadedVisual]=useState(false);
  const [loadedIndependent,setLoadedIndependent] = useState(false);
  const [loadedMoving,setLoadedMoving] = useState(false);
  const [neuralAuthority, setNeuralAuthority] = useState<NeuralArtifact | null>(null);
  const [locomotion, setLocomotion] = useState<LocomotionReplay | null>(null);
  const [runIndex, setRunIndex] = useState(0);
  const [time, setTime] = useState(0);
  const [replay, setReplay] = useState<CoursePlaybackResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(false);
  const request = useRef(0);
  useEffect(() => () => { request.current++; }, []);
  const neuralMode = mode === "neural" || mode === "comparison";
  const active = mode === "course" && replay !== null && !error;
  const moving = (mode === "locomotion" || mode === "neural" || mode === "comparison") && locomotion !== null && !error;
  const motionPlaying = moving && playing && time < locomotion.config.duration_s;
  const last = replay ? replay.frames.length - 1 : 0;
  const isPlaying = active && playing && cursor < last;
  useEffect(() => {
    if (!isPlaying) return;
    let animation = 0, previous: number | null = null;
    const tick = (now: number) => {
      if (previous !== null) {
        const elapsed = now - previous;
        setCursor(c => advanceScenarioCursor(c, elapsed, true, last));
      }
      previous = now;
      animation = requestAnimationFrame(tick);
    };
    animation = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animation);
  }, [isPlaying, last]);

  useEffect(() => {
    if (!motionPlaying) return;
    let animation = 0, previous: number | null = null;
    const tick = (now: number) => {
      if (previous !== null) { const elapsed = now - previous; setTime(t => advanceLocomotion(t, elapsed, true)); }
      previous = now;
      animation = requestAnimationFrame(tick);
    };
    animation = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animation);
  }, [motionPlaying]);

  async function choose(mode: "static" | "course" | "locomotion" | "neural" | "comparison" | "interactive" | "navigation" | "moving" | "independent" | "visual-programs" | "scheduler" | "motor-bridge" | "flight-preview" | "flight-v8" | "neural-flight") {
    const generation = ++request.current;
    setMode(mode); setLoadedProtocol(mode === "scheduler"); setLoadedVisual(mode === "visual-programs"); setLoadedMoving(mode === "moving" || mode === "independent" || mode === "visual-programs" || mode === "scheduler"); setLoadedIndependent(mode === "independent" || mode === "visual-programs" || mode === "scheduler"); setTime(0); setNeuralAuthority(null); setLocomotion(null); setRunIndex(0); setPlaying(false); setCursor(0); setReplay(null); setError(null); setLoading(mode !== "static");
    if (mode === "neural-flight" || mode === "flight-v8" || mode === "flight-preview" || mode === "motor-bridge" || mode === "static" || mode === "interactive" || mode === "navigation" || mode === "moving" || mode === "independent" || mode === "visual-programs" || mode === "scheduler") { setLoading(false); return; }
    try {
      if (mode === "neural" || mode === "comparison") {
        const data = await loadNeuralLocomotion();
        if (generation === request.current) { setLocomotion(data.replay); setNeuralAuthority(data.authority); setRunIndex(1); }
        return;
      }
      if (mode === "locomotion") {
        const data = await loadLocomotion();
        if (generation === request.current) setLocomotion(data);
        return;
      }
      const response = await loadScenarioPlayback(ARENA_COURSE_ID);
      if (generation !== request.current) return;
      if ("error" in response) throw new Error(response.error);
      setReplay(validateArenaCourseReplay(response.result));
    } catch (cause) {
      if (generation === request.current) setError(cause instanceof Error ? displayText(cause.message) : "Canonical replay unavailable.");
    } finally { if (generation === request.current) setLoading(false); }
  }
  const scene = active ? courseScene(replay, cursor) : null;
  const motion = moving ? locomotionScene(locomotion, runIndex, time) : null;
  const overview = useMemo(() => neuralAuthority ? comparisonOverview(neuralAuthority) : null, [neuralAuthority]);
  const comparison = mode === "comparison" && moving && overview ? {overview, states: comparisonScenes(locomotion, time), time, focus: overview.tracks.find(t => t.index === runIndex)?.key} : undefined;
  const trajectory = useMemo(() => neuralAuthority && locomotion ? locomotion.result.runs[runIndex].frames.map(f => f.position) : undefined, [neuralAuthority, locomotion, runIndex]);
  const pose = motion ? motion.pose : active ? arenaCoursePose(replay, cursor) : undefined;
  const frame = scene?.frame;
  const unavailable = "Not available at this boundary";
  return <>
    <div className="arena-mode-controls" aria-label="Arena mode">
      <button aria-pressed={mode === "neural-flight"} onClick={()=>void choose("neural-flight")}>Experimental Neural Flight Steering v9</button>
      <button aria-pressed={mode === "flight-v8"} onClick={()=>void choose("flight-v8")}>Experimental 3D Flight v8</button>
      <button aria-pressed={mode === "flight-preview"} onClick={()=>void choose("flight-preview")}>Flight Visual Preview v7.1</button>
      <button aria-pressed={mode === "motor-bridge"} onClick={()=>void choose("motor-bridge")}>Motor-to-Gait Bridge v7</button>
      <button aria-pressed={mode === "static"} onClick={() => void choose("static")}>Static arena</button>
      <button aria-pressed={mode === "course"} onClick={() => void choose("course")}>Course Replay</button>
      <button aria-pressed={mode === "locomotion"} onClick={() => void choose("locomotion")}>Experimental Locomotion v0</button>
      <button aria-pressed={mode === "neural"} onClick={() => void choose("neural")}>Experimental Locomotion v1</button>
      <button aria-pressed={loadedProtocol} onClick={() => void choose("scheduler")}>Visual Protocol Scheduler</button>
      <button aria-pressed={(mode === "visual-programs" || mode === "independent" || mode === "moving" || mode === "navigation") && !loadedProtocol && loadedVisual} onClick={() => void choose("visual-programs")}>Visual Stimulus Comparison</button>
      <button aria-pressed={(mode === "moving" || mode === "navigation" || mode === "independent" || mode === "visual-programs" || mode === "scheduler") && !loadedProtocol && !loadedVisual && loadedIndependent} onClick={() => void choose("independent")}>Independent Visual Stimuli v5</button>
      <button aria-pressed={(mode === "moving" || mode === "navigation" || mode === "independent" || mode === "visual-programs" || mode === "scheduler") && !loadedProtocol && !loadedVisual && loadedMoving && !loadedIndependent} onClick={() => void choose("moving")}>Moving Visual Stimuli v4</button>
      <button aria-pressed={(mode === "moving" || mode === "navigation" || mode === "independent" || mode === "visual-programs" || mode === "scheduler") && !loadedProtocol && !loadedVisual && !loadedMoving} onClick={() => void choose("navigation")}>Continuous Arena Navigation v3</button>
      <button aria-pressed={mode === "interactive"} onClick={() => void choose("interactive")}>Interactive Neural Locomotion v2</button>
      <button aria-pressed={mode === "comparison"} onClick={() => void choose("comparison")}>Neural Steering Comparison</button>
    </div>
    {(mode === "locomotion" || mode === "neural" || mode === "comparison") && <section className="arena-replay-panel" aria-label={mode === "comparison" ? "Neural Steering Comparison" : neuralMode ? "Experimental Locomotion v1" : "Experimental Locomotion v0"}>
      <p className="arena-replay-identity">Precomputed simulation replay · {neuralMode ? "Connectome-informed neural steering + engineering propulsion" : "Engineering kinematic locomotion"}</p>
      <p className="arena-science-limit">{neuralMode ? "HS/DNp15 influences heading through an engineering conversion. Geometric landmarks, not a calibrated retina. Trails: floor projection of the Python results. Engineering propulsion; no biological gait or wall avoidance." : "Engineering propulsion in arena units. No neural steering or biological gait. It stops at the wall; it neither detects nor avoids it."}</p>
      {loading && <p role="status">Checking the Python simulation…</p>}
      {error && <p role="alert">{error} The view stays static.</p>}
      {motion && locomotion && <>
        <label htmlFor="arena-locomotion-run">{comparison ? "Fly in focus (time is kept)" : "Experimental condition"}</label>
        <select id="arena-locomotion-run" value={runIndex} onChange={event => { setRunIndex(Number(event.target.value)); if (!comparison) { setTime(0); setPlaying(false); } }}>
          {neuralAuthority ? <>{!comparison && <option value={0}>A — Engineering baseline</option>}<option value={1}>B — Neural steering on</option><option value={2}>C — Neural output off</option><option value={3}>D — Plano visual alterado</option></> : <><option value={0}>A — Engineering propulsion</option><option value={1}>B — Propulsion off (control)</option></>}
        </select>

        <label htmlFor="arena-locomotion-time">Simulated time</label>
        <input id="arena-locomotion-time" type="range" min={0} max={8} step={.02} value={time} onChange={event => { setPlaying(false); setTime(Number(event.target.value)); }} />
        <p className="arena-replay-note">Distance: {motion.distance.toFixed(3)} · Speed: {motion.speed.toFixed(2)} units/s · Contact: {motion.frame.contact ?? "none"}</p>
        {neuralAuthority && <p className="arena-replay-note" data-neural-readout={motion.frame.neural_summary?.mean_yaw_drive_eq ?? "UNAVAILABLE"} data-heading={motion.pose.rotation} data-steering-mode={motion.frame.steering_applied ? "ACTIVE" : "DISABLED"}>Heading {motion.pose.rotation.toFixed(4)} rad · Drive neural {motion.frame.neural_summary?.mean_yaw_drive_eq?.toExponential(4) ?? "unavailable"} yaw_drive_eq · {motion.frame.steering_applied ? "Steering on" : "Steering output off"} · Landmarks Z={locomotion.result.runs[runIndex].condition?.plane_z}</p>}
        {comparison && <NeuralComparisonInspector {...comparison} />}
        <details><summary>Telemetry and engineering assumptions</summary>
        <dl className="arena-course-telemetry">
          <div><dt>Position X / Y / Z (presentation units)</dt><dd>{motion.pose.anchor.map(v => v.toFixed(4)).join(" / ")}</dd></div>
          <div><dt>Distance travelled</dt><dd>{motion.distance.toFixed(4)} units</dd></div>
          <div><dt>Speed / propulsion</dt><dd>{motion.speed.toFixed(2)} / {motion.frame.propulsion_model_value.toFixed(2)} units/s</dd></div>
          <div><dt>Orientation / angular velocity</dt><dd>{motion.pose.rotation.toFixed(4)} rad / {motion.frame.angular_velocity.toFixed(5)} rad/s</dd></div>
          <div><dt>Contacto / steering neural</dt><dd>{motion.frame.contact ?? "No contact"} / {motion.frame.steering_applied ? "HS/DNp15 + engineering conversion" : "Desligado"}</dd></div>
        </dl>
        {neuralAuthority && <><p>MaleCNS v1.0 · HS R 10015/10016/10023, L 10034/10181/10419 → DNp15 R 11215 / L 12069. Proxy states, with no firing-rate or biological-speed calibration. 200 substeps of 0.1 ms per 20 ms interval; the observation of the completed movement is held constant over the next interval. The three HS cells in each hemisphere share the same input and dynamics.</p><p>Gain: 2.5 rad/orientation_eq · limit: ±0.5 rad/s. The angular contribution sums kernel increments and does not multiply dt twice. Contact stops translation; neural and heading continue. There is no wall reflex and no target controller. Receptors, gait and muscles are not modelled.</p><p>HS: {motion.frame.neural_summary?.hs_states.map(v=>v.toExponential(3)).join(" / ") ?? "not computed"}<br/>DNp15: {motion.frame.neural_summary?.dnp15_states.map(v=>v.toExponential(3)).join(" / ") ?? "not computed"}<br/>Observation R/L: {motion.frame.sensory_summary ? `${motion.frame.sensory_summary.right.toExponential(4)} / ${motion.frame.sensory_summary.left.toExponential(4)}` : "no completed interval"} · substeps: {motion.frame.neural_summary?.substeps ?? 0}</p><p className="arena-artifact-id">Policy: {neuralAuthority.config.policy_sha256} · Resultado: {neuralAuthority.result_sha256}</p></>}
        <p>Python · fixed step 0.02 s · duration 8 s · random policy NONE · {neuralAuthority ? motion.frame.model_mode : "EXPERIMENTAL_KINEMATIC_ONLY"}. Pose interpolated between boundaries; speed and contact from the previous boundary. Y fixed on the floor; conservative circular footprint. The camera does not influence the simulation.</p><p className="arena-artifact-id">Artifact: {locomotion.artifact_id}</p></details>
      </>}
    </section>}
    {mode === "course" && <section className="arena-replay-panel" aria-label="Canonical Course replay">
      <p className="arena-science-limit">Canonical replay of model orientation, shown in a laboratory view. Fixed presentation position; translation is not modelled. The camera took no part in the simulation. Collisions are not simulated.</p>
      {loading && <p role="status">Checking the canonical replay… The specimen stays in a static presentation.</p>}
      {error && <p role="alert">Replay unavailable: {error} No substitute movement was created. The view stays static.</p>}
      {frame && replay && scene && <>
        <p className="arena-replay-identity">{replay.scenario.id} · VALIDATED_CANONICAL_REPLAY</p>
        <div className="arena-replay-controls">
          <button onClick={() => { if (cursor >= last) setCursor(0); setPlaying(!isPlaying); }}>{isPlaying ? "Pausar" : "Reproduzir"}</button>
          <button onClick={() => { setPlaying(false); setCursor(0); }}>Reset Replay</button>
          <output aria-live="off" data-boundary={frame.step} data-render-yaw={scene.renderRotation}>Boundary {frame.step} / {last} · {frame.time_ms.toFixed(1)} ms{cursor >= last ? " · End of record" : ""}</output>
        </div>
        <label htmlFor="arena-course-boundary">Select scientific boundary</label>
        <input id="arena-course-boundary" type="range" min={0} max={last} step={1} value={Math.floor(cursor)} onChange={event => { const value = Number(event.target.value); if (Number.isInteger(value) && value >= 0 && value <= last) { setPlaying(false); setCursor(value); } }} />
        <p className="arena-replay-note">50 ms of scientific time shown over 6 s. Visual orientation is interpolated only between adjacent boundaries; telemetry for boundary {frame.step}, with no interpolation. One abstract cycle = one visual turn, with no amplification.</p>
        <dl className="arena-course-telemetry">
          <div><dt>Orientation · yaw_orientation_eq</dt><dd>{frame.yaw_orientation_eq.toFixed(12)}</dd></div>
          <div><dt>Drive · yaw_drive_eq (model proxy)</dt><dd>{frame.yaw_drive_eq.toExponential(6)}</dd></div>
          <div><dt>DNp15 R / L · dnp15_state_eq</dt><dd>{frame.dnp15_states.map(n => n.toExponential(6)).join(" / ")}</dd></div>
          <div><dt>Observation · horizontal_motion_eq</dt><dd>{frame.observation ? frame.observation.global_horizontal_motion_eq.toExponential(6) : unavailable}</dd></div>
          <div><dt>Incremento externo · orientation_eq</dt><dd>{frame.external_orientation_increment_eq === null ? unavailable : frame.external_orientation_increment_eq.toExponential(6)}</dd></div>
        </dl>
        <p className="arena-replay-note">Model states built on MaleCNS structural evidence. They are not calibrated biological angles or physical speeds. The specimen is a visual asset, not reconstructed MaleCNS anatomy.</p>
      </>}
    </section>}
    {mode === "neural-flight" ? <NeuralFlightArena/> : mode === "flight-v8" ? <EngineeringFlightArena/> : mode === "flight-preview" ? <FlightVisualPreview/> : mode === "motor-bridge" ? <MotorGaitBridgeArena/> : (mode === "navigation" || mode === "moving" || mode === "independent" || mode === "visual-programs" || mode === "scheduler") ? <ContinuousNavigationArena key={mode} initialMoving={mode === "moving" || mode === "independent" || mode === "visual-programs" || mode === "scheduler"} initialIndependent={mode === "independent" || mode === "visual-programs" || mode === "scheduler"} initialVisualComparison={mode === "visual-programs"} initialProtocol={mode === "scheduler"} onProtocolLoaded={setLoadedProtocol} onVersionLoaded={(m,i,v)=>{setLoadedMoving(m);setLoadedIndependent(i);setLoadedVisual(v);setLoadedProtocol(false);}}/> : mode === "interactive" ? <InteractiveNeuralArena/> : <FlyViewer arena replayPose={pose} locomotion={Boolean(motion)} locomotionVersion={neuralAuthority ? "v1" : "v0"} trajectory={comparison ? undefined : trajectory} comparison={comparison} stimulusPlane={neuralAuthority && !comparison ? locomotion?.result.runs[runIndex].condition?.plane_z : undefined} playbackControls={motion ? <div className="arena-replay-controls">
          <button onClick={() => { if (time >= 8) setTime(0); setPlaying(!motionPlaying); }}>{motionPlaying ? "Pause" : "Play"}</button>
          <button onClick={() => { setPlaying(false); setTime(0); }}>Reset Experiment</button>
          <output data-simulation-time={time} data-world-position={JSON.stringify(motion.pose.anchor)} data-contact={motion.frame.contact ?? "NONE"} data-render-heading={motion.pose.rotation}>{time.toFixed(2)} / 8.00 s{time >= 8 ? " · End of simulation" : ""}</output>
        </div> : undefined} />}
  </>;
}
