"use client";

import Link from "next/link";
import { useState, type ReactNode } from "react";
import type { NavigationSnapshot } from "@/lib/continuousArenaNavigation";
import type { LiveSample, LiveStatus } from "@/lib/liveGroundSession";
import { neuralActivityTrace } from "@/lib/neuralActivityTrace";
import type { ExplorationMode } from "@/lib/engineeringExploration";
import { neuralActivityViewSnapshot, type NeuralActivityTrace, type NeuralActivityViewSnapshot } from "@/lib/neuralMorphologyExplorer";
import { NeuralActivityExplorer3D } from "@/components/NeuralActivityExplorer3D";

export function explorationStatus(state: NavigationSnapshot | null, playing: boolean, error: string | null) {
  return error ? "Unavailable" : !state ? "Preparing" : state.step === 1500 ? "Exploration complete" : playing ? "Exploring" : state.step ? "Paused" : "Ready to explore";
}

export function ExploreLabView({ state, playing, error, notice, neuralEnabled, onPlay, onReset, onNeuralChange, onExport, onReplay, lagging, liveStatus, latestSample, onStop, sessionId, mode, onModeChange, children }: {
  state: NavigationSnapshot | null; playing: boolean; error: string | null; notice: string;
  neuralEnabled: boolean; onPlay: () => void; onReset: () => void; onNeuralChange: (enabled: boolean) => void;
  onExport?: () => void; onReplay?: () => void; lagging: boolean; children?: ReactNode;
  liveStatus?: LiveStatus; latestSample?: LiveSample | null; onStop?: () => void; sessionId?: string | null;
  mode?: ExplorationMode; onModeChange?: (mode: ExplorationMode) => void;
}) {
  const [neuralExplorerOpen, setNeuralExplorerOpen] = useState(false);
  const complete = !liveStatus && state?.step === 1500;
  const status = error ? "Unavailable" : !state ? "Preparing" : liveStatus ? ({ready:"Ready to explore",running:"Exploring",paused:"Paused",stopped:"Stopped",error:"Unavailable"} as const)[liveStatus] : explorationStatus(state, playing, error);
  const seconds = Math.floor(state?.time ?? 0);
  const liveTime = `${String(Math.floor(seconds / 3600)).padStart(2, "0")}:${String(Math.floor(seconds / 60) % 60).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
  let trace: NeuralActivityTrace | null = null;
  let traceError: string | null = null;
  if (liveStatus && latestSample) {
    try {
      trace = neuralActivityTrace(latestSample);
    } catch (cause) {
      traceError = cause instanceof Error ? cause.message : "Neural interval telemetry is invalid";
    }
  }
  let activitySnapshot: NeuralActivityViewSnapshot | null = null;
  let activityError: string | null = traceError;
  if (trace && sessionId) {
    try {
      activitySnapshot = neuralActivityViewSnapshot(sessionId, trace);
    } catch (cause) {
      activityError = cause instanceof Error ? cause.message : "Live neural activity could not be validated";
    }
  } else if (trace) {
    activityError = "Live session identity is unavailable";
  }
  return <div className="lab-experience" data-lab-state={status}>
    <div className="lab-activity"><div><span className="lab-eyebrow">The living question</span><h1>Explore<span>.</span></h1><p>A small organism. A world to move through.</p></div><span className={`lab-status${playing ? " is-running" : ""}`} role="status"><i aria-hidden="true" />{status}</span></div>
    <div className="lab-workspace">
      <div className="lab-view-area">
        {children}
        <div className="lab-controls" aria-label="Exploration controls">
          <button className="lab-play" disabled={!state || Boolean(error) || liveStatus === "stopped"} onClick={onPlay}><span aria-hidden="true">{playing ? "Ⅱ" : "▶"}</span>{playing ? "Pause" : complete ? "Explore again" : state?.step ? "Resume" : "Play"}</button>
          {liveStatus ? <button disabled={!state || liveStatus === "stopped" || liveStatus === "error"} onClick={onStop}>Stop</button> : null}
          <button disabled={!state} onClick={onReset}>Reset</button>
          <div className="lab-time"><output aria-label="Exploration time" aria-live="off" data-live-time={state?.time ?? 0}>{liveStatus ? liveTime : `00:${String(seconds).padStart(2, "0")} / 00:30`}</output><span>Time in the model</span></div>
          <span className="lab-neural-state">Neural influence <strong>{neuralEnabled ? "On" : "Off"}</strong></span>
        </div>
        {liveStatus ? <p className="lab-live-window">Trajectory shows recent history only.</p> : null}
        {error ? <p className="lab-error" role="alert">{error} The simulation is stopped. No substitute movement is generated.</p> : null}
        {liveStatus && notice ? <p className="lab-feedback" role="status">{notice}</p> : null}
        {complete ? <p className="lab-completion" role="status">Exploration complete. Inspect the scene, or explore again from the beginning.</p> : null}
        <div className="lab-performance-slot">{lagging ? <span className="lab-performance" role="status" title="The fixed simulation timestep remains unchanged. The timer shows simulation time, not wall-clock time."><span aria-hidden="true">◷</span> Simulation slower than real time</span> : null}</div>
        <details className="lab-neural-details" onToggle={(event) => setNeuralExplorerOpen(event.currentTarget.open)}>
          <summary>Inspect verified neural anatomy · 3D <span aria-hidden="true">⌄</span></summary>
          <div className="lab-neural-details-content">
            {neuralExplorerOpen ? <NeuralActivityExplorer3D snapshot={activitySnapshot} activityError={activityError} /> : null}
          </div>
        </details>
      </div>
      <aside className="lab-sidebar" aria-label="Exploration settings and information">
        <div className="lab-introduction"><span className="lab-eyebrow">Your laboratory</span><p>Explore movement.<br />Look closer whenever you like.</p></div>
        {liveStatus && mode && onModeChange ? <details className="lab-settings" open><summary>Locomotion mode <span aria-hidden="true">⌄</span></summary><div className="lab-panel-content"><label className="lab-mode-select"><span>Controller</span><select aria-label="Locomotion mode" value={mode} disabled={!state || Boolean(error) || liveStatus === "running" || liveStatus === "paused"} onChange={e => onModeChange(e.target.value as ExplorationMode)}><option value="baseline_v10_5b">Baseline · v10.5b</option><option value="engineering_exploration_v1">Engineering exploration · v1</option></select></label><p>{mode === "baseline_v10_5b" ? "Constant engineering propulsion at 0.18 arena units/s, with the existing modeled neural yaw and boundary response." : "Speed decreases deterministically as geometric forward clearance falls; neural yaw and boundary response remain unchanged."}</p><p className="lab-setting-note">Choose before starting. Changing the mode starts a new session from the initial pose.</p></div></details> : null}
        <details className="lab-settings"><summary>Settings <span aria-hidden="true">+</span></summary><div className="lab-panel-content"><label className="lab-toggle"><span>Neural influence</span><input type="checkbox" checked={neuralEnabled} disabled={!state || Boolean(error)} onChange={e => onNeuralChange(e.target.checked)} /></label><p>Allow the selected neural model to influence the fly’s direction. Engineering propulsion and boundary response remain active.</p><p className="lab-setting-note">Changing this starts a new exploration from the initial state.</p></div></details>
        {liveStatus ? <details><summary>Why did it turn?</summary><div className="lab-panel-content">{trace ? <><p>Interval {trace.tick} → {trace.accepted_tick} ({trace.time_s.toFixed(2)} s). Modelled neural yaw contribution: {trace.neural_yaw_rad_s.toFixed(4)} rad/s; engineering boundary yaw: {trace.boundary_yaw_rad_s.toFixed(4)} rad/s; resulting angular velocity: {trace.angular_velocity_rad_s.toFixed(4)} rad/s.</p><p>Engineering state: <strong>{trace.engineering.behavior_state.replaceAll("_", " ")}</strong>. Forward clearance {trace.engineering.forward_clearance_units.toFixed(3)} arena units; commanded speed {trace.engineering.commanded_speed_units_s.toFixed(3)} units/s; accepted movement {trace.engineering.accepted_speed_units_s.toFixed(3)} units/s{trace.engineering.contact ? ` · ${trace.engineering.contact}` : ""}.</p><p>HS and DNp15 model-space states at interval start (not calibrated fluorescence): {trace.states.map(s => `${s.model} ${s.id}: ${s.value.toFixed(4)}`).join(' · ')}.</p><p>MaleCNS-derived authority supplies structural connectivity. HS/DNp15 values are computed model states; neural yaw is an engineering motor projection. Speed modulation and boundary recovery are engineering rules, not neural decisions.</p></> : <p>{traceError ? `Neural interval telemetry is unavailable: ${traceError}. No substitute activity is displayed.` : "Start the session to inspect an accepted interval."}</p>}</div></details> : null}
        <details className="lab-details"><summary>Simulation details <span aria-hidden="true">+</span></summary><div className="lab-panel-content">
          {lagging ? <p className="lab-performance-detail">Simulation running slower than real time. The fixed simulation timestep remains unchanged. The timer shows simulation time, not wall-clock time.</p> : null}
          <p>Connectome-informed steering, engineering movement and leg animation. This is a computational model, not physiologically calibrated fly behaviour.</p>
          {state ? <dl className="lab-telemetry" data-live-step={state.step} data-live-position={JSON.stringify(state.position)} data-live-heading={state.heading} data-live-neural={JSON.stringify({hs:state.hs,dn:state.dn})} data-live-substeps={state.substeps}>
            <div><dt>Position X / Y / Z</dt><dd>{state.position.map(n => n.toFixed(4)).join(" / ")}</dd></div><div><dt>Heading</dt><dd>{state.heading.toFixed(4)} rad</dd></div><div><dt>Neural turn</dt><dd>{state.neuralOmega.toFixed(4)} rad/s</dd></div><div><dt>Boundary response</dt><dd>{state.boundaryOmega.toFixed(4)} rad/s</dd></div><div><dt>Contacts / recoveries</dt><dd>{state.contacts} / {state.recoveries}</dd></div><div><dt>Model</dt><dd>Continuous Arena Navigation v3 · 20 ms body intervals · 200 neural substeps{liveStatus ? " · live session" : " · 30 seconds"}</dd></div>
            {liveStatus && latestSample ? <><div><dt>Interval start / accepted tick</dt><dd>{latestSample.interval.step} / {latestSample.accepted.step}</dd></div><div><dt>Interval velocity X / Y / Z</dt><dd>{latestSample.interval.linear_velocity.map(n => n.toFixed(4)).join(" / ")}</dd></div><div><dt>Sensory input R / L</dt><dd>{latestSample.interval.sensory_summary ? `${latestSample.interval.sensory_summary.right.toFixed(4)} / ${latestSample.interval.sensory_summary.left.toFixed(4)}` : "Initial observation"}</dd></div><div><dt>HS / DNp15 at accepted boundary</dt><dd>{state.hs.map(n => n.toFixed(3)).join(" / ")} · {state.dn.map(n => n.toFixed(3)).join(" / ")}</dd></div></> : null}
          </dl> : null}
          {liveStatus ? <p>Trajectory and telemetry show a rolling window. Complete live-session recording and export are not available.</p> : <div className="lab-detail-actions"><button disabled={!state || playing || Boolean(error)} onClick={onExport}>Export session</button><button disabled={!state || playing || Boolean(error)} onClick={onReplay}>Verify replay</button></div>}
          {!liveStatus && notice ? <p className="lab-feedback" role="status">{notice}</p> : null}
          <Link prefetch={false} href="/scenarios">Research archive ↗</Link><Link prefetch={false} href="/visual-lab/arena/research">Laboratory research tools ↗</Link>
        </div></details>

      </aside>
    </div>
  </div>;
}
