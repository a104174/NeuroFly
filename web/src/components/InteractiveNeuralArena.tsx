"use client";
import {useEffect,useRef,useState} from "react";
import {loadNeuralLocomotion,type NeuralArtifact} from "@/lib/neuralLocomotion";
import {InteractiveNeuralEngine,FixedStepClock,replayEventLog,validateSession,type RuntimeSnapshot,type Plane,type StimulusEvent} from "@/lib/interactiveNeuralLocomotion";
import {FlyViewer} from "./FlyViewer";

export function InteractiveNeuralArena(){
 const engine=useRef<InteractiveNeuralEngine|null>(null),clock=useRef(new FixedStepClock());
 const [authority,setAuthority]=useState<NeuralArtifact|null>(null),[state,setState]=useState<RuntimeSnapshot|null>(null);
 const [pending,setPending]=useState<Plane|null>(null),[events,setEvents]=useState<StimulusEvent[]>([]);
 const [playing,setPlaying]=useState(false),[path,setPath]=useState<[number,number,number][]>([]);
 const [error,setError]=useState<string|null>(null),[notice,setNotice]=useState("");
 const [cost,setCost]=useState({last:0,max:0,limited:0});
 useEffect(()=>{let cancelled=false;loadNeuralLocomotion().then(({authority})=>{if(cancelled)return;try{engine.current=new InteractiveNeuralEngine(authority);setAuthority(authority);setState(engine.current.snapshot());setPath(engine.current.trajectory());}catch(e){setError(String(e));}}).catch(e=>{if(!cancelled)setError(String(e));});return()=>{cancelled=true;};},[]);
 useEffect(()=>{
  if(!playing)return;let animation=0,previous:number|null=null;
  const tick=(now:number)=>{
   if(previous!==null&&engine.current){try{
    const start=performance.now(),result=clock.current.advance(engine.current,now-previous,true),elapsed=performance.now()-start;
    if(result.steps){setState(engine.current.snapshot());setPath(engine.current.trajectory());setPending(engine.current.pendingPlane());setEvents(engine.current.eventLog().events);setCost(old=>({last:elapsed,max:Math.max(old.max,elapsed),limited:old.limited+(result.limited?1:0)}));}
    if(engine.current.snapshot().step===400){setPlaying(false);clock.current.reset();return;}
   }catch(e){setPlaying(false);setError(String(e));return;}}
   previous=now;animation=requestAnimationFrame(tick);
  };animation=requestAnimationFrame(tick);return()=>cancelAnimationFrame(animation);
 },[playing]);
 function synchronize(next:InteractiveNeuralEngine){engine.current=next;clock.current.reset();setState(next.snapshot());setPath(next.trajectory());setPending(next.pendingPlane());setEvents(next.eventLog().events);setPlaying(false);}
 function reset(){if(authority){synchronize(new InteractiveNeuralEngine(authority));setCost({last:0,max:0,limited:0});setNotice("");setError(null);}}
 function planeChange(plane:Plane){try{engine.current?.requestPlane(plane);setPending(engine.current?.pendingPlane()??null);setState(engine.current?.snapshot()??null);setNotice(`Stimulus requested: Z=${plane}; applies at the next interval, boundary ${engine.current?.snapshot().step}.`);}catch(e){setError(String(e));}}
 function replay(){if(authority&&engine.current){try{const old=engine.current.snapshot(),next=replayEventLog(authority,engine.current.eventLog());if(JSON.stringify(old)!==JSON.stringify(next.snapshot()))throw new Error("Replay divergiu");synchronize(next);setNotice("Log recomputed from the initial state: identical final state. The simulation can continue.");}catch(e){setError(String(e));}}}
 async function exportRun(){if(engine.current){try{const data=await engine.current.exportSession();const url=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:"application/json"}));const a=document.createElement('a');a.href=url;a.download='neurofly-interactive-v2.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setNotice(`Log/result hashes: ${data.log_sha256} / ${data.result_sha256}`);}catch(e){setError(String(e));}}}
 async function importRun(file:File|undefined){if(!file||!authority)return;setPlaying(false);clock.current.reset();try{if(file.size>2_000_000)throw new Error("Log demasiado grande");const data=await validateSession(authority,JSON.parse(await file.text()));if(data.log.config.mode!=="neural")throw new Error("This interactive mode requires neural steering on");synchronize(replayEventLog(authority,data.log));setError(null);setNotice("Session imported, validated and recomputed. No external trajectory was applied directly.");}catch(e){setError(String(e));}}
 const pose=state&&authority?{anchor:state.position,rotation:state.heading,assetOffset:authority.config.body.asset_offset}:undefined;
 return <>
  <section className="arena-replay-panel" aria-label="Interactive Neural Locomotion v2">
   <p className="arena-replay-identity">Interactive Neural Locomotion v2 · LIVE_BROWSER_MODEL_SIMULATION</p>
   <p className="arena-science-limit">INTERACTIVE_CONNECTOME_INFORMED_NEURAL_STEERING · ENGINEERING_PROPULSION. Computed locally in the browser; the stimulus changes the observation, not the heading directly. No gait, muscles or calibrated biological speed.</p>
   {!state&&!error?<p role="status">Checking the Python HS/DNp15 authority…</p>:null}
   {error?<p role="alert">{error} Simulation stopped; no substitute movement was created.</p>:null}
   {state?<>
    <label htmlFor="interactive-plane">Plano visual (landmarks X=±0.6)</label><select id="interactive-plane" disabled={state.step===400||Boolean(error)} value={pending??state.plane} onChange={e=>planeChange(Number(e.target.value) as Plane)}><option value={.4}>Z = +0.4</option><option value={-.4}>Z = −0.4</option></select>
    <p data-live-step={state.step} data-live-position={JSON.stringify(state.position)} data-live-heading={state.heading} data-live-neural={JSON.stringify({hs:state.hs,dn:state.dn})} data-live-readout={state.readout??"UNAVAILABLE"} data-live-plane={state.plane} data-live-contact={state.contact??"NONE"} data-live-substeps={state.substeps}>Time {state.time.toFixed(2)} / 8 s · X/Z {state.position[0].toFixed(5)} / {state.position[2].toFixed(5)} · heading {state.heading.toFixed(5)} rad · contact {state.contact??"none"}</p>
    <p>Drive of the last interval: {state.readout?.toExponential(5)??"not yet computed"} yaw_drive_eq · omega of the last interval {state.omega.toFixed(5)} rad/s · propulsion 0.18 units/s (translational speed {state.contact?"0.00":"0.18"}) · distance {state.distance.toFixed(4)} units · active stimulus Z={state.plane}{pending!==null?` (Z=${pending} pendente)`:""}.</p>
    {cost.limited>0?<p className="arena-replay-note" data-live-lagging="true">Simulated pace reduced: catch-up limit reached. The scientific timestep stays fixed.</p>:null}
    {events.length?<p className="arena-replay-note">Last intervention applied: {events[events.length-1].time.toFixed(2)} s · Z={events[events.length-1].new_plane} · boundary {events[events.length-1].step}.</p>:null}
    <details><summary>Interventions, replay and model</summary>
     <p data-live-events={JSON.stringify(events)}>{events.length?events.map(e=>`Boundary ${e.step}, ${e.time.toFixed(2)} s: Z ${e.old_plane} → ${e.new_plane}`).join(" · "):"No interventions applied."}</p>
     <button onClick={replay} disabled={Boolean(error)}>Recompute intervention log</button><button onClick={()=>void exportRun()}>Export session JSON</button><label htmlFor="interactive-import">Import and recompute session</label><input id="interactive-import" type="file" accept="application/json" onChange={e=>void importRun(e.target.files?.[0])}/>
     <p>200 substeps of 0.1 ms per 20 ms interval; exactly {state.substeps} executed. HS/DNp15 states persist; updates are simultaneous, using the old states. Geometric observation of the last completed movement is held during each interval; a plane change applies the new geometry to both endpoints, with no relocation flash. Engineering gain 2.5 rad/orientation_eq, omega limited to ±0.5 rad/s. Contact stops translation; neural/heading continuam.</p>
     <p>Events apply at the next boundary not yet computed, including while paused. Repeated requests are coalesced at that boundary; the last requested plane wins. Reset restores Z=+0.4, the initial pose and zero states. Replay recomputes the log prefix from zero, without consulting B/D trajectories. Export includes a recoverable configuration, events and telemetry with hashes; import requires a semantic replay.</p>
     <p>Pose shown at the last completed boundary, with no extrapolation. Fixed scientific clock, independent of FPS. Up to five intervals per frame; excess lag is discarded, so simulated time can run slower than real time. Absolute Python/JS parity ≤1e−8 model units, over an eight-second window. Readouts are not measured firing rates; landmarks are not a calibrated retina.</p>
     <p data-live-cost-ms={cost.last} data-live-max-cost-ms={cost.max} data-live-catchup={cost.limited}>Update cost: {cost.last.toFixed(2)} ms · maximum {cost.max.toFixed(2)} ms · limite de catch-up ativado {cost.limited} vezes. {cost.limited>0?"The simulation may run slower than real time.":"No catch-up limit observed."}</p>
     <p className="arena-artifact-id">Fonte Python: {authority?.artifact_id} · MaleCNS v1.0 / {authority?.config.dataset_uuid}. HS R 10015/10016/10023, L 10034/10181/10419 → DNp15 11215/12069. Model assumptions kept; no new physiological signal has been established.</p>
    </details>
    {notice?<p className="arena-artifact-id" role="status">{notice}</p>:null}
   </>:null}
  </section>
  <FlyViewer arena locomotion={Boolean(state)} locomotionVersion="v2" replayPose={pose} liveTrajectory={path} stimulusPlane={state?.plane} playbackControls={state?<div className="arena-replay-controls"><button disabled={Boolean(error)} onClick={()=>{if(state.step===400){reset();setPlaying(true);}else{clock.current.reset();setPlaying(!playing);}}}>{playing?"Pause":"Play"}</button><button onClick={reset}>Reset Experiment</button><button disabled={state.step===400||Boolean(error)} onClick={()=>planeChange((pending??state.plane)===.4?-.4:.4)}>Switch visual plane</button><output data-live-time={state.time}>{state.time.toFixed(2)} / 8.00 s{state.step===400?" · Fim":playing?" · Live":" · Pausado"}</output></div>:undefined}/>
 </>;
}
