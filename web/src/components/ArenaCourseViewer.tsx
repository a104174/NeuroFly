"use client";

import { useEffect, useRef, useState } from "react";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { advanceScenarioCursor } from "@/lib/scenarioPlayback";
import { courseScene, type CoursePlaybackResult } from "@/lib/courseControlPlayback";
import { ARENA_COURSE_ID, arenaCoursePose, validateArenaCourseReplay } from "@/lib/arenaCourseReplay";
import { FlyViewer } from "./FlyViewer";

export function ArenaCourseViewer() {
  const [mode, setMode] = useState<"static" | "course">("static");
  const [replay, setReplay] = useState<CoursePlaybackResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(false);
  const request = useRef(0);
  useEffect(() => () => { request.current++; }, []);
  const active = mode === "course" && replay !== null && !error;
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

  async function choose(mode: "static" | "course") {
    const generation = ++request.current;
    setMode(mode); setPlaying(false); setCursor(0); setReplay(null); setError(null); setLoading(mode === "course");
    if (mode === "static") return;
    try {
      const response = await loadScenarioPlayback(ARENA_COURSE_ID);
      if (generation !== request.current) return;
      if ("error" in response) throw new Error(response.error);
      setReplay(validateArenaCourseReplay(response.result));
    } catch (cause) {
      if (generation === request.current) setError(cause instanceof Error ? cause.message : "Replay canónico indisponível.");
    } finally { if (generation === request.current) setLoading(false); }
  }
  const scene = active ? courseScene(replay, cursor) : null;
  const pose = active ? arenaCoursePose(replay, cursor) : undefined;
  const frame = scene?.frame;
  const unavailable = "Não disponível neste boundary";
  return <>
    <div className="arena-mode-controls" aria-label="Modo da arena">
      <button aria-pressed={mode === "static"} onClick={() => void choose("static")}>Arena estática</button>
      <button aria-pressed={mode === "course"} onClick={() => void choose("course")}>Course Replay</button>
    </div>
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
    <FlyViewer arena replayPose={pose} />
  </>;
}
