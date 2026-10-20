"use client";
import { useEffect, useState } from 'react';
import { FlyViewer } from './FlyViewer';
import { flightPose, WING_RIG } from '@/lib/articulatedWings';

/** A presentation-only timeline. Never enters scientific session storage or neural runtimes. */
export function FlightVisualPreview() {
  const [time, setTime] = useState(0);
  const [playing, setPlaying] = useState(false);
  const active = playing && time < WING_RIG.animation.duration_s;
  useEffect(() => {
    if (!active) return;
    // An absolute clock anchor, not a phase increment per rendered frame. Resume reanchors
    // at the current presentation time; resize/renderer frame skips do not alter the law.
    const origin = performance.now(), initial = time;
    let frame = 0;
    const tick = (now: number) => {
      setTime(Math.min(WING_RIG.animation.duration_s, initial + (now - origin) / 1000));
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
    // Only start/stop anchors the clock. A timestamp update must not restart it.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active]);
  const pose = flightPose(time);
  return <section className="arena-replay-panel flight-preview" aria-label="Flight Visual Preview v7.1">
    <h2>Flight Visual Preview v7.1</h2>
    <p>Engineering flight visualization — wing motion is not neurally or aerodynamically validated.</p>
    <p>Presentation time only · Original wing surfaces · Stable leg posture · No scientific trajectory or experiment is created.</p>
    <FlyViewer arena flightPresentation={pose} presentationLabel="Engineering flight visual preview / presentation clock only" playbackControls={<div className="arena-replay-controls">
      <button disabled={time === 8} onClick={() => setPlaying(!active)}>{active ? 'Pause' : time > 0 && time < 8 ? 'Resume' : 'Play'}</button>
      <button onClick={() => { setPlaying(false); setTime(0); }}>Reset</button>
      <label>Presentation time <input aria-label="Flight presentation time" type="range" min={0} max={8} step={.01} value={time} onChange={e => { setPlaying(false); setTime(Number(e.target.value)); }}/></label>
      <output data-flight-presentation={JSON.stringify(pose)}>{time.toFixed(2)} / 8.00 s · {pose.state} · visual altitude {pose.offset.toFixed(3)} units</output>
    </div>}/>
    <details><summary>Wing presentation contract</summary>
      <p>ENGINEERING_FLIGHT_VISUAL_DEMO · 0–1 s grounded; 1–2.25 s takeoff; 2.25–5.75 s hover; 5.75–7 s landing; 7–8 s grounded. Maximum visual vertical offset 0.18 presentation units. No XY route or aerodynamics.</p>
      <p>2 Hz engineering inspection frequency; 0.45 rad maximum mirrored stroke about Z, 0.95 rad deployment about Y. Smoothstep transition envelope. Phase is an analytic function of presentation time. Original V2-F rest transforms return exactly when grounded. This is independent from MaleCNS/model time.</p>
      <p>articulated_wing_motion_v7_1 · CC BY 4.0 source attribution retained below. No wing-muscle signal, neural input, lift, flight stabilization or scientific flight telemetry.</p>
    </details>
  </section>;
}
