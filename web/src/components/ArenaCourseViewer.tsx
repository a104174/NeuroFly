"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { advanceScenarioCursor } from "@/lib/scenarioPlayback";
import { courseScene, type CoursePlaybackResult } from "@/lib/courseControlPlayback";
import { ARENA_COURSE_ID, arenaCoursePose, validateArenaCourseReplay } from "@/lib/arenaCourseReplay";
import { advanceLocomotion, loadLocomotion, locomotionScene, type LocomotionReplay } from "@/lib/experimentalLocomotion";
import { loadNeuralLocomotion, type NeuralArtifact } from "@/lib/neuralLocomotion";
import { comparisonOverview, comparisonScenes } from "@/lib/neuralSteeringComparison";
import { NeuralComparisonInspector } from "./NeuralComparisonInspector";
import { FlyViewer } from "./FlyViewer";

export function ArenaCourseViewer() {
  const [mode, setMode] = useState<"static" | "course" | "locomotion" | "neural" | "comparison">("static");
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

  async function choose(mode: "static" | "course" | "locomotion" | "neural" | "comparison") {
    const generation = ++request.current;
    setMode(mode); setTime(0); setNeuralAuthority(null); setLocomotion(null); setRunIndex(0); setPlaying(false); setCursor(0); setReplay(null); setError(null); setLoading(mode !== "static");
    if (mode === "static") return;
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
      if (generation === request.current) setError(cause instanceof Error ? cause.message : "Replay canónico indisponível.");
    } finally { if (generation === request.current) setLoading(false); }
  }
  const scene = active ? courseScene(replay, cursor) : null;
  const motion = moving ? locomotionScene(locomotion, runIndex, time) : null;
  const overview = useMemo(() => neuralAuthority ? comparisonOverview(neuralAuthority) : null, [neuralAuthority]);
  const comparison = mode === "comparison" && moving && overview ? {overview, states: comparisonScenes(locomotion, time), time, focus: overview.tracks.find(t => t.index === runIndex)?.key} : undefined;
  const trajectory = useMemo(() => neuralAuthority && locomotion ? locomotion.result.runs[runIndex].frames.map(f => f.position) : undefined, [neuralAuthority, locomotion, runIndex]);
  const pose = motion ? motion.pose : active ? arenaCoursePose(replay, cursor) : undefined;
  const frame = scene?.frame;
  const unavailable = "Não disponível neste boundary";
  return <>
    <div className="arena-mode-controls" aria-label="Modo da arena">
      <button aria-pressed={mode === "static"} onClick={() => void choose("static")}>Arena estática</button>
      <button aria-pressed={mode === "course"} onClick={() => void choose("course")}>Course Replay</button>
      <button aria-pressed={mode === "locomotion"} onClick={() => void choose("locomotion")}>Experimental Locomotion v0</button>
      <button aria-pressed={mode === "neural"} onClick={() => void choose("neural")}>Experimental Locomotion v1</button>
      <button aria-pressed={mode === "comparison"} onClick={() => void choose("comparison")}>Neural Steering Comparison</button>
    </div>
    {(mode === "locomotion" || mode === "neural" || mode === "comparison") && <section className="arena-replay-panel" aria-label={mode === "comparison" ? "Neural Steering Comparison" : neuralMode ? "Experimental Locomotion v1" : "Experimental Locomotion v0"}>
      <p className="arena-replay-identity">Precomputed simulation replay · {neuralMode ? "Connectome-informed neural steering + engineering propulsion" : "Engineering kinematic locomotion"}</p>
      <p className="arena-science-limit">{neuralMode ? "HS/DNp15 influencia o heading através de uma conversão de engenharia. Landmarks geométricos, não uma retina calibrada. Trilhos: projeção no piso dos resultados Python. Propulsão de engenharia; sem gait biológico ou wall avoidance." : "Propulsão de engenharia em unidades da arena. Sem steering neural ou gait biológico. Pára na parede; não a deteta nem evita."}</p>
      {loading && <p role="status">A verificar a simulação Python…</p>}
      {error && <p role="alert">{error} A vista permanece estática.</p>}
      {motion && locomotion && <>
        <label htmlFor="arena-locomotion-run">{comparison ? "Fly em foco (mantém o tempo)" : "Condição experimental"}</label>
        <select id="arena-locomotion-run" value={runIndex} onChange={event => { setRunIndex(Number(event.target.value)); if (!comparison) { setTime(0); setPlaying(false); } }}>
          {neuralAuthority ? <>{!comparison && <option value={0}>A — Baseline de engenharia</option>}<option value={1}>B — Steering neural ativo</option><option value={2}>C — Saída neural desligada</option><option value={3}>D — Plano visual alterado</option></> : <><option value={0}>A — Propulsão de engenharia</option><option value={1}>B — Propulsão desligada (controlo)</option></>}
        </select>

        <label htmlFor="arena-locomotion-time">Tempo simulado</label>
        <input id="arena-locomotion-time" type="range" min={0} max={8} step={.02} value={time} onChange={event => { setPlaying(false); setTime(Number(event.target.value)); }} />
        <p className="arena-replay-note">Distância: {motion.distance.toFixed(3)} · Velocidade: {motion.speed.toFixed(2)} unidades/s · Contacto: {motion.frame.contact ?? "nenhum"}</p>
        {neuralAuthority && <p className="arena-replay-note" data-neural-readout={motion.frame.neural_summary?.mean_yaw_drive_eq ?? "UNAVAILABLE"} data-heading={motion.pose.rotation} data-steering-mode={motion.frame.steering_applied ? "ACTIVE" : "DISABLED"}>Heading {motion.pose.rotation.toFixed(4)} rad · Drive neural {motion.frame.neural_summary?.mean_yaw_drive_eq?.toExponential(4) ?? "indisponível"} yaw_drive_eq · {motion.frame.steering_applied ? "Steering ativo" : "Saída para steering desligada"} · Landmarks Z={locomotion.result.runs[runIndex].condition?.plane_z}</p>}
        {comparison && <NeuralComparisonInspector {...comparison} />}
        <details><summary>Telemetria e pressupostos de engenharia</summary>
        <dl className="arena-course-telemetry">
          <div><dt>Posição X / Y / Z (unidades de apresentação)</dt><dd>{motion.pose.anchor.map(v => v.toFixed(4)).join(" / ")}</dd></div>
          <div><dt>Distância percorrida</dt><dd>{motion.distance.toFixed(4)} unidades</dd></div>
          <div><dt>Velocidade / propulsão</dt><dd>{motion.speed.toFixed(2)} / {motion.frame.propulsion_model_value.toFixed(2)} unidades/s</dd></div>
          <div><dt>Orientação / velocidade angular</dt><dd>{motion.pose.rotation.toFixed(4)} rad / {motion.frame.angular_velocity.toFixed(5)} rad/s</dd></div>
          <div><dt>Contacto / steering neural</dt><dd>{motion.frame.contact ?? "Sem contacto"} / {motion.frame.steering_applied ? "HS/DNp15 + conversão de engenharia" : "Desligado"}</dd></div>
        </dl>
        {neuralAuthority && <><p>MaleCNS v1.0 · HS R 10015/10016/10023, L 10034/10181/10419 → DNp15 R 11215 / L 12069. Estados proxy, sem calibração de firing rate ou velocidade biológica. 200 substeps de 0.1 ms por intervalo de 20 ms; observação do movimento já concluído, mantida constante no intervalo seguinte. Os três HS de cada hemisfério partilham o mesmo input/dinâmica.</p><p>Ganho: 2.5 rad/orientation_eq · limite: ±0.5 rad/s. A contribuição angular soma incrementos do kernel, não multiplica dt duas vezes. Contacto trava translação; neural/heading continuam. Não há reflexo de parede nem controlador de targets. Receptores, gait e músculos não modelados.</p><p>HS: {motion.frame.neural_summary?.hs_states.map(v=>v.toExponential(3)).join(" / ") ?? "não calculado"}<br/>DNp15: {motion.frame.neural_summary?.dnp15_states.map(v=>v.toExponential(3)).join(" / ") ?? "não calculado"}<br/>Observação R/L: {motion.frame.sensory_summary ? `${motion.frame.sensory_summary.right.toExponential(4)} / ${motion.frame.sensory_summary.left.toExponential(4)}` : "nenhum intervalo concluído"} · substeps: {motion.frame.neural_summary?.substeps ?? 0}</p><p className="arena-artifact-id">Policy: {neuralAuthority.config.policy_sha256} · Resultado: {neuralAuthority.result_sha256}</p></>}
        <p>Python · passo fixo 0.02 s · duração 8 s · random policy NONE · {neuralAuthority ? motion.frame.model_mode : "EXPERIMENTAL_KINEMATIC_ONLY"}. Pose interpolada entre boundaries; velocidade/contacto do boundary anterior. Y fixo sobre o piso; footprint circular conservador. A câmara não influencia a simulação.</p><p className="arena-artifact-id">Artifact: {locomotion.artifact_id}</p></details>
      </>}
    </section>}
    {mode === "course" && <section className="arena-replay-panel" aria-label="Replay canónico Course">
      <p className="arena-science-limit">Replay canónico de orientação de modelo, apresentado numa visualização laboratorial. Posição fixa de apresentação; translação não modelada. A câmara não participou na simulação. Não são simuladas colisões.</p>
      {loading && <p role="status">A validar o replay canónico… O espécime permanece numa apresentação estática.</p>}
      {error && <p role="alert">Replay indisponível: {error} Não foi criado movimento de substituição. A vista permanece estática.</p>}
      {frame && replay && scene && <>
        <p className="arena-replay-identity">{replay.scenario.id} · VALIDATED_CANONICAL_REPLAY</p>
        <div className="arena-replay-controls">
          <button onClick={() => { if (cursor >= last) setCursor(0); setPlaying(!isPlaying); }}>{isPlaying ? "Pausar" : "Reproduzir"}</button>
          <button onClick={() => { setPlaying(false); setCursor(0); }}>Reset Replay</button>
          <output aria-live="off" data-boundary={frame.step} data-render-yaw={scene.renderRotation}>Boundary {frame.step} / {last} · {frame.time_ms.toFixed(1)} ms{cursor >= last ? " · Fim do registo" : ""}</output>
        </div>
        <label htmlFor="arena-course-boundary">Selecionar boundary científico</label>
        <input id="arena-course-boundary" type="range" min={0} max={last} step={1} value={Math.floor(cursor)} onChange={event => { const value = Number(event.target.value); if (Number.isInteger(value) && value >= 0 && value <= last) { setPlaying(false); setCursor(value); } }} />
        <p className="arena-replay-note">50 ms científicos apresentados em 6 s. Orientação visual interpolada apenas entre boundaries adjacentes; telemetria do boundary {frame.step}, sem interpolação. Um ciclo abstrato = uma volta visual, sem amplificação.</p>
        <dl className="arena-course-telemetry">
          <div><dt>Orientação · yaw_orientation_eq</dt><dd>{frame.yaw_orientation_eq.toFixed(12)}</dd></div>
          <div><dt>Drive · yaw_drive_eq (proxy de modelo)</dt><dd>{frame.yaw_drive_eq.toExponential(6)}</dd></div>
          <div><dt>DNp15 R / L · dnp15_state_eq</dt><dd>{frame.dnp15_states.map(n => n.toExponential(6)).join(" / ")}</dd></div>
          <div><dt>Observação · horizontal_motion_eq</dt><dd>{frame.observation ? frame.observation.global_horizontal_motion_eq.toExponential(6) : unavailable}</dd></div>
          <div><dt>Incremento externo · orientation_eq</dt><dd>{frame.external_orientation_increment_eq === null ? unavailable : frame.external_orientation_increment_eq.toExponential(6)}</dd></div>
        </dl>
        <p className="arena-replay-note">Estados de modelo sobre evidência estrutural MaleCNS; não são ângulos biológicos calibrados nem velocidades físicas. O espécime é um asset visual, não anatomia MaleCNS reconstruída.</p>
      </>}
    </section>}
    <FlyViewer arena replayPose={pose} locomotion={Boolean(motion)} locomotionVersion={neuralAuthority ? "v1" : "v0"} trajectory={comparison ? undefined : trajectory} comparison={comparison} stimulusPlane={neuralAuthority && !comparison ? locomotion?.result.runs[runIndex].condition?.plane_z : undefined} playbackControls={motion ? <div className="arena-replay-controls">
          <button onClick={() => { if (time >= 8) setTime(0); setPlaying(!motionPlaying); }}>{motionPlaying ? "Pause" : "Play"}</button>
          <button onClick={() => { setPlaying(false); setTime(0); }}>Reset Experiment</button>
          <output data-simulation-time={time} data-world-position={JSON.stringify(motion.pose.anchor)} data-contact={motion.frame.contact ?? "NONE"} data-render-heading={motion.pose.rotation}>{time.toFixed(2)} / 8.00 s{time >= 8 ? " · Fim da simulação" : ""}</output>
        </div> : undefined} />
  </>;
}
