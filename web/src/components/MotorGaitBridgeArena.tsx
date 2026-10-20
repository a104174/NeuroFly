"use client";
import {useEffect,useMemo,useState} from 'react';
import {FlyViewer} from './FlyViewer';
import {loadMotorReference,motorAt,projectMotorGait,PROJECTION,type MotorReference,type BridgeCondition} from '@/lib/motorGaitBridge';
import {loadNeuralLocomotion,type NeuralArtifact} from '@/lib/neuralLocomotion';
import {locomotionScene,type LocomotionReplay} from '@/lib/experimentalLocomotion';
import {gaitAt,gaitHistory,legJoints} from '@/lib/articulatedGait';

const conditions:{id:BridgeCondition;label:string}[]=[{id:'BASE',label:'Base Gait'},{id:'ON',label:'Motor Model Bridge ON'},{id:'ROUTE_OFF',label:'Route OFF control'},{id:'SHAM',label:'Sham control'}];
type Inputs={reference:MotorReference;replay:LocomotionReplay;authority:NeuralArtifact;loadMs:number};
export function MotorGaitBridgeArena(){
 const [inputs,setInputs]=useState<Inputs|null>(null),[error,setError]=useState<string|null>(null),[time,setTime]=useState(0),[playing,setPlaying]=useState(false),[condition,setCondition]=useState<BridgeCondition>('BASE');
 useEffect(()=>{let active=true;const start=performance.now();Promise.all([loadMotorReference(),loadNeuralLocomotion()]).then(([reference,{replay,authority}])=>{if(active)setInputs({reference,replay,authority,loadMs:performance.now()-start});}).catch(e=>{if(active)setError(String(e));});return()=>{active=false;};},[]);
 const activePlayback=playing&&time<2;
 useEffect(()=>{if(!activePlayback)return;let id=0,previous:number|null=null;const tick=(now:number)=>{if(previous!==null)setTime(t=>Math.min(2,t+(now-previous!)/1000));previous=now;id=requestAnimationFrame(tick);};id=requestAnimationFrame(tick);return()=>cancelAnimationFrame(id);},[activePlayback]);
 const samples=useMemo(()=>inputs?.replay.result.runs[1].frames.filter(f=>f.time<=2).map(f=>({time:f.time,position:f.position,heading:f.orientation}))??[],[inputs]);
 const history=useMemo(()=>gaitHistory(samples),[samples]);
 const frames=useMemo(()=>samples.slice(0,-1).map(s=>({time:s.time,position:s.position,orientation:s.heading})),[samples]);
 const curves=useMemo(()=>{if(!inputs)return null;const rows=inputs.reference.samples;return {response:rows.map((r,n)=>`${n/2000*600},${80-r[1]}`).join(' '),height:rows.map((_,n)=>`${n/2000*600},${170-(motorAt(inputs.reference,n*.001,condition).height-.012)*10000}`).join(' ')};},[inputs,condition]);
 if(error)return <section role="alert">Motor-to-Gait Bridge unavailable: {error} No substitute motor activity or gait projection was created.</section>;
 if(!inputs||!history.length||!curves)return <p role="status">Validating pinned Python motor response and body reference…</p>;
 const {reference,replay,authority}=inputs,scene=locomotionScene(replay,1,time),signal=motorAt(reference,time,condition),base=gaitAt(history,time),projected=projectMotorGait(base,reference,condition),joint=legJoints(3,projected.feet[3].foot,projected.body),baseJoint=legJoints(3,base.feet[3].foot,base.body);
 const bend=(p:typeof joint.points)=>p[1].clone().sub(p[0]).angleTo(p[2].clone().sub(p[1]));
 const details={...signal,body:base.body,foot:projected.feet[3].foot,baseFoot:base.feet[3].foot,knee_rad:bend(joint.points),base_knee_rad:bend(baseJoint.points),clamped:joint.clamped};
 return <section aria-label="Motor-to-Gait Bridge v7">
  <div className="arena-mode-controls" aria-label="Motor projection controls">{conditions.map(c=><button key={c.id} aria-pressed={condition===c.id} onClick={()=>setCondition(c.id)}>{c.label}</button>)}</div>
  <p className="arena-science-limit">EXPERIMENTAL_MODEL_DERIVED_GAIT_MODULATION · SHADOW_ONLY_MOTOR_RESPONSE · ENGINEERING_JOINT_PROJECTION · NO_VALIDATED_NEUROMUSCULAR_ACTUATION</p>
  <p>Enable Articulated Gait v6 below the arena. One front-right swing-height overlay; other five legs and body remain matched. Open-loop source: no HS/DNp15 → DNg100 connection is assumed.</p>
  <FlyViewer arena locomotion presentationLabel="Motor-to-Gait v7 / PRECOMPUTED_PYTHON_MOTOR_MODEL_RESPONSE" gaitMotion={{frames,end:samples.at(-1)!,time}} motorBridge={{reference,condition}} replayPose={scene.pose} trajectory={samples.map(s=>[s.position[0],.008,s.position[2]])} playbackControls={<div className="arena-replay-controls"><button onClick={()=>{if(time===2){setTime(0);setPlaying(true);}else setPlaying(!playing);}}>{playing&&time<2?'Pause':'Play'}</button><button onClick={()=>{setPlaying(false);setTime(0);}}>Reset bridge</button><output>{time.toFixed(3)} / 2.000 s{time===2?' · End':playing?' · Playing':' · Paused'}</output></div>}/>
  <label>Bridge time (s) <input aria-label="Bridge time (s)" type="range" min={0} max={2} step={.001} value={time} onChange={e=>{setPlaying(false);setTime(Number(e.target.value));}}/></label>
  <output data-motor-bridge={JSON.stringify(details)} aria-label="Motor bridge scientific inspector" className="arena-replay-note">
   {condition} · t={time.toFixed(3)} s · source 903216: {signal.source.toFixed(6)} model units · receiver 804257: {signal.receiver.toFixed(6)} uncalibrated receiver units<br/>
   Front-right peak swing height: {signal.height.toFixed(7)} presentation units · calculated articulated foot lift (requires Articulated Gait): {(projected.feet[3].foot[1]-base.feet[3].foot[1]).toExponential(4)} · knee: {details.knee_rad.toFixed(6)} rad (base {details.base_knee_rad.toFixed(6)}) · IK projected: {String(joint.clamped)}<br/>
   Body X/Z {scene.pose.anchor[0].toFixed(6)} / {scene.pose.anchor[2].toFixed(6)} · heading {scene.pose.rotation.toFixed(6)} rad · engineering propulsion 0.18 units/s · contact {scene.frame.contact??'NONE'}
  </output>
  <details open><summary>Matched response / visual-parameter timeline</summary>
   <svg viewBox="0 0 600 190" style={{width:'100%',maxHeight:220}} role="img" aria-label="Motor receiver and front-right peak swing height, shared scientific time">
    <text x="0" y="14" fill="currentColor" fontSize="11">Receiver: uncalibrated model units (0–80), 1 ms boundaries</text><line x1="0" y1="80" x2="600" y2="80" stroke="#777"/><polyline points={condition==='ROUTE_OFF'?'0,80 600,80':curves.response} fill="none" stroke="#49b4c1" strokeWidth="1"/>
    <text x="0" y="110" fill="currentColor" fontSize="11">Front-right peak swing height: 0.012–0.016 presentation units</text><line x1="0" y1="170" x2="600" y2="170" stroke="#777"/><polyline points={curves.height} fill="none" stroke="#d8aa71" strokeWidth="1"/><line x1={time*300} x2={time*300} y1="16" y2="175" stroke="currentColor"/>
    <text x="0" y="180" fill="currentColor" fontSize="11">0 s</text><text x="565" y="180" fill="currentColor" fontSize="11">2 s</text>
   </svg>
   <p>Python boundary states y[n] precede consumption of u[n] over [t[n],t[n+1]). Linear interpolation is a visual reconstruction only; no extrapolation, repetition or future neural calculation. Height is a swing envelope parameter, not a joint angle or measured muscle activity. Stance remains unchanged.</p>
  </details>
  <details><summary>Source, engineering projection and limitations</summary>
   <p>MALECNS_STRUCTURAL_PATHWAY · MODEL_DERIVED_NEURAL_ACTIVITY · SHADOW_ONLY_MOTOR_RESPONSE · ENGINEERING_GAIT_PROJECTION · PRECOMPUTED_PYTHON_MOTOR_RESPONSE</p>
   <p>MaleCNS v1.0 · 903216 INXXX466_R → 804257 Ti extensor MN_R · 23 structural contacts (provenance only, never a force or gain). Recurrent source: prescribed DNg100 input of 20 model units, hypothetical signs. Receiver: tau dy/dt = −y + u; tau=0.01 s, gain=1, initial y=0; exact held-input solution. Functional sign and physiological recruitment UNKNOWN.</p>
   <p>Projection v7: height = clamp(0.012 + 0.004 × clamp(m/100, −1, 1), 0.008, 0.016). Fixed engineering reference 100 receiver units, gain 0.004 presentation units; no per-run normalization. Only swing lift is scaled, using the existing v6 envelope and bounded IK. BASE disables projection; ROUTE_OFF zeros only the selected route input, retaining source dynamics; SHAM reproduces ON. No validated external-drive intervention is added.</p>
   <p>PRECOMPUTED_PYTHON_MOTOR_MODEL_RESPONSE · Body: existing v1 NEURAL_STEERING replay, first 2 s; all conditions share exactly this trajectory and HS/DNp15 history. Motor source is an independent open-loop experiment. No feedback to neural dynamics, propulsion or contacts. No spiking, muscles, force or calibrated anatomy.</p>
   <p className="arena-artifact-id">Motor artifact {reference.response_artifact_id} · recurrent source {reference.source.neural_source_artifact_id} · body {authority.artifact_id} · rig descriptor 1349d977ef9f72ba9d7f7ac8fe284572039b14c3c59dff2204e1bead800c191f · projection {PROJECTION.version} · randomness NONE · source load/validation {inputs.loadMs.toFixed(1)} ms.</p>
  </details>
 </section>;
}
