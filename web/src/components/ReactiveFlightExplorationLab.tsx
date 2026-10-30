"use client";

import { useEffect, useRef, useState, useMemo, type ReactNode } from 'react';
import { FlyViewer } from './FlyViewer';
import { FlightClock, FLIGHT_MODEL, flightScene } from '@/lib/engineeringFlight';
import { MixedGroundFlightSession, SUSTAINED_MIXED_PROTOCOL, LANDING_RECOVERY_PROTOCOL } from '@/lib/mixedGroundFlight';
import type { NeuralArtifact } from '@/lib/neuralLocomotion';
import { gaitHistory } from '@/lib/articulatedGait';
import { TouchAndGoSession, TOUCH_AND_GO_CONFIG } from '@/lib/flightTouchAndGo';
import { flightWingsV8 } from '@/lib/flightWingsV8';
import {
  REACTIVE_FLIGHT_CONFIG, ReactiveFlightExplorationSession,
  type ReactiveFlightStatus,
} from '@/lib/reactiveFlightExploration';

const statusText: Record<ReactiveFlightStatus, string> = {
  ready: 'Grounded · ready', running: 'Exploring chamber boundaries', paused: 'Paused',
  completed: 'Finite trial complete', failed: 'Exploration stopped on error',
};

export type ReactiveFlightBehavior = 'continuous' | 'touch-and-go' | 'mixed' | 'sustained' | 'landing-recovery';
export function createReactiveFlightLabSession(behavior: ReactiveFlightBehavior, authority?: NeuralArtifact | null) {
  if (behavior === 'mixed' || behavior === 'sustained' || behavior === 'landing-recovery') {
    if (!authority) throw new Error('Ground runtime authority unavailable');
    return new MixedGroundFlightSession(authority, behavior !== 'mixed', behavior === 'landing-recovery' ? 0 : undefined, behavior === 'landing-recovery');
  }
  return behavior === 'touch-and-go' ? new TouchAndGoSession() : new ReactiveFlightExplorationSession();
}
export function ReactiveFlightExplorationLab({ modeControl, authority, authorityError }: { modeControl: ReactNode; authority?: NeuralArtifact | null; authorityError?: string | null }) {
  const [behavior, setBehavior] = useState<ReactiveFlightBehavior>('continuous');
  const controls = <>{modeControl}<div className="lab-simulation-mode" role="group" aria-label="Reactive flight behavior">
    <button type="button" aria-pressed={behavior === 'continuous'} onClick={() => setBehavior('continuous')}>Continuous exploration</button>
    <button type="button" aria-pressed={behavior === 'touch-and-go'} onClick={() => setBehavior('touch-and-go')}>Landing and re-takeoff</button>
    <button type="button" aria-pressed={behavior === 'mixed'} onClick={() => setBehavior('mixed')}>Flight + ground exploration</button>
    <button type="button" aria-pressed={behavior === 'sustained'} onClick={() => setBehavior('sustained')}>Sustained flight + ground exploration</button>
    <button type="button" aria-pressed={behavior === 'landing-recovery'} onClick={() => setBehavior('landing-recovery')}>Mixed exploration — landing recovery</button>
  </div></>;
  if ((behavior === 'mixed' || behavior === 'sustained' || behavior === 'landing-recovery') && !authority) return <section>{controls}<p role={authorityError ? 'alert' : 'status'}>{authorityError ?? 'Loading validated ground runtime…'}</p></section>;
  return <ReactiveFlightSessionLab key={behavior} behavior={behavior} authority={authority} modeControl={controls}/>;
}
export function ReactiveFlightSessionLab({ modeControl, behavior, authority }: { modeControl: ReactNode; behavior: ReactiveFlightBehavior; authority?: NeuralArtifact | null }) {
  const [session, setSession] = useState(() => createReactiveFlightLabSession(behavior, authority));
  const clock = useRef(new FlightClock());
  const [frame, setFrame] = useState(() => session.snapshot());
  const [metrics, setMetrics] = useState(() => session.metrics());
  const [latestInterval, setLatestInterval] = useState(() => session.latestInterval());
  const [status, setStatus] = useState<ReactiveFlightStatus>('ready');
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!playing) return;
    let raf = 0, previous: number | null = null;
    const tick = (now: number) => {
      if (session.status !== 'running') return;
      if (document.hidden) {
        session.pause(); clock.current.reset(); setPlaying(false); setStatus(session.status); return;
      }
      if (previous !== null) {
        try {
          const result = clock.current.advance(session, now - previous);
          if (result.steps) {
            const accepted = session.snapshot();
            setFrame(accepted);
            setLatestInterval(session.latestInterval());
            if (accepted.step % 10 < result.steps || session.status !== 'running') setMetrics(session.metrics());
          }
          const nextStatus = session.status as ReactiveFlightStatus;
          if (nextStatus === 'completed' || nextStatus === 'failed') {
            setStatus(nextStatus); setError(session.error); setPlaying(false); clock.current.reset(); return;
          }
        } catch (cause) {
          setFrame(session.snapshot()); setLatestInterval(session.latestInterval()); setMetrics(session.metrics());
          setStatus(session.status); setError(cause instanceof Error ? cause.message : String(cause));
          setPlaying(false); clock.current.reset(); return;
        }
      }
      previous = now; raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, session]);

  useEffect(() => {
    const onVisibility = () => {
      if (document.hidden && session.status === 'running') {
        session.pause(); clock.current.reset(); setPlaying(false); setStatus(session.status);
      }
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, [session]);

  function start() {
    if (document.hidden) return;
    try { session.start(); clock.current.reset(); setError(null); setStatus(session.status); setPlaying(true); }
    catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); }
  }

  function pause() {
    session.pause(); clock.current.reset(); setPlaying(false); setStatus(session.status);
  }

  function reset() {
    clock.current.reset(); setPlaying(false);
    const next = createReactiveFlightLabSession(behavior, authority); setSession(next);
    setFrame(next.snapshot()); setMetrics(next.metrics()); setLatestInterval(next.latestInterval());
    setStatus('ready'); setError(null);
  }

  const touchAndGo = behavior === 'touch-and-go';
  const sustained = behavior === 'sustained' || behavior === 'landing-recovery';
  const controller = behavior === 'landing-recovery' ? {id:LANDING_RECOVERY_PROTOCOL.schema,version:LANDING_RECOVERY_PROTOCOL.version} : sustained ? {id:SUSTAINED_MIXED_PROTOCOL.schema,version:SUSTAINED_MIXED_PROTOCOL.version} : behavior === 'mixed' ? {id:'mixed_ground_flight_v1',version:1} : touchAndGo ? TOUCH_AND_GO_CONFIG.controller : REACTIVE_FLIGHT_CONFIG.controller;
  const mixed = behavior === 'mixed' || sustained;
  const gait = useMemo(() => session instanceof MixedGroundFlightSession ? gaitHistory(session.presentationBodySamples(frame)).at(-1) : undefined, [session, frame]);
  useEffect(() => () => { if (session instanceof MixedGroundFlightSession) session.dispose(); }, [session]);
  const altitude = frame.position[1] - REACTIVE_FLIGHT_CONFIG.environment.bounds.min[1];
  const wings = flightWingsV8(frame.time, frame.state, Math.max(0, altitude), REACTIVE_FLIGHT_CONFIG.wing_presentation.preset);
  const clearance = latestInterval?.observation;
  const bodyPose = flightScene(frame);

  return <section className="lab-experience" data-lab-mode="reactive-flight" data-flight-behavior={behavior} data-flight-status={status}>
    <div className="lab-activity"><div><span className="lab-eyebrow">Engineering state feedback</span><h1>Flight exploration<span>.</span></h1><p>{mixed ? 'Engineering flight with neural-influenced walking; fresh ground neural episodes are explicitly initialized.' : touchAndGo ? 'Engineering landing and re-takeoff from accepted body state. Walking is not integrated.' : 'Current-state wall response and altitude stabilization inside the existing chamber.'}</p></div><span className={`lab-status${playing ? ' is-running' : ''}`} role="status"><i aria-hidden="true" />{statusText[status]}</span></div>
    <div className="lab-workspace">
      <div className="lab-view-area">
        <FlyViewer experience initialGait={mixed} liveGaitState={gait} arena replayPose={bodyPose} flightPresentation={wings}
          presentationLabel="Engineering reactive flight · fixed 20 ms plant intervals"
          flightDisclosure={mixed ? "Engineering flight and behavioral transitions; existing neural-influenced planar ground locomotion starts a fresh zero-state HS/DNp15 episode after landing. No continuous neural flight state or biological autonomy is claimed. Wing motion produces no lift." : "Landing and re-takeoff, when selected, are engineering controller decisions. Walking is not integrated; biological autonomy is not established. Engineering state-feedback exploration. Bounded geometric chamber clearances influence motor commands; they are not biological sensory recordings or validated Drosophila vision. The body plant controls accepted motion. Wing articulation is visual only and does not generate lift."}
          playbackControls={<div className="lab-controls" aria-label="Reactive flight controls">
            <button className="lab-play" disabled={playing || status === 'completed' || status === 'failed'} onClick={start}>{status === 'paused' ? 'Resume' : 'Start takeoff'}</button>
            <button disabled={!playing} onClick={pause}>Pause</button>
            <button onClick={reset}>Reset</button>
            <div className="lab-time"><output aria-label="Accepted flight time" aria-live="off">{frame.time.toFixed(2)} s</output><span>Accepted model time · maximum {sustained ? 60 : REACTIVE_FLIGHT_CONFIG.maximum_duration_s} s</span></div>
          </div>}/>
        <p className="lab-live-window" data-flight-step={frame.step} data-flight-position={JSON.stringify(frame.position)} data-flight-velocity={JSON.stringify(frame.velocity)}>
          Accepted state {frame.step} · {frame.state} · X/Y/Z {frame.position.map(value => value.toFixed(4)).join(' / ')} · velocity {frame.velocity.map(value => value.toFixed(4)).join(' / ')} units/s
        </p>
        {error ? <p className="lab-error" role="alert">{error} The controller stopped at the last accepted body state.</p> : null}
        {status === 'completed' ? <p className="lab-completion" role="status">{sustained ? 'Finite sustained window complete; inspect recorded episode counts and final plant state.' : mixed ? 'Walking and flight handoffs verified; second airborne exploration accepted.' : touchAndGo ? 'Landing and re-takeoff verified; second airborne exploration accepted.' : 'Finite 30-second verification window complete. This duration limit does not represent a landing decision.'}</p> : null}
      </div>
      <aside className="lab-sidebar" aria-label="Reactive flight mode and telemetry">
        {modeControl}
        <div className="lab-introduction"><span className="lab-eyebrow">Engineering model</span><p>Engineering state-feedback exploration. The controller uses geometric clearance to the existing chamber bounds; it has no internal-obstacle sensor and is not a biological flight-control model.</p></div>
        <details className="lab-details" open><summary>Accepted flight telemetry <span aria-hidden="true">+</span></summary><div className="lab-panel-content">
          <dl className="lab-telemetry" data-controller={controller.id} data-controller-version={controller.version}>
            <div><dt>Controller / plant</dt><dd>{controller.id} · v{controller.version} / {FLIGHT_MODEL.schema}</dd></div>
            <div><dt>Plant state / controller phase</dt><dd>{frame.state} / {session.controllerPhase}</dd></div>
            <div><dt>Position / velocity</dt><dd>{frame.position.map(value => value.toFixed(4)).join(' / ')} units · {frame.velocity.map(value => value.toFixed(4)).join(' / ')} units/s</dd></div>
            <div><dt>Heading / horizontal speed</dt><dd>{frame.heading.toFixed(4)} rad / {Math.hypot(frame.velocity[0], frame.velocity[2]).toFixed(4)} units/s</dd></div>
            <div><dt>Forward / left / right clearance</dt><dd>{clearance ? `${clearance.forward_wall_clearance_units.toFixed(3)} / ${clearance.left_wall_clearance_units.toFixed(3)} / ${clearance.right_wall_clearance_units.toFixed(3)} units` : 'No post-start observation yet'}</dd></div>
            <div><dt>Floor / ceiling clearance</dt><dd>{clearance ? `${clearance.floor_clearance_units.toFixed(3)} / ${clearance.ceiling_clearance_units.toFixed(3)} units` : 'No post-start observation yet'}</dd></div>
            <div><dt>Horizontal distance / explored X/Z extent</dt><dd>{metrics.horizontal_distance_units.toFixed(3)} / {metrics.explored_x_extent_units.toFixed(3)} / {metrics.explored_z_extent_units.toFixed(3)} units</dd></div>
            <div><dt>Steering responses / wall contacts</dt><dd>{metrics.steering_response_count} / {metrics.wall_contacts.length}</dd></div>
            <div><dt>Altitude range / vertical speed</dt><dd>{metrics.altitude_range_above_floor_units.map(value => value.toFixed(3)).join('–')} units above floor · {frame.velocity[1].toFixed(4)} units/s</dd></div>
            <div><dt>Bound violations / floor or ceiling contacts</dt><dd>{metrics.accepted_bound_violations} / {metrics.floor_ceiling_contacts.length}</dd></div>
            {touchAndGo && latestInterval && 'landing_eligible' in latestInterval.decision ? <div><dt>Landing / re-takeoff eligibility</dt><dd>{String(latestInterval.decision.landing_eligible)} / {String(latestInterval.decision.takeoff_eligible)} · {latestInterval.decision.reason}</dd></div> : null}
            {sustained && 'ground_episode_count' in metrics && typeof metrics.ground_episode_count === 'number' && 'walking_distance_units' in metrics && typeof metrics.walking_distance_units === 'number' && 'walking_duration_s' in metrics && typeof metrics.walking_duration_s === 'number' ? <div><dt>Ground episodes / walking distance / duration</dt><dd>{metrics.ground_episode_count} / {metrics.walking_distance_units.toFixed(3)} units / {metrics.walking_duration_s.toFixed(2)} s</dd></div> : null}
            <div><dt>Termination</dt><dd>{status === 'completed' ? sustained ? 'DURATION_WINDOW_COMPLETED' : touchAndGo || mixed ? 'SECOND_FLIGHT_CONFIRMED' : 'DURATION_LIMIT_REACHED' : status === 'failed' ? 'FAILED' : 'IN PROGRESS'}</dd></div>
          </dl>
          <p className="lab-setting-note">State n produces a bounded geometric observation and feedback command for interval n; the existing FlightEngine then accepts state n+1. No waypoints, scheduled turns, neural lift command or renderer-driven translation are used. Wall distance is an engineering world query, not biological optic flow.</p>
        </div></details>
      </aside>
    </div>
  </section>;
}
