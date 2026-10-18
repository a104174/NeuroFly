"use client";
import {useLayoutEffect,useMemo,useRef,useState} from 'react';
import {timelineSamples,timelineEvents,timelinePath,type TimelineSample,type TimelineFrame,type TimelineSnapshot,type TimelineEvent} from '@/lib/neuralResponseTimeline';
const lanes=[{name:'Self / external R/L · raw normalized proxy',keys:['self','external']},{name:'Input combinado R/L · clipped proxy [−1,1]',keys:['combined']},{name:'HS/DNp15 mean readout · yaw_drive_eq',keys:['readout']},{name:'Neural / boundary · rad/s',keys:['neural','boundary']},{name:'Heading · rad (unwrapped)',keys:['heading']}] as const;
const colors=['#6ee7da','#f4bd73','#a5bcff','#e7a3d5'];
/** Rasterize full-resolution curves only when recorded data changes. Cursor stays separate. */
function SignalCanvas({paths}:{paths:readonly string[]}){
 const canvas=useRef<HTMLCanvasElement>(null);
 useLayoutEffect(()=>{const ctx=canvas.current?.getContext('2d');if(!ctx)throw new Error('Timeline Canvas indisponível');ctx.clearRect(0,0,900,94);paths.forEach((path,i)=>{ctx.strokeStyle=colors[i];ctx.lineWidth=1.3;ctx.setLineDash(i%2?[4,3]:[]);ctx.stroke(new Path2D(path));});},[paths]);
 return <canvas ref={canvas} width={900} height={94} aria-label="Curvas científicas, todas as amostras"/>;
}
export function NeuralResponseTimeline({frames,end,time,events,onSeek,onLive}:{frames:readonly TimelineFrame[];end:TimelineSnapshot;time:number;events:TimelineEvent[];onSeek:(t:number)=>void;onLive:()=>void}){
 const independent='landmarks' in end.stimulus;
 const [open,setOpen]=useState(false);
 const samples=useMemo(()=>timelineSamples(frames,end),[frames,end]);
 const markers=useMemo(()=>timelineEvents(events,end.step),[events,end.step]);
 const current=samples[Math.round(time/.02)];
 const plots=useMemo(()=>!open?[]:lanes.map(l=>{const series=l.keys.flatMap(key=>{const first=samples.find(s=>s[key]!==null)?.[key];return Array.isArray(first)?[0,1].map(i=>({label:`${key} ${independent?(i===0?'A (proxy R)':'B (proxy L)'):(i===0?'R':'L')}`,get:(s:TimelineSample)=>(s[key] as number[]|null)?.[i]??null})): [{label:key,get:(s:TimelineSample)=>s[key] as number|null}];});const values=series.flatMap(s=>samples.map(s.get).filter((v):v is number=>v!==null)),extent=Math.max(1e-8,...values.map(Math.abs));const paths=series.map(s=>timelinePath(samples,s.get,extent));return {l,series,extent,paths,hasData:values.length>0};}),[samples,open,independent]);
 return <details className="neural-timeline" onToggle={e=>setOpen(e.currentTarget.open)}><summary>Neural Response Timeline</summary>{open?<>
 <details><summary>Tempo, unidades e modelo</summary><p>Boundary selecionado: {time.toFixed(2)} s. Observação do intervalo corporal/mundial anterior, mantida durante o intervalo neural seguinte. Readout médio e rates apresentados no fim desse intervalo de 20 ms; sem interpolação neural. No início: sinal indisponível. HS R 10015/10016/10023 e L 10034/10181/10419 → DNp15 11215/12069. Neural: CONNECTOME_INFORMED_NEURAL_STEERING; fronteira: ENGINEERING_BOUNDARY_RECOVERY. Propulsão é ENGINEERING_PROPULSION. Play regressa ao último boundary e continua o estado vivo preservado; seek só inspeciona.</p></details>
 <label htmlFor="neural-timeline-time">Inspecionar tempo científico · {time.toFixed(2)} s</label><input id="neural-timeline-time" type="range" min={0} max={end.time} step={.02} value={time} onChange={e=>onSeek(Number(e.target.value))}/><button onClick={onLive}>Voltar ao último boundary</button>
 <p data-timeline-sample={JSON.stringify(current)}>Input disponível em {current?.inputAvailable===null?'—':current?.inputAvailable.toFixed(2)+' s'} · readout {current?.readout?.toExponential(5)??'indisponível'} · neural {current?.neural?.toFixed(5)??'—'} / engenharia {current?.boundary?.toFixed(5)??'—'} rad/s · contacto {current?.contact??'nenhum'}.</p>
 <div className="neural-timeline-plots">{plots.map(({l,series,extent,paths,hasData})=>{const x=(t:number)=>50+820*t/30;
 return <div className="neural-timeline-lane" key={l.name}><p>{l.name} · {series.map((s,i)=><span key={s.label} style={{color:colors[i]}}> {s.label} {i%2?'┄':'━'} </span>)}</p><div className="neural-timeline-plot"><SignalCanvas paths={paths}/><svg preserveAspectRatio="none" viewBox="0 0 900 94" role="img" aria-label={l.name} onClick={e=>{const r=e.currentTarget.getBoundingClientRect();onSeek(Math.min(end.time,Math.max(0,((e.clientX-r.left)/r.width*900-50)/820*30)));}}>
 <text x="0" y="16" fill="currentColor" fontSize="16">{extent.toPrecision(3)}</text><text x="0" y="75" fill="currentColor" fontSize="16">−{extent.toPrecision(3)}</text><text x="28" y="47" fill="currentColor" fontSize="16">0</text><line x1="50" x2="870" y1="44" y2="44" stroke="#526070"/>
 {markers.map(e=><line key={e.markerKey} x1={x(e.time)} x2={x(e.time)} y1="8" y2="78" stroke="#d5c58a" strokeDasharray="2 3"><title>{e.label}</title></line>)}
 {samples.filter((s,i)=>s.contact!==samples[i-1]?.contact&&s.contact!==null).map(s=><circle key={s.step} cx={x(s.time)} cy="78" r="3" fill="#f4bd73"><title>Contacto {s.contact} · {s.time.toFixed(2)} s</title></circle>)}
 <line x1={x(time)} x2={x(time)} y1="6" y2="80" stroke="white"/>{[0,5,10,15,20,25,30].map(t=><text key={t} x={x(t)} y="92" fill="currentColor" fontSize="16">{t}s</text>)}</svg></div>{!hasData?<p>Sinal indisponível; nenhum zero foi inventado.</p>:null}</div>;})}</div>
 <p>Seek apenas inspeciona; Play continua no último boundary calculado. Em ecrãs estreitos, deslize as lanes horizontalmente; o eixo é comum. Linhas verticais tracejadas: intervenções. Círculos: início de contacto.</p><p>Eventos: {markers.map(e=>e.label).join(' · ')||'nenhum'}. Self-motion mantém landmarks anteriores fixos; external mede a mudança adicional na pose final. Só o combinado é clipped; componentes clipped não são somáveis. Unidades de modelo, não medições biológicas. A→R e B→L são a codificação geométrica herdada, não campos recetivos medidos. Não se somam os dois landmarks num único input nem se presume cancelamento em oposição. Neural OFF pode conservar readout não zero.</p>
 </>:null}</details>;
}
