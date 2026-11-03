"use client";
import {useMemo,useState} from 'react';
import {SignalCanvas} from './NeuralResponseTimeline';
import {timelinePath} from '@/lib/neuralResponseTimeline';
import {visualTimeline,type VisualComparison} from '@/lib/visualStimulusComparison';
const colors=['#6ee7da','#f4bd73','#a5bcff','#e7a3d5'];
export function VisualProgramTimeline({pair,time,onSeek}:{pair:VisualComparison;time:number;onSeek:(t:number)=>void}){
 const [open,setOpen]=useState(false),model=useMemo(()=>visualTimeline(pair),[pair]);
 const plots=useMemo(()=>model.lanes.map(l=>({...l,paths:l.series.map(s=>timelinePath(model.samples[s.condition],sample=>s.values[sample.step],l.extent))})),[model]);
 const {events,contacts}=model;
 const x=(t:number)=>50+820*t/30;
 return <details className="neural-timeline" onToggle={e=>setOpen(e.currentTarget.open)}><summary>Comparative Neural Response Timeline</summary>{open?<>
 <p>P solid / Q dashed. Common vertical scale per quantity, computed from all P and Q samples. A/R and B/L are geometric encodings, not measured receptive fields. Self-motion and world-motion are separate; only the combined input is clipped.</p>
 <p>Observation of the completed interval held for 200 substeps. Readout and rates are available at the end of the 20 ms neural interval. Cursor, pose, landmarks and inspector use the same boundary; no neural interpolation and no new simulation when seeking.</p>
 <p data-visual-timeline-samples={JSON.stringify(model.samples.map(s=>s[Math.round(time/.02)]))}>Scientific cursor {time.toFixed(2)} s · P/Q: {model.samples.map(s=>s[Math.round(time/.02)]?.readout?.toExponential(5)??'unavailable').join(' / ')} yaw_drive_eq</p>
 <div className="neural-timeline-plots">{plots.map(l=><div className="neural-timeline-lane" key={l.key} data-visual-lane={l.key} data-common-extent={l.extent}><p>{l.name} · {l.series.map((s,i)=><span key={s.label} style={{color:colors[i]}}> {s.label} {i%2?'┄':'━'} </span>)}</p><div className="neural-timeline-plot"><SignalCanvas paths={l.paths}/><svg preserveAspectRatio="none" viewBox="0 0 900 94" role="img" aria-label={l.name} onClick={e=>{const r=e.currentTarget.getBoundingClientRect();onSeek(Math.min(pair.config.duration_s,Math.max(0,((e.clientX-r.left)/r.width*900-50)/820*30)));}}>
 <text x="0" y="16" fill="currentColor" fontSize="16">{l.extent.toPrecision(3)}</text><text x="0" y="75" fill="currentColor" fontSize="16">−{l.extent.toPrecision(3)}</text><text x="28" y="47" fill="currentColor" fontSize="16">0</text><line x1="50" x2="870" y1="44" y2="44" stroke="#526070"/>
 {events.map(e=><line key={`${e.condition}:${e.markerKey}`} x1={x(e.time)} x2={x(e.time)} y1="8" y2="78" stroke={e.condition==='P'?colors[0]:colors[1]} strokeDasharray={e.condition==='P'?'2 3':'5 3'}><title>{e.condition}: {e.label}</title></line>)}
 {contacts.map(e=><circle key={`${e.condition}:${e.step}`} cx={x(e.time)} cy={e.condition==='P'?75:81} r={e.kind==='RECOVERY'?2:3} fill={e.condition==='P'?colors[0]:colors[1]}><title>{e.condition} {e.kind} {e.wall} · {e.time.toFixed(2)} s</title></circle>)}
 <line x1={x(time)} x2={x(time)} y1="6" y2="84" stroke="white"/>{[0,5,10,15,20,25,30].map(t=><text key={t} x={x(t)} y="93" fill="currentColor" fontSize="16">{t}s</text>)}</svg></div></div>)}</div>
 <p data-visual-event-markers={JSON.stringify(events)}>Interventions: {events.map(e=>`${e.condition}: ${e.label}`).join(' · ')||'No events applied in the common window.'}</p><p data-visual-contact-markers={JSON.stringify(contacts)}>Contacts and recoveries computed: {contacts.map(e=>`${e.condition} ${e.kind} ${e.time.toFixed(2)}s`).join(' · ')||'none'}. Small circles mark a recovery. Pending requests and events after the common window are not applied.</p>
 </>:null}</details>;
}
