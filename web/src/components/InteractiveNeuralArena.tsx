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
 function planeChange(plane:Plane){try{engine.current?.requestPlane(plane);setPending(engine.current?.pendingPlane()??null);setState(engine.current?.snapshot()??null);setNotice(`Estímulo solicitado: Z=${plane}; aplica no próximo intervalo, boundary ${engine.current?.snapshot().step}.`);}catch(e){setError(String(e));}}
 function replay(){if(authority&&engine.current){try{const old=engine.current.snapshot(),next=replayEventLog(authority,engine.current.eventLog());if(JSON.stringify(old)!==JSON.stringify(next.snapshot()))throw new Error("Replay divergiu");synchronize(next);setNotice("Log recalculado desde o estado inicial: estado final idêntico. Pode continuar a simulação.");}catch(e){setError(String(e));}}}
 async function exportRun(){if(engine.current){try{const data=await engine.current.exportSession();const url=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:"application/json"}));const a=document.createElement('a');a.href=url;a.download='neurofly-interactive-v2.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setNotice(`Log/result hashes: ${data.log_sha256} / ${data.result_sha256}`);}catch(e){setError(String(e));}}}
 async function importRun(file:File|undefined){if(!file||!authority)return;setPlaying(false);clock.current.reset();try{if(file.size>2_000_000)throw new Error("Log demasiado grande");const data=await validateSession(authority,JSON.parse(await file.text()));if(data.log.config.mode!=="neural")throw new Error("Este modo interativo requer steering neural ativo");synchronize(replayEventLog(authority,data.log));setError(null);setNotice("Sessão importada, validada e recalculada. Nenhuma trajetória externa foi aplicada diretamente.");}catch(e){setError(String(e));}}
 const pose=state&&authority?{anchor:state.position,rotation:state.heading,assetOffset:authority.config.body.asset_offset}:undefined;
 return <>
  <section className="arena-replay-panel" aria-label="Interactive Neural Locomotion v2">
   <p className="arena-replay-identity">Interactive Neural Locomotion v2 · LIVE_BROWSER_MODEL_SIMULATION</p>
   <p className="arena-science-limit">INTERACTIVE_CONNECTOME_INFORMED_NEURAL_STEERING · ENGINEERING_PROPULSION. Computação local no browser; o estímulo altera a observação, não o heading diretamente. Sem gait, músculos ou velocidade biológica calibrados.</p>
   {!state&&!error?<p role="status">A verificar a autoridade Python HS/DNp15…</p>:null}
   {error?<p role="alert">{error} Simulação parada; nenhum movimento de substituição foi criado.</p>:null}
   {state?<>
    <label htmlFor="interactive-plane">Plano visual (landmarks X=±0.6)</label><select id="interactive-plane" disabled={state.step===400||Boolean(error)} value={pending??state.plane} onChange={e=>planeChange(Number(e.target.value) as Plane)}><option value={.4}>Z = +0.4</option><option value={-.4}>Z = −0.4</option></select>
    <p data-live-step={state.step} data-live-position={JSON.stringify(state.position)} data-live-heading={state.heading} data-live-neural={JSON.stringify({hs:state.hs,dn:state.dn})} data-live-readout={state.readout??"UNAVAILABLE"} data-live-plane={state.plane} data-live-contact={state.contact??"NONE"} data-live-substeps={state.substeps}>Tempo {state.time.toFixed(2)} / 8 s · X/Z {state.position[0].toFixed(5)} / {state.position[2].toFixed(5)} · heading {state.heading.toFixed(5)} rad · contacto {state.contact??"nenhum"}</p>
    <p>Drive do último intervalo: {state.readout?.toExponential(5)??"ainda não calculado"} yaw_drive_eq · omega do último intervalo {state.omega.toFixed(5)} rad/s · propulsão 0.18 unidades/s (velocidade translacional {state.contact?"0.00":"0.18"}) · distância {state.distance.toFixed(4)} unidades · estímulo ativo Z={state.plane}{pending!==null?` (Z=${pending} pendente)`:""}.</p>
    {cost.limited>0?<p className="arena-replay-note" data-live-lagging="true">Ritmo simulado reduzido: limite de catch-up atingido. O timestep científico permanece fixo.</p>:null}
    {events.length?<p className="arena-replay-note">Última intervenção aplicada: {events[events.length-1].time.toFixed(2)} s · Z={events[events.length-1].new_plane} · boundary {events[events.length-1].step}.</p>:null}
    <details><summary>Intervenções, reprodução e modelo</summary>
     <p data-live-events={JSON.stringify(events)}>{events.length?events.map(e=>`Boundary ${e.step}, ${e.time.toFixed(2)} s: Z ${e.old_plane} → ${e.new_plane}`).join(" · "):"Sem intervenções aplicadas."}</p>
     <button onClick={replay} disabled={Boolean(error)}>Recalcular log de intervenções</button><button onClick={()=>void exportRun()}>Exportar sessão JSON</button><label htmlFor="interactive-import">Importar e recalcular sessão</label><input id="interactive-import" type="file" accept="application/json" onChange={e=>void importRun(e.target.files?.[0])}/>
     <p>200 substeps de 0.1 ms por intervalo de 20 ms; exatamente {state.substeps} executados. Estados HS/DNp15 persistentes, updates simultâneos com estados antigos. Observação geométrica do último movimento concluído mantida durante cada intervalo; mudança do plano aplica a geometria nova a ambos os endpoints, sem flash de relocação. Ganho de engenharia 2.5 rad/orientation_eq, omega limitada a ±0.5 rad/s. Contacto trava translação; neural/heading continuam.</p>
     <p>Eventos aplicam no próximo boundary ainda não computado, incluindo quando pausado. Pedidos repetidos são coalescidos nesse boundary; vale o último plano solicitado. Reset repõe Z=+0.4, pose inicial e estados zero. Replay recalcula o prefixo do log desde zero, sem consultar trajetórias B/D. Exportação inclui configuração recuperável, eventos e telemetria com hashes; importação exige replay semântico.</p>
     <p>Pose apresentada no último boundary completo, sem extrapolação. Clock científico fixo, independente do FPS. Até cinco intervalos por frame; atraso excedente é descartado e tempo simulado pode avançar mais lentamente que tempo real. Paridade absoluta Python/JS ≤1e−8 unidades de modelo, janela de oito segundos. Readouts não são firing rates medidos; landmarks não são retina calibrada.</p>
     <p data-live-cost-ms={cost.last} data-live-max-cost-ms={cost.max} data-live-catchup={cost.limited}>Custo da atualização: {cost.last.toFixed(2)} ms · máximo {cost.max.toFixed(2)} ms · limite de catch-up ativado {cost.limited} vezes. {cost.limited>0?"Simulação pode estar mais lenta que tempo real.":"Sem limite de catch-up observado."}</p>
     <p className="arena-artifact-id">Fonte Python: {authority?.artifact_id} · MaleCNS v1.0 / {authority?.config.dataset_uuid}. HS R 10015/10016/10023, L 10034/10181/10419 → DNp15 11215/12069. Hipóteses do modelo mantidas; nenhum sinal fisiológico novo foi estabelecido.</p>
    </details>
    {notice?<p className="arena-artifact-id" role="status">{notice}</p>:null}
   </>:null}
  </section>
  <FlyViewer arena locomotion={Boolean(state)} locomotionVersion="v2" replayPose={pose} liveTrajectory={path} stimulusPlane={state?.plane} playbackControls={state?<div className="arena-replay-controls"><button disabled={Boolean(error)} onClick={()=>{if(state.step===400){reset();setPlaying(true);}else{clock.current.reset();setPlaying(!playing);}}}>{playing?"Pause":"Play"}</button><button onClick={reset}>Reset Experiment</button><button disabled={state.step===400||Boolean(error)} onClick={()=>planeChange((pending??state.plane)===.4?-.4:.4)}>Switch visual plane</button><output data-live-time={state.time}>{state.time.toFixed(2)} / 8.00 s{state.step===400?" · Fim":playing?" · Live":" · Pausado"}</output></div>:undefined}/>
 </>;
}
