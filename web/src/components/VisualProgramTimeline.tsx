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
 <p>P solid / Q dashed. Escala vertical comum por grandeza, calculada com todas as amostras P e Q. A/R e B/L são codificações geométricas, não campos recetivos medidos. Self-motion e world-motion separados; só o input combinado é clipped.</p>
 <p>Observação do intervalo concluído mantida em 200 substeps. Readout e rates disponíveis no fim do intervalo neural de 20 ms. Cursor, pose, landmarks e inspector usam o mesmo boundary; sem interpolação neural ou nova simulação ao seek.</p>
 <p data-visual-timeline-samples={JSON.stringify(model.samples.map(s=>s[Math.round(time/.02)]))}>Cursor científico {time.toFixed(2)} s · P/Q: {model.samples.map(s=>s[Math.round(time/.02)]?.readout?.toExponential(5)??'indisponível').join(' / ')} yaw_drive_eq</p>
 <div className="neural-timeline-plots">{plots.map(l=><div className="neural-timeline-lane" key={l.key} data-visual-lane={l.key} data-common-extent={l.extent}><p>{l.name} · {l.series.map((s,i)=><span key={s.label} style={{color:colors[i]}}> {s.label} {i%2?'┄':'━'} </span>)}</p><div className="neural-timeline-plot"><SignalCanvas paths={l.paths}/><svg preserveAspectRatio="none" viewBox="0 0 900 94" role="img" aria-label={l.name} onClick={e=>{const r=e.currentTarget.getBoundingClientRect();onSeek(Math.min(pair.config.duration_s,Math.max(0,((e.clientX-r.left)/r.width*900-50)/820*30)));}}>
 <text x="0" y="16" fill="currentColor" fontSize="16">{l.extent.toPrecision(3)}</text><text x="0" y="75" fill="currentColor" fontSize="16">−{l.extent.toPrecision(3)}</text><text x="28" y="47" fill="currentColor" fontSize="16">0</text><line x1="50" x2="870" y1="44" y2="44" stroke="#526070"/>
 {events.map(e=><line key={`${e.condition}:${e.markerKey}`} x1={x(e.time)} x2={x(e.time)} y1="8" y2="78" stroke={e.condition==='P'?colors[0]:colors[1]} strokeDasharray={e.condition==='P'?'2 3':'5 3'}><title>{e.condition}: {e.label}</title></line>)}
 {contacts.map(e=><circle key={`${e.condition}:${e.step}`} cx={x(e.time)} cy={e.condition==='P'?75:81} r={e.kind==='RECOVERY'?2:3} fill={e.condition==='P'?colors[0]:colors[1]}><title>{e.condition} {e.kind} {e.wall} · {e.time.toFixed(2)} s</title></circle>)}
 <line x1={x(time)} x2={x(time)} y1="6" y2="84" stroke="white"/>{[0,5,10,15,20,25,30].map(t=><text key={t} x={x(t)} y="93" fill="currentColor" fontSize="16">{t}s</text>)}</svg></div></div>)}</div>
 <p data-visual-event-markers={JSON.stringify(events)}>Intervenções: {events.map(e=>`${e.condition}: ${e.label}`).join(' · ')||'Sem eventos aplicados na janela comum.'}</p><p data-visual-contact-markers={JSON.stringify(contacts)}>Contactos/recuperações computados: {contacts.map(e=>`${e.condition} ${e.kind} ${e.time.toFixed(2)}s`).join(' · ')||'nenhum'}. Círculos pequenos representam recuperação. Requests pendentes e eventos posteriores à janela comum não são aplicados.</p>
 </>:null}</details>;
}
