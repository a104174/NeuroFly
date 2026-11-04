"use client";
import {useEffect,useMemo,useState,type ReactNode,type ComponentProps} from 'react';
import type {NeuralArtifact} from '@/lib/neuralLocomotion';
import {activePairPlane,pairScene,pairOverview,PAIR_STYLE,type PairKey} from '@/lib/neuralContributionComparison';
import {advanceLocomotion} from '@/lib/experimentalLocomotion';
import {wrappedAngle} from '@/lib/neuralSteeringComparison';
import {validateArenaPair,type ArenaPair} from "@/lib/arenaSessionDispatch";
import {movingPairWorld,movingPairOverview} from "@/lib/movingVisualStimuli";
import {independentPairWorld,independentPairOverview} from '@/lib/independentVisualStimuli';
import {FlyViewer} from './FlyViewer';

export function NeuralContributionComparison({pair,authority,onReturn,onImport,generationMs,livePanel,liveViewerProps,libraryPanel}:{pair:ArenaPair|null;authority:NeuralArtifact|null;livePanel:ReactNode;libraryPanel?:ReactNode;liveViewerProps:ComponentProps<typeof FlyViewer>;onReturn:()=>void;onImport:(p:ArenaPair,elapsed:number)=>void;generationMs:number}){
 const [storedTime,setTime]=useState(0),[shownId,setShownId]=useState<string|null>(null),[playing,setPlaying]=useState(false),[focus,setFocus]=useState<PairKey>('ON'),[error,setError]=useState<string|null>(null),[importNotice,setImportNotice]=useState("");
 const identity=pair?.artifact_id??null;
 if(shownId!==identity){setShownId(identity);setTime(0);setPlaying(false);setFocus('ON');}
 const time=shownId===identity?Math.min(storedTime,pair?.config.duration_s??30):0;
 const duration=pair?.config.duration_s??30,running=Boolean(pair&&playing&&time<duration);
 useEffect(()=>{if(!running)return;let handle=0,previous:number|null=null;const tick=(now:number)=>{if(previous!==null){const elapsed=now-previous;setTime(t=>advanceLocomotion(t,elapsed,true,duration));}previous=now;handle=requestAnimationFrame(tick);};handle=requestAnimationFrame(tick);return()=>cancelAnimationFrame(handle);},[running,duration]);
 const base=useMemo(()=>pair&&authority?pair.schema==='independent_visual_stimulus_comparison_v5'?independentPairOverview(pair):pair.schema==='moving_visual_stimulus_comparison_v4'?movingPairOverview(pair):pairOverview(pair,authority.config.policy.landmark_x):null,[pair,authority]);
 async function exportPair(){if(!pair)return;const url=URL.createObjectURL(new Blob([JSON.stringify(pair)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download=pair.schema==='independent_visual_stimulus_comparison_v5'?'neurofly-independent-comparison-v5.json':pair.schema==='moving_visual_stimulus_comparison_v4'?'neurofly-moving-comparison-v4.json':'neurofly-neural-comparison-v3-1.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 async function importPair(file:File|undefined){if(!file||!authority)return;setPlaying(false);try{if(file.size>16_000_000)throw new Error('Comparison exceeds bounded file limit');const start=performance.now(),original=JSON.parse(await file.text()),validated=await validateArenaPair(authority,original);onImport(validated,performance.now()-start);setImportNotice(`Ficheiro validado ${original.artifact_id}; comparison recomputed ${validated.artifact_id}. Supplied trajectories were not applied directly.`);setTime(0);setError(null);}catch(e){setError(String(e));}}
 if(!pair||!authority||!base)return <>{livePanel}<FlyViewer {...liveViewerProps}/></>;
 const world=pair.schema==='independent_visual_stimulus_comparison_v5'?independentPairWorld(pair,time):pair.schema==='moving_visual_stimulus_comparison_v4'?movingPairWorld(pair,time):null;
 const plane=world?.z??(pair.schema==='neural_contribution_comparison_v3_1'?activePairPlane(pair,time):.4),overview={...base,landmarkX:world?[]:base.landmarkX,tracks:base.tracks.map(t=>({...t,plane}))};
 const states=PAIR_STYLE.map((style,i)=>({...style,scene:pairScene(pair.result.tracks[i],time,authority.config.body.asset_offset)}));
 const chosen=states.find(s=>s.key===focus)!,a=states[0].scene,b=states[1].scene;
 const separation=Math.hypot(a.pose.anchor[0]-b.pose.anchor[0],a.pose.anchor[2]-b.pose.anchor[2]),heading=wrappedAngle(a.pose.rotation-b.pose.rotation);
 return <>
  <section className="arena-replay-panel" aria-label="Neural contribution comparison">
   <p className="arena-replay-identity">Neural Contribution Comparison {world&&'landmarks' in world?'v5':world?'v4':'v3.1'} · NEURAL STEERING ON/OFF COUNTERFACTUAL</p>
   <p className="arena-science-limit">Local reconstruction of the LIVE CONNECTOME-INFORMED MODEL from the external log. ENGINEERING PROPULSION · ENGINEERING BOUNDARY RECOVERY. OFF keeps computing neural states and suppresses only their application to heading; is not a physiological lesion. Each world observes its own pose.</p>
   {world?<p data-pair-world-x={JSON.stringify(world.x)} data-pair-world-phase={'phase' in world?world.phase:undefined} data-pair-independent-world={'landmarks' in world?JSON.stringify(world):undefined}>EXPERIMENTAL_MOVING_VISUAL_STIMULUS · X {world.x.map(x=>x.toFixed(5)).join(" / ")} · {'landmarks' in world?world.landmarks.map(s=>`${s.id}: ${s.enabled?'moving':'stopped'}/${s.direction}, phase ${s.phase.toFixed(5)} rad`).join(' · '):`phase ${world.phase.toFixed(5)} rad · movimento ${world.motion}`} . Same external geometry in both worlds; observations depend on each pose.</p>:null}
   <p data-pair-generation-ms={generationMs}>Paired reconstruction: {generationMs.toFixed(1)} ms · {pair.parent.log.stop_step*2} intervalos, {pair.parent.log.stop_step*400} neural substeps. Visual replay does not run the solvers again.</p>
   <button onClick={()=>{setPlaying(false);setTime(0);setFocus("ON");setError(null);setImportNotice("");onReturn();}}>Return to interactive simulation</button>
   <label htmlFor="pair-focus">Fly in focus (time is kept)</label><select id="pair-focus" value={focus} onChange={e=>setFocus(e.target.value as PairKey)}><option value="ON">● Neural ON</option><option value="OFF">■ Neural OFF</option></select>
   <label htmlFor="pair-time">Shared time</label><input id="pair-time" type="range" min={0} max={duration} step={.001} value={time} onChange={e=>{setPlaying(false);setTime(Number(e.target.value));}}/>
   <p className="arena-replay-note" data-pair-time={time}>Time {time.toFixed(3)} / {duration.toFixed(2)} s · recorded prefix, with no extension and no pending requests applied. Markers ● ON / ■ OFF; ON trail solid, OFF trail dashed.</p>
   <div className="comparison-table-scroll"><table><thead><tr><th>Condition</th><th>X / Z</th><th>Heading rad</th><th>Readout yaw_drive_eq</th><th>Neural rad/s</th><th>Engenharia rad/s</th><th>Propulsion</th><th>Distance</th><th>Contact / recoveries</th></tr></thead><tbody>
    {states.map(s=><tr key={s.key} data-pair-condition={s.key} data-pair-position={JSON.stringify(s.scene.pose.anchor)} data-pair-heading={s.scene.pose.rotation} data-pair-readout={s.scene.readout??'UNAVAILABLE'} data-pair-neural={s.scene.neural} data-pair-boundary={s.scene.boundary} data-pair-contact={s.scene.frame.contact??'NONE'} data-pair-recoveries={s.scene.recoveries}>
     <th style={{color:s.color}}>{s.symbol} {s.key}</th><td>{s.scene.pose.anchor[0].toFixed(5)} / {s.scene.pose.anchor[2].toFixed(5)}</td><td>{s.scene.pose.rotation.toFixed(5)}</td><td>{s.scene.readout?.toExponential(5)??'No next interval'}</td><td>{s.scene.neural.toFixed(5)}</td><td>{s.scene.boundary.toFixed(5)}</td><td>{s.scene.frame.propulsion_model_value.toFixed(2)} units/s</td><td>{s.scene.distance.toFixed(5)}</td><td>{s.scene.frame.contact??'None'} / {s.scene.recoveries}</td>
    </tr>)}
   </tbody></table></div>
   <p data-pair-separation={separation} data-pair-wrapped-heading={heading}>Current ON−OFF: separation {separation.toFixed(5)} units; heading wrapped ±π {heading.toFixed(5)} rad; difference in distance travelled {(a.distance-b.distance).toFixed(5)} units.</p>
   <details><summary>Maxima, contacts and stimuli</summary>
    <p data-pair-max-separation={pair.result.metrics.max_separation.value} data-pair-max-heading={pair.result.metrics.max_wrapped_heading.value}>Maxima over the full prefix: separation {pair.result.metrics.max_separation.value.toFixed(5)} units at {pair.result.metrics.max_separation.time.toFixed(3)} s; |heading wrapped| {pair.result.metrics.max_wrapped_heading.value.toFixed(5)} rad em {pair.result.metrics.max_wrapped_heading.time.toFixed(3)} s. Maxima are independent of the current cursor. Final distance difference {pair.result.metrics.traveled_difference.toFixed(5)} units.</p>
    {pair.result.tracks.map(track=><p key={track.key}>{track.key}: {track.contact_events.filter(e=>e.kind==='CONTACT').length} contactos / {track.contact_events.filter(e=>e.kind==='RECOVERY').length} recoveries. {track.contact_events.map(e=>`${e.kind} ${e.wall} ${e.time.toFixed(2)} s`).join(' · ')}</p>)}
    <p>Current stimulus Z={plane}. Identical external interventions in both worlds: {pair.parent.log.events.length?pair.parent.log.events.map(e=><button key={'sequence' in e?e.sequence:e.step} data-pair-event={e.step} onClick={()=>{setPlaying(false);setTime(e.time);}}>{e.time.toFixed(2)} s · {'stimulus_id' in e?`${e.stimulus_id} ${e.kind}`:'new_motion' in e?`movimento ${e.old_motion} → ${e.new_motion}`:`Z ${e.old_plane} → ${e.new_plane}`}</button>):'No interventions applied.'}</p>
    <p>Readout and contributions correspond to the interval that starts at the selected boundary (held between boundaries); poses and distance are interpolated. At the endpoint there is no next interval. The largest separation considers linear segments; the largest wrapped heading also checks crossings of π between samples.</p>
    <p>States and contacts are recomputed, not trajectories supplied by the import. 200 substeps of 0.1 ms per 20 ms interval, {pair.parent.log.stop_step*200} per condition. Recomputed with the same parameters and events; only NEURAL_TO_HEADING_ENABLED differs. More distance does not demonstrate better biological navigation.</p>
    <p className="arena-artifact-id">Parent: {pair.config.parent_session_id} · comparison: {pair.artifact_id} · config: {pair.config_sha256} · result: {pair.result_sha256}</p>
   </details>
   {libraryPanel}
   <button onClick={()=>void exportPair()}>Export comparison JSON</button><label htmlFor="pair-import">Import comparison JSON</label><input id="pair-import" type="file" accept="application/json" onChange={e=>void importPair(e.target.files?.[0])}/>
   {importNotice?<p role="status" className="arena-artifact-id">{importNotice}</p>:null}
   {error?<p role="alert">{error}. Previous comparison preserved; no substitute movement.</p>:null}
  </section>
  <FlyViewer arena locomotion locomotionVersion={world&&'landmarks' in world?"v5":world?"v4":"v3.1"} stimulusIds={world&&'landmarks' in world?["A","B"]:undefined} stimulusPlane={world?.z} stimulusX={world?.x} replayPose={chosen.scene.pose} comparison={{overview,states,time,focus}} playbackControls={<div className="arena-replay-controls"><button onClick={()=>{if(time>=duration){setTime(0);setPlaying(true);}else setPlaying(!playing);}}>{playing&&time<duration?'Pause':'Play'}</button><button onClick={()=>{setPlaying(false);setTime(0);}}>Reset Comparison</button><output data-pair-playback-time={time}>{time.toFixed(2)} / {duration.toFixed(2)} s{time>=duration?' · Fim':' · Counterfactual replay'}</output></div>}/>
 </>;
}
