"use client";
import {useEffect,useRef,useState} from "react";
import {loadNeuralLocomotion,type NeuralArtifact} from "@/lib/neuralLocomotion";
import {FixedStepClock,type Plane,type StimulusEvent} from "@/lib/interactiveNeuralLocomotion";
import {ContinuousNavigationEngine,replayNavigation,validateNavigation,type NavigationSnapshot} from "@/lib/continuousArenaNavigation";
import {generatePair,type PairArtifact,type NavigationSession} from "@/lib/neuralContributionComparison";
import {NeuralContributionComparison} from "./NeuralContributionComparison";

export function ContinuousNavigationArena(){
 const engine=useRef<ContinuousNavigationEngine|null>(null),clock=useRef(new FixedStepClock());
 const importedSource=useRef<NavigationSession|null>(null),suspended=useRef(false),alive=useRef(true);
 const [pair,setPair]=useState<PairArtifact|null>(null),[generating,setGenerating]=useState(false),[progress,setProgress]=useState(0),[pairError,setPairError]=useState<string|null>(null),[pairCost,setPairCost]=useState(0);
 const [authority,setAuthority]=useState<NeuralArtifact|null>(null),[state,setState]=useState<NavigationSnapshot|null>(null);
 const [pending,setPending]=useState<Plane|null>(null),[events,setEvents]=useState<StimulusEvent[]>([]);
 const [neuralEnabled,setNeuralEnabled]=useState(true);
 const [playing,setPlaying]=useState(false),[path,setPath]=useState<[number,number,number][]>([]);
 const [error,setError]=useState<string|null>(null),[notice,setNotice]=useState("");
 const [cost,setCost]=useState({last:0,max:0,limited:0});
 useEffect(()=>{alive.current=true;let cancelled=false;loadNeuralLocomotion().then(({authority})=>{if(cancelled)return;try{engine.current=new ContinuousNavigationEngine(authority);setAuthority(authority);setState(engine.current.snapshot());setPath(engine.current.trajectory());}catch(e){setError(String(e));}}).catch(e=>{if(!cancelled)setError(String(e));});return()=>{cancelled=true;alive.current=false;};},[]);
 useEffect(()=>{
  if(!playing)return;let animation=0,previous:number|null=null;
  const tick=(now:number)=>{
   if(suspended.current)return;
   if(previous!==null&&engine.current){try{
    const start=performance.now(),result=clock.current.advance(engine.current,now-previous,true,30),elapsed=performance.now()-start;
    if(result.steps){importedSource.current=null;setState(engine.current.snapshot());setPath(engine.current.trajectory());setPending(engine.current.pendingPlane());setEvents(engine.current.navigationLog().events);setCost(old=>({last:elapsed,max:Math.max(old.max,elapsed),limited:old.limited+(result.limited?1:0)}));}
    if(engine.current.snapshot().step===1500){setPlaying(false);clock.current.reset();return;}
   }catch(e){setPlaying(false);setError(String(e));return;}}
   previous=now;animation=requestAnimationFrame(tick);
  };animation=requestAnimationFrame(tick);return()=>cancelAnimationFrame(animation);
 },[playing]);
 function synchronize(next:ContinuousNavigationEngine){engine.current=next;clock.current.reset();setState(next.snapshot());setPath(next.trajectory());setPending(next.pendingPlane());setEvents(next.navigationLog().events);setPlaying(false);}
 function reset(){importedSource.current=null;if(authority){synchronize(new ContinuousNavigationEngine(authority,neuralEnabled?"neural":"output_disabled"));setCost({last:0,max:0,limited:0});setNotice("");setError(null);}}
 function planeChange(plane:Plane){importedSource.current=null;try{engine.current?.requestPlane(plane);setPending(engine.current?.pendingPlane()??null);setState(engine.current?.snapshot()??null);setNotice(`Estímulo solicitado: Z=${plane}; aplica no próximo intervalo, boundary ${engine.current?.snapshot().step}.`);}catch(e){setError(String(e));}}
 function replay(){if(authority&&engine.current){try{const old=engine.current.snapshot(),next=replayNavigation(authority,engine.current.navigationLog());if(JSON.stringify(old)!==JSON.stringify(next.snapshot()))throw new Error("Replay divergiu");synchronize(next);setNotice("Log recalculado desde o estado inicial: estado final idêntico. Pode continuar a simulação.");}catch(e){setError(String(e));}}}
 async function exportRun(){if(engine.current){try{const data=await engine.current.exportNavigation();const url=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:"application/json"}));const a=document.createElement('a');a.href=url;a.download='neurofly-navigation-v3.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setNotice(`Log/result hashes: ${data.log_sha256} / ${data.result_sha256}`);}catch(e){setError(String(e));}}}
 async function importRun(file:File|undefined){if(!file||!authority)return;setPlaying(false);clock.current.reset();try{if(file.size>8_000_000)throw new Error("Log demasiado grande");const data=await validateNavigation(authority,JSON.parse(await file.text()));setNeuralEnabled(data.log.config.mode==="neural");synchronize(replayNavigation(authority,data.log));importedSource.current=data;setError(null);setNotice("Sessão importada, validada e recalculada. Nenhuma trajetória externa foi aplicada diretamente.");}catch(e){setError(String(e));}}
 async function compare(){if(!authority||!engine.current)return;suspended.current=true;setPlaying(false);clock.current.reset();setState(engine.current.snapshot());setPath(engine.current.trajectory());setGenerating(true);setPairError(null);setProgress(0);const start=performance.now();try{const source=importedSource.current??await engine.current.exportNavigation();const next=await generatePair(authority,source,n=>{if(alive.current)setProgress(n);});if(alive.current){setPair(next);setPairCost(performance.now()-start);}}catch(e){if(alive.current){setPairError(String(e));suspended.current=false;}}finally{if(alive.current)setGenerating(false);}}
 function back(){setPair(null);suspended.current=false;clock.current.reset();setPlaying(false);}

 const pose=state&&authority?{anchor:state.position,rotation:state.heading,assetOffset:authority.config.body.asset_offset}:undefined;
 const livePanel=(
  <section className="arena-replay-panel" aria-label="Continuous Arena Navigation v3">
   <p className="arena-replay-identity">Continuous Arena Navigation v3 · LIVE_BROWSER_MODEL_SIMULATION</p>
   <p className="arena-science-limit">CONNECTOME_INFORMED_NEURAL_STEERING_WITH_ENGINEERING_BOUNDARY_NAVIGATION · ENGINEERING_PROPULSION. Computação local no browser; o estímulo altera a observação, não o heading diretamente. Sem gait, músculos ou velocidade biológica calibrados.</p>
   {!state&&!error?<p role="status">A verificar a autoridade Python HS/DNp15…</p>:null}
   {error?<p role="alert">{error} Simulação parada; nenhum movimento de substituição foi criado.</p>:null}
   {state?<>
    <button disabled={Boolean(error)||generating||state.step<1} onClick={()=>void compare()}>Compare Neural Contribution</button>
    {generating?<p role="status">Reconstruindo ON/OFF… {Math.round(progress*100)}% · sessão original suspensa e preservada.</p>:null}
    {pairError?<p role="alert">{pairError}. Sessão original preservada.</p>:null}
    {pairCost>0?<p data-pair-generation-ms={pairCost}>Última reconstrução: {pairCost.toFixed(1)} ms.</p>:null}
    <label><input type="checkbox" checked={neuralEnabled} disabled={generating} onChange={e=>{importedSource.current=null;const active=e.target.checked;setNeuralEnabled(active);if(authority)synchronize(new ContinuousNavigationEngine(authority,active?"neural":"output_disabled"));setCost({last:0,max:0,limited:0});setNotice("Controlo neural alterado: nova sessão desde estado inicial.");setError(null);}}/> Neural steering ativo (alterar reinicia sessão)</label>
    <label htmlFor="interactive-plane">Plano visual (landmarks X=±0.6)</label><select id="interactive-plane" disabled={state.step===1500||Boolean(error)||generating} value={pending??state.plane} onChange={e=>planeChange(Number(e.target.value) as Plane)}><option value={.4}>Z = +0.4</option><option value={-.4}>Z = −0.4</option></select>
    <p data-live-step={state.step} data-live-position={JSON.stringify(state.position)} data-live-heading={state.heading} data-live-neural={JSON.stringify({hs:state.hs,dn:state.dn})} data-live-readout={state.readout??"UNAVAILABLE"} data-live-plane={state.plane} data-live-contact={state.contact??"NONE"} data-live-substeps={state.substeps} data-boundary-omega={state.boundaryOmega} data-neural-omega={state.neuralOmega} data-recoveries={state.recoveries} data-contacts={state.contacts}>Tempo {state.time.toFixed(2)} / 30 s · X/Z {state.position[0].toFixed(5)} / {state.position[2].toFixed(5)} · heading {state.heading.toFixed(5)} rad · contacto {state.contact??"nenhum"}</p>
    <p>Drive do último intervalo: {state.readout?.toExponential(5)??"ainda não calculado"} yaw_drive_eq · omega do último intervalo {state.omega.toFixed(5)} rad/s · propulsão 0.18 unidades/s (velocidade translacional {state.contact?"0.00":"0.18"}) · distância {state.distance.toFixed(4)} unidades · estímulo ativo Z={state.plane}{pending!==null?` (Z=${pending} pendente)`:""}.</p>
    <p className="arena-replay-note">Contribuições do último intervalo · Neural: {state.neuralOmega.toFixed(5)} rad/s · Engenharia de fronteira: {state.boundaryOmega.toFixed(5)} rad/s · soma explícita, sem clamp combinado. Proximidade {state.proximity.toFixed(4)} unidades · contactos {state.contacts} · recuperações {state.recoveries} · tempo parado {state.contactSeconds.toFixed(2)} s. ENGINEERING_BOUNDARY_RECOVERY, não reflexo biológico. {neuralEnabled?"Steering neural aplicado.":"Controlo: neural calculado, contribuição para heading desligada."}</p>
    {cost.limited>0?<p className="arena-replay-note" data-live-lagging="true">Ritmo simulado reduzido: limite de catch-up atingido. O timestep científico permanece fixo.</p>:null}
    {events.length?<p className="arena-replay-note">Última intervenção aplicada: {events[events.length-1].time.toFixed(2)} s · Z={events[events.length-1].new_plane} · boundary {events[events.length-1].step}.</p>:null}
    <details><summary>Intervenções, reprodução e modelo</summary>
     <p data-live-events={JSON.stringify(events)}>{events.length?events.map(e=>`Boundary ${e.step}, ${e.time.toFixed(2)} s: Z ${e.old_plane} → ${e.new_plane}`).join(" · "):"Sem intervenções aplicadas."}</p>
     <button onClick={replay} disabled={Boolean(error)||generating}>Recalcular log de intervenções</button><button onClick={()=>void exportRun()}>Exportar sessão JSON</button><label htmlFor="interactive-import">Importar e recalcular sessão</label><input id="interactive-import" disabled={generating} type="file" accept="application/json" onChange={e=>void importRun(e.target.files?.[0])}/>
     <p>200 substeps de 0.1 ms por intervalo de 20 ms; exatamente {state.substeps} executados. Estados HS/DNp15 persistentes, updates simultâneos com estados antigos. Observação geométrica do último movimento concluído mantida durante cada intervalo; mudança do plano aplica a geometria nova a ambos os endpoints, sem flash de relocação. Ganho de engenharia 2.5 rad/orientation_eq, omega limitada a ±0.5 rad/s. Contacto trava translação apenas enquanto o rumo aponta para fora; rumo e neural continuam. Margem 0.06 unidades, ganho 2/s e contribuição geométrica até ±1.2 rad/s. Normais internas ponderadas pela proximidade; empate π vira positivo. Sem teleporte, rota predefinida ou steering neural falsificado.</p>
     <p>Eventos aplicam no próximo boundary ainda não computado, incluindo quando pausado. Pedidos repetidos são coalescidos nesse boundary; vale o último plano solicitado. Reset repõe Z=+0.4, pose inicial e estados zero. Replay recalcula o prefixo do log desde zero, sem consultar trajetórias B/D. Exportação inclui configuração recuperável, eventos e telemetria com hashes; importação exige replay semântico.</p>
     <p>Pose apresentada no último boundary completo, sem extrapolação. Clock científico fixo, independente do FPS. Até cinco intervalos por frame; atraso excedente é descartado e tempo simulado pode avançar mais lentamente que tempo real. Paridade absoluta Python/JS ≤1e−8 unidades de modelo, janela de trinta segundos. Readouts não são firing rates medidos; landmarks não são retina calibrada.</p>
     <p data-live-cost-ms={cost.last} data-live-max-cost-ms={cost.max} data-live-catchup={cost.limited}>Custo da atualização: {cost.last.toFixed(2)} ms · máximo {cost.max.toFixed(2)} ms · limite de catch-up ativado {cost.limited} vezes. {cost.limited>0?"Simulação pode estar mais lenta que tempo real.":"Sem limite de catch-up observado."}</p>
     <p className="arena-artifact-id">Fonte Python: {authority?.artifact_id} · MaleCNS v1.0 / {authority?.config.dataset_uuid}. HS R 10015/10016/10023, L 10034/10181/10419 → DNp15 11215/12069. Hipóteses do modelo mantidas; nenhum sinal fisiológico novo foi estabelecido.</p>
    </details>
    {notice?<p className="arena-artifact-id" role="status">{notice}</p>:null}
   </>:null}
  </section>
 );
 return <NeuralContributionComparison pair={pair} authority={authority} onReturn={back} onImport={(next,elapsed)=>{setPair(next);setPairCost(elapsed);}} generationMs={pairCost} livePanel={livePanel} liveViewerProps={{arena:true,locomotion:Boolean(state),locomotionVersion:"v3",replayPose:pose,liveTrajectory:path,stimulusPlane:state?.plane,playbackControls:state?<div className="arena-replay-controls"><button disabled={Boolean(error)||generating} onClick={()=>{if(state.step===1500){reset();setPlaying(true);}else{clock.current.reset();setPlaying(!playing);}}}>{playing?"Pause":"Play"}</button><button disabled={generating} onClick={reset}>Reset Experiment</button><button disabled={state.step===1500||Boolean(error)||generating} onClick={()=>planeChange((pending??state.plane)===.4?-.4:.4)}>Switch visual plane</button><output data-live-time={state.time}>{state.time.toFixed(2)} / 30.00 s{state.step===1500?" · Fim":playing?" · Live":" · Pausado"}</output></div>:undefined}}/>;
}
