"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { FlyViewer } from './FlyViewer';
import { EngineeringVerticalFlightLab } from './EngineeringVerticalFlightLab';
import { LabSimulationModeControl, type LabSimulationMode } from './lab/LabSimulationModeControl';
import { ExploreLabView } from './lab/ExploreLabView';
import { gaitHistory, type GaitState } from '@/lib/articulatedGait';
import { loadNeuralLocomotion, type NeuralArtifact } from '@/lib/neuralLocomotion';
import { LiveClock, LiveGroundSession, pauseForVisibility, type LiveSample, type LiveStatus } from '@/lib/liveGroundSession';
import type { ExplorationMode } from '@/lib/engineeringExploration';
import type { NavigationSnapshot } from '@/lib/continuousArenaNavigation';

export function LiveExploreArena() {
  const session = useRef<LiveGroundSession | null>(null);
  const clock = useRef(new LiveClock());
  const gait = useRef<GaitState | null>(null);
  const [authority, setAuthority] = useState<NeuralArtifact | null>(null);
  const [state, setState] = useState<NavigationSnapshot | null>(null);
  const [status, setStatus] = useState<LiveStatus>('ready');
  const [gaitState, setGaitState] = useState<GaitState | undefined>();
  const [path, setPath] = useState<[number, number, number][]>([]);
  const [sample, setSample] = useState<LiveSample | null>(null);
  const [history, setHistory] = useState<LiveSample[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [neural, setNeural] = useState(true);
  const [mode, setMode] = useState<ExplorationMode>('baseline_v10_5b');
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState('');
  const [lagging, setLagging] = useState(false);
  const [labMode, setLabMode] = useState<LabSimulationMode>('ground');

  const install = useCallback((source: NeuralArtifact, enabled: boolean, selectedMode: ExplorationMode) => {
    session.current?.stop(); clock.current.reset();
    const next = new LiveGroundSession(source, enabled, crypto.randomUUID(), undefined, undefined, selectedMode);
    session.current = next;
    setSessionId(next.config.session_id);
    const snapshot = next.snapshot();
    gait.current = gaitHistory([{ time: snapshot.time, position: snapshot.position, heading: snapshot.heading }])[0];
    setGaitState(gait.current); setState(snapshot); setPath(next.trajectory.values());
    setStatus('ready'); setSample(null); setHistory([]); setError(null); setLagging(false);
  }, []);

  useEffect(() => {
    let active = true;
    const mountedClock = clock.current;
    loadNeuralLocomotion().then(({ authority: source }) => {
      if (!active) return;
      try { install(source, true, 'baseline_v10_5b'); setAuthority(source); } catch (e) { setError(String(e)); }
    }).catch(e => { if (active) setError(String(e)); });
    return () => { active = false; session.current?.stop(); mountedClock.reset(); };
  }, [install]);

  useEffect(() => {
    const onVisibility = () => {
      if (session.current && pauseForVisibility(session.current, document.hidden)) {
        setHistory(session.current.telemetry.values()); clock.current.reset(); setStatus('paused'); setNotice('Paused while this page was hidden. Resume when ready.');
      }
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, []);

  useEffect(() => {
    if (status !== 'running') return;
    let animation = 0, previous: number | null = null;
    const tick = (now: number) => {
      const current = session.current;
      if (!current || current.status !== 'running') return;
      if (document.hidden) {
        pauseForVisibility(current, true); setHistory(current.telemetry.values()); clock.current.reset(); setStatus('paused'); setNotice('Paused while this page was hidden. Resume when ready.'); return;
      }
      if (previous !== null) {
        try {
          let latest: LiveSample | null = null;
          const result = clock.current.advance(current, now - previous, next => {
            latest = next;
            const body = { time: next.accepted.time, position: next.accepted.position, heading: next.accepted.heading };
            if (!gait.current) throw new Error('Gait state unavailable');
            gait.current = gaitHistory([gait.current.body, body], [gait.current])[1];
          });
          if (result.steps) { const currentSnapshot = current.snapshot(); setState(currentSnapshot); setPath(current.trajectory.values()); setSample(latest); if (currentSnapshot.step % 10 < result.steps) setHistory(current.telemetry.values()); setGaitState(gait.current ?? undefined); }
          if (result.limited) setLagging(true);
        } catch (e) {
          if (!current.error) current.stop();
          clock.current.reset(); setStatus(current.error ? 'error' : 'stopped'); setError(String(e)); return;
        }
      }
      previous = now; animation = requestAnimationFrame(tick);
    };
    animation = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animation);
  }, [status]);

  function play() {
    const current = session.current; if (!current) return;
    if (current.status === 'running') { current.pause(); setHistory(current.telemetry.values()); clock.current.reset(); setStatus('paused'); return; }
    if (document.hidden) { setNotice('Return to this page to start the session.'); return; }
    try { current.start(); clock.current.reset(); setStatus('running'); setNotice(''); } catch (e) { setError(String(e)); }
  }
  function stop() { session.current?.stop(); clock.current.reset(); setStatus('stopped'); setNotice('Session stopped. Reset to start a new session.'); }
  function reset() { if (authority) { install(authority, neural, mode); setNotice('New session from the original initial state.'); } }
  function changeNeural(enabled: boolean) { setNeural(enabled); if (authority) { install(authority, enabled, mode); setNotice('Neural influence changed. A new session starts from the initial state.'); } }
  function changeMode(selectedMode: ExplorationMode) {
    if (!authority || ['running', 'paused'].includes(status)) return;
    setMode(selectedMode); install(authority, neural, selectedMode);
    setNotice('Locomotion mode changed. A new session starts from the original initial state.');
  }
  function changeLabMode(selectedMode: LabSimulationMode) {
    if (selectedMode === labMode) return;
    session.current?.stop(); clock.current.reset();
    if (selectedMode === 'ground') {
      if (authority) install(authority, neural, mode);
      else setStatus('ready');
    } else setStatus('stopped');
    setLabMode(selectedMode);
  }
  const pose = state && authority ? { anchor: state.position, rotation: state.heading, assetOffset: authority.config.body.asset_offset } : undefined;
  const modeControl = <LabSimulationModeControl value={labMode} onChange={changeLabMode}/>;

  if (labMode === 'vertical-flight') return <EngineeringVerticalFlightLab modeControl={modeControl}/>;

  return <ExploreLabView state={state} playing={status === 'running'} error={error} notice={notice} neuralEnabled={neural} onPlay={play} onStop={stop} onReset={reset} onNeuralChange={changeNeural} mode={mode} onModeChange={changeMode} modeControl={modeControl} lagging={lagging} liveStatus={status} latestSample={sample} recentSamples={history} sessionId={sessionId}>
    <FlyViewer experience initialGait arena locomotion={Boolean(state)} locomotionVersion="v3" replayPose={pose} stimulusPlane={state?.plane} liveTrajectory={path} liveGaitState={gaitState}/>
  </ExploreLabView>;
}
