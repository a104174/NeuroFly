"use client";
import {useEffect,useRef,useState} from 'react';
import type {NeuralArtifact} from '@/lib/neuralLocomotion';
import type {ContinuousNavigationEngine} from '@/lib/continuousArenaNavigation';
import {ExperimentLibrary,createRecord,restoreRecord,compareRecord,renameRecord,type LibraryEntry,type LibraryRecord} from '@/lib/experimentSessionLibrary';
import type {ArenaSession,ArenaPair} from '@/lib/arenaSessionDispatch';
export function ExperimentSessionLibrary({authority,capture,onOpen,onCompare,onVisualCompare,disabled}:{authority:NeuralArtifact;capture:()=>Promise<{session:ArenaSession;hasComparison:boolean}>;onOpen:(engine:ContinuousNavigationEngine,session:ArenaSession)=>void;onCompare:(pair:ArenaPair,elapsed:number)=>void;disabled:boolean;onVisualCompare?:(id:string)=>void}){
 const store=useRef(new ExperimentLibrary()),mounted=useRef(true);
 const [entries,setEntries]=useState<LibraryEntry[]>([]),[name,setName]=useState(''),[rename,setRename]=useState<{id:string;name:string;revision:string}|null>(null),[deleting,setDeleting]=useState<LibraryEntry|null>(null);
 const [busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null),[notice,setNotice]=useState(''),[cost,setCost]=useState<{operation:string;ms:number;bytes?:number}|null>(null);
 async function refresh(){setEntries(await store.current.list());}
 useEffect(()=>{mounted.current=true;const update=()=>{store.current.list().then(rows=>{if(mounted.current)setEntries(rows);}).catch(e=>{if(mounted.current)setError(String(e));});};update();window.addEventListener('focus',update);return()=>{mounted.current=false;window.removeEventListener('focus',update);};},[]);
 async function run(label:string,work:()=>Promise<{bytes?:number}|void>){if(busy)return;setBusy(true);setError(null);setNotice('');const start=performance.now();try{const result=await work();if(mounted.current){await refresh();setCost({operation:label,ms:performance.now()-start,bytes:result?.bytes});}}catch(e){if(mounted.current)setError(String(e));}finally{if(mounted.current)setBusy(false);}}
 async function save(value?:unknown){const source=value?{session:value,hasComparison:false}:await capture();let record=await createRecord(authority,source.session,name);if(source.hasComparison)record=(await compareRecord(authority,record)).record;await store.current.insert(record);setNotice(`Guardado: ${record.name} · ${record.summary.status==='RECORDED_PREFIX'?'prefixo pausado':'30 s completos'}.`);return {bytes:new TextEncoder().encode(JSON.stringify(record)).length};}
 async function handleLoad(id:string,compare=false){const record=await store.current.get(id);if(compare){const result=await compareRecord(authority,record);await store.current.replace(result.record,record.revision);onCompare(result.pair,result.elapsed);setNotice('Comparação recalculada; referência guardada na sessão-mãe.');}else{const result=await restoreRecord(authority,record);onOpen(result.engine,result.session);setNotice('Sessão recalculada desde o estado inicial e verificada.');}}
 function download(data:unknown,filename:string){const url=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const locked=busy||disabled;
 return <details className="experiment-library" aria-label="My Experiments">
  <summary>My Experiments · Biblioteca local</summary>
  <p className="arena-replay-note">Guardado neste browser e nesta origem. Outro hostname Preview, dispositivo ou browser tem outra biblioteca; limpar dados do site ou usar modo privado pode removê-la. JSON mantém a portabilidade. Hashes detetam corrupção, não autenticam o autor.</p>
  <label>Nome da experiência<input aria-label="Nome da experiência" maxLength={100} value={name} onChange={e=>setName(e.target.value)}/></label>
  <button disabled={locked||!name.trim()} onClick={()=>void run('Guardar',()=>save())}>Guardar sessão atual</button>
  <label>Importar sessão para biblioteca<input aria-label="Importar sessão para biblioteca" disabled={locked||!name.trim()} type="file" accept="application/json" onChange={e=>{const file=e.target.files?.[0];e.target.value='';if(file)void run('Importar',async()=>{if(file.size>8_000_000)throw new Error('Sessão excede 8 MB.');return save(JSON.parse(await file.text()));});}}/></label>
  <button disabled={locked} onClick={()=>void run('Atualizar',refresh)}>Atualizar biblioteca</button>
  {busy?<p role="status">A validar, recalcular e concluir a transação…</p>:null}
  {error?<p role="alert">{error} A sessão atual e exportação JSON continuam disponíveis; nenhuma experiência de substituição foi criada.</p>:null}
  {notice?<p role="status">{notice}</p>:null}
  {cost?<p className="arena-replay-note" data-library-cost-ms={cost.ms} data-library-bytes={cost.bytes}>{cost.operation}: {cost.ms.toFixed(1)} ms{cost.bytes!==undefined?` · ${cost.bytes} bytes de inputs/metadados`:''}.</p>:null}
  {!entries.length?<p>Sem experiências guardadas.</p>:null}
  <ul className="experiment-library-list">{entries.map(entry=><li key={entry.id} data-library-id={entry.id}>
   {entry.record?<>
    <strong data-library-name={entry.record.name}>{entry.record.name}</strong>
    <p>{new Date(entry.record.created_at).toLocaleString()} · {entry.record.schema==='experiment_session_library_v5'?'v5':entry.record.schema==='experiment_session_library_v4'?'v4':'v3'} {entry.record.summary.mode} · {entry.record.summary.duration_s.toFixed(2)} s {entry.record.summary.status==='RECORDED_PREFIX'?'(prefixo pausado)':'(completa)'} · {entry.record.summary.interventions} intervenções · {entry.record.summary.distance.toFixed(4)} unidades (verificado ao guardar; recalculado ao abrir). {entry.record.comparison?'Comparação referenciada.':'Comparação disponível por reconstrução.'}</p>
    <button disabled={locked} onClick={()=>void run('Abrir',()=>handleLoad(entry.id))}>Abrir</button>
    {entry.record.schema==='experiment_session_library_v5'&&onVisualCompare?<button disabled={locked} onClick={()=>onVisualCompare(entry.id)}>Compare Visual Programs</button>:null}
    <button disabled={locked} onClick={()=>void run('Comparar',()=>handleLoad(entry.id,true))}>Compare Neural Contribution</button>
    <button disabled={locked} onClick={()=>setRename({id:entry.id,name:entry.record!.name,revision:entry.record!.revision})}>Renomear</button>
    <button disabled={locked} onClick={()=>void run('Exportar',async()=>{const {session}=await restoreRecord(authority,await store.current.get(entry.id));download(session,session.schema==='independent_visual_stimulus_session_v5'?'neurofly-independent-visual-stimuli-v5.json':session.schema==='moving_visual_stimulus_session_v4'?'neurofly-moving-visual-stimuli-v4.json':'neurofly-navigation-v3.json');})}>Exportar JSON</button>
   </>:<p role="alert">Registo indisponível: {entry.error} · {entry.id}. Não será reproduzido.</p>}
   <button disabled={locked} onClick={()=>setDeleting(entry)}>Eliminar</button>
  </li>)}</ul>
  {rename?<div role="group" aria-label="Renomear experiência"><input aria-label="Novo nome" maxLength={100} value={rename.name} onChange={e=>setRename({...rename,name:e.target.value})}/><button disabled={locked} onClick={()=>void run('Renomear',async()=>{const r=await store.current.get(rename.id);if(r.revision!==rename.revision)throw new Error('Registo alterado noutra aba; atualize e renomeie novamente.');const next=await renameRecord(r,rename.name);await store.current.replace(next,r.revision);setRename(null);setNotice('Nome atualizado; identidade científica preservada.');})}>Confirmar nome</button><button disabled={locked} onClick={()=>setRename(null)}>Cancelar nome</button></div>:null}
  {deleting?<div role="group" aria-label="Confirmar eliminação"><p>Eliminar “{deleting.record?.name??deleting.id}” desta biblioteca? Remove também a referência ON/OFF associada; não altera a sessão em execução nem ficheiros exportados.</p><button disabled={locked} onClick={()=>void run('Eliminar',async()=>{await store.current.remove(deleting.id,true,deleting.record?.revision);setDeleting(null);setNotice('Registo e referência dependente eliminados.');})}>Confirmar eliminação</button><button disabled={locked} onClick={()=>setDeleting(null)}>Cancelar eliminação</button></div>:null}
  <p className="arena-science-limit">INTERACTIVE_CONNECTOME_INFORMED_NEURAL_STEERING · ENGINEERING_PROPULSION · ENGINEERING_BOUNDARY_RECOVERY. ON/OFF é uma NEURAL_ON_OFF_COMPUTATIONAL_INTERVENTION; guardar não representa memória ou aprendizagem da mosca.</p>
 </details>;
}
