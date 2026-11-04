"use client";
import {ScheduledVisualEngine,exportProtocolExecution} from '@/lib/visualProtocol';
import {useEffect,useRef,useState} from 'react';
import type {NeuralArtifact} from '@/lib/neuralLocomotion';
import type {ContinuousNavigationEngine} from '@/lib/continuousArenaNavigation';
import {ExperimentLibrary,createRecord,restoreRecord,compareRecord,renameRecord,type LibraryEntry,type LibraryRecord} from '@/lib/experimentSessionLibrary';
import type {ArenaSession,ArenaPair} from '@/lib/arenaSessionDispatch';
export function ExperimentSessionLibrary({authority,capture,onOpen,onCompare,onVisualCompare,disabled}:{authority:NeuralArtifact;capture:()=>Promise<{session:unknown;hasComparison:boolean}>;onOpen:(engine:ContinuousNavigationEngine,session:ArenaSession)=>void;onCompare:(pair:ArenaPair,elapsed:number)=>void;disabled:boolean;onVisualCompare?:(id:string)=>void}){
 const store=useRef(new ExperimentLibrary()),mounted=useRef(true);
 const [entries,setEntries]=useState<LibraryEntry[]>([]),[name,setName]=useState(''),[rename,setRename]=useState<{id:string;name:string;revision:string}|null>(null),[deleting,setDeleting]=useState<LibraryEntry|null>(null);
 const [busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null),[notice,setNotice]=useState(''),[cost,setCost]=useState<{operation:string;ms:number;bytes?:number}|null>(null);
 async function refresh(){setEntries(await store.current.list());}
 useEffect(()=>{mounted.current=true;const update=()=>{store.current.list().then(rows=>{if(mounted.current)setEntries(rows);}).catch(e=>{if(mounted.current)setError(String(e));});};update();window.addEventListener('focus',update);return()=>{mounted.current=false;window.removeEventListener('focus',update);};},[]);
 async function run(label:string,work:()=>Promise<{bytes?:number}|void>){if(busy)return;setBusy(true);setError(null);setNotice('');const start=performance.now();try{const result=await work();if(mounted.current){await refresh();setCost({operation:label,ms:performance.now()-start,bytes:result?.bytes});}}catch(e){if(mounted.current)setError(String(e));}finally{if(mounted.current)setBusy(false);}}
 async function save(value?:unknown){const source=value?{session:value,hasComparison:false}:await capture();let record=await createRecord(authority,source.session,name);if(source.hasComparison)record=(await compareRecord(authority,record)).record;await store.current.insert(record);setNotice(`Guardado: ${record.name} · ${record.summary.status==='PROTOCOL_COMPLETED'?'protocolo completo':record.summary.status==='OPERATOR_TERMINATED'?'prefixo terminado explicitamente':record.summary.status==='RECORDED_PREFIX'?'prefixo pausado':'30 s completos'}.`);return {bytes:new TextEncoder().encode(JSON.stringify(record)).length};}
 async function handleLoad(id:string,compare=false){const record=await store.current.get(id);if(compare){const result=await compareRecord(authority,record);await store.current.replace(result.record,record.revision);onCompare(result.pair,result.elapsed);setNotice('Comparison recomputed; reference stored in the parent session.');}else{const result=await restoreRecord(authority,record);onOpen(result.engine,result.session);setNotice('Session recomputed from the initial state and integrity-checked.');}}
 function download(data:unknown,filename:string){const url=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const locked=busy||disabled;
 return <details className="experiment-library" aria-label="My Experiments">
  <summary>My Experiments · Local library</summary>
  <p className="arena-replay-note">Saved in this browser and this origin. Another Preview hostname, device or browser has a different library; clearing site data or using a private window can remove it. JSON keeps it portable. Hashes detect corruption; they do not authenticate the author.</p>
  <label>Experiment name<input aria-label="Experiment name" maxLength={100} value={name} onChange={e=>setName(e.target.value)}/></label>
  <button disabled={locked||!name.trim()} onClick={()=>void run('Save',()=>save())}>Save current session</button>
  <label>Import session into library<input aria-label="Import session into library" disabled={locked||!name.trim()} type="file" accept="application/json" onChange={e=>{const file=e.target.files?.[0];e.target.value='';if(file)void run('Import',async()=>{if(file.size>8_000_000)throw new Error('Session exceeds 8 MB.');return save(JSON.parse(await file.text()));});}}/></label>
  <button disabled={locked} onClick={()=>void run('Refresh',refresh)}>Refresh library</button>
  {busy?<p role="status">Checking, recomputing and completing the transaction…</p>:null}
  {error?<p role="alert">{error} The current session and JSON export remain available; no substitute experiment was created.</p>:null}
  {notice?<p role="status">{notice}</p>:null}
  {cost?<p className="arena-replay-note" data-library-cost-ms={cost.ms} data-library-bytes={cost.bytes}>{cost.operation}: {cost.ms.toFixed(1)} ms{cost.bytes!==undefined?` · ${cost.bytes} bytes de inputs/metadados`:''}.</p>:null}
  {!entries.length?<p>No saved experiments.</p>:null}
  <ul className="experiment-library-list">{entries.map(entry=><li key={entry.id} data-library-id={entry.id}>
   {entry.record?<>
    <strong data-library-name={entry.record.name}>{entry.record.name}</strong>
    <p>{new Date(entry.record.created_at).toLocaleString()} · {entry.record.schema==='experiment_session_library_v5_2'?'v5.2':entry.record.schema==='experiment_session_library_v5'?'v5':entry.record.schema==='experiment_session_library_v4'?'v4':'v3'} {entry.record.summary.mode} · {entry.record.summary.duration_s.toFixed(2)} s {entry.record.summary.status==='PROTOCOL_COMPLETED'?'(protocolo completo)':entry.record.summary.status==='OPERATOR_TERMINATED'?'(prefixo terminado)':entry.record.summary.status==='RECORDED_PREFIX'?'(prefixo pausado)':'(completa)'} · {entry.record.summary.interventions} interventions · {entry.record.summary.distance.toFixed(4)} units (integrity-checked when saved; recomputed when opened). {entry.record.comparison?'Comparison referenced.':'Comparison available by reconstruction.'}</p>
    <button disabled={locked} onClick={()=>void run('Abrir',()=>handleLoad(entry.id))}>Abrir</button>
    {(entry.record.schema==='experiment_session_library_v5'||entry.record.schema==='experiment_session_library_v5_2')&&onVisualCompare?<button disabled={locked} onClick={()=>onVisualCompare(entry.id)}>Compare Visual Programs</button>:null}
    <button disabled={locked} onClick={()=>void run('Comparar',()=>handleLoad(entry.id,true))}>Compare Neural Contribution</button>
    <button disabled={locked} onClick={()=>setRename({id:entry.id,name:entry.record!.name,revision:entry.record!.revision})}>Renomear</button>
    <button disabled={locked} onClick={()=>void run('Export',async()=>{const {session,engine}=await restoreRecord(authority,await store.current.get(entry.id));if(engine instanceof ScheduledVisualEngine){download(await exportProtocolExecution(engine),'neurofly-visual-protocol-v5-2.json');return;}download(session,session.schema==='independent_visual_stimulus_session_v5'?'neurofly-independent-visual-stimuli-v5.json':session.schema==='moving_visual_stimulus_session_v4'?'neurofly-moving-visual-stimuli-v4.json':'neurofly-navigation-v3.json');})}>Export JSON</button>
   </>:<p role="alert">Record unavailable: {entry.error} · {entry.id}. It will not be replayed.</p>}
   <button disabled={locked} onClick={()=>setDeleting(entry)}>Delete</button>
  </li>)}</ul>
  {rename?<div role="group" aria-label="Rename experiment"><input aria-label="New name" maxLength={100} value={rename.name} onChange={e=>setRename({...rename,name:e.target.value})}/><button disabled={locked} onClick={()=>void run('Renomear',async()=>{const r=await store.current.get(rename.id);if(r.revision!==rename.revision)throw new Error('Registo alterado noutra aba; atualize e renomeie novamente.');const next=await renameRecord(r,rename.name);await store.current.replace(next,r.revision);setRename(null);setNotice('Name updated; scientific identity preserved.');})}>Confirm name</button><button disabled={locked} onClick={()=>setRename(null)}>Cancel name</button></div>:null}
  {deleting?<div role="group" aria-label="Confirm deletion"><p>Delete “{deleting.record?.name??deleting.id}” from this library? This also removes the linked ON/OFF reference; it does not change the running session or exported files.</p><button disabled={locked} onClick={()=>void run('Delete',async()=>{await store.current.remove(deleting.id,true,deleting.record?.revision);setDeleting(null);setNotice('Record and dependent reference deleted.');})}>Confirm deletion</button><button disabled={locked} onClick={()=>setDeleting(null)}>Cancel deletion</button></div>:null}
  <p className="arena-science-limit">INTERACTIVE_CONNECTOME_INFORMED_NEURAL_STEERING · ENGINEERING_PROPULSION · ENGINEERING_BOUNDARY_RECOVERY. ON/OFF is a NEURAL_ON_OFF_COMPUTATIONAL_INTERVENTION; saving does not represent memory or learning in the fly.</p>
 </details>;
}
