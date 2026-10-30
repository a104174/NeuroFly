"use client";

import { useEffect, useRef, useState, type ReactNode } from 'react';
import { FlyViewer } from './FlyViewer';
import { FlightClock, FLIGHT_MODEL, flightScene } from '@/lib/engineeringFlight';
import { flightWingsV8 } from '@/lib/flightWingsV8';
import { VERTICAL_FLIGHT_CONFIG, VerticalFlightSession, type VerticalFlightStatus } from '@/lib/verticalFlightFeedback';

const statusText: Record<VerticalFlightStatus, string> = {
  ready: 'Grounded · ready', running: 'Flight verification running', paused: 'Paused',
  completed: 'Landing verified', failed: 'Verification failed',
};

export function EngineeringVerticalFlightLab({ modeControl }: { modeControl: ReactNode }) {
  const [session, setSession] = useState(() => new VerticalFlightSession());
  const clock = useRef(new FlightClock());
  const [frame, setFrame] = useState(() => session.snapshot());
  const [metrics, setMetrics] = useState(() => session.metrics());
  const [status, setStatus] = useState<VerticalFlightStatus>('ready');
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
          if (result.steps) { setFrame(session.snapshot()); setMetrics(session.metrics()); }
          const nextStatus = session.status as VerticalFlightStatus;
          if (nextStatus === 'completed' || nextStatus === 'failed') {
            setStatus(nextStatus); setError(session.error); setPlaying(false); clock.current.reset(); return;
          }
        } catch (cause) {
          setFrame(session.snapshot()); setMetrics(session.metrics()); setStatus(session.status);
          setError(cause instanceof Error ? cause.message : String(cause)); setPlaying(false); clock.current.reset(); return;
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

  function play() {
    if (document.hidden) return;
    try { session.start(); clock.current.reset(); setError(null); setStatus(session.status); setPlaying(true); }
    catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); }
  }

  function pause() {
    session.pause(); clock.current.reset(); setPlaying(false); setStatus(session.status);
  }

  function reset() {
    clock.current.reset(); setPlaying(false);
    const next = new VerticalFlightSession(); setSession(next);
    setFrame(next.snapshot()); setMetrics(next.metrics()); setStatus('ready'); setError(null);
  }

  const altitude = frame.position[1] - FLIGHT_MODEL.ground_y;
  const wings = flightWingsV8(frame.time, frame.state, Math.max(0, altitude), VERTICAL_FLIGHT_CONFIG.wing_presentation.preset);
  const bodyPose = flightScene(frame);

  return <section className="lab-experience" data-lab-mode="engineering-flight" data-flight-status={status}>
    <div className="lab-activity"><div><span className="lab-eyebrow">Engineering verification</span><h1>Flight<span>.</span></h1><p>Bounded vertical motion in the existing arena.</p></div><span className={`lab-status${playing ? ' is-running' : ''}`} role="status"><i aria-hidden="true" />{statusText[status]}</span></div>
    <div className="lab-workspace">
      <div className="lab-view-area">
        <FlyViewer experience arena replayPose={bodyPose} flightPresentation={wings}
          presentationLabel="State-feedback vertical flight · fixed 20 ms plant intervals"
          flightDisclosure="Engineering flight using the existing kinematic body plant and a versioned altitude-feedback controller. The motor commands are engineering assumptions, not MaleCNS-derived vertical control. Wing motion is visual only; it does not generate lift or validate biological flight."
          playbackControls={<div className="lab-controls" aria-label="Flight verification controls">
            <button className="lab-play" disabled={playing || status === 'completed' || status === 'failed'} onClick={play}>{status === 'paused' ? 'Resume' : 'Start takeoff'}</button>
            <button disabled={!playing} onClick={pause}>Pause</button>
            <button onClick={reset}>Reset</button>
            <div className="lab-time"><output aria-label="Accepted flight time" aria-live="off">{frame.time.toFixed(2)} s</output><span>Accepted model time · maximum {VERTICAL_FLIGHT_CONFIG.maximum_duration_s} s</span></div>
          </div>}/>
        <p className="lab-live-window" data-flight-snapshot={JSON.stringify(frame)} data-flight-position={JSON.stringify(frame.position)} data-flight-velocity={JSON.stringify(frame.velocity)}>
          Accepted state {frame.step} · {frame.state} · X/Y/Z {frame.position.map(value => value.toFixed(4)).join(' / ')} · velocity {frame.velocity.map(value => value.toFixed(4)).join(' / ')} units/s
        </p>
        {error ? <p className="lab-error" role="alert">{error} The verification stopped at the last accepted body state.</p> : null}
        {status === 'completed' ? <p className="lab-completion" role="status">Takeoff, altitude condition, descent and grounded floor contact verified.</p> : null}
      </div>
      <aside className="lab-sidebar" aria-label="Flight verification mode and telemetry">
        {modeControl}
        <div className="lab-introduction"><span className="lab-eyebrow">Explicit model assumptions</span><p>Engineering state feedback commands altitude. The existing plant integrates motion and arena contacts. This is not a biological flight-control model.</p></div>
        <details className="lab-details" open><summary>Accepted flight telemetry <span aria-hidden="true">+</span></summary><div className="lab-panel-content">
          <dl className="lab-telemetry" data-controller={VERTICAL_FLIGHT_CONFIG.controller.id} data-controller-version={VERTICAL_FLIGHT_CONFIG.controller.version}>
            <div><dt>Controller</dt><dd>{VERTICAL_FLIGHT_CONFIG.controller.id} · v{VERTICAL_FLIGHT_CONFIG.controller.version}</dd></div>
            <div><dt>Plant state / controller phase</dt><dd>{frame.state} / {session.controllerPhase}</dd></div>
            <div><dt>Altitude / vertical speed</dt><dd>{altitude.toFixed(5)} units / {frame.velocity[1].toFixed(5)} units/s</dd></div>
            <div><dt>Target condition</dt><dd>{VERTICAL_FLIGHT_CONFIG.controller.target_altitude_above_ground.toFixed(3)} ± {VERTICAL_FLIGHT_CONFIG.controller.target_altitude_tolerance.toFixed(3)} units above ground</dd></div>
            <div><dt>Maximum altitude reached</dt><dd>{metrics.maximum_altitude_above_ground.toFixed(5)} units</dd></div>
            <div><dt>Airborne duration</dt><dd>{metrics.airborne_duration_s.toFixed(2)} s</dd></div>
            <div><dt>Descent / landing</dt><dd>{metrics.descent_onset_time_s === null ? 'not initiated' : `${metrics.descent_onset_time_s.toFixed(2)} s`} / {metrics.landing_time_s === null ? 'not landed' : `${metrics.landing_time_s.toFixed(2)} s`}</dd></div>
            <div><dt>Contacts / bound violations</dt><dd>{metrics.contacts.map(contact => contact.detail).join(', ') || 'none'} / {metrics.bound_violations}</dd></div>
            <div><dt>Termination</dt><dd>{status === 'completed' ? 'LANDED' : status === 'failed' ? 'FAILED' : 'IN PROGRESS'}</dd></div>
          </dl>
          <p className="lab-setting-note">Takeoff begins only after Start. The climb-to-descent decision uses an accepted altitude and vertical-speed condition. Horizontal and turn commands remain zero. Wing articulation is presentation only.</p>
        </div></details>
      </aside>
    </div>
  </section>;
}
